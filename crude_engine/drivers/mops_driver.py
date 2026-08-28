"""
MOPS.py — MOPS protocol driver for napalm-hios.

Layer: Driver. Translates wire YAML source dicts into MOPS operations.
Owns: get_multi batching, index keying, row filtering, tag dispatch.
Cannot: interpret data meaning, decide what to gather, know about schemas.
Talks to: mops_transport.py (raw I/O). Called by: engine (gather/set_values).
Wire output: str, int, float, bool, list, dict, None.
"""

import logging
from typing import Dict, List, Tuple, Any

from crude_engine.engine import crude as transforms
from crude_engine.drivers.base import BaseDriver

logger = logging.getLogger(__name__)


class MOPSDriver(BaseDriver):
    """MOPS protocol driver — gather and set via HTTPS/XML MIB operations."""

    # ------------------------------------------------------------------
    # Gather — main read path (3-phase batching)
    # ------------------------------------------------------------------

    def gather(self, sources: List[Tuple[str, Dict]],
               value_maps: Dict = None) -> Dict[str, Any]:
        """Gather attribute values via MOPS.

        Three-phase pipeline:
        1. Build merged query — one entry per (mib, table)
        2. Execute one get_multi for all tables
        3. Process each attribute using cached rows
        """
        results = {}

        # Phase 1: Build merged query
        mops_queries = {}  # (mib, table) → set of field names
        for name, source in sources:
            mib, table = source["mib"], source["table"]
            key = (mib, table)
            if key not in mops_queries:
                mops_queries[key] = set()
            # Collect fields needed
            fields_map = source.get("fields")
            if isinstance(fields_map, dict):
                mops_queries[key].update(fields_map.values())
            elif "field" in source:
                mops_queries[key].add(source["field"])
            # Index fields
            for idx_key in ("index_field", "inner_index_field"):
                idx = source.get(idx_key)
                if idx and idx != "_enumerate":
                    mops_queries[key].add(idx)
            # Filter fields
            ff = source.get("filter_field")
            if ff:
                mops_queries[key].add(ff)
            # Context sources (may reference other MOPS tables)
            if "context" in source:
                for ctx_key, ctx_src in source["context"].items():
                    if "mib" in ctx_src and "table" in ctx_src:
                        ctx_k = (ctx_src["mib"], ctx_src["table"])
                        if ctx_k not in mops_queries:
                            mops_queries[ctx_k] = set()
                        if "field" in ctx_src:
                            mops_queries[ctx_k].add(ctx_src["field"])

        # Phase 2: Execute one get_multi for all tables
        mops_cache = {}
        if mops_queries:
            queries = [
                (mib, table, list(fields))
                for (mib, table), fields in mops_queries.items()
            ]
            try:
                multi_result = self.transport.client.get_multi(
                    queries, decode_strings=False)
                for (mib, table) in mops_queries:
                    mops_cache[(mib, table)] = (
                        multi_result.get(mib, {}).get(table, []))
            except Exception:
                for key in mops_queries:
                    mops_cache[key] = []

        # Phase 3: Process each attribute using cached rows
        for name, source in sources:
            tag = self._resolve_tag(source.get("tag", ""), source, attr_name=name)
            mib, table = source["mib"], source["table"]
            cached_rows = mops_cache.get((mib, table), [])

            # Resolve context from cache
            self._resolve_context(source, mops_cache, value_maps)

            # Table walk: index_field or multi-field dict
            is_table = (source.get("index_field") is not None
                        or isinstance(source.get("fields"), dict))
            if is_table:
                result = self._list_to_dict(
                    source, tag, value_maps, rows=cached_rows
                )
                # Targeted cell read: pick single value from walked dict
                idx_filter = source.get("_index_filter")
                if idx_filter is not None and isinstance(result, dict):
                    result = result.get(str(idx_filter), result.get(idx_filter))
                aggregate = source.get("aggregate")
                if aggregate and aggregate in transforms.REGISTRY:
                    result = self._transform(aggregate, result, value_maps)
                results[name] = result
            else:
                # Scalar: first row, single field
                val = (cached_rows[0].get(source.get("field"))
                       if cached_rows and "field" in source else None)
                if val is None:
                    continue
                results[name] = self._apply_pipeline(val, source, tag, value_maps)

        return results

    # ------------------------------------------------------------------
    # List→dict conversion (the core MOPS table handler)
    # ------------------------------------------------------------------

    def _list_to_dict(self, source: Dict, tag: str,
                      value_maps: Dict, rows: list = None) -> Dict:
        """Convert MOPS List[Dict] table response to {index: value} dict.

        Handles: index_field, inner_index_field, fields_map, filter,
        format strings, key_tag, inner_key_tag.
        """
        mib, table = source["mib"], source["table"]
        index_field = source.get("index_field")
        inner_index_field = source.get("inner_index_field")

        # Multi-field vs single-field
        fields_map = None
        if isinstance(source.get("fields"), dict):
            fields_map = source["fields"]
            field = None
        else:
            field = source["field"]

        # Fetch rows if not pre-fetched (fallback for bulk: false)
        if rows is None:
            request_fields = list(fields_map.values()) if fields_map else [field]
            if index_field and index_field != "_enumerate" and index_field not in request_fields:
                request_fields.append(index_field)
            if inner_index_field and inner_index_field != "_enumerate" and inner_index_field not in request_fields:
                request_fields.append(inner_index_field)
            try:
                rows = self.transport.client.get(mib, table, attributes=request_fields,
                                                 decode_strings=False)
            except Exception:
                rows = []
        if not rows:
            return {}

        # Pre-filter rows
        filter_field = source.get("filter_field")
        filter_value = source.get("filter_value")
        if filter_field and filter_value is not None:
            rows = [r for r in rows
                    if str(r.get(filter_field, "")) == str(filter_value)]
            if not rows:
                return {}

        # Resolve tag
        base_tag = tag
        hex_decode_first = base_tag == "hex_value_map"
        if base_tag in ("value_map", "hex_value_map"):
            base_tag = source.get("map", base_tag)

        fmt = source.get("format")

        result = {}
        exclude_fields = set()
        if index_field and index_field != "_enumerate":
            exclude_fields.add(index_field)
        if inner_index_field and inner_index_field != "_enumerate":
            exclude_fields.add(inner_index_field)
        reverse_map = {v: k for k, v in fields_map.items()} if fields_map else None

        for i, row in enumerate(rows, start=1):
            # Key extraction
            if index_field == "_enumerate":
                key = str(i)
            elif index_field:
                key = str(row.get(index_field, i))
            else:
                idx_key = next((k for k in row if k.startswith("_idx_")), None)
                key = str(row.get(idx_key, i)) if idx_key else str(i)

            if fields_map:
                # Multi-field: rename MIB fields → logical names
                combined = {
                    reverse_map.get(k, k): v
                    for k, v in row.items()
                    if k not in exclude_fields
                }
                if fmt:
                    fmt_vals = {}
                    for fk, fv in combined.items():
                        try:
                            fmt_vals[fk] = int(fv)
                        except (ValueError, TypeError):
                            fmt_vals[fk] = str(fv) if fv is not None else ""
                    val = fmt.format(**fmt_vals)
                elif base_tag:
                    val = self._transform(base_tag, combined, value_maps)
                else:
                    val = combined
            else:
                val = row.get(field)
                if val is not None:
                    if hex_decode_first:
                        val = self._transform("hex_string", val, value_maps)
                    val = self._apply_pipeline(val, source, base_tag, value_maps)

            # Compound index nesting
            if inner_index_field:
                if inner_index_field == "_enumerate":
                    group = result.setdefault(key, {})
                    inner_key = str(len(group) + 1)
                else:
                    inner_key = str(row.get(inner_index_field, i))
                result.setdefault(key, {})[inner_key] = val
            elif source.get("collect") == "list":
                result.setdefault(key, []).append(val)
            else:
                result[key] = val

        # Apply inner_key_tag
        inner_key_tag = source.get("inner_key_tag")
        if inner_index_field and inner_key_tag:
            result = {
                gk: {
                    self._transform(inner_key_tag, ik, value_maps, source=source): iv
                    for ik, iv in group.items()
                }
                for gk, group in result.items()
            }

        # Apply key_tag
        key_tag = source.get("key_tag")
        if key_tag:
            result = {
                self._transform(key_tag, k, value_maps, source=source): v
                for k, v in result.items()
            }

        return result

    # ------------------------------------------------------------------
    # Context resolution
    # ------------------------------------------------------------------

    def _resolve_context(self, source, mops_cache, value_maps):
        """Resolve context values from MOPS cache."""
        if "context" not in source:
            return
        for ctx_key, ctx_src in source["context"].items():
            if "mib" in ctx_src and "table" in ctx_src:
                ctx_rows = mops_cache.get(
                    (ctx_src["mib"], ctx_src["table"]), [])
                ctx_field = ctx_src.get("field")
                if ctx_src.get("collect") == "all":
                    ctx_tag = ctx_src.get("tag", "")
                    ctx_val = set()
                    for row in ctx_rows:
                        rv = row.get(ctx_field)
                        if rv is not None:
                            if ctx_tag:
                                rv = self._transform(ctx_tag, rv, value_maps)
                            ctx_val.add(rv)
                    self.context[ctx_key] = ctx_val
                    continue
                elif ctx_rows and ctx_field:
                    ctx_val = ctx_rows[0].get(ctx_field)
                else:
                    ctx_val = None
            else:
                # Non-MOPS context — dispatch individually
                ctx_val = None
            ctx_tag = ctx_src.get("tag", "")
            if ctx_tag and ctx_val is not None:
                ctx_val = self._transform(ctx_tag, ctx_val, value_maps)
            self.context[ctx_key] = ctx_val

    # ------------------------------------------------------------------
    # Set — write path
    # ------------------------------------------------------------------

    def set_values(self, source: Dict, tokens: Dict,
                   value_maps: Dict = None) -> bool:
        """Execute MOPS SET operation.

        Resolution priority for each field:
        1. Explicit tag: → use that transform (legacy path)
        2. Explicit value: expression → token substitution (legacy path)
        3. Matrix dispatch: _attr_name → attr syntax → crude_*(direction=ingress)
        """
        mib = source.get("mib", source.get("table", ""))
        table = source.get("table", "")
        wire_def = source.get("_wire_def")
        row_index = source.get("_row_index")
        index = {
            k: self._apply_tokens(str(v), tokens)
            for k, v in source.get("index", {}).items()
        }
        # Row index from engine SET path (table row update)
        if row_index is not None and not index:
            if isinstance(row_index, dict):
                index = row_index
            else:
                idx_field = source.get("index_field", "")
                if idx_field:
                    index = {idx_field: str(row_index)}
        payload = {}
        fields = source.get("fields", {})
        tags = source.get("tags", {})
        val_expr = source.get("value")
        attr_name = source.get("_attr_name")

        if "field" in source:
            tag = source.get("tag")
            if tag:
                # Legacy path: explicit tag
                fields = {source["field"]: val_expr if val_expr is not None else 1}
                tags = {source["field"]: tag}
            elif attr_name:
                # Matrix path: get raw value, apply crude_* SET
                val = tokens.get(attr_name, tokens.get("value"))
                resolved_tag = self._resolve_tag("", {}, attr_name=attr_name)
                if resolved_tag:
                    ctx = dict(self.context) if self.context else {}
                    ctx["_direction"] = "ingress"
                    if value_maps:
                        ctx["_value_maps"] = value_maps
                    val = transforms.resolve(resolved_tag, val, ctx=ctx,
                                             value_maps=value_maps)
                payload[source["field"]] = str(val)
                self._apply_set_with_lifecycle(mib, table, payload, index, wire_def)
                return True
            else:
                fields = {source["field"]: 1}
                tags = {source["field"]: None}

        for k, v in fields.items():
            rv = self._apply_tokens(str(v), tokens)
            if k in tags and tags[k]:
                # SET context: transforms get _direction=ingress
                source_ctx = {"_direction": "ingress"}
                rv = self._transform(tags[k], rv, value_maps, source=source_ctx)
            payload[k] = rv
        self._apply_set_with_lifecycle(mib, table, payload, index, wire_def)
        return True

    def dispatch_batch(self, batch: list, index=None) -> bool:
        """GATE 3 INGRESS: CRUDE encode + MOPS batch dispatch.

        Groups by (mib, table) for atomic SET per table.
        """
        if not batch:
            return True
        # Group by (mib, table)
        groups = {}  # (mib, table) -> {field: encoded_value}
        wire_def = batch[0][2].wire_def  # all share same wire source
        value_maps = batch[0][2].value_maps

        for wire_name, value, wire_ctx in batch:
            encoded = self._crude_encode(wire_name, value, wire_ctx, value_maps)
            proto_src = wire_ctx.proto_src
            if isinstance(proto_src, dict) and "write" in proto_src:
                proto_src = proto_src["write"]
            elif isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            if not isinstance(proto_src, dict):
                continue
            mib = proto_src.get("mib", proto_src.get("table", ""))
            table = proto_src.get("table", "")
            field = proto_src.get("field", wire_name)
            idx_field = proto_src.get("index_field", "")
            groups.setdefault((mib, table, idx_field), {})[field] = str(encoded)

        for (mib, table, idx_field), payload in groups.items():
            idx = None
            if index is not None:
                if isinstance(index, dict):
                    idx = {k: str(v) for k, v in index.items()}
                elif idx_field:
                    idx = {idx_field: str(index)}
            self._apply_set_with_lifecycle(mib, table, payload, idx, wire_def)
        return True

    def _find_rowstatus_for_table(self, table, wire_def=None):
        """Find RowStatus attr in wire_def for the given MOPS table.

        Scans wire attrs for one with access: crud in the same table.
        Returns (rs_field, create_method) or (None, None).
        """
        if not wire_def:
            wire_def = self.context.get("_wire_def", {}) if self.context else {}
        for attr_name, attr_def in wire_def.get("attributes", {}).items():
            if attr_def.get("access") != "crud":
                continue
            proto_src = attr_def.get("sources", {}).get("mops", {})
            if isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            if isinstance(proto_src, dict) and proto_src.get("table") == table:
                rs_field = proto_src.get("field", attr_name)
                create_method = attr_def.get("create_method", self.protocol_defaults.get("create_method_default", "createAndWait"))
                return rs_field, create_method
        return None, None

    def _apply_set_with_lifecycle(self, mib, table, payload, index, wire_def=None):
        """SET with RowStatus lifecycle awareness.

        If the table has a RowStatus column and uses createAndWait,
        wrap the SET in notInService(2) → set → active(1).
        Otherwise plain SET.
        """
        if index:
            rs_field, create_method = self._find_rowstatus_for_table(table, wire_def)
            if rs_field and create_method != "createAndGo":
                self._rowstatus_lifecycle(mib, table, rs_field, index, payload,
                                          "update", create_method)
                return
        self.transport._apply_set(mib, table, payload, index=index)

    def _resolve_row_index(self, rs_source, index, index_field):
        """Resolve row index to protocol-ready dict."""
        if not index_field:
            index_field = rs_source.get("index_field", "")
        if isinstance(index, dict):
            encoded = {}
            for field, val in index.items():
                resolved_tag = self._resolve_tag("", {}, attr_name=field)
                if resolved_tag:
                    ctx = dict(self.context) if self.context else {}
                    ctx["_direction"] = "ingress"
                    val = transforms.resolve(resolved_tag, val, ctx=ctx)
                encoded[field] = str(val)
            return encoded
        if index_field:
            idx_val = index
            resolved_tag = self._resolve_tag("", {}, attr_name=index_field)
            if resolved_tag:
                ctx = dict(self.context) if self.context else {}
                ctx["_direction"] = "ingress"
                idx_val = transforms.resolve(resolved_tag, idx_val, ctx=ctx)
            return {index_field: str(idx_val)}
        return {}

    def _encode_row_payload(self, fields):
        """Encode field values through CRUDE matrix for wire."""
        payload = {}
        for field_name, value in fields.items():
            resolved_tag = self._resolve_tag("", {}, attr_name=field_name)
            if resolved_tag:
                ctx = dict(self.context) if self.context else {}
                ctx["_direction"] = "ingress"
                value = transforms.resolve(resolved_tag, value, ctx=ctx)
            payload[field_name] = str(value)
        return payload

    def _rowstatus_lifecycle(self, mib, table, rs_field, idx, payload, intent, create_method):
        """Execute RowStatus state machine.

        intent="create": createAndGo(4) or createAndWait(5)→set→active(1)
        intent="update": notInService(2)→set→active(1)
        """
        if intent == "create":
            if create_method == "createAndGo":
                payload[rs_field] = "4"
                self.transport._apply_set(mib, table, payload, index=idx)
            else:
                self.transport._apply_set(mib, table, {rs_field: "5"}, index=idx)
                if payload:
                    self.transport._apply_set(mib, table, payload, index=idx)
                self.transport._apply_set(mib, table, {rs_field: "1"}, index=idx)
        elif intent == "update":
            if create_method == "createAndGo":
                # createAndGo tables allow direct SET on active rows
                self.transport._apply_set(mib, table, payload, index=idx)
            else:
                # createAndWait tables need notInService→set→active
                self.transport._apply_set(mib, table, {rs_field: "2"}, index=idx)
                if payload:
                    self.transport._apply_set(mib, table, payload, index=idx)
                self.transport._apply_set(mib, table, {rs_field: "1"}, index=idx)

    def create_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    fields: Dict, value_maps: Dict = None,
                    index_field: str = None,
                    create_method: str = "createAndWait",
                    **kwargs) -> bool:
        """Create a table row via RowStatus lifecycle."""
        mib = rs_source.get("mib", "")
        table = rs_source.get("table", "")
        rs_field = rs_source.get("field", rs_wire)
        idx = self._resolve_row_index(rs_source, index, index_field)
        payload = self._encode_row_payload(fields)
        self._rowstatus_lifecycle(mib, table, rs_field, idx, payload, "create", create_method)
        return True

    def update_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    fields: Dict, value_maps: Dict = None,
                    index_field: str = None,
                    create_method: str = "createAndWait",
                    **kwargs) -> bool:
        """Update an existing table row via RowStatus lifecycle."""
        mib = rs_source.get("mib", "")
        table = rs_source.get("table", "")
        rs_field = rs_source.get("field", rs_wire)
        idx = self._resolve_row_index(rs_source, index, index_field)
        payload = self._encode_row_payload(fields)
        self._rowstatus_lifecycle(mib, table, rs_field, idx, payload, "update", create_method)
        return True

    def delete_row(self, rs_source: Dict, rs_wire: str, index: Any,
                    index_field: str = None, **kwargs) -> bool:
        """Delete a table row via RowStatus destroy.

        MOPS: POST with RowStatus=6 (destroy).
        """
        mib = rs_source.get("mib", "")
        table = rs_source.get("table", "")
        rs_field = rs_source.get("field", rs_wire)

        payload = {rs_field: "6"}  # destroy
        idx = self._resolve_row_index(rs_source, index, index_field)
        self.transport._apply_set(mib, table, payload, index=idx)
        return True

    @staticmethod
    def _apply_tokens(template: str, tokens: Dict) -> str:
        """Substitute {token} placeholders."""
        result = template
        for key, val in tokens.items():
            result = result.replace("{" + key + "}", str(val))
        return result
