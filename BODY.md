Tests-only pins for the plant model seam's 46 full-gate survivors (class I1, #3755), judged in `dev/audit/rounds/round11/D3/wave-judge/JUDGE.json` at a826f55f8c. 45 are pinned. Each pin drives the production entry point its judge's probe drives, fails under the finding's one-line patch and passes without it. One finding is a non-finding at this base, returned to the judge below. No file under `custom_components/` is edited.

Closes #3919

Pin homes follow ADR-011 decision 2 (`dev/audit/rounds/round11/PLAN/ADR-011-survivor-pins.md` at e8aefbb452): beside the existing checks of the same behaviour in `tests/features.py` where there are any, else `tests/guard_pins.py`.
- `tests/features.py`:
  - "Defrost derate (item 14)": the 12 `defrost.py` keys. The `DefrostWindow.peek` pins sit there too, because no existing check drives `peek` mid-defrost.
  - "R9 N-clamp-range": `2aa0f17a216035ee`.
  - "T3 — hot water": `1b476993921016f9`, `ea888783bb621669`, `b098598faf0d87dc`.
  - "The optimizer can see the buffer tank (item 29)": `cde383447b865539`.
  - "The batched trajectory is the scalar trajectory": `7068e39e4608027f`, `6462c28df2f973e0`, `78b7f2ebcf85c8a1`.
- `tests/guard_pins.py`, in `_plant_pins` and `_valve_batch_params_pins`: the other 25 `thermal_model.py` keys.
  - `git grep -cE "_batch_cop\(|_valve_two_zone_delivery\(" 7194ff84c09dd9d54a99f8208c906136981fd9dc -- 'tests/*.py' ':!tests/guard_pins.py'` prints nothing; the same pattern matches `tests/guard_pins.py` at the head.
  - The rest (the scalar COP cap above 27 C, rain, irradiance, ECL110, `dhw_coast_hours`, the buffer loss-rate clamp, the draw pattern, `apply_dhw_coil`, `_simulate_step_two_zone`) have features.py checks that call the same method. Those checks drive other inputs, in sections about other behaviour (combi store floors, configuration mapping, numpy scalar types). None of them is a check of the pinned bound.
- `tests/mutation_ledger/killed_by/`: 42 rows for the 45 keys.
  - Built by `tests/mutation_table.py`'s own `inventory`, `ledger_relpath` and `row_text`.
  - Each key matched exactly one inventory site by file, line, kind and mutated text.
  - Three pairs of keys share one line's anchor: `defrost.py:392`, `defrost.py:537` and `thermal_model.py:674`.
  - An anchor is pinned only when every site under it is killed. Two anchors also hold a mutant of the same line that is not a wave finding; each was driven and is killed by a pin of this diff:
    - `_valve_two_zone_delivery CLAMP_DROP 4cc7cd0a`, the outer-`min` drop: killed by the `39041ccf21eedba6` check.
    - `ThermalModel._simulate_step_two_zone CLAMP_DROP bd87497f`, the outer-`max` drop: killed by the `c5e678a5d1812e40` check.
  - `mutation_table.py --normalize` leaves every row byte-identical.

## Head

a20d9eaa335896be5a1e63940d9fcf959e26ba1d, cut from origin/main 7194ff84c09dd9d54a99f8208c906136981fd9dc (merge base). Measured 2026-11-27 UTC.

## Mutation proof

`bash dev/audit/rounds/round11/D3/pins-plant/run.sh` drives the six specs beside it through `tools/audit/seat/mutant_run.py`. It runs in a git-archive copy of HEAD, with the NULL mutant first.

Each spec entry is one finding's patch, re-located at main by its text:
- Where the text occurs several times in the file, the entry takes the occurrence with the same ordinal as at the baseline 92d38ecb64.
- The entry's `old` is widened by neighbouring lines until it occurs once.

Result at the head:
- `guard_pins` (cmd `tests/guard_pins.py`): SURVIVED NULL; KILLED 27 of 27 (25 keys plus the two same-line siblings). Re-taken at a20d9eaa.
- `features_defrost` (the "Defrost derate (item 14)" block, run by `tools/audit/seat/features_block.py`): SURVIVED NULL; KILLED 12 of 12.
- `features_flow_bias`, `features_t3_hot_water`, `features_buffer_store`, `features_batch`: SURVIVED NULL; KILLED 1 of 1, 3 of 3, 1 of 1 and 3 of 3.
- These four specs and `features_defrost` were taken at 404206fd. No file their commands read has changed since: the later commits touch `tests/guard_pins.py`, one ledger row and this directory's `guard_pins.json`.

Per key, the check that goes red is the one whose name ends `(D3-wave-<key>)`. The `## Figures` run counts FAIL lines per run, and under every patch only `D3-wave-` names are among them. So no pre-existing check of the pin's own command kills any key.

Some patches also redden a sibling pin:
- `8297234e122897ff` and `681130c48add1573`: each other's pin.
- `7068e39e4608027f` and `6462c28df2f973e0`: each other's pin.
- `dfe094233a9164e0`: the `e3a350a3272762f1` and `94ce174acf85b6f2` pins.
- `94ce174acf85b6f2`: the `e3a350a3272762f1` pin.
- `f66c6e9cf9d1f84a`: the `36117bb3a189672b` pin.
- `d90533f4d17cfa14`: the `402ffd06ddbd856a` pin.
- `19404e3632806509`, `beeb068352333132`, `ea9c4705de428b28`: one sibling each.

