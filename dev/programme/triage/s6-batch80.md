# Proposal triage, session s8, batch 80 (P317)

The rolling batch (V182) after batch 79 (handoff `triage-s8-batch79`). Facts were read at
origin/main `18b788ac2`, on the roster branch, and in the orchestrator's `seat-ledger.md`.

## P317: a PR body's host path is first refused at dispatch, after the body is public

Verdict: ACCEPT, a carry on **R10-FLY-NO-FOOTERS** (`carries-open`, S). That group owns
body-hygiene refusals in `tools/pr/prepr.sh` (no attribution footers or session links in a PR body,
refused at prepr with a planted-defect control). A host path in a body is the same class of
refusal, at the same step.
- **The rule.** `prepr.sh --body-check`, the step `body_push.sh` runs before publishing a body
  (`body_push.sh:45`) and `open_pr.sh`'s prepr step 7 runs, applies `ref_privacy.body_refusal` to
  the body text, and refuses on a non-empty answer. One call, at the single step every body path
  already passes through.
- **Narrowed from the filing's "body_push.sh and/or prepr's pr-body step":** prepr's
  `--body-check` only. It already gates both writers, and a second call site would be a second
  copy of the check.
- `review_packet.py:427`'s call stays, as the backstop at dispatch.

Source: the orchestrator s8's message of 2026-10-31 (a slip; the class is "an instrument guard
narrower than the policy").

Instances:
- **The gap, read at main.** `ref_privacy.body_refusal` (`ref_privacy.py:300`) is called on a body
  only at `review_packet.py:427` (dispatch), `gh_comment.py:141` (comments) and `ci_probe.py`
  (lines 255, 278).
- **What `--body-check` runs instead.** It runs `privacy_line` (`prepr.sh:1586`), which is
  `ref_privacy --check`: ref names and lines the diff adds. That never sees the body text.
  `body_push.sh:90` runs `ref_privacy.py guard` on the ref name and commits, not the body.
- **#3024.** A home-directory path sat in a `## Figures` grep command. It was first refused at
  dispatch, then patched live with `body_patch.sh`, and the body ref was re-pushed clean
  (`c15dfa5a`). The fixer measured `body_refusal` returning "home-directory, account-name in the
  body" on the old body and None on the clean one, so the detector works and runs too late.
- **#2958 (batch 60, 2026-10-29).** `seat-ledger.md:2325`: the triage body quoted a home-directory
  value, which "tripped review_packet host-path on the cloud reviewer". That was the same late
  catch, on a body already public.
- Two public leaks in round 10, each caught only after the PR was open.

Cost:
- About 4 lines in `prepr.sh --body-check`: call `ref_privacy.py` on the body file through
  `body_refusal` (a `guard --message`-style arm, or a small `body <file>` subcommand), print
  `REFUSE ref_privacy (body): <reason>`, and fold the rc.
- Two self-test rows. Under 1 s per call.
- No new file. `prepr.sh` is not a capped file.

Binding: a public host-path leak twice in round 10, each needing a live body patch, against one
function call at a step every body already passes. Clearly positive. Owner privacy is the binding
reason: a leak is public the moment the PR opens, and no later fix unpublishes it.

Carry text (for `roster_edit.py append-carry R10-FLY-NO-FOOTERS`, citing
`triage: dev/programme/triage/s6-batch80.md#P317`): "P317 (orchestrator 2026-10-31, slip:
instrument guard narrower than the policy).
- `tools/pr/prepr.sh --body-check` (the step `body_push.sh:45` runs before publishing and
  `open_pr.sh`'s prepr step 7 runs) applies `ref_privacy.body_refusal` (`ref_privacy.py:300`) to
  the body text.
- A non-empty answer prints `REFUSE ref_privacy (body): <reason>` and refuses, folded into the
  step's rc like the other arms.
- `review_packet.py:427`'s dispatch check stays as the backstop.
- Do not add a second call site in `body_push.sh`: `--body-check` already gates both writers.
- Observed: #3024's body carried a home-directory path in a `## Figures` command, first refused at
  dispatch after the PR was public. It was patched live and the body ref re-pushed clean
  (`c15dfa5a`). #2958 (2026-10-29, `seat-ledger.md:2325`) is the same late catch. `body_refusal`
  returns "home-directory, account-name in the body" on #3024's old body and None on the clean
  one.
- Self-test rows (`prepr.sh --self-test`):
  - A body with a planted home-directory path refuses with that line.
  - Null: a body naming only repository-relative paths and `~/`-free text passes.
- One mutant: drop the call, and the planted row passes."
