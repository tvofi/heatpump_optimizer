# R10-FLOW-MQ-PROBE: merge queue refused on a User-owned repository

Refs #2715. Study group, no production change. It lands the probe record at
`dev/audit/rounds/round10/D13/mq-probe.md` and its raw API requests and
responses under `dev/audit/rounds/round10/D13/mq-probe/`.

## Head

`a03b799bff2f5a80438db44805dc471bf45810ac`. Linear history, no merge commit: `a03b799bf` (round 2, the record edit)
has parent `754ab29f7` (this PR's own delivery row), whose parent is
`f1eb42a97` (round-1 code), whose parent is `dfcd8d9be` (`origin/main` when the
probe was taken, 2026-10-25T18:10Z). `git merge-tree --write-tree origin/main
HEAD` against `origin/main` `c9cbe6b45` reports no conflict, so main was not
merged in.

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
in the record's table. Three of the five carry an `after` edge on this group
(R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY, R10-FLY-CARRY-DOC-CONTEXT), so
the release edit removes three edges; R10-TRAIN-OVERLAP-GRADE is already
released (`after: []`) and R10-FLOW-BODY-ONLY (a) is held by carry text only.

**Open blocker, round 2: the positive control was not taken.** The brief's
round-2 scope was one POST of `01`'s body minus `merge_queue` on
`refs/heads/probe/mq-r10`, then DELETE, a 404 read-back and a rulesets list.
This seat's first write call (the re-POST of `01`, before the control) was
refused by the seat's own tool-permission layer ("Modify Shared Resources")
before any request was sent. The brief forbids working around a refusal, so
no POST, DELETE or ruleset write happened in round 2, and the round-1 block
(`control-missing`) still stands. The control needs a seat whose harness
permits a ruleset write under tvofi's grant. The record states this in
"Positive control: not taken (open)".

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
- **Positive control: missing.** No accepted POST of the payload minus
  `merge_queue` exists, so the 422 is not yet shown to be the `merge_queue`
  rule's alone (see the open blocker above).
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
| `mergeQueue(branch:"main")` = `null`; corroborates only the owner type, since it is `null` on any repo with no queue configured | `gh api graphql`, `mq-probe/05-graphql-mergequeue.json` |
| payload minus `merge_queue` accepted (201 + id), DELETE, GET 404, list of 3 ids | **not taken**: the seat's write call was refused before sending |
| release edges: three groups' `after` name R10-FLOW-MQ-PROBE; R10-TRAIN-OVERLAP-GRADE `after: []`; R10-FLOW-BODY-ONLY `after` = [R10-UPDATE-PR-SIGNALS, R10-FLOW-BODY-PATCH] | `git show origin/main:dev/programme/rosters/wave-r10-groups.json`, groups' `after` read with a walk over every object carrying `after`, at `origin/main` `c9cbe6b45` |
| prelude self-test 29 checks, 0 failed | `python3 -I tools/ci/prelude.py --self-test` |
| `merge_group` resolves to class `pr` (18 names) or `pr-cc` (19); the other fixture names are the push-only and arch-score splits, the same as `pull_request` | `gate.REQUIRED[gate.event_class(ev, "12", cc)]` against `tools/policy/fixtures/required-contexts.json`, `mq-probe/07-*` |
| no required job's `if:` names `pull_request` without `merge_group`; `tests / fast (3.14)` unresolved by the name match | `mq-probe/08-job-if-census.txt` |
| train batch runs 83.2 and 93.6 job-min; PR code runs 39.8 to 214.4 | sum of `completed_at - started_at` over `/actions/runs/<id>/jobs`, negative durations excluded and counted, `mq-probe/11-ci-minutes.tsv` |
| scoped gate | `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run` |

## Red checks

None known at handoff.

## Forward-carry

- The round-1 PR body's `## Head` paragraph was written by
  `tools/audit/seat/update_pr.sh` (its `head_note.prefix` call), not by this
  body. It says "merges origin/main `<M>`" whenever it runs `git merge
  origin/main`, including when that merge is a no-op (here `754ab29f7` has the
  single parent `f1eb42a97`). This body's `## Head` states the real chain.
  Carry: R10-UPDATE-PR-SIGNALS
- The positive control could not be taken from a cloud seat whose tool layer
  refuses ruleset writes (open blocker above); it needs a seat permitted to
  write the probe ruleset under tvofi's grant. Carry: R10-FLOW-MQ-PROBE

- Carry [2] names the orchestrator's roster edit as the release of the held
  groups: it removes three `after` edges (R10-FLOW-RECORD-PITCH,
  R10-FLY-ROW-HEAD-CARRY, R10-FLY-CARRY-DOC-CONTEXT), records
  R10-TRAIN-OVERLAP-GRADE as already released, and cites
  `dev/audit/rounds/round10/D13/mq-probe.md` once this is on main.
  Carry: R10-FLOW-MQ-PROBE

## Friction

none
