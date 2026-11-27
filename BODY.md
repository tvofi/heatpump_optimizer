R11-OWNER-HOTFILE-COUNTS (owner order, tvofi 2026-11-27). The five hot files were the conflicted files in 90 of the 174 file-conflicts replayed over the window below. #3911 (FG-1, merged 2026-11-27) had already taken the module and pair counts out of `tests/deployment_shape.py`, `docs/architecture.md` and `claims.py`'s header. What still stored a tree-derived value on every module- or entity-adding branch was the D6 register: `claims.json` and `claims.md` are `claims.py`'s committed output, and their rows carry counts (entities, links, translated names, the C35 module list).

This change routes the register through `tools/merge/ledger_merge.py` as a writer-format arm (`tools/merge/d6_register.py`) that merges row by row by claim id. A row one side changed takes that side. A row both sides re-derived takes the incoming row whole. A row added or deleted on one side lands. Anything outside `claims.py`'s own layout refuses to git's text merge. The register stays committed, so no check loses its input. A pick that neither tree derives is refused by the check that already owns the file: `tests/harness_headers.py` (`run_always`) re-runs `claims.py` and fails `the executed harnesses leave their committed output byte-identical`. So a re-derivation now happens at a gate the merge reports, not through hand-resolving conflict markers.

Alternatives considered:
- Stop committing the register and compute it at check time. Rejected: `tests/entities.py` reads row C42 against `VERSION`, `stamp.py` re-records it, and #1148's arm exists to catch drift in exactly that committed file. Removing it removes a pin.
- A merge driver that re-runs `claims.py`. Rejected: git runs a driver per path before the merged tree exists, and `merge-tree` runs it with no worktree at all, so it would measure one side's tree.

## Head

`6de57ed03c832c8f82c576cba7a58d9828a3dbfe` on main `ef797d794017c98f7fb2d8a168d7de63d435ef3b` (`date -u`: `2026-11-27T09:00:47Z`).

## Mutation proof

The self-test entry point is `python3 -I tools/merge/ledger_merge.py --self-test`, the line `governance.yml`'s `instrument-self-tests` runs. `tests/entities.py` also calls it in process. Each mutant was applied, run and restored:
- Deleting `_TABLE_ARMS`' `claims.json` entry gives `FAIL driver: the D6 register merges row by row through its arm` and `FAIL driver: and says the register is owed a re-run`.
- In `d6_register._pick`, `raise Refuse("a row one side rewrote, the other deleted")` changed to `return theirs` gives `FAIL the D6 register arm's own cases pass` and `FAIL json: a row ours rewrote and theirs deleted refuses`.
- `_pick`'s final `return theirs` changed to `return ours` gives `FAIL json: a row both sides re-derived takes the incoming row, the others theirs`, `FAIL md: the same rows merge to the rendering of the merged json`, and three ordering and deletion cases.
- In `_order`, the predecessor insert replaced by `out.append(k)` gives `FAIL json: a row theirs added mid-table lands after its predecessor there`. This mutant survived the first test set; the mid-table case was added to kill it.
- `_json_rows`' layout guard disabled (`if False:`) gives `FAIL json: a file not in json.dump(indent=1)'s layout refuses`.
- `merge_md`'s preamble guard disabled gives `FAIL md: a preamble both sides changed differently refuses`.

The first test set also caught a real defect, which was fixed before the first push: `_order` dropped rows the incoming side had deleted before `_pick` saw them, which silently lost a rewrite/delete conflict.

## Null control

The detector is shown to detect (defect-root-cause.md). I replayed merge `010e0088d5` (`Merge origin/main af4d89f763 into the R11-OWNER-FLOWCAP repair`) in a scratch worktree with the driver, and every other file took its historical resolution. The driver's pick wrote C32/C33 as `documented=101` / `on disk=101`, main's rows. The merged tree derives 102, which is what the historical commit carried after a re-run. I then committed the pick and ran `claims.py`. `harness_headers.dirty_registers()` returned `(False, 'uncommitted:  M .../claims.json;  M .../claims.md')`. After committing the regenerated register it returned `(True, 'clean')`.

Replay null control: the routing touches only the two register paths. `other files` reads the same in all three columns, and the harness prints an `OTHER-FILE-MOVED` line for any non-hot file whose count differs between columns. It printed none.

## Figures

- Conflicts per file over the window, from `python3 dev/audit/harnesses/hotfile_conflicts.py --main ef797d794017c98f7fb2d8a168d7de63d435ef3b --days 10`. Window: 143 pull requests merged into main's first parent in the 10 days before `ef797d7940`, and the 286 main-merges on their branches. The rule for each column is in the harness docstring:
  - `before`: the merge under its own first parent's `.gitattributes`.
  - `driver`: the merge under this head's `.gitattributes`.
  - `after`: the `driver` merge, with each hot text file's passages that main no longer stores (`ANCHORS`) replaced on all three sides by main's current text.

| file | before | driver | after |
|---|---|---|---|
| `tests/deployment_shape.py` | 30 | 30 | 0 |
| `docs/architecture.md` | 12 | 12 | 1 |
| `dev/audit/rounds/round4/D6/claims.json` | 13 | 0 | 0 |
| `dev/audit/rounds/round4/D6/claims.md` | 13 | 0 | 0 |
| `dev/audit/rounds/round4/D6/claims.py` | 22 | 22 | 0 |
| other files | 84 | 84 | 84 |
| merges with any conflict | 76 | 74 | 49 |

  The `driver` column is this change. The `after` text-file arm models #3911's already-merged change: this diff does not touch those three files.
- Independent cross-check of `before`: a separate loop (`git merge-tree --write-tree --name-only` per main-merge on each PR side, without `--attr-source`) found the same 76 merges and the same per-file counts.
- Residual: the 1 `docs/architecture.md` conflict that remains (`d497f7c047`) is two branches each adding a module to the boundary sentence's list of names. That list is documentation that C35 checks against the measured importers, not a stored figure. The claims.py header's `config_defaults_compared` / `config_ranges_compared` still pin counts. They read 0 in `after` because their one window conflict was adjacent to the arch lines #3911 removed. They stay: the exact count is the only thing that catches a documented row the comparator silently skips (`_f is None: continue`), so replacing it with an invariant would need a new census, not a deletion. Carry: dismissed: neither is a stored tree-derived count this diff can drop without weakening C35 or C30/C31; the window measures 0 conflicts on the config lines once #3911's arch lines are gone.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

none

## Friction

none
