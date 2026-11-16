#!/usr/bin/env python3
"""R11-RCA-SELFTEST-TABLE-DRIFT harness, the rejected countermeasure: one-hop static detector of new reads by gated self-test steps.

    python3 dev/audit/harnesses/r11_selftest_static_edge.py REPO BASE HEAD [--table-ref REF]

For each gated step's committed entry (table at --table-ref, default HEAD), every
file the diff BASE..HEAD changes that the entry already reads is scanned at BASE
and HEAD for references to tracked paths (literal path strings, a bare file name
resolved beside the file, Python imports); a reference new at HEAD that the entry
does not name (files, dirs, probes) is printed: STEP KIND PATH VIA.
"""
import json, os, re, subprocess, sys

repo, base, head = sys.argv[1:4]
tref = sys.argv[sys.argv.index("--table-ref") + 1] if "--table-ref" in sys.argv else head


def git(*a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout


def show(ref, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


tracked = set(git("ls-tree", "-r", "--name-only", head).split("\n")) - {""}
dirs = set()
for p in tracked:
    d = os.path.dirname(p)
    while d:
        dirs.add(d)
        d = os.path.dirname(d)
TOK = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*")
IMP = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\s+([\w, ]+)|import\s+([\w., ]+))", re.M)


def refs(path, text):
    out = set()
    here = os.path.dirname(path)
    for t in TOK.findall(text):
        t = t.rstrip("/.")
        if t.startswith("./"):
            t = t[2:]
        for c in (t, os.path.normpath(os.path.join(here, t)) if "/" not in t or t.startswith("..") else None):
            if c and c != path and (c in tracked or (c in dirs and "/" in c)):
                out.add(c)
    if path.endswith(".py"):
        for m in IMP.finditer(text):
            mods = [m.group(1)] if m.group(1) else [x.strip().split(" ")[0] for x in m.group(3).split(",")]
            if m.group(1):
                mods += [m.group(1) + "." + x.strip().split(" ")[0] for x in m.group(2).split(",")]
            for mod in mods:
                rel = mod.replace(".", "/")
                for c in (rel + ".py", rel + "/__init__.py", os.path.join(here, rel + ".py")):
                    if c in tracked and c != path:
                        out.add(c)
    return out


table = json.loads(show(tref, "tools/ci/selftest_closures.json"))["steps"]
changed = [l.split("\t") for l in git("diff", "--name-status", "--no-renames", base, head).splitlines()]
changed = {p for s, p in changed if s != "D"}
cache = {}
n = 0
for sid, e in sorted(table.items()):
    known = set(e.get("files", [])) | set(e.get("dirs", [])) | set(e.get("probes", []))
    for f in sorted(changed & set(e.get("files", []))):
        if f not in cache:
            h, b = show(head, f), show(base, f)
            cache[f] = refs(f, h or "") - refs(f, b or "")
        for r in sorted(cache[f] - known):
            kind = "dirs" if r in dirs and r not in tracked else "files"
            print(sid, kind, r, "via", f)
            n += 1
print(f"# {n} flagged, {len(changed)} changed files", file=sys.stderr)
