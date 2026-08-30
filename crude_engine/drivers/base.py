"""
base.py — Base driver interface for crude-engine.

Layer: Driver (abstract). The contract between engine and transport.
Engine calls gather() and set_values(). Driver calls transport. Nothing
else crosses the boundary.

Owns: protocol YAML loading, wire_type_defaults, tag dispatch, regex/math.
Cannot: interpret data meaning, decide what to gather, know about schemas.
Wire output: str, int, float, bool, list, dict, None.

Protocol YAMLs declare defaults — wire YAML declarations override these
("declare exceptions, not rules").
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import logging
import yaml

from crude_engine.engine import crude as transforms

logger = logging.getLogger(__name__)

# Tags that operate on whole dicts, not per-value
AGGREGATE_TAGS = {"cli_nonzero", "dict_keys_to_list",
                  "agg_any", "agg_all"}


class BaseDriver(ABC):
    """Protocol driver base class.

    Subclasses implement the transport-specific gathering and setting
    logic. The engine never touches transport objects directly — it
    calls the driver, the driver calls the transport.
    """

    def __init__(self, transport: Any, context: Dict = None,
                 attr_types: Dict = None, attr_syntaxes: Dict = None):
        """
        Args:
            transport: Protocol-specific transport object (pysnmp, MOPS client, netmiko)
            context: Shared engine context (ifindex_map, bridge_port_map, device_info)
            attr_types: Attribute type declarations {attr_name: "boolean"/"integer"/etc}
                        from feature YAML. Used to resolve default tags from driver YAML.
            attr_syntaxes: MIB SYNTAX declarations {attr_name: "TruthValue"/"Integer32"/etc}
                           from feature YAML. Used for CRUDE matrix dispatch.
        """
        self.transport = transport
        self.context = context or {}
        self.attr_types = attr_types or {}
        self.attr_syntaxes = attr_syntaxes or {}
        self._driver_config = self._load_driver_yaml()

    def _load_driver_yaml(self) -> Dict:
        """Load protocol-level YAML defaults via transport registry."""
        from crude_engine.transport_registry import get_protocol_yaml_path
        # Find which protocol this driver serves
        from crude_engine.transport_registry import PROTOCOLS
        for proto, entry in PROTOCOLS.items():
            if entry.get("driver", "").endswith(self.__class__.__name__):
                yaml_path = get_protocol_yaml_path(proto)
                if yaml_path and os.path.exists(yaml_path):
                    with open(yaml_path) as f:
                        return yaml.safe_load(f) or {}
                break
        return {}

    @property
    def wire_type_defaults(self) -> Dict[str, str]:
        """Schema type → default tag from driver YAML."""
        return self._driver_config.get("wire_type_defaults", {})

    @property
    def protocol_defaults(self) -> Dict[str, Any]:
        """Protocol-level source defaults (e.g. method: walk)."""
        return self._driver_config.get("defaults", {})

    # ------------------------------------------------------------------
    # Gather — the main read path
    # ------------------------------------------------------------------

    @abstractmethod
    def gather(self, sources: List[Tuple[str, Dict]],
               value_maps: Dict = None) -> Dict[str, Any]:
        """Gather attribute values from the device.

        Args:
            sources: List of (attr_name, source_dict) from feature YAML.
                     Each source_dict contains protocol-specific instructions
                     (OIDs, MIB paths, CLI commands, tags, etc.)
            value_maps: Feature-level value maps for tag resolution.

        Returns:
            Dict of {attr_name: value} where each value is in a schema-ready
            type (str, int, bool, float, list, dict). Values not gathered
            are omitted (schema defaults will fill them).
        """
        ...

    # ------------------------------------------------------------------
    # Set — the write path
    # ------------------------------------------------------------------

    @abstractmethod
    def set_values(self, source: Dict, tokens: Dict,
                   value_maps: Dict = None) -> bool:
        """Execute a write operation against the device."""
        ...

    # ------------------------------------------------------------------
    # Gate 3 — batch dispatch (ingress) and gather (egress)
    # ------------------------------------------------------------------

    def dispatch_batch(self, batch: list, index=None) -> bool:
        """GATE 3 INGRESS: CRUDE encode + transport dispatch.

        Args:
            batch: [(wire_name, translated_value, WireContext), ...]
            index: row index for table operations (scalar, dict, or None)

        Returns: True if dispatch succeeded.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement dispatch_batch")

    def gather_and_decode(self, wire_contexts: list,
                          value_maps: Dict = None,
                          extra_hints: Dict = None) -> Dict[str, Any]:
        """GATE 3 EGRESS: build sources from WireContext, gather, CRUDE decode.

        Args:
            wire_contexts: [(wire_name, WireContext), ...]
            value_maps: feature-level value maps
            extra_hints: {wire_name: {key: val}} — schema-level hints

        Returns: {wire_name: decoded_value}
        """
        sources = []
        for wire_name, wire_ctx in wire_contexts:
            self.attr_types[wire_name] = wire_ctx.schema_type
            self.attr_syntaxes[wire_name] = wire_ctx.syntax
            proto_src = wire_ctx.proto_src
            if not proto_src:
                continue
            if isinstance(proto_src, dict) and "read" in proto_src:
                proto_src = proto_src["read"]
            proto_src = dict(proto_src)
            for hint_key in ("bit_map", "scale", "offset", "format", "case"):
                if hint_key in wire_ctx.wire_attr:
                    proto_src[hint_key] = wire_ctx.wire_attr[hint_key]
            if extra_hints and wire_name in extra_hints:
                proto_src.update(extra_hints[wire_name])
            sources.append((wire_name, proto_src))
        if not sources:
            return {}
        return self.gather(sources, value_maps)

    def _crude_encode(self, wire_name, value, wire_ctx, value_maps=None):
        """CRUDE encode a single value for ingress dispatch."""
        self.attr_types[wire_name] = wire_ctx.schema_type
        self.attr_syntaxes[wire_name] = wire_ctx.syntax
        resolved_tag = self._resolve_tag("", {}, attr_name=wire_name)
        if resolved_tag:
            ctx = dict(self.context) if self.context else {}
            ctx["_direction"] = "ingress"
            if value_maps:
                ctx["_value_maps"] = value_maps
            value = transforms.resolve(resolved_tag, value, ctx=ctx,
                                       value_maps=value_maps)
        return value

    # ------------------------------------------------------------------
    # Transform helpers — available to all drivers
    # ------------------------------------------------------------------

    def _transform(self, tag: str, val: Any, value_maps: Dict = None,
                   source: Dict = None) -> Any:
        """Apply a tag transform with driver context + YAML source hints.

        Merges runtime context (ifindex_map, bridge_port_map) with YAML
        source dict (scale, bit_map, format, etc.) so primitives can
        read hints declared in the YAML.
        """
        if not tag:
            return val
        ctx = dict(self.context) if self.context else {}
        if source:
            ctx.update(source)
        if value_maps:
            ctx["_value_maps"] = value_maps
        return transforms.resolve(tag, val, ctx=ctx, value_maps=value_maps)

    def _apply_regex(self, val: Any, source: Dict) -> Any:
        """Apply source-level regex extraction or substitution.

        regex: pattern — extract group(1) or group(0)
        regex: + regex_format: — capture groups, format with {0}, {1}, etc.
        """
        pattern = source.get("regex")
        if not pattern or not isinstance(val, str):
            return val
        import re
        m = re.search(pattern, val)
        if not m:
            return ""
        fmt = source.get("regex_format")
        if fmt and m.groups():
            groups = []
            for g in m.groups():
                try:
                    groups.append(int(g))
                except (ValueError, TypeError):
                    groups.append(g or "")
            return fmt.format(*groups)
        return m.group(1) if m.groups() else m.group(0)

    def _apply_math(self, val: Any, source: Dict) -> Any:
        """Apply source-level math expression if declared.

        Source YAML can declare `math:` expression. `val` is the input.
        Expression is evaluated with `val` as the only variable.
        Only arithmetic operators allowed — no builtins, no imports.

        Examples:
            math: "val * 1000000"     # Mbps → bps
            math: "val / 100"         # centiseconds → seconds
            math: "val & 0xFFF"       # extract low 12 bits
        """
        expr = source.get("math")
        if not expr:
            return val
        try:
            numeric = float(val) if isinstance(val, str) else val
            result = eval(expr, {"__builtins__": {}}, {"val": numeric})
            return int(result) if isinstance(result, float) and result == int(result) else result
        except (ValueError, TypeError, SyntaxError, NameError):
            return val

    def _apply_pipeline(self, val: Any, source: Dict, tag: str = "",
                        value_maps: Dict = None) -> Any:
        """Apply tag/regex/math in YAML source key declaration order.

        Python 3.7+ dicts preserve insertion order. The YAML source dict
        keys determine processing order:
            {regex: '(\\S+)', tag: hex_mac}    → regex first, then tag
            {tag: str_bool, regex: '(\\d+)'}   → tag first, then regex
            {tag: to_int, math: "val * 1000"}  → tag first, then math

        If no tag/regex/math keys in source, returns val unchanged.
        The resolved tag (from _resolve_tag) is passed in — not re-read
        from source, because driver YAML defaults may have provided it.
        """
        for key in source:
            if key == "tag":
                val = self._transform(tag, val, value_maps, source=source)
            elif key == "regex":
                val = self._apply_regex(val, source)
            elif key == "math":
                val = self._apply_math(val, source)
        # If tag was resolved from driver defaults (not in source keys),
        # apply it — this handles the common case where no explicit tag
        # is in the YAML but wire_type_defaults provides one
        if tag and "tag" not in source:
            val = self._transform(tag, val, value_maps, source=source)
        return val

    def _resolve_tag(self, tag: str, source: Dict,
                     attr_name: str = None) -> str:
        """Resolve tag from source, falling back to matrix or driver defaults.

        Priority:
        1. Explicit tag in source (feature YAML override)
        2. CRUDE matrix lookup (syntax + type → crude_* function)
        3. Driver YAML wire_type_defaults (schema type → default tag)
        4. Empty string (no transform)
        """
        # value_map special case
        if tag in ("value_map", "hex_value_map"):
            return source.get("map", tag)
        # Explicit tag — use it
        if tag:
            return tag
        if attr_name:
            # Matrix lookup: (syntax, type) → crude_* function
            syntax = self.attr_syntaxes.get(attr_name)
            schema_type = self.attr_types.get(attr_name)
            if syntax and schema_type:
                matrix_tag = transforms.CRUDE_MATRIX.get((syntax, schema_type))
                if not matrix_tag and " " in syntax:
                    # Strip size/range qualifiers: "DisplayString (SIZE(0..32))" → "DisplayString"
                    base_syntax = syntax.split("(")[0].strip().split(" ")[0].strip()
                    matrix_tag = transforms.CRUDE_MATRIX.get((base_syntax, schema_type))
                if matrix_tag:
                    return matrix_tag
            # Fallback: driver YAML wire_type_defaults
            if schema_type and self.wire_type_defaults:
                default_tag = self.wire_type_defaults.get(schema_type)
                if default_tag:
                    # Support {function: name, args: {}} format (same as matrix)
                    if isinstance(default_tag, dict):
                        return (default_tag["function"], default_tag.get("args", {}))
                    return default_tag
        return ""