Failing-first order: each pin was run unpatched (passing) and under the on-disk patch (failing) as it was written, before the next was written.

Disclosed self-correction: a first full re-take with a scratch on-disk driver read `4aac8e694ddc5dfe` as killed by the `1ba9abbe8e702464` check, not by its own. Python had reused the previous same-size mutant's bytecode. A second re-take turned bytecode writes off and purged the package's `__pycache__` around every run, and it read each key killed by its own check. `mutant_run.py` already runs its command with `PYTHONDONTWRITEBYTECODE=1`.

## Null control

On the unedited tree, every `mutant_run.py` spec's NULL mutant SURVIVED: each command passes with no edit. Whole scripts at the head:
- `tests/guard_pins.py`: passes (`## Figures`).
- `tests/features.py`: ALL 6292 FEATURE CHECKS PASSED at 2c128dba7f, the last commit to touch it.

The judges' probes were re-run at the head from the wave's export, `dev/audit/rounds/round11/D3/s1/wave/<box>/probes/probe_<key>.py` at a826f55f8c. Two things were adapted and nothing else changed:
- Their baseline-line anchors were re-located by patch text.
- `valvecommon.py` passes `_valve_two_zone_delivery` the tuple `zone_loss=(0.2, 0.0)` that its main signature takes. The baseline took the scalar 0.2, with the lower-zone term defaulting to 0.

Results:
- **All 45 pinned keys:** the mutant arm differs from the baseline arm.
- **38 probes that print a null arm:** that arm does not move.
- **7 probes that print none** (`5b8e7044ee7974f8`, `f7e051cc469b465f`, `402ffd06ddbd856a`, `d90533f4d17cfa14`, `011b9e2e975b5e98`, `9df41596c4fa89c6`, `029c040224dc4e38`, box D3-g42): these report a moved count over listed inputs.
- **`c5e678a5d1812e40`:** moves only below the 1e-6 h floor, as its probe is built to. The probe reports `below_floor_moved=13`, and its null arm (production step sizes) reports `production_moved=0`.
- **`dd40fdb4edae4d79`** (`_valve_flow_set`, `if valve_target is not None:` -> `if False:`): NON-FINDING at this base, line gone, no pin written. The line's text occurs 0 times at main against 2 at the baseline, so its probe cannot apply the patch (rc 1). Main computes the target as `... if valve_target is None else float(valve_target)` instead.

## Figures

- The re-location, at the merge base: `python3 $EXPORT/dev/audit/rounds/round11/PLAN/d3_fnstate.py $EXPORT/dev/audit/rounds/round11/PLAN/D3-FOLD.json 7194ff84c09dd9d54a99f8208c906136981fd9dc --group R11-D3-PINS-plant --ids`, where `$EXPORT` is `git archive e8aefbb452` extracted (`d3_fnstate.py` sha1 12167cf457102840685558bc28c9c6833e3aae11, `D3-FOLD.json` sha1 25231ce450a8ddf169b7b56f7f6f3b05b6944900).
  - It printed `same 34 changed 10 gone 0 module 2`.
  - The ten changed:
    - `simulate_trajectory_batch`: `7068e39e4608027f`, `6462c28df2f973e0`, `78b7f2ebcf85c8a1`.
    - `_simulate_step_two_zone`: `c5e678a5d1812e40`.
    - `_valve_flow_set`: `dd40fdb4edae4d79`.
    - `_valve_two_zone_delivery`: `19404e3632806509`, `beeb068352333132`, `ea9c4705de428b28`, `98853a541b6b5d6a`, `39041ccf21eedba6`.
  - Each was re-located by its patch text.
- The mutation proof: `bash dev/audit/rounds/round11/D3/pins-plant/run.sh` (results above).
- The scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff 7194ff84c09dd9d54a99f8208c906136981fd9dc --workdir "$D"`, mode line and `scope.run` re-derived at a20d9eaa.
  - At 2c128dba7f: `tests/doc_claims.py`, `tests/entities.py`, `tests/features.py` and `tests/guard_pins.py` each rc 0, as were `tests/run.sh`'s `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`).
  - At a20d9eaa: `tests/guard_pins.py`, `tests/entities.py`, `tests/doc_claims.py` and `tests/layout.py` rc 0. These are the scripts the delta since 2c128dba7f reaches, other than through `dev/audit/`, which `tests/closure.py` holds INERT by prefix.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at a20d9eaa.
- Architecture score: dS 0. No production file is touched (ADR-011, Consequences).

## Red checks

none

## Forward-carry

none

## Friction

- fixer-step-2: cost: a `mutation_table.py --anchor` re-take of a `tests/features.py` kill runs the whole script per site (`tests/closures.json` records 1616.7 s for it). So the 20 features.py kills were proven on `features_block.py` blocks, and those rows' reasons name the block. Carry: dismissed: the ledger's checks read a row's anchor, bytes and `old`, never its reason, and the block run applies the same mutant text to the same check.
