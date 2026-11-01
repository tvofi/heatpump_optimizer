Adds the roster's two missing field-writing ops, `set-size` and `set-files`, to `tools/audit/seat/roster_edit.py` (R10-ROSTER-OPS-2 part 1, issue #3131; owner tvofi approved plan-slip card 1, cap gate passed with `--over-cap "tvofi 2026-11-01 plan-slip card 1"`). Until now nothing could write a group's own `size`, `files` or `hot_files`, so the queued re-sizes of R10-FLY-STANDING-CONTRACTS and R10-ADVISOR-WHATIF and the held `set-files R10-ARCH-SHAPES-CLASSIFIER --set-hot -` could not run.

**One design per op, reconciling carries 5, 9, 10 and 11** (1-based, as the group row lists them):

- `set-size <group> <size> [--cite <ref>@<sha>]` (carries 5 and 9). The size must be keyed by `tools/plan/durations.json`, by the same `_size_why` check `append-group` runs. `--cite` is optional; where given it must be `<ref>@<sha>` and the ref must hold the sha. The old size (or `unset`) and the cite go to `resume.note`.
- `set-files <group> [--add <path>...] [--set-files <p,p|->] [--set-hot <p,p|->] [--cite <ref>@<sha>]` (carries 5, 10 and 11). `--add` appends; `--set-files` replaces `files` whole; `--set-hot` replaces `hot_files` whole (`-` for none, key kept). A path new to `files` must be in the tree at origin/main or at the cited sha. A hot token must be a basename of the group's resulting files or a token some group already holds. An unknown group refuses; every other field stays byte-identical; the lint gate, triage gate and push race are the shared `write_roster` path.
- A value already held writes nothing (no note, no commit), which is each op's null control.

**Round 2 repair (one finding, the fix review's unpinned-site block).** `cite_why`'s `git merge-base --is-ancestor <sha> <ref>` clause survived deletion (reviewer mutant R11, `rc=0 fails=0`) because no arm cited a sha that exists but that the named ref does not hold. Added: one self-test arm per op citing `main@<sha of a commit only the `cited` branch holds>`, expecting rc 2, "does not hold" and the remote tip unchanged; and plant R11 in the new block of `r10_roster_ops_mutants.py`. Nothing else changed.

## Head

b0976a20f27ce5abbc07a6c175113b54295a4b83 (code head; merges origin/main 56630e7e6d229d960cf1b4db304d488ee20873e6 into the round-1 PR head e323d75500c843ae2ffaa076a33ddabca7c68853, which carries the round-1 code head 1b4932489d81d72af4cdba9ed108bff1874a0917 and the repair commit). Measured 2026-11-01 after the merge; `git merge-tree --write-tree origin/main HEAD` rc 0.

## Mutation proof

Reviewer's R11 (replace the ancestry clause with `True`) reproduced as plant R11: `python3 tools/audit/seat/r10_roster_ops_mutants.py R11` prints `RESULT mutant=R11 rc=1 fails=5` (was `rc=0 fails=0` at e323d7550). The full run `python3 tools/audit/seat/r10_roster_ops_mutants.py` after the repair: `RESULT mutant=null rc=0 fails=0` and every Z1-Z12 and R11 plant `rc=1` with FAIL lines (Z1 6, Z2 5, Z3 4, Z4 1, Z5 8, Z6 10, Z7 4, Z8 1, Z9 2, Z10 1, Z11 5, Z12 4, R11 5). The run prints `plants: 46, without a FAIL line: ['C6']`; C6 belongs to the pre-existing block, which this PR does not touch (it is a crash-kill, rc=1 with a traceback, not a survivor).

## Null control

`python3 tools/audit/seat/r10_roster_ops_mutants.py --null` prints `RESULT mutant=null rc=0 fails=0`. For the new arms, the control is the accepting path: `set-size ... --cite main@<main tip>` lands (existing arm) and `set-files --add NEW.md --cite cited@<sha>` lands, where `cited` does hold that sha. The earlier controls stand: set-size to the current size, `--add` of a held path, `--set-hot` with the current value and `--set-hot -` on an empty field each leave the tip unchanged.

## Figures

- `python3 tools/audit/seat/roster_edit.py --self-test` prints `169 checks, 0 failed` (instrument: roster_edit self-test; counts every `check(` call; 167 plus the two new arms).
- `python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test` prints `144 checks, 0 failed`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `git merge-tree --write-tree HEAD refs/pull/3054/head` still reports conflicts in roster_edit.py, roster_sync.py and r10_roster_ops_mutants.py; so does origin/main against #3054, which does not merge with main, and the additions here are separate-block and additive. This PR adds no file to that conflict set.

## Unpinned sites

The diff adds only tools/ sites, pinned by the in-tree harness `r10_roster_ops_mutants.py`. This round adds one site, cite_why's ancestry clause, pinned by plant R11 and the two new arms. Count of new-block plants: `grep -cE '^    "(Z[0-9]+|R11)": ' tools/audit/seat/r10_roster_ops_mutants.py` prints 13 (12 at e323d7550); every one is killed (see Mutation proof).

## Red checks

none. The whole check-run set at PR head e323d75500c843ae2ffaa076a33ddabca7c68853 was read (55 runs, one page of 100): no run concluded failure; the rest are success or skipped.

## Forward-carry

Carries answered. Built here: 5 (set-size and set-files --add), 9 (set-size), 10 (--set-hot), 11 (set-files replace and clear). Left for part 2, unchanged, landing in the R10-ROSTER-OPS-2 row of dev/programme/rosters/wave-r10-groups.json: carries 1, 2, 3, 4, 6, 7, 8 and 12 -- Carry: R10-ROSTER-OPS-2.

## Friction

none
