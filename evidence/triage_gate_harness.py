"""Reviewer-built harness for roster_edit.triage_refusal, PR #2891.
Reads the committed ruling at <wt>/dev/programme/triage/s6-batch42.md.
Prints RESULT lines; exit 1 if any arm does not move."""
import sys, pathlib
WT = pathlib.Path(sys.argv[1])
SEAT = WT / "tools/audit/seat"
sys.path.insert(0, str(SEAT))
import roster_edit  # noqa

BATCH = "dev/programme/triage/s6-batch42.md"
SRC = (WT / BATCH).read_text(encoding="utf-8")
CITE = f"triage: {BATCH}#P216"
CARRY = "Rule V129 as P216: record a contradictory peer instruction as pending owner confirmation. " + CITE

def reader(src):
    return lambda rel: src if rel == BATCH else None

checks = []
def check(name, cond, detail=""):
    checks.append(bool(cond))
    print(f"RESULT {'PASS' if cond else 'FAIL'} | {name} | {detail}")

# 1. the committed entry's verdict
v = roster_edit.ruling_verdict(SRC, "P216")
check("committed P216 verdict is ACCEPT", v == "ACCEPT", f"ruling_verdict={v!r}")

# 2. a carry citing the ACCEPT entry resolves
r = roster_edit.triage_refusal([CARRY], reader(SRC))
check("ACCEPT citation resolves (None)", r is None, f"refusal={r!r}")

# 3. a DEFER mutant is refused
defer = SRC.replace("Verdict: ACCEPT", "Verdict: DEFER", 1)
r = roster_edit.triage_refusal([CARRY], reader(defer))
check("DEFER mutant refused", r is not None and "DEFER" in r, f"refusal={r!r}")

# 4. a REJECT mutant is refused
reject = SRC.replace("Verdict: ACCEPT", "Verdict: REJECT", 1)
r = roster_edit.triage_refusal([CARRY], reader(reject))
check("REJECT mutant refused", r is not None and "REJECT" in r, f"refusal={r!r}")

# 5. a renamed heading is refused (no such entry)
renamed = SRC.replace("## P216:", "## P216 (relay P1):", 1)
r = roster_edit.triage_refusal([CARRY], reader(renamed))
check("renamed heading refused", r is not None and "no such entry" in r, f"refusal={r!r}")

# 6. null control: a carry naming a proposal with no citation is refused
r = roster_edit.triage_refusal(["proposal P3 changes a lane"], reader(SRC))
check("uncited proposal-sourced text refused", r is not None and "cites no triage ruling" in r, f"refusal={r!r}")

# 7. a citation to a missing batch is refused
r = roster_edit.triage_refusal(["x. triage: dev/programme/triage/nope.md#P1"], lambda rel: None)
check("missing batch refused", r is not None, f"refusal={r!r}")

# 8. non-proposal text passes (true null control, must NOT refuse)
r = roster_edit.triage_refusal(["a normal carry about heat meters"], reader(SRC))
check("plain carry lands (true null control)", r is None, f"refusal={r!r}")

# 9. a citation to an absent entry is refused
r = roster_edit.triage_refusal(["proposal P999. " + CITE.replace("P216", "P999")], reader(SRC))
check("absent entry refused", r is not None and "no such entry" in r, f"refusal={r!r}")

sys.exit(0 if all(checks) else 1)
