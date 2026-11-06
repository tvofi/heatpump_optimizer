# Proposal triage, session s12, batch 126 (P391, P392): the existing set under the 5 % and 10 % rules

**The bar.** Owner, relayed by the orchestrator: "the non production CIs and the triage seat should fulfil the cost benefit analysis, the "5 percent rule" for existing ones and 10 percent rule for new ones". Working reading, the orchestrator's: a measured improvement in CI time, programme completion time, right-first-time or token usage, each figure with its command. New: over 10 %. Existing: at least 5 %, or a candidate for removal. Unmeasured does not pass. It applies to every ruling from P391. Removing anything is a proposal to the orchestrator; nothing here is an action.

**Every figure is printed by one arm of `dev/audit/harnesses/r10_triage_p391.py` at `41c5e7bc82e2ce0ccf3baab58242c590c243fa95`, over a fixed window.** Run each from a checkout of that commit. Each REST read is cached on disk, and an arm waits rather than take the account's shared API budget under 2500.

| arm | command | prints |
|---|---|---|
| cost | `python3 -I dev/audit/harnesses/r10_triage_p391.py ci-cost 2026-11-04T22:06:00Z 2026-11-05T07:05:00Z cost.json` | 221 completed CI runs, 309.7 runner h, 84.1 min a run |
| benefit | `python3 -I dev/audit/harnesses/r10_triage_p391.py ci-fails 2026-10-28T00:00:00Z 2026-11-05T07:30:00Z fails.json` | 423 failed pull-request runs, 55 failed push runs, 262 pull requests merged over 232 branches |
| lanes | `python3 -I dev/audit/harnesses/r10_triage_p391.py report cost.json fails.json` | the per-lane table below; 5 % of 232 branches is 11.6 |
| nightly | `python3 -I dev/audit/harnesses/r10_triage_p391.py nightly 2026-10-29T00:00:00Z 2026-11-05T07:30:00Z` | 16 scheduled or dispatched runs, 176.2 runner h; 244 push runs, 3.8 h |
| git | `python3 -I dev/audit/harnesses/r10_triage_p391.py git 9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6 2026-10-29T00:00:00Z 2026-11-05T07:30:00Z` | commit counts by subject prefix; 229 merges on main's first parent |
| roster | `python3 -I dev/audit/harnesses/r10_triage_p391.py roster f85b3b4d56eed0b57f5b3b1f46471f8ae323113a` | verdicts, triage-cited carries, `exemptions` |
| tokens | `python3 -I dev/audit/harnesses/r10_triage_p391.py tokens 2026-10-01T00:00:00Z` | this host's transcripts only: **another seat cannot re-run it**, and a later run reads more sessions |

The cost window is 9 hours of runs, not a week, and a share counts waiting inside a job. "Caught" counts branches whose lane went red, then a later green run or a merge. A red within 12 h of the same lane red on main is left out. **"Caught" is an upper bound on right-first-time:** later green proves no defect, a scope change also clears a red, and no failure log was read. Branches, not pull requests, are the unit, because a record branch is reused across pull requests.

## P391: the non-production CI lanes

Verdict: DEFER. Twelve lanes fail the bar even at the upper bound, together 24 % of the sampled runner hours. What would change it: the owner's decision on each proposal below, or a measured benefit the lane's owner brings.

Source: the owner's ruling above, by the orchestrator's message after P390.

Instances, from the lanes arm unless named:

**Proposed for removal or narrowing: under 11.6 branches caught at the upper bound.** "Req" means `tools/ci/prelude.py` `UNITS` names it, so removing it changes the gate and its ruleset contract.

| lane | share | mean s | caught | req | proposal |
|---|---|---|---|---|---|
| `governance / instrument-self-tests` | 10.7 % | 1328 | 9 | no | run only on a diff reaching the instruments; 19 of its red runs sat within 12 h of its own red on main |
| `tests / arch-instrument` | 5.4 % | 779 | 0 | yes | run only on a diff reaching the score's own files |
| `governance / env-matrix` | 2.8 % | 346 | 1 | yes | remove or narrow |
| `governance / policy-docs` | 1.5 % | 192 | 2 | yes | narrow to policy paths |
| `arch-score / arch-score` | 0.9 % | 82 | 2 | when production is reached | keep only if the owner wants the score enforced |
| `governance / wave-script` | 0.8 % | 93 | 0 | yes | narrow |
| `tests / briefs` | 0.7 % | 89 | 1 | yes | narrow to roster and brief paths |
| `tests / graders-head-copy` | 0.3 % | 84 | 0 | no | remove or narrow |
| `tests / lane-proofs` | under 0.1 % | 6 | 0 | no | negligible either way |

**Proposed for removal because the red catches nothing.** These lanes report main's state, so their red does not depend on the pull request.

| lane | share | red | evidence |
|---|---|---|---|
| `governance / delivery-status` | 0.6 % | 29 branches | reports the record's conclusion on main |
| `tests / nightly-status` | 0.4 % | 81 branches | reports the last nightly; the nightly arm lists the last three scheduled runs as failures. A red must be answered in a body; the cost of that is not counted |
| `tests / ci-ratchet` | 0.1 % | 52 red pushes to main | the owner ruled no pause on it (2026-11-04), so its red stops nothing |

**Not refuted, kept.** `tests / mutation-pins (1-7)`, 9.0 %, with `tests / mutation-autofix`. The git arm counts 29 `ci: pin killed` commits, 12.5 % of 232 branches, though commits are not branches. Each spares a repair round but restarts CI, which is not netted out.

