# Review packet #3238
head: 08d62371ac0d8170ab74042b254f3b961d26fdfc
base: b88684a218923f85de66f1e8fb1833e31a76a154

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=127755607996 success
arch-score / arch-score id=127764555395 success
arm id=127755384114 skipped
budget-raise-gate / budget-raise-gate id=127764554853 success
cancel-superseded id=127764554709 success
codeql id=127764554562 skipped
codeql / Analyze (actions) id=127755553082 success
codeql / Analyze (javascript-typescript) id=127755553065 success
codeql / Analyze (python) id=127755552969 success
gate id=127764554410 success
governance id=127764554676 skipped
governance / delivery-status id=127755553003 success
governance / delivery-status-publish id=127755555340 skipped
governance / env-matrix id=127755552991 success
governance / instrument-self-tests id=127755553165 success
governance / policy-docs id=127755553156 success
governance / record id=127755554523 skipped
governance / wave-script id=127755553089 success
hassfest id=127764554345 skipped
hassfest / hassfest id=127755552869 success
kernel-points id=127764554617 skipped
pr-contract id=127764555812 skipped
pr-contract / pr-contract id=127763796116 success
prelude id=127764606000 success
refresh id=127764553641 success
tests id=127764554486 skipped
tests / arch-instrument id=127755742365 success
tests / briefs id=127755552989 success
tests / browser id=127755742480 success
tests / ci-ratchet id=127761701024 skipped
tests / claims-autofix id=127757085999 skipped
tests / closure-scope id=127755552898 success
tests / closures id=127755742495 success
tests / closures-autofix id=127757684260 skipped
tests / coverage id=127755742469 success
tests / coverage-ratchet id=127761699143 success
tests / fast (3.14) id=127755742477 success
tests / graders-head-copy id=127761699176 success
tests / lane-proofs id=127761699146 success
tests / mutation id=127755552971 success
tests / mutation-autofix id=127755812334 skipped
tests / mutation-pins id=127755812143 skipped
tests / nightly-ha id=127755744545 skipped
tests / nightly-status id=127755552833 success
tests / replay id=127755744367 skipped
tests / typing id=127755742379 success
validate id=127764554762 skipped
validate / validate-hacs id=127755552935 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat dad3178d6c81cfe2bb410e7045de28f686a6f845...c1dd4a51c0aa9aaf39b0ca4556aa11e487f05824
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
diff --git a/dev/programme/delivery/3238.md b/dev/programme/delivery/3238.md
new file mode 100644
index 000000000..66fec7266
--- /dev/null
+++ b/dev/programme/delivery/3238.md
@@ -0,0 +1 @@
+- [#3238](https://github.com/tvofi/heatpump_optimizer/pull/3238) — **open**, triage: batch 126, P391 and P392 DEFER (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch126.md b/dev/programme/triage/s6-batch126.md
new file mode 100644
index 000000000..c0fedc3c5
--- /dev/null
+++ b/dev/programme/triage/s6-batch126.md
@@ -0,0 +1,95 @@
+# Proposal triage, session s12, batch 126 (P391, P392): the existing set under the 5 % and 10 % rules
+
+**The bar.** Owner, relayed by the orchestrator: "the non production CIs and the triage seat should fulfil the cost benefit analysis, the "5 percent rule" for existing ones and 10 percent rule for new ones". Working reading, the orchestrator's: a measured improvement in CI time, programme completion time, right-first-time or token usage, each figure with its command. New: over 10 %. Existing: at least 5 %, or a candidate for removal. Unmeasured does not pass. It applies to every ruling from P391. Removing anything is a proposal to the orchestrator; nothing here is an action.
+
+**How a figure was taken.**
+- **Cost, CI.** `actions/workflows/ci.yml/runs` and `actions/runs/<id>/jobs`: job end less start, skipped jobs excluded. Sample: 220 of the 400 newest of 2405 runs in 7 days, from 2026-11-04T22:06Z to 2026-11-05T07:04Z: 294 runner hours, 80 minutes a run. A share below is of those 294 hours. It is 9 hours of runs, not a week, and it counts waiting inside a job.
+- **Benefit, CI.** Every failed run of 2026-10-28 to 2026-11-05, read whole: 380 pull-request and 55 push runs, against 228 pull requests merged since 2026-10-29. "PRs" counts pull requests whose branch had this lane red, then a later green run or a merge. **It is an upper bound on right-first-time:** later green does not prove a defect, a scope change also clears a red, and no failure log was read. A red within 12 h of the same lane red on main is not counted. 5 % of 228 is 12 pull requests.
+- **Tokens.** Local session transcripts modified since 2026-10-01, usage summed per message id. Cloud seats are not in these files.
+- The two listing scripts and the raw JSON are kept in the seat's folder, outside the tree.
+
+## P391: the non-production CI lanes
+
+Verdict: DEFER. Twelve lanes fail the bar even at the upper bound, together 25 % of the sampled runner hours. What would change it: the owner's decision on each proposal below, or a measured benefit the lane's owner brings.
+
+Source: the owner's ruling above, by the orchestrator's message after P390.
+
+Instances:
+
+**Proposed for removal or narrowing: under 12 pull requests at the upper bound.** "Req" means `tools/ci/prelude.py` `UNITS` names it, so removing it is a change to the gate and its ruleset contract.
+
+| lane | share | mean s | PRs | req | proposal |
+|---|---|---|---|---|---|
+| `governance / instrument-self-tests` | 10.9 % | 1317 | 8 | no | run only on a diff reaching the instruments; 19 of its 31 red runs sat within 12 h of its own red on main |
+| `tests / arch-instrument` | 5.6 % | 669 | 0 | yes | run only on a diff reaching the score's own files |
+| `governance / env-matrix` | 2.9 % | 349 | 0 | yes | remove or narrow; five past assertions are its reason, none in this window |
+| `governance / policy-docs` | 1.6 % | 191 | 1 | yes | narrow to policy paths |
+| `arch-score / arch-score` | 1.0 % | 82 | 1 | when production is reached | keep only if the owner wants the score enforced |
+| `governance / wave-script` | 0.8 % | 94 | 0 | yes | narrow |
+| `tests / briefs` | 0.7 % | 90 | 1 | yes | narrow to roster and brief paths |
+| `tests / graders-head-copy` | 0.3 % | 55 | 0 | no | remove or narrow |
+| `tests / lane-proofs` | under 0.1 % | 4 | 0 | no | negligible either way |
+
+**Proposed for removal because the red catches nothing.** They report main's state, so a red does not depend on the pull request.
+
+| lane | share | red | evidence |
+|---|---|---|---|
+| `governance / delivery-status` | 0.7 % | 36 heads, 25 pull requests | reports the record's conclusion on main |
+| `tests / nightly-status` | 0.4 % | 175 heads, 74 pull requests | reports the last nightly; `slow` was red on three of the last three schedules. A red must be answered in the body: this batch's predecessor was refused for it once. That cost is not counted |
+| `tests / ci-ratchet` | 0.1 % | 52 of 55 failed pushes to main | the owner has ruled no pause on it (2026-11-04), so its red stops nothing |
+
+**Not refuted, kept.**
+- `tests / mutation-pins (1-7)`, 7.4 %, with `tests / mutation-autofix`: 18 `ci: pin killed` commits on main since 2026-10-29, 7.9 % of 228. Each spares a repair round but restarts CI, which is not netted out. This is the nearest case: the net could be under 5 %.
+
+**Cost known, benefit not measurable from this data, so unmeasured and not passing.**
+
+| lane | cost, 7 days | why |
+|---|---|---|
+| `merge-main.yml` | 244 runs, about 10.6 h | conflict repairs it spares were not counted |
+| `gate-sweep.yml` | 2500 runs, about 19.7 h from 12 sampled | re-judges a stale red; false reds cleared were not counted. Close to the gate's safety |
+| `record-autofix` (`nightly.yml` push) | 244 runs, about 4.4 h | a record beat, not a check: 46 `ci: record delivery` and 12 `ci: record nightly` commits are its output, not a measure |
+| `governance / record`, `delivery-status-publish` | 0.2 % | same |
+| `tests / closures-autofix` | under 0.1 % | 3 `ci: re` commits, 1.3 %; cheap, under the bar |
+| `tests / claims-autofix` | under 0.1 % | no commit in the window |
+| `dependabot-automerge.yml` | 822 runs, about 1.9 h | 1 dependabot pull request of 228; 397 of 400 listed runs skipped. Proposed for narrowing |
+| `dependency-graph.yml`, `marketplace.yml`, `pages.yml` | under 0.1 h | negligible; no improvement figure exists for any of them |
+
+**Could not be measured.** `kernel-points.yml`: 0 of 220 sampled runs executed it, so no cost. `tests.yml`, `governance.yml`, `codeql.yml` and the other called files have no runs of their own: they are priced as jobs of `ci.yml`. `probe.yml` and `probe-options-freeze.yml`: listed by the API, no runs.
+
+**Separate, not ruled.** Required safety lanes: `gate` (1.2 %), `prelude` (11.8 %), `pr-contract` (0.4 %, 63 pull requests), `budget-raise-gate` (0.7 %, 4), `codeql` (15.6 %, no red), `hassfest` (0.4 %), `validate-hacs` (0.5 %), `closures` (9.8 %, 8) and `closure-scope` (0.6 %, 0), which keep the scoped gate honest, `refresh` and `cancel-superseded` (2.8 %), and `release.yml`. Production tests: `fast` (8.1 %, 18), `coverage` (9.1 %), `coverage-ratchet`, `browser` (1.7 %), `typing` (0.6 %, 2), `mutation` (2.9 %, 17), `replay` (1.1 %, 8), and `nightly.yml`'s `slow`, `nightly-ha`, `mutation-nightly` and `mutation-ledger`.
+- **Worth the orchestrator's eye, not ruled:** the 16 scheduled and dispatched nightlies cost 176 h in 7 days, and a run rose from about 7 h to about 17 h on 2026-11-01. `prelude` holds a runner for 570 s a run, 11.8 %, partly waiting. `closures` is 9.8 % and sits under the 12 at its upper bound, so if the owner reads it as non-production it joins the first table.
+
+**Limits of this reading.** A check is insurance, so eight days without a red is weak evidence against it. A lane too cheap to measure cannot show 5 % either. The orchestrator's reading, not the owner's, puts both in the candidate column.
+
+Cost: removing the first two tables would free up to 25 % of sampled runner hours. Gate-listed lanes need `tools/ci/prelude.py`, the workflows and the ruleset's contract changed, all code-owned. Narrowing needs a measured scope, as `replay` already has (R10-REPLAY-SCOPED). No capped file is touched by this ruling.
+
+Binding: no action. Each proposal goes to the owner through the orchestrator; a removal keeps its reason in the decision record. Do not route this as CI capacity: the owner ruled that out on 2026-11-01, and this is the cost-benefit ruling the owner asked for.
+
+## P392: the triage seat
+
+Verdict: DEFER. On the working reading the seat does not pass: its cost is measured and its benefit is not. This seat is ruling on itself, so the orchestrator should weigh this with that in mind.
+
+Source: the owner's ruling above.
+
+Instances:
+- **Cost, strict match on seat prompts, 55 sessions from 2026-10-24 to 2026-11-04, against all local transcripts since 2026-10-01.**
+
+  | | seat | share |
+  |---|---|---|
+  | output | 5.27 M | 8.6 % |
+  | cache creation | 71.5 M | 12.0 % |
+  | cache read | 1.92 G | 7.2 % |
+
+  Reviews of triage pull requests add 0.50 M output and 0.16 G cache read. The two windows differ, and cloud seats are missing from both sides, so a share is approximate. This session alone: 0.31 M output and 36 M cache read for four rulings (P387 to P390) and their repairs.
+- **What it produced.** 382 entries on the roster branch: 233 ACCEPT, 93 DEFER, 55 REJECT, 1 owner. 247 roster carries cite triage: 56 marked implemented, 58 moved, 5 dismissed, 57 on a closed group, 71 on an open group.
+- **What is not measured.** No ruling has a before-and-after figure on any of the four measures. The ledger meant to record a proven improvement over 10 %, `exemptions` in `dev/governance/config/machinery_budgets.json`, is empty. The cost a REJECT or DEFER avoided is an estimate, never a measurement. No week ran without the seat to compare.
+- **This session's own record.** P389 was a proposal the instrument already answered, and the orchestrator withdrew it. P387's finding was real when filed, then answered by the fix. This seat also made four slips, all corrected: a wrong calibration re-check, a wrong note on one harness arm, body commits under the owner's name, and a copy into another seat's temp directory.
+
+Cost: removing the seat frees at most 7 to 12 % of local tokens, less whatever moves to the orchestrator; that is not measured either.
+
+Binding: proposed, for the owner through the orchestrator, smallest first:
+1. **From P391, apply the bar at the door.** A queue line with no measured figure gets a one-line DEFER, with no investigation. That needs no decision and is this seat's own change. It should cut tokens per ruling, and the ledger will show by how much.
+2. **Measure before deciding:** one week of that form against the week before, on tokens per ruling and on blocked verdicts of the groups that received carries. Under 5 % on both, remove the seat.
+3. **Or remove it now:** the orchestrator applies the one-line cost test itself and sends only what it cannot judge.
+
+An owner directive keeps its route: P386 needed no cost test on whether, only on form.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
