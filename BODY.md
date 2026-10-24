Gate-lease slot pool admitted two holders when a rival read an owner file mid-write: `Owner.create` (O_EXCL then write) and `Owner.write` (truncate then write) leave an empty file, `_free_slot` unlinks an unparseable slot. Seen as `tests / fast` FAIL `concurrency control: two waiters released in one poll` (`overlaps=1`), 3 reds in 2.4 days. RCA: `dev/audit/rca/R10-RCA-GATE-LEASE-FLAKE.md`, state (c).

## Head

fab4a07c15ae167d221d8708f5cc75a1c2f4938f

## Mutation proof

`python tests/gate_lock.py --accept` (venv-ha python 3.14): with `Owner.create` reverted, `FAIL concurrency control: a rival taking while a slot is being created cannot also hold it [winners=['rival', 'a']]`, 1 of 30 FAILED; with `Owner.write` reverted, `FAIL ... a slot being renewed is never read as empty by a waiter [torn reads=3745 of 4000 rewrites]` (three runs: 3745, 6067, 5300), 1 of 31 FAILED.

## Null control

Fixed tree: `ALL 31 gate lock acceptance checks PASSED`, three runs. The existing `one_winner` and the 28 other cases are unchanged and pass.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
