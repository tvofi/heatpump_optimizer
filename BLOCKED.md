# BLOCKED: r11-owner-community-standards

Question: body_push.sh refused the figure block on a base mismatch; the brief routes that to the orchestrator for a re-render. Re-render the `scope-line` block (`figure_block.py refresh <body>`) and re-run body_push.sh?

Code handed off: refs/heads/handoff/r11-owner-community-standards at 4e8c918de7dff76e552a5864bed1989766b4568d (6ee7ba56e48b plus a merge of origin/main 92d38ecb640b; tests/layout.json resolved by union). `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh BODY.md` at that head: rc=0 (`PRE-PR: 4e8c918de7df...`).
Refused body kept at handoff-wip/r11-owner-community-standards-body fb1f380b00934ac4a7b3b66979be7f93661fa793.

body_push.sh output:

    figures ok: FIGURES: 13 resolved, 1 not verified, 0 refused
      ERROR   [figure-block] line 85: block `scope-line` names head=4e8c918de7df mb=921214bf4246, this run is head=4e8c918de7df mb=92d38ecb640b; re-render with `figure_block.py refresh <body>`
    figure_block verify: 1 block(s), 1 refused
    REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
    body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again
    body_push: REFUSED BODY-LINT

The body as written named mb=92d38ecb640b; after the prepr run the block's marker read mb=921214bf4246 (#3626's merge, an ancestor-side main older than 92d38ecb640b), while origin/main is still 92d38ecb640b.
