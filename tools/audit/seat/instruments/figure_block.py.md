# `figure_block.py`

- `figure_block.py` (tools/pr/) — fills and checks the generated figure blocks
  in a PR body (`<!-- figure-block: NAME -->` ... `<!-- /figure-block -->`).
  When: a figure a registered instrument prints (scope-line, structure-ratchet,
  merge-base), which must not be typed. Refusal: the registry is read from the
  BASE's `tools/pr/figure_registry.json`, so the author chooses no command, only
  a registered name; an unregistered name, or a block that differs from what
  the instrument renders at the head, is refused. A body with no block passes.
  `render NAME` prints one block; `refresh BODY` fills the blocks in a body
  file at the head (what `seat/body_push.sh` and `prepr.sh --body-check` run);
  `verify BODY --base SHA --head SHA` re-renders read-only and refuses a
  difference (what `pr-contract` runs). `--self-test` runs offline over
  fixtures and prints `figure_block self-test: N checks, 0 failed`.
