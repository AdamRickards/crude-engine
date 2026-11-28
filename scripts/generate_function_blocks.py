#!/usr/bin/env python3
"""Generate function-block (IEC 61131-3 FBD style) views as SVG.

Blocks have typed input pins on the left and typed output pins on the right;
wires carry the declared type. Everything drawn is read from the repository:

  * block names, pins, types ........ Python annotations (ast, never imported)
  * gate titles ..................... first docstring line of each gate function
  * wires ........................... return/param type match, else call order
  * protocols / drivers / transports  crude_engine/transport_registry.py
  * data-file blocks ................ file counts under crude_engine/
  * per-method view ................. schemas/*.yaml + wire/*.yaml (+ wire/<overlay>/)
                                      + drivers/*.yaml + engine/crude_matrix.yaml

Where a type cannot be derived the pin is drawn "untyped" (red). A declared
but loose type (bare list/dict/Any) is drawn amber. Nothing is guessed.

    python3 scripts/generate_function_blocks.py            # write SVGs
    python3 scripts/generate_function_blocks.py --check    # fail if stale
    python3 scripts/generate_function_blocks.py --method get_aca   # extra method view

Outputs (generated, never hand-edit): docs/function-blocks/*.svg

Only PyYAML and the standard library are used. The engine is not imported.
"""
from __future__ import annotations

import argparse
import ast
import copy
import os
import re
import sys
from xml.sax.saxutils import escape

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("pyyaml required\n")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PKG = os.path.join(ROOT, "crude_engine")
OUT_DIR = os.path.join(ROOT, "docs", "function-blocks")
DEFAULT_METHODS = ["get_aca"]
REGEN = "python3 scripts/generate_function_blocks.py"

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

UNTYPED = "untyped"
LOOSE_TYPES = {"list", "dict", "Dict", "List", "Any", "Tuple", "tuple"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


_YAML_CACHE = {}


def load_yaml(path):
    """Parse once per run; callers get a private copy (wire_for mutates)."""
    if path not in _YAML_CACHE:
        with open(path, encoding="utf-8") as f:
            _YAML_CACHE[path] = yaml.safe_load(f) or {}
    return copy.deepcopy(_YAML_CACHE[path])


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def engine_version():
    m = re.search(r'__version__\s*=\s*"([^"]+)"', read(os.path.join(PKG, "version.py")))
    return m.group(1) if m else UNTYPED


def count_yaml(d):
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith(".yaml")])


def ann_text(node):
    """Annotation node -> declared type text, or UNTYPED when absent."""
    if node is None:
        return UNTYPED
    txt = ast.unparse(node).strip()
    if len(txt) >= 2 and txt[0] == txt[-1] and txt[0] in "'\"":
        txt = txt[1:-1]
    return txt


def is_loose(t):
    return t.split("[")[0] in LOOSE_TYPES and "[" not in t


# ---------------------------------------------------------------------------
# Source readers (AST only)
# ---------------------------------------------------------------------------

class Fn:
    def __init__(self, qual, node, path):
        self.qual = qual                  # Class.method
        self.name = node.name
        self.node = node
        self.path = path
        self.doc = (ast.get_docstring(node) or "").split("\n")[0].strip()
        a = node.args
        params = []
        pos = a.posonlyargs + a.args
        defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
        for arg, d in zip(pos, defaults):
            if arg.arg in ("self", "cls"):
                continue
            params.append((arg.arg, ann_text(arg.annotation), d is not None))
        for arg, d in zip(a.kwonlyargs, a.kw_defaults):
            params.append((arg.arg, ann_text(arg.annotation), d is not None))
        if a.vararg:
            params.append(("*" + a.vararg.arg, ann_text(a.vararg.annotation), True))
        if a.kwarg:
            params.append(("**" + a.kwarg.arg, ann_text(a.kwarg.annotation), True))
        self.params = params
        self.ret = ann_text(node.returns)
        # (lineno, attribute-or-name) of every call in the body, in source order
        calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Attribute):
                    calls.append((n.lineno, n.col_offset, f.attr))
                elif isinstance(f, ast.Name):
                    calls.append((n.lineno, n.col_offset, f.id))
        self.calls = [c[2] for c in sorted(calls)]
        self.src = ast.get_source_segment(read(path), node) or ""


def parse_module(path):
    tree = ast.parse(read(path))
    fns, classes = {}, {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fields = []
            for m in node.body:
                if isinstance(m, ast.AnnAssign) and isinstance(m.target, ast.Name):
                    fields.append((m.target.id, ann_text(m.annotation)))
            bases = [ast.unparse(b) for b in node.bases]
            classes[node.name] = {"fields": fields, "bases": bases,
                                  "doc": (ast.get_docstring(node) or "").split("\n")[0]}
            for m in node.body:
                if isinstance(m, ast.FunctionDef):
                    fns[f"{node.name}.{m.name}"] = Fn(f"{node.name}.{m.name}", m, path)
        elif isinstance(node, ast.FunctionDef):
            fns[node.name] = Fn(node.name, node, path)
    return fns, classes


def read_registry():
    """transport_registry.PROTOCOLS as a literal dict (no import)."""
    tree = ast.parse(read(os.path.join(PKG, "transport_registry.py")))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "PROTOCOLS" for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


def driver_subclasses():
    """class name -> (file, bases) for classes under drivers/ deriving a *Driver base."""
    out = {}
    d = os.path.join(PKG, "drivers")
    for f in sorted(os.listdir(d)):
        if f.endswith(".py"):
            _, classes = parse_module(os.path.join(d, f))
            for cname, c in classes.items():
                out[cname] = (f, c["bases"])
    return out


# ---------------------------------------------------------------------------
# SVG toolkit
# ---------------------------------------------------------------------------

CW = 6.7      # monospace char width at 11px (generous)
RH = 17       # pin row height
HDR = 26      # block header height
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

PALETTE = {
    "bg": "#ffffff", "ink": "#1f2933", "mute": "#5f6b7a", "line": "#2b6cb0",
    "dash": "#7a8699", "untyped": "#c53030", "loose": "#b7791f", "ok": "#2f855a",
    "frame": "#9aa5b1",
}
KIND = {   # header colours per block kind
    "gate1": "#0f766e", "gate2": "#6d28d9", "gate3": "#b45309",
    "engine": "#475569", "data": "#334155", "proto": "#9a3412", "caller": "#1e40af",
}


def tw(text, size=11):
    return len(text) * CW * size / 11.0


def tcolor(t):
    if t == UNTYPED or t.startswith(UNTYPED):
        return PALETTE["untyped"]
    if is_loose(t):
        return PALETTE["loose"]
    return PALETTE["ink"]


class Svg:
    def __init__(self):
        self.under, self.body, self.over = [], [], []

    def text(self, x, y, s, size=11, color=None, anchor="start", weight="normal",
             italic=False, layer="body", halo=False):
        style = f'font-family:{FONT};font-size:{size}px;font-weight:{weight};'
        if italic:
            style += "font-style:italic;"
        if halo:
            style += f'paint-order:stroke;stroke:{PALETTE["bg"]};stroke-width:3px;stroke-linejoin:round;'
        el = (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
              f'fill="{color or PALETTE["ink"]}" style="{style}">{escape(s)}</text>')
        getattr(self, layer).append(el)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1, rx=0, dash=None, layer="body"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        getattr(self, layer).append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}"{s}{d}/>')

    def path(self, d, color, sw=1.6, dash=None, layer="under", marker=True):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arr)"' if marker else ""
        getattr(self, layer).append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{m}/>')

    def pin(self, x, y, color, layer="body"):
        getattr(self, layer).append(
            f'<rect x="{x-3:.1f}" y="{y-3:.1f}" width="6" height="6" fill="{color}"/>')

    def render(self, width, height, title, desc, header_lines):
        defs = (f'<defs><marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
                f'markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{PALETTE["line"]}"/>'
                f'</marker></defs>')
        head = "\n".join(f"  {l}" for l in header_lines)
        return "\n".join([
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<!--",
            head,
            "-->",
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
            f'width="{width:.0f}" height="{height:.0f}" role="img" aria-labelledby="t d">',
            f'<title id="t">{escape(title)}</title>',
            f'<desc id="d">{escape(desc)}</desc>',
            defs,
            f'<rect width="{width:.0f}" height="{height:.0f}" fill="{PALETTE["bg"]}"/>',
            *self.under, *self.body, *self.over, "</svg>", ""])


