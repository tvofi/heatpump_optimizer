# BLOCKED: R11-OUTSIDE-ROOMS-P2 repair, body_push refused the figure block on a base mismatch

Question: the figure block cannot satisfy both bases until the pull request's recorded base moves. Will the orchestrator land the body kept at `handoff-wip/r11-outside-rooms-p2-body` (`ff038a8639cff42acd9aa704298e8d82dafc9cf1`) once the PR head is updated to the code head below?

- Code head, pushed to `handoff/r11-outside-rooms-p2`: `3a16b7a938b10b66a49c5c9fceb20835e9d06785`, a fast-forward of the PR head `69dc1cd4f2e1b3ca16be9ebb1a4e3a9764bdb92f`.
- `tools/pr/prepr.sh` at that head, with the body: `PRE-PR: 3a16b7a938b10b66a49c5c9fceb20835e9d06785 ... rc=0` (PREPR_SKIP_CLOSURES=1).
- Refusal, `bash tools/audit/seat/body_push.sh r11-outside-rooms-p2 BODY.md`, exit 1:

~~~text
figure_block: refreshed 1 block(s) at 3a16b7a938b1
  ERROR   [figure-block] line 92: block `scope-line` names head=3a16b7a938b1 mb=6f422812d5d8, this run is head=3a16b7a938b1 mb=2d7161a4b709; re-render with `figure_block.py refresh <body>`
figure_block verify: 1 block(s), 1 refused
REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
body_push: REFUSED BODY-LINT
body_push: refused body kept at handoff-wip/r11-outside-rooms-p2-body ff038a8639cff42acd9aa704298e8d82dafc9cf1
~~~

Cause: the code head merges origin/main at `2d7161a4b709`, because `git merge-tree --write-tree origin/main 69dc1cd4f2` reported conflicts. `body_push.sh` renders against the open pull request's recorded `base.sha`, which is still `6f422812d5d8`. Its local verify reads the merge base `2d7161a4b709`. Every other step passed: pr-body, carry, preflight, figures and ref_privacy.

What the code head carries: three checks in `tests/features.py` and three `killed_by` rows, which pin the five sites CI run 43942831682 refused (`PIN KILLED: 5 pinned, 0 left unpinned`). The mutation ratchet now reads 2162 against 2175 at `6f422812d5d8` and 2162 against 2165 at `2d7161a4b709`. Then the origin/main merge, with the runs.py/rooms.py count conflicts resolved to both, and `docs/architecture.md` brought to 96 modules and 62 HA-free modules. The kept body has the measurements.
