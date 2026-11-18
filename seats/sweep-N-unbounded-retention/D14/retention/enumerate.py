"""D14 sweep, class N-unbounded-retention: list every growable container seam.

A seam is a container stored on `self.<name>` (any class) or at module level
in custom_components/heatpump_optimizer/**/*.py that some method GROWS:
  self.X.append/appendleft/extend/insert/add/update/setdefault(...)
  self.X[k] = v   (subscript store)
  self.X += [...]
For each seam it reports whether the same class (or module) also has a BOUND:
  - the container was built as deque(..., maxlen=...)   -> 'maxlen'
  - an eviction on the same name: .pop/.popleft/.popitem/.remove/.discard/
    .clear(), `del self.X[...]`, or a re-assignment `self.X = <expr reading
    self.X>` (slice / filter / comprehension)            -> 'evict'
  - neither                                              -> 'UNBOUNDED'
The card JS (www/*.js) is scanned the same way per `class`, see scan_js.
A bound being present is not proof it bounds by the served window; the
runtime probe (probe.py) decides that for the seams a cycle actually grows.
Run:  python3 dev/audit/rounds/round11/D14/retention/enumerate.py [--root DIR] [--json] [--unbounded]
"""
import ast
import json
import os
import re
import sys

args = sys.argv[1:]
ROOT = args[args.index("--root") + 1] if "--root" in args else "custom_components/heatpump_optimizer"
GROW = {"append", "appendleft", "extend", "extendleft", "insert", "add", "update", "setdefault"}
EVICT = {"pop", "popleft", "popitem", "remove", "discard", "clear"}


