# `ci_supersede.sh`

- `ci_supersede.sh` — runs this tree's `tools/pr/cancel_superseded.py sweep`
  once, or every SECONDS with `--loop [SECONDS]` (300), each pass stamped
  (CI-6). When: the orchestrator's beat, so a run at a head its pull request
  has left is cancelled within one pass even while the newer run still queues
  for a runner. The cancel rule is the sweep's (never main, a push run, the live
  head or a bot-authored live head). A failed pass is printed and the loop goes
  on; it stops once `$HPO_STATE_DIR/ci-supersede.STOP` exists. Refusal:
  `--loop` without `HPO_STATE_DIR` refuses to start (nothing could stop it);
  `--dry-run` or `DRY=1` cancels nothing.
