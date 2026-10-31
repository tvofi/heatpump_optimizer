# Review packet #3025
head: 35b1ef2e52d3622f9aef104b6e76a32204b9a2dd
base: 18b788ac20af17ecfe83c552420926fbcb05290b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124397194494 success
arch-score / arch-score id=124397154999 success
arm id=124397034732 skipped
budget-raise-gate / budget-raise-gate id=124397155176 success
cancel-superseded id=124397037394 success
codeql / Analyze (actions) id=124397155169 success
codeql / Analyze (javascript-typescript) id=124397155104 success
codeql / Analyze (python) id=124397155175 success
governance / delivery-status id=124397155154 success
governance / delivery-status-publish id=124397156319 skipped
governance / env-matrix id=124397155197 success
governance / instrument-self-tests id=124397155193 in_progress
governance / policy-docs id=124397155258 success
governance / record id=124397156874 skipped
governance / wave-script id=124397155127 success
hassfest / hassfest id=124397155211 success
kernel-points id=124397156199 skipped
prelude id=124397037603 in_progress
refresh id=124397037525 success
tests / arch-instrument id=124397304723 success
tests / briefs id=124397155043 success
tests / browser id=124397304799 success
tests / claims-autofix id=124398496402 skipped
tests / closure-scope id=124397155206 success
tests / closures id=124397304778 in_progress
tests / coverage id=124397304687 success
tests / coverage-ratchet id=124397527732 success
tests / fast (3.14) id=124397304697 success
tests / graders-head-copy id=124397527585 success
tests / lane-proofs id=124398494724 success
tests / mutation id=124397155171 success
tests / mutation-autofix id=124397371478 skipped
tests / mutation-pins id=124397371710 skipped
tests / nightly-ha id=124397306341 skipped
tests / nightly-status id=124397155199 success
tests / replay id=124397306270 skipped
tests / typing id=124397304695 success
validate / validate-hacs id=124397154975 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 18b788ac20af17ecfe83c552420926fbcb05290b lacks origin/main 05be22881b1e63221da6ccec9604c0371969c9c0; roster read at origin/main
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git grep -n 'body_refusal' origin/main -- tools
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3025.md b/dev/programme/delivery/3025.md
new file mode 100644
index 000000000..dd64a82ae
--- /dev/null
+++ b/dev/programme/delivery/3025.md
@@ -0,0 +1 @@
+- [#3025](https://github.com/tvofi/heatpump_optimizer/pull/3025) — **open**, triage: s8 batch 80 (P317 ruling) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch80.md b/dev/programme/triage/s6-batch80.md
new file mode 100644
index 000000000..85181a4dc
--- /dev/null
+++ b/dev/programme/triage/s6-batch80.md
@@ -0,0 +1,69 @@
+# Proposal triage, session s8, batch 80 (P317)
+
+The rolling batch (V182) after batch 79 (handoff `triage-s8-batch79`). Facts were read at
+origin/main `18b788ac2`, on the roster branch, and in the orchestrator's `seat-ledger.md`.
+
+## P317: a PR body's host path is first refused at dispatch, after the body is public
+
+Verdict: ACCEPT, a carry on **R10-FLY-NO-FOOTERS** (`carries-open`, S). That group owns
+body-hygiene refusals in `tools/pr/prepr.sh` (no attribution footers or session links in a PR body,
+refused at prepr with a planted-defect control). A host path in a body is the same class of
+refusal, at the same step.
+- **The rule.** `prepr.sh --body-check`, the step `body_push.sh` runs before publishing a body
+  (`body_push.sh:45`) and `open_pr.sh`'s prepr step 7 runs, applies `ref_privacy.body_refusal` to
+  the body text, and refuses on a non-empty answer. One call, at the single step every body path
+  already passes through.
+- **Narrowed from the filing's "body_push.sh and/or prepr's pr-body step":** prepr's
+  `--body-check` only. It already gates both writers, and a second call site would be a second
+  copy of the check.
+- `review_packet.py:427`'s call stays, as the backstop at dispatch.
+
+Source: the orchestrator s8's message of 2026-10-31 (a slip; the class is "an instrument guard
+narrower than the policy").
+
+Instances:
+- **The gap, read at main.** `ref_privacy.body_refusal` (`ref_privacy.py:300`) is called on a body
+  only at `review_packet.py:427` (dispatch), `gh_comment.py:141` (comments) and `ci_probe.py`
+  (lines 255, 278).
+- **What `--body-check` runs instead.** It runs `privacy_line` (`prepr.sh:1586`), which is
+  `ref_privacy --check`: ref names and lines the diff adds. That never sees the body text.
+  `body_push.sh:90` runs `ref_privacy.py guard` on the ref name and commits, not the body.
+- **#3024.** A home-directory path sat in a `## Figures` grep command. It was first refused at
+  dispatch, then patched live with `body_patch.sh`, and the body ref was re-pushed clean
+  (`c15dfa5a`). The fixer measured `body_refusal` returning "home-directory, account-name in the
+  body" on the old body and None on the clean one, so the detector works and runs too late.
+- **#2958 (batch 60, 2026-10-29).** `seat-ledger.md:2325`: the triage body quoted a home-directory
+  value, which "tripped review_packet host-path on the cloud reviewer". That was the same late
+  catch, on a body already public.
+- Two public leaks in round 10, each caught only after the PR was open.
+
+Cost:
+- About 4 lines in `prepr.sh --body-check`: call `ref_privacy.py` on the body file through
+  `body_refusal` (a `guard --message`-style arm, or a small `body <file>` subcommand), print
+  `REFUSE ref_privacy (body): <reason>`, and fold the rc.
+- Two self-test rows. Under 1 s per call.
+- No new file. `prepr.sh` is not a capped file.
+
+Binding: a public host-path leak twice in round 10, each needing a live body patch, against one
+function call at a step every body already passes. Clearly positive. Owner privacy is the binding
+reason: a leak is public the moment the PR opens, and no later fix unpublishes it.
+
+Carry text (for `roster_edit.py append-carry R10-FLY-NO-FOOTERS`, citing
+`triage: dev/programme/triage/s6-batch80.md#P317`): "P317 (orchestrator 2026-10-31, slip:
+instrument guard narrower than the policy).
+- `tools/pr/prepr.sh --body-check` (the step `body_push.sh:45` runs before publishing and
+  `open_pr.sh`'s prepr step 7 runs) applies `ref_privacy.body_refusal` (`ref_privacy.py:300`) to
+  the body text.
+- A non-empty answer prints `REFUSE ref_privacy (body): <reason>` and refuses, folded into the
+  step's rc like the other arms.
+- `review_packet.py:427`'s dispatch check stays as the backstop.
+- Do not add a second call site in `body_push.sh`: `--body-check` already gates both writers.
+- Observed: #3024's body carried a home-directory path in a `## Figures` command, first refused at
+  dispatch after the PR was public. It was patched live and the body ref re-pushed clean
+  (`c15dfa5a`). #2958 (2026-10-29, `seat-ledger.md:2325`) is the same late catch. `body_refusal`
+  returns "home-directory, account-name in the body" on #3024's old body and None on the clean
+  one.
+- Self-test rows (`prepr.sh --self-test`):
+  - A body with a planted home-directory path refuses with that line.
+  - Null: a body naming only repository-relative paths and `~/`-free text passes.
+- One mutant: drop the call, and the planted row passes."

