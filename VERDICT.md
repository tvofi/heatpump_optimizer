Fix review: merge d7e9677502d03d9e62f96aab6c17a43e7a745a49

bus-nonce: 93e2cfeacef87183dc3032e5693a5362

## Notes

- Note: figure: the body's `## Figures` reports `r10_flow_dispatch_mutants.py` as 60 `verdict=killed` beside `M0` plus 5 `CRASHED`. At this head the run prints 67 distinct `RESULT mutant=` rows: `M0` null-ok, 61 killed and 5 CRASHED. Its own `RESULT mutants=66 survived=0` and exit 0 match the body, so the miscount is off by one on the killed rows only and changes no conclusion (ev/r10_flow_head.log). Carry: dismissed: body paperwork, off by one with no survivor; it changes no stage's work

## Evidence

Round 3. This is a delta review over the reviewed head 036d2a7ff405b55e9178de65b2cbd14ec50d57b8, measured from a detached worktree at d7e9677502d03d9e62f96aab6c17a43e7a745a49.

Contract and head:

- `git diff 174e78cebf...origin/main -- dev/governance/roles/` touches only `architect-planner.md` and `plan-review.md`. `fix-review.md` is current.
- The delta from 036d2a7ff4 is c19f09a911 plus the merge d7e9677502 (parents 036d2a7ff4 and c19f09a911). It touches only `dev/audit/harnesses/r10_flow_dispatch_mutants.py`, 2 lines.
- There is no production delta, so the scope is not widened.
- The three-dot diff from 174e78cebf names no `VERSION`, `RELEASE_NOTES.md` or `custom_components/` path.
- The PR body's `## Head` names d7e9677502d03d9e62f96aab6c17a43e7a745a49. `git ls-remote origin refs/pull/3705/head` re-read before the verdict prints the same SHA (ev/head_recheck.txt).

Previous block (class-open, `brief-drop` and `part-line-dropped` matching nothing):

- RESULT pin counts at this head in `tools/audit/seat/cloud_dispatch.py`: `brief=group_brief(group, roster, fixer=role == "fixer")\n` occurs 1 time, and `for ln in (dline, pline) if ln)` occurs 1 time (lines 700-701).
- RESULT `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`, whole, at this head: `RESULT mutant=M0 failed=0 verdict=null-ok`, `RESULT mutant=brief-drop failed=12 verdict=killed`, `RESULT mutant=part-line-dropped failed=3 verdict=killed`, `RESULT mutants=66 survived=0`, exit 0 (ev/r10_flow_head.log).
- The worktree was clean after the run. Round 2 recorded the failing reading at 036d2a7ff4: `abort: brief-drop's pattern occurs 0 times`, exit 2.
- The two re-spelled pins carry the intents round 2 planted by hand: the brief is dropped, and the part line is dropped from the join. Resolved.
- RESULT step-8 rule, widened to path spellings: `git grep -l -e cloud_dispatch -e cloud-setup d7e9677502 -- dev/audit/harnesses` returns 8 files, the eight the body lists and says it ran (ev/step8_rule.txt). The class is closed for this diff.
- The 5 CRASHED rows (`parent-drop`, `topic-to-id`, `roster-repo-ignored`, `pointer-off`, `part-count`) match the body. The body records the first four as identical at the merge base. I did not re-run the base, because they are outside the delta.

Checks and merge:

- RESULT classify: `GREEN d7e9677502d03d9e62f96aab6c17a43e7a745a49 pending: none red: none` (ev/classify.final).
- `owed-reds` excludes `tests / nightly-status`, the packet digest's only red, so no `## Red checks` answer is owed (ev/owed_reds.txt).
- RESULT `git merge-tree --write-tree origin/main d7e9677502`: rc=0, no conflict (ev/merge_tree.txt).

Prior-round findings: the `r10_cloud_setup_mutants.py` `M0` temp-dir finding was dismissed as main's, and nothing in this delta touches it.
