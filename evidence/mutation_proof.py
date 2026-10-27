"""Re-run of s6-batch41.md's triage-gate mutation proof, with the seat's own gate.

Usage: python3 -I mutation_proof.py <repo-worktree>
Reads only the tree; writes nothing. Prints RESULT lines.
"""
import sys
from pathlib import Path
WT = Path(sys.argv[1])
sys.path.insert(0, str(WT / "tools/audit/seat"))
import roster_edit as R

SRC = (WT / "dev/programme/triage/s6-batch41.md").read_text()
CITE = "dev/programme/triage/s6-batch41.md"
read = lambda s: (lambda rel: s)

def show(label, texts, src=SRC):
    why = R.triage_refusal(texts, read(src))
    print(f"RESULT {label}: {'REFUSE ' + why if why else 'ACCEPTED'}")

print("== verdict lines read by the gate ==")
for pid in ("P212", "P213", "P214", "P215"):
    print(f"RESULT verdict {pid}: {R.ruling_verdict(SRC, pid)}")
print("== baseline: ACCEPT entries resolve ==")
show("cite P213", [f"x triage: {CITE}#P213"])
show("cite P214", [f"x triage: {CITE}#P214"])
show("cite P215", [f"x triage: {CITE}#P215"])
print("== control: a REJECT entry must not resolve ==")
show("cite P212", [f"x triage: {CITE}#P212"])
print("== mutant 1: heading '## P213:' changed ==")
m1 = SRC.replace("## P213:", "## P913:", 1)
print("RESULT mutant1 heading changed:", "## P913:" in m1 and "## P213:" not in m1)
show("cite P213 under mutant heading", [f"x triage: {CITE}#P213"], m1)
print("== mutant 2: P213 verdict ACCEPT -> DEFER ==")
i, j = SRC.index("## P213:"), SRC.index("## P214:")
m2 = SRC[:i] + SRC[i:j].replace("Verdict: ACCEPT", "Verdict: DEFER", 1) + SRC[j:]
print("RESULT mutant2 verdict:", R.ruling_verdict(m2, "P213"))
show("cite P213 under mutant verdict", [f"x triage: {CITE}#P213"], m2)
print("== null control: proposal-named text with no citation ==")
show("triage P213 no citation", ["triage P213 asks for the repair hint"])
show("proposal P215 no citation", ["proposal P215 lane rule"])
