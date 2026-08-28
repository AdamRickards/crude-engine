"""
interpreter.py — YAML-driven schema engine (crude-engine).

Layer: Engine. Reads schema YAMLs, resolves wire sources, dispatches
to drivers, applies transforms, shapes canonical output.
Cannot: hardcode protocol-specific behavior, know about OIDs/CLI commands.
Talks to: schemas (YAML), wire (YAML), drivers (gather/set_values).
The NAPALM adapter is a consumer; it does not belong in this module.
"""

import dataclasses
import os
import yaml
import re
import logging
import copy
from typing import Any, Dict, List, Optional

from crude_engine.engine import crude as transforms

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class ResolvedIntent:
    """Frozen intent produced by resolve_intent, consumed by execute_resolved."""
    method_name: str
    schema_def: dict
    method_def: dict
    schema_attrs: dict
    methods: dict
    clean_kwargs: dict
    index_list: list
    direction: str       # "egress" or "ingress"
    validate: bool
    tracing: bool        # whether to record pipeline trace
    trace: list          # mutable [] or None — frozen prevents reassignment, not append


@dataclasses.dataclass(frozen=True)
class SchemaContext:
    """Output of Gate 1. Consumed by engine pipeline runners."""
    schema_attrs: dict
    method_def: dict
    methods: dict
    defaults: dict
    primary_key: Optional[str]
    index_fields: list
    feature_id: str


@dataclasses.dataclass(frozen=True)
class WireContext:
    """Output of Gate 2. Resolved wire context for a single schema attr."""
    wire_def: dict          # full wire YAML (for value_maps, other attrs)
    wire_attr: dict         # the specific attr dict
    proto_src: dict         # raw sources dict (caller resolves read/write branch)
    value_maps: dict        # wire_def["value_maps"]
    access: str             # wire_attr["access"] (default "r")
    wire_name: str          # the wire attr name
    wire_source: str        # wire source filename (for grouping)
    syntax: str             # wire_attr["syntax"]
    schema_type: str        # wire_attr["type"] (renamed to avoid builtin)
    validation: dict        # wire_attr["validation"] (for constraint checks)


