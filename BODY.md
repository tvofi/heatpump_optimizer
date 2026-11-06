Closes the R10-GATE-LEASE-TOCTOU free-slot race carried from PR 3170 (body item 42008ca4). `_free_slot` read a slot with `_read_at`, and on None looked again with `is_file()`; a rival that created the slot between the two reads was seen as present, and the unparseable-slot branch unlinked its fresh owner, so two takers held one slot. Now one `read_text` decides absent (`FileNotFoundError`, return the index; `Owner.create`'s hard-link arbitrates) against broken, and a broken slot is reaped through `_steal(path, None)`, which renames it aside and puts back any valid owner that landed meanwhile. The race is closed in production code; no test wait was widened.

Alternatives that lost: a lock around `_free_slot` (the pool takes no flock by design, only the single lease does); a retry loop on the test side (hides the race).

## Head

635bbc61854c49ca0f1488819cfa34be9dbf6b9e, merge base b88684a218923f85de66f1e8fb1833e31a76a154. origin/main had not moved since that base when the last `prepr.sh` ran, so no second run was owed.

## Mutation proof

The new acceptance case `delayed_read` fires a rival create right after the slot's missing read, the delay-only plant made exact. With the production hunk reverted to the merge base's `_read_at` / `is_file` / unlink form, three runs of `python3 tests/gate_lock.py --accept` each printed `FAIL concurrency control: a delay after a missing-slot read cannot let two waiters hold the slot [fired=True kept=None second_create=True]` and `1 of 42 ... FAILED`. Restored: three of three runs `ALL 42 gate lock acceptance checks PASSED`.

## Null control

The unmodified tree is the mutant above: the rival's slot is unlinked (`kept=None`) and a second create succeeds. A first plant that only slept 30 ms after the read and ran `one_winner` stayed green on the baseline in 3 of 3 runs, so it was replaced by the exact rival-create plant; the 8-of-10 figure in the brief is the prior review's, not re-measured here.

## Figures

- Mutation and fix runs: `python3 tests/gate_lock.py --accept` with `PYTHONPATH=tests/hastub`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED`, naming `tests/doc_claims.py` and `tests/entities.py`; `doc_claims.py` passed (`ALL 296 checks PASSED`).
- Structure: `python3 tests/structure.py` ended `STRUCTURE RATCHET PASSED`.
- Seam enumeration for the class "check a slot, then act on a second look": `grep -n "is_file" tests/gate_lock.py` after the fix returns only `_read_at`'s own use, which feeds single-owner reads (`read_owner`, `_slot_of`, `_held_slots`), none of which acts on a second look.

## Red checks

none

## Forward-carry

none

## Friction

none