def owner_name(node):
    """self.X -> 'X'; module-level Name X -> '::X'."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return node.attr
    return None


def reads(expr, name):
    return any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self"
               and n.attr == name for n in ast.walk(expr))


def scan(path):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    tree = ast.parse(text)
    out = []
    module_names = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    scopes = [(n.name, n) for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    scopes.append(("<module>", tree))
    for cname, scope in scopes:
        grow, bound, maxlen = {}, {}, set()
        nodes = ast.walk(scope) if cname != "<module>" else [
            x for f in tree.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) for x in ast.walk(f)]
        for n in nodes:
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                tgt, meth = n.func.value, n.func.attr
                nm = owner_name(tgt)
                if nm is None and cname == "<module>" and isinstance(tgt, ast.Name) and tgt.id in module_names:
                    nm = "::" + tgt.id
                if nm:
                    if meth in GROW:
                        grow.setdefault(nm, (n.lineno, "keyed" if meth in ("setdefault", "update") else "seq"))
                    elif meth in EVICT:
                        bound.setdefault(nm, ("evict", n.lineno, meth))
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
                # dataclass field: x: Deque = field(default_factory=lambda: deque(maxlen=N))
                if any(isinstance(c, ast.Call) and getattr(c.func, "id", getattr(c.func, "attr", "")) == "deque"
                       and any(k.arg == "maxlen" for k in c.keywords) for c in ast.walk(n.value)):
                    maxlen.add(n.target.id)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name not in ("__init__", "__post_init__"):
                for a in ast.walk(n):
                    if isinstance(a, ast.Assign):
                        flat = [e for t in a.targets for e in (t.elts if isinstance(t, ast.Tuple) else [t])]
                        vals = a.value.elts if isinstance(a.value, ast.Tuple) else [a.value]
                        for t in flat:
                            nm = owner_name(t)
                            if nm and any(isinstance(v, (ast.List, ast.Dict, ast.Set)) and not getattr(v, "elts", getattr(v, "keys", [1]))
                                          or isinstance(v, ast.Constant) and v.value is None
                                          or isinstance(v, ast.Call) and getattr(v.func, "id", "") in ("set", "dict", "list") and not v.args
                                          for v in vals):
                                bound.setdefault(nm, ("evict", a.lineno, "reset"))
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                targets = [e for t in targets for e in (t.elts if isinstance(t, ast.Tuple) else [t])]
                for t in targets:
                    if isinstance(t, ast.Subscript):
                        nm = owner_name(t.value)
                        if nm:
                            grow.setdefault(nm, (n.lineno, "keyed"))
                    nm = owner_name(t)
                    if nm and n.value is not None:
                        v = n.value
                        if isinstance(n, ast.AugAssign) and isinstance(n.value, (ast.List, ast.Tuple, ast.ListComp)):
                            grow.setdefault(nm, (n.lineno, "seq"))
                        elif isinstance(v, ast.Call) and getattr(v.func, "id", getattr(v.func, "attr", "")) == "deque" \
                                and any(k.arg == "maxlen" for k in v.keywords):
                            maxlen.add(nm)
                        elif reads(v, nm):
                            bound.setdefault(nm, ("evict", n.lineno, "reassign"))
            elif isinstance(n, ast.Delete):
                for t in n.targets:
                    if isinstance(t, ast.Subscript):
                        nm = owner_name(t.value)
                        if nm:
                            bound.setdefault(nm, ("evict", n.lineno, "del"))
        for nm, (ln, kind) in sorted(grow.items(), key=lambda x: x[1][0]):
            if nm in maxlen:
                b = "maxlen"
            elif nm in bound:
                b = f"evict:{bound[nm][2]}@{bound[nm][1]}"
            else:
                b = "UNBOUNDED"
            out.append({"file": path, "symbol": f"{cname}.{nm.lstrip(':')}", "grow_line": ln, "bound": b,
                        "kind": kind, "src": lines[ln - 1].strip()[:110]})
    return out


JS_GROW = re.compile(r"this\.(\w+)\.(push|unshift|add|set)\(|this\.(\w+)\[[^\]]+\]\s*=[^=]")
JS_EVICT = re.compile(r"this\.(\w+)\.(splice|shift|pop|delete|clear)\(|this\.(\w+)\.length\s*=|this\.(\w+)\s*=\s*[^;]*this\.\4\.(filter|slice)\(")
JS_CLASS = re.compile(r"^\s*class\s+(\w+)")


def scan_js(path):
    """Per JS class: this.X grown (push/unshift/add/set/[k]=) vs evicted
    (splice/shift/pop/delete/clear/length=/self-filter/slice).  A grow site whose
    container is built fresh in a method other than the constructor counts
    as a reset (`this.X = []|{}|new Set()|new Map()` outside constructor)."""
    out = []
    cls, grow, evict, reset, in_ctor = None, {}, set(), set(), False
    lines = open(path, encoding="utf-8").read().splitlines()

    def flush():
        for nm, (ln, kind, src) in sorted(grow.items(), key=lambda x: x[1][0]):
            b = "evict" if nm in evict else ("reset" if nm in reset else "UNBOUNDED")
            out.append({"file": path, "symbol": f"{cls}.{nm}", "grow_line": ln, "bound": b, "kind": kind, "src": src})

    for i, line in enumerate(lines, 1):
        m = JS_CLASS.match(line)
        if m:
            if cls:
                flush()
            cls, grow, evict, reset = m.group(1), {}, set(), set()
            continue
        if cls is None:
            continue
        if re.match(r"^\s{2}constructor\(", line):
            in_ctor = True
        elif re.match(r"^\s{2}(async\s+)?(static\s+)?(get\s+|set\s+)?\w+\(.*\)\s*\{", line):
            in_ctor = False
        for g in JS_GROW.finditer(line):
            nm = g.group(1) or g.group(3)
            kind = "seq" if g.group(2) in ("push", "unshift", "add") else "keyed"
            grow.setdefault(nm, (i, kind, line.strip()[:110]))
        for e in JS_EVICT.finditer(line):
            evict.add(e.group(1) or e.group(3) or e.group(4))
        r = re.search(r"this\.(\w+)\s*=\s*(\[\]|\{\}|new (Set|Map)\(\))", line)
        if r and not in_ctor:
            reset.add(r.group(1))
    if cls:
        flush()
    return out


def seams():
    res = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if d not in ("translations", "__pycache__", "node_modules"))
        for f in sorted(fn):
            if f.endswith(".py"):
                res.extend(scan(os.path.join(dp, f)))
            elif f.endswith(".js") and not f.endswith(".min.js"):
                res.extend(scan_js(os.path.join(dp, f)))
    return res


if __name__ == "__main__":
    s = seams()
    if "--unbounded" in args:
        s = [x for x in s if x["bound"] == "UNBOUNDED"]
    if "--json" in args:
        print(json.dumps(s, indent=1))
    else:
        for x in s:
            print(f"{x['file']}:{x['grow_line']}  {x['symbol']}  {x['bound']}  {x['kind']}  | {x['src']}")
        print(f"RESULT seams={len(s)} count")
        print(f"RESULT unbounded={sum(x['bound'] == 'UNBOUNDED' for x in s)} count")
        print(f"RESULT unbounded_seq={sum(x['bound'] == 'UNBOUNDED' and x['kind'] == 'seq' for x in s)} count")
