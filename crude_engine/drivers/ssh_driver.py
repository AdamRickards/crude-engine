"""
SSH_gather.py — SSH protocol driver for crude-engine.

Layer: Driver. Translates wire YAML source dicts into SSH CLI operations.
Owns: command dedup, level navigation, CLI parsing, response caching.
Cannot: interpret data meaning, decide what to gather, know about schemas.
Talks to: ssh.py (state machine + netmiko). Called by: engine (gather/set_values).
Wire output: str, int, float, bool, list, dict, None.
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Any

from crude_engine.engine import crude as transforms
from crude_engine.drivers.base import BaseDriver, AGGREGATE_TAGS

logger = logging.getLogger(__name__)


class SSHGatherDriver(BaseDriver):
    """SSH protocol driver — gather via CLI commands."""

    # ------------------------------------------------------------------
    # Gather — main read path (3-phase: dedup, execute, parse)
    # ------------------------------------------------------------------

    def gather(self, sources: List[Tuple[str, Dict]],
               value_maps: Dict = None) -> Dict[str, Any]:
        """Gather attribute values via SSH CLI.

        Three-phase pipeline:
        1. Deduplicate commands — one execution per unique (command, level)
        2. Execute each command, cache raw response
        3. Parse cached response per attribute using declared parser
        """
        results = {}

        # Phase 1: Collect unique (command, level) pairs
        ssh_cache = {}
        ssh_source_map = {}
        for name, source in sources:
            if source.get("iterate_from"):
                continue  # handled in Phase 4
            cmd = source.get("command", "")
            level = source.get("level", self._infer_level(source))
            key = (cmd, level)
            if key not in ssh_cache:
                ssh_cache[key] = None
                ssh_source_map[key] = source
            # Also collect default_from commands for cross-table queries
            default_from = source.get("default_from")
            if default_from:
                d_cmd = default_from.get("command", "")
                d_level = default_from.get("level", self._infer_level(default_from))
                d_key = (d_cmd, d_level)
                if d_key not in ssh_cache:
                    ssh_cache[d_key] = None
                    ssh_source_map[d_key] = default_from

        # Phase 2: Execute each unique command once
        for (cmd, level), src in ssh_source_map.items():
            params = {}
            if level == "config_interface":
                iface = src.get("interface", "")
                if iface:
                    params["interface"] = iface
            if hasattr(self.transport, 'navigate_to'):
                self.transport.navigate_to(level, params=params)
            else:
                if level not in ("user",):
                    self.transport._enable()
                if level == "config":
                    self.transport._config_mode()
            try:
                # Per-source cmd_verify override (None = use SSH.yaml default)
                verify = src.get("cmd_verify")
                resp = self.transport.cli(cmd, cmd_verify=verify)
                if isinstance(resp, dict):
                    resp = resp.get(cmd, "")
                ssh_cache[(cmd, level)] = resp
            except Exception as e:
                logger.debug("SSH command failed: %s — %s", cmd, str(e)[:80])
                ssh_cache[(cmd, level)] = ""

        # Keep the command text for inspect/sidecar trace. Does not change
        # parse or what was sent. Cap each blob so a poll body stays usable.
        _cli = []
        for (cmd, level), resp in ssh_cache.items():
            text = resp if isinstance(resp, str) else str(resp)
            if len(text) > 32768:
                text = text[:32768] + "\n…truncated"
            _cli.append({"command": cmd, "level": level, "response": text})
        self.last_cli = _cli
        if getattr(self, "transport", None) is not None:
            self.transport.last_cli = _cli

        # Phase 3: Each attribute parses from cached response
        for name, source in sources:
            if source.get("iterate_from"):
                continue  # handled in Phase 4
            cmd = source.get("command", "")
            level = source.get("level", self._infer_level(source))
            resp = ssh_cache.get((cmd, level))
            if resp is None:
                continue
            val = self._parse_response(resp, source)
            if val is None:
                continue
            tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
            if isinstance(val, dict) and self._tag_name(tag) in AGGREGATE_TAGS:
                # Aggregate tag: pass whole dict to transform
                results[name] = self._apply_pipeline(val, source, tag, value_maps)
            elif isinstance(val, dict):
                # Dict from parser: apply pipeline per value
                results[name] = {
                    k: self._apply_pipeline(v, source, tag, value_maps)
                    for k, v in val.items()
                }
            else:
                # Scalar from parser: apply pipeline
                results[name] = self._apply_pipeline(val, source, tag, value_maps)

        # Phase 3b: Cross-table default_from — fill missing dict keys with
        # scalar from another command. Runs after all Phase 3 attributes are
        # gathered so referenced attributes (keys_from) are available.
        for name, source in sources:
            if source.get("iterate_from"):
                continue
            default_from = source.get("default_from")
            if not default_from or not isinstance(results.get(name), dict):
                continue
            d_cmd = default_from.get("command", "")
            d_level = default_from.get("level", self._infer_level(default_from))
            d_resp = ssh_cache.get((d_cmd, d_level), "")
            if not d_resp:
                continue
            d_val = self._parse_response(d_resp, default_from)
            if not d_val or not isinstance(d_val, str):
                continue
            # Apply parent source's tag pipeline to default value
            tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
            if tag:
                d_val = self._apply_pipeline(d_val, source, tag, value_maps)
            keys_from = default_from.get("keys_from")
            if keys_from and keys_from in results:
                ref_data = results[keys_from]
                if isinstance(ref_data, dict):
                    for k in ref_data:
                        if k not in results[name]:
                            results[name][k] = d_val

        # Phase 4: Per-entity iteration (iterate_from: gathered attribute or static list)
        # Cache responses per (command_template, entity) to avoid re-executing
        iterate_sources = [(n, s) for n, s in sources if s.get("iterate_from")]
        # Process static lists first (they don't depend on results),
        # then reference-based (they need previously gathered results)
        iterate_sources.sort(key=lambda x: 0 if isinstance(x[1].get("iterate_from"), list) else 1)
        iterate_cache = {}  # (cmd_template, entity) → raw response
        for name, source in iterate_sources:
            ref = source["iterate_from"]
            if isinstance(ref, list):
                entities = {str(v): str(v) for v in ref}
            else:
                entities = results.get(ref, {})
            if not isinstance(entities, dict):
                continue
            cmd_template = source.get("command", "")
            level = source.get("level", self._infer_level(source))
            tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
            per_entity = {}
            for entity_key, entity_val in entities.items():
                entity = entity_val if isinstance(entity_val, str) else str(entity_key)
                cache_key = (cmd_template, entity)
                if cache_key not in iterate_cache:
                    cmd = cmd_template.replace("{entity}", entity)
                    params = {}
                    if hasattr(self.transport, 'navigate_to'):
                        self.transport.navigate_to(level, params=params)
                    try:
                        verify = source.get("cmd_verify")
                        resp = self.transport.cli(cmd, cmd_verify=verify)
                        if isinstance(resp, dict):
                            resp = resp.get(cmd, "")
                    except Exception:
                        resp = ""
                    iterate_cache[cache_key] = resp
                resp = iterate_cache[cache_key]
                val = self._parse_response(resp, source)
                if val is not None:
                    if isinstance(val, dict) and self._tag_name(tag) in AGGREGATE_TAGS:
                        val = self._apply_pipeline(val, source, tag, value_maps)
                    elif isinstance(val, dict):
                        val = {k: self._apply_pipeline(v, source, tag, value_maps)
                               for k, v in val.items()}
                    else:
                        val = self._apply_pipeline(val, source, tag, value_maps)
                    per_entity[entity] = val
            results[name] = per_entity

        return results

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _is_empty_sentinel(self, line: str) -> bool:
        """Check if a line is a vendor empty-table sentinel (from SSH.yaml)."""
        sentinels = self.protocol_defaults.get("empty_table_sentinels", [])
        stripped = line.strip().lower()
        return any(stripped.startswith(s.lower()) for s in sentinels)

    # ------------------------------------------------------------------
    # Level inference
    # ------------------------------------------------------------------

    def _infer_level(self, source: Dict) -> str:
        """Infer target SSH level from source definition."""
        mode = source.get("mode")
        if mode:
            mode_map = {
                "config": "config",
                "enable": "priv",
                "vlan_database": "vlan_database",
                "config_interface": "config_interface",
            }
            if mode in mode_map:
                return mode_map[mode]
            if mode.startswith("config_interface"):
                return "config_interface"

        if not source.get("priv", True):
            return "user"

        if hasattr(self.transport, 'infer_level'):
            return self.transport.infer_level(source.get("command", ""))

        return "config"

    # ------------------------------------------------------------------
    # Response parsing — shape-based, not feature-specific
    # ------------------------------------------------------------------

    def _parse_response(self, resp: str, source: Dict) -> Any:
        """Parse SSH CLI response using declared shape.

        Shapes are vendor-agnostic data structures:
        - dot_keys: key....value pairs
        - table: columnar rows after separator
        - paired_rows: multi-line records after separator
        - sections: block-per-entry with header lines
        - simple_table: header + separator + rows
        - regex: pattern match with capture groups

        Selectors (field, column, line, section) extract specific data
        from the parsed shape. Transforms handle type conversion.
        """
        default_parser = self.protocol_defaults.get("parser")
        parser = source.get("parser", default_parser)
        if not parser or parser == "none":
            return resp

        if parser == "regex":
            m = re.search(source.get("pattern", ""), resp)
            if m and m.groups():
                return m.group(1)
            return m.group(0) if m else resp

        elif parser == "dot_keys":
            return self._parse_dot_keys(resp, source)

        elif parser == "table":
            return self._parse_table(resp, source)

        elif parser == "paired_rows":
            return self._parse_paired_rows(resp, source)

        elif parser == "sections":
            return self._parse_sections(resp, source)

        elif parser == "simple_table":
            return self._parse_simple_table(resp, source)

        # Fallback: try dot_keys if output has .... pattern
        if "...." in resp:
            result = self._parse_dot_keys(resp, source)
            if result and result != resp:
                return result

        return resp

    # ------------------------------------------------------------------
    # Parser implementations — generic shapes only
    # ------------------------------------------------------------------

    def _parse_dot_keys(self, resp: str, source: Dict) -> Any:
        """Shape: key....value pairs.

        Options:
            field: extract single field value
            filter: regex pattern to filter keys (e.g. "Power Supply")
            filter_key_extract: regex to extract key from matched lines
        (no field) → return full dict
        """
        data = {}
        key_filter = source.get("filter")
        key_extract = source.get("filter_key_extract")

        for line in resp.splitlines():
            if "...." not in line:
                continue
            key, _, value = line.partition("....")
            key = key.strip()
            value = value.strip().lstrip(".")
            if not key:
                continue
            if key_filter and not re.search(key_filter, key, re.IGNORECASE):
                continue
            if key_extract:
                m = re.search(key_extract, key)
                if m:
                    key = m.group(1)
            data[key] = value

        field = source.get("field")
        if not field:
            return data
        if field in data:
            return data[field]
        fl = field.lower()
        for k, v in data.items():
            if fl in k.lower():
                return v
        return None

    def _parse_table(self, resp: str, source: Dict) -> Any:
        """Shape: columnar rows after separator line(s).

        Options:
            column: int — extract this column index per row
            section: "last" — use the LAST separator-delimited table
            field: str — extract specific named column (by field mapping)
        """
        lines = resp.splitlines()
        section = source.get("section")

        # Find separator(s)
        seps = [i for i, line in enumerate(lines)
                if re.match(r'^[-\s]+$', line.strip()) and '---' in line]
        if not seps:
            return {}

        # Select which separator to use
        if section == "last":
            sep_idx = seps[-1]
        elif isinstance(section, int) and section < len(seps):
            sep_idx = seps[section]
        else:
            sep_idx = seps[0]
        sep_line = lines[sep_idx]

        # Determine column boundaries from separator dashes
        col_ranges = []
        i = 0
        while i < len(sep_line):
            if sep_line[i] == '-':
                start = i
                while i < len(sep_line) and sep_line[i] == '-':
                    i += 1
                col_ranges.append((start, i))
            else:
                i += 1

        # Determine end boundary — next separator or blank line (scoped section)
        end_idx = len(lines)
        if isinstance(section, int):
            # Scoped to section: stop at next blank line or next separator
            for ei in range(sep_idx + 1, len(lines)):
                if not lines[ei].strip():
                    end_idx = ei
                    break
                if ei > sep_idx + 1 and re.match(r'^[-\s]+$', lines[ei].strip()) and '---' in lines[ei]:
                    end_idx = ei
                    break

        # Extract rows using column boundaries
        col = source.get("column")
        key_column = source.get("key_column")
        filter_col = source.get("filter_column")
        filter_val = source.get("filter_value")
        result = {}
        row_num = 0
        for line in lines[sep_idx + 1:end_idx]:
            stripped = line.strip()
            if not stripped or self._is_empty_sentinel(line):
                continue
            values = []
            for ci, (start, end) in enumerate(col_ranges):
                col_end = col_ranges[ci + 1][0] if ci + 1 < len(col_ranges) else len(line)
                val = line[start:col_end].strip() if start < len(line) else ""
                values.append(val)

            # Row filter: skip rows where filter column doesn't match
            if filter_col is not None and filter_val is not None:
                if filter_col < len(values) and values[filter_col] != filter_val:
                    continue

            if key_column is not None and key_column < len(values):
                key = values[key_column]
            else:
                key = str(row_num)
            row_num += 1
            if col is not None and isinstance(col, int):
                result[key] = values[col] if col < len(values) else ""
            else:
                result[key] = values

        return result

    def _parse_paired_rows(self, resp: str, source: Dict) -> Any:
        """Shape: multi-line records after separator.

        Records are either separated by blank lines, or fixed-size
        (declared via lines_per_record).

        Options:
            lines_per_record: int — fixed record size (default: detect by blank lines)
            line: which line of the record (0-based)
            column: which whitespace-delimited column
            columns: list of column indices → joined
            key: return record key instead of column value
            regex_extract: regex to extract value from full record text
            index: which regex match to use (0-based)
        """
        lines = resp.splitlines()
        sep_idx = None
        for i, line in enumerate(lines):
            if re.match(r'^[-\s]+$', line.strip()) and '---' in line:
                sep_idx = i
                break
        if sep_idx is None:
            return {}

        # Build column boundaries from separator dashes
        sep_line = lines[sep_idx]
        col_ranges = []
        ci = 0
        while ci < len(sep_line):
            if sep_line[ci] == '-':
                start = ci
                while ci < len(sep_line) and sep_line[ci] == '-':
                    ci += 1
                col_ranges.append((start, ci))
            else:
                ci += 1

        data_lines = [l for l in lines[sep_idx + 1:]
                      if l.strip() and not self._is_empty_sentinel(l)]
        lpr = source.get("lines_per_record")

        if lpr:
            # Fixed record size
            records = [data_lines[i:i+lpr] for i in range(0, len(data_lines), lpr)]
        else:
            # Detect by blank lines
            records = []
            current = []
            for line in lines[sep_idx + 1:]:
                if not line.strip() or self._is_empty_sentinel(line):
                    if current:
                        records.append(current)
                        current = []
                else:
                    current.append(line)
            if current:
                records.append(current)

        line_idx = source.get("line", 0)
        col = source.get("column")
        cols = source.get("columns")
        key_column = source.get("key_column")
        key = source.get("key")
        regex_extract = source.get("regex_extract")
        match_index = source.get("index", 0)

        overflow = source.get("column_overflow",
                              self.protocol_defaults.get("column_overflow", "flexible"))

        def extract_col(line_text, col_idx):
            """Extract column value using separator-defined boundaries.

            flexible: values wider than column dashes extend to next 2+ space gap.
            strict: values clip at dash-defined column boundary.
            """
            if col_idx < 0:
                col_idx = len(col_ranges) + col_idx
            if col_idx < 0 or col_idx >= len(col_ranges):
                return ""
            start, _ = col_ranges[col_idx]
            if start >= len(line_text):
                return ""
            if overflow == "strict":
                end = col_ranges[col_idx + 1][0] if col_idx + 1 < len(col_ranges) else len(line_text)
                return line_text[start:end].strip()
            # flexible: find actual value end via 2+ space gap
            raw = line_text[start:]
            stripped = raw.lstrip()
            if not stripped:
                return ""
            val_start = start + len(raw) - len(stripped)
            m = re.search(r'\S\s{2,}', line_text[val_start:])
            if m:
                val_end = val_start + m.start() + 1
            else:
                val_end = len(line_text)
            return line_text[val_start:val_end].strip()

        result = {}
        for i, record in enumerate(records):
            kc = key_column if key_column is not None else 0
            rec_key = extract_col(record[0], kc) if record else str(i)
            if not rec_key:
                rec_key = str(i)

            if regex_extract:
                full_text = " ".join(record)
                matches = re.findall(regex_extract, full_text)
                if match_index < len(matches):
                    try:
                        result[rec_key] = float(matches[match_index])
                    except ValueError:
                        result[rec_key] = matches[match_index]
                continue

            if line_idx >= len(record):
                continue

            if key:
                result[str(i)] = rec_key
            elif cols and isinstance(cols, list):
                vals = [extract_col(record[line_idx], c) for c in cols]
                result[rec_key] = " ".join(v for v in vals if v)
            elif col is not None and isinstance(col, int):
                result[rec_key] = extract_col(record[line_idx], col)
            else:
                result[rec_key] = record[line_idx].strip()

        return result

    def _parse_sections(self, resp: str, source: Dict) -> Any:
        """Shape: block-per-entry with header lines + dot_keys body.

        Options:
            section_pattern: regex to detect section headers (default: "Remote data,")
            key_extract: regex group(1) extracts key from header
            field: extract specific field from section body
            key: return section keys as values
        """
        field = source.get("field")
        key_field = source.get("key")
        section_pattern = source.get("section_pattern", r"^Remote data,")
        key_extract = source.get("key_extract", r",\s*(\S+)")

        sections = {}
        current_key = None
        current_data = {}

        for line in resp.splitlines():
            stripped = line.strip()
            if re.match(section_pattern, stripped):
                if current_key and current_data:
                    sections[current_key] = current_data
                m = re.search(key_extract, stripped)
                current_key = m.group(1) if m else stripped
                current_data = {}
            elif "...." in stripped and current_key is not None:
                k, _, v = stripped.partition("....")
                k = k.strip()
                v = v.strip().lstrip(".")
                k_lower = k.lower().replace(" ", "_")
                if k:
                    current_data[k_lower] = v

        if current_key and current_data:
            sections[current_key] = current_data

        if key_field:
            return {k: k for k in sections}
        if field:
            field_lower = field.lower().replace(" ", "_")
            return {k: v.get(field_lower, v.get(field, ""))
                    for k, v in sections.items()}
        return sections

    def _parse_simple_table(self, resp: str, source: Dict) -> Any:
        """Shape: header + separator + single-column-key rows.

        Options:
            column: int — extract this column per row (default: 0)
            field: extract single field value by key
        """
        lines = resp.splitlines()
        col = source.get("column", 0)
        field = source.get("field")

        sep_idx = None
        for i, line in enumerate(lines):
            if re.match(r'^[-\s]+$', line.strip()) and '---' in line:
                sep_idx = i
                break
        if sep_idx is None:
            return {}

        result = {}
        for line in lines[sep_idx + 1:]:
            if not line.strip():
                continue
            parts = line.split()
            if not parts:
                continue
            key = parts[0]
            if isinstance(col, int) and col < len(parts):
                result[key] = parts[col]
            else:
                result[key] = line.strip()

        if field:
            return result.get(field, "")
        return result

    # ------------------------------------------------------------------
    # Set — write path
    # ------------------------------------------------------------------

    def set_values(self, source: Dict, tokens: Dict,
                   value_maps: Dict = None) -> bool:
        """Execute SSH SET operation(s)."""
        if "_row_index" in source:
            tokens["_row_index"] = source["_row_index"]
        commands = source.get("sets", [source] if "command" in source else [])
        for item in commands:
            cmd = item.get("command", "")
            if "{" in cmd:
                cmd = self._apply_tokens(cmd, tokens)
            level = item.get("level", self._infer_level(item))
            params = {}
            if level == "config_interface":
                iface = tokens.get("interface", item.get("interface", ""))
                if iface:
                    params["interface"] = iface
            if hasattr(self.transport, 'navigate_to'):
                self.transport.navigate_to(level, params=params)
            # Wire YAML can override cmd_verify per-command
            verify = item.get("cmd_verify")
            confirm = item.get("confirm")
            if confirm:
                # Command prompts for confirmation — send command then response
                self.transport.connection.send_command_timing(cmd)
                self.transport.connection.send_command_timing(confirm)
            else:
                self.transport.cli(cmd, cmd_verify=verify)
        return True

    def dispatch_batch(self, batch: list, index=None) -> bool:
        """GATE 3 INGRESS: SSH dispatch — per-command (no batching)."""
        for wire_name, value, wire_ctx in batch:
            proto_src = wire_ctx.proto_src
            if isinstance(proto_src, dict) and "write" in proto_src:
                proto_src = proto_src["write"]
            elif isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            if not isinstance(proto_src, dict):
                continue
            source = dict(proto_src)
            tokens = {"value": value, wire_name: value}
            if index is not None:
                source["_row_index"] = index
            self.set_values(source, tokens, wire_ctx.value_maps)
        return True

    def create_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    fields: Dict, value_maps: Dict = None,
                    index_field: str = None,
                    create_method: str = "createAndWait",
                    **kwargs) -> bool:
        """SSH CREATE — wire YAML declares the command + level."""
        cmd_src = rs_source.get("create", {})
        if not isinstance(cmd_src, dict) or not cmd_src.get("command"):
            return False
        tokens = dict(kwargs)
        tokens.update(fields)
        tokens["index"] = index
        return self.set_values(cmd_src, tokens)

    def delete_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    index_field: str = None, **kwargs) -> bool:
        """SSH DELETE — wire YAML declares the command + level."""
        cmd_src = rs_source.get("delete", {})
        if not isinstance(cmd_src, dict) or not cmd_src.get("command"):
            return False
        tokens = dict(kwargs)
        tokens["index"] = index
        return self.set_values(cmd_src, tokens)

    @staticmethod
    def _apply_tokens(template: str, tokens: Dict) -> str:
        import re
        def replacer(match):
            expr = match.group(1).strip()
            if expr in tokens:
                return str(tokens[expr])
            try:
                return str(eval(expr, {"__builtins__": {}}, dict(tokens)))
            except Exception:
                return match.group(0)
        return re.sub(r"\{(.*?)\}", replacer, template)