class FeatureEngine:


    """Load YAML feature definitions, execute getters and setters."""

    # ==================================================================
    # Shape normalisation
    # ==================================================================

    @staticmethod
    def _coerce(value, target_shape):
        """Normalise value to target shape. Called by step handlers before logic.

        target_shape:
          "dict"   — scalar→{"0": v}, list→{str(i): v}, dict→unchanged
          "list"   — scalar→[v], dict→values(), list→unchanged
          "scalar" — dict→first value, list→first element, scalar→unchanged
        """
        if target_shape == "dict":
            if isinstance(value, dict):
                return value
            if isinstance(value, list):
                return {str(i): v for i, v in enumerate(value)}
            return {"0": value} if value is not None else {}
        if target_shape == "list":
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return list(value.values())
            return [value] if value is not None else []
        if target_shape == "scalar":
            if isinstance(value, dict):
                return next(iter(value.values()), None)
            if isinstance(value, list):
                return value[0] if value else None
            return value
        return value

    # ==================================================================
    # PUBLIC API — Adapter ↔ Engine boundary
    # CAN ACCESS: schemas (via load_feature), wire (via gates)
    # CANNOT ACCESS: transports, drivers directly
    # ==================================================================

    def resolve_intent(self, method_name: str, is_setter: bool = False,
                       **kwargs) -> ResolvedIntent:
        """Resolve user call into a frozen intent. Protocol/transport-independent."""
        feature_id = self._find_feature(method_name)
        schema_def = self.load_feature(feature_id)
        tracing = kwargs.pop("trace", False) or schema_def.get("debug", False)
        validate = kwargs.pop("validate", True)
        trace = [] if tracing else None
        direction = "ingress" if is_setter else "egress"

        method_def, schema_attrs, methods = self._load_method(method_name, schema_def)
        kwargs, index_list = self._resolve_intent(
            kwargs, schema_attrs, method_def, methods)

        if direction == "ingress":
            kwargs = self._apply_assemble(kwargs, schema_attrs, method_def)

        return ResolvedIntent(
            method_name=method_name,
            schema_def=schema_def,
            method_def=method_def,
            schema_attrs=schema_attrs,
            methods=methods,
            clean_kwargs=kwargs,
            index_list=index_list,
            direction=direction,
            validate=validate,
            tracing=tracing,
            trace=trace,
        )

    def execute_resolved(self, resolved: ResolvedIntent, protocol: str,
                         transport: Any) -> Any:
        """Execute a resolved intent against a protocol and transport.

        Always returns the result. Trace stored on self.last_trace.
        """
        trace = resolved.trace
        kwargs = dict(resolved.clean_kwargs)

        # Gate 1 — always produces context (validates ingress when validate=True)
        schema_ctx = self._gate1_validate(resolved, trace)
        mtype = schema_ctx.method_def.get("type", "dict")

        # Pipeline dispatch
        if resolved.direction == "egress":
            result = self._pipeline_egress(
                schema_ctx, protocol, transport, trace, resolved.index_list)
        elif mtype in ("create", "delete"):
            if resolved.index_list and resolved.index_list[0] is not None:
                kwargs["index"] = resolved.index_list[0]
            result = self._pipeline_crud(
                schema_ctx, protocol, transport,
                trace=trace, validate=resolved.validate, **kwargs)
        else:
            result = self._pipeline_ingress(
                kwargs, resolved.index_list, schema_ctx,
                protocol, transport, resolved.validate, trace)

        # Gate 1 exit — validate output contract (egress only)
        if resolved.validate and resolved.direction == "egress":
            result = self._gate1_exit(result, schema_ctx, trace)

        self.last_trace = trace
        return result

    def execute(self, method_name: str, protocol: str, transport: Any,
                is_setter: bool = False, **kwargs) -> Any:
        """Execute a getter or setter by method name.

        Convenience wrapper around resolve_intent + execute_resolved.
        Trace available via last_trace after call.
        """
        resolved = self.resolve_intent(method_name, is_setter=is_setter, **kwargs)
        return self.execute_resolved(resolved, protocol, transport)

    def _shape_table_output(self, method_def: Dict, schema_attrs: Dict,
                            walked: Dict, primary_key: str,
                            method_index_fields: List, protocol: str) -> Any:
        """Shape walked data into keyed table output. Used by _execute_egress.

        Handles: compound index decomposition, key_map remapping,
        membership_of, per-row compute, type:list / list_append.
        """
        defaults = method_def.get("defaults", {})
        key_map = method_def.get("key_map")
        pk_data = walked.get(primary_key, {})
        if not isinstance(pk_data, dict):
            return {}

        # Compound index decomposition (method declares index_fields = suffixes are compound)
        if method_index_fields:
            last_is_implied = method_def.get("index_type") == "implied_string"

            for suffix in pk_data:
                decomposed = self._decompose_index(str(suffix), method_index_fields, last_is_implied)
                for field_name, field_value in decomposed.items():
                    if field_name not in walked:
                        walked[field_name] = {}
                    walked[field_name][suffix] = field_value

        # Build keyed rows
        result = {}
        for idx, pk_value in pk_data.items():
            output_key = pk_value
            entry = dict(defaults)
            all_data = {}
            output_type = method_def.get("type", "dict")
            for schema_name in schema_attrs:
                # Primary key: skip for dict output (it's the dict key)
                # Include for list/list_append (needs to be in each row)
                # Include for compound index tables (decomposes into fields)
                if schema_name == primary_key:
                    all_data[schema_name] = pk_value
                attr_data = walked.get(schema_name, {})
                if isinstance(attr_data, dict) and attr_data:
                    all_data[schema_name] = attr_data.get(idx, defaults.get(schema_name, ""))

            # Per-row compute
            for schema_name, attr_ref in schema_attrs.items():
                compute = attr_ref.get("compute") if isinstance(attr_ref, dict) else None
                if not compute:
                    continue
                from_fields = compute.get("from", [])
                fmt = compute.get("format", "")
                fallback = compute.get("fallback")
                expr = compute.get("expr", "")
                if all(f in all_data for f in from_fields):
                    vals = {f: all_data[f] for f in from_fields}
                    if fmt:
                        fmt_vals = {}
                        for f, v in vals.items():
                            try:
                                fmt_vals[f] = int(v)
                            except (ValueError, TypeError):
                                fmt_vals[f] = v if v is not None else ""
                        if schema_name in defaults:
                            entry[schema_name] = fmt.format(**fmt_vals)
                    elif expr:
                        try:
                            result_val = eval(expr, {"__builtins__": {"len": len, "str": str, "int": int, "list": list}}, vals)
                            if compute.get("sort") == "natural" and isinstance(result_val, dict):
                                result_val = dict(sorted(result_val.items(),
                                    key=lambda x: (0 if '/' in x[0] and x[0][0].isdigit() else 1,
                                                   [int(n) if n.isdigit() else n for n in x[0].replace('/', ' ').split()])))
                            if schema_name in defaults:
                                entry[schema_name] = result_val
                        except Exception as e:
                            logger.warning("compute expr failed for %s: %s", schema_name, e)
                elif fallback and fallback in all_data:
                    if schema_name in defaults:
                        entry[schema_name] = all_data[fallback]

            for k in defaults:
                if k in all_data:
                    entry[k] = all_data[k]

            output_type = method_def.get("type", "dict")
            if output_type == "list_append":
                result.setdefault(output_key, []).append(entry)
            else:
                result[output_key] = entry

        # Key remapping via context map
        if isinstance(key_map, str):
            ctx_map = self._resolve_context_map(key_map)
            if ctx_map:
                if method_index_fields:
                    remapped = {}
                    for k, v in result.items():
                        key_parts = []
                        for i, field in enumerate(method_index_fields):
                            fval = walked.get(field, {}).get(k, "")
                            if i == 0:
                                fval = ctx_map.get(str(fval), str(fval))
                            key_parts.append(str(fval))
                        remapped[":".join(key_parts)] = v
                    result = remapped
                else:
                    result = {ctx_map.get(str(k), str(k)): v for k, v in result.items()}

        # List conversion
        if method_def.get("type") == "list":
            return list(result.values())

        return result

    # ------------------------------------------------------------------
    # Membership resolution
    # ------------------------------------------------------------------



    # ==================================================================
    # SCHEMA ↔ SCHEMA (formatter — intra-layer)
    # ==================================================================

    # ------------------------------------------------------------------
    # v2.7 Formatter Functions
    # Signature constraint: (gathered: dict, schema_attrs: dict) → dict
    # No protocol, no transport, no driver. Schema-layer only.
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_one(target_name, compute, data):
        """Evaluate a single compute declaration against a data dict.

        Returns (value, True) on success, (None, False) on skip.
        Used by _apply_compute (flat gathered) and _apply_sub_tables (per-row).
        """
        from_fields = compute.get("from", [])
        fmt = compute.get("format", "")
        expr = compute.get("expr", "")
        fallback = compute.get("fallback")
        if all(f in data for f in from_fields):
            vals = {f: data[f] for f in from_fields}
            if fmt:
                fmt_vals = {}
                for f, v in vals.items():
                    try:
                        fmt_vals[f] = int(v)
                    except (ValueError, TypeError):
                        fmt_vals[f] = v if v is not None else ""
                return fmt.format(**fmt_vals), True
            elif expr:
                try:
                    result_val = eval(expr, {"__builtins__": {"len": len, "str": str, "int": int}}, vals)
                    if compute.get("sort") == "natural" and isinstance(result_val, dict):
                        result_val = dict(sorted(result_val.items(),
                            key=lambda x: (0 if '/' in x[0] and x[0][0].isdigit() else 1,
                                           [int(n) if n.isdigit() else n for n in x[0].replace('/', ' ').split()])))
                    return result_val, True
                except Exception as e:
                    logger.warning("compute expr failed for %s: %s", target_name, e)
        elif fallback and fallback in data:
            return data[fallback], True
        return None, False

    @staticmethod
    def _apply_compute(gathered: Dict, schema_attrs: Dict) -> Dict:
        """Derive values from other gathered attrs. Egress only.

        Supports: format (string assembly), expr (eval), fallback, sort.
        """
        for schema_name, attr_ref in schema_attrs.items():
            compute = attr_ref.get("compute") if isinstance(attr_ref, dict) else None
            if not compute:
                continue
            value, ok = FeatureEngine._compute_one(schema_name, compute, gathered)
            if ok:
                gathered[schema_name] = value
        return gathered

    @staticmethod
    def _apply_assemble(kwargs: Dict, schema_attrs: Dict,
                        method_def: Dict = None) -> Dict:
        """Assemble wire values from multiple user kwargs. Ingress only.

        Reverse of compute — builds one value from multiple fields.
        Schema attr declares assemble: "{ip_address}/{prefix_length}"
        Respects method fields: restriction if declared.
        """
        allowed = method_def.get("fields") if method_def else None
        for schema_name, attr_ref in schema_attrs.items():
            if schema_name in kwargs:
                continue
            if allowed and schema_name not in allowed:
                continue
            if not isinstance(attr_ref, dict):
                continue
            assemble_fmt = attr_ref.get("assemble") or attr_ref.get("set_format")
            if not assemble_fmt:
                continue
            fields = re.findall(r'\{(\w+)\}', assemble_fmt)
            if fields and all(f in kwargs for f in fields):
                kwargs[schema_name] = assemble_fmt.format(**kwargs)
                # Consume template fields that aren't schema attrs
                for f in fields:
                    if f not in schema_attrs:
                        kwargs.pop(f, None)
        return kwargs

    def _apply_sub_tables(self, result: Dict, method_def: Dict,
                          gathered: Dict, schema_attrs: Dict) -> Dict:
        """Build nested dicts from walked table data. Egress only.

        Handles: dict pk_data (table walk), scalar pk_data (single value + child_key),
        field_map for row building, key_map for key resolution.
        """
        sub_tables = method_def.get("sub_tables", {})
        for sub_key, sub_def in sub_tables.items():
            pk = sub_def.get("primary_key")
            sub_field_map = sub_def.get("field_map", {})
            sub_defaults = sub_def.get("defaults", {})
            pk_data = gathered.get(pk, {})
            child_key = sub_def.get("child_key")
            if not isinstance(pk_data, dict):
                row = copy.deepcopy(sub_defaults) if sub_defaults else {}
                if sub_field_map:
                    for field, attr_name in sub_field_map.items():
                        val = gathered.get(attr_name)
                        if val is not None:
                            row[field] = val
                elif pk_data is not None:
                    row[pk] = pk_data
                if child_key:
                    result[sub_key] = {child_key: row}
                else:
                    result[sub_key] = row
                continue
            sub_result = {}
            for idx, pk_value in pk_data.items():
                row = copy.deepcopy(sub_defaults) if sub_defaults else {}
                for field, attr_name in sub_field_map.items():
                    attr_ref = schema_attrs.get(attr_name)
                    compute = attr_ref.get("compute") if isinstance(attr_ref, dict) else None
                    if compute:
                        # Compute: derive from row data already populated (YAML order)
                        value, ok = self._compute_one(field, compute, row)
                        if ok:
                            row[field] = value
                    else:
                        # Regular: populate from gathered table data
                        attr_data = gathered.get(attr_name, {})
                        if isinstance(attr_data, dict):
                            val = attr_data.get(idx)
                            if val is not None:
                                row[field] = val
                        elif attr_data is not None:
                            row[field] = attr_data
                sub_result[idx] = row if row else pk_value
            # Key resolution on sub_table keys
            sub_key_map = sub_def.get("key_map")
            if isinstance(sub_key_map, str):
                ctx_map = self._resolve_context_map(sub_key_map)
                if ctx_map:
                    sub_result = {ctx_map.get(str(k), str(k)): v for k, v in sub_result.items()}
            result[sub_key] = sub_result
        return result

    @staticmethod
    def _apply_lookup(gathered: Dict, schema_attrs: Dict) -> Dict:
        """Resolve lookup: chains from already-gathered data. Egress only.

        Ported from v2.6 _resolve_lookups — same algorithm, but reads from
        gathered dict instead of calling the driver. Phase A already gathered
        all lookup source data with index_field rekey applied.

        Processes in YAML declaration order so chained lookups resolve correctly
        (A → B → C: A gathered, B resolves from A, C resolves from B).

        No protocol, no transport, no wire access. Schema-layer only.
        """
        # Group lookups by from: source, preserving YAML order for chains
        from_groups = {}   # group_key → [(attr_name, lookup)]
        from_order = []
        for attr_name, attr_def in schema_attrs.items():
            if not isinstance(attr_def, dict):
                continue
            lookup = attr_def.get("lookup")
            if not lookup:
                continue
            from_val = lookup.get("from")
            if not from_val:
                continue
            group_key = tuple(from_val) if isinstance(from_val, list) else from_val
            if group_key not in from_groups:
                from_groups[group_key] = []
                from_order.append(group_key)
            from_groups[group_key].append((attr_name, lookup))

        if not from_groups:
            return gathered

        for group_key in from_order:
            group = from_groups[group_key]

            # Resolve from: data — static list or already-gathered attribute
            if isinstance(group_key, tuple):
                from_data = {str(v): str(v) for v in group_key}
            else:
                from_data = gathered.get(group_key, {})

            # Extract lookup keys
            if isinstance(from_data, dict):
                lookup_keys = {str(k): str(v) for k, v in from_data.items()}
            elif isinstance(from_data, (list, set)):
                lookup_keys = {str(v): str(v) for v in from_data}
            elif from_data:
                lookup_keys = {"0": str(from_data)}
            else:
                continue

            # For each attr in this from: group, resolve from gathered data
            for attr_name, lu in group:
                raw = gathered.get(attr_name, {})
                resolve_mode = lu.get("resolve", "value")

                if resolve_mode == "broadcast":
                    gathered[attr_name] = {k: raw for k in lookup_keys}
                elif not isinstance(raw, dict):
                    gathered[attr_name] = {k: raw for k in lookup_keys}
                else:
                    # Match: for each from entity, find the row in raw whose
                    # key matches the lookup value (index_field rekey already applied by driver)
                    result = {}
                    for entity_key, lookup_value in lookup_keys.items():
                        if lookup_value in raw:
                            result[entity_key] = raw[lookup_value]
                        else:
                            # Fallback: suffix match (SNMP compound OID keys)
                            for wk, wv in raw.items():
                                if wk.endswith("." + lookup_value) or wk.endswith(lookup_value):
                                    result[entity_key] = wv
                                    break
                    gathered[attr_name] = result

                # Apply resolve expression (e.g. "'rw' if value != 'none' else 'ro'")
                if resolve_mode not in ("value", "broadcast"):
                    resolved = gathered.get(attr_name, {})
                    if isinstance(resolved, dict):
                        new_resolved = {}
                        for k, v in resolved.items():
                            try:
                                new_resolved[k] = eval(resolve_mode,
                                    {"__builtins__": {}},
                                    {"value": v, "key": k})
                            except Exception as e:
                                logger.warning("lookup resolve failed for %s key=%s: %s", attr_name, k, e)
                                new_resolved[k] = v
                        gathered[attr_name] = new_resolved

        return gathered

    @staticmethod
    def _apply_membership(gathered: Dict, schema_attrs: Dict) -> Dict:
        """Resolve membership_of: from already-gathered data. Egress only.

        membership_of: attr_name — checks if each row key exists in that attr's value set.
        Both the membership source and the target are in gathered.

        No protocol, no transport, no wire access. Schema-layer only.
        """
        for schema_name, attr_ref in schema_attrs.items():
            if not isinstance(attr_ref, dict):
                continue
            member_of = attr_ref.get("membership_of")
            if not member_of or schema_name not in gathered:
                continue

            # Build membership set from gathered data
            raw = gathered[schema_name]
            if isinstance(raw, dict):
                members = set(raw.values())
            elif isinstance(raw, (list, set)):
                members = set(raw)
            else:
                members = {raw} if raw else set()

            # Get the reference attribute's keys
            ref_data = gathered.get(member_of, {})
            if isinstance(ref_data, dict):
                gathered[schema_name] = {
                    k: (v in members) for k, v in ref_data.items()
                }
            else:
                gathered[schema_name] = ref_data in members if ref_data else False

        return gathered

    # ==================================================================
    # GATE 1 — Schema Contract (validate + produce SchemaContext)
    # CAN ACCESS: schema attrs, method defs, defaults
    # CANNOT ACCESS: wire YAMLs, protocol, transport
    #
    # GATE 2 — Wire Contract (validate + produce WireContext)
    # CAN ACCESS: wire YAMLs (via load_wire), protocol sources
    # CANNOT ACCESS: CRUDE encode/decode, transport dispatch
    # ==================================================================

    @staticmethod
    def _flatten_kwargs(kwargs: Dict, schema_attrs: Dict,
                        method_def: Dict, all_methods: Dict = None) -> Dict:
        """Gate 1a: Intent mapping — resolve dotted paths and nested dicts to flat kwargs.

        "http.enabled" → "http_enabled" (via sub_tables field_map)
        {"http": {"enabled": False}} → {"http_enabled": False}
        Direct kwargs pass through unchanged. Most explicit wins.

        Scans current method and sibling methods for sub_tables field_map
        (SET method may not have sub_tables but its GET sibling does).
        """
        sub_tables = method_def.get("sub_tables", {})
        if not sub_tables and all_methods:
            for m_def in all_methods.values():
                if isinstance(m_def, dict) and m_def.get("sub_tables"):
                    sub_tables = m_def["sub_tables"]
                    break
        if not sub_tables:
            # Alias resolution: "enabled" → "is_enabled" if the schema has it
            resolved = {}
            for k, v in kwargs.items():
                if k in schema_attrs:
                    resolved[k] = v
                elif f"is_{k}" in schema_attrs:
                    resolved[f"is_{k}"] = v
                else:
                    resolved[k] = v
            return resolved

        # Build reverse map: {(sub_key, field_name): schema_attr_name}
        reverse_map = {}
        for sub_key, sub_def in sub_tables.items():
            for field_name, attr_name in sub_def.get("field_map", {}).items():
                reverse_map[(sub_key, field_name)] = attr_name

        resolved = {}
        for k, v in kwargs.items():
            if "." in k:
                # Dotted path: "http.enabled" → ("http", "enabled")
                parts = k.split(".", 1)
                attr_name = reverse_map.get((parts[0], parts[1]))
                if attr_name:
                    resolved[attr_name] = v
                else:
                    resolved[k] = v
            elif isinstance(v, dict) and k in sub_tables:
                # Nested dict: {"http": {"enabled": False}}
                for field_name, field_val in v.items():
                    attr_name = reverse_map.get((k, field_name))
                    if attr_name:
                        resolved[attr_name] = field_val
            else:
                # Direct: "http_enabled" passes through
                resolved[k] = v

        # Alias resolution: "enabled" → "is_enabled" if the schema has it
        final = {}
        for k, v in resolved.items():
            if k in schema_attrs:
                final[k] = v
            elif f"is_{k}" in schema_attrs:
                final[f"is_{k}"] = v
            else:
                final[k] = v
        return final

    @staticmethod
    def _validate_schema(kwargs: Dict, schema_attrs: Dict, method_def: Dict):
        """Gate 1b: Adapter→Schema — check fields exist and are writable.

        Raises ValueError with all problems at once (not one-at-a-time).
        """
        allowed_fields = set(method_def.get("fields", []))
        errors = []
        for kwarg_name in kwargs:
            if kwarg_name == "index":
                continue
            attr_ref = schema_attrs.get(kwarg_name)
            if not attr_ref or not isinstance(attr_ref, dict):
                errors.append(f"unknown field: '{kwarg_name}'")
                continue
            if allowed_fields and kwarg_name not in allowed_fields:
                errors.append(f"field '{kwarg_name}' not allowed by this method "
                              f"(allowed: {', '.join(sorted(allowed_fields))})")
                continue
            if not attr_ref.get("wire") or not attr_ref.get("source"):
                errors.append(f"field '{kwarg_name}' has no wire mapping")
                continue
            # Check value against value_map if present (user input must be a valid key)
            vmap = attr_ref.get("value_map")
            if vmap and isinstance(vmap, dict):
                val = kwargs[kwarg_name]
                reverse = {v: k for k, v in vmap.items()}
                if str(val) not in reverse and val not in reverse:
                    errors.append(f"field '{kwarg_name}': value '{val}' not valid "
                                  f"(allowed: {list(reverse.keys())})")
        if errors:
            raise ValueError("Schema validation failed:\n  " + "\n  ".join(errors))

    @staticmethod
    def _validate_wire_value(value, wire_attr: Dict, kwarg_name: str) -> Optional[str]:
        """Gate 3: Engine→Wire — check transformed value fits wire constraints.

        Checks validation: {min, max, allowed} from wire YAML.
        Returns error string or None if valid.
        """
        validation = wire_attr.get("validation", {})
        if not validation:
            return None
        if "min" in validation or "max" in validation:
            try:
                num_val = float(value) if not isinstance(value, (int, float)) else value
                if "min" in validation and num_val < validation["min"]:
                    return (f"'{kwarg_name}': value {value} below minimum "
                            f"{validation['min']}")
                if "max" in validation and num_val > validation["max"]:
                    return (f"'{kwarg_name}': value {value} above maximum "
                            f"{validation['max']}")
            except (ValueError, TypeError):
                pass  # Non-numeric value, skip range check
        # 'allowed' not checked on ingress — generator outputs MIB enum names
        # (up/down/testing) but ingress values are wire integers (1/2/3).
        # value_map already constrains input. min/max catches range violations.
        return None


    # ==================================================================
    # PIPELINE — Transition steps (bidirectional)
    # CAN ACCESS: context maps (via _resolve_context_map)
    # CANNOT ACCESS: wire YAMLs directly, transport
    # ==================================================================

    def get_execute_methods(self, protocol: str) -> list:
        """Return the list of execute_methods declared in a protocol YAML."""
        proto_config = self._load_protocol_config(protocol)
        return proto_config.get('execute_methods', [])

    def _load_protocol_config(self, protocol: str) -> Dict:
        """Load protocol YAML via transport registry — cached."""
        if protocol in self._protocol_config_cache:
            return self._protocol_config_cache[protocol]
        from crude_engine.transport_registry import get_protocol_yaml_path
        path = get_protocol_yaml_path(protocol)
        if not path or not os.path.exists(path):
            self._protocol_config_cache[protocol] = {}
            return {}
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        self._protocol_config_cache[protocol] = data
        return data


    @staticmethod
    def _decompose_index(suffix: str, index_fields: list,
                         last_is_implied: bool = False) -> Dict:
        """Decompose a compound walk suffix into individual field values.

        Walk suffix "45.1" with index_fields
        [interface, vrid] → {interface: "45", vrid: "1"}.

        If last_is_implied, last field consumes remaining parts as ASCII:
        "45.1.112.105.110.103.45.49" → {track_name: "ping-1"}.
        """
        parts = suffix.split(".")
        result = {}
        if not last_is_implied:
            for i, field in enumerate(index_fields):
                result[field] = parts[i] if i < len(parts) else ""
        else:
            for i, field in enumerate(index_fields[:-1]):
                result[field] = parts[i] if i < len(parts) else ""
            remaining = parts[len(index_fields) - 1:]
            try:
                result[index_fields[-1]] = "".join(chr(int(c)) for c in remaining)
            except (ValueError, IndexError):
                result[index_fields[-1]] = ".".join(remaining)
        return result

    # ------------------------------------------------------------------
    # Step Registry + Pipeline Builder (v2.7)
    # ------------------------------------------------------------------

    # STEP_REGISTRY: YAML key → {egress: fn_name, ingress: fn_name}
    # Loaded from engine/steps.yaml at init. Transition steps are
    # bidirectional. Formatter steps are single-direction.
    _steps_config = None  # lazy loaded

    def _load_steps_config(self):
        """Load step registry from steps.yaml — cached."""
        if self._steps_config is not None:
            return self._steps_config
        steps_path = os.path.join(os.path.dirname(__file__), "steps.yaml")
        with open(steps_path) as f:
            self._steps_config = yaml.safe_load(f) or {}
        return self._steps_config

    def _build_transition_steps(self, attr_ref: Dict) -> List[Dict]:
        """Build ordered transition step list from schema attr YAML keys.

        Reads keys in declaration order. Each key that matches a
        transition_step in the registry becomes a pipeline step.
        Returns list of {key, config, egress, ingress} dicts.

        Only receives attr_ref. No protocol, no method, no runtime state.
        """
        config = self._load_steps_config()
        transition_defs = config.get("transition_steps", {})
        steps = []
        for key in attr_ref:
            if key in transition_defs:
                step_def = transition_defs[key]
                steps.append({
                    "key": key,
                    "config": attr_ref[key],
                    "egress": step_def.get("egress"),
                    "ingress": step_def.get("ingress"),
                })
        return steps

    def _build_formatter_steps(self, attr_ref: Dict) -> List[Dict]:
        """Build ordered formatter step list from schema attr YAML keys.

        Formatter steps are intra-layer (schema↔schema). Single direction.
        Returns list of {key, config, direction} dicts.

        Only receives attr_ref. No protocol, no method, no runtime state.
        """
        config = self._load_steps_config()
        formatter_defs = config.get("formatter_steps", {})
        steps = []
        for key in attr_ref:
            if key in formatter_defs:
                step_def = formatter_defs[key]
                steps.append({
                    "key": key,
                    "config": attr_ref[key],
                    "direction": step_def.get("direction"),
                })
        return steps

    # Step list cache: {schema_feature_id + attr_name → (transition_steps, formatter_steps)}
    _step_cache = {}

    def _get_steps(self, feature_id: str, attr_name: str, attr_ref: Dict):
        """Get or build cached step lists for a schema attr."""
        wire = attr_ref.get("wire", "") if isinstance(attr_ref, dict) else ""
        cache_key = f"{feature_id}.{attr_name}.{wire}"
        if cache_key not in self._step_cache:
            self._step_cache[cache_key] = (
                self._build_transition_steps(attr_ref),
                self._build_formatter_steps(attr_ref),
            )
        return self._step_cache[cache_key]

    # ------------------------------------------------------------------
    # Pipeline Executor (v2.7)
    # ------------------------------------------------------------------

    # Handler dispatch: step key → method on this class
    _STEP_HANDLERS = {
        "value_map": "step_value_map",
        "key_map": "step_key_map",
        "index_fields": "step_index_codec",
        "collect": "step_collect",
        "regex": "step_regex",
    }

    def _translate(self, attr_name: str, attr_ref: Dict, direction: str,
                   value: Any, context: Dict, trace=None, **extra) -> Any:
        """Run transition pipeline for one attribute.

        direction="egress":  device → user (YAML top→bottom)
        direction="ingress": user → device (YAML bottom→top)

        If trace is a list, appends {step, attr, direction, input, output}
        per step. Caller owns the list. Zero cost when None.
        """
        transition_steps, _ = self._get_steps(
            extra.get("feature_id", ""), attr_name, attr_ref)

        steps = transition_steps
        if direction == "ingress":
            steps = list(reversed(steps))

        for step in steps:
            key = step["key"]
            config = step["config"]
            handler_name = step.get(direction)

            if not handler_name:
                continue

            method_name = self._STEP_HANDLERS.get(key)
            if not method_name:
                continue

            handler = getattr(self, method_name, None)
            if not handler:
                continue

            before = value
            value = handler(value, config, direction, context)

            if trace is not None:
                trace.append({
                    "step": key,
                    "attr": attr_name,
                    "direction": direction,
                    "input": repr(before)[:200],
                    "output": repr(value)[:200],
                })

        return value

    # ------------------------------------------------------------------
    # Transition Step Handlers (v2.7)
    # Bidirectional: every handler has egress + ingress.
    # These are the conduits — data crosses wire↔schema boundary here.
    # ------------------------------------------------------------------

    def step_value_map(self, value, config, direction, context):
        """Value translation. Egress: wire→human. Ingress: human→wire.

        config is the value_map declaration from schema attr:
          dict: {"1": "enabled", "2": "disabled"} — explicit map
          "ifindex": resolve via context ifindex_map
          "bridge_port": resolve via context bridge_port_map
        """
        if config is None:
            return value

        # Context map resolution: config is a string name, resolved lazily
        if isinstance(config, str):
            ctx_map = self._resolve_context_map(config)
            if ctx_map:
                def _map_val(v, m):
                    if isinstance(v, list):
                        return [m[str(x)] for x in v if str(x) in m]
                    return m.get(str(v), str(v))
                if direction == "egress":
                    if isinstance(value, dict):
                        return {k: _map_val(v, ctx_map) for k, v in value.items()}
                    return _map_val(value, ctx_map)
                elif direction == "ingress":
                    rev = {v: k for k, v in ctx_map.items()}
                    if isinstance(value, dict):
                        return {k: _map_val(v, rev) for k, v in value.items()}
                    return _map_val(value, rev)
            return value

        # Dict value_map
        if isinstance(config, dict):
            if direction == "egress":
                # Wire→human: "1" → "enabled"
                if isinstance(value, dict):
                    return {k: config.get(str(v), v) for k, v in value.items()}
                return config.get(str(value), value)
            else:
                # Human→wire: "enabled" → "1"
                rev = {str(v): k for k, v in config.items()}
                if isinstance(value, dict):
                    return {k: rev.get(str(v), v) for k, v in value.items()}
                return rev.get(str(value), value)

        return value

    def step_collect(self, value, config, direction, context):
        """Collect/collapse walked data. Egress only.

        String shorthand:
          collect: value  — first/only value as scalar
          collect: list   — all values as list

        Dict form:
          collect: {type: value, key: "1"}      — value at specific key
          collect: {type: list, filter: "active"} — values matching filter
        """
        if direction != "egress":
            return value
        value = self._coerce(value, "dict")

        if isinstance(config, str):
            if config == "value":
                return self._coerce(value, "scalar")
            elif config == "list":
                return self._coerce(value, "list")
            raise ValueError(f"Unknown collect type: {config!r}")

        if isinstance(config, dict):
            ctype = config.get("type", "value")
            key = config.get("key")
            filt = config.get("filter")

            if key is not None:
                return value.get(str(key), value.get(key))
            if filt is not None:
                return [v for v in value.values() if str(v) == str(filt)]
            if ctype == "value":
                return self._coerce(value, "scalar")
            if ctype == "list":
                return self._coerce(value, "list")
            raise ValueError(f"Unknown collect type: {ctype!r}")

        raise ValueError(f"Unknown collect config: {config!r}")

    def step_regex(self, value, config, direction, context):
        """Regex extraction. Egress only.

        config is either:
          str: pattern with capture group — returns group(1)
          dict: {regex: pattern, format: "{0}-{1}"} — format from groups
        """
        if direction != "egress" or value is None:
            return value

        if isinstance(config, dict):
            pattern = config.get("regex", "")
            fmt = config.get("format")
        else:
            pattern = str(config)
            fmt = None

        def _extract(v):
            v = str(v) if v is not None else ""
            m = re.search(pattern, v)
            if not m:
                return v
            if fmt and m.groups():
                return fmt.format(*m.groups())
            return m.group(1) if m.lastindex else m.group(0)

        if isinstance(value, dict):
            return {k: _extract(v) for k, v in value.items()}
        return _extract(value)

    def step_key_map(self, value, config, direction, context):
        """Key remapping on dicts. Egress: internal→human. Ingress: human→internal.

        config is a context map name (e.g. "ifindex" → ifindex_map in context).
        value must be a dict — keys get remapped, values unchanged.
        """
        if not isinstance(value, dict) or not isinstance(config, str):
            return value

        ctx_map = self._resolve_context_map(config)
        if not ctx_map:
            return value

        if direction == "egress":
            return {ctx_map.get(str(k), str(k)): v for k, v in value.items()}
        else:
            rev = {v: k for k, v in ctx_map.items()}
            return {rev.get(str(k), k): v for k, v in value.items()}

        return value

    def step_index_codec(self, value, config, direction, context):
        """Compound index decompose (egress only).

        config is a list of field names: ["interface", "vrid"]
        or a dict: {"fields": [...], "index_type": "implied_string"}
        Only used in table shaping. Ingress compound indexes go through the driver.
        """
        if isinstance(config, list):
            fields = config
            index_type = None
        elif isinstance(config, dict):
            fields = config.get("fields", [])
            index_type = config.get("index_type")
        else:
            return value
        if not fields or direction != "egress":
            return value

        last_is_implied = index_type == "implied_string"
        return self._decompose_index(str(value), fields, last_is_implied)

    # ==================================================================
    # PIPELINE RUNNERS — Dispatch coordination
    # CAN ACCESS: gates (via SchemaContext, WireContext), drivers
    # CANNOT ACCESS: wire YAMLs directly
    # ==================================================================

    @staticmethod
    def _get_protocol_names():
        """Return available protocol names from transport registry."""
        from crude_engine.transport_registry import REGISTRY
        return tuple(k for k in REGISTRY if k != "offline")

    def _get_driver(self, protocol: str, transport: Any,
                    attr_types: Dict = None, attr_syntaxes: Dict = None):
        """Return the correct driver instance for the protocol.

        Driver classes resolved via transport_registry.DRIVER_REGISTRY.
        """
        from crude_engine.transport_registry import get_driver_class
        cls = get_driver_class(protocol)
        return cls(transport, context=self.context,
                   attr_types=attr_types or {}, attr_syntaxes=attr_syntaxes or {})



    # ==================================================================
    # INTENT RESOLUTION — kwargs, index, assemble
    # ==================================================================

    def _load_method(self, method_name: str, schema_def: Dict) -> tuple:
        """Block 1: Load method definition and merge method-scoped attributes.

        Returns (method_def, schema_attrs, methods).
        """
        methods = schema_def.get("methods", {})
        method_def = methods.get(method_name, {})
        if "schema" in method_def:
            method_def = methods.get(method_def["schema"], {})
        schema_attrs = dict(schema_def.get("attributes", {}))
        schema_attrs.update(method_def.get("attributes", {}))
        return method_def, schema_attrs, methods

    def _resolve_intent(self, kwargs: Dict, schema_attrs: Dict,
                            method_def: Dict, methods: Dict,
                            index=None) -> tuple:
        """Block 2: Resolve all user intent into concrete engine inputs.

        Handles: dotted paths, nested dicts, is_ aliases, 'all' expansion,
        index_filter, 'interface' kwarg. Runs ONCE before any gate.

        Returns (clean_kwargs, index_list).
        index_list is always a list — [None] for no-index, [single] for one,
        [multiple] for list/all.
        """
        # Pop index from kwargs if not provided as arg
        if index is None:
            index = kwargs.pop("index", None) or kwargs.pop("interface", None)

        # Resolve kwarg shorthand (dotted paths, nested dicts, is_ aliases)
        kwargs = self._flatten_kwargs(kwargs, schema_attrs, method_def, methods)

        # 'all' → expand via key_map context
        if index == "all":
            for m_def in methods.values():
                if isinstance(m_def, dict) and m_def.get("key_map"):
                    ctx_map = self._resolve_context_map(m_def['key_map'])
                    if ctx_map:
                        index = list(ctx_map.values())
                    break

        # index_filter (YAML-declared regex)
        index_filter = method_def.get("index_filter")
        if index_filter and isinstance(index, list):
            index = [idx for idx in index if re.match(index_filter, str(idx))]

        # Normalize to list
        index_list = index if isinstance(index, list) else [index]

        return kwargs, index_list

    def _gate1_validate(self, resolved: ResolvedIntent, trace=None) -> 'SchemaContext':
        """Gate 1: validate and produce SchemaContext.

        Always produces context. validate=False skips rejection, still produces.
        Ingress: validates kwargs against schema before producing context.
        Egress: produces context without validation (read path needs no input check).
        """
        if resolved.validate and resolved.direction == "ingress":
            self._validate_schema(
                dict(resolved.clean_kwargs), resolved.schema_attrs, resolved.method_def)
        if trace is not None:
            trace.append({"gate": 1, "check": "schema", "result": "pass"})
        md = resolved.method_def
        return SchemaContext(
            schema_attrs=resolved.schema_attrs,
            method_def=md,
            methods=resolved.methods,
            defaults=md.get("defaults", {}),
            primary_key=md.get("primary_key"),
            index_fields=md.get("index_fields", []),
            feature_id=resolved.schema_def.get("feature", ""),
        )

    @staticmethod
    def _gate1_exit(result: Any, schema_ctx: 'SchemaContext', trace=None) -> Any:
        """Gate 1 egress: validate output matches schema defaults contract.

        Dict methods: all keys in defaults must be present in result.
        Table methods: result is dict-of-dicts/lists, each row checked.
        Returns result unchanged if valid. Raises ValueError if not.
        """
        defaults = schema_ctx.defaults
        mtype = schema_ctx.method_def.get("type", "dict")

        # CRUD returns bool, no defaults contract to check
        if mtype in ("create", "delete"):
            return result

        if schema_ctx.primary_key:
            # Table method: dict-of-dicts or dict-of-lists (list_append)
            if isinstance(result, dict) and defaults:
                for row_key, row in result.items():
                    if isinstance(row, dict):
                        missing = [k for k in defaults if k not in row]
                        if missing:
                            raise ValueError(
                                f"Gate 1 exit: row '{row_key}' missing keys: "
                                f"{missing}")
                    elif isinstance(row, list):
                        for i, item in enumerate(row):
                            if isinstance(item, dict):
                                missing = [k for k in defaults if k not in item]
                                if missing:
                                    raise ValueError(
                                        f"Gate 1 exit: row '{row_key}' item {i} "
                                        f"missing keys: {missing}")
        elif isinstance(result, dict) and defaults:
            # Flat dict method: all defaults keys must be present
            missing = [k for k in defaults if k not in result]
            if missing:
                raise ValueError(
                    f"Gate 1 exit: result missing keys from defaults: "
                    f"{missing}")

        if trace is not None:
            trace.append({"gate": 1, "check": "exit", "result": "pass"})
        return result

    def _gate2_resolve(self, attr_name: str, attr_ref: Dict,
                       protocol: str, validate: bool = True,
                       trace=None) -> 'WireContext':
        """Gate 2: resolve schema attr to full wire context.

        Loads wire YAML, resolves wire attr, checks access (if validate),
        resolves proto_source. Always produces WireContext.
        validate=False skips rejection — still produces context.
        """
        wire_source = attr_ref.get("source", "")
        wire_name = attr_ref.get("wire", "")
        wire_def = self.load_wire(wire_source, protocol)
        wire_attr = wire_def.get("attributes", {}).get(wire_name, {})
        access = wire_attr.get("access", "r")
        proto_src = wire_attr.get("sources", {}).get(protocol, {})

        if validate:
            if not wire_attr:
                raise ValueError(
                    f"Wire validation failed: wire attr '{wire_name}' "
                    f"not found in '{wire_source}'")
            if "u" not in access and "c" not in access:
                raise ValueError(
                    f"Wire validation failed: wire attr '{wire_name}' "
                    f"is read-only (access: '{access}')")
            if not proto_src:
                raise ValueError(
                    f"Wire validation failed: wire attr '{wire_name}' "
                    f"has no {protocol} source")

        if trace is not None:
            trace.append({"gate": 2, "check": "wire",
                          "attr": attr_name, "result": "pass"})

        return WireContext(
            wire_def=wire_def,
            wire_attr=wire_attr,
            proto_src=proto_src,
            value_maps=wire_def.get("value_maps", {}),
            access=access,
            wire_name=wire_name,
            wire_source=wire_source,
            syntax=wire_attr.get("syntax", ""),
            schema_type=wire_attr.get("type", ""),
            validation=wire_attr.get("validation", {}),
        )

    def _gate2_check_constraints(self, value, wire_ctx: 'WireContext',
                                  kwarg_name: str, trace=None) -> None:
        """Gate 2 constraint check: validate transformed value against wire limits.

        Checks min/max from wire_ctx.validation. Raises ValueError on violation.
        """
        wire_error = self._validate_wire_value(value, wire_ctx.wire_attr, kwarg_name)
        if wire_error:
            if trace is not None:
                trace.append({"gate": 3, "check": "wire_value",
                              "attr": kwarg_name, "result": "fail",
                              "error": wire_error})
            raise ValueError(f"Wire value validation failed: {wire_error}")
        if trace is not None:
            trace.append({"gate": 3, "check": "wire_value",
                          "attr": kwarg_name, "result": "pass",
                          "value": repr(value)[:200]})

    # ------------------------------------------------------------------
    # Context map resolution (lazy, cached)
    # ------------------------------------------------------------------

    def _collect_context_map_needs(self, schema_attrs, method_def, method_scope):
        """Scan schema attrs + method_def for context map references.

        Returns an ordered list of map names with dependencies first
        (e.g. [ifindex, bridge_port] since bridge_port depends_on ifindex).
        """
        needed = set()
        # Method-level key_map
        km = method_def.get("key_map")
        if isinstance(km, str):
            needed.add(km)
        # Sub-table key_maps
        for sub_def in method_def.get("sub_tables", {}).values():
            skm = sub_def.get("key_map") if isinstance(sub_def, dict) else None
            if isinstance(skm, str):
                needed.add(skm)
        # Per-attr value_map and key_map (within method scope)
        for schema_name, attr_ref in schema_attrs.items():
            if not isinstance(attr_ref, dict):
                continue
            if method_scope and schema_name not in method_scope:
                continue
            vm = attr_ref.get("value_map")
            if isinstance(vm, str):
                needed.add(vm)
            akm = attr_ref.get("key_map")
            if isinstance(akm, str):
                needed.add(akm)
        # Expand dependencies and return in dependency order
        ordered = []
        for name in list(needed):
            spec = self._get_context_map_spec(name)
            if spec and spec.get("depends_on"):
                dep = spec["depends_on"]
                if dep not in needed:
                    needed.add(dep)
                if dep not in ordered:
                    ordered.append(dep)
        for name in needed:
            if name not in ordered:
                ordered.append(name)
        return ordered

    def _get_context_map_spec(self, name):
        """Load context_maps.yaml (once) and return spec for a named map."""
        if self._context_maps_config is None:
            engine_dir = os.path.dirname(__file__)
            maps_path = os.path.join(engine_dir, "context_maps.yaml")
            if os.path.exists(maps_path):
                with open(maps_path) as f:
                    self._context_maps_config = yaml.safe_load(f) or {}
            else:
                self._context_maps_config = {}
        return self._context_maps_config.get("maps", {}).get(name)

    def _populate_context_maps(self, context_map_batch, wire_results):
        """Populate context map caches from batch gather results.

        Processes maps in insertion order (dependencies first).
        """
        for map_name, wire_attr in context_map_batch.items():
            result = wire_results.get(wire_attr, {})
            if isinstance(result, dict):
                result = {str(k): str(v) for k, v in result.items()}
            else:
                result = {}
            # Cross-reference through dependency map
            map_spec = self._get_context_map_spec(map_name)
            if map_spec:
                cross_ref = map_spec.get("cross_ref")
                if cross_ref:
                    ref_map = self.context.get(f"{cross_ref}_map", {})
                    result = {k: ref_map.get(str(v), str(v))
                              for k, v in result.items()}
            self.context[f"{map_name}_map"] = result

    def _resolve_context_map(self, name: str) -> dict:
        """Resolve a context map lazily. Cached after first resolution.

        Reads map declaration from context_maps.yaml, resolves through
        Gate 2 → Gate 3 pipeline. No protocol-specific branching —
        wire declares what's available.
        """
        # Cache hit — None means not yet resolved, {} means resolved-but-empty
        cached = self.context.get(f"{name}_map")
        if cached is not None:
            return cached

        # Load context_maps.yaml (once)
        if self._context_maps_config is None:
            engine_dir = os.path.dirname(__file__)
            maps_path = os.path.join(engine_dir, "context_maps.yaml")
            if os.path.exists(maps_path):
                with open(maps_path) as f:
                    self._context_maps_config = yaml.safe_load(f) or {}
            else:
                self._context_maps_config = {}

        maps_def = self._context_maps_config.get("maps", {})
        map_spec = maps_def.get(name)
        if not map_spec:
            # Not declared in YAML — return empty, cache it
            self.context[f"{name}_map"] = {}
            return {}

        # Resolve dependencies first
        depends = map_spec.get("depends_on")
        if depends:
            self._resolve_context_map(depends)

        # Need protocol + transport for gathering
        if not self._active_protocol or not self._active_transport:
            self.context[f"{name}_map"] = {}
            return {}

        # Build synthetic attr_ref and resolve through Gate 2
        wire_source = map_spec["wire_source"]
        wire_attr = map_spec["wire_attr"]
        attr_ref = {"source": wire_source, "wire": wire_attr}
        wire_ctx = self._gate2_resolve(wire_attr, attr_ref,
                                       self._active_protocol, validate=False)

        # Wire has no source for this protocol — empty map
        if not wire_ctx.proto_src:
            self.context[f"{name}_map"] = {}
            return {}

        # Gather through Gate 3 — index_field is a gather hint from context_maps.yaml
        extra_hints = {}
        idx_field = map_spec.get("index_field")
        if idx_field:
            extra_hints[wire_attr] = {"index_field": idx_field}
        driver = self._get_driver(self._active_protocol, self._active_transport)
        raw = driver.gather_and_decode(
            [(wire_attr, wire_ctx)], wire_ctx.value_maps,
            extra_hints=extra_hints if extra_hints else None)
        result = raw.get(wire_attr, {})

        # Normalize: ensure {str_key: str_value}
        if isinstance(result, dict):
            result = {str(k): str(v) for k, v in result.items()}
        else:
            result = {}

        # Cross-reference through dependency map if declared
        cross_ref = map_spec.get("cross_ref")
        if cross_ref:
            ref_map = self.context.get(f"{cross_ref}_map", {})
            result = {k: ref_map.get(str(v), str(v)) for k, v in result.items()}

        self.context[f"{name}_map"] = result
        return result

    def build_context(self, protocol: str, transport: Any,
                      fetch_device_info=None):
        """Store refs for lazy resolution. Zero device I/O.

        Protocol + transport are engine session state. Context maps
        resolve lazily on first use via _resolve_context_map.
        """
        self._active_protocol = protocol
        self._active_transport = transport
        self.context["device_info"] = {}
        if fetch_device_info:
            self.context["_fetch_device_info"] = fetch_device_info

    def _resolve_index(self, index, method_def: Dict, methods: Dict,
                       schema_attrs: Dict, trace=None):
        """Shared: translate user-facing index to wire-ready value.

        key_map reverse (e.g. '1/10' → 10), then value_map reverse
        via index_key/primary_key attr (e.g. 'bpdu-rate' → '6').

        Used by _pipeline_egress and _pipeline_ingress for user-provided indexes.
        Used by _pipeline_crud ONLY for explicit user index (not auto-derived).
        """
        if index is None:
            return None

        # key_map reverse from sibling GET method
        for m_def in methods.values():
            if isinstance(m_def, dict) and m_def.get("key_map"):
                index = self.step_value_map(
                    index, m_def["key_map"], "ingress", self.context)
                break

        # value_map reverse via index_key or primary_key attr
        idx_attr_name = method_def.get("index_key")
        if not idx_attr_name:
            for m_def in methods.values():
                if isinstance(m_def, dict) and m_def.get("primary_key"):
                    idx_attr_name = m_def["primary_key"]
                    break
        if idx_attr_name and idx_attr_name in schema_attrs:
            idx_ref = schema_attrs[idx_attr_name]
            if isinstance(idx_ref, dict) and idx_ref.get("value_map") and isinstance(idx_ref["value_map"], dict):
                index = self._translate(
                    idx_attr_name, idx_ref, "ingress", index, self.context, trace=trace)

        # sub_tables key_map reverse (e.g. bridge_port on sub_table when method uses ifindex)
        for m_def in methods.values():
            if isinstance(m_def, dict):
                for st_def in m_def.get("sub_tables", {}).values():
                    km = st_def.get("key_map")
                    if isinstance(km, str):
                        index = self.step_value_map(index, km, "ingress", self.context)
                        return index

        return index

    # ------------------------------------------------------------------
    # v2.8 Pipeline Runners
    # ------------------------------------------------------------------

    def _pipeline_ingress(self, kwargs: dict, index_list: list,
                          schema_ctx: 'SchemaContext', protocol: str,
                          transport: Any, validate: bool, trace):
        """Ingress pipeline: assemble → gate2 per-kwarg → index iterate → translate → scatter.

        Gate 2 runs ONCE per kwarg (wire source/attr/access don't change per index).
        Index iteration is a loop, NOT recursion.
        """
        schema_attrs = schema_ctx.schema_attrs
        method_def = schema_ctx.method_def
        feature_id = schema_ctx.feature_id

        kwargs = self._apply_assemble(kwargs, schema_attrs)

        # Gate 2 once per kwarg — resolve wire context, validate access
        validated_kwargs = []
        for kwarg_name, value in kwargs.items():
            if value is None:
                continue
            attr_ref = schema_attrs.get(kwarg_name)
            if not attr_ref or not isinstance(attr_ref, dict):
                continue
            wire_source = attr_ref.get("source", "")
            wire_name = attr_ref.get("wire", "")
            if not wire_source or not wire_name:
                continue
            wire_ctx = self._gate2_resolve(
                kwarg_name, attr_ref, protocol, validate, trace)
            validated_kwargs.append((kwarg_name, value, attr_ref, wire_ctx))

        # Iterate over indexes — translate then dispatch_batch per index
        success = False
        for current_index in index_list:
            resolved_index = self._resolve_index(
                current_index, method_def, schema_ctx.methods, schema_attrs, trace)

            batch = []
            for kwarg_name, value, attr_ref, wire_ctx in validated_kwargs:
                # Schema transforms only (value_map, regex) — no _protocol in context
                translated = self._translate(
                    kwarg_name, attr_ref, "ingress", value, self.context,
                    trace=trace, feature_id=feature_id)
                if translated is None:
                    continue
                if validate:
                    self._gate2_check_constraints(
                        translated, wire_ctx, kwarg_name, trace)
                batch.append((wire_ctx.wire_name, translated, wire_ctx))

            if batch:
                driver = self._get_driver(protocol, transport)
                driver.dispatch_batch(batch, index=resolved_index)
                success = True

        return success

    def _pipeline_egress(self, schema_ctx: 'SchemaContext', protocol: str,
                         transport: Any, trace, index_list):
        """Egress pipeline: gather → translate → format → shape."""
        schema_attrs = schema_ctx.schema_attrs
        method_def = schema_ctx.method_def
        defaults = schema_ctx.defaults
        primary_key = schema_ctx.primary_key
        method_index_fields = schema_ctx.index_fields
        feature_id = schema_ctx.feature_id

        # Phase A: Method-scoped gather
        gathered = self._egress_gather(schema_attrs, method_def, protocol, transport)

        # Phase B: Per-attr translate (egress direction)
        for schema_name, attr_ref in schema_attrs.items():
            if not isinstance(attr_ref, dict) or schema_name not in gathered:
                continue
            gathered[schema_name] = self._translate(
                schema_name, attr_ref, "egress",
                gathered[schema_name], self.context,
                trace=trace, feature_id=feature_id)

        # Phase C: Formatters (egress post-hooks)
        # regex: now runs in Phase B as a transition step (YAML key order)
        gathered = self._apply_lookup(gathered, schema_attrs)
        gathered = self._apply_membership(gathered, schema_attrs)
        if not primary_key:
            gathered = self._apply_compute(gathered, schema_attrs)

        # Phase D: Output shaping
        if primary_key:
            return self._shape_table_output(
                method_def, schema_attrs, gathered, primary_key,
                method_index_fields, protocol)

        result = copy.deepcopy(defaults)
        for k in defaults:
            if k in gathered:
                result[k] = gathered[k]
        return self._apply_sub_tables(result, method_def, gathered, schema_attrs)

    def _egress_gather(self, schema_attrs, method_def, protocol, transport):
        """Egress Phase A: method-scoped batch gather. Returns {schema_name: value}."""
        defaults = method_def.get("defaults", {})
        primary_key = method_def.get("primary_key")
        method_index_fields = method_def.get("index_fields", [])

        # Build method scope
        method_scope = self._build_method_scope(schema_attrs, method_def)

        # Gate 2 per attr (validate=False for egress), group by wire source
        wire_groups = {}
        for schema_name, attr_ref in schema_attrs.items():
            if not isinstance(attr_ref, dict):
                continue
            if method_scope and schema_name not in method_scope:
                continue
            if attr_ref.get("compute"):
                continue
            wire_source = attr_ref.get("source", "")
            wire_name = attr_ref.get("wire", "")
            if not wire_source or not wire_name:
                continue
            wire_ctx = self._gate2_resolve(
                schema_name, attr_ref, protocol, validate=False)
            wire_groups.setdefault(wire_source, []).append(
                (schema_name, wire_name, attr_ref, wire_ctx))

        # Batch gather via Gate 3 — driver owns batching strategy
        raw_walked = {}
        all_wire_contexts = []
        merged_value_maps = {}
        merged_extra_hints = {}
        wire_to_source = {}
        seen = set()
        for wire_source, attr_list in wire_groups.items():
            first_ctx = attr_list[0][3]
            merged_value_maps.update(first_ctx.value_maps)
            for schema_name, wire_name, attr_ref, wire_ctx in attr_list:
                if wire_name in seen:
                    continue
                seen.add(wire_name)
                if not wire_ctx.wire_attr or not wire_ctx.proto_src:
                    continue
                wire_to_source[wire_name] = wire_source
                hints = {}
                lookup = attr_ref.get("lookup", {}) if isinstance(attr_ref, dict) else {}
                if lookup.get("index_field"):
                    hints["index_field"] = lookup["index_field"]
                idx_filter = attr_ref.get("index_filter")
                if idx_filter is not None:
                    vmap = attr_ref.get("value_map")
                    if isinstance(vmap, dict):
                        rev = {v: k for k, v in vmap.items()}
                        idx_filter = rev.get(str(idx_filter), idx_filter)
                    hints["_index_filter"] = idx_filter
                if hints:
                    merged_extra_hints[wire_name] = hints
                all_wire_contexts.append((wire_name, wire_ctx))

        # Inject uncached context map wire contexts into the same batch
        context_map_names = self._collect_context_map_needs(
            schema_attrs, method_def, method_scope)
        context_map_batch = {}  # map_name → wire_attr name (for post-gather population)
        for map_name in context_map_names:
            if self.context.get(f"{map_name}_map") is not None:
                continue  # already cached
            map_spec = self._get_context_map_spec(map_name)
            if not map_spec:
                continue
            wire_attr = map_spec["wire_attr"]
            if wire_attr in seen:
                continue
            seen.add(wire_attr)
            attr_ref = {"source": map_spec["wire_source"], "wire": wire_attr}
            wire_ctx = self._gate2_resolve(
                wire_attr, attr_ref, protocol, validate=False)
            if not wire_ctx.proto_src:
                self.context[f"{map_name}_map"] = {}
                continue
            idx_field = map_spec.get("index_field")
            if idx_field:
                merged_extra_hints[wire_attr] = {"index_field": idx_field}
            all_wire_contexts.append((wire_attr, wire_ctx))
            context_map_batch[map_name] = wire_attr

        if all_wire_contexts:
            driver = self._get_driver(protocol, transport)
            try:
                wire_results = driver.gather_and_decode(
                    all_wire_contexts, merged_value_maps, merged_extra_hints)
            except Exception as e:
                logger.debug("Gather failed: %s", e)
                wire_results = {}
            for wire_name, value in wire_results.items():
                source_key = wire_to_source.get(wire_name, "")
                raw_walked.setdefault(source_key, {})[wire_name] = value

            # Populate context map caches from batch results
            self._populate_context_maps(context_map_batch, wire_results)

        # Resolve: wire → schema name (collect at resolve time)
        gathered = {}
        for schema_name, attr_ref in schema_attrs.items():
            if not isinstance(attr_ref, dict):
                continue
            if method_scope and schema_name not in method_scope:
                continue
            wire_source = attr_ref.get("source", "")
            wire_name = attr_ref.get("wire", "")
            if not wire_source or not wire_name:
                continue
            source_data = raw_walked.get(wire_source, {})
            if wire_name not in source_data:
                continue
            raw = source_data[wire_name]
            if attr_ref.get("collect"):
                gathered[schema_name] = list(raw.values()) if isinstance(raw, dict) else (raw if isinstance(raw, list) else ([raw] if raw else []))
            else:
                gathered[schema_name] = raw
        return gathered

    @staticmethod
    def _build_method_scope(schema_attrs, method_def):
        """Build the set of attr names this method needs to gather."""
        defaults = method_def.get("defaults", {})
        primary_key = method_def.get("primary_key")
        method_index_fields = method_def.get("index_fields", [])

        scope = set(defaults.keys()) if defaults else set()
        if primary_key and primary_key not in scope:
            scope.add(primary_key)
        for f in method_index_fields:
            scope.add(f.get("field", "") if isinstance(f, dict) else f)
        for sub_def in method_def.get("sub_tables", {}).values():
            for attr_name in sub_def.get("field_map", {}).values():
                scope.add(attr_name)
            sub_pk = sub_def.get("primary_key")
            if sub_pk:
                scope.add(sub_pk)
        # Generic dependency expansion
        expanded = True
        while expanded:
            expanded = False
            for attr_name in list(scope):
                attr_ref = schema_attrs.get(attr_name)
                if not isinstance(attr_ref, dict):
                    continue
                for key, val in attr_ref.items():
                    if key in ("wire", "source", "access", "collect"):
                        continue
                    refs = set()
                    if isinstance(val, str) and val in schema_attrs:
                        refs.add(val)
                    elif isinstance(val, list):
                        refs.update(v for v in val if isinstance(v, str) and v in schema_attrs)
                    elif isinstance(val, dict):
                        for v in val.values():
                            if isinstance(v, str) and v in schema_attrs:
                                refs.add(v)
                            elif isinstance(v, list):
                                refs.update(x for x in v if isinstance(x, str) and x in schema_attrs)
                    new = refs - scope
                    if new:
                        scope.update(new)
                        expanded = True
        return scope

    def _pipeline_crud(self, schema_ctx: 'SchemaContext', protocol: str,
                       transport: Any, trace=None, validate: bool = True,
                       **kwargs):
        """CRUD pipeline: RowStatus lifecycle for create and delete.

        Dispatch driven by method_def.get("type") — create or delete.
        Index resolution is wire-derived (not user intent).
        """
        method_def = schema_ctx.method_def
        schema_attrs = schema_ctx.schema_attrs
        mtype = method_def.get("type", "create")

        if mtype == "delete":
            index = self._resolve_crud_index_delete(method_def, schema_attrs, protocol, kwargs)
            index = self._resolve_index(index, method_def, {},
                                        schema_attrs, trace)
            return self._dispatch_crud_delete(
                method_def, schema_attrs, protocol, transport,
                index, trace, **kwargs)

        # create (kwargs already resolved by coordinator's _resolve_intent)
        index = self._resolve_crud_index_create(
            method_def, schema_attrs, protocol, transport, kwargs)
        payload = self._build_crud_payload(
            method_def, schema_attrs, protocol, kwargs, validate, trace)
        return self._dispatch_crud_create(
            method_def, schema_attrs, protocol, transport,
            index, payload, trace, **kwargs)

    def _resolve_compound_index(self, method_def, schema_attrs, protocol, kwargs):
        """Resolve compound index from wire index_fields declaration.

        Used by both create and delete. Returns compound dict or None.
        Maps wire index_fields → schema attrs → values from kwargs/defaults.
        """
        row_status_name = method_def.get("row_status")
        linked = method_def.get("linked_tables")
        if not row_status_name and linked:
            row_status_name = linked[0]["row_status"]
        rs_ref = schema_attrs.get(row_status_name or "", {})
        if not rs_ref.get("source") or not rs_ref.get("wire"):
            return None
        wire_ctx = self._gate2_resolve(
            row_status_name, rs_ref, protocol, validate=False)
        rs_attr = wire_ctx.wire_attr
        if not rs_attr.get("index_type"):
            return None
        rs_proto = wire_ctx.proto_src
        if isinstance(rs_proto, dict) and "read" in rs_proto:
            rs_proto = rs_proto["read"]
        compound_fields = rs_proto.get("index_fields", []) if isinstance(rs_proto, dict) else []
        if not compound_fields:
            return None
        merged = dict(method_def.get("defaults", {}))
        merged.update(kwargs)
        compound = {}
        for wire_field in compound_fields:
            for attr_name, attr_ref in schema_attrs.items():
                if isinstance(attr_ref, dict) and attr_ref.get("wire", "").lower() == wire_field.lower():
                    val = merged.get(attr_name)
                    if val is not None:
                        compound[wire_field] = val
                    break
        return compound if compound else None

    def _resolve_crud_index_create(self, method_def, schema_attrs,
                                   protocol, transport, kwargs):
        """CRUD index for CREATE: from kwargs, defaults, required, or auto-assign."""
        index = kwargs.pop("index", None)

        # From index_key in kwargs or defaults
        index_key = method_def.get("index_key")
        method_defaults = method_def.get("defaults", {})
        if index is None and index_key:
            if index_key in kwargs:
                index = kwargs[index_key]
            elif index_key in method_defaults:
                index = method_defaults[index_key]

        # Compound index from wire index_fields
        if index is None:
            index = self._resolve_compound_index(method_def, schema_attrs, protocol, kwargs)

        # Scalar from required fields
        row_status_name = method_def.get("row_status")
        linked = method_def.get("linked_tables")
        if not row_status_name and linked:
            row_status_name = linked[0]["row_status"]
        rs_ref = schema_attrs.get(row_status_name or "", {})
        wire_ctx = self._gate2_resolve(
            row_status_name or "", rs_ref, protocol, validate=False)
        rs_attr = wire_ctx.wire_attr
        wire_attrs = wire_ctx.wire_def.get("attributes", {})
        rs_wire = wire_ctx.wire_name
        index_type = rs_attr.get("index_type", "")

        if index is None and index_type:
            for req in method_def.get("required", []):
                if req in kwargs:
                    index = kwargs[req]
                    break
        if index_type and index is None:
            raise ValueError(f"index_type={index_type} requires index from required fields")

        # Auto-index: gather existing, find next available
        if index is None:
            driver = self._get_driver(protocol, transport)
            results = driver.gather_and_decode(
                [(rs_wire, wire_ctx)], wire_ctx.value_maps)
            existing_val = results.get(rs_wire)
            used = set()
            if isinstance(existing_val, dict):
                for k in existing_val:
                    try:
                        used.add(int(k))
                    except (ValueError, TypeError):
                        pass
            idx_field = self._resolve_index_field(wire_attrs, protocol, rs_wire)
            validation = wire_attrs.get(idx_field.lower(), {}).get("validation", {}) if idx_field else {}
            start = validation.get("min", 1)
            ceiling = validation.get("max")
            index = start
            while index in used:
                index += 1
            if ceiling is not None and index > ceiling:
                raise ValueError(f"Table full: range {start}..{ceiling}")

        # Reverse context map on index
        for attr_ref in schema_attrs.values():
            if isinstance(attr_ref, dict) and isinstance(attr_ref.get("value_map"), str):
                index = self.step_value_map(index, attr_ref["value_map"], "ingress", self.context)
                break

        return index

    def _resolve_crud_index_delete(self, method_def, schema_attrs,
                                    protocol, kwargs):
        """CRUD index for DELETE: from kwargs, index_key, compound, or defaults."""
        index_key = method_def.get("index_key")
        index = kwargs.pop("index", None)
        if index is None and index_key:
            index = kwargs.pop(index_key, None)
        if index is None and index_key:
            method_defaults = method_def.get("defaults", {})
            if index_key in method_defaults:
                index = method_defaults[index_key]
        # Compound index from wire index_fields (same helper as create)
        if index is None:
            index = self._resolve_compound_index(method_def, schema_attrs, protocol, kwargs)
        if index is None:
            raise ValueError("DELETE requires 'index' parameter")
        return index

    def _build_crud_payload(self, method_def, schema_attrs, protocol,
                            kwargs, validate, trace):
        """Build wire field payload for CREATE: merge defaults, assemble, translate, gate2."""
        merged = dict(method_def.get("defaults", {}))
        merged.update(kwargs)
        merged = self._apply_assemble(merged, schema_attrs)

        fields = {}
        attr_types = {}
        attr_syntaxes = {}
        for kwarg_name, value in merged.items():
            attr_ref = schema_attrs.get(kwarg_name)
            if not attr_ref or not isinstance(attr_ref, dict):
                continue
            wire_name = attr_ref.get("wire", "")
            wire_source = attr_ref.get("source", "")
            if not wire_name or not wire_source:
                continue
            wire_ctx = self._gate2_resolve(
                kwarg_name, attr_ref, protocol, validate=False)
            value = self._translate(kwarg_name, attr_ref, "ingress", value,
                                    self.context, trace=trace)
            if validate:
                self._gate2_check_constraints(value, wire_ctx, kwarg_name, trace)
            proto_src = wire_ctx.proto_src
            if isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            field_name = (proto_src.get("oid") or proto_src.get("field") or wire_ctx.wire_name) if isinstance(proto_src, dict) else wire_ctx.wire_name
            fields[field_name] = value
            attr_types[field_name] = wire_ctx.schema_type
            attr_syntaxes[field_name] = wire_ctx.syntax

        return {"fields": fields, "attr_types": attr_types,
                "attr_syntaxes": attr_syntaxes}

    def _dispatch_crud_create(self, method_def, schema_attrs, protocol, transport,
                              index, payload, trace, **kwargs):
        """Dispatch CREATE: encode index, resolve RowStatus, call driver."""
        row_status_name = method_def.get("row_status")
        linked = method_def.get("linked_tables")
        if not row_status_name and linked:
            row_status_name = linked[0]["row_status"]

        ctx = self._resolve_rs_context(row_status_name, schema_attrs, protocol)
        wire_attrs = ctx["wire_attrs"]
        idx_field = ctx["idx_field"]

        # Encode index through pipeline
        encoded_index = index
        index_key = method_def.get("index_key", "")
        if index_key and index_key in schema_attrs:
            idx_attr = schema_attrs[index_key]
            if isinstance(idx_attr, dict) and idx_attr.get("wire"):
                encoded_index = self._translate(
                    index_key, idx_attr, "ingress", index, self.context, trace=trace)
        elif index is not None and not isinstance(index, dict):
            try:
                encoded_index = int(index)
            except (ValueError, TypeError):
                pass

        fields = payload["fields"]
        attr_types = payload["attr_types"]
        attr_syntaxes = payload["attr_syntaxes"]

        attr_types[ctx["rs_wire"]] = ctx["rs_attr"].get("type", "")
        attr_syntaxes[ctx["rs_wire"]] = ctx["rs_attr"].get("syntax", "")
        # Register index field syntax/type so driver can CRUDE-encode
        idx_fields_to_register = list(index.keys()) if isinstance(index, dict) else ([idx_field] if idx_field else [])
        for ifield in idx_fields_to_register:
            idx_wire_attr = wire_attrs.get(ifield.lower(), {})
            if idx_wire_attr:
                idx_proto = idx_wire_attr.get("sources", {}).get(protocol, {})
                if isinstance(idx_proto, dict) and "read" in idx_proto:
                    idx_proto = idx_proto["read"]
                idx_proto_field = (idx_proto.get("field", "") or ifield) if isinstance(idx_proto, dict) else ifield
                attr_types[idx_proto_field] = idx_wire_attr.get("type", "")
                attr_syntaxes[idx_proto_field] = idx_wire_attr.get("syntax", "")

        driver = self._get_driver(protocol, transport, attr_types, attr_syntaxes)

        # Linked tables: per-table context resolution
        if linked:
            for table_def in linked:
                lt = self._resolve_rs_context(table_def["row_status"], schema_attrs, protocol)
                lt_at = {lt["rs_wire"]: lt["rs_attr"].get("type", "")}
                lt_as = {lt["rs_wire"]: lt["rs_attr"].get("syntax", "")}
                # Register index field syntax/type so driver can CRUDE-encode
                lt_idx_fields = list(index.keys()) if isinstance(index, dict) else ([lt["idx_field"]] if lt["idx_field"] else [])
                for ifield in lt_idx_fields:
                    iw = lt["wire_attrs"].get(ifield.lower(), {})
                    if iw:
                        ip = iw.get("sources", {}).get(protocol, {})
                        if isinstance(ip, dict) and "read" in ip:
                            ip = ip["read"]
                        ipf = (ip.get("field", "") or ifield) if isinstance(ip, dict) else ifield
                        lt_at[ipf] = iw.get("type", "")
                        lt_as[ipf] = iw.get("syntax", "")
                lt_driver = self._get_driver(protocol, transport, lt_at, lt_as)
                f_filter = set(table_def.get("fields", []))
                filtered = {k: v for k, v in fields.items() if k in f_filter} if f_filter else fields
                lt_driver.create_row(lt["rs_proto"], lt["rs_wire"], encoded_index, filtered,
                                     lt["value_maps"], index_field=lt["idx_field"],
                                     create_method=lt["create_method"])
            return True
        return driver.create_row(ctx["rs_proto"], ctx["rs_wire"], encoded_index, fields,
                                 ctx["value_maps"], index_field=idx_field,
                                 create_method=ctx["create_method"])

    def _dispatch_crud_delete(self, method_def, schema_attrs, protocol, transport,
                              index, trace, **kwargs):
        """Dispatch DELETE: encode index, call driver. Linked tables: per-table context."""
        row_status_name = method_def.get("row_status")
        linked = method_def.get("linked_tables")
        if not row_status_name and linked:
            row_status_name = linked[0]["row_status"]

        ctx = self._resolve_rs_context(row_status_name, schema_attrs, protocol)
        wire_attrs = ctx["wire_attrs"]
        idx_field = ctx["idx_field"]

        # Encode index through pipeline
        encoded_index = index
        for attr_name, attr_ref in schema_attrs.items():
            if isinstance(attr_ref, dict) and attr_ref.get("wire", "").lower() == idx_field.lower():
                encoded_index = self._translate(
                    attr_name, attr_ref, "ingress", index, self.context, trace=trace)
                break

        attr_types = {ctx["rs_wire"]: ctx["rs_attr"].get("type", "")}
        attr_syntaxes = {ctx["rs_wire"]: ctx["rs_attr"].get("syntax", "")}
        # Register index field syntax/type so driver can CRUDE-encode
        idx_fields_to_register = list(index.keys()) if isinstance(index, dict) else ([idx_field] if idx_field else [])
        for ifield in idx_fields_to_register:
            idx_wire_attr = wire_attrs.get(ifield.lower(), {})
            if idx_wire_attr:
                idx_proto = idx_wire_attr.get("sources", {}).get(protocol, {})
                if isinstance(idx_proto, dict) and "read" in idx_proto:
                    idx_proto = idx_proto["read"]
                idx_proto_field = (idx_proto.get("field", "") or ifield) if isinstance(idx_proto, dict) else ifield
                attr_types[idx_proto_field] = idx_wire_attr.get("type", "")
                attr_syntaxes[idx_proto_field] = idx_wire_attr.get("syntax", "")

        driver = self._get_driver(protocol, transport, attr_types, attr_syntaxes)

        # Linked tables: per-table context resolution
        if linked:
            for table_def in linked:
                lt = self._resolve_rs_context(table_def["row_status"], schema_attrs, protocol)
                lt_at = {lt["rs_wire"]: lt["rs_attr"].get("type", "")}
                lt_as = {lt["rs_wire"]: lt["rs_attr"].get("syntax", "")}
                # Register index field syntax/type so driver can CRUDE-encode
                lt_idx_fields = list(index.keys()) if isinstance(index, dict) else ([lt["idx_field"]] if lt["idx_field"] else [])
                for ifield in lt_idx_fields:
                    iw = lt["wire_attrs"].get(ifield.lower(), {})
                    if iw:
                        ip = iw.get("sources", {}).get(protocol, {})
                        if isinstance(ip, dict) and "read" in ip:
                            ip = ip["read"]
                        ipf = (ip.get("field", "") or ifield) if isinstance(ip, dict) else ifield
                        lt_at[ipf] = iw.get("type", "")
                        lt_as[ipf] = iw.get("syntax", "")
                lt_driver = self._get_driver(protocol, transport, lt_at, lt_as)
                lt_driver.delete_row(lt["rs_proto"], lt["rs_wire"], encoded_index,
                                     index_field=lt["idx_field"], **kwargs)
            return True
        return driver.delete_row(ctx["rs_proto"], ctx["rs_wire"], encoded_index,
                                 index_field=idx_field, **kwargs)

    # ==================================================================
    # INFRASTRUCTURE — Loading, caching, index encoding
    # ==================================================================

    def _resolve_rs_context(self, row_status_name: str, schema_attrs: Dict,
                             protocol: str) -> Dict:
        """Resolve a row_status name to its full wire context for CRUD dispatch.

        Used by both create and delete paths (top-level and linked_tables loop).
        Returns dict with all values needed to call driver create_row/delete_row.
        """
        rs_ref = schema_attrs.get(row_status_name, {})
        wire_ctx = self._gate2_resolve(
            row_status_name, rs_ref, protocol, validate=False)
        wire_attrs = wire_ctx.wire_def.get("attributes", {})
        value_maps = wire_ctx.value_maps
        rs_wire = wire_ctx.wire_name
        rs_attr = wire_ctx.wire_attr

        rs_proto = wire_ctx.proto_src
        if isinstance(rs_proto, dict) and "read" in rs_proto:
            rs_full = dict(rs_proto["read"])
            for k in ("create", "delete"):
                if k in rs_proto:
                    rs_full[k] = rs_proto[k]
            rs_proto = rs_full

        idx_field = self._resolve_index_field(wire_attrs, protocol, rs_wire)

        # create_method: wire attr declares it, protocol YAML provides fallback
        create_method = rs_attr.get("create_method")
        if not create_method:
            proto_config = self._load_protocol_config(protocol)
            create_method = proto_config.get("create_method_default", "")

        return {
            "rs_wire": rs_wire,
            "rs_attr": rs_attr,
            "rs_proto": rs_proto,
            "wire_attrs": wire_attrs,
            "value_maps": value_maps,
            "idx_field": idx_field,
            "create_method": create_method,
        }

    @staticmethod
    def _resolve_index_field(wire_attrs: Dict, protocol: str,
                              rs_wire: str = "") -> str:
        """Find the index_field name from wire attr sources."""
        if rs_wire:
            wa = wire_attrs.get(rs_wire, {})
            ps = wa.get("sources", {}).get(protocol, {})
            src = ps.get("read", ps) if isinstance(ps, dict) else {}
            if isinstance(src, dict):
                idx_f = src.get("index_field", "")
                if idx_f and idx_f != "_enumerate":
                    return idx_f
        for wa in wire_attrs.values():
            if not isinstance(wa, dict):
                continue
            ps = wa.get("sources", {}).get(protocol, {})
            src = ps.get("read", ps) if isinstance(ps, dict) else {}
            if isinstance(src, dict):
                idx_f = src.get("index_field", "")
                if idx_f and idx_f != "_enumerate":
                    return idx_f
        return ""

    def __init__(self, wire_dir=None, schemas_dir=None, context=None):
        pkg_root = os.path.join(os.path.dirname(__file__), "..")
        if wire_dir is None:
            wire_dir = os.path.join(pkg_root, "wire")
        if schemas_dir is None:
            schemas_dir = os.path.join(pkg_root, "schemas")
        self.wire_dir = wire_dir
        self.schemas_dir = schemas_dir
        self.features_cache = {}
        self.wire_cache = {}
        self.method_map = {}  # method_name → feature_id (built on first lookup)
        # Runtime context: ifindex_map, bridge_port_map, etc.
        # Populated by the driver at connect time.
        self.context = context or {}
        self.last_trace = None
        self._protocol_config_cache = {}
        self._drivers_dir = os.path.join(pkg_root, "drivers")
        self._context_maps_config = None  # loaded lazily from context_maps.yaml
        self._active_protocol = None      # set by build_context()
        self._active_transport = None     # set by build_context()

    # ------------------------------------------------------------------
    # Index encoding — protocol YAML drives the format
    # ------------------------------------------------------------------


    def load_feature(self, feature_id: str) -> Dict:
        if feature_id in self.features_cache:
            return self.features_cache[feature_id]
        path = os.path.join(self.schemas_dir, f"{feature_id}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema not found: {feature_id}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        self.features_cache[feature_id] = data
        return data


    def load_wire(self, wire_id: str, protocol: str = None) -> Dict:
        """Load a wire YAML, optionally merging protocol-specific overrides.

        If protocol has a wire_overlay_dir declared in transport_registry,
        checks wire/{overlay_dir}/{wire_id}.yaml for protocol-specific
        sources and merges into the base wire file.
        """
        cache_key = f"{wire_id}:{protocol}" if protocol else wire_id
        if cache_key in self.wire_cache:
            return self.wire_cache[cache_key]

        # Load base wire file
        path = os.path.join(self.wire_dir, f"{wire_id}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Wire definition not found: {path}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        # Merge protocol-specific overlay if registry declares one
        if protocol:
            from crude_engine.transport_registry import get_wire_overlay_dir
            overlay_dir = get_wire_overlay_dir(protocol)
            if overlay_dir:
                overlay_path = os.path.join(
                    self.wire_dir, overlay_dir, f"{wire_id}.yaml")
                if os.path.exists(overlay_path):
                    with open(overlay_path, "r") as f:
                        override = yaml.safe_load(f)
                    # Merge: add protocol sources to base attributes
                    for attr_name, attr_def in override.get("attributes", {}).items():
                        if attr_name in data.get("attributes", {}):
                            base_attr = data["attributes"][attr_name]
                            # Merge sources
                            base_sources = base_attr.setdefault("sources", {})
                            for proto, src in attr_def.get("sources", {}).items():
                                base_sources[proto] = src
                            # Override attr-level keys (type, syntax, etc.)
                            for key, val in attr_def.items():
                                if key != "sources":
                                    base_attr[key] = val

        self.wire_cache[cache_key] = data
        return data


    def get_capabilities(self, device_info: Optional[Dict] = None) -> Dict:
        """Return all available CRUDE operations, optionally filtered by device."""
        if not self.method_map:
            self._build_method_map()

        crude = {"create": [], "read": [], "upsert": [], "delete": [], "execute": []}
        features = {}

        for method_name in sorted(self.method_map.keys()):
            feature_id = self.method_map[method_name]
            fdef = self.load_feature(feature_id)
            method_def = fdef.get("methods", {}).get(method_name, {})
            if not method_def:
                continue

            mtype = method_def.get("type", "dict")
            if mtype == "create":
                crude["create"].append(method_name)
            elif mtype == "delete":
                crude["delete"].append(method_name)
            elif mtype == "upsert":
                crude["upsert"].append(method_name)
            else:
                crude["read"].append(method_name)

            # Resolve protocols from wire sources
            protocols = set()
            for attr_ref in fdef.get("attributes", {}).values():
                if not isinstance(attr_ref, dict) or "wire" not in attr_ref:
                    continue
                wire_source = attr_ref.get("source", "")
                wire_name = attr_ref.get("wire", "")
                for proto in self._get_protocol_names():
                    try:
                        wire_def = self.load_wire(wire_source, proto)
                        wa = wire_def.get("attributes", {}).get(wire_name, {})
                        if proto in wa.get("sources", {}):
                            protocols.add(proto)
                    except FileNotFoundError:
                        pass
            features[method_name] = {
                "type": mtype if mtype in ("create", "delete", "upsert") else "read",
                "protocols": sorted(protocols),
            }

        execute = []
        for proto in self._get_protocol_names():
            for name in self.get_execute_methods(proto):
                if name not in execute:
                    execute.append(name)
        crude["execute"] = execute

        result = {
            "device": device_info or {},
            "features": features,
            "crude": crude,
            "totals": {k: len(v) for k, v in crude.items()} | {"total": len(self.method_map)},
        }
        return result


    def _find_feature(self, method_name: str) -> str:
        """Map method name → schema YAML filename."""
        if not self.method_map:
            self._build_method_map()
        if method_name in self.method_map:
            return self.method_map[method_name]
        # Derive schema from prefix: set_facts → facts, create_vlan → vlan
        for prefix in ("get_", "set_", "delete_", "create_", "activate_"):
            if method_name.startswith(prefix):
                feature_name = method_name[len(prefix):]
                schema_path = os.path.join(self.schemas_dir, f"{feature_name}.yaml")
                if os.path.exists(schema_path):
                    return feature_name
                break
        raise ValueError(f"No schema found for '{method_name}'")

    def has_method(self, method_name: str) -> bool:
        """Check if a method name maps to a known schema feature."""
        try:
            self._find_feature(method_name)
            return True
        except (ValueError, FileNotFoundError):
            return False

    def _build_method_map(self):
        """Scan schema YAMLs, build method_name → schema_id map."""
        for fname in os.listdir(self.schemas_dir):
            if not fname.endswith(".yaml"):
                continue
            fid = fname[:-5]
            fdef = self.load_feature(fid)
            for method_name in fdef.get("methods", {}):
                self.method_map[method_name] = fid



