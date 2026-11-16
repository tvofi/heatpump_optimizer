Question: body_push.sh refuses the figure block on a base mismatch; please re-render it (brief: "If body_push refuses the figure block on a base mismatch ... the orchestrator re-renders it").

Topic r11-pre-round-check-gate-p2, PR #3633. Code handed off: refs/heads/handoff/r11-pre-round-check-gate-p2 at 2cb653f2dddc258386bddd7dc097bb9c0e323c17 (2061e87b06 merged with origin/main 30f9caac90, conflict in tools/audit/seat/roster_edit.py resolved by union, plus one self-test row). `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <body>` passed rc=0 at that sha, its figure-blocks step included (`figure_block verify: 1 block(s), 0 refused` with mb=30f9caac90...).

The body that was refused is kept at refs/heads/handoff-wip/r11-pre-round-check-gate-p2-body a0e1f7eb719028123bcd0e6547b435c5c12b7383.

body_push.sh output (tail):

    figure_block: refreshed 1 block(s) at 2cb653f2dddc
    ERROR   [figure-block] line 91: block `scope-line` names head=2cb653f2dddc mb=6f422812d5d8, this run is head=2cb653f2dddc mb=30f9caac9073; re-render with `figure_block.py refresh <body>`
    figure_block verify: 1 block(s), 1 refused
    REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
    body_push: REFUSED BODY-LINT
    body_push: refused body kept at handoff-wip/r11-pre-round-check-gate-p2-body a0e1f7eb719028123bcd0e6547b435c5c12b7383

The refresh step rendered against mb=6f422812d5 (the PR's base sha), and the verify step reads against the merge base with origin/main, 30f9caac90. The two disagree now that origin/main is merged into the head.
