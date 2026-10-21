"""Reviewer-built probe: does a sibling group's pull request decide another group's stage?"""
import sys; sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_sync as rs
def g(gid, stage, br): return {"group": gid, "resume": {"stage": stage, "branch": br}}
# Case A: STALE-PATHS still open, its sibling STALE-PATHS-2's PR merges.
roster = {"groups": [g("R10-STALE-PATHS", "in-progress", "handoff/r10-stale-paths"),
                     g("R10-STALE-PATHS-2", "in-progress", "handoff/r10-stale-paths-2")]}
prs = [rs.PR(900, "MERGED", "fix/r10-stale-paths-2", "f" * 40, "")]
ch, _, _ = rs.derive(roster, prs)
for c in ch: print("A", c.group, c.was, "->", c.stage, "PR", c.pr, c.merge_commit[:8])
print("RESULT caseA_misattributed=", sum(c.group == "R10-STALE-PATHS" for c in ch))
# Case B: DEEPLINK done; a sibling DEEPLINK-CENSUS PR is open.
roster = {"groups": [g("R10-DEEPLINK", "done", "handoff/r10-deeplink"),
                     g("R10-DEEPLINK-CENSUS", "not-started", "handoff/r10-deeplink-census")]}
prs = [rs.PR(901, "OPEN", "fix/r10-deeplink-census", None, None)]
ch, _, _ = rs.derive(roster, prs)
for c in ch: print("B", c.group, c.was, "->", c.stage, "PR", c.pr)
print("RESULT caseB_done_reopened=", sum(c.group == "R10-DEEPLINK" for c in ch))
# Null control: siblings absent, only the group's own PR.
roster = {"groups": [g("R10-STALE-PATHS", "in-progress", "handoff/r10-stale-paths")]}
ch, _, _ = rs.derive(roster, [rs.PR(902, "MERGED", "fix/r10-stale-paths-2", "e" * 40, "")])
print("RESULT null_no_sibling_group_still_matches=", len(ch))
