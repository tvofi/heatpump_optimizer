Fix review: merge ec8b7300e74f082ce236604d4fe8ff3294e7f69b

bus-nonce: 885d0efce37d5a0d3aaee0c552b84705

Round 2 (delta over reviewed head 2469c52668c90af0c143b6905c9ee6e25e140add).

## Previous findings

- Block (class-open, `draw/engaged` cell-only cost unguarded): resolved. Arm 6's cost probe now covers every non-key field. A cell-only field that costs another leaf is refused unless `_A6_CELL_SPENT` records it. I re-applied the round-1 mutant M5b (`ev/m5b.diff`) at the head: `tests/finite_boundary.py` gives rc 1, `1 of 118 FINITE BOUNDARY CHECKS FAILED`, `CELL accuracy:accuracy/draw/engaged costs 16 other leaves, declared cell-only (recorded 0)` (`ev/m5b_finite_boundary.txt`). In round 1 the same mutant passed all 116.
- Note: figure `draw/config/#`: the body now says 17, and the head prints `COST accuracy:accuracy/draw/config/# 17 other leaves (whole)`. Resolved.
- Note: figure `duty_switch`: the body now says 5 or 6, taken from the in-tree `COST` lines. Resolved, and the `/tmp` figures are dropped.

## Evidence

- Scope: the delta `git diff 2469c526 ec8b7300` touches only `tests/finite_boundary.py` (+155 / -7). It has no `custom_components/` delta, so nothing widens the review (step 12). The head is the live PR head and the body's head line. `ev/HEAD.txt` names it.
- Merge: `git merge-tree --write-tree origin/main ec8b7300` exits 0. The head is 76 commits behind origin/main and merges cleanly. The role pack was rendered from origin/main.
- CI: `merge_train.py classify ec8b7300e74f082ce236604d4fe8ff3294e7f69b --pr 3714` printed `GREEN ec8b7300e74f082ce236604d4fe8ff3294e7f69b pending: none red: none`, rc 0 (`ev/classify.log`). `tests / nightly-status` is a failure, but it is not in `owed-reds`, so it needs no answer.
- Head run (`ev/head_finite_boundary.txt`): `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` gives `ALL 118 FINITE BOUNDARY CHECKS PASSED` rc 0. It also prints `domain_whole_fields=33`, `domain_whole_unused=0`, `domain_cell_fields=232`, `domain_cell_spent=86` and `domain_cell_refused=0`. Every one matches the body. `_A6_CELL_SPENT` has 86 entries, counted by parsing the literal, which matches `domain_cell_spent`.
- My own mutant L1 (`ev/l1.diff`) deletes the `draw/idle/#` entry from the table: rc 1, `1 of 118 FINITE BOUNDARY CHECKS FAILED`, `CELL accuracy:accuracy/draw/idle/# costs 1 other leaves, declared cell-only (recorded 0)` (`ev/l1_finite_boundary.txt`). This matches the body's L1. I did not re-run the body's other mutants (M1, M2', M3', L2, L3, L4). Their figures are the fixer's.
- The table is a ratchet: a listed field may cost up to its recorded number of other leaves. A regression inside a recorded cost is not caught. That limit is the body's stated disposition, and the 86 fields are carried by the body to R11-INTAKE-R10-RESIDUE.
- Not re-derived: carry 3's tail-arm counts (4/0, 9/0, 9/9). Nothing for carry 3 is built here.
- I did not re-run the gate, the mutation table, `structure.py` or archscore. CI's `gate`, `tests / mutation` and `arch-score` are success at this head.
- Finder's harness: the packet names none. The instrument is the fixer's in-tree Arm 6, so it is the fixer's harness, not a finder's.
- Self-audit: `carry_audit.py check` was run over this verdict as the comment, with an empty body file. It gave rc 0 and `0 finding item(s)` (`ev/carry_audit.txt`). The packet's own run over the PR body at the head reported 5 routed, 0 unrouted.