def header_comment(view, sources):
    return [
        "GENERATED FILE - do not edit by hand.",
        f"Generator : scripts/generate_function_blocks.py (engine {engine_version()})",
        f"Regenerate: {REGEN}",
        f"Check     : {REGEN} then git diff (or pass the check flag)",
        f"View      : {view}",
        "Derived from: " + ", ".join(sources),
    ]


def draw_legend(svg, x, y):
    items = [("declared type", PALETTE["ink"], "solid"),
             ("declared but loose (bare list/dict/Any)", PALETTE["loose"], "solid"),
             ("untyped (no declaration found)", PALETTE["untyped"], "solid")]
    cx = x
    for label, col, _ in items:
        svg.pin(cx, y - 4, col)
        svg.text(cx + 8, y, label, 10, PALETTE["mute"])
        cx += 8 + tw(label, 10) + 22
    return cx


class Box:
    """A function block with typed pins. Pin rows are [(name, type)]."""

    def __init__(self, bid, title, kind, subtitle="", ins=(), outs=(), note=""):
        self.id, self.title, self.kind, self.subtitle = bid, title, kind, subtitle
        self.ins, self.outs, self.note = list(ins), list(outs), note
        self.x = self.y = 0.0
        self.w = self.h = 0.0

    def measure(self):
        rows = max(len(self.ins), len(self.outs), 1)
        row_w = []
        for i in range(rows):
            lw = tw(f"{self.ins[i][0]} : {self.ins[i][1]}") if i < len(self.ins) else 0
            rw = tw(self.out_label(i)) if i < len(self.outs) else 0
            row_w.append(lw + rw + (30 if lw and rw else 0))
        head = max(tw(self.title, 12) + 18, tw(self.subtitle, 10) + 18)
        self.w = max(max(row_w) + 22, head, 150)
        self.hdr = HDR + (12 if self.subtitle else 0)
        self.h = self.hdr + rows * RH + 8

    def out_label(self, i):
        n, t = self.outs[i]
        return t if n == "return" else f"{n} : {t}"

    def pin_y(self, side, idx):
        return self.y + self.hdr + idx * RH + RH / 2 + 2

    def pin_x(self, side):
        return self.x if side == "in" else self.x + self.w

    def draw(self, svg):
        col = KIND[self.kind]
        svg.rect(self.x, self.y, self.w, self.h, "#ffffff", col, 1.6, 3)
        svg.rect(self.x, self.y, self.w, self.hdr, col, None, 0, 3)
        svg.text(self.x + 9, self.y + 17, self.title, 12, "#ffffff", weight="bold")
        if self.subtitle:
            svg.text(self.x + 9, self.y + 30, self.subtitle, 10, "#e6edf3")
        for i, (n, t) in enumerate(self.ins):
            y = self.pin_y("in", i)
            svg.pin(self.x, y, tcolor(t))
            svg.text(self.x + 9, y + 4, f"{n} : ", 11, PALETTE["ink"])
            svg.text(self.x + 9 + tw(f"{n} : "), y + 4, t, 11, tcolor(t),
                     italic=(t == UNTYPED))
        for i, (n, t) in enumerate(self.outs):
            y = self.pin_y("out", i)
            svg.pin(self.x + self.w, y, tcolor(t))
            svg.text(self.x + self.w - 9, y + 4, self.out_label(i), 11, tcolor(t),
                     anchor="end", italic=(t == UNTYPED))
        if self.note:
            svg.text(self.x + 9, self.y + self.h + 12, self.note, 9.5, PALETTE["mute"])


def draw_edge(svg, a, aidx, b, bidx, label, kind, chan_x, ymid=None):
    """Orthogonal wire from a's output pin to b's input pin.

    Forward wire: out -> vertical channel -> in. Back/cross-tier wire (ymid given):
    out -> right stub -> down/up to ymid -> left of target -> in.
    """
    x1, y1 = a.pin_x("out"), a.pin_y("out", aidx)
    x2, y2 = b.pin_x("in"), b.pin_y("in", bidx)
    dash = None if kind == "data" else "5,4"
    col = PALETTE["line"] if kind == "data" else PALETTE["dash"]
    if ymid is not None:
        sx = x1 + 12
        d = (f"M{x1:.1f},{y1:.1f} L{sx:.1f},{y1:.1f} L{sx:.1f},{ymid:.1f} "
             f"L{chan_x:.1f},{ymid:.1f} L{chan_x:.1f},{y2:.1f} L{x2:.1f},{y2:.1f}")
    elif abs(y1 - y2) < 0.5:
        d = f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"
    else:
        d = (f"M{x1:.1f},{y1:.1f} L{chan_x:.1f},{y1:.1f} "
             f"L{chan_x:.1f},{y2:.1f} L{x2:.1f},{y2:.1f}")
    svg.path(d, col, 1.6, dash)
    if label:
        svg.text(x2 - 6, y2 - 4, label, 9.5, tcolor(label) if kind == "data" else PALETTE["mute"],
                 anchor="end", halo=True, layer="over")


