"""Reviewer's own driver for carried_from / carry_plan at PR #2889's head."""
import json, sys
WT = __import__("os").path.expanduser("~/hpo-seats/r10s6/review-2889/wt")
sys.path.insert(0, WT + "/tools/audit/seat")
sys.path.insert(0, WT + "/tools/audit")
import roster_sync as R

def show(name, got, want):
    print(f"RESULT {name}: got={got!r} want={want!r} -> {'PASS' if got == want else 'FAIL'}")

# ---- the four constructions the brief names -------------------------------
held_from_15 = ["From #15 (R9-CARRY): landed."]
show("a_duplicate_refused", R.carried_from(held_from_15, 15), held_from_15[0])
show("b_same_pr_no_matching_carry_appends", R.carried_from([], 15), None)
show("c_other_pr_named_appends", R.carried_from(["From #1525 (other): landed."], 15), None)
show("d_null_control_appends", R.carried_from([], 15), None)
# (b) as the predicate itself cannot distinguish: destination names PR #15,
# derived item is a genuinely different finding from #15.
show("b_ii_same_pr_distinct_finding_refused", R.carried_from(held_from_15, 15), held_from_15[0])

# ---- end-to-end: two distinct Carry: rows, same destination, one held ----
DEST = "R9-DEST"
def roster(carries):
    return {"repo": "fixture/roster", "session": "r9-sync", "groups": [
        {"group": DEST, "lane": "L1", "issues": [], "fixes": [], "after": [],
         "brief": "dest", "carry": list(carries),
         "resume": {"stage": "not-started"}}]}

BODY = (
    "## Forward-carry\n\n"
    "- finding one, already landed by routing. Carry: " + DEST + "\n\n"
    "- finding two, genuinely new and not held. Carry: " + DEST + "\n")

def plan(carries):
    body = BODY
    R.pr_body = lambda pr, repo, state: body
    pr = R.PR(15, "MERGED", "h", "c" * 40, BODY)
    appends, refusals = R.carry_plan(roster(carries), [pr], "fixture/roster", None)
    return appends, refusals

appends, refusals = plan(["From #15 (R9-CARRY): finding one landed."])
print("RESULT e_two_rows_one_held: appends=%r refusals=%r" % (appends, refusals))
print("RESULT e_finding_two_lost:", len(appends) == 0 and any(
    "already carried from #15" in r[2] for r in refusals))

appends2, refusals2 = plan([])
print("RESULT f_null_control_both_append:", len(appends2) == 2, appends2)

# ---- live corpus: a prose reference to a PR is read as a carry from it ----
live = json.load(open("/tmp/r10roster.json"))
groups = live.get("groups") or live
if isinstance(groups, dict):
    groups = list(groups.values())
for g in groups:
    if isinstance(g, dict) and g.get("group") == "R10-POLICY-FIXER-MD":
        got = R.carried_from(g.get("carry") or [], 2447)
        print("RESULT g_live_prose_reference_matches_2447:", repr(got)[:160])
