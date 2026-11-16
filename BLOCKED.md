# BLOCKED: r11-outside-slab-seed-guard (PR #3640 body repair)

Question: body_push.sh refreshes the scope-line figure block against the PR's recorded base 5825e1346c (as pr-contract verifies it), but its own `prepr.sh --body-check` verifies the block against origin/main 6aa7ddc712, and the two render differently at this head (5825e1346c: `MODE: SCOPED -- 23 script(s) run, 10 scoped out.`; origin/main: `MODE: FULL -- every test script runs, nothing is scoped out.`, main having changed tests/closure.py and tests/closures.json since the recorded base). Every body therefore refuses `REFUSED BODY-LINT` while pr-contract would pass it. Should the orchestrator move the PR's recorded base (merge origin/main into fix/r11-outside-slab-seed-guard), or land the body by hand, and should `figure_block_check` in tools/pr/prepr.sh take the recorded base?

Cause of the pr-contract red at 74a57885a3: the scope-line block was rendered at 59070bb608; mutation-autofix's `ci: pin killed mutants` (74a57885a3) moved the head after the body was set, and `figure_block.py verify` refused the stale head. Nothing else at the head is red.

Repaired body: kept at handoff-wip/r11-outside-slab-seed-guard-body e3edf18508 (## Head names 74a57885a3ef178f2556b4b105063a2b3a2edd9a; block re-rendered against 5825e1346c). `python3 -I tools/pr/figure_block.py verify <body> --base 5825e1346c14eecace5c87c046558774145a94dc --head 74a57885a3` prints `figure_block verify: 1 block(s), 0 refused`; every other body check in body_push's run passed (pr-body 0 errors, figures 0 refused, carry, preflight, ref_privacy).

Code: handoff/r11-outside-slab-seed-guard pushed to 74a57885a3 (the PR's head, fast-forward from a902e7fad4); no code change.

body_push output (refusal lines):
  ERROR   [figure-block] line 49: block `scope-line` is not what the registered instrument printed at 74a57885a3ef; a figure block is rendered, never typed -- run `figure_block.py refresh <body>`
  REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
  body_push: REFUSED BODY-LINT
