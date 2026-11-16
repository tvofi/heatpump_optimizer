# BLOCKED at the body push: R11-OUTSIDE-SELF-SETTING-PUMP (PR #3662), round-3 design build

Question: `tools/audit/seat/body_push.sh` refuses the body it has just rendered (`body_push: REFUSED BODY-LINT`, rc 1), on the figure block alone. Which base should the `scope-line` block of a pull request whose branch merged main after it opened carry: the pull request's recorded base.sha (what `body_push.sh` renders with, and `pr-contract` verifies with), or the merge base with origin/main (what `prepr.sh --body-check`'s `figure_block_check` verifies with)? Until one of the two instruments moves, no body for this head passes `body_push.sh`; the relay can push the kept body once that is ruled.

## State

- Code, handed off: refs/heads/handoff/r11-outside-self-setting-pump at e1fa50dd751679423507796b6ac938a79df7d791. `tools/pr/prepr.sh` (scoped, `PREPR_SKIP_CLOSURES=1`, the block driver as `MUTANT_CMD`) printed `PRE-PR: e1fa50dd751679423507796b6ac938a79df7d791 00000000000000000000000000000000 rc=0` with the body below.
- Body, not published: kept by `body_push.sh` at refs/heads/handoff-wip/r11-outside-self-setting-pump-body, 302a27ee63f42b40809ca4dc7ebfe8057d2013b1. refs/heads/handoff-body/r11-outside-self-setting-pump is unmoved (51ba79dea3, the first handoff's body).
- origin/main is b08346b222; `git merge-tree --write-tree origin/main e1fa50dd75` reports no conflict (rc 0).

## The refusal, measured

`body_push.sh` finds origin holding fix/r11-outside-self-setting-pump, reads #3662's recorded base and runs `figure_block.py refresh <body> --base <that base>`. The block then reads `mb=367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c head=e1fa50dd751679423507796b6ac938a79df7d791`. Its next step, `prepr.sh --body-check <body> --pr-branch fix/r11-outside-self-setting-pump`, calls `figure_block_check`, which is `figure_block.py verify "$1" --base origin/main --head HEAD`, and prints:

    ERROR   [figure-block] line 133: block `scope-line` names head=e1fa50dd7516 mb=367c3b9cac0f, this run is head=e1fa50dd7516 mb=6f422812d5d8; re-render with `figure_block.py refresh <body>`
    figure_block verify: 1 block(s), 1 refused
    REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused

Both ends, on the kept body: `figure_block.py verify <body> --base 367c3b9cac --head HEAD` prints `1 block(s), 0 refused`; the same with `--base origin/main` prints `1 block(s), 1 refused`. The two bases differ because this branch contains the repair seat's merge of origin/main 6f422812d5 (b7a77e86dd), made after the pull request opened on 367c3b9cac. Every other line of the lint is `ok` (pr-body 0 errors, carry 9 routed, figures 0 refused, preflight, ref privacy).

Rendered against origin/main by hand, the same body passes `prepr.sh --body-check`; that render is what `body_push.sh` replaces. Not worked around.

## What the body reports, in two lines

The class fix review 1 blocked on is closed at e1fa50dd75: the domain sweep reads 0 of 2370 self-setting rows `follows` and 0 of 360 heat-led rows `does_not_follow`, and the reviewer's seven rows read `does_not_follow` at 1.000 on all five seeds (20 of 35 `follows` at the blocked head). Two heat-led harness rows that learned at the base and at the blocked head do not learn under the approved design, `repriced_heat1.2_true_0.8_x672` and `sub_min_true_0.6_x1440`; both are at the top of the body and under its `## Forward-carry`.
