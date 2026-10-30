away: set back the weekend and holiday comfort pairs too (r10-hotfix-away-setback)

Hotfix from tvofi's live finding (#201 comment 6528614583, 2026-10-30), using the latent (b) the probe `r10-live-away-heating` measured (report: `handoff-body/r10-live-away-heating` at aa6e5db30ba6fe7cb4a2f1016c271ae9bf260af2). While away and not recovering, `away.solve_bands` set back `target_temp`, `min_temp` and `comfort_temp_day/night`, but it left `comfort_temp_{day,night}_weekend` and `holiday_comfort_{day,night}` as configured. `OptimizationConfig._comfort_pair` substitutes those fields per step on Saturdays, Sundays and holiday dates, so with away on, Saturday's comfort target read 21.0 where the away target was 16.0.

**Fix.** The four schedule fields join `away._OPT_FIELDS` and the `_SetbackConfig` protocol (typed `float | None`). `solve_bands` now reads only the configured (non-None) fields, and while away and not recovering it sets every comfort number it read to the away target, keeping `target_temp` and `min_temp` as `min(configured, target)`. An unconfigured field returns no band and keeps None through `replace`. The coordinator caller (`_solve_hubs`) is unchanged, because it already spreads `**config_bands` into `replace`.

**Alternatives considered.**
- (a) Bypass the weekend and holiday branches in `_comfort_pair` while away. This would put away state into the optimizer config, a second owner of the setback concept. Rejected (fixer step 17: one owner per concern; `away.py` owns the setback).
- (b) Always return all eight keys, including None. This would widen the return type to `dict[str, float | None]` and touch the coordinator's annotation for no behavioural gain. Rejected.

No issue is closed: the finding came from a #201 comment, not an issue. The presence-entity state listener (the probe's (c)) was routed to R10-LIVESTATE's coordinator move by the dispatch brief before this seat ran, so this body carries nothing forward.

## Head

Measured at `3ec79824c44eb346f6da62af678eae08ec742f2b` (branch `handoff/r10-hotfix-away-setback`), cut from `origin/main` = `cc930cdd1a3cfb005ba7ec557f4451ff5e53e364` (merge base, behind main by 0), measured 2026-10-30 UTC.

Commits:
- `82c6913c2`: the fix, the test and the harness.
- `3ec79824c`: `tests/closures.json`, the harness's INERT READS entry written by `tools/pr/ci_predict.py --apply-inert`.

## Mutation proof

The failing test came first. The new checks are in `tests/features.py`, in the `away.solve_bands` block after the economy-widening check, and they run through the production `OptimizationConfig`, then `away.solve_bands`, then `replace`, then `HeatPumpOptimizer._build_comfort_bounds`, with step times Sat 2026-10-31 14:00 and 03:00. No formula is re-implemented.

- **Before the fix** (test added, `away.py` at the base), `PYTHONPATH=tests/hastub python3 tests/features.py` gave `1 of 4607 FEATURE CHECKS FAILED`: `FAIL away sets back the weekend and holiday comfort pairs too: Saturday day and night read the away target [... ('weekend', 'away'): [21.0, 19.5] ... ('holiday', 'away'): [21.0, 19.5] ...]`.
- **After the fix**, the same command gave `ALL 4607 FEATURE CHECKS PASSED`.

**Mutants: one per added field.** Each mutant deletes that one name from `_OPT_FIELDS`. Each ran in a copy of `custom_components/` and `tests/` outside git. All four were killed by the new check, and each mutant reverts exactly its own slot:

| mutant (field removed) | killing check | weekend away [Sat 14:00, 03:00] | holiday away [Sat 14:00, 03:00] |
|---|---|---|---|
| `comfort_temp_day_weekend` | away sets back the weekend and holiday comfort pairs too | [21.0, 16.0] | [16.0, 16.0] |
| `comfort_temp_night_weekend` | the same | [16.0, 19.5] | [16.0, 16.0] |
| `holiday_comfort_day` | the same | [16.0, 16.0] | [21.0, 16.0] |
| `holiday_comfort_night` | the same | [16.0, 16.0] | [16.0, 19.5] |

Each mutant run also printed `FAIL and the path that proceeds still stamps a resolvable recorded_at (#363)`. That is the runner's own failure for an out-of-git copy, which fixer step 2 names (#1713, #1723), and not the mutant's.

Disclosed: those copies did not include `tools/`, so each run stopped later at `ModuleNotFoundError: gen_device_fixtures`. That happened after the killing check had printed FAIL, so the kills stand, but no mutant run reached the end of the suite. CI's required mutation check is the complete run.

## Unpinned sites