# ---------------------------------------------------------------------------
# System view
# ---------------------------------------------------------------------------

BUILTIN_TYPES = {"str", "int", "bool", "float", "bytes", "dict", "list", "tuple", "set",
                 "None", "Any", "Optional", "Dict", "List", "Tuple", "Set", "Union",
                 "Callable", UNTYPED}

# Which functions are drawn as blocks (a presentation filter; facts about them are read).
SHOW_ENGINE = re.compile(r"^(resolve_intent|execute_resolved|_gate\d_.*|_pipeline_.*|_egress_gather)$")
SHOW_DRIVER = {"dispatch_batch", "gather_and_decode"}

# Data file sets and the source token that proves a function reads them.
FILESETS = [
    ("schemas", "schemas/*.yaml", "load_feature"),
    ("wire", "wire/*.yaml", "load_wire"),
    ("matrix", "engine/crude_matrix.yaml", "CRUDE_MATRIX"),
    ("driver_yaml", "drivers/*.yaml", "_driver_config"),
    ("steps", "engine/steps.yaml", "steps.yaml"),
    ("context_maps", "engine/context_maps.yaml", "context_maps.yaml"),
]


def type_tokens(t):
    return {tok for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t)} - BUILTIN_TYPES


def gate_headings():
    """docs/ARCHITECTURE.md '### Gate N — title (file)' -> {N: (title, file)}."""
    out = {}
    p = os.path.join(ROOT, "docs", "ARCHITECTURE.md")
    if os.path.exists(p):
        for m in re.finditer(r"^### Gate (\d) [\u2014-] (.+?) \((.+?)\)\s*$", read(p), re.M):
            out[int(m.group(1))] = (m.group(2), m.group(3))
    return out


