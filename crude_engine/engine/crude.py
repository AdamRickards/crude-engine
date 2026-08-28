"""
crude.py — CRUDE layer: bidirectional wire-to-schema data conversions.

Functions are the verbs (fixed set). YAML is the lookup (grows with new
syntaxes). Adding a new MIB syntax = one line in crude_matrix.yaml, zero
new code.

Layer: Engine (shared). Stupid type converters — no protocol knowledge,
no feature logic, no filtering/deciding.
Cannot: know about protocols, OIDs, MIB names, or feature intent.

Resolution order:
  1. REGISTRY[tag](val, ctx) → transformed value
  2. value_maps[tag][str(val)] → mapped value
  3. Pass through unchanged
"""

import os
import yaml
import ipaddress
import re
import struct


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _coerce_to_bytes(val):
    """Coerce various input types to bytes for bitmask/MAC processing."""
    if isinstance(val, (bytes, bytearray)):
        return val
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("0x"):
            try:
                return bytes.fromhex(s[2:])
            except ValueError:
                return b""
        parts = s.split()
        if parts and all(len(p) == 2 for p in parts):
            try:
                return bytes.fromhex("".join(parts))
            except ValueError:
                pass
        try:
            return val.encode("latin-1")
        except UnicodeEncodeError:
            return b""
    return b""


# ---------------------------------------------------------------------------
# Egress helpers (called by crude_* on GET path, not directly from REGISTRY)
# ---------------------------------------------------------------------------

def to_bool(val, ctx=None):
    """Universal boolean. Handles all protocols."""
    if val is None:
        return False
    custom_map = (ctx or {}).get("bool_map")
    if custom_map:
        key = str(val).strip()
        if key in custom_map:
            return bool(custom_map[key])
        key_lower = key.lower()
        if key_lower in custom_map:
            return bool(custom_map[key_lower])
    v = str(val).strip().lower()
    if v in ("disabled", "disable", "down", "off", "false", "no", "inactive",
             "none", "ignored", "0", "[ ]", "2", ""):
        return False
    if not v:
        return False
    return True


def to_num(val, ctx=None):
    """Universal numeric. Strips units, applies scale/offset.

    Hints: scale, offset, type ("int"/"float")
    """
    hints = ctx or {}
    is_float = hints.get("type") == "float"
    zero = 0.0 if is_float else 0
    if val is None:
        return zero
    v = str(val).strip()
    if not v:
        return zero
    m = re.match(r'^([+-]?\d+\.?\d*)', v)
    if not m:
        return zero
    raw = float(m.group(1))
    scale = hints.get("scale", 1.0)
    offset = hints.get("offset", 0.0)
    result = (raw * scale) + offset
    if hints.get("type") == "float":
        return result
    return int(result)


def to_str(val, ctx=None):
    """Universal string. Coerce, strip nulls, optional case."""
    if val is None:
        return ""
    if isinstance(val, bytes):
        s = val.decode("utf-8", errors="replace").strip("\x00\x07")
    else:
        s = str(val).strip().strip("\x00\x07")
    if s == "-":
        return ""
    hints = ctx or {}
    case = hints.get("case", "")
    if case == "lower":
        return s.lower()
    if case == "upper":
        return s.upper()
    return s


def hex_string(val, ctx=None):
    """MOPS space-separated hex bytes → ASCII string."""
    if not val or not isinstance(val, str):
        return str(val) if val is not None else ""
    parts = val.strip().split()
    if parts and all(len(p) == 2 for p in parts):
        try:
            raw = bytes.fromhex("".join(parts))
            return raw.decode("utf-8", errors="replace").strip("\x00").strip()
        except ValueError:
            pass
    return val


def to_hex_decode(val, ctx=None):
    """Universal hex decoder. ascii (default) or colon format."""
    hints = ctx or {}
    fmt = hints.get("format", "ascii")
    if fmt == "colon":
        return hex_octet(val, ctx)
    return hex_string(val, ctx)


