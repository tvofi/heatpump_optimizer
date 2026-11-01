# `body_push.sh`

- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
  fast-forwards after. When: every fixer handoff — the body must never enter
  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
  head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
  checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
  before anything is pushed, with each arm's repair printed; so is a PR body
  `review_packet.py handoff` refuses (P256); a fetch that
  half-failed leaves a parentless commit the push refuses as a
  non-fast-forward — a rewrite is never forced through; the body commit it
  wrote is read back through `ref_privacy.py guard --commits`, message and
  identity, before the push.
  A PR body's commit (a `handoff/<topic>` exists) ends its message in a
  trailer line `Code: <handoff/<topic> tip>`, the sha the script has proved
  equal to the checkout's HEAD; a result body writes none. `cloud_relay.sh`'s
  handoff arm reads it: a body naming another head is held as
  `handoff-body-stale`, and a body naming a tip the PR head already holds is
  applied body-only (`update_pr.sh` with code `-`).
