"""Reviewer's own harness: run the Pages section of tests/entities.py at a worktree.
Slices from `_PG_WF = Path(".github/workflows/pages.yml")` to the
"# Classified as its siblings" comment, execs it with a recording R, cwd = worktree."""
import os, sys, re, subprocess, tempfile, shutil
from pathlib import Path
from datetime import UTC, datetime, timedelta
import yaml as _yaml
wt = Path(sys.argv[1]).resolve()
wf_override = sys.argv[2] if len(sys.argv) > 2 else None
sys.path.insert(0, str(wt / "tests"))
os.chdir(wt)
lines = (wt / "tests/entities.py").read_text().splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith('_PG_WF = Path(".github/workflows/pages.yml")'))
end = int(os.environ["END"]) if os.environ.get("END") else next(i for i in range(start, len(lines)) if lines[i].startswith("# Classified as its siblings"))
src = "\n".join(lines[start:end])
class _R:
    def __init__(s): s.res = []
    def check(s, name, ok, detail=""):
        s.res.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -- {detail}"))
R = _R()
import throwaway_git
g = {"__name__": "pages_section", "R": R, "Path": Path, "subprocess": subprocess, "tempfile": tempfile,
     "os": os, "re": re, "shutil": shutil, "_yaml": _yaml, "UTC": UTC, "datetime": datetime, "timedelta": timedelta, "_REL_WF": ".github/workflows/release.yml"}
g.update({k: getattr(throwaway_git, k) for k in dir(throwaway_git) if k.startswith("throwaway_git")})
if wf_override:
    src = src.replace('_PG_WF = Path(".github/workflows/pages.yml")', f'_PG_WF = Path({wf_override!r})', 1)
import ast
full = "\n".join(lines); tree = ast.parse(full)
defs = {}
for node in tree.body[:]:
    if node.lineno - 1 >= start: break
    names = []
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        for t in (node.targets if isinstance(node, ast.Assign) else [node.target]):
            names += [n.id for n in ast.walk(t) if isinstance(n, ast.Name)]
    elif isinstance(node, (ast.FunctionDef, ast.ClassDef)): names = [node.name]
    for n in names: defs[n] = ast.get_source_segment(full, node)  # last top-level def before the section wins
for node in tree.body:
    if node.lineno - 1 >= start: break
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        try: exec(ast.get_source_segment(full, node), g)
        except Exception as e: print(f"[harness] import skipped: {e}", file=sys.stderr)
for _ in range(40):
    R.res.clear()
    try:
        exec(compile(src, "entities.py[pages]", "exec"), g); break
    except NameError as e:
        n = e.name
        if n not in defs: raise
        print(f"[harness] pulling top-level definition of {n}", file=sys.stderr)
        exec(defs[n], g)
bad = [r for r in R.res if not r[1]]
print(f"RESULT: {len(R.res)} checks, {len(bad)} failed at {wt.name}")
sys.exit(1 if bad else 0)