def build_system():
    eng_path = os.path.join(PKG, "engine", "interpreter.py")
    base_path = os.path.join(PKG, "drivers", "base.py")
    efns, eclasses = parse_module(eng_path)
    bfns, bclasses = parse_module(base_path)
    headings = gate_headings()
    file_to_gate = {}
    for n, (_, f) in headings.items():
        file_to_gate.setdefault(f, []).append(n)

    shown = {}      # block id -> (Fn, gate or None)
    for q, fn in efns.items():
        cls, name = q.split(".", 1) if "." in q else ("", q)
        if cls == "FeatureEngine" and SHOW_ENGINE.match(name):
            m = re.match(r"_gate(\d)_", name)
            shown[name] = (fn, int(m.group(1)) if m else None, cls)
    for q, fn in bfns.items():
        cls, _, name = q.partition(".")
        if cls == "BaseDriver" and name in SHOW_DRIVER:
            g = file_to_gate.get(os.path.basename(base_path), [])
            shown[name] = (fn, g[0] if len(g) == 1 else None, cls)

    # name -> Fn for closure walks (engine + base)
    allfns = {}
    for q, fn in list(efns.items()) + list(bfns.items()):
        allfns.setdefault(fn.name, fn)

    def closure_src(fn, stop):
        seen, out, stack = set(), [], [fn]
        while stack:
            f = stack.pop()
            if f.qual in seen:
                continue
            seen.add(f.qual)
            out.append(f.src)
            for c in f.calls:
                g = allfns.get(c)
                if g is not None and (g.name not in stop or g is fn):
                    stack.append(g)
        return "\n".join(out)

    boxes = {}
    for name, (fn, gate, cls) in shown.items():
        ins = []
        if cls != "FeatureEngine":
            ins.append(("self", cls))
        ins += [(("?" if opt else "") + pn, pt) for pn, pt, opt in fn.params]
        boxes[name] = Box(name, name + "()", f"gate{gate}" if gate else "engine",
                          ins=[("EN", "call")] + ins, outs=[("return", fn.ret)])
        boxes[name].gate, boxes[name].fn = gate, fn

    gaps = {"untyped": [], "loose": []}
    for name in sorted(shown):
        fn = shown[name][0]
        for pn, pt, _ in fn.params:
            (gaps["untyped"] if pt == UNTYPED else gaps["loose"] if is_loose(pt) else []).append(
                f"{name}({pn})" + ("" if pt == UNTYPED else f" : {pt}"))
        if fn.ret == UNTYPED:
            gaps["untyped"].append(f"{name} -> (return)")
        elif is_loose(fn.ret):
            gaps["loose"].append(f"{name} -> {fn.ret}")

    edges = []   # (src, srcpin, dst, dstpin, label, kind)

    # typed data wires: return type token == a param type token of another block
    for a in boxes.values():
        rt = type_tokens(a.fn.ret)
        for b in boxes.values():
            if a is b:
                continue
            for i, (pn, pt) in enumerate(b.ins):
                if rt & type_tokens(pt):
                    edges.append((a, 0, b, i, sorted(rt & type_tokens(pt))[0], "data"))

    # call wires: shown function calls another shown function
    for a in boxes.values():
        callees = []
        for c in a.fn.calls:
            if c in boxes and c != a.id and c not in callees:
                callees.append(c)
        if callees:
            a.outs.append(("call", f"x{len(callees)}"))
            pin = len(a.outs) - 1
            for c in callees:
                b = boxes[c]
                if any(e[0] is a and e[2] is b and e[5] == "data" for e in edges):
                    pass  # data wire already joins them; the call is still real
                edges.append((a, pin, b, 0, "", "call"))

    # driver-method calls made from engine helpers that are not drawn: lift to nearest shown caller
    # (e.g. _egress_gather -> gather_and_decode is a direct call and already captured above)

    # declared YAML inputs: external terminals on the blocks that read them
    reg = read_registry()
    overlay_dirs = sorted({p["wire_overlay_dir"] for p in reg.values() if "wire_overlay_dir" in p})
    counts = {
        "schemas": count_yaml(os.path.join(PKG, "schemas")),
        "wire": count_yaml(os.path.join(PKG, "wire")),
        "matrix": 1, "driver_yaml": count_yaml(os.path.join(PKG, "drivers")),
        "steps": 1, "context_maps": 1,
    }
    fileinfo = []
    for key, label, token in FILESETS:
        readers = [b for b in boxes.values()
                   if token in closure_src(b.fn, set(boxes) - {b.id})]
        if not readers:
            continue
        n = counts[key]
        extra = ""
        if key == "wire" and overlay_dirs:
            extra = " + overlay " + ", ".join(
                f"wire/{d}/*.yaml ({count_yaml(os.path.join(PKG, 'wire', d))})"
                for d in overlay_dirs)
        fileinfo.append(f"{key} = {label} ({n}{extra})")
        for r in readers:
            r.ins.append((key, "YAML"))

    # collapse pipeline-internal blocks: keep EN + a one-line parameter summary
    for b in boxes.values():
        if b.kind == "engine" and b.id not in ("resolve_intent", "execute_resolved"):
            full = [x for x in b.ins if x[0] not in ("EN",)]
            un = sum(1 for _, t in full if t == UNTYPED)
            b.ins = [("EN", "call"), ("params", f"{len(full)} ({un} untyped)")]
            b.collapsed = True
    edges[:] = [(a, ai, b, (1 if getattr(b, "collapsed", False) and bi > 0 else bi), lbl, k)
                for a, ai, b, bi, lbl, k in edges]
    # one wire per (src pin, dst pin, label)
    seen, uniq = set(), []
    for e in edges:
        key = (id(e[0]), e[1], id(e[2]), e[3], e[4], e[5])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    edges[:] = uniq

    # protocol blocks (registry) feeding G3
    drv = driver_subclasses()

    def chain_has(cname, base):
        seen = set()
        while cname in drv and cname not in seen:
            seen.add(cname)
            bases = drv[cname][1]
            if base in bases:
                return True
            cname = bases[0] if bases else ""
        return False

    protos = {}
    g3_blocks = [b for b in boxes.values() if b.fn.qual.startswith("BaseDriver.")]
    for pname, p in reg.items():
        outs = []
        def cls_of(key):
            dotted = p.get(key)
            if not dotted:
                return UNTYPED
            cname = dotted.rsplit(".", 1)[1]
            return cname if cname in drv else UNTYPED
        d_cls, t_cls = cls_of("driver"), cls_of("transport")
        ins = []
        if "wire_overlay_dir" in p:
            ins.append(("overlay", f"wire/{p['wire_overlay_dir']}/*.yaml"))
        ins.append(("defaults", p.get("protocol_yaml", UNTYPED)))
        outs = [("transport", t_cls),
                ("driver", d_cls if d_cls == UNTYPED or chain_has(d_cls, "BaseDriver") else UNTYPED)]
        pb = Box("proto_" + pname, pname, "proto",
                 subtitle=f"engine_protocol: {p.get('engine_protocol', UNTYPED)}"
                          + (f" · port {p['default_port']}" if "default_port" in p else ""),
                 ins=ins, outs=outs)
        protos[pname] = pb
        if outs[1][1] != UNTYPED:
            for g in g3_blocks:
                edges.append((pb, 1, g, 0, "BaseDriver", "data"))
    impl = {}
    d_dir = os.path.join(PKG, "drivers")
    for f in sorted(os.listdir(d_dir)):
        if f.endswith(".py"):
            dfns, _ = parse_module(os.path.join(d_dir, f))
            for q in dfns:
                c, _, m = q.partition(".")
                if c != "BaseDriver" and m:
                    impl.setdefault(m, set()).add(c)
    for g in g3_blocks:    # implicit self pin carries the BaseDriver instance
        g.ins[1] = ("self", "BaseDriver")
        abstract = any("abstractmethod" in ast.unparse(d) for d in g.fn.node.decorator_list)
        n = len(impl.get(g.fn.name, ()))
        g.subtitle = ("abstract · " if abstract else "") + f"overridden in {n} driver class{'es' if n != 1 else ''}"
    return boxes, fileinfo, protos, edges, headings, gaps


def layout_tiers(tiers, edges, top=96, vgap=26, left=24, band=70):
    """tiers: list of tiers; tier = list of columns; column = list of Box.

    Assigns x/y. Returns (width, height, tier_of_box, tier_tops).
    """
    tier_of = {id(b): ti for ti, t in enumerate(tiers) for col in t for b in col}
    col_of = {id(b): (ti, ci) for ti, t in enumerate(tiers) for ci, col in enumerate(t) for b in col}
    need = {}
    cnt = {}
    for a, ai, b, bi, label, kind in edges:
        key = col_of[id(b)]
        need[key] = max(need.get(key, 0), tw(label, 9.5) + 30 + 4 * cnt.get(key, 0))
        cnt[key] = cnt.get(key, 0) + 1
    for t in tiers:
        for col in t:
            for b in col:
                b.measure()
    width, y0, tops = 0, top, []
    for ti, t in enumerate(tiers):
        cross = sum(1 for a, ai, b, bi, l, k in edges if tier_of[id(b)] == ti and tier_of[id(a)] != ti)
        if ti:
            y0 += band + 7 * cross
        tops.append(y0)
        x, bottom = left, y0
        for ci, col in enumerate(t):
            x += max(need.get((ti, ci), 0), 44 if ci else 0)
            w = max(b.w for b in col)
            y = y0
            for b in col:
                b.x, b.w, b.y = x, w, y
                y += b.h + vgap
            bottom = max(bottom, y)
            x += w
        width = max(width, x + left)
        y0 = bottom
    return width, y0 + 40, tier_of, tops


