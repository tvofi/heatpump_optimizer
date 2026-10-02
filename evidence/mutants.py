"""Reviewer's own mutants of the new code in tests/mutation_table.py, each applied
in place, the entities.py block run with the fixer's runner (sha1 1cc0dcf8), restored."""
import subprocess, sys
from pathlib import Path
P = Path("tests/mutation_table.py"); orig = P.read_text()
RUN = ["python3", "/Users/timmalmstrom/hpo-seats/R9-F10.6/scratch/run_block.py"]
M = {
 "M0 none": ("", ""),
 "E1 CMP_BOUND out of RATCHETED": ('"BOOLOP", "CONST", "CMP_BOUND"))', '"BOOLOP", "CONST"))'),
 "M1 keep operator": ("+ gap.replace(flip[0], flip[1], 1)", "+ gap"),
 "M4 listed_sites ignores ledger": ("loose = {id(s) for s in unpinned_sites(budgets, sites)}", "loose = {id(s) for s in sites}"),
 "R2 chain left not advanced": ("        left = right\n", "        pass\n"),
 "R3 no Gt/GtE": ("ast.Gt: (\">\", \">=\"), ast.GtE: (\">=\", \">\")}", "}"),
 "R5 multi-line compares admitted": ("if bounds and isinstance(node, ast.Compare) and _one_line(node, lines):", "if bounds and isinstance(node, ast.Compare):"),
 "R6 gap check dropped": ("if flip and gap.strip(\" \\t()\") == flip[0]:", "if flip:"),
 "R7 bounds never generated": ('return (m for m in _generate(path, "CMP_BOUND" in kinds)', 'return (m for m in _generate(path, False)'),
 "R8 Lt flips wrong way": ("ast.Lt: (\"<\", \"<=\")", "ast.Lt: (\"<\", \">\")"),
 "R9 kinds filter dropped": ("            if m[\"kind\"] in kinds)", "            if True)"),
 "R10 LISTED empty": ("LISTED = RATCHETED", "LISTED = frozenset(('CMP_BOUND',)) - RATCHETED"),
}
for name, (a, b) in M.items():
    if a:
        assert orig.count(a) == 1, (name, orig.count(a)); P.write_text(orig.replace(a, b))
    try:
        r = subprocess.run(RUN, capture_output=True, text=True, timeout=300)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print(f"RESULT mutant [{name}] rc={r.returncode} fails={len(fails)} last={tail[:100]!r}")
        for f in fails: print("     ", f[:110])
    finally:
        P.write_text(orig)
