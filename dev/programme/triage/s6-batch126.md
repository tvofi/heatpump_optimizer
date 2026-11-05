# Proposal triage, session s12, batch 126 (P391, P392): the existing set under the 5 % and 10 % rules

**The bar.** Owner, relayed by the orchestrator: "the non production CIs and the triage seat should fulfil the cost benefit analysis, the "5 percent rule" for existing ones and 10 percent rule for new ones". Working reading, the orchestrator's: a measured improvement in CI time, programme completion time, right-first-time or token usage, each figure with its command. New: over 10 %. Existing: at least 5 %, or a candidate for removal. Unmeasured does not pass. It applies to every ruling from P391. Removing anything is a proposal to the orchestrator; nothing here is an action.

**How a figure was taken.**
- **Cost, CI.** `actions/workflows/ci.yml/runs` and `actions/runs/<id>/jobs`: job end less start, skipped jobs excluded. Sample: 220 of the 400 newest of 2405 runs in 7 days, from 2026-11-04T22:06Z to 2026-11-05T07:04Z: 294 runner hours, 80 minutes a run. A share below is of those 294 hours. It is 9 hours of runs, not a week, and it counts waiting inside a job.
- **Benefit, CI.** Every failed run of 2026-10-28 to 2026-11-05, read whole: 380 pull-request and 55 push runs, against 228 pull requests merged since 2026-10-29. "PRs" counts pull requests whose branch had this lane red, then a later green run or a merge. **It is an upper bound on right-first-time:** later green does not prove a defect, a scope change also clears a red, and no failure log was read. A red within 12 h of the same lane red on main is not counted. 5 % of 228 is 12 pull requests.
- **Tokens.** Local session transcripts modified since 2026-10-01, usage summed per message id. Cloud seats are not in these files.
- The two listing scripts and the raw JSON are kept in the seat's folder, outside the tree.

## P391: the non-production CI lanes

Verdict: DEFER. Eleven lanes fail the bar even at the upper bound, together 25 % of the sampled runner hours. What would change it: the owner's decision on each proposal below, or a measured benefit the lane's owner brings.

Source: the owner's ruling above, by the orchestrator's message after P390.

Instances:

**Proposed for removal or narrowing: under 12 pull requests at the upper bound.** "Req" means `tools/ci/prelude.py` `UNITS` names it, so removing it is a change to the gate and its ruleset contract.

| lane | share | mean s | PRs | req | proposal |
|---|---|---|---|---|---|
| `governance / instrument-self-tests` | 10.9 % | 1317 | 8 | no | run only on a diff reaching the instruments; 19 of its 31 red runs sat within 12 h of its own red on main |
| `tests / arch-instrument` | 5.6 % | 669 | 0 | yes | run only on a diff reaching the score's own files |
| `governance / env-matrix` | 2.9 % | 349 | 0 | yes | remove or narrow; five past assertions are its reason, none in this window |
| `governance / policy-docs` | 1.6 % | 191 | 1 | yes | narrow to policy paths |
| `arch-score / arch-score` | 1.0 % | 82 | 1 | when production is reached | keep only if the owner wants the score enforced |
| `governance / wave-script` | 0.8 % | 94 | 0 | yes | narrow |
| `tests / briefs` | 0.7 % | 90 | 1 | yes | narrow to roster and brief paths |
| `tests / graders-head-copy` | 0.3 % | 55 | 0 | no | remove or narrow |
| `tests / lane-proofs` | under 0.1 % | 4 | 0 | no | negligible either way |

**Proposed for removal because the red catches nothing.** They report main's state, so a red does not depend on the pull request.

| lane | share | red | evidence |
|---|---|---|---|
| `governance / delivery-status` | 0.7 % | 36 heads, 25 pull requests | reports the record's conclusion on main |
| `tests / nightly-status` | 0.4 % | 175 heads, 74 pull requests | reports the last nightly; `slow` was red on three of the last three schedules. A red must be answered in the body: this batch's predecessor was refused for it once. That cost is not counted |
| `tests / ci-ratchet` | 0.1 % | 52 of 55 failed pushes to main | the owner has ruled no pause on it (2026-11-04), so its red stops nothing |

**Not refuted, kept.**
- `tests / mutation-pins (1-7)`, 7.4 %, with `tests / mutation-autofix`: 18 `ci: pin killed` commits on main since 2026-10-29, 7.9 % of 228. Each spares a repair round but restarts CI, which is not netted out. This is the nearest case: the net could be under 5 %.

**Cost known, benefit not measurable from this data, so unmeasured and not passing.**

| lane | cost, 7 days | why |
|---|---|---|
| `merge-main.yml` | 244 runs, about 10.6 h | conflict repairs it spares were not counted |
| `gate-sweep.yml` | 2500 runs, about 19.7 h from 12 sampled | re-judges a stale red; false reds cleared were not counted. Close to the gate's safety |
| `record-autofix` (`nightly.yml` push) | 244 runs, about 4.4 h | a record beat, not a check: 46 `ci: record delivery` and 12 `ci: record nightly` commits are its output, not a measure |
| `governance / record`, `delivery-status-publish` | 0.2 % | same |
| `tests / closures-autofix` | under 0.1 % | 3 `ci: re` commits, 1.3 %; cheap, under the bar |
| `tests / claims-autofix` | under 0.1 % | no commit in the window |
| `dependabot-automerge.yml` | 822 runs, about 1.9 h | 1 dependabot pull request of 228; 397 of 400 listed runs skipped. Proposed for narrowing |
| `dependency-graph.yml`, `marketplace.yml`, `pages.yml` | under 0.1 h | negligible; no improvement figure exists for any of them |

