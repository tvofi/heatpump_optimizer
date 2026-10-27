"""Fix-review's driver for #2889 B1: the finder's end-to-end construction,
run at both ends, plus the predicate edges the brief names.
WT=<worktree> python3 -I driver.py
"""
import json, os, sys
WT = os.environ["WT"]
sys.path.insert(0, WT + "/tools/audit/seat")
sys.path.insert(0, WT + "/tools/audit")
import roster_sync as R
import roster_edit

OLD = hasattr(R, "carried_from")
print("RESULT driver_end:", os.path.basename(WT), "predicate=",
      "carried_from" if OLD else "already_carried")

def show(name, got, want):
    print(f"RESULT {name}: got={got!r} want={want!r} -> "
          f"{'PASS' if got == want else 'FAIL'}")

# ---- end-to-end: the finder's construction, verbatim ----------------------
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
    return R.carry_plan(roster(carries), [pr], "fixture/roster", None)

appends, refusals = plan(["From #15 (R9-CARRY): finding one landed."])
print("RESULT e_two_rows_one_held: appends=%r refusals=%r" % (appends, refusals))
lost = len(appends) == 0
print("RESULT e_finding_two_lost:", lost)
print("RESULT e_both_distinct_findings_survive:", len(appends) == 2)

appends2, refusals2 = plan([])
print("RESULT f_null_control_both_append:", len(appends2) == 2,
      "appends=%r refusals=%r" % (appends2, refusals2))

# ---- unit arms, feature-detected -----------------------------------------
held15 = ["From #15 (R9-CARRY): landed."]
if OLD:
    pred = R.carried_from
    show("a_duplicate_refused", pred(held15, 15), held15[0])
    show("b_same_pr_no_matching_carry_appends", pred([], 15), None)
    show("c_other_pr_named_appends", pred(["From #1525 (other): landed."], 15), None)
    show("d_null_control_appends", pred([], 15), None)
    show("b_ii_same_pr_distinct_finding_refused", pred(held15, 15), held15[0])
    show("two_distinct_one_pr_lost",
         pred(held15, 15) is not None, True)
else:
    pred = R.already_carried
    show("a_duplicate_refused",
         pred(held15, "From #15 (R9-CARRY): landed."), held15[0])
    show("b_same_pr_no_matching_carry_appends",
         pred([], "a finding. Carry: R9-DEST"), None)
    show("c_other_pr_named_appends",
         pred(["From #1525 (other): landed."], "a distinct finding. Carry: R9-DEST"), None)
    show("d_null_control_appends", pred([], "x"), None)
    show("b_ii_same_pr_distinct_finding_survives",
         pred(held15, "a genuinely different finding from #15. Carry: R9-DEST"), None)
    show("e_1525_is_not_15",
         pred(["From #1525 (other): landed."], "fifteen. Carry: R9-DEST"), None)

# ---- the predicate's own edges -------------------------------------------
HELD_WIDGET = ["the widget parser drops a unit. `Carry: R9-ECHO`"]
if not OLD:
    show("edge_markup_only_duplicate_refused",
         pred(HELD_WIDGET, "the widget parser drops a unit. Carry: R9-ECHO"),
         HELD_WIDGET[0])
    # one finding, recorded twice in DIFFERENT words, no shared ruling:
    # disclosed to append.
    show("edge_reworded_duplicate_appends",
         pred(["finding one landed."], "finding one, already landed by routing. Carry: R9-DEST"),
         None)
    # two distinct findings on one PR, sharing only provenance boilerplate:
    show("edge_boilerplate_only_appends",
         pred(["From #15 (R9-CARRY): the widget parser drops a unit."],
              "From #15 (R9-CARRY): the batch loader double-counts. Carry: R9-DEST"),
         None)
    # a ruling key shared by two DIFFERENT findings: suppressed by the ruling arm
    h = ["triage P3 (s4) routed the widget parser fix."]
    show("edge_shared_ruling_collapses_distinct",
         pred(h, "a different finding whose row merely cites triage P3 (s4). Carry: R9-DEST"),
         h[0])
    # markup normalisation joins two different numeric/identifier spellings
    show("edge_asterisk_collision",
         pred(["budget 2*3 per pass."], "budget 23 per pass. Carry: R9-DEST"),
         "budget 2*3 per pass.")
    show("edge_underscore_collision",
         pred(["call set_state now."], "call setstate now. Carry: R9-DEST"),
         "call set_state now.")

# ---- an unresolvable ruling key ------------------------------------------
def gate(texts):
    return roster_edit.triage_refusal(
        texts, roster_edit.ruling_reader(WT, WT))
print("RESULT unresolvable_prose_no_match_appends_and_gate:",
      pred([], "a proposal: triage P99 (s4). Carry: R9-DEST") if not OLD else "n/a",
      "->", gate(["a proposal: triage P99 (s4). Carry: R9-DEST"]))
print("RESULT unresolvable_cite_no_match_appends_and_gate:",
      pred([], "proposal triage P7 (s4). Carry: R9-DEST") if not OLD else "n/a",
      "->", gate(["proposal triage P7 (s4). Carry: R9-DEST"]))
print("RESULT unresolvable_file_cite_gate:", gate(
    ["proposal (triage: dev/programme/triage/s9-batch1.md#P1). Carry: R9-DEST"]))
if not OLD:
    show("edge_unresolvable_key_matches_held",
         pred(["holds triage: dev/programme/triage/s9-batch1.md#P1"],
              "proposal triage P1 (s9). Carry: R9-DEST"),
         "holds triage: dev/programme/triage/s9-batch1.md#P1")

# ---- live corpus: prose #2447 reference no longer matches ------------------
live = json.load(open("/tmp/r10roster.json"))
groups = live.get("groups") or live
for g in groups:
    if isinstance(g, dict) and g.get("group") == "R10-POLICY-FIXER-MD":
        got = pred(g.get("carry") or [], "a distinct finding. Carry: R10-POLICY-FIXER-MD") \
              if not OLD else pred(g.get("carry") or [], 2447)
        print("RESULT g_live_prose_reference_matches_2447:", repr(got)[:160])
