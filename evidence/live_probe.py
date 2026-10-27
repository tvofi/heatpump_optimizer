import json, sys, os, copy
WT = os.environ["WT"]
sys.path.insert(0, WT + "/tools/audit/seat")
sys.path.insert(0, WT + "/tools/audit")
import roster_sync as R

body = open(os.environ["BODY"], encoding="utf-8").read()
live = json.load(open("/tmp/r10roster.json"))
roster = copy.deepcopy(live)
pr = R.PR(2625, "MERGED", "h", "c"*40, body)

R.pr_body = lambda p, repo, state: body
appends, refusals = R.carry_plan(roster, [pr], "tvofi/heatpump_optimizer", None)
print("RESULT appends_n:", len(appends))
for d, t in appends:
    print("  APPEND", d, "::", t[:110])
print("RESULT refusals_n:", len(refusals))
for n, d, why in refusals:
    print("  REFUSED", d, "from #%s::" % n, why[:140])

# the triage gate over the appended rows (the write path's own gate)
sys.path.insert(0, WT + "/tools/audit/seat")
import roster_edit
read = roster_edit.ruling_reader(WT, WT)
why = roster_edit.triage_refusal([t for _, t in appends], read)
print("RESULT triage_gate_over_appends:", why)

# the livelock row specifically
for d, t in appends:
    if "triage P3/Q3" in t or "P3/Q3" in t:
        print("RESULT livelock_row_appended: True")
