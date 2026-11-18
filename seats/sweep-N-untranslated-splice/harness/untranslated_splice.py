#!/usr/bin/env python3
"""Enumerate N-untranslated-splice seams: a translated message whose placeholder
carries runtime text the integration does not translate (an exception string).

Python: every value of a translation_placeholders / description_placeholders /
placeholders dict literal whose expression reads an exception (a name bound by
`except ... as NAME`, str()/repr()/f-string of it, `.args`) or a parameter or
local named like an error string (error, err, detail, reason, cause, exc, msg).
JS (card): every L(...) parameter object value reading `.message` or String(err).
Usage: untranslated_splice.py [ROOT] [--json]
"""
import ast, json, re, sys
from pathlib import Path

ERRWORDS = re.compile(r"^(e|err|error|exc|ex|exception|detail|reason|cause|msg|message|why)$")
KW = {"translation_placeholders", "description_placeholders", "placeholders"}


def except_names(fn):
    return {h.name for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler) and h.name}


def tainted(expr, excn):
    for n in ast.walk(expr):
        if isinstance(n, ast.Name) and (n.id in excn or ERRWORDS.match(n.id)):
            return n.id
        if isinstance(n, ast.Attribute) and n.attr in ("args", "message", "strerror"):
            return n.attr
    return None


def py_seams(root):
    out = []
    for f in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            continue
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        owner = {}
        for fn in funcs:  # innermost function wins (walk order: outer before inner)
            for n in ast.walk(fn):
                owner[id(n)] = fn
        for call in ast.walk(tree):
            if not isinstance(call, ast.Call):
                continue
            for kw in call.keywords:
                if kw.arg not in KW or not isinstance(kw.value, ast.Dict):
                    continue
                fn = owner.get(id(call))
                excn = except_names(fn) if fn else set()
                for k, v in zip(kw.value.keys, kw.value.values):
                    t = tainted(v, excn)
                    if t:
                        out.append({"file": str(f.relative_to(root.parent.parent) if root.parent.parent in f.parents else f),
                                    "line": v.lineno, "symbol": getattr(fn, "name", "<module>"),
                                    "key": getattr(k, "value", None), "expr": ast.unparse(v), "reads": t})
    return out


JSRE = re.compile(r"(\w+)\s*:\s*\(?\s*(\w+)\s*&&\s*\2\.message|String\((err|error|e)\)")


def js_seams(root):
    out = []
    for f in sorted(root.rglob("*.js")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if JSRE.search(line) and not line.strip().startswith("//"):
                out.append({"file": str(f.relative_to(root.parent.parent)), "line": i, "symbol": "L(...) param",
                            "expr": line.strip()[:120], "reads": "message"})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else "custom_components/heatpump_optimizer").resolve()
    seams = py_seams(root) + js_seams(root)
    if "--json" in sys.argv:
        print(json.dumps(seams, indent=1))
    else:
        for s in seams:
            print(f"{s['file']}:{s['line']} {s['symbol']} {s.get('key')} <- {s['expr']}")
        print(f"seams={len(seams)}")


main()
