`merge_train.py batch --overlap` re-carries every serial entry onto the batch's start base and lands them later in queue order, so the batch's own merges move the base under a car that has not merged yet. `at_head`'s guard only asks that the recarry base stay an ancestor of `origin/main`, which any forward move satisfies, and the ruleset is non-strict (`strict_required_status_checks_policy: false`, ruleset 23698884), so a car could land on a merge tree no CI had ever read. #2586 did: the third instance of this class after `6077bf70e` and `143e2d0ac` (process state (c)), and the group's cost test -- the brief's, not re-measured here -- is at least 1.5 h of red `main` per instance, roughly weekly.

This PR adds that grade. Before a car lands on a base the batch's own merges moved, `Train.grade_merge` builds the merge GitHub would make with the train's driver-free text merge (`Train.merge_tree` -> `text_merge`; never the ledger's driver), materialises it as a throwaway worktree, and reads it with `policy_lint` always -- it reads the whole corpus, so no car's own diff can be trusted to have covered it -- and `tests/structure.py` where the gate's own closure table (`tests/closures.json`, read at the merge tree) selects it for what the merge changes. A red is HELD, not merged: the existing `MAIN-MOVED` recarry-and-wait path re-carries the car and CI judges the new head, and a recarry that reproduces the same red tree is a `Stop`, so a recarry cannot launder a graded red back into a merge. A car whose base did not move is graded never: its merge is a fast-forward and `tree(head)` is exactly what its CI read.

Repair cars keep their path, structurally rather than by a flag: the grade fires only when the batch itself moved the car's base, which a one-car batch cannot do, so `--overlap` admitting one car onto a red `main` -- the #2595 repair shape -- merges ungraded. Multi-car overlap on a red `main` was not narrowed here: that is P7's log-only ruling, and this PR is the in-tool barrier for the owner's 2026-10-22T05:20Z rule -- trains run with `--overlap` while each PR's CI has run on its current head -- not a change to it.

The grade's cache is keyed on the two things its verdict is a function of -- the merge tree it read, and whether the gate's selection reached the ratchet for it -- so a second encounter with one tree costs no checks, and a car that meets a tree some other car was graded on under a *narrower* selection is graded, never handed that car's green.

`tools/audit/seat/INSTRUMENTS.md` gains the instrument's entry: what `Train.grade_merge` grades, with which checks, how a red is held, and that a one-car repair batch never fires it.

The prototype the brief names (the ratchet-on-merge script in the semmerge RCA seat directory) is not in the tree and its path was not handed to this seat: `git grep -n -i semmerge` returns only `dev/programme/rosters/wave-r10-groups.json`, which names it as outside the tree. The grade was implemented from the brief, and the brief's next paragraph is why the merge is built driver-free: `merge-tree` mirrors GitHub, which runs no merge drivers, so a cloned ledger or claimnotes driver must not decide what the graded tree is. The self-test pins that with a car whose clone-configured ledger driver would have resolved a conflict silently; it is reported as a conflict and re-carried instead.

Part of #2725.

## Head

`e679ed34fb5057b99f88b8ac7334ccf180014e48`

## Mutation proof

Three mutations of the production predicate in `tools/audit/seat/merge_train.py`, each graded by `python3 tools/audit/seat/merge_train.py --self-test`, and restored afterwards:

- M1 -- `grade_merge` returns before its first fetch, so no car is ever graded (the barrier's entry): 5 arms red -- `THE OVERLAP GRADE, arm 1`, `... the red arm read the MERGE tree`, `... builds GitHub's merge with git's TEXT merge`, `... arm 2 (the unmodified green car)`, and `... runs structure.py where the gate's own closure selects it`. The null control and the repair-car arms stay green, which is what they assert: nothing is graded.
- M2 -- `merge_tree` drops `text_merge` and lets the clone's configured drivers run: the arm `THE OVERLAP GRADE builds GitHub's merge with git's TEXT merge, never the clone's ledger driver` is red.
- M3 -- the second encounter with an already-held red tree re-carries instead of stopping: the arm `THE OVERLAP GRADE, arm 1: a serial car whose base the batch's own merges moved is graded before it lands, and a red one is HELD -- never merged -- and re-carried` is red.

Restored, the same command prints `merge_train self-test: 327 checks, 0 failed`.

## Null control

- The unmodified head is the defect: with the grade removed (M1 above) the same red car merges, and the arms above are the arms that fail. So each arm passes at this head only because the grade ran.
- The grade's own null control, in the tree: a one-car batch whose base never moved is graded zero times (`THE OVERLAP GRADE's null control` arm). Had the grade taxed every merge, that arm's `not w.get("grades")` would be red.
- The real checks, both arms, at this head: the two-arm demo builds each merge tree with `Train.merge_tree` and grades it with `Train.grade_tree`. Green arm: `grade policy_lint 91325e70: ok (67s)`, `grade structure.py 91325e70: ok (85s)`, `GRADE: GREEN`. Red arm (the same base moved by the batch's own merge, a car that lowers a ratchet budget): `grade policy_lint 16421daa: ok (76s)`, `grade structure.py 16421daa: RED (61s) FAIL methods_over_200 9 > 0 (+9)`, `GRADE: ['structure.py (FAIL methods_over_200 9 > 0 (+9))']`. The red arm is a genuine red the stubbed arms cannot fake, and the green arm is the same instrument reading the same way when nothing is wrong.

## Figures

- `merge_train self-test: 327 checks, 0 failed` -- `python3 tools/audit/seat/merge_train.py --self-test`
- `STRUCTURE RATCHET PASSED`, every metric at its budget -- `python3 tests/structure.py`
- `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script `tests/entities.py` -- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`. The RUN itself did not happen: it waited on a heavy gate slot while all four were pinned by the prepr wedge, and it was ordered aborted at 2026-10-27T12:19:58Z to free the gate lease, so CI's `gate` carries `tests/entities.py` for this head and this body claims no gate run it did not make
- the cost of one graded car, measured by the two arms above at this head: `policy_lint` 67 s and 76 s, `structure.py` 61 s and 85 s on this seat under load -- the instrument is the train's own `grade <name> <tree>: ok|RED (<Ns>)` log line, and its null control is the car whose base did not move, which prints no such line at all; the roster's cost test counts ~16 s per merge for the same check, so read these as an upper bound
- `semmerge` has exactly one hit in the tree and it is the roster line naming the prototype as outside it -- `git grep -n -i semmerge`

## Red checks

none

## Forward-carry

none

## Friction

none
