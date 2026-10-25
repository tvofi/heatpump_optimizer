# R10-FLOW-MQ-PROBE: merge queue refused on a User-owned repository

Refs #2715. Study group, no production change. It lands the probe record at
`dev/audit/rounds/round10/D13/mq-probe.md` and its raw API requests and
responses under `dev/audit/rounds/round10/D13/mq-probe/`.

## Head

`f1eb42a97522468208bb8eed76bfe9941400082d`, on base `dfcd8d9be` (`origin/main`, 2026-10-25T18:10Z).

## Summary

`POST repos/tvofi/heatpump_optimizer/rulesets` was sent with a schema-valid
`merge_queue` rule (MERGE, decision 0010). Its only target was
`refs/heads/probe/mq-r10`. The response was HTTP 422 `Invalid rule
'merge_queue': `. The repository's owner is a `User` account, and the queue
cannot be enabled here. No ruleset, probe branch, probe PR or queue entry was
created. The live arms (latency per entry, the 22 `gate_required` names on a
queue run, CI minutes per queue run, a passing and a red entry) cannot be
measured on this repository. They are not estimated.

Recommendation on each held group of carry [2]: **adopt**, because the queue
is infeasible and so makes none of them moot. The groups are
R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY, R10-FLY-CARRY-DOC-CONTEXT,
R10-TRAIN-OVERLAP-GRADE and R10-FLOW-BODY-ONLY (a). The reasoning for each is
in the record's table.

## Mutation proof

Not applicable: the diff is a measurement record and its evidence files. No
check or production line changes.

## Null control

- The refusal is specific to the rule type. A malformed `merge_queue` rule
  (`merge_method: BOGUS`, or missing `grouping_strategy`) and an unknown type
  `no_such_rule` each fail **schema** validation (`Invalid property /rules/0:
  data matches no possible input`). The well-formed rule, alone or beside
  `required_status_checks`, is refused **by name**. Had the parameters been
  the cause, 01 and 03a would read like 03b and 03d.
- Nothing was created. The ruleset list before the first POST and after the
  last one is `22628467 23698884 23937752` both times (`diff` empty). Each of
  the three has an unchanged `updated_at` (`mq-probe/12-ruleset-updated-at.txt`).
- The tests.yml guard simulation has both arms: a two-parent commit is
  accepted, and a one-parent commit is refused.

## Figures

| figure | command / source |
|---|---|
| owner type `User` | `gh api repos/tvofi/heatpump_optimizer --jq .owner.type` |
| 422 `Invalid rule 'merge_queue': ` (01, 03a); schema 422 (03b, 03c, 03d) | `gh api -X POST repos/tvofi/heatpump_optimizer/rulesets --input <body>`; bodies and responses in `mq-probe/01*`, `mq-probe/03*` |
| `mergeQueue(branch:"main")` = `null` | `gh api graphql`, `mq-probe/05-graphql-mergequeue.json` |
| prelude self-test 29 checks, 0 failed | `python3 -I tools/ci/prelude.py --self-test` |
| `merge_group` resolves to class `pr` (18 names) or `pr-cc` (19); the other fixture names are the push-only and arch-score splits, the same as `pull_request` | `gate.REQUIRED[gate.event_class(ev, "12", cc)]` against `tools/policy/fixtures/required-contexts.json`, `mq-probe/07-*` |
| no required job's `if:` names `pull_request` without `merge_group`; `tests / fast (3.14)` unresolved by the name match | `mq-probe/08-job-if-census.txt` |
| train batch runs 83.2 and 93.6 job-min; PR code runs 39.8 to 214.4 | sum of `completed_at - started_at` over `/actions/runs/<id>/jobs`, negative durations excluded and counted, `mq-probe/11-ci-minutes.tsv` |
| scoped gate | `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run` |

## Red checks

None known at handoff.

## Forward-carry

n/a: carry [2] names the orchestrator's roster edit as the release of the five held groups. That edit cites `dev/audit/rounds/round10/D13/mq-probe.md` once this is on main. No other stage's brief changes.

## Friction

none
