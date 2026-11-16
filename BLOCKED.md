# BLOCKED: r11-pre-owner-criteria handoff body

Question: body_push.sh refreshes the scope-line figure block against #3641's recorded base.sha 5825e1346c14eecace5c87c046558774145a94dc, and its own `prepr.sh --body-check --pr-branch fix/r11-pre-owner-criteria` then verifies the block against the merge base with origin/main, e30408f7881cd5602a2c4d7ea9517b0d765652f6, so every run refuses; does the relay move fix/r11-pre-owner-criteria to the code head (updating the recorded base) and re-run body_push.sh, or is body_push.sh's base choice to be fixed first?

State:
- Code head 92af7f3f9b134188e67e8cd6c985b51049a2f43c is pushed to refs/heads/handoff/r11-pre-owner-criteria (merges origin/main 921214bf42 and e30408f788; CLAUDE.md union and corpus_tokens re-record in the commit messages).
- `PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1 tools/pr/prepr.sh <body>` at that head: rc=0.
- The body is kept, refused, at refs/heads/handoff-wip/r11-pre-owner-criteria-body 4be0d535c70f49d4ba0d050142d151a2e320bc69.

body_push.sh output (the refusing lines):
  ERROR   [figure-block] line 40: block `scope-line` names head=92af7f3f9b13 mb=5825e1346c14, this run is head=92af7f3f9b13 mb=e30408f7881c; re-render with `figure_block.py refresh <body>`
  REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
  body_push: REFUSED BODY-LINT

Cause, read in tools/audit/seat/body_push.sh: `FB=$(pr_recorded_base ...)` feeds `figure_block.py refresh --base "$FB"`, while the following `prepr.sh --body-check` verifies at the merge base with origin/main. Not worked around.
