Fix review: merge c2e55101f0dc216d5ce4a17d53e5d73adad03c31

bus-nonce: a3f4999687be4cb37baddaa0923bbd68

## Scope

Round 1 review of #3320 (R10-SUITE-HOST-DETERMINISM part 2) at head c2e55101f0dc216d5ce4a17d53e5d73adad03c31. Reviewed from detached worktrees at the head and at merge base 6188936a8bdc58b510ecb8794ad86350283c49a7. I compared the role contract between the merge base and origin/main: no difference under dev/governance/roles/.

## Evidence

- RESULT head: the head I measured is c2e55101f0dc216d5ce4a17d53e5d73adad03c31, and `git ls-remote` shows the branch still at that SHA when this verdict was written. The PR body names the same head. Its prepr SHA, b974110d7, is an ancestor of the head; the later commits are a clean main merge and the delivery row.
- RESULT merge: `git merge-tree --write-tree origin/main c2e55101f0dc216d5ce4a17d53e5d73adad03c31` gives rc=0 with tree 25c3a1133b50db7ba9094c2b6259c52f26e89dcf (ev/merge-tree.txt). There are no conflicts and no claim-file paths.
- RESULT CI: `merge_train.py classify c2e55101f0dc216d5ce4a17d53e5d73adad03c31 --pr 3320` gives `GREEN c2e55101f0dc216d5ce4a17d53e5d73adad03c31 pending: none red: none`, rc=0, both times it ran (ev/classify-1.txt, ev/classify-2.txt). No gate check went red at this head, which matches the body's "Red checks: none".
- RESULT mutation: I applied each mutant to tests/entities.py alone and ran the full module; each gives `4 of 2667 ENTITY CHECKS FAILED` against 3 at the unmutated head, so each kills exactly one added row (ev/m1..m4.diff and -out.txt):
  - m1 drops `if platform != "darwin": raise`: FAIL "a task-port refusal is a printed skip on darwin only..."
  - m2 widens `except PermissionError` to `except Exception`: the same row goes red.
  - m3 changes the control to `_ba.scan()` in place of `_ba.scan("HEAD")`: FAIL "bare_array: an uncommitted bare site is invisible to the HEAD scan...".
  - m4 is my own: it deletes the SKIP print. The task-port row goes red because the printed skip is pinned.
- RESULT null/both-ends: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `3 of 2665 ENTITY CHECKS FAILED` at the merge base and `3 of 2667 ENTITY CHECKS FAILED` at the head, both rc=1. The top-level failures are the same three at both ends: the coverage-cache, release-ZIP and Pages-workflow probes. These depend on this seat's environment and are untouched by the diff. Only the embedded nondeterministic detail inside nested null-control lines differs (ev/fails-base.txt, ev/fails-head.txt). The head adds exactly 2 checks, both passing ("a task-port refusal..." and "bare_array: an uncommitted bare site..."), and nothing else moved. This confirms the body's claim of +2.
- Not re-derived: the body's absolute counts, 2645 and 2647 "ALL PASSED" at b4ec2f332. My base is the newer 6188936a8, where both ends carry 20 more checks and the 3 environment failures above. I verified the delta (+2, no other movement) and not the absolute figure. Carry 5's "does not reproduce in this cloud seat" holds here too, in the sense that no U0c or delivery_status row failed; the 3 failures in this seat are different, environment-only rows present at both ends.
- Figures: I did not re-run structure.py or prepr.sh, following the rule to cite CI's heavy runs. CI's gate, structure/ratchet lanes and pr-contract are green at this head. The mutation lane is green, and the diff writes no production line, so the lane drew no mutant; the hand mutants above stand in for it.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden: untouched (three-dot diff covers only dev/programme/delivery/3320.md and tests/entities.py).
- Class: I grepped for `_remote_debugging`, `task_for_pid` and `_ba.scan(` in tests/entities.py. That turned up one stdlib-sampler call site, now routed through `_hb_stdlib_arm` with sys.platform, and one HEAD scan plus its control. The class is one seam per carry, and no undispositioned site remains. The rule is one platform rule, only PermissionError on darwin, and m1 and m2 show it does not widen.
- Metrics: the diff moves no budget, closure, INERT, golden or claim file, so steps 4 and 14 have nothing to judge beyond the entities count, which these two new rows earn.
- Harness: the body names no finder's harness for these suite-host carries. The instruments are the entities rows themselves, which the mutants above exercise.
- Forward-carry: carries 1-4 cite merged #3170 (8bf45e5). Carry 9 is routed to R10-FLY-SUITE-ENV-FLAKES with a dismissal reason; carry_audit routes all 5 items.
- Self-audit: `carry_audit.py check` gives rc 0 (ev/carry-audit.txt).

## Findings

none

## Friction

none
