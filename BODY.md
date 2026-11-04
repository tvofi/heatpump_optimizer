`coord_footprint` charged one AST statement as one logic statement however much it packed, so a seat could lower the architecture score by packing (PR 3185 review, item a2e21972: 6 of the 7 statements behind its movement were one packed generator unpack). Counter C25 (`metrics/footprint.py` `_units`) reads a packed statement as the plain statements it spells. Shapes enumerated and closed: tuple target (`a, b, c = (f(x) for x in xs)`), tuple value (`a, b = f(), g()`), chained targets (`a = b = f()`), a bare tuple expression, several `with` items, several `import` names, a multi-target `del`. A tuple pair of plumbing (`a, b = x.p, x.q`), a chain of aliases and a bare tuple of delegations stay plumbing, as the plain spelling is. Not packing, left as one operation: `for a, b in x` and one destructured value (`a, b = pair`, read by arity like `a = pair[0]; b = pair[1]`). Alternatives rejected: counting arity only for generator values (a wrapping `tuple(...)` call evades it); counting every tuple pair (reads G5, a GOOD frozen-record refactor, as WORSENS). Closes the review item; no issue.

## Head

176a6a9e899786bac477437836dcd87b93781951, on origin/main 783d8dc72811ab75ae4ffca367456f44896f47d3. origin/main unmoved since the last `tools/pr/prepr.sh` run (rc=0), so no second run.

## Mutation proof

Mutant: `footprint.PACKING_UNITS = False` (what `ARCHSCORE_ABLATE=C25` sets), so `_units` is not read. Measured: packed vs plain statement counts (packed, plain) were (3,3) (0,0) (0,0) (2,2) fixed and (1,3) (1,0) (1,0) (1,2) mutant, so the new `tests/arch_score.py` check "coord_footprint reads a packed statement as the plain statements it spells (every packing shape)" fails; and `ARCHSCORE_ABLATE=C25 calibrate.py --only rt_48_footprint_packed_unpack` reads `rt_48 GAME IMPROVES`, which fails "no red-team attempt reads IMPROVES". Restored. The suite's mutation job was not run locally.

## Null control

Untouched tree: `rt_00_null_rename` reads NULL, and the packing attempt (rt_48 packs runs of plain assignments in the coordinator into generator unpacks) reads NULL with C25 and IMPROVES (+0.0092 on coord_footprint) with it off. Packed and plain spellings read the same: the `packed_plain` table in `tests/arch_score.py`, nine shapes. Stored corpus: no verdict moved under `calibrate.py --measure-corpus --only-metric footprint`; the corpus vectors were re-measured twice (second pass after the bare-tuple rule) and the second pass changed nothing. One planted verdict moved: `a1_G2_dedupe` (GOOD) NULL -> IMPROVES, correct direction (the replay block it removes holds `wind_speed, precipitation = self._current_weather()`); recorded in `expected.json`.

## Figures

- Footprint of the tree with C25 and without, same tree: 2483 and 2381. Command: `python3 -c` over `archscore.metrics.footprint.measure` with `PACKING_UNITS` True then False (the instrument is `tools/audit/archscore/metrics/footprint.py`; the number moves with the tree). The budget file's `archscore.coord_footprint` in `tests/ci_budgets.json` still holds it.
- `PYTHONPATH=tests/hastub python3 tests/arch_score.py`: all checks pass (final count printed by the instrument).
- Toolchain: numpy 2.5.4, scipy 1.18.1 match `tests/requirements-ci.txt`; `cloud-setup.sh --check` OK. Golden fixtures untouched.
- `python3 tests/structure.py`: PASSED, no budget raised. `tools/pr/prepr.sh`: rc=0.
- Gate scope: `MODE: FULL` (tools/ files are unmeasured until the closure records; CI re-records). `tests/closures.json` carries one `tests/arch_score.py` closure entry for the new red-team file, from `derive_closures.sh --single tests/arch_score.py` on Linux.

## Red checks

none

## Forward-carry

none

## Friction

none
