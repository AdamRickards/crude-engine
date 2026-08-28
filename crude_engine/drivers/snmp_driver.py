"""
SNMP.py — SNMP protocol driver for napalm-hios.

Layer: Driver. Translates wire YAML source dicts into SNMP operations.
Owns: walk batching, scalar normalization, index decomposition, tag dispatch.
Cannot: interpret data meaning, decide what to gather, know about schemas.
Talks to: snmp_transport.py (raw I/O). Called by: engine (gather/set_values).
Wire output: str, int, float, bool, list, dict, None.
"""

import logging
from typing import Dict, List, Tuple, Any

from crude_engine.engine import crude as transforms
from crude_engine.drivers.base import BaseDriver

logger = logging.getLogger(__name__)


class SNMPDriver(BaseDriver):
    """SNMP protocol driver — gather and set via SNMP OIDs."""

    # ------------------------------------------------------------------
    # Gather — main read path
    # ------------------------------------------------------------------

    def gather(self, sources: List[Tuple[str, Dict]],
               value_maps: Dict = None) -> Dict[str, Any]:
        """Gather attribute values via SNMP.

        Categorizes sources into scalars, walks, multi-OID, walk_columns,
        then executes each batch optimally.
        """
        results = {}
        scalars = []
        walks = {}      # name → source (ordered)
        multi_oids = []
        walk_columns = []

        # Phase 1: categorize sources (apply driver default method)
        default_method = self.protocol_defaults.get("method", "walk")
        for name, source in sources:
            if "oid" not in source and "oids" not in source:
                continue
            # Targeted cell read: index_filter → scalar GET at oid.index
            idx_filter = source.get("_index_filter")
            if idx_filter is not None:
                cell = dict(source, oid=f"{source['oid']}.{idx_filter}", is_cell=True)
                scalars.append((name, cell))
                continue
            method = source.get("method", default_method)
            # OIDs ending in .0 are scalars regardless of default
            oid = source.get("oid", "")
            if method == "walk" and oid.endswith(".0"):
                method = "scalar"
            if "oids" in source:
                multi_oids.append((name, source))
            elif method == "walk_columns":
                walk_columns.append((name, source))
            elif method == "walk":
                walks[name] = source
            else:
                scalars.append((name, source))

        # Phase 2: execute each category
        self._gather_scalars(scalars, results, value_maps)
        self._gather_walks(walks, results, value_maps)
        self._gather_join(walks, results)
        self._gather_multi_oids(multi_oids, results, value_maps)
        self._gather_walk_columns(walk_columns, results, value_maps)

        return results

    # ------------------------------------------------------------------
    # Scalar batching
    # ------------------------------------------------------------------

    def _gather_scalars(self, scalars, results, value_maps):
        """Batch scalar GETs — multiple OIDs in one request."""
        if not scalars:
            return
        oid_map = {}
        for name, source in scalars:
            oid = source["oid"]
            suffix = source.get("suffix", "")
            if suffix:
                oid = oid + suffix
            elif not oid.endswith(".0") and not source.get("is_cell"):
                oid += ".0"
            oid_map.setdefault(oid, []).append((name, source))

        raw = self.transport._get_scalars_sync(*list(oid_map.keys()))
        for oid, val in raw.items():
            # Skip SNMP error values (normalized to None by transport)
            if val is None:
                continue
            key = oid.lstrip(".")
            targets = oid_map.get(key) or oid_map.get(oid, [])
            for name, source in targets:
                tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
                results[name] = self._apply_pipeline(val, source, tag, value_maps)

    # ------------------------------------------------------------------
    # Walk processing
    # ------------------------------------------------------------------

    def _gather_walks(self, walks, results, value_maps):
        """Process SNMP walks with index decomposition, context, transforms."""
        for name, source in walks.items():
            raw = self.transport._walk_sync(source["oid"])

            # RFC 2578 INDEX decomposition — MIB INDEX clause in YAML
            index_fields = source.get("index_fields")
            if index_fields:
                results[name] = self._gather_rfc_walk(
                    raw, source, index_fields, value_maps, name
                )
                continue

            # Legacy positional index — compound OID suffix handler
            index_spec = source.get("index")
            if index_spec and isinstance(index_spec, list):
                tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
                results[name] = self._process_walk_index(
                    raw, index_spec, tag, value_maps, source=source
                )
                continue

            explicit_tag = source.get("tag", "")
            tag = self._resolve_tag(explicit_tag, source, attr_name=name)
            key_tag = source.get("key_tag")

            # Fetch context OIDs (scalars or walks needed by transform)
            self._resolve_context(source, value_maps)

            # SNMP key_tag distinction:
            # - key_tag WITH explicit tag: transform both key and value
            # - key_tag WITHOUT explicit tag: data is in the OID suffix,
            #   value is irrelevant (e.g. RowStatus). Use key_tag-only path.
            if key_tag and explicit_tag:
                # Both key and value transforms
                results[name] = {
                    self._transform(key_tag, str(k).lstrip("."), value_maps, source=source):
                    self._transform(tag, v, value_maps, source=source)
                    for k, v in raw.items()
                }
            elif key_tag:
                # Transform applied to walk KEY (data in OID index)
                results[name] = {
                    str(k).lstrip("."): self._transform(
                        key_tag, str(k).lstrip("."), value_maps, source=source
                    )
                    for k, v in raw.items()
                }
            else:
                # Per-value pipeline (tag/regex/math in YAML declaration order)
                result = {
                    str(k).lstrip("."): self._apply_pipeline(v, source, tag, value_maps)
                    for k, v in raw.items()
                }
                # Aggregate: collapse dict → scalar
                aggregate = source.get("aggregate")
                if aggregate and aggregate in transforms.REGISTRY:
                    result = self._transform(aggregate, result, value_maps)
                results[name] = result

    # ------------------------------------------------------------------
    # Join (re-key walks to match sibling suffixes)
    # ------------------------------------------------------------------

    def _gather_join(self, walks, results):
        """Post-process: join walks by re-keying to match sibling suffixes."""
        for name, source in walks.items():
            join_def = source.get("join")
            if not join_def or name not in results:
                continue
            walk_data = results[name]
            if not isinstance(walk_data, dict) or not walk_data:
                continue
            join_positions = sorted(join_def.values())
            collect = source.get("collect") == "list"
            # Build join key → value mapping
            join_map = {}
            for suffix, val in walk_data.items():
                parts = str(suffix).split(".")
                join_parts = [parts[i] for i in join_positions if i < len(parts)]
                join_key = ".".join(join_parts)
                if collect:
                    join_map.setdefault(join_key, []).append(val)
                elif join_key not in join_map:
                    join_map[join_key] = val
            # Find sibling walk result
            sibling_data = None
            for other_name, other_val in results.items():
                if other_name != name and isinstance(other_val, dict) and other_val:
                    sibling_data = other_val
                    break
            if not sibling_data:
                continue
            # Re-key
            rekeyed = {}
            for sib_suffix in sibling_data:
                sib_parts = str(sib_suffix).split(".")
                sib_join_parts = [sib_parts[i] for i in join_positions if i < len(sib_parts)]
                sib_join_key = ".".join(sib_join_parts)
                if sib_join_key in join_map:
                    rekeyed[sib_suffix] = join_map[sib_join_key]
            results[name] = rekeyed

    # ------------------------------------------------------------------
    # Multi-OID (oids: {name: oid, ...})
    # ------------------------------------------------------------------

    def _gather_multi_oids(self, multi_oids, results, value_maps):
        """Walk multiple OIDs, combine by suffix or bulk scalar GET."""
        for name, source in multi_oids:
            oids_map = source["oids"]
            tag = source.get("tag", "")
            fmt = source.get("format")
            method = source.get("method", "walk")

            if method == "walk":
                walks = {}
                for oid_name, oid in oids_map.items():
                    raw = self.transport._walk_sync(oid)
                    for suffix, val in raw.items():
                        walks.setdefault(suffix, {})[oid_name] = str(val)
                if fmt:
                    combined = {}
                    for suffix, row in walks.items():
                        fmt_vals = {}
                        for fk, fv in row.items():
                            try:
                                fmt_vals[fk] = int(fv)
                            except (ValueError, TypeError):
                                fmt_vals[fk] = fv if fv is not None else ""
                        combined[suffix] = fmt.format(**fmt_vals)
                    results[name] = combined
                else:
                    results[name] = {
                        suffix: self._transform(tag, row, value_maps)
                        for suffix, row in walks.items()
                    }
            else:
                # Bulk scalar GET
                norm = {}
                for oid_name, oid in oids_map.items():
                    if not oid.endswith(".0"):
                        oid += ".0"
                    norm[oid_name] = oid
                raw = self.transport._get_scalars_sync(*norm.values())
                combined = {}
                for oid_name, oid in norm.items():
                    key = oid.lstrip(".")
                    val = raw.get(key) or raw.get(oid)
                    if val is not None:
                        val_type = str(type(val).__name__)
                        if "NoSuch" not in val_type and "EndOfMib" not in val_type:
                            combined[oid_name] = val
                results[name] = self._transform(tag, combined, value_maps)

    # ------------------------------------------------------------------
    # Walk columns (multi-column table walk)
    # ------------------------------------------------------------------

    def _gather_walk_columns(self, walk_columns, results, value_maps):
        """Walk multiple OID columns, zip by suffix, filter, transform."""
        for name, source in walk_columns:
            base_oid = source["oid"]
            columns = source.get("columns", {})
            tags = source.get("tags", {})
            row_filter = source.get("row_filter", {})

            # Walk each column
            walks = {}
            for col_name, col_num in columns.items():
                col_oid = f"{base_oid}.{col_num}"
                raw = self.transport._walk_sync(col_oid)
                for suffix, val in raw.items():
                    walks.setdefault(suffix, {})[col_name] = val

            # Row filter
            if row_filter:
                filtered = {}
                for suffix, row in walks.items():
                    keep = True
                    for filt_col, allowed in row_filter.items():
                        raw_val = row.get(filt_col)
                        if raw_val is None:
                            keep = False
                            break
                        try:
                            int_val = int(raw_val)
                        except (ValueError, TypeError):
                            int_val = None
                        str_val = str(raw_val)
                        if not isinstance(allowed, list):
                            allowed = [allowed]
                        if int_val not in allowed and str_val not in [str(a) for a in allowed]:
                            keep = False
                            break
                    if keep:
                        filtered[suffix] = row
                walks = filtered

            # Transform and build rows
            rows = []
            for suffix in sorted(walks.keys()):
                row = walks[suffix]
                out = {}
                for col_name, raw_val in row.items():
                    col_tag = tags.get(col_name, "")
                    if col_tag:
                        out[col_name] = self._transform(col_tag, raw_val, value_maps)
                    else:
                        out[col_name] = str(raw_val) if raw_val is not None else ""
                rows.append(out)
            results[name] = rows

    # ------------------------------------------------------------------
    # Context resolution (scalars/walks needed by transforms)
    # ------------------------------------------------------------------

    def _resolve_context(self, source, value_maps):
        """Fetch context OIDs and store in driver context."""
        if "context" not in source:
            return
        for ctx_key, ctx_src in source["context"].items():
            ctx_method = ctx_src.get("method", "get")
            if ctx_method == "walk" and ctx_src.get("collect") == "all":
                ctx_raw = self.transport._walk_sync(ctx_src["oid"])
                ctx_tag = ctx_src.get("tag", "")
                ctx_val = set()
                for v in ctx_raw.values():
                    if v is not None:
                        rv = self._transform(ctx_tag, v, value_maps) if ctx_tag else v
                        ctx_val.add(rv)
            else:
                ctx_val = self.transport._get_scalar_sync(ctx_src["oid"])
                ctx_tag = ctx_src.get("tag", "")
                if ctx_tag:
                    ctx_val = self._transform(ctx_tag, ctx_val, value_maps)
            self.context[ctx_key] = ctx_val

    # ------------------------------------------------------------------
    # RFC 2578 INDEX decomposition
    # ------------------------------------------------------------------

    @staticmethod
    def _decompose_rfc_index(suffix, index_fields):
        """RFC 2578 INDEX decomposition.

        Decomposes an OID suffix into named fields based on the MIB INDEX
        clause declaration. Each field type consumes a defined number of
        sub-identifiers per RFC 2578 §7.7:

            integer      — 1 sub-ID
            ipaddress    — 4 sub-IDs (fixed)
            octet_string — length prefix + N sub-IDs (variable)
            fixed_string — N sub-IDs (declared size, no length prefix)
            implied      — remaining sub-IDs (must be last field)

        Args:
            suffix: OID suffix string, e.g. "5.1.4.192.168.1.1"
            index_fields: list of {name, type} dicts from YAML

        Returns:
            dict of {field_name: typed_value}
            - integer → int
            - ipaddress → list[int] (4 octets)
            - octet_string/fixed_string/implied → list[int] (N octets)

        Raises:
            ValueError: malformed suffix (insufficient sub-IDs)
        """
        parts = [int(p) for p in suffix.split('.')]
        pos = 0
        result = {}

        for field in index_fields:
            name = field['name']
            ftype = field.get('type', 'integer')
            implied = field.get('implied', False)

            if pos > len(parts):
                raise ValueError(
                    f"RFC INDEX decomposition: insufficient sub-IDs in "
                    f"suffix '{suffix}' at field '{name}' (pos {pos}, "
                    f"have {len(parts)})"
                )

            if ftype == 'integer':
                if pos >= len(parts):
                    raise ValueError(
                        f"RFC INDEX: no sub-ID for integer field '{name}'"
                    )
                result[name] = parts[pos]
                pos += 1

            elif ftype == 'ipaddress':
                if pos + 4 > len(parts):
                    raise ValueError(
                        f"RFC INDEX: need 4 sub-IDs for ipaddress field "
                        f"'{name}', have {len(parts) - pos}"
                    )
                result[name] = parts[pos:pos + 4]
                pos += 4

            elif ftype == 'octet_string':
                if implied:
                    # IMPLIED: consume all remaining sub-IDs, no length prefix
                    result[name] = parts[pos:]
                    pos = len(parts)
                else:
                    # Length-prefixed variable
                    if pos >= len(parts):
                        raise ValueError(
                            f"RFC INDEX: no length prefix for "
                            f"octet_string field '{name}'"
                        )
                    length = parts[pos]
                    pos += 1
                    if pos + length > len(parts):
                        raise ValueError(
                            f"RFC INDEX: octet_string field '{name}' "
                            f"declares length {length} but only "
                            f"{len(parts) - pos} sub-IDs remain"
                        )
                    result[name] = parts[pos:pos + length]
                    pos += length

            elif ftype == 'fixed_string':
                size = field['size']
                if pos + size > len(parts):
                    raise ValueError(
                        f"RFC INDEX: fixed_string field '{name}' needs "
                        f"{size} sub-IDs, have {len(parts) - pos}"
                    )
                result[name] = parts[pos:pos + size]
                pos += size

        return result

    @staticmethod
    def _format_index_value(raw, fmt):
        """Format a decomposed RFC INDEX field value.

        Args:
            raw: typed value from _decompose_rfc_index (int or list[int])
            fmt: format string — 'ipv4', 'ipv6', 'mac', or None

        Returns:
            Formatted string representation.

        Raises:
            ValueError: insufficient octets for declared format
        """
        if fmt == 'ipv4':
            if not isinstance(raw, list) or len(raw) != 4:
                raise ValueError(
                    f"ipv4 format needs exactly 4 octets, got {raw}"
                )
            return '.'.join(str(o) for o in raw)

        elif fmt == 'ipv6':
            if not isinstance(raw, list) or len(raw) != 16:
                raise ValueError(
                    f"ipv6 format needs exactly 16 octets, got {raw}"
                )
            import ipaddress as _ipaddress
            return str(_ipaddress.IPv6Address(bytes(raw)))

        elif fmt == 'mac':
            if not isinstance(raw, list) or len(raw) != 6:
                raise ValueError(
                    f"mac format needs exactly 6 octets, got {raw}"
                )
            return ':'.join(f'{o:02x}' for o in raw)

        # No format: int → str, list → dot-joined
        if isinstance(raw, list):
            return '.'.join(str(o) for o in raw)
        return str(raw)

    def _gather_rfc_walk(self, raw, source, index_fields, value_maps,
                         attr_name):
        """Gather walk results using RFC 2578 INDEX decomposition.

        Decomposes each OID suffix per index_fields, builds result dict
        keyed by the declared key_field. Value comes from either the
        walked column or a decomposed index field (value_from_index).

        Note: value_from_index can equal key_field (e.g. ip attribute
        where the IP address is both the key and the value).
        """
        key_field = source.get("key_field")
        key_format = source.get("key_format")
        value_from = source.get("value_from_index")
        value_format = source.get("value_format")
        index_filter = source.get("index_filter")
        tag = self._resolve_tag(
            source.get("tag", ""), source, attr_name=attr_name
        )

        # Resolve context if needed (for transforms like ifindex_to_name)
        self._resolve_context(source, value_maps)

        result = {}
        for suffix, walked_value in raw.items():
            try:
                decomposed = self._decompose_rfc_index(suffix, index_fields)

                # Filter rows by decomposed index field values
                # e.g. index_filter: {addrType: 1} keeps only IPv4 entries
                if index_filter:
                    skip = False
                    for filt_name, filt_val in index_filter.items():
                        if decomposed.get(filt_name) != filt_val:
                            skip = True
                            break
                    if skip:
                        continue

                # Build dict key from declared key_field
                if key_field:
                    raw_key = decomposed.get(key_field, suffix)
                    key = self._format_index_value(raw_key, key_format)
                else:
                    key = suffix

                # Value: from decomposed index field or walked column
                if value_from:
                    raw_val = decomposed.get(value_from, "")
                    if value_format:
                        val = self._format_index_value(raw_val, value_format)
                    else:
                        val = raw_val  # pass typed value through
                else:
                    val = walked_value

            except ValueError as e:
                logger.debug("RFC INDEX skip suffix '%s': %s", suffix, e)
                continue

            result[key] = self._apply_pipeline(val, source, tag, value_maps)

        return result

    # ------------------------------------------------------------------
    # Legacy index decomposition (_skip, key, group, inner)
    # ------------------------------------------------------------------

    def _process_walk_index(self, raw, index_spec, tag, value_maps, source=None):
        """Route walk results through declared index structure."""
        components = []
        for elem in index_spec:
            if isinstance(elem, str):
                components.append({"role": elem, "tag": None})
            elif isinstance(elem, dict):
                components.append(dict(elem, tag=elem.get("tag")))

        has_group = any(c["role"] == "group" for c in components)
        if has_group:
            return self._index_group(raw, components, tag, value_maps, source=source)
        return self._index_strip(raw, components, tag, value_maps, source=source)

    def _index_strip(self, raw, components, tag, value_maps, source=None):
        """key + _skip: extract key element by position, skip others."""
        # Find position of the 'key' role
        key_pos = next((i for i, c in enumerate(components) if c["role"] in ("key", None)), 0)
        key_comp = components[key_pos] if key_pos < len(components) else {"tag": None}
        result = {}
        for k, v in raw.items():
            parts = str(k).lstrip(".").split(".")
            if key_pos < len(parts):
                new_key = parts[key_pos]
                if key_comp.get("tag"):
                    key_source = {**(source or {}), **key_comp}
                    new_key = self._transform(key_comp["tag"], new_key, value_maps, source=key_source)
                if source:
                    result[new_key] = self._apply_pipeline(v, source, tag, value_maps)
                else:
                    result[new_key] = self._transform(tag, v, value_maps) if tag else v
        return result

    def _index_group(self, raw, components, tag, value_maps, source=None):
        """group + inner: group walk results into nested dicts."""
        group_idx = next(i for i, c in enumerate(components) if c["role"] == "group")
        group_comp = components[group_idx]
        inner_comp = next((c for c in components if c["role"] == "inner"), {"tag": None})
        grouped = {}
        for k, v in raw.items():
            parts = str(k).lstrip(".").split(".")
            if len(parts) <= group_idx:
                continue
            group_key = parts[group_idx]
            if group_comp["tag"]:
                group_source = {**(source or {}), **group_comp}
                group_key = self._transform(group_comp["tag"], group_key, value_maps, source=group_source)
            inner_key = ".".join(parts[group_idx + 1:])
            if inner_comp["tag"]:
                inner_source = {**(source or {}), **inner_comp}
                inner_key = self._transform(inner_comp["tag"], inner_key, value_maps, source=inner_source)
            tv = self._transform(tag, v, value_maps, source=source) if tag else v
            grouped.setdefault(group_key, {})[inner_key] = tv
        return grouped

    # ------------------------------------------------------------------
    # Set — write path
    # ------------------------------------------------------------------

    def _find_rowstatus_for_oid(self, oid, wire_def=None):
        """Find RowStatus attr in wire_def for the same SNMP table as oid.

        Matches by OID prefix (same table = same OID prefix up to column).
        Returns (rs_oid_base, create_method) or (None, None).
        """
        if not wire_def:
            wire_def = self.context.get("_wire_def", {}) if self.context else {}
        # SNMP table OID: {table}.{column}.{index}
        # Input oid includes index (e.g. ...10.1.5.2). Wire OID is base (e.g. ...10.1.7).
        # Strip last 2 from input (column+index), strip last 1 from wire (column).
        # Both should yield the table OID (e.g. ...10.1).
        parts = oid.rsplit(".", 2)
        if len(parts) < 3:
            return None, None
        table_prefix = parts[0]  # everything before column.index

        for attr_name, attr_def in wire_def.get("attributes", {}).items():
            if attr_def.get("access") != "crud":
                continue
            proto_src = attr_def.get("sources", {}).get("snmp", {})
            if isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            rs_oid = proto_src.get("oid", "") if isinstance(proto_src, dict) else ""
            rs_table = rs_oid.rsplit(".", 1)[0] if rs_oid else ""
            if rs_table and rs_table == table_prefix:
                create_method = attr_def.get("create_method", self.protocol_defaults.get("create_method_default", "createAndWait"))
                return rs_oid, create_method
        return None, None

    def _apply_set_with_lifecycle(self, sets, row_index, wire_def=None):
        """SET with RowStatus lifecycle awareness for SNMP.

        If the table uses createAndWait, wrap in notInService(2)→set→active(1).
        """
        if row_index is not None and sets:
            oid = sets[0][0]  # first OID to determine table
            rs_oid_base, create_method = self._find_rowstatus_for_oid(oid, wire_def)
            if rs_oid_base and create_method != "createAndGo":
                rs_oid = f"{rs_oid_base}.{row_index}"
                self.transport._set_oids_sync((rs_oid, 2))  # notInService
                for oid_val in sets:
                    try:
                        self.transport._set_oids_sync(oid_val)
                    except Exception as e:
                        logger.debug(f"Field SET skipped ({oid_val[0]}): {e}")
                self.transport._set_oids_sync((rs_oid, 1))  # active
                return
        self.transport._set_oids_sync(*sets)

    def set_values(self, source: Dict, tokens: Dict,
                   value_maps: Dict = None) -> bool:
        """Execute SNMP SET operation(s).

        Resolution priority for each SET item:
        1. Explicit tag: → use that transform (legacy path)
        2. Explicit value: expression → token substitution (legacy path)
        3. Matrix dispatch: param → attr syntax → crude_*(direction=ingress)
        """
        row_index = source.get("_row_index")
        wire_def = source.get("_wire_def")
        sets = []
        items = source.get("sets", [source] if "oid" in source else [])
        for item in items:
            oid = item["oid"]
            if isinstance(oid, str) and "{" in oid:
                oid = self._apply_tokens(oid, tokens)
            if row_index is not None:
                oid = f"{oid}.{row_index}"

            tag = item.get("tag")
            val_expr = item.get("value")
            param = item.get("param")

            if tag or val_expr is not None:
                # Legacy path: explicit value expression + tag
                val = val_expr if val_expr is not None else 1
                if isinstance(val, str) and "{" in val:
                    val = self._apply_tokens(val, tokens)
                if tag:
                    val = self._transform(tag, val, value_maps)
            elif param or source.get("_attr_name"):
                # Matrix path: get raw value from tokens, apply crude_* SET
                param_name = (param if isinstance(param, str) else
                              param[0] if param else source.get("_attr_name"))
                val = tokens.get(param_name, tokens.get("value"))
                resolved_tag = self._resolve_tag("", {}, attr_name=param_name)
                if resolved_tag:
                    ctx = dict(self.context) if self.context else {}
                    ctx["_direction"] = "ingress"
                    if value_maps:
                        ctx["_value_maps"] = value_maps
                    val = transforms.resolve(resolved_tag, val, ctx=ctx,
                                             value_maps=value_maps)
            else:
                val = 1  # fallback default

            if (not oid.endswith(".0")
                    and row_index is None
                    and not source.get("is_cell")
                    and not item.get("is_cell")):
                oid += ".0"
            sets.append((oid, val))
        self._apply_set_with_lifecycle(sets, row_index, wire_def)
        return True

    def dispatch_batch(self, batch: list, index=None) -> bool:
        """GATE 3 INGRESS: CRUDE encode + SNMP batch dispatch.

        Builds OID list, dispatches as single SNMP SET.
        """
        if not batch:
            return True
        wire_def = batch[0][2].wire_def
        value_maps = batch[0][2].value_maps
        sets = []

        for wire_name, value, wire_ctx in batch:
            encoded = self._crude_encode(wire_name, value, wire_ctx, value_maps)
            proto_src = wire_ctx.proto_src
            if isinstance(proto_src, dict) and "write" in proto_src:
                proto_src = proto_src["write"]
            elif isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            if not isinstance(proto_src, dict):
                continue
            oid = proto_src.get("oid", "")
            if not oid:
                continue
            if index is not None:
                suffix = self._resolve_oid_suffix(index)
                oid = f"{oid}.{suffix}"
            elif not oid.endswith(".0"):
                oid += ".0"
            sets.append((oid, encoded))

        if sets:
            self._apply_set_with_lifecycle(sets, index, wire_def)
        return True

    def _resolve_oid_suffix(self, index, index_field=None):
        """Encode index to OID suffix string. Handles scalar and compound."""
        if isinstance(index, dict):
            suffix_parts = []
            for field, val in index.items():
                resolved_tag = self._resolve_tag("", {}, attr_name=field)
                if resolved_tag:
                    ctx = dict(self.context) if self.context else {}
                    ctx["_direction"] = "ingress"
                    val = transforms.resolve(resolved_tag, val, ctx=ctx)
                part = str(val)
                if " " in part:
                    hex_parts = part.split()
                    if all(len(p) == 2 for p in hex_parts):
                        try:
                            part = ".".join(str(int(p, 16)) for p in hex_parts)
                        except ValueError:
                            pass
                suffix_parts.append(part)
            return ".".join(suffix_parts)
        if index_field:
            resolved_tag = self._resolve_tag("", {}, attr_name=index_field)
            if resolved_tag:
                ctx = dict(self.context) if self.context else {}
                ctx["_direction"] = "ingress"
                index = transforms.resolve(resolved_tag, index, ctx=ctx)
        idx_str = str(index)
        if " " in idx_str:
            parts = idx_str.split()
            if all(len(p) == 2 for p in parts):
                try:
                    idx_str = ".".join(str(int(p, 16)) for p in parts)
                except ValueError:
                    pass
        return idx_str

    def create_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    fields: Dict, value_maps: Dict = None,
                    index_field: str = None,
                    create_method: str = "createAndWait",
                    **kwargs) -> bool:
        """Create a table row. Wire YAML declares the lifecycle method.

        createAndGo: SET RowStatus.index=4 (single operation)
        createAndWait: SET RowStatus.index=5, SET fields, SET RowStatus.index=1
        """
        oid_base = rs_source.get("oid", "")
        idx_str = self._resolve_oid_suffix(index, index_field)
        rs_oid = f"{oid_base}.{idx_str}"

        # Encode field values through matrix
        unsigned = set(self._driver_config.get("unsigned_syntaxes", []))
        sets = []
        for field_oid, value in fields.items():
            resolved_tag = self._resolve_tag("", {}, attr_name=field_oid)
            if resolved_tag:
                ctx = dict(self.context) if self.context else {}
                ctx["_direction"] = "ingress"
                ctx.update(kwargs)
                value = transforms.resolve(resolved_tag, value, ctx=ctx)
            # Unsigned syntaxes → Unsigned32 (declared in SNMP.yaml)
            syntax = self.attr_syntaxes.get(field_oid, "")
            if syntax in unsigned and isinstance(value, (int, str)):
                try:
                    from pysnmp.proto.rfc1902 import Unsigned32
                    value = Unsigned32(int(value))
                except (ValueError, TypeError):
                    pass
            sets.append((f"{field_oid}.{index}", value))

        if create_method == "createAndGo":
            # Single batch: all fields + RowStatus=4
            sets.append((rs_oid, 4))
            self.transport._set_oids_sync(*sets)
        else:
            # createAndWait: RowStatus=5, set fields one by one, RowStatus=1
            # Some tables reject batched field SETs — individual SETs are safest
            self.transport._set_oids_sync((rs_oid, 5))
            for oid_val in sets:
                try:
                    self.transport._set_oids_sync(oid_val)
                except Exception as e:
                    logger.debug(f"Field SET skipped ({oid_val[0]}): {e}")
            self.transport._set_oids_sync((rs_oid, 1))
        return True

    def delete_row(self, rs_source: Dict, rs_wire: str, index: Any, index_field: str = None, **kwargs) -> bool:
        """Delete a table row via RowStatus destroy.

        SNMP: SET RowStatus OID.index = 6 (destroy).
        """
        oid_base = rs_source.get("oid", "")
        idx_str = self._resolve_oid_suffix(index, index_field)
        rs_oid = f"{oid_base}.{idx_str}"
        self.transport._set_oids_sync((rs_oid, 6))
        return True

    @staticmethod
    def _apply_tokens(template: str, tokens: Dict) -> str:
        """Substitute {token} placeholders in OID/value strings."""
        result = template
        for key, val in tokens.items():
            result = result.replace("{" + key + "}", str(val))
        return result