def system_svg():
    boxes, fileinfo, protos, edges, headings, gaps = build_system()
    ri = [boxes[n] for n in ("resolve_intent",) if n in boxes]
    entry = [boxes[n] for n in ("execute_resolved",) if n in boxes]
    g1 = [b for b in boxes.values() if b.gate == 1]
    g2 = [b for b in boxes.values() if b.gate == 2]
    g3 = [b for b in boxes.values() if b.gate == 3]
    pipe = [b for n, b in boxes.items() if b.gate is None and n not in
            ("resolve_intent", "execute_resolved") and b.kind == "engine"]
    other = [b for b in boxes.values() if b.gate is None and b not in entry + ri and b not in pipe]
    byline = lambda bs: sorted(bs, key=lambda b: (b.fn.path, b.fn.node.lineno))
    tiers = [[c for c in (ri, entry, byline(g1), byline(pipe)) if c],
             [c for c in (byline(g2), [protos[k] for k in protos], byline(g3) + other) if c]]
    cols = [c for t in tiers for c in t]
    col_of = {id(b): i for i, c in enumerate(cols) for b in c}
    width, height, tier_of, tops = layout_tiers(tiers, edges)
    svg = Svg()

    # gate frames
    def frame(blocks, title, color):
        if not blocks:
            return
        x0 = min(b.x for b in blocks) - 10
        y0 = min(b.y for b in blocks) - 26
        x1 = max(b.x + b.w for b in blocks) + 10
        y1 = max(b.y + b.h + (12 if b.note else 0) for b in blocks) + 10
        svg.rect(x0, y0, x1 - x0, y1 - y0, "none", color, 1.4, 6, dash="6,4", layer="under")
        svg.text(x0 + 8, y0 + 16, title, 11, color, weight="bold", layer="under")
    for gi, blocks in ((1, g1), (2, g2), (3, g3)):
        h = headings.get(gi)
        title = f"GATE {gi}" + (f" · {h[0]} ({h[1]})" if h else "")
        frame(blocks, title, KIND[f"gate{gi}"])
    frame(pipe, "ENGINE PIPELINE (interpreter.py)", KIND["engine"])

    # wires (under blocks)
    used = {}
    for a, ai, b, bi, label, kind in edges:
        k = used.get(id(b), 0)
        used[id(b)] = k + 1
        chan = b.x - (tw(label, 9.5) + 18 + 4 * k) if label else b.x - 16 - 4 * k
        if tier_of[id(a)] != tier_of[id(b)]:
            draw_edge(svg, a, ai, b, bi, label, kind, chan, ymid=tops[tier_of[id(b)]] - 40 - 6 * k)
        elif col_of[id(a)] == col_of[id(b)]:
            draw_edge(svg, a, ai, b, bi, label, kind, chan, ymid=b.y - 13 - 3 * k)
        else:
            draw_edge(svg, a, ai, b, bi, label, kind, max(chan, a.x + a.w + 8))
    for col in cols:
        for b in col:
            b.draw(svg)

    # title + legend
    svg.text(24, 28, f"crude-engine {engine_version()} · system view (function blocks)", 15,
             weight="bold")
    svg.text(24, 46, "Left pins = typed inputs, right pins = typed outputs. Solid blue wire = "
             "declared type match; dashed grey = call (EN) wire; yellow-red pins = loose/untyped.",
             10, PALETTE["mute"])
    draw_legend(svg, 24, 68)
    n_untyped, n_loose = len(gaps["untyped"]), len(gaps["loose"])
    for i, line in enumerate(["YAML terminals read by blocks: " + "; ".join(fileinfo)]):
        svg.text(24, height - 32 + 14 * i, line, 10, PALETTE["mute"])
    svg.text(24, height - 14,
             f"Parameters/returns with no annotation: {n_untyped} · declared but loose: {n_loose} · "
             f"Generated: {REGEN} (do not edit by hand)", 10, PALETTE["mute"])
    srcs = ["crude_engine/engine/interpreter.py", "crude_engine/drivers/base.py",
            "crude_engine/transport_registry.py", "crude_engine/drivers/*.py (class bases)",
            "docs/ARCHITECTURE.md (gate headings)", "file counts under crude_engine/"]
    out = svg.render(width, height, "crude-engine system view",
                     "Function-block view of the three-gate model: engine, gate and driver "
                     "functions with typed pins, protocol blocks feeding Gate 3.",
                     header_comment("system", srcs))
    return out, {"untyped": n_untyped, "loose": n_loose, "gaps": gaps}


# ---------------------------------------------------------------------------
# Per-method view
# ---------------------------------------------------------------------------

def py_type(v):
    """Declared default value -> type name (what Gate 1's contract says)."""
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    if isinstance(v, dict):
        return "dict"
    if isinstance(v, list):
        return "list"
    return UNTYPED   # null / undeclared default


def step_names():
    d = load_yaml(os.path.join(PKG, "engine", "steps.yaml"))
    names = set()
    for sec in ("transition_steps", "formatter_steps"):
        names |= set((d.get(sec) or {}).keys())
    return names - {"wire", "source"}


def load_matrix():
    raw = load_yaml(os.path.join(PKG, "engine", "crude_matrix.yaml"))
    out = {}
    for syntax, tmap in raw.items():
        if isinstance(tmap, dict):
            for t, entry in tmap.items():
                out[(syntax, t)] = entry["function"] if isinstance(entry, dict) else entry
    return out


def find_method(method):
    sdir = os.path.join(PKG, "schemas")
    for f in sorted(os.listdir(sdir)):
        if f.endswith(".yaml"):
            d = load_yaml(os.path.join(sdir, f))
            m = (d.get("methods") or {}).get(method)
            if isinstance(m, dict):
                return f[:-5], d, m
    raise SystemExit(f"method not found in schemas: {method}")


def wire_for(source, proto, reg):
    """Mirror of FeatureEngine.load_wire: base wire YAML + protocol overlay merge."""
    base_path = os.path.join(PKG, "wire", f"{source}.yaml")
    if not os.path.exists(base_path):
        return None
    data = load_yaml(base_path)
    od = reg.get(proto, {}).get("wire_overlay_dir")
    if od:
        op = os.path.join(PKG, "wire", od, f"{source}.yaml")
        if os.path.exists(op):
            ov = load_yaml(op)
            for an, ad in (ov.get("attributes") or {}).items():
                if an in (data.get("attributes") or {}):
                    base = data["attributes"][an]
                    srcs = base.setdefault("sources", {})
                    for pr, sr in (ad.get("sources") or {}).items():
                        srcs[pr] = sr
                    for k, v in ad.items():
                        if k != "sources":
                            base[k] = v
    return data


def resolve_tag(proto_src, syntax, wtype, matrix, wtd):
    """Mirror of BaseDriver._resolve_tag precedence -> (function name or UNTYPED, via)."""
    src = proto_src.get("read", proto_src) if isinstance(proto_src, dict) else {}
    tag = src.get("tag") if isinstance(src, dict) else None
    if tag:
        return str(tag), "source tag"
    if syntax and wtype:
        m = matrix.get((syntax, wtype))
        if not m and " " in syntax:
            m = matrix.get((syntax.split("(")[0].strip().split(" ")[0].strip(), wtype))
        if m:
            return m, "matrix"
    if wtype and wtd.get(wtype):
        d = wtd[wtype]
        return (d["function"] if isinstance(d, dict) else d), "driver default"
    return UNTYPED, "none"


