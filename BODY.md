Root-cause record for the class #3735's `## Red checks` handed on: a `tests/structure_budgets.json` key only the branch measures (`module_excess_loc`) is carried unchanged by the `ledgermerge` driver across every merge of main while main's code moves the quantity. Six `tests / fast (3.14)` reds on #3735, read from the jobs' logs, each main's growth (`branch_delta=+0`). Process state (d). Record text only: `dev/audit/rca/R11-RCA-BOTMERGE-ROW.md`, and in `dev/audit/config/bugclasses.json` the six breaches as non-round instances of `N-postreview-merge-red`, this RCA in its `rca` list and an `_rca` index entry. The countermeasure, an amendment of R11-PRE-SHARED-FILES parts 2 and 3, is proposal P-R11-BOTMERGE-ROW for the round-end instrument triage, not a carry: the tooling freeze leaves every instrument unchanged, and that group's roster stage is `carries-open`, which receives none.

## Head

`2fce0edfe45fb0f8fc554e4341e74cb334bd05c2` on `origin/main` `726e5bbc32`.

## Mutation proof

n/a: no code, check or test changes; `python3 tools/audit/fold_ledger.py check` reads the ledger edit: `0 violation(s)`, and before the `_rca` entry was added it printed `UNKNOWN-RCA: N-postreview-merge-red cites R11-RCA-BOTMERGE-ROW, which _rca does not index`.

## Null control

At `origin/main` `726e5bbc32` `fold_ledger.py check` prints `0 violation(s)` over 180 rca entries; at the head, 181. The record's overlay demonstration (section 7) carries its own null control.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
