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
- Refuses `head-stale` (exit 1, body kept at `handoff-wip/<topic>-body`) when the body's `## Head` does not name `handoff/<topic>`'s code sha: a repair body kept the previous handoff's head (#3212, #3230, #3231; R10-PROCESS-SLIM carry 1).
- Renders the body's figure block (`figure_block.py refresh`) against the base `pr-contract` verifies with: the open pull request's recorded `base.sha` when origin holds `fix/<topic>` with an open pull request (read by `pr_args.sh`'s `pr_recorded_base`, as `update_pr.sh` and `open_pr.sh`'s p2 do), `origin/main` where none exists yet (R11-HOTFIX-FIGURE-BLOCK-BASE). An unreadable recorded base refuses, nothing pushed.