def build_method(method):
    feature, sdef, mdef = find_method(method)
    reg = read_registry()
    protos = [p for p in reg if "driver" in reg[p]]          # transports with a driver
    matrix = load_matrix()
    steps = step_names()
    attrs = sdef.get("attributes") or {}
    wtd_by_proto = {}
    for p in protos:
        y = load_yaml(os.path.join(PKG, "drivers", reg[p]["protocol_yaml"]))
        wtd_by_proto[p] = y.get("wire_type_defaults") or {}

    # output rows: (out_path, attr_name or None, g1_default)
    rows_spec = []
    defaults = mdef.get("defaults") or {}
    subs = mdef.get("sub_tables") or {}
    for k, v in defaults.items():
        if k in subs:
            sub = subs[k]
            sdefs = sub.get("defaults") or {}
            pk = sub.get("primary_key", "")
            for ok, an in (sub.get("field_map") or {}).items():
                rows_spec.append((f"{k}[{pk}].{ok}", an, sdefs.get(ok)))
        else:
            rows_spec.append((k, k if k in attrs else None, v))

    findings = []          # (id, text)
    rows = []
    for out_path, an, dflt in rows_spec:
        ref = attrs.get(an) if an else None
        row = {"out": out_path, "attr": an or "-", "g1": py_type(dflt), "marks": [],
               "pins": [], "steps": [], "decoded": UNTYPED, "g2out": UNTYPED, "wire": "",
               "access": UNTYPED, "validation": UNTYPED}
        if not isinstance(ref, dict) or "wire" not in ref:
            row["wire"] = "no wire (structural or computed)"
            row["decoded"] = UNTYPED
            row["g2out"] = UNTYPED
            row["nowire"] = True
            rows.append(row)
            continue
        row["wire"] = ref["wire"]
        row["steps"] = [k for k in ref if k in steps]
        tags, wtypes, missing, accs, vals, viad = [], [], [], set(), set(), []
        for p in protos:
            data = wire_for(ref.get("source", ""), p, reg)
            wattr = ((data or {}).get("attributes") or {}).get(ref["wire"]) if data else None
            if data is None or wattr is None:
                row["pins"].append((p, "wire attr not found", UNTYPED, False))
                missing.append(p)
                continue
            psrc = (wattr.get("sources") or {}).get(p)
            syn, wt = str(wattr.get("syntax", "") or ""), str(wattr.get("type", "") or "")
            if not psrc:
                row["pins"].append((p, "no source", "", False))
                continue
            tag, via = resolve_tag(psrc, syn, wt, matrix, wtd_by_proto[p])
            if via == "driver default":
                viad.append((p, syn))
            accs.add(str(wattr.get("access", UNTYPED)))
            v = wattr.get("validation") or {}
            vals.add(("allowed(%d)" % len(v["allowed"])) if isinstance(v.get("allowed"), list)
                     else ("range" if ("min" in v or "max" in v) else "none"))
            tags.append((p, tag))
            wtypes.append((p, wt or UNTYPED))
            row["pins"].append((p, f"{syn or UNTYPED}:{wt or UNTYPED}", tag, True))
        dtags = sorted({t for _, t in tags})
        row["decoded"] = " | ".join(dtags) if dtags else UNTYPED
        # G2 output type
        vm = ref.get("value_map")
        if isinstance(vm, dict) and vm:
            vt = {py_type(v) for v in vm.values()}
            row["g2out"] = vt.pop() if len(vt) == 1 else "mixed"
        elif isinstance(vm, str):
            row["g2out"] = f"{UNTYPED} (context map {vm})"
        elif any(x in row["steps"] for x in ("regex", "compute", "lookup", "membership_of", "collect")):
            row["g2out"] = f"{UNTYPED} ({'/'.join(x for x in row['steps'] if x != 'value_map')})"
        else:
            wts = sorted({t for _, t in wtypes})
            row["g2out"] = " | ".join(wts) if wts else UNTYPED
        row["_tags"], row["_wtypes"], row["_missing"] = tags, wtypes, missing
        row["_viad"] = viad
        row["access"] = "|".join(sorted(accs)) if accs else UNTYPED
        row["validation"] = "|".join(sorted(vals)) if vals else UNTYPED
        rows.append(row)

    def add(text, attrs_):
        fid = len(findings) + 1
        findings.append((fid, text))
        for r in rows:
            if r["out"] in attrs_:
                r["marks"].append(fid)

    nos = {}
    for r in rows:
        for p, note, _, ok in r["pins"]:
            if not ok and note == "no source":
                nos.setdefault(p, []).append(r["out"])
    for p in protos:
        if p in nos:
            add(f"{p}: no wire source for {len(nos[p])} of {len(rows)} outputs "
                f"({', '.join(nos[p][:6])}{', ...' if len(nos[p]) > 6 else ''})", set(nos[p]))
    div = [r["out"] for r in rows if len({t for _, t in r.get("_wtypes", [])}) > 1]
    if div:
        add("wire type differs across transports (overlay or base): " + ", ".join(div), set(div))
    undec = [r["out"] for r in rows if r.get("_tags") and any(t == UNTYPED for _, t in r["_tags"])]
    if undec:
        add("no decode function resolves from matrix or driver defaults: " + ", ".join(undec), set(undec))
    dd = [r["out"] for r in rows if r.get("_viad")]
    if dd:
        syn = sorted({sy for r in rows for _, sy in r.get("_viad", [])})
        add("decoded by the driver's per-type default because the syntax is not in the CRUDE matrix "
            f"({', '.join(syn)}): " + ", ".join(dd), set(dd))
    mism = []
    for r in rows:
        if r.get("nowire"):
            continue
        g2 = r["g2out"]
        if g2.startswith(UNTYPED):
            continue
        if r["g1"] != UNTYPED and g2 != r["g1"] and r["g1"] != "dict":
            mism.append(r["out"])
    if mism:
        add("Gate 2 output type differs from the Gate 1 default's type: " + ", ".join(mism), set(mism))
    unk = [r["out"] for r in rows if r["g2out"].startswith(UNTYPED) and not r.get("nowire")]
    if unk:
        add("Gate 2 output type cannot be derived (map reference or computed step): " + ", ".join(unk), set(unk))
    g1un = [r["out"] for r in rows if r["g1"] == UNTYPED]
    if g1un:
        add("Gate 1 default has no type (null default): " + ", ".join(g1un), set(g1un))
    nw = [r["out"] for r in rows if r.get("nowire")]
    if nw:
        add("output has no wire attribute behind it: " + ", ".join(nw), set(nw))
    return {"method": method, "feature": feature, "mtype": str(mdef.get("type", UNTYPED)),
            "protos": protos, "rows": rows, "findings": findings}