**Withdrawn: not re-derivable within budget.** These figures came from an earlier ad-hoc sample, not from the harness: `merge-main.yml` (10.6 h), `gate-sweep.yml` (19.7 h) and `dependabot-automerge.yml` (1.9 h). They are no longer claimed, and no proposal rests on them.

**Benefit not measurable here, so unmeasured and not passing:**
- `merge-main.yml`, `gate-sweep.yml` and `dependabot-automerge.yml`, as above.
- `record-autofix`: the nightly arm's push runs, 3.8 h. The git arm's 52 `ci: record delivery` and 13 `ci: record nightly` commits are its output, not a measure.
- `governance / record` and `delivery-status-publish` (0.2 %).
- `tests / closures-autofix` (7 `ci: re-record closures` commits) and `tests / claims-autofix` (0 `ci: drop inherited claims`).
- `dependency-graph.yml`, `marketplace.yml` and `pages.yml`: no improvement figure exists for any of them.

**Could not be measured:**
- `kernel-points.yml`: no sampled run executed it.
- `tests.yml`, `governance.yml`, `codeql.yml` and the other called files have no runs of their own; they are priced as jobs of `ci.yml`.
- `probe.yml` and `probe-options-freeze.yml`: listed by the API, with no runs.

**Separate, not ruled.**
- **Required safety lanes:** `gate` (1.1 %), `prelude` (11.9 %), `pr-contract` (0.4 %, 64 caught), `budget-raise-gate` (0.6 %, 4), `codeql` (15.4 %, no red), `hassfest` (0.4 %), `validate-hacs` (0.4 %), `refresh` and `cancel-superseded` (2.7 %), `release.yml`. Also `closures` (9.7 %, 10 caught) and `closure-scope` (0.6 %, 0), which keep the scoped gate honest.
- **Production tests:** `fast` (7.8 %, 22), `coverage` (9.0 %, 0), `coverage-ratchet`, `browser` (1.7 %, 0), `typing` (0.6 %, 2), `mutation` (3.0 %, 22), `replay` (1.2 %, 9), and `nightly.yml`'s `slow`, `nightly-ha`, `mutation-nightly` and `mutation-ledger`.
- **For the orchestrator's eye:** the 16 nightlies cost 176.2 h in 7 days, and a run rose from about 7 h to about 17 h on 2026-11-01 (nightly arm). `closures` sits under 11.6 at its upper bound; read as non-production, it would join the first table.

**Limits of this reading.** A check is insurance, so eight days without a red is weak evidence against it. A lane too cheap to measure cannot show 5 % either. The orchestrator's reading, not the owner's, puts both in the candidate column.

Cost: the first two tables free up to 24 % of sampled runner hours. Removing gate-listed lanes changes `tools/ci/prelude.py`, the workflows and the ruleset contract, all code-owned. Narrowing needs a measured scope, as `replay` already has (R10-REPLAY-SCOPED). No capped file is touched.

Binding: no action. Each proposal goes to the owner through the orchestrator. This is not a CI-capacity proposal, which the owner ruled out on 2026-11-01.

## P392: the triage seat

Verdict: DEFER. On the working reading the seat does not pass: its cost is measured and its benefit is not. This seat is ruling on itself, so the orchestrator should weigh the entry with that in mind.

Source: the owner's ruling above.

Instances:
- **Cost, from the tokens arm.** 55 seat sessions against all local transcripts since 2026-10-01. Not reproducible by another seat; the share moves as sessions are added.

  | | seat | share |
  |---|---|---|
  | output | 5.31 M | 8.5 % |
  | cache creation | 72.7 M | 11.7 % |
  | cache read | 1.93 G | 7.0 % |

  Reviews of triage pull requests add 0.50 M output and 0.16 G cache read. Cloud seats are in neither the seat's figures nor the total.
- **What it produced, from the roster arm.** 387 entries in 129 batch files: ACCEPT 235, DEFER 95, REJECT 56, OWNER 1. 247 roster carries cite triage: 60 implemented, 58 moved, 5 dismissed, 57 on a closed group, 67 on an open group.
- **What is not measured.** No ruling has a before-and-after figure on any of the four measures. `exemptions` in `dev/governance/config/machinery_budgets.json` is empty (roster arm). The cost a REJECT or DEFER avoided is an estimate, and no week ran without the seat.
- **This session's own record.** P389 was a proposal the instrument already answered, and the orchestrator withdrew it. P387's finding was real when filed, then answered by the fix. The seat made slips, all corrected: a wrong calibration re-check, a wrong note on a harness arm, body commits under the owner's name, a copy into another seat's temp directory, and figures carried out of the tree, which this repair cites.

Cost: removing the seat frees at most 7 to 12 % of local tokens, less whatever moves to the orchestrator; that is not measured either.

Binding: proposed, for the owner through the orchestrator, smallest first:
1. **Measure before deciding:** one week of the proposed one-line-DEFER form below (if the owner adopts it by policy pull request) against the week before, on tokens per ruling and on blocked verdicts of the groups that received carries. Under 5 % on both, remove the seat.
2. **Or remove it now:** the orchestrator applies the one-line cost test itself.

Proposal for `proposal-triage` (not adopted here): a queue line with no measured figure gets a one-line DEFER without investigation. It changes the ruling form that `dev/governance/roles/proposal-triage.md` requires, so it is policy; it needs the owner's approval and a policy pull request, and this record adopts nothing. Destination: `dev/governance/roles/proposal-triage.md` (the ruling form), if proposal-triage accepts it.

An owner directive keeps its route: P386 needed no cost test on whether, only on form.
