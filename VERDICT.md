Fix review: blocked 5d0223e47fcb3070f71a2474133acb8c5f8e8a66 scope-incomplete: the REVIEW STALLED arm (P328) the dispatch brief and the PR title name is not in the diff

bus-nonce: 2304b6e3bc4e52f3e5641f42c105944e

Round 1. Measured head 5d0223e47fcb3070f71a2474133acb8c5f8e8a66 (authored code 76d7da18).

## Block
- The dispatch brief lists P328 (REVIEW STALLED arm: git-only, dispatch ref older than 90 min, no verdict at the head) among the group's carries, and the PR title says "and stalled reviews". The three-dot diff (merge base 2fc0e95b2) touches only orchestrator_tick.py (verdict_levels, prs, one_pr, self-test), owed_unactioned.py and two instrument docs, with no REVIEW STALLED line and no 90-minute rule. The body describes only the P294 arms and its Forward-carry says "none".
- I could not read P327/P328 either: dev/programme/triage/s6-batch90.md does not exist on origin/main, the roster brief for this group at origin/handoff/audit-r10-roster stops at P294, and neither names P327 or P328. Either the arm is owed in this PR (add it, with the null controls: a head with a verdict at it and a dispatch younger than 90 min must not be listed) or the title and body must drop it and the arm be carried to a named group. The orchestrator should decide which.

## Findings
- The PR title claims stalled reviews while the code adds none: a mismatch between title and diff. Carry: R10-FLY-TICK-APPROVAL-OWED | #3041 | O1 | dismissed: not dismissed, owed by the block above

## Evidence
- Self-tests under env -u BASH_ENV at the head: orchestrator_tick 230 checks, 0 failed; owed_unactioned 43 checks, 0 failed. Both match the body's figures.
- Mutants, each restored: (1) APPROVAL-OWED predicate replaced by False fails "BLOCKED + REVIEW_REQUIRED + merge at the head: APPROVAL-OWED" (230 checks, 1 failed); (2) my own, the isDraft guard dropped, fails "a one-pass UNKNOWN, BEHIND and a draft print neither" (1 failed); (3) my own, UNLEVELLED removed from owed_unactioned FAMILY, fails 3 UNLEVELLED rows (43 checks, 3 failed). The body's mutants 2 and 3 were not re-run.
- Null controls present and passing: stale-head merge verdict, DIRTY, APPROVED+CLEAN gives MERGE-READY only, UNKNOWN, BEHIND, draft, and pending or red check each print neither level.
- git merge-tree --write-tree origin/main 5d0223e47fcb3070f71a2474133acb8c5f8e8a66 exits 0 (tree 721c3fb7), no conflict.
- Carry audit at the head: 0 finding items. Figure lint: 3 resolved, 0 not verified. VERSION, manifest and notes heading are not in the diff.
- CI at render: 6 jobs still in progress (python CodeQL, env-matrix, instrument-self-tests, browser, closures, fast); I did not wait, since the verdict is blocked on scope.
- Not run: the finder's harness (none named; the group is an instrument fly-in).