def method_svg(method):
    m = build_method(method)
    rows, protos = m["rows"], m["protos"]
    heads = gate_headings()
    gname = lambda n, dflt: heads[n][0] if n in heads else dflt
    left, pad = 24, 24
    rh = RH * (1 + len(protos)) + 12
    top = 130
    pin_txt = lambda p, note, tag, ok: (f"{p:<4} {note}" + (f" -> {tag}" if ok else ""))
    w3 = max([tw(pin_txt(*pin)) for r in rows for pin in r["pins"]] +
             [tw(r["wire"] + " [9]") for r in rows] + [230]) + 30
    w2 = max([tw(f"access: {r['access']}") for r in rows] +
             [tw(f"validation: {r['validation']}") for r in rows] + [180]) + 30
    wt = max([tw("steps: " + ", ".join(r["steps"])) for r in rows] +
             [tw(r["attr"]) for r in rows] + [210]) + 30
    w1 = max([tw(f"{r['out']} : {r['g1']}") for r in rows] + [230]) + 30
    lab = lambda k: max([tw(r[k], 9.5) for r in rows] + [40]) + 46
    x3 = left
    x2 = x3 + w3 + lab("decoded")
    xt = x2 + w2 + lab("decoded")
    x1 = xt + wt + lab("g2out")
    xc = x1 + w1 + 90
    wc = 190
    width = xc + wc + pad
    n = len(rows)
    ytop = top
    body_h = HDR + 12 + 6 + n * rh + 4
    svg = Svg()

    def block(x, w, title, kind, sub):
        svg.rect(x, ytop, w, body_h, "#ffffff", KIND[kind], 1.6, 3)
        svg.rect(x, ytop, w, HDR + 12, KIND[kind], None, 0, 3)
        svg.text(x + 9, ytop + 17, title, 12, "#ffffff", weight="bold")
        svg.text(x + 9, ytop + 31, sub, 10, "#e6edf3")
    block(x3, w3, f"G3 · {gname(3, 'transport')}", "gate3", "per transport: syntax:type -> decode fn")
    block(x2, w2, f"G2 · {gname(2, 'wire contract')}", "gate2", "WireContext fields per wire attr")
    block(xt, wt, "ENGINE · translate", "engine", "schema attribute + declared steps")
    block(x1, w1, f"G1 · {method} contract", "gate1", f"{m['feature']}.yaml · method type {m['mtype']}")
    # caller terminal
    svg.rect(xc, ytop, wc, HDR + 12 + RH + 8, "#ffffff", KIND["caller"], 1.6, 3)
    svg.rect(xc, ytop, wc, HDR + 12, KIND["caller"], None, 0, 3)
    svg.text(xc + 9, ytop + 17, "caller", 12, "#ffffff", weight="bold")
    svg.text(xc + 9, ytop + 31, "adapter / consumer", 10, "#e6edf3")
    cy = ytop + HDR + 12 + RH / 2 + 2
    svg.pin(xc, cy, PALETTE["ink"])
    svg.text(xc + 9, cy + 4, f"{method}() : {m['mtype']}", 11)

    def wire(xa, xb, y, label):
        svg.pin(xa, y, tcolor(label))
        svg.pin(xb, y, tcolor(label))
        svg.path(f"M{xa:.1f},{y:.1f} L{xb:.1f},{y:.1f}", PALETTE["line"], 1.6, layer="under")
        svg.text(xb - 6, y - 4, label, 9.5, tcolor(label), anchor="end", halo=True, layer="over")

    y0 = ytop + HDR + 12 + 6
    for i, r in enumerate(rows):
        ry = y0 + i * rh
        if i:
            for x, w in ((x3, w3), (x2, w2), (xt, wt), (x1, w1)):
                svg.rect(x + 6, ry - 3, w - 12, 0.5, "#d5dbe3", None, 0)
        py = ry + RH / 2 + 2
        mark = (" [" + ",".join(map(str, r["marks"])) + "]") if r["marks"] else ""
        # G3: wire attr + one input pin per transport
        svg.text(x3 + 9, py + 4, r["wire"] or "-", 11, weight="bold")
        if mark:
            svg.text(x3 + 9 + tw(r["wire"] or "-") + 4, py + 4, mark, 10, PALETTE["untyped"], weight="bold")
        for j, (p, note, tag, ok) in enumerate(r["pins"]):
            qy = py + (j + 1) * RH
            svg.pin(x3, qy, PALETTE["ok"] if ok else PALETTE["untyped"])
            svg.text(x3 + 9, qy + 4, f"{p:<4} ", 11, PALETTE["mute"])
            if ok:
                svg.text(x3 + 9 + tw(f"{p:<4} "), qy + 4, f"{note} -> ", 11)
                svg.text(x3 + 9 + tw(f"{p:<4} {note} -> "), qy + 4, tag, 11, tcolor(tag),
                         italic=(tag == UNTYPED))
            else:
                svg.text(x3 + 9 + tw(f"{p:<4} "), qy + 4, note, 11, PALETTE["untyped"], italic=True)
        wire(x3 + w3, x2, py, r["decoded"])
        # G2: context fields
        svg.text(x2 + 9, py + 4, f"access: {r['access']}", 11)
        svg.text(x2 + 9, py + 4 + RH, f"validation: {r['validation']}", 10.5, PALETTE["mute"])
        wire(x2 + w2, xt, py, r["decoded"])
        # translate
        svg.text(xt + 9, py + 4, r["attr"], 11, weight="bold")
        steps = ("steps: " + ", ".join(r["steps"])) if r["steps"] else "steps: none (pass-through)"
        svg.text(xt + 9, py + 4 + RH, steps, 10.5, PALETTE["mute"])
        wire(xt + wt, x1, py, r["g2out"])
        # G1 contract row
        svg.text(x1 + 9, py + 4, f"{r['out']} : ", 11)
        svg.text(x1 + 9 + tw(f"{r['out']} : "), py + 4, r["g1"], 11, tcolor(r["g1"]),
                 italic=(r["g1"] == UNTYPED))
    svg.pin(x1 + w1, cy, PALETTE["ink"])
    svg.path(f"M{x1 + w1:.1f},{cy:.1f} L{xc:.1f},{cy:.1f}", PALETTE["line"], 1.6, layer="under")
    svg.text(xc - 6, cy - 4, m["mtype"], 9.5, anchor="end", halo=True, layer="over")

    svg.text(24, 28, f"{method} · function-block view (all transports with a driver)", 15, weight="bold")
    svg.text(24, 46, "Read path: transport -> G3 decode -> G2 wire context -> engine translate -> G1 output "
             "contract. Green pin = transport has a wire source; red = none.", 10, PALETTE["mute"])
    svg.text(24, 62, f"Transports drawn: {', '.join(m['protos'])} (offline replays the mops wire). "
             "Types: wire YAML syntax:type, CRUDE matrix, driver wire_type_defaults, schema defaults.",
             10, PALETTE["mute"])
    draw_legend(svg, 24, 88)
    fy = ytop + body_h + 30
    svg.text(24, fy, "Findings derived from the declarations (numbers match [n] markers above)", 12,
             weight="bold")
    for i, (fid, text) in enumerate(m["findings"] or [(0, "none")]):
        svg.text(24, fy + 18 * (i + 1), f"[{fid}] {text}" if fid else "none", 10.5, PALETTE["ink"])
    fy2 = fy + 18 * (len(m["findings"]) + 1) + 14
    svg.text(24, fy2, f"Generated: {REGEN} --method {method}  (do not edit by hand)", 10, PALETTE["mute"])
    srcs = [f"crude_engine/schemas/{m['feature']}.yaml", "crude_engine/wire/*.yaml + wire/<overlay>/*.yaml",
            "crude_engine/engine/crude_matrix.yaml", "crude_engine/engine/steps.yaml",
            "crude_engine/drivers/*.yaml (wire_type_defaults)", "crude_engine/transport_registry.py",
            "docs/ARCHITECTURE.md (gate headings)"]
    out = svg.render(width, fy2 + 24, f"{method} function-block view",
                     f"Function-block view of {method}: per-transport wire sources and decode functions, "
                     f"Gate 2 wire context, engine translate steps, and the Gate 1 output contract, with typed pins.",
                     header_comment(f"method {method}", srcs))
    return out, m


