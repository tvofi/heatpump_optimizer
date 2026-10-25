# R10-FLOW-MQ-PROBE: GitHub's merge queue is not available to this repository

Lean flow study K9 asked for a probe of GitHub's merge queue on a throwaway
branch under a throwaway ruleset (merge method MERGE, decision 0010). Carry [2]
of the roster group asks for an adopt-or-decline recommendation on each held
group. This file is the measurement record. The raw requests and responses are
in `mq-probe/` beside it.

Taken 2026-10-25T18:10Z against `origin/main` at `dfcd8d9be`. Every API call
was made by `tvofi` under the owner's grant for this probe ("Local seat, I
grant it", 2026-10-25). The grant covers one ruleset scoped to a probe branch,
one probe PR, and the ruleset's deletion.

## Result

**The repository cannot hold a `merge_queue` rule.** The owner is a `User`
account (`gh api repos/tvofi/heatpump_optimizer --jq .owner.type`). A
schema-valid ruleset whose only target is `refs/heads/probe/mq-r10` was
refused:

    POST repos/tvofi/heatpump_optimizer/rulesets   (mq-probe/01-ruleset-post.body.json)
    -> HTTP 422 {"message":"Validation Failed","errors":["Invalid rule 'merge_queue': "]}

So no ruleset was created. No probe branch, probe PR or queue entry was made,
because nothing could be enqueued. The live arms the brief names (latency per
entry, the 22 `gate_required` names on a queue run, CI minutes per queue run,
and a passing and a red queue entry) **cannot be measured on this repository**.
They are not estimated here.

### The refusal is about the rule type, not the request (control)

The same endpoint was given four more bodies (`mq-probe/03*`). Each was refused,
so none created anything.

| body | response |
|---|---|
| 01: `merge_queue` + `required_status_checks` (`gate`) | 422 `Invalid rule 'merge_queue': ` |
| 03a: `merge_queue` alone, same parameters | 422 `Invalid rule 'merge_queue': ` |
| 03b: `merge_queue` with `merge_method: BOGUS` | 422 `Invalid property /rules/0: data matches no possible input` |
| 03c: an unknown rule type `no_such_rule` | 422 `Invalid property /rules/0: data matches no possible input` |
| 03d: `merge_queue` missing `grouping_strategy` | 422 `Invalid property /rules/0: data matches no possible input` |

A malformed `merge_queue` rule (03b, 03d) and an unknown type (03c) fail
**schema** validation. The well-formed rule (01, 03a) passes the schema and is
refused **by name**, with an empty reason. That is the response the API gives
for a rule type the repository cannot use. It is not a parameter error: had
the parameters been wrong, 01 would have read like 03b or 03d. The GraphQL read
agrees: `repository.mergeQueue(branch:"main")` is `null` on a `User` owner
(`mq-probe/05-graphql-mergequeue.json`). This record does not quote GitHub's
published availability rule (organization-owned repositories), because the
documentation fetch did not return it. The attribution to the owner type is
inference from the refusal, with no wording from GitHub behind it.

### Nothing was created, so nothing was left behind (read-back)

`GET repos/tvofi/heatpump_optimizer/rulesets` returned ids
`22628467 23698884 23937752` before the first POST
(`mq-probe/00-rulesets-before.tsv`) and the same three after the last POST
(`mq-probe/04-rulesets-after.tsv`). `diff` of the two lists is empty. The
refused POSTs returned no id, so there is no ruleset to DELETE and no GET to
read back as 404. `main-protect` and `main-protect-checks` were read but never
written. Each of the three has the same `updated_at` before and after
(`mq-probe/12-ruleset-updated-at.txt`). No branch or PR was created, so there is nothing to delete or close.

## What the tree does on `merge_group` (offline, not a queue run)

These runs check the tree's own code against a synthetic queue event. They show
that the dormant K9 wiring is internally consistent. They are **not** a
substitute for a live queue run, which this repository cannot produce.

- `python3 -I tools/ci/prelude.py --self-test`: 29 checks, 0 failed. This
  includes the queue-ref arm. `derive` on a queue ref for the non-main base
  `probe/mq-r10` returns `('code', '12', 'probe/mq-r10')` with all eight units
  in `workset` (`mq-probe/07-gate-required-merge_group.txt`).
- `gate.REQUIRED` on `merge_group` resolves to the same event class as on
  `pull_request`: `pr` (18 names) or `pr-cc` (19 names). The other 4 of the
  fixture's 22 are the 3 push-only `tests` jobs, plus `arch-score` when the
  diff does not reach `custom_components/`. That is the same split a pull
  request gets (`mq-probe/07-...`).
- Job `if:` census over the unit files for every name above
  (`mq-probe/08-job-if-census.txt`). No job's condition names `pull_request`
  without also naming `merge_group`. `tests / fast (3.14)` is a matrix name
  that this census's name match does not resolve, so it is unchecked.
- `tests.yml`'s golden-ref guard and `pr-contract.yml`'s queue-ref parse were
  re-run on a scratch repository (`mq-probe/09-guard-and-queue-ref-sim.txt`).
  A two-parent (MERGE) commit is accepted, with `CLAIM_HEAD` equal to the PR
  head. A one-parent (squash) commit is refused: "no second parent". The jq
  capture yields `2715` and `12` for well-formed queue refs, including one on
  a non-main base. It yields an empty number for a malformed ref, which the
  next `gh api pulls/<n>` then fails closed on.

## CI minutes, for context only

These are job minutes summed over `/actions/runs/<id>/jobs` (completed minus
started, with negative-duration skipped jobs excluded and counted;
`mq-probe/11-ci-minutes.tsv`). The two most recent train batch dispatch runs
took 83.2 and 93.6 job-minutes. Four recent successful pull-request code runs
took 39.8 to 214.4. A queue would have run one code run per entry where the
train runs one batch run per train. That comparison is moot while the queue
cannot exist.

## Recommendations on carry [2]'s held groups

All five depend on one fact: **the queue cannot replace any of them on this
repository.** Every one is **adopt** (build as briefed), and the queue is
**declined** as infeasible:

| group | recommendation | why |
|---|---|---|
| R10-FLOW-RECORD-PITCH | adopt | Record merges keep moving main under every open head, and only a pitch bound reduces that. A queue would have absorbed the moves, but there is none. |
| R10-FLY-ROW-HEAD-CARRY | adopt | Row-only second pushes re-run full CI on an unchanged code diff. A queue does not touch pull-request-head runs in any case. |
| R10-FLY-CARRY-DOC-CONTEXT | adopt | `app_approve.sh --carry` still has to accept main-introduced `.md` context lines, because heads keep absorbing main. |
| R10-TRAIN-OVERLAP-GRADE | adopt | `merge_train.py --overlap` stays the batching path, and the non-strict ruleset still lets a batch merge onto an untested tree. A queue would have tested the merged tree. Without one, the in-tool grade is the barrier the third instance owes. |
| R10-FLOW-BODY-ONLY (a) | adopt | Merging main only when DIRTY or conflicting is the remaining lever against head-moved re-reviews. The queue's alternative (test the merge, leave the head) is unavailable. |

The one route that reopens the question is moving the repository to an
organization account. That decision is the owner's, and this probe does not
recommend it: it would move the HACS URL, every App installation, the deploy
key and the ruleset ids, so it is not a round-10 flow change. If it is ever
taken, re-run this probe as briefed. The `merge_group` wiring in `ci.yml`,
`tests.yml` and `pr-contract.yml` is dormant until then, and costs nothing:
the event never fires.
