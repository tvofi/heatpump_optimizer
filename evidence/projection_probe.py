"""Reviewer's own probe (A4/A5 equivalence): one pass merges R9-LEG (only a legacy carry) and R9-OTH,
whose body routes `Carry: R9-LEG`. The projection with the cut-over set makes R9-LEG done and refuses
the carry; without it (A4/A5) R9-LEG projects carries-open, the carry is appended, and the write path
then writes R9-LEG done holding a pending carry -- STRANDED."""
import sys, copy, io, contextlib
sys.path[:0] = ["/home/user/wt-head/tools/audit/seat", "/home/user/wt-head/tools/audit"]
import roster_lib, roster_sync
def grp(g, carry, br): return {"group": g, "lane": "L1", "issues": [], "fixes": [], "after": [], "brief": "b",
                              "carry": carry, "resume": {"stage": "in-progress", "branch": br}}
roster = {"repo": "fixture/roster", "session": "r9", "groups": [grp("R9-LEG", ["legacy one"], "handoff/r9-leg"),
                                                                 grp("R9-OTH", [], "handoff/r9-oth")]}
legacy = {"R9-LEG": frozenset({"legacy one"})}
body = "## Forward-carry\n\n- the oth finding that the leg group must take up next. Carry: R9-LEG\n"
prs = [roster_sync.PR(61, roster_sync.MERGED, "handoff/r9-leg", "6"*40, "## Friction\n\n- none\n"),
       roster_sync.PR(62, roster_sync.MERGED, "handoff/r9-oth", "7"*40, body)]
for label, proj_legacy in (("projection WITH legacy (head)", legacy), ("projection WITHOUT legacy (A4/A5)", None)):
    r = copy.deepcopy(roster)
    with contextlib.redirect_stdout(io.StringIO()):
        changes, _, transitions = roster_sync.derive(r, prs, legacy)
        projected = copy.deepcopy(r)
        roster_sync.apply_plan(projected, changes, [], proj_legacy)
        appends, refusals = roster_sync.carry_plan(projected, transitions, "x/y", None)
        roster_sync.apply_plan(r, changes, appends, legacy)
    g = roster_lib.groups_of(r)["R9-LEG"]
    print(f"RESULT {label}: derived={[ (c.group,c.stage) for c in changes]} appends={appends} refusals={[x[2][:40] for x in refusals]} "
          f"written R9-LEG stage={g['resume']['stage']} carries={len(g['carry'])} stranded={roster_lib.stranded(r, legacy)}")
