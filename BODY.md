This is the root-cause record for the recurring-friction key `claim-false`
(#2907), plus the one countermeasure its cost test passes: a sentence in the
proposal-triage contract. The rest is the record and its evidence. It changes
no production code and moves no budget.

Disposes #2907. The roster group lists 2907 under `issues` with `fixes: []`, so `pr-contract`'s intended list refuses a closing keyword here. Closing #2907 on merge needs the orchestrator to move 2907 into the group's `fixes`.

The record is `dev/audit/rca/R10-RCA-FRICTION-CLAIM-FALSE.md`, with
`dev/audit/rca/claim-false/{items.tsv,stats_v7.0.5.txt}`, and it is indexed as
`_rca` `R10-RCA-FRICTION-CLAIM-FALSE` in `dev/audit/config/bugclasses.json`.

- **Count.** 4 PRs / 8 entries (#2883, #2890, #2891, #2900), re-derived.
- **Items.** The 8 verdicts hold 18 blocking items, sorted by author path in
  `items.tsv`.
- **Typed citations.** Ids and line numbers typed from memory make up 7 of the
  12 items in the three triage PRs. That is the brief's hypothesis, and it holds
  only inside triage: across the whole key it is 7 of 18. Two of those 7 are
  V-ids, which P219 has already closed (0 of the 52 headings in batches 45-59
  carry one). The other 5 never caused a round on their own.
- **What cost rounds.** Three verdicts blocked on a single item each, and each
  item was either a triage ruling whose rule never ran on its own instance
  (#2900, twice) or a `Cost:` that read no cap (#2891's second). That is
  3 rounds and 287 min, measured from block to next verdict. The process state
  is **(a)**: the contract required instances to be cited and the cost to be an
  estimate, but never asked for the rule to be run or a cap to be read.
- **Countermeasure, landed.** In `proposal-triage.md`: "An ACCEPT runs its rule
  on each instance, result beside it", and `Cost:` carries "each capped file's
  `--budgets` row". It is paid inside the file's own cap.
- **Refused.** A citation-resolving lint over triage batches and bodies. At most
  1 round would have been saved in the window, and the one carried error
  (`456/464`) is a single occurrence seen twice.
- **#2883.** Its 6 items are the `class-open` residue under #2784's standing
  refusal, plus a red check that already has its own record
  (`R10-RCA-CLOSURE-ARGV`).

## Approval

`dev/governance/roles/proposal-triage.md` is a policy file. Its edit is the
countermeasure this root-cause seat was dispatched to land. The dispatch
brief approves it under the orchestrator's mandate in force (scope `all`):
"A countermeasure that edits a policy file is approved under the
orchestrator's mandate (scope all)." The edit changes what a triage seat must
do: an ACCEPT now runs its rule on each counted instance, and `Cost:` reads the
cap of each capped file it grows. It addresses process state (a). No budget
file moves, so `budget-raise-gate` does not apply.

## Head

The code head is `1f961669846ff860ed578d3e557d9ec19a8528bb` on `handoff/r10-friction-claim-false`, one commit
on merge base `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`. That base was
`origin/main` when every figure below was measured (2026-10-29).

## Mutation proof

n/a: no check, test or production line changes. The diff is a record, two
evidence files, one register entry and one contract sentence. The contract
sentence is an instruction, not a check, so `defect-root-cause.md`'s
fail-then-pass demonstration does not apply. Its instances are the three
verdicts in the record's section 2.

## Null control

- The contract edit is paid inside its cap rather than with a raise.
  `node tools/policy/policy_lint.mjs --budgets` prints
  `dev/governance/roles/proposal-triage.md 36 36 489 489` at both the base and
  the head, rc=0. The cap is `round(bytes/4)`: the base is 1956 bytes and the
  head is 1956 bytes. An earlier draft of the same sentence printed `494 489`,
  so the row does move under an edit to this file.
- P219 held. `git grep -cE '^## P[0-9]+:.*\(V[0-9]+\)'` finds 0 matches in
  `dev/programme/triage/s6-batch4[5-9].md` and `s6-batch5*.md`, which hold
  52 headings between them. The control is batches 35-43: 13 headings still
  carry an id there, so the pattern does match where ids exist.
- The typed-citation items re-derive as false at the base. The two `def`s sit
  at `tools/audit/seat/roster_edit.py:455` and `:466`, not 456 and 464.
  `git log --all -S conflicting_claims_message -- tests/env_drift.py` finds
  0 commits, and the function at 1844 is `merge_claim_refusal`.

## Figures

All figures were taken at `88c6ad5bb`.

- `node tools/policy/policy_lint.mjs --stats --since v7.0.5`: rc=0 in
  2 min 7 s. It prints `4 / 8 claim-false <- at or over threshold`, the
  `would open "[policy] recurring friction: claim-false"` line, and
  `55 of 59 merged pull request(s) ... carried a parsable verdict`. Its
  `STATS COVERAGE BY CLASS` line counts `triage 0 of 5`, which is 5 triage PRs.
  The output is in `dev/audit/rca/claim-false/stats_v7.0.5.txt`.
- Minutes from each blocked verdict to the same PR's next `Fix review:` comment
  (`gh api repos/tvofi/heatpump_optimizer/issues/<pr>/comments`, `created_at`):
  - #2883: 268, 308
  - #2890: 23, 298
  - #2891: 308, 62
  - #2900: 51, 174

  The sum is 1492 min and the median 221 min. The three single-item R/C
  rounds are 62 + 51 + 174 = 287 min.
- Blocking items by path (`awk -F'\t' '!/^#/ && $1!="pr" {print $5}'
  dev/audit/rca/claim-false/items.tsv | sort | uniq -c`): F 5, T 5, V 2, O 2,
  R 2, C 1, B 1, a total of 18. With #2883 excluded: T 5, V 2, O 2, R 2, C 1,
  a total of 12.
- `node tools/policy/policy_lint.mjs --budgets` at the base prints
  `CLAUDE.md 213 221 3605 3605 yes`, which is #2891's C item.
- `tools/ci/gate.py:224` reads `f"FAIL {why[0]}"` and `:295` reads
  `"\n".join([outcome] + why[1:])`. This is #2900's R item, re-derived from
  source. The job log itself was not re-read: the log's blob host is outside
  this seat's network policy. The job's API metadata reads `gate failure
  2026-10-27T23:10:21Z run=40596083060`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names
  `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3.13 tests/entities.py` (venv with `tests/requirements-ci.txt`): `ALL 2470 ENTITY CHECKS PASSED`, rc=0
- `python3 -I tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/fold_ledger.py check`: `130 rca entries`,
  `0 violation(s)`.

## Red checks

None at this head before handoff. This seat has not seen CI on it.

## Forward-carry

- **The triage contract sentence** lands in this PR, in
  `dev/governance/roles/proposal-triage.md`, which is the contract the triage
  seat opens. No other stage's brief changes.
  Carry: dismissed: landed in this pull request's own contract edit
- **`claim-false` is an untaught class word.** `VERDICT_CLASSES` teaches
  `claims`, which is the golden-claim class. The derived `other (untaught)`
  family drafted for #2436 would also fold it. Carry: dismissed: #2436 has no live owner and this key already reached its threshold under its own spelling

## Friction

- `policy_lint.mjs`: cost: the job log behind #2900's instance sits on a blob
  host this seat's network policy refuses, so the R items were re-derived from
  `gate.py` source and job metadata, not from the log. Carry: dismissed: environment network policy, not repository tooling
