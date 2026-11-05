import shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(sys.argv[1]); P="tools/audit/machinery_ratchet.py"
src=(ROOT/P).read_text()
M=[
 ("null-control", "\n", "\n"),
 ("budgets-from-base", "doc = load_budgets(_budgets_text(repo, head, BUDGETS))", "doc = load_budgets(_budgets_text(repo, base or head, BUDGETS))"),
 ("round-down", "(2000 * nonproduct + product) // (2 * product)", "(1000 * nonproduct) // product"),
 ("octopus-counted", "        if len(ps) == 2:\n", "        if len(ps) >= 2:\n"),
 ("budgets-touch-not-required", "    if pr is None or budgets not in touched:", "    if pr is None:"),
 ("before-zero-allowed", "or before <= 0:", "or before < 0:"),
 ("short-history-accepted", "        if len(rows) < w:\n            raise", "        if False:\n            raise"),
 ("extra-key-accepted", "    if extra:\n", "    if False:\n"),
 ("event-base-only", "    if base and pr:\n", "    if base:\n"),
 ("no-product-refusal", "    if product == 0:\n        raise", "    if False:\n        raise"),
 ("bool-before-accepted", "if isinstance(v, bool) or not isinstance(v, (int, float))", "if not isinstance(v, (int, float))"),
 ("entry-key-missing-ok", "    if missing:\n        return False", "    if False:\n        return False"),
 ("record-file-version-dropped", "RECORD_FILES = (\"RELEASE_NOTES.md\", \"VERSION\")", "RECORD_FILES = (\"RELEASE_NOTES.md\",)"),
 ("window-lt1-ok", "    if doc[WINDOW_KEY] < 1:", "    if False:"),
 ("candidate-exempt-unchecked", "        ex, why = exemption(repo, mb, head, pr, s[\"paths\"], g.budgets) if g.honour else (False, \"\")", "        ex, why = False, \"\""),
]
with tempfile.TemporaryDirectory() as d:
  t=Path(d)
  for rel in (P,"tests/throwaway_git.py"):
    (t/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/rel,t/rel)
  for name,a,b in M:
    if src.count(a)!=1: print("STALE",name,src.count(a)); continue
    (t/P).write_text(src.replace(a,b,1))
    r=subprocess.run([sys.executable,"-I",str(t/P),"--self-test"],capture_output=True,text=True)
    f=[l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(("killed  " if r.returncode else "SURVIVED"), name, len(f), (f[0][:150] if f else ""))
