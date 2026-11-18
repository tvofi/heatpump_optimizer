#!/usr/bin/env python3
"""Enumerate N-vocabulary-drift seams in the development tooling: places where a
record's writer holds one vocabulary and a reader another.

R1 (two closed vocabularies of one concept): every pair of named word-set
   literals (ALL_CAPS constant, >=3 lower-kebab words; Python AST, JS/MJS const
   arrays/Sets/regex alternations, shell NAME="..."/NAME=(...)) in different
   definitions that share >=2 words, with overlap >= 0.2 of the smaller, and differ.
R2 (a free writer of a closed word): an ALL_CAPS constant named *CLASS*/*STAGE*/
   *VERDICT*/*KIND*/*ID*/*STATUS* whose value is a regex accepting an open
   word ([a-z-]+, [A-Za-z...]*), i.e. a writer contract no closed reader bounds.
Usage: vocabulary_drift.py [ROOT ...] [--json]
"""
import ast, itertools, json, re, sys
from pathlib import Path

WORD = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
NAMEOK = re.compile(r"^[A-Z][A-Z0-9_]*$")
R2NAME = re.compile(r"(CLASS|STAGE|VERDICT|KIND|_ID|ID_|STATUS)")
OPEN = re.compile(r"\[(?:a-z|A-Za-z)[^\]]*\][*+]")
SKIPDIR = ("node_modules", "/rounds/", "/.git/", "fixtures")


def words(seq):
    w = [s for s in seq if isinstance(s, str) and WORD.match(s)]
    return w if len(w) >= 3 and len(w) == len([s for s in seq if isinstance(s, str)]) else None


def py_vocab(f, text):
    out = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for n in ast.walk(tree):
        tgt = val = None
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            tgt, val = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
            tgt, val = n.target.id, n.value
        if not tgt or not NAMEOK.match(tgt):
            continue
        if isinstance(val, ast.Call) and val.args:
            val = val.args[0]
        if isinstance(val, (ast.Set, ast.List, ast.Tuple)):
            w = words([e.value for e in val.elts if isinstance(e, ast.Constant)])
            if w and len(w) == len(val.elts):
                out.append((tgt, n.lineno, w))
        elif isinstance(val, ast.Constant) and isinstance(val.value, str) and R2NAME.search(tgt) and OPEN.search(val.value):
            out.append((tgt, n.lineno, ("R2", val.value)))
    return out


JSCONST = re.compile(r"(?:const|let|var)\s+([A-Z][A-Z0-9_]*)\s*=\s*(new Set\(\s*)?\[([^\]]*)\]", re.S)
JSRX = re.compile(r"(?:const|let|var)\s+([A-Z][A-Z0-9_]*)\s*=\s*/(.+?)/[a-z]*\s*;", re.M)
JSSTR = re.compile(r"(?:const|let|var)\s+([A-Z][A-Z0-9_]*)\s*=\s*(?:new RegExp\(\s*)?(['\"`][\s\S]{0,400}?)(?:\)\s*;|;|\n\n)")
SHVAR = re.compile(r"^\s*(?:readonly\s+|local\s+|declare\s+-a\s+)?([A-Z][A-Z0-9_]*)=(?:\(([^)]*)\)|\"([^\"]*)\"|'([^']*)')", re.M)


def js_vocab(f, text):
    out = []
    for m in JSCONST.finditer(text):
        body = re.sub(r"//[^\n]*", "", m.group(3))
        items = re.findall(r"""['"`]([^'"`]*)['"`]""", body)
        raw = [x for x in body.split(",") if x.strip()]
        w = words(items)
        if w and len(items) == len(raw):
            out.append((m.group(1), text.count("\n", 0, m.start()) + 1, w))
    for m in JSRX.finditer(text):
        name, body = m.group(1), m.group(2)
        alt = re.search(r"\((?:\?:)?([a-z0-9-]+(?:\|[a-z0-9-]+){2,})\)", body)
        line = text.count("\n", 0, m.start()) + 1
        if alt:
            out.append((name, line, alt.group(1).split("|")))
        elif R2NAME.search(name) and OPEN.search(body):
            out.append((name, line, ("R2", body)))
    for m in JSSTR.finditer(text):
        name, body = m.group(1), m.group(2)
        if R2NAME.search(name) and OPEN.search(body):
            out.append((name, text.count("\n", 0, m.start()) + 1, ("R2", body)))
    return out


def sh_vocab(f, text):
    out = []
    for m in SHVAR.finditer(text):
        body = m.group(2) or m.group(3) or m.group(4) or ""
        items = [x for x in re.split(r"[\s|]+", body.strip()) if x]
        w = words(items)
        if w:
            out.append((m.group(1), text.count("\n", 0, m.start()) + 1, w))
    return out


def scan(roots):
    defs = []
    for root in roots:
        root = Path(root)
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        for f in files:
            s = str(f)
            if not f.is_file() or any(k in s for k in SKIPDIR):
                continue
            try:
                text = f.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            fn = {".py": py_vocab, ".mjs": js_vocab, ".js": js_vocab, ".sh": sh_vocab}.get(f.suffix)
            if fn:
                defs += [(s, n, l, w) for n, l, w in fn(f, text)]
    seams = []
    closed = [d for d in defs if not (isinstance(d[3], tuple) and d[3][0] == "R2")]
    for a, b in itertools.combinations(closed, 2):
        sa, sb = set(a[3]), set(b[3])
        common = sa & sb
        if sa == sb or len(common) < 2 or len(common) < 0.2 * min(len(sa), len(sb)):
            continue
        seams.append({"rule": "R1", "a": f"{a[0]}:{a[2]} {a[1]}", "b": f"{b[0]}:{b[2]} {b[1]}",
                      "shared": len(common), "only_a": sorted(sa - sb), "only_b": sorted(sb - sa)})
    for d in defs:
        if isinstance(d[3], tuple) and d[3][0] == "R2":
            seams.append({"rule": "R2", "a": f"{d[0]}:{d[2]} {d[1]}", "regex": d[3][1]})
    return seams


def main():
    roots = [a for a in sys.argv[1:] if not a.startswith("--")] or ["tools", ".claude/workflows", ".claude/hooks"]
    seams = scan(roots)
    if "--json" in sys.argv:
        print(json.dumps(seams, indent=1))
        return
    for s in seams:
        if s["rule"] == "R1":
            print(f"R1 {s['a']}  <>  {s['b']}  shared={s['shared']} only_a={s['only_a'][:8]} only_b={s['only_b'][:8]}")
        else:
            print(f"R2 {s['a']}  open={s["regex"][:70]!r}")
    print(f"seams={len(seams)}")


main()