The added production lines are the four `_OPT_FIELDS` names, the `if (v := getattr(...)) is not None` filter and the `dict.fromkeys(config, target)` setback.
- The four names are pinned by the value check above (the mutants).
- The setback line is pinned by the same check: without it, every arm reads [21.0, 19.5].
- The None filter is pinned by the existing `_G8Opt` checks, now with the four fields set to None. "And RECOVERY ends it" compares the exact four-key dict returned when away is off or recovering, so a filter that let None through would add four keys and fail it (reasoned from the exact-dict comparison; this one was not mutant-run).

## Null control

- **Away off** ("home" rows) and **recovery_active** ("recovering" rows) keep the configured pairs, [21.0, 19.5], in both the weekend and holiday arms. Check: `and away off, or recovering, keeps the configured weekend and holiday pairs (the null control)`. It passes at both the base and the head; under a fix that ignored the away state it would read [16.0, 16.0].
- Recovery deliberately keeps today's behaviour, which drops the setback wholesale. Whether it should is a design question for tvofi, not this fix.
- The harness's `weekend_away_off` row is unchanged between the base and the head (Sat 21.0).

## Figures

**Harness** `dev/audit/harnesses/r10_live_away_heating.py` (sha1 `822ccca27a2189754ee77e334e1e0544f8901191`; the probe's harness verbatim, committed here). Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_live_away_heating.py`. The rule is `diff` of the full output, base against head:
- Before (`cc930cdd1`): `arm=weekend ... comfort_sat=21.0`, `arm=weekend_flat ... comfort_sat=21.0`, `arm=holiday ... comfort_sat=21.0`, and `VERDICT weekend/holiday comfort REPLACES the away target (Sat 21.0 / 21.0 vs 16.0)`.
- After (`3ec79824c`): the same three rows read `comfort_sat=16.0`, and the verdict reads `keeps the away target (Sat 16.0 / 16.0 vs 16.0)`.
- `diff` returned exactly lines 6, 7, 9 and 13: those three rows and the verdict. Every other RESULT row (away, null_away_off, away_off_setpoint21, null_flat, indoor18, weekend_away_off, recovery) is byte-identical, including space slots, kWh and DHW. The null for this is the diff itself: a change touching any other row would have listed it.
- Space slots are 0 in the weekend and holiday arms at both ends. In this house the defect raised the comfort target and not the slot count (the probe's "extra space slots: none").

**Scoped gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=cc930cdd1… PYTHONPATH=tests/hastub bash tests/run.sh` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out` and `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, exit 0. The scope comes from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`.

**Goldens.** `tests/env_drift.py --all cc930cdd1…` reported `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`.
- Rule: per-scenario lines in the env_drift section of the gate log.
- Of the 56, 37 printed `is byte-identical`, and every remaining one is a may-drift fixture printing `did not move here`.
- Neither claim file was touched, so no golden moved.

**Ratchet and architecture.**
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff cc930cdd1…`: `Architecture score: dS +0.0000 NULL`.

**ci_predict.** `python3 tools/pr/ci_predict.py --apply-inert` wrote `APPLIED inert_reads tests/harness_headers.py: dev/audit/harnesses/r10_live_away_heating.py` (commit `3ec79824c`), then `CI PREDICT: no closures, fast, governance or instrument red predicted`. The harness path is otherwise INERT by the `dev/audit/` prefix in `tests/closure.py`'s `INERT`.

**Class seams (fixer step 8).** The rule is an AST pass over `OptimizationConfig`, listing every `self.<attr>` read by `_comfort_pair`, `get_comfort_temp` and `get_temp_bounds`, the readers `_build_comfort_bounds` calls per step. It returned 15 fields:

| seam | disposition |
|---|---|
| `comfort_temp_day_weekend`, `comfort_temp_night_weekend`, `holiday_comfort_day`, `holiday_comfort_night` | closed in this diff |
| `comfort_temp_day`, `comfort_temp_night`, `min_temp` | already set back (unchanged) |
| `max_temp` | the ceiling. A setback lowers the target and the floor, and a ceiling above them buys no heat. Not part of the class. |
| `day_start_hour`, `day_end_hour`, `day_start_hour_weekend`, `day_end_hour_weekend`, `holiday_day_start_hour`, `holiday_day_end_hour`, `holiday_dates` | these only choose between the day and night value, and both are now the away target while away. Inert. |

Outside this class and not touched here: `coordinator._resolve_away` calls `get_comfort_temp(now.hour)` without `when` for the recovery target (probe report, code-chain step 4). That is the recovery design question below, not a setback seam.

## Red checks

None turned red on this branch. The predicted closures red for a new harness (`tests/harness_headers.py`) was repaired before the handoff with `ci_predict.py --apply-inert` (`ci-autofix.md`).

## Forward-carry

none

## Friction

none
