# Review packet #3272
head: d37fea157d55bdd82fb5b7dc39937b25d954d669
base: f2a015142714383722bf49d7ab20d8398ec9674c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128273359239 success
arch-score / arch-score id=128282221069 success
arm id=128273192077 skipped
budget-raise-gate / budget-raise-gate id=128282220960 success
cancel-superseded id=128282217576 success
codeql id=128282212279 skipped
codeql / Analyze (actions) id=128275230533 success
codeql / Analyze (javascript-typescript) id=128275252800 success
codeql / Analyze (python) id=128275263600 success
gate id=128282221520 success
governance id=128282184472 skipped
governance / delivery-status id=128275264047 success
governance / delivery-status-publish id=128275230381 skipped
governance / env-matrix id=128275229112 success
governance / instrument-self-tests id=128275228970 success
governance / policy-docs id=128275257313 success
governance / record id=128275229994 skipped
governance / wave-script id=128275230306 success
hassfest id=128282222121 skipped
hassfest / hassfest id=128275230081 success
kernel-points id=128282184449 skipped
pr-contract id=128282184641 skipped
pr-contract / pr-contract id=128282072137 success
prelude id=128282183826 success
refresh id=128282218545 success
tests id=128282223422 skipped
tests / arch-instrument id=128275231312 success
tests / briefs id=128275272462 success
tests / browser id=128275229345 success
tests / ci-ratchet id=128276912417 skipped
tests / claims-autofix id=128275230813 skipped
tests / closure-scope id=128275252388 success
tests / closures id=128275229384 success
tests / closures-autofix id=128276911139 skipped
tests / coverage id=128275230578 success
tests / coverage-ratchet id=128275231493 success
tests / fast (3.14) id=128275230401 success
tests / graders-head-copy id=128275231351 success
tests / lane-proofs id=128276605069 success
tests / mutation id=128275268714 success
tests / mutation-autofix id=128275230480 skipped
tests / mutation-pins id=128275230677 skipped
tests / nightly-ha id=128275230492 skipped
tests / nightly-status id=128275258029 success
tests / replay id=128275230655 skipped
tests / typing id=128275230998 success
validate id=128282184089 skipped
validate / validate-hacs id=128275230100 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat f2a015142...17a48e8e8c1f0b0b086da7b455f1b4e29e87af56
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3272.md b/dev/programme/delivery/3272.md
new file mode 100644
index 000000000..8728b3db0
--- /dev/null
+++ b/dev/programme/delivery/3272.md
@@ -0,0 +1 @@
+- [#3272](https://github.com/tvofi/heatpump_optimizer/pull/3272) — **open**, triage: batch 128, P399 ACCEPT narrowed (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch128.md b/dev/programme/triage/s6-batch128.md
new file mode 100644
index 000000000..c682e3cde
--- /dev/null
+++ b/dev/programme/triage/s6-batch128.md
@@ -0,0 +1,28 @@
+# Proposal triage, session s12, batch 128 (P399)
+
+The rolling batch after batch 127. Facts were read at origin/main `f2a015142`, at the roster branch `649f3ed84` and in the dispatch seat's ledger. The ledger is host-local, so another seat re-runs these commands only on the host that holds it.
+
+## P399: fire-without-sources, cloud fires hand-built without session_context.sources
+
+Verdict: ACCEPT narrowed. The benefit is measured, and one incident costs more than the build. The proposed form is changed. A renderer the orchestrator must remember to call fails exactly as the incident did: after a compaction, the orchestrator did not use the body `cloud_dispatch.py` already publishes. The check moves to where every fire passes, a PreToolUse hook on the `RemoteTrigger` tool. Destination R10-POLICY-ROLE-PACK (carries-open), which already owns `.claude/hooks/session-start.sh` and the rendered cloud prompt. This ACCEPT is not taken on the >10 % exemption.
+
+Source: the orchestrator's queue line `s12-fire-without-sources`, 2026-11-07.
+
+Instances (ledger `s9/seat-dispatch/ledger-standin.txt`):
+- **Sourceless fires:** `grep -c REFIRED <ledger>` gives 7, all at 2026-11-07T01:55:33Z, each "first fire had no repo". Their first fires are ledger lines 357 to 363, from 00:28:48Z to 01:40:21Z: f-3262-r1, f-3241-merge, f-3264-r4, f-tml2-resume, f-3244-r6, f-3265-r2 and f-3232-body.
+  - That is 7 of the 7 fires in that window, and 7 of the 12 `FIRED` lines dated 2026-11-07.
+  - The queue line's "7 of 8" denominator was not found in the ledger.
+- **Wall clock lost:** for each seat, the refire time minus the first fire time. The losses are 86.8, 86.8, 50.9, 49.7, 37.8, 15.7 and 15.2 min, which sum to 342.7 min, or 5.7 seat-hours. That corrects the queue line's "30-85 min, about 6.5 seat-hours".
+  - The "about 20 s, last_run SUCCEEDED" detail is the queue line's. It was not re-read, because doing so needs the API.
+- **Window rate:** the ledger has 342 `FIRED` lines since 2026-10-31. The 7 above are the only sourceless fires it records, 2.0 % of fires. The trigger is a compaction, which recurs: the rate is low across the window and 58 % on the day the trigger fired.
+- **The body already exists:** `tools/audit/seat/cloud_dispatch.py` `render` at `f2a015142`, lines 320 to 325, builds `session_context` with `allowed_tools`, `model` and `sources`. Its self-test checks those three keys and the repo URL (lines 994 to 1015). So the defect is in the hand path, not in the renderer.
+
+Cost:
+- One hook script under `.claude/hooks/` of about 30 lines, plus a `RemoteTrigger` matcher in `.claude/settings.json`. It refuses a `create` or `update` whose `job_config.ccr.session_context` lacks a non-empty `sources` or a `model`. A driver test refuses a no-sources body, admits the `cloud_dispatch.py` render, and kills a mutant that drops the check.
+- An S-sized part inside an existing group. There is no API call, and the standing cost is one local process per `RemoteTrigger` call.
+- Both files are code-owned (`/.claude/hooks/` and `/.claude/settings.json` are `@tvofi` in CODEOWNERS), so the pull request needs the owner's review, or a mandate in force. Neither is a `policy_lint.mjs --budgets` row, and no `tests/structure_budgets.json` row covers them.
+- Against that build cost, one incident lost 5.7 seat-hours.
+
+Binding:
+- Carry text: `From triage batch 128 (triage: dev/programme/triage/s6-batch128.md#P399 at <roster sha>): a PreToolUse hook on RemoteTrigger (matcher in .claude/settings.json, script under .claude/hooks/) refuses a create or update whose job_config.ccr.session_context has no non-empty sources or no model, and names the dispatch/<role>-<topic> PAYLOAD.json that cloud_dispatch.py publishes as the body to send. Driver test: a no-sources body refused, a no-model body refused, the cloud_dispatch.py render admitted; a mutant that drops the check is killed. First step: prove the orchestrator session loads the repo hook by a refused no-sources call in that session. Not a cloud_fire.py renderer: the published PAYLOAD.json is that renderer already.`
+- The fixer re-reads the ledger figures at its own base and does not carry them.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
