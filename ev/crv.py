"""Reviewer's own harness (not the finder's; none committed): run head's
_coverage_revalidation helper against the coverage_tree.sh of a given worktree."""
import ast, sys, os, subprocess, tempfile
from pathlib import Path
src = Path(sys.argv[1]).read_text()          # head's tests/entities.py
tree = ast.parse(src)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_coverage_revalidation")
ns = {"_tempfile": tempfile, "_os": os, "_subprocess": subprocess, "Path": Path}
exec(compile(ast.Module([fn], []), "crv", "exec"), ns)
os.chdir(sys.argv[2])
for label, kw in (("null", dict(late=False)), ("late", dict(late=True)), ("late_wait0", dict(late=True, wait_s=0))):
    runs, ran, out, led, nodata, who = ns["_coverage_revalidation"](floor_fails=False, **kw)
    print(f"RESULT {label}: late_script={who!r} nodata={nodata} refused={'left descendants still running' in out}")
