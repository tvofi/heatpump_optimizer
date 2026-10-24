Roster for round 10: marks R10-REF-PRIVACY and R10-STORE done, re-aligns issue wiring with the roster, appends R10-ARCH-DOCS, and carries the roster branch's later stage and carry rows. Part of #201.

## Head

`faf04b0ef3d83d21e2388e000e442da78c97637a` merges the authored code head `47313f3a98f4173ccb6f8ec80d859a85ba4eadff` and then merges origin/main `003c3731c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0d11a7bd63ecac474f3222c3f73272e819f22f4c` merges the authored code head `94929f74abc8408a3e516ba96b828135337b4f03` and then merges origin/main `003c3731c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0942893c2633eb468ba690e11047f2eb88f8b992` merges the authored code head `07ba56db12032cb3412e56c97f9ea9f812ed8c55` and then merges origin/main `dc8aa807f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`21cb9efa67f6f4a2a3c442f03c7134c3a25b5113` merges the authored code head `0fd18f115efe78bb9d6323931d22c473834b5e97` and then merges origin/main `3fb386d50` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`a80d0c67bd29bd23ae5d36d3e0f40ecfd32caad1` merges the authored code head `db7429225c6fb41f9f163f59bdc8252dfe664468` and then merges origin/main `cb93535d8` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d0acb3f5ba141336c297776567900d7cc5c10097` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2384.md`. The authored code head is `6883a65aa5d56a2a92347ce74f325aa7b6497a32`.

`0ae19a514ccf1cf4270b5a02b9aa0c6e2b141374` merges origin/main `994695e06` into the authored code head `6883a65aa5d56a2a92347ce74f325aa7b6497a32` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`07ba56db1` — handoff/audit-r10-roster: everything `db7429225` carried, plus the issue-alignment edits made through `tools/audit/seat/roster_edit.py`: #2228, #2253 and #2317 unwired from R10-ARCHSCORE-COVERAGE, R10-DEEPLINK and R10-DEEPLINK-CENSUS; #2253 wired to R10-ADVISOR and R10-UX-HEALTH; R10-STORE set done (#2375); a BRIEFS-FOLD carry for #2373 round 3; two R10-SCORES brief edits re-anchoring a citation; and R10-ARCH-DOCS appended for #2395. Since `0fd18f115`: five groups appended so every open issue is named by a not-done group (R10-RCA-FRICTION #2331/#2353, R10-POLICY-FIXER-MD #2378, R10-POLICY-GATE-SCOPING #2381, R10-RCA-HEADMOVED #2389, R10-RCA-STRUCTURE-BLIND #2235), R10-ARCHSCORE-COVERAGE `fixes` set to [2259] (needed by #2401's Closes), and stage updates. Each is one `roster_edit` commit (`git log --oneline a80d0c67b..07ba56db1`).

## Mutation proof

N/A — roster state; no production code.

## Null control

N/A — roster state.

## Figures

`git diff --stat origin/main...origin/handoff/audit-r10-roster` prints one path, `dev/programme/rosters/wave-r10-groups.json` (349 insertions(+), 23 deletions(-), measured at `94929f74a`). The roster is not in POLICY_GLOBS (same check as #2380), so no `## Approval` is owed. 

## Red checks

`instrument-self-tests` was red at `0942893c2`. Cause: `ref_privacy --check` refused two roster briefs (R10-RCA-FRICTION and R10-RCA-STRUCTURE-BLIND) that each named an absolute host path, so the roster published this host's account name. Fix: both briefs are rewritten with `roster_edit.py edit-brief` to home-relative `~/...` paths; the roster ref is now at `94929f74abc8408a3e516ba96b828135337b4f03`, where `python3 -I tools/audit/seat/ref_privacy.py --check` prints 0 refused and brief_lint from main prints `TOTAL: 0 error(s)`. The cheaper detector is that same `ref_privacy --check`, which already runs in `instrument-self-tests`; its standing cost is a red after the roster lands, because nothing refuses at `roster_edit` write time (it guards the ref name and commit message, not the brief text). The `pr-contract` red at the same head was this section saying "none".

## Forward-carry

none — stage bookkeeping only.

## Friction

none



