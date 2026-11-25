# `figure_block.py`

- `figure_block.py` (tools/pr/) — renders the registered figures and refuses a
  PR body that stores a figure block (`<!-- figure-block: NAME -->` ...
  `<!-- /figure-block -->`).
  When: a figure a registered instrument prints (scope-line, structure-ratchet,
  merge-base); `pr-contract` renders each into its job summary at the head it
  grades, so a body stores none and no head move leaves one stale. Refusal: the
  registry is read from the BASE's `tools/pr/figure_registry.json`, so the
  author chooses no command, only a registered name; `verify BODY` refuses any
  block marker in a body, rendered, empty or typed (what `pr-contract` and
  `prepr.sh --body-check` run); it reads the body alone. `render NAME` prints
  one block; `strip BODY` deletes every block from a body file written before
  this rule (what `seat/open_pr.sh` and `seat/update_pr.sh` run on the body
  they push). `--self-test` runs offline over fixtures and prints
  `figure_block self-test: N checks, 0 failed`.
