# BLOCKED: r10-process-slim-p2 merge repair (PR #3451)

Question: prepr.sh at 9efb4daf8be91abd9347b00666de5800d96a609c refuses only on `ci predict` (one predicted red: governance / instrument-self-tests, step "Show the tick loop refusing its own fixtures", rc 1 at the head, 0 at the base). The cause is in main's tools/audit/seat/tick_loop.sh self-test, not this diff. May this seat move its `HPO_TICK_CODE_DIR=$t/nogit` export above the TICK-GH rows (a one-line repair to an instrument this group does not own), or does the orchestrator take the head with this prediction recorded as local-only?

Code: the merge is done and verified. It is at handoff-wip/r10-process-slim-p2 (step commit ecb36039, parents 4dfe2f4f and 9efb4daf, tree = 9efb4daf). The draft body is at handoff-wip/r10-process-slim-p2-body (BODY.md). Nothing has been pushed to handoff/ or handoff-body/.

Evidence:
- tick_loop.sh is byte-identical between origin/main and this head. Its rows at lines 205-215 (the TICK-GH rows, e899dde4) run before line 218 exports HPO_TICK_CODE_DIR=$t/nogit, so they read the real checkout. Line 216's comment says those rows should never read it.
- If that checkout has a branch checked out and origin/main touched CODE_PATHS since HEAD (behind>0), the pass prints an extra TICK-STALE line. Then `grep -c '^TICK-' = 2` fails.
- Control: main's own commit e899dde4ab, as a branch checkout (behind 441), prints `tick_loop self-test: 30 checks, 1 failed` (the same row). The same commit detached prints `30 checks, 0 failed`. origin/main 14f227c5 as a branch at behind=0 prints `30 checks, 0 failed`.
- This head on its branch (behind=3: origin/main moved 0b276e8c -> 14f227c5 during prepr) fails the row. CI checks out detached, and PR #3451's head 4bc2f3bc had governance / instrument-self-tests success (job 131042180665).
- Second defect, same cause: at a detached checkout behind origin/main, the self-test's restart arm moved this worktree's HEAD to origin/main (observed: HEAD became 14f227c5 after `git checkout --detach` and one `tick_loop.sh --self-test`). That is why prepr cannot simply be re-run detached.

Everything else prepr ran is ok or skip. The body check passed on its own (`prepr.sh --body-check`: PR-BODY 0 error(s), FIGURES 0 refused, CARRY-AUDIT 0 bad). `policy_lint.mjs --budgets` is within every cap with no raise. bus.sh --self-test: 182/0. review_packet.py --self-test: 123/0. check-wave-script.mjs: 222/0. entities.py: ALL 2701 PASSED. structure.py: PASSED.