# ---------------------------------------------------------------------------
# Index page + CLI
# ---------------------------------------------------------------------------

def index_md(method_results, sys_stats):
    lines = [
        "<!-- GENERATED FILE - do not edit by hand. -->",
        f"<!-- Generator: scripts/generate_function_blocks.py - regenerate with: {REGEN} -->",
        "",
        "# Function-block views (generated)",
        "",
        "IEC 61131-style function-block diagrams of the engine: each block has typed "
        "inputs on the left and typed outputs on the right, and every wire is labelled with "
        "the declared type. They are **generated from the repository's own declarations** "
        "(Python annotations, `transport_registry.py`, wire/schema YAML, the CRUDE matrix and "
        "driver defaults) - nothing is hand-drawn. Where a type is not declared the pin is "
        "drawn `untyped` in red; a bare `list`/`dict`/`Any` is drawn amber.",
        "",
        f"Regenerate: `{REGEN}`",
        "",
        f"Check for drift: `{REGEN} --check`",
        "",
        "## System view",
        "",
        "![System view](system.svg)",
        "",
        f"Annotation gaps on the drawn functions: {sys_stats['untyped']} with no annotation "
        f"(red), {sys_stats['loose']} declared but loose (amber).",
        "",
        "No annotation:",
        "",
        *[f"- `{g}`" for g in sys_stats["gaps"]["untyped"]],
        "",
        "Declared but loose (bare container or `Any`):",
        "",
        *[f"- `{g}`" for g in sys_stats["gaps"]["loose"]],
        "",
    ]
    for method, m in method_results:
        lines += [f"## `{method}`", "", f"![{method}]({method}.svg)", ""]
        lines += ["Findings derived from the declarations:", ""]
        lines += [f"{fid}. {text}" for fid, text in m["findings"]] or ["- none"]
        lines += [""]
    lines += ["## How blocks, pins and types are derived", "",
              "| Element | Source |", "|---|---|",
              "| Gate / pipeline / driver blocks | `FeatureEngine` and `BaseDriver` methods, read with `ast` (not imported) |",
              "| Pin names and types | the function's annotations; no annotation -> `untyped` |",
              "| Gate titles and frames | `### Gate N` headings in `docs/ARCHITECTURE.md` |",
              "| Typed wires | a return type that matches another block's parameter type |",
              "| Dashed wires | calls from one drawn block to another (enable pin) |",
              "| Protocol blocks | `crude_engine/transport_registry.py` `PROTOCOLS` |",
              "| Per-method rows | schema `defaults`/`sub_tables` -> attribute `wire`/`source` -> wire YAML (+ protocol overlay) |",
              "| Decode function | explicit source `tag`, else CRUDE matrix `(syntax, type)`, else driver `wire_type_defaults`, else `untyped` |",
              "| Gate 1 type | Python type of the schema `defaults` value |",
              ""]
    return "\n".join(lines)


def build_all(methods):
    files = {}
    sysout, stats = system_svg()
    files["system.svg"] = sysout
    results = []
    for mth in methods:
        out, m = method_svg(mth)
        files[f"{mth}.svg"] = out
        results.append((mth, m))
    files["README.md"] = index_md(results, stats)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if generated files are stale")
    ap.add_argument("--method", action="append", default=[],
                    help="additional schema method to render (default set: " + ", ".join(DEFAULT_METHODS) + ")")
    ap.add_argument("--out", default=OUT_DIR, help="output directory")
    args = ap.parse_args(argv)
    methods = sorted(set(DEFAULT_METHODS + args.method))
    files = build_all(methods)
    stale = []
    for name, text in files.items():
        path = os.path.join(args.out, name)
        if args.check:
            cur = read(path) if os.path.exists(path) else None
            if cur != text:
                stale.append(name)
        else:
            os.makedirs(args.out, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(f"wrote {rel(path)}")
    if args.check:
        if stale:
            sys.stderr.write("stale (regenerate with " + REGEN + "): " + ", ".join(stale) + "\n")
            return 1
        print("function-block views up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
