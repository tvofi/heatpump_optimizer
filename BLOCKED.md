# BLOCKED: r11-seam-ratchet-raise

Question: body_push.sh refuses the body at code head c4faf32b9851ba7a1cba3a87453268d409bf2195 because two of its own steps use different bases for the `scope-line` figure block. How should the block be rendered, or should the orchestrator update PR #3735's head first so its recorded base moves?

State:
- The code head c4faf32b98 is pushed to handoff/r11-seam-ratchet-raise. It is b278df39d6 merged with origin/main e698fc8ac3, with no conflict, as the orchestrator directed. Two commits follow. bd58b7341e re-records `module_excess_loc` 21694 -> 21718; the +24 is sensor.py's, from #3616 phase 3a on main, and the commit message carries the reason. c4faf32b98 splits two docstring sentences that `tests/doc_claims.py`'s 40-word comment ratchet refused.
- `tests/structure.py` passes at the head. The eight scoped scripts all return rc 0. `tools/pr/prepr.sh` returned rc 0 at c4faf32b98 with this body.
- The body is kept by body_push at handoff-wip/r11-seam-ratchet-raise-body bf36a165e5.

The refusal (body_push.sh output, verbatim):

    figure_block: refreshed 1 block(s) at c4faf32b9851
    ERROR   [figure-block] line 46: block `scope-line` names head=c4faf32b9851 mb=689f33e2653f, this run is head=c4faf32b9851 mb=e698fc8ac374; re-render with `figure_block.py refresh <body>`
    figure_block verify: 1 block(s), 1 refused
    REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
    body_push: REFUSED BODY-LINT

Cause: body_push.sh (line 243) refreshes the block with `--base` set to the open PR's recorded base.sha. For #3735 that is 689f33e265, the base of the current PR head 430bc6bfad. prepr.sh's `figure_block_check` (`--body-check`, line 264) then verifies with `--base origin/main`, which resolves to the merge base e698fc8ac3. The two agree only while the branch's merge base equals the PR's recorded base, and the directed main merge broke that. The refusal was not worked around.
