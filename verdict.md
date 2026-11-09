Fix review: blocked 1310d182e16b613937de0e200f03f2aa15c65785 ci-red: gate

bus-nonce: bdeaafe96d102f67462f7757276d246a

Round 1 (first review of this head).

## Block
`python3 tools/audit/seat/merge_train.py classify 1310d182e16b613937de0e200f03f2aa15c65785 --pr 3329` prints `RED 1310d182e16b613937de0e200f03f2aa15c65785 pending: none red: gate` (rc 1) at 2026-11-09T01:58Z, the instrument's A5 rule (an older suite's red gate is never hidden behind a newer green). The red suite is run 42524777454 ("CI edit", attempt 1, gate job 128868937229, failure 21:37:08Z): its only non-green job is `gate`. A later "CI edit" run on the same title and sha, 42525709909 attempt 2, concluded success (gate 128931519130, 01:36Z), as did "CI code" run 42524776987 (gate 128896933860) and `pr-contract / pr-contract`. So the substance is green and this looks like a superseded body-edit suite, but the body's Red checks section does not name `gate` at this head (it answers the 1b2307959d53 reds) and the classifier does not read green. Resolve by re-running/superseding run 42524777454 or by the orchestrator's call; I find no defect in the diff. If the orchestrator judges that suite superseded, the rest of this review is a merge.

## Findings
- Residual: the body's headline figure "At origin/main 4fe7d5934b ... reruns=86" is stale for today's main: the same harness at origin/main 6457496ab prints reruns=1 max_attempt=2 alarm=no (fix #3327 merged), so the harness reads as the fixed end there, not red. Not a defect in the PR (the 86 is correct at 52f9fc5b34, re-taken); the RCA document's "at origin/main" wording should say the SHA. Carry: dismissed: the SHAs are named beside each figure in the body; harness behaves correctly at both ends
- Follow-up: Carry 1 (closed-loop convergence check, "must reach the fix before it merges") now targets a fixer whose PR #3327 already merged; its destination is #201 rather than a brief. Whether the closed-loop check landed in the settle self-test was not checked here. Carry: #201

## Evidence
- Head measured: 1310d182e16b613937de0e200f03f2aa15c65785 (ev/HEAD.txt). Merges cleanly with origin/main: `git merge-tree --write-tree origin/main <head>` rc 0, tree c9393df6ab22.
- Diff is six files, no production line, no VERSION/manifest/RELEASE_NOTES change. INERT entry in tests/closures.json is the harness only.
- Harness at head, own RESULT lines (ev/replay_head.txt, ev/replay_ends.txt): replay 52f9fc5b34 reruns=86 max_attempt=44 sim_minutes=72 alarm=yes (red on defect); replay 52f9fc5b34^ reruns=0 max_attempt=1; replay --no-restamp reruns=1 max_attempt=2 alarm=no (null control); replay at origin/main reruns=1 (fixed). Body's 86 / 44 / 72 reproduced; null controls reproduced.
- tests/structure.py: STRUCTURE RATCHET PASSED; fold_ledger.py check: 0 violation(s); carry_audit at head: 3 routed, 0 unrouted. tests/harness_headers.py could not run here (no homeassistant); CI `tests / fast (3.14)` is success.
- Not re-derived: census figures (465/428/324/1618/17) and gate-sweep run totals need the live Actions history TSV; not re-taken. The 2.84 s probe not timed.
- Mutation: the PR adds no production line; the harness's candidate arm-1 control was not rebuilt by me, but the replay's red/green pair at 52f9fc5b34 and origin/main (fix) shows the detector flips.
- CI at head: gate/code run 42524776987 green; budget-raise-gate success.
