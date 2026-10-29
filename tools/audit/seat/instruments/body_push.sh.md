# `body_push.sh`

- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
  fast-forwards after. When: every fixer handoff — the body must never enter
  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
  head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
  checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
  before anything is pushed, with each arm's repair printed; a fetch that
  half-failed leaves a parentless commit the push refuses as a
  non-fast-forward — a rewrite is never forced through; the body commit it
  wrote is read back through `ref_privacy.py guard --commits`, message and
  identity, before the push.
