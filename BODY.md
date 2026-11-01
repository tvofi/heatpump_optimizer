Adds the roster's two missing field-writing ops, `set-size` and `set-files`, to `tools/audit/seat/roster_edit.py` (R10-ROSTER-OPS-2 part 1, issue #3131; owner tvofi approved plan-slip card 1, cap gate passed with `--over-cap "tvofi 2026-11-01 plan-slip card 1"`). Until now nothing could write a group's own `size`, `files` or `hot_files`, so the queued re-sizes of R10-FLY-STANDING-CONTRACTS and R10-ADVISOR-WHATIF and the held `set-files R10-ARCH-SHAPES-CLASSIFIER --set-hot -` could not run.

**One design per op, reconciling carries 5, 9, 10 and 11** (1-based, as the group row lists them):

- `set-size <group> <size> [--cite <ref>@<sha>]` (carries 5 and 9). The size must be keyed by `tools/plan/durations.json`, by the same `_size_why` check `append-group` runs, so `XS` is legal exactly when the model keys it. `--cite` is optional: carry 9 gives the op no cite, carry 5 requires one; where given it must be `<ref>@<sha>` and the ref must hold the sha. The old size (or `unset`) and the cite go to `resume.note`.
- `set-files <group> [--add <path>...] [--set-files <p,p|->] [--set-hot <p,p|->] [--cite <ref>@<sha>]` (carries 5, 10 and 11). `--add` appends; `--set-files` replaces `files` whole; `--set-hot` replaces `hot_files` whole (`-` for none, key kept). A path new to `files` must be in the tree at origin/main or at the cited sha. A hot token must be a basename of the group's resulting files or a token some group already holds. Old values and the cite go to `resume.note`. An unknown group refuses; every other field stays byte-identical; the lint gate, triage gate and push race are the shared `write_roster` path.
- A value already held writes nothing (no note, no commit), which is each op's null control.

## Head

1b4932489d81d72af4cdba9ed108bff1874a0917. origin/main unmoved since the last prepr.sh run (rc=0, ci predict clean), so no second run.

## Mutation proof

`python3 tools/audit/seat/r10_roster_ops_mutants.py Z1 Z2 Z3 Z4 Z5 Z6 Z7 Z8 Z9 Z10 Z11 Z12` prints `plants: 12, without a FAIL line: none`, each plant `rc=1` with at least one FAIL line: Z1 skips set-size's `_size_why` (fails=5), Z2 its cite check (4), Z3 drops the size write (4), Z4 lets the no-op write a note (1); Z5 skips set-files' path-in-tree refusal (7), Z6 drops the files write (10), Z7 the hot_files write (4), Z8 skips the hot-token refusal (1), Z9 the cite check (1), Z10 the unknown-group refusal (1), Z11 drops the cite in the dispatch (4), Z12 writes hot_files on a call that never named it (4). The plants are a separate block of `r10_roster_ops_mutants.py`, merged into `PLANTS` after the existing table.

## Null control

`python3 tools/audit/seat/r10_roster_ops_mutants.py --null` prints `RESULT mutant=null rc=0 fails=0`. In the self-test: `set-size` to the current size, `set-files --add` of a held path, `--set-hot` with the current value and `--set-hot -` on an empty field each leave the remote tip unchanged. Failing test first: with the arms in and the ops absent, `roster_edit.py --self-test` crashed in the new block; it now prints `167 checks, 0 failed`.

## Figures

- `python3 tools/audit/seat/roster_edit.py --self-test` : the self-test count and failure count above (instrument: roster_edit self-test; counts every `check(` call).
- `python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test` : every anchor, including Z1-Z12, occurs once in the target.
- `git merge-tree --write-tree origin/main refs/pull/3054/head` already reports conflicts in roster_edit.py, roster_sync.py and r10_roster_ops_mutants.py at the base ca6333333; this branch's merge-tree against the same head reports the same three files, with more hunks in roster_edit.py (the usage block, docstring, argparse choices and flags, validation and the dispatch beside #3054's own edits to those lines). I cannot say it is conflict-free: #3054 does not merge with main yet, so its resolution decides, and both sides are additive (new ops, new flags, a separate mutants block) and compose by union.
- Measured at base ca6333333afc, origin/main unmoved at the time of the last `prepr.sh` run, 2026-11-01.

## Unpinned sites

The diff adds only tools/ sites; each is pinned by the in-tree harness r10_roster_ops_mutants.py (plants Z1-Z12, all killed).

## Red checks

none

## Forward-carry

Carries answered. Built here: 5 (set-size and set-files --add), 9 (set-size), 10 (--set-hot), 11 (set-files replace and clear). Left for part 2, unchanged, landing in the R10-ROSTER-OPS-2 row of dev/programme/rosters/wave-r10-groups.json: carries 1, 2, 3, 4, 6, 7, 8 and 12 -- Carry: R10-ROSTER-OPS-2.

## Friction

none
