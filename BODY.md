R10-OUTSIDE-DHW-CHARGE-SETTLE: the build of outside pull request #3434 by @Bankaifan, whose commit opens this branch with its authorship kept (its tool-attribution trailers removed, which `ref_privacy.py guard` refuses). A DHW charge start drops the tank reading 3-5 K within minutes; the usage learner booked that dip as a draw on the unheated intervals after a short charge, and the draw-statistics fold booked it on heated intervals, inflating the heavy-day p90 the planner reads through `DrawStats.quantile`.

The fix, in `dhw_learning.py`'s `async_learn_dynamics`: an interval is charge-affected when it was heated, started on a heated sample, or ends within the new settle constant (the DHW charge settle window, 0.25 h) of the last heated sample, which the learner stamps in memory as `last_heated_time`. A charge-affected interval feeds neither the cooling nor the usage learner and is folded into the draw statistics with a zero drop (still folded, so occurrence accounting is unchanged). The author paid for the added class lines by folding the two duplicated day-type restore loops of `async_load_profile` and `apply_payload` into one `_restore_daytypes`; `apply_payload` now takes an overflowing day count as zero, as the loader already did (main raised `OverflowError` out of it), pinned below.

Design choices a reviewer may read as bugs: a restart mid-settle forgets `last_heated_time`, so at most one dip after a restart is learned (the author's choice; persisting it would add a store field for one interval). A `last_heated_time` ahead of the reading clock gives a negative age, which reads as inside the window: the interval is not learned rather than learned on an unknowable age (`fixer.md` step 16). A real draw during a charge, or within 15 min after one, is now folded as zero; before, a heated interval's drop was folded as a lower bound. The charge arm below measures what that costs against the dip-free truth trace.

Alternatives considered: (a) fold heated intervals as before and gate only the settle window — leaves the in-charge dip folded, the defect's second half; (b) persist `last_heated_time` — a store migration for one interval per restart; (c) subtract a modelled dip — a model of a transient with no in-tree evidence for its shape. The author's gate is the smallest change that removes both phantom routes.

## Head

Measured at code head `8e2b7d99d0e99f3cbd00d49ceb9b4a1458b87257` on base `8f97247fc1a6911b85788a73fe502ea0097bac13` (`origin/main` at measurement, 2026-11-11T06:40Z).

## Mutation proof

Failing test first: the features block `a charge-start dip is learned as neither a draw nor usage` and `a snapshot restore takes an overflowing day-type count as zero, as the loader does, and keeps a day type with a malformed profile as it was`, run with `dhw_learning.py` checked out at `origin/main` and the rest of the head:

```
  FAIL a charge-start dip is learned as neither a draw nor usage  [(kWh folded, usage points) heated (0.68904, 0), 5 min after the charge (0.68904, 1), 20 min after (control) (0.68904, 1), space-heating start with no DHW charge on record (control) (0.68904, 1), driven heated-then-settling sequence (0.68904, 1), cooling samples from a 30-min interval started heated / not (control) (0, 1)]
  FAIL a snapshot restore takes an overflowing day-type count as zero, as the loader does, and keeps a day type with a malformed profile as it was  [(weekend day count, profile length) restored from inf / 7 (control) / 7 beside a 23-long profile / 7 with no profile / -3: ('OverflowError', (7, 24), (0, 24), (0, 24), (0, 24))]
2 of 2 FEATURES BLOCK FAILED
```

Only the inf arm differs at main: the other restore arms pin what the refactor had to keep. At the head both checks read `ok` (`ALL 2 FEATURES BLOCK PASSED`).

Mutants, each `{name, file, old, new}` on `custom_components/heatpump_optimizer/dhw_learning.py`, run by `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd "<CMD>"` (copy-tree) at the head, CMD being:

```
env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from harness import FakeEntry as _r7d203_entry' --prelude 'import asyncio as _aio' --prelude 'from homeassistant.util import dt as dt_util' --prelude 'from datetime import timedelta' '# A charge start makes the tank reading FALL' '# A zero-capacity tank is the input'
```

| mutant | old | new |
|---|---|---|
| SETTLE_ARM_OFF | `<= DHW_CHARGE_SETTLE_HOURS` | `<= 0.0` |
| SETTLE_SHORT | `DHW_CHARGE_SETTLE_HOURS = 0.25` | `DHW_CHARGE_SETTLE_HOURS = 0.05` |
| SETTLE_LONG | `DHW_CHARGE_SETTLE_HOURS = 0.25` | `DHW_CHARGE_SETTLE_HOURS = 0.5` |
| STAMP_DEL | `            self.last_heated_time = now\n` | `            pass\n` |
| ZERO_DROP_OFF | `0.0 if charge_affected else temp_drop` | `temp_drop` |
| USAGE_HEATING_ONLY | `            charge_affected,\n            weekend=` | `            heating,\n            weekend=` |
| COOLING_HEATING_ONLY | `        if not charge_affected:\n` | `        if not heating:\n` |
| OVERFLOW_DROP | `except (TypeError, ValueError, OverflowError):\n                self.daytype_samples[idx] = 0` | `except (TypeError, ValueError):\n                self.daytype_samples[idx] = 0` |

```
SURVIVED NULL
KILLED SETTLE_ARM_OFF
KILLED SETTLE_SHORT
KILLED SETTLE_LONG
KILLED STAMP_DEL
KILLED ZERO_DROP_OFF
KILLED USAGE_HEATING_ONLY
KILLED COOLING_HEATING_ONLY
KILLED OVERFLOW_DROP
```

The author's `_restore_daytypes` refactor, same CMD, same head:

| mutant | old | new |
|---|---|---|
| RESTORE_RESET_OFF | `self._restore_daytypes(stored, reset_missing=True)` | `self._restore_daytypes(stored, reset_missing=False)` |
| RESTORE_POOLED_OFF | `            elif reset_missing:\n` | `            elif False:\n` |
| RESTORE_SKIP_OFF | `            else:\n                continue\n            try:` | `            else:\n                pass\n            try:` |
| RESTORE_LEN_OFF | `if isinstance(arr, list) and len(arr) == 24:\n                setattr(self, key, self.normalize_profile(arr))` | `if isinstance(arr, list):\n                setattr(self, key, self.normalize_profile(arr))` |
| RESTORE_CLAMP_DROP | `self.daytype_samples[idx] = max(0, int(source.get(f"{key}_samples", 0)))` | `self.daytype_samples[idx] = int(source.get(f"{key}_samples", 0))` |

```
SURVIVED NULL
SURVIVED RESTORE_RESET_OFF
SURVIVED RESTORE_POOLED_OFF
KILLED RESTORE_SKIP_OFF
KILLED RESTORE_LEN_OFF
KILLED RESTORE_CLAMP_DROP
```

The two loader-path mutants are pinned by the existing store-loader checks elsewhere in `tests/features.py`, so they are run over the whole script, in place (`--in-place`, a second worktree at the same head; a `git archive` copy fails the unedited script, `KILLED NULL`), `mutant_run.py --in-place --spec <those two> --cmd "env PYTHONPATH=tests/hastub python3 tests/features.py"`:

```
SURVIVED NULL
KILLED RESTORE_RESET_OFF
KILLED RESTORE_POOLED_OFF
```

RESTORE_SKIP_OFF and RESTORE_LEN_OFF first survived the whole of `tests/features.py` (`SURVIVED RESTORE_SKIP_OFF`, `SURVIVED RESTORE_LEN_OFF` beside `SURVIVED NULL`, at `348e0c8ca623`): `apply_payload`'s keep-as-it-was arm had no check at main either. The restore check's absent-profile, 23-long-profile and negative-count arms were added for them.

COOLING_HEATING_ONLY survived the author's test (`SURVIVED COOLING_HEATING_ONLY` beside `SURVIVED NULL`) until the 30-min started-heated arm was added. The settle window's own extension of the cooling guard is equivalent and has no mutant: `last_heated_time` is stamped only at a sample, so an interval that is affected by the settle window alone (its start sample unheated, its end within 0.25 h of a heated sample) has `dt_h` under 0.25 h, which `async_learn_cooling` refuses below `DHW_COOLING_MIN_SAMPLE_HOURS` (0.25) on its own.

## Null control

Two in-tree nulls in the same block, both reading `ok` at the head and the same values at main: a compressor start for space heating with no DHW charge on record learns exactly what the 20-min-after control learns (`(0.68904, 1)` at both ends), because the learner's only heating input is the plan's `dhw_heating_active` flag; and the 30-min interval with no charge on record still teaches one cooling sample. In the p90 harness the flat arm (the same reheat, flag never set, no dip) is bit-identical at both ends.

## Figures

The heavy-day p90, `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_dhw_charge_settle_p90.py` (sha1 df1bc6619db4b95b19a9472316524a98f4ce8549), run in a `git archive origin/main` export (base) and at the head; 28 days, 5-min samples, seed 3434, one morning draw and one 10-min charge a day; per arm `(usage profile updates, {window: (occurrences, quantile(window, 0.9) kWh)})`:

```
# base 8f97247fc1a6 (git archive origin/main)
dip      {'usage_points': 112, '00:00-24:00': (27, 6.1506)}
truth    {'usage_points': 84, '00:00-24:00': (27, 5.5346)}
flat     {'usage_points': 84, '00:00-24:00': (27, 5.5346)}
dip@max  {'usage_points': 112, '00:00-24:00': (27, 5.8376)}
truth@max {'usage_points': 84, '00:00-24:00': (27, 5.3169)}
# head 348e0c8ca623
dip      {'usage_points': 84, '00:00-24:00': (27, 5.5307)}
truth    {'usage_points': 84, '00:00-24:00': (27, 5.5326)}
flat     {'usage_points': 84, '00:00-24:00': (27, 5.5346)}
dip@max  {'usage_points': 84, '00:00-24:00': (27, 5.3169)}
truth@max {'usage_points': 84, '00:00-24:00': (27, 5.3169)}
```

Read: at the base the dip adds one phantom usage update per day (112 vs the truth trace's 84) and lifts the p90 above the dip-free truth trace; at the head the dip arm reads the truth trace's figures within the zero-drop cost of the charge interval itself (`truth` at head vs base), and the flat control is identical at both ends. The clamp end (`dip@max`, `truth@max`, cooling rate pinned at `DHW_COOLING_RATE_MAX`) reads the same way, and every arm starts from a fresh learner (zero evidence).

Structure ratchet: `python3 tests/structure.py` at the merge base prints `RESULT class_excess_loc=17537 count`, at the head `RESULT class_excess_loc=17535 count`; re-recorded by `python3 tests/structure.py --record` from main's budget file, so the file's only metric change is that row, down, and `recorded_at` (to the merge base `8f97247fc1a6`). No metric moved up. The author's own re-record (17533, at `45adb0c3b425`) predated the two lines the typing fix added; it is superseded, not raised. `STRUCTURE RATCHET PASSED`.

Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0237 IMPROVES` (`literal_clone_copies 122 -> 120`, `reflective_writes 11 -> 9`, `computed_attr_access 28 -> 26`).

Class seams (`fixer.md` step 8). The class: a tank-temperature drop attributed to consumption while a charge drives the reading. Enumerator: `git grep -n "dhw_heating_active\|_heating_active()" -- custom_components/` and `git grep -n "async_learn_dynamics\|CONF_DHW_TEMP_ENTITY" -- custom_components/`. Dispositions:
- `dhw_learning.py` `async_learn_dynamics`, the one reader of the learner's heating flag, and its three consumers `async_learn_cooling`, `async_learn_usage`, `async_fold_draw_stats`: closed in this diff.
- `coordinator.py` `_dhw_probe_temperature` and the DHW lead-prediction record: compares the plan's promised tank temperature with the reading; a dip there is a real miss of the promise, not a consumption attribution. Outside the class.
- `boost.py`, `optimizer.py`, `payload.py`, `climate.py`, `sensor.py`, `coordinator.py` (`dhw_heating_active` writes and publication), `device_prefill.py`, `modbus_prefill.py`, `name_match.py`, `topology.py`, `thermal_model.py`, `sensor.py` probe slots (configuration and display): no drop attribution.

Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at the head printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` and `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`. A first run at an earlier head of this branch failed `tests/typing_ruler.py` (`by_code[arg-type] did not grow  [recorded 0, measured 1 (+1)]`, in the author's `_restore_daytypes`, whose `usable` flag does not narrow the list for mypy); the head tests `isinstance` inline and `python3 tests/typing_ruler.py` reads `ALL 12 typing-ruler source checks PASSED`.

## Unpinned sites

Each site `tools/pr/ci_predict.py` lists as ADDED UNPINNED, every one in `custom_components/`, so `mutation-autofix` pins it after the push (its lane mutates `custom_components/`); the value check that already kills a mutant at the same site is named:

- custom_components/heatpump_optimizer/dhw_learning.py:72 CONST — pinned by `mutation-autofix`; value check: SETTLE_SHORT and SETTLE_LONG killed above.
- custom_components/heatpump_optimizer/dhw_learning.py:277 GUARD_OFF — pinned by `mutation-autofix`; value check: RESTORE_POOLED_OFF killed above (whole `tests/features.py`).
- custom_components/heatpump_optimizer/dhw_learning.py:282 CLAMP_DROP — pinned by `mutation-autofix`; value check: RESTORE_CLAMP_DROP killed above.
- custom_components/heatpump_optimizer/dhw_learning.py:362 GUARD_OFF — pinned by `mutation-autofix`; value check: STAMP_DEL killed above.
- custom_components/heatpump_optimizer/dhw_learning.py:387 GUARD_OFF — pinned by `mutation-autofix`; value check: COOLING_HEATING_ONLY killed above.

The two `killed_by` ledger pins this diff deletes (`DhwProfileLearner.async_learn_dynamics.GUARD_OFF.a63ec5b3`, `DhwProfileLearner.apply_payload.BOOLOP.e4eb8c37`) name lines the diff rewrote; `ci_predict.py` predicted each a STALE PIN red on `ledger`, repaired by the deletion.

## Red checks

- `mutation` at 8e2b7d99d0e9: red by construction on the 5 site(s) under `## Unpinned sites`; `mutation-autofix` pins killed sites after the push (`ci-autofix.md`). Root-cause answer: the cheaper detector already ran — `tools/pr/ci_predict.py` (prepr step 6d) named every site locally before the handoff, at no added standing cost; the red is the pin-recording step, not an escaped defect, so no further countermeasure is owed.

## Forward-carry

none

## Friction

none