def hex_octet(val, ctx=None, expected_len=None):
    """Raw OCTET STRING → colon-separated hex.

    When expected_len is set, enforces exact byte count (e.g. 6 for MAC).
    """
    if not val:
        return ""
    def _check_len(n):
        return expected_len is None or n == expected_len
    def _format(octets):
        return ":".join(f"{b:02x}" for b in octets)
    if isinstance(val, str) and ":" in val:
        parts = val.split(":")
        if _check_len(len(parts)) and all(len(p) == 2 for p in parts):
            return val.lower()
    if isinstance(val, str):
        parts = val.strip().split()
        if len(parts) > 1 and all(len(p) == 2 for p in parts) and _check_len(len(parts)):
            try:
                bytes.fromhex("".join(parts))
                return ":".join(p.lower() for p in parts)
            except ValueError:
                pass
        s = val.strip()
        if s.startswith("0x"):
            hex_body = s[2:]
            if len(hex_body) % 2 == 0 and _check_len(len(hex_body) // 2):
                return ":".join(hex_body[i:i+2] for i in range(0, len(hex_body), 2)).lower()
    if isinstance(val, bytes) and _check_len(len(val)):
        return _format(val)
    if isinstance(val, str) and " " not in val and ":" not in val and _check_len(len(val)):
        return ":".join(f"{ord(c):02x}" for c in val)
    return str(val)


def to_ip(val, ctx=None):
    """SNMP/MOPS IP bytes → dotted quad / IPv6."""
    if val is None:
        return ""
    if isinstance(val, bytes):
        if len(val) == 4:
            return ".".join(str(b) for b in val)
        if len(val) == 16:
            return str(ipaddress.IPv6Address(val))
    if isinstance(val, str) and len(val) == 4:
        try:
            raw = val.encode("iso-8859-1")
            if all(0 <= b <= 255 for b in raw):
                return ".".join(str(b) for b in raw)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    if isinstance(val, str):
        parts = val.strip().split()
        if len(parts) == 4:
            try:
                octets = [int(p, 16) for p in parts]
                return ".".join(str(o) for o in octets)
            except ValueError:
                pass
        if len(parts) == 16:
            try:
                raw = bytes(int(p, 16) for p in parts)
                return str(ipaddress.IPv6Address(raw))
            except ValueError:
                pass
    return str(val).strip()


def to_bits(val, ctx=None):
    """Universal bitmask decoder. BITS OCTET STRING → list of names.

    Hint: map (str) or bit_map (dict) — {bit_number: "name"}
    """
    hints = ctx or {}
    bit_map = hints.get("bit_map", {})
    # String → named reference in value_maps; dict → inline
    if isinstance(bit_map, str):
        vmaps = hints.get("_value_maps", {})
        bit_map = vmaps.get(bit_map, {})
    if bit_map:
        bit_map = {int(k): v for k, v in bit_map.items()}
    octets = _coerce_to_bytes(val)
    if not octets:
        return []
    enabled = []
    for byte_idx, byte_val in enumerate(octets):
        for bit_idx in range(8):
            if byte_val & (0x80 >> bit_idx):
                bit_num = byte_idx * 8 + bit_idx
                name = bit_map.get(bit_num)
                if name:
                    enabled.append(name)
    return enabled


def to_dt(val, ctx=None):
    """Universal timestamp decoder. epoch or dateandtime format."""
    import datetime
    hints = ctx or {}
    fmt = hints.get("format", "epoch")
    if fmt == "dateandtime":
        octets = _coerce_to_bytes(val)
        if not octets or len(octets) < 8:
            return ""
        try:
            year = (octets[0] << 8) | octets[1]
            if year <= 1970:
                return ""
            month, day = octets[2], octets[3]
            hour, minute, second = octets[4], octets[5], octets[6]
            dt = datetime.datetime(year, month, day, hour, minute, second)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            return str(val) if val else ""
    s = str(val).strip()
    if s in ("", "-"):
        return ""
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', s):
        return s
    try:
        ts = int(val)
        if ts <= 0:
            return ""
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return ""


def taddress(val, ctx=None):
    """Decode SNMP TAddress (6-byte OctetString) → 'ip:port'."""
    raw = _coerce_to_bytes(val)
    if raw and len(raw) == 6:
        ip = ".".join(str(b) for b in raw[:4])
        port = raw[4] * 256 + raw[5]
        return f"{ip}:{port}"
    return str(val) if val else ""


def hex_taddress_to_ip_port(val, ctx=None):
    """MOPS hex TAddress (6 space-separated hex bytes) → 'ip:port'."""
    if not val or not isinstance(val, str):
        return str(val) if val else ""
    parts = val.strip().split()
    if len(parts) == 6:
        try:
            ip = ".".join(str(int(p, 16)) for p in parts[:4])
            port = int(parts[4], 16) * 256 + int(parts[5], 16)
            return f"{ip}:{port}"
        except ValueError:
            pass
    return val


# ---------------------------------------------------------------------------
# CRUDE Bidirectional Primitives
#
# Each handles both GET (wire→Python) and SET (Python→wire)
# via ctx["_direction"]: "egress" (default) or "ingress".
# ---------------------------------------------------------------------------

def crude_boolean(val, ctx=None):
    """Bidirectional boolean: wire 1/2 ↔ True/False."""
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        return 1 if val else 2
    return to_bool(val, ctx)


def crude_numeric(val, ctx=None, **kwargs):
    """Bidirectional numeric: wire decimal string ↔ int/float.

    Args from matrix: type ("int"/"float")
    Hints in ctx: scale, offset, type
    """
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        return str(int(val)) if isinstance(val, bool) else str(val)
    if kwargs:
        ctx = dict(ctx or {}, **kwargs)
    return to_num(val, ctx)


def crude_text(val, ctx=None, **kwargs):
    """Bidirectional text: wire hex-spaced bytes ↔ decoded string.

    Args from matrix: decode (bool, default True) — False for SSH (plain text)
    Hints in ctx: case, format
    """
    decode = kwargs.get("decode", True)
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        if not val:
            return ""
        s = str(val)
        if not decode:
            return s
        return " ".join(f"{b:02x}" for b in s.encode("utf-8"))
    if not decode:
        return to_str(val, ctx)
    return to_hex_decode(val, ctx)


def crude_timestamp(val, ctx=None):
    """Bidirectional timestamp: wire epoch/DateAndTime ↔ ISO string."""
    import datetime
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        if not val:
            return 0
        try:
            dt = datetime.datetime.strptime(str(val), "%Y-%m-%d %H:%M:%S")
            import calendar
            return int(calendar.timegm(dt.timetuple()))
        except (ValueError, TypeError):
            return 0
    return to_dt(val, ctx)


def crude_bits(val, ctx=None, **kwargs):
    """Bidirectional BITS: wire BITS octets ↔ list of names/numbers.

    Args from matrix: mode ("portlist" for positional bitmask → port numbers)
    """
    mode = kwargs.get("mode")

    # PortList: positional bitmask ↔ list of port numbers (1-based)
    if mode == "portlist":
        direction = (ctx or {}).get("_direction", "egress")
        if direction == "ingress":
            if not val or not isinstance(val, list):
                return b"\x00"
            max_port = max(int(p) for p in val) if val else 0
            num_bytes = (max_port + 7) // 8
            result = bytearray(num_bytes)
            for port in val:
                bit_num = int(port) - 1
                result[bit_num // 8] |= (0x80 >> (bit_num % 8))
            return ' '.join(f'{b:02x}' for b in result)
        octets = _coerce_to_bytes(val)
        if not octets:
            return []
        return [byte_idx * 8 + bit_idx + 1
                for byte_idx, byte_val in enumerate(octets)
                for bit_idx in range(8)
                if byte_val & (0x80 >> bit_idx)]
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        if not val or not isinstance(val, list):
            return b"\x00"
        hints = ctx or {}
        bit_map = hints.get("bit_map", {})
        if isinstance(bit_map, str):
            vmaps = hints.get("_value_maps", {})
            bit_map = vmaps.get(bit_map, {})
        if bit_map:
            bit_map = {int(k): v for k, v in bit_map.items()}
        name_to_bit = {v: k for k, v in bit_map.items()}
        max_bit = max(name_to_bit.values()) if name_to_bit else 0
        num_bytes = (max_bit // 8) + 1
        result = bytearray(num_bytes)
        for name in val:
            bit_num = name_to_bit.get(name)
            if bit_num is not None:
                byte_idx = bit_num // 8
                bit_idx = bit_num % 8
                result[byte_idx] |= (0x80 >> bit_idx)
        return bytes(result)
    return to_bits(val, ctx)


def crude_octet(val, ctx=None, **kwargs):
    """Bidirectional octet: wire hex ↔ colon-separated string.

    Args from matrix: expected_len (int) — enforce exact byte count
    """
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        if not val or not isinstance(val, str):
            return ""
        if ":" in val:
            return " ".join(val.split(":"))
        return val
    return hex_octet(val, ctx, **kwargs)


def to_port_name(val, ctx=None):
    """Bidirectional ifIndex ↔ port name via ifindex_map context."""
    direction = (ctx or {}).get("_direction", "egress")
    ifmap = (ctx or {}).get("ifindex_map", {})
    if direction == "ingress":
        rev = {name: idx for idx, name in ifmap.items()}
        return int(rev.get(str(val), val))
    return ifmap.get(str(int(val)), str(val)) if val else ""


def crude_address(val, ctx=None, encoding=None):
    """Bidirectional address: wire hex bytes ↔ dotted quad / IPv6.

    encoding="dotted": ingress passes through dotted-quad as-is (SMIv1 IpAddress).
    Default: ingress converts dotted-quad → hex bytes (SMIv2 InetAddress).
    """
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        if not val:
            return ""
        s = str(val)
        if encoding == "dotted":
            return s
        parts = s.split(".")
        if len(parts) == 4:
            try:
                return " ".join(f"{int(p):02x}" for p in parts)
            except ValueError:
                pass
        try:
            addr = ipaddress.IPv6Address(s)
            return " ".join(f"{b:02x}" for b in addr.packed)
        except (ipaddress.AddressValueError, ValueError):
            pass
        return s
    return to_ip(val, ctx)


def crude_enum(val, ctx=None):
    """Bidirectional enum: wire integer ↔ named string via value_map."""
    direction = (ctx or {}).get("_direction", "egress")
    hints = ctx or {}
    map_name = hints.get("map", "")
    vmaps = hints.get("_value_maps", {})
    vmap = vmaps.get(map_name, {}) if map_name else {}
    if direction == "ingress":
        if not vmap:
            return str(val) if val is not None else ""
        reverse = {v: k for k, v in vmap.items()}
        return reverse.get(str(val), str(val))
    if vmap:
        key = str(val)
        return vmap.get(key, key)
    return str(val) if val is not None else ""


def crude_taddress(val, ctx=None):
    """Bidirectional TAddress: hex bytes ↔ 'ip:port'."""
    direction = (ctx or {}).get("_direction", "egress")
    if direction == "ingress":
        s = str(val)
        port = int((ctx or {}).get("port", 162))
        parts = s.split(".")
        if len(parts) == 4:
            try:
                ip_bytes = [int(p) for p in parts]
                port_bytes = [port >> 8, port & 0xFF]
                return ' '.join(f'{b:02x}' for b in ip_bytes + port_bytes)
            except ValueError:
                pass
        return val
    return taddress(val, ctx) or hex_taddress_to_ip_port(val, ctx)


# ---------------------------------------------------------------------------
# CRUDE MATRIX — loaded from crude_matrix.yaml
# ---------------------------------------------------------------------------

def _load_matrix():
    """Load (syntax, type) → function mapping from YAML."""
    matrix_path = os.path.join(os.path.dirname(__file__), "crude_matrix.yaml")
    with open(matrix_path) as f:
        raw = yaml.safe_load(f) or {}
    matrix = {}
    for syntax, type_map in raw.items():
        if not isinstance(type_map, dict):
            continue
        for schema_type, entry in type_map.items():
            if isinstance(entry, dict):
                matrix[(syntax, schema_type)] = (entry["function"], entry.get("args", {}))
            else:
                matrix[(syntax, schema_type)] = entry
    return matrix

CRUDE_MATRIX = _load_matrix()


# ---------------------------------------------------------------------------
# REGISTRY — tag name → function
# ---------------------------------------------------------------------------

REGISTRY = {
    # --- CRUDE bidirectional primitives (the core) ---
    "crude_boolean": crude_boolean,
    "crude_numeric": crude_numeric,
    "crude_text": crude_text,
    "crude_timestamp": crude_timestamp,
    "crude_bits": crude_bits,
    "crude_octet": crude_octet,
    "crude_address": crude_address,
    "crude_enum": crude_enum,
    "crude_taddress": crude_taddress,
    "to_port_name": to_port_name,
    # --- Legacy (wire YAML key_tag refs — TODO: regenerate, then delete) ---
    "to_hex_decode": crude_text,
}


def resolve(tag, val, ctx=None, value_maps=None):
    """Master resolver — called by drivers for every value.

    tag can be:
      str — function name, looked up in REGISTRY
      tuple — (function_name, args_dict) from CRUDE_MATRIX with args
    """
    args = {}
    if isinstance(tag, tuple):
        tag, args = tag[0], tag[1]
    func = REGISTRY.get(tag)
    if func:
        if args:
            return func(val, ctx, **args)
        return func(val, ctx)
    if value_maps and tag in value_maps:
        vmap = value_maps[tag]
        key = str(val)
        if key in vmap:
            return vmap[key]
        if "default" in vmap:
            return vmap["default"]
    return val