**Could not be measured.** `kernel-points.yml`: 0 of 220 sampled runs executed it, so no cost. `tests.yml`, `governance.yml`, `codeql.yml` and the other called files have no runs of their own: they are priced as jobs of `ci.yml`. `probe.yml` and `probe-options-freeze.yml`: listed by the API, no runs.

**Separate, not ruled.** Required safety lanes: `gate` (1.2 %), `prelude` (11.8 %), `pr-contract` (0.4 %, 63 pull requests), `budget-raise-gate` (0.7 %, 4), `codeql` (15.6 %, no red), `hassfest` (0.4 %), `validate-hacs` (0.5 %), `closures` (9.8 %, 8) and `closure-scope` (0.6 %, 0), which keep the scoped gate honest, `refresh` and `cancel-superseded` (2.8 %), and `release.yml`. Production tests: `fast` (8.1 %, 18), `coverage` (9.1 %), `coverage-ratchet`, `browser` (1.7 %), `typing` (0.6 %, 2), `mutation` (2.9 %, 17), `replay` (1.1 %, 8), and `nightly.yml`'s `slow`, `nightly-ha`, `mutation-nightly` and `mutation-ledger`.
- **Worth the orchestrator's eye, not ruled:** the 16 scheduled and dispatched nightlies cost 176 h in 7 days, and a run rose from about 7 h to about 17 h on 2026-11-01. `prelude` holds a runner for 570 s a run, 11.8 %, partly waiting. `closures` is 9.8 % and sits under the 12 at its upper bound, so if the owner reads it as non-production it joins the first table.

**Limits of this reading.** A check is insurance, so eight days without a red is weak evidence against it. A lane too cheap to measure cannot show 5 % either. The orchestrator's reading, not the owner's, puts both in the candidate column.

Cost: removing the first two tables would free up to 25 % of sampled runner hours. Gate-listed lanes need `tools/ci/prelude.py`, the workflows and the ruleset's contract changed, all code-owned. Narrowing needs a measured scope, as `replay` already has (R10-REPLAY-SCOPED). No capped file is touched by this ruling.

Binding: no action. Each proposal goes to the owner through the orchestrator; a removal keeps its reason in the decision record. Do not route this as CI capacity: the owner ruled that out on 2026-11-01, and this is the cost-benefit ruling he asked for.

## P392: the triage seat

Verdict: DEFER. On the working reading the seat does not pass: its cost is measured and its benefit is not. This seat is ruling on itself, so the orchestrator should weigh this with that in mind.

Source: the owner's ruling above.

Instances:
- **Cost, strict match on seat prompts, 55 sessions from 2026-10-24 to 2026-11-04, against all local transcripts since 2026-10-01.**

  | | seat | share |
  |---|---|---|
  | output | 5.27 M | 8.6 % |
  | cache creation | 71.5 M | 12.0 % |
  | cache read | 1.92 G | 7.2 % |

  Reviews of triage pull requests add 0.50 M output and 0.16 G cache read. The two windows differ, and cloud seats are missing from both sides, so a share is approximate. This session alone: 0.31 M output and 36 M cache read for six rulings and their repairs.
- **What it produced.** 382 entries on the roster branch: 233 ACCEPT, 93 DEFER, 55 REJECT, 1 owner. 247 roster carries cite triage: 56 marked implemented, 58 moved, 5 dismissed, 57 on a closed group, 71 on an open group.
- **What is not measured.** No ruling has a before-and-after figure on any of the four measures. The ledger meant to record a proven improvement over 10 %, `exemptions` in `dev/governance/config/machinery_budgets.json`, is empty. The cost a REJECT or DEFER avoided is an estimate, never a measurement. No week ran without the seat to compare.
- **This session's own record.** P389 was a proposal the instrument already answered, and the orchestrator withdrew it. P387's finding was real when filed, then answered by the fix. I made three errors, all corrected, that a seat with no such step would not have made.

Cost: removing the seat frees at most 7 to 12 % of local tokens, less whatever moves to the orchestrator; that is not measured either.

Binding: proposed, for the owner through the orchestrator, smallest first:
1. **From P391, apply the bar at the door.** A queue line with no measured figure gets a one-line DEFER, with no investigation. That needs no decision and is this seat's own change. It should cut tokens per ruling, and the ledger will show by how much.
2. **Measure before deciding:** one week of that form against the week before, on tokens per ruling and on blocked verdicts of the groups that received carries. Under 5 % on both, remove the seat.
3. **Or remove it now:** the orchestrator applies the one-line cost test itself and sends only what it cannot judge.

An owner directive keeps its route: P386 needed no cost test on whether, only on form.
