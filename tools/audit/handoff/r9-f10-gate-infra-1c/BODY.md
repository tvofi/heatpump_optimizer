<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the P7 barrier (the DST tracer in `tests/dst_checks.py`, #1665) caught one of the class's three historical members. A capacity tariff was never configured in its replay, and the plan age was only read in the cycle that stamped it, so the `window_factors` (#777) and `_plan_age_minutes` (#1299) shapes passed it. A manual override applied the evening before the autumn fold lasted 21 true hours, and 19 across the spring gap, instead of its stated 20.

After: the tracer replays the three days three more ways (a config arm and a straddle arm, below), the R3 and R5 shapes fail it, and the override lasts 20 true hours on both transition days. The P7 barrier text in `tools/audit/bugclasses.json` names what the tracer still does not reach.

Closes #1756.

The config arm runs the replayed day with a capacity tariff and an off-peak mask at 15 and at 60 minutes, and applies a manual plan through the real `handle_apply_manual_plan` before the fold. The straddle arm fails the solve for four cycles (2 h) across the transition, so stamps written before the fold are read after it. Decided under the mandate (D9): fix, do not exempt, so `services.py`, `manual_plan.build_override` and `manual_plan.channel_pins` go through `accuracy.utc_shift`, and `channel_pins` compares instants because its step-end label (02:00 CET after the autumn fold) otherwise sorts before a start inside the step. This changes behaviour on two days a year: an override's length, and the one step that ends at a fold.

How: `_traced_replay(options, before_cycle, solve_fails)` in `tests/dst_checks.py` is the old inline replay loop as a function; the first run calls it unchanged. Three arm runs follow, each judged by the existing tracer rule (a `-` of two stamps sharing the zone, or a `+ timedelta`, whose result differs from the UTC arithmetic). Instance pins for the override length and the fold step sit beside them. Production changes: `utc_shift` at three sites in `services.py` and `manual_plan.py`, plus an `_instant` helper and its use in the compares in `channel_pins`.

## Head

`e26fa13b8af3359b633471f1ef0c7d220b97fc17` (code head: arms, fix, barrier text, mutation ledger; transport commits sit above it).

## Mutation proof

Instrument: `tools/audit/handoff/r9-f10-gate-infra-1c/run_mutants.sh` (mutants from RCA-BULK-1's `p7_mutants.py`, sha1 62a78339775b64a7de7ed5c534719e4b1cd014b8, copied beside it, and `fix_mutants.py`, which reverts one line of this fix). Each mutant applies to a scratch copy and runs `tests/dst_checks.py` from it. Head, then the same two RCA mutants against the base's own `dst_checks.py`:

| mutant | head: checks that go red | base tests: tracer check |
|---|---|---|
| R3-D2-02 (`window_factors` walks wall time) | arm [tariff 15 min], arm [tariff 60 min], plus #777's own 2 pins | ok, blind (only #777's own 2 pins red) |
| R5-D1-08 (`_plan_age_minutes` subtracts raw) | arm [straddle], plus #1299's own 3 pins | ok, blind (only #1299's own 3 pins red) |
| R5-helper (`_utc_age_seconds` raw) | the tracer check and all three arms, plus 8 instance pins | not measured at base (the tracer caught it at F1.1) |
| R2-D2-03 (`_utc_step_starts` wall) | the tracer check and all three arms, plus 4 instance pins | not measured at base (the tracer caught it at F1.1) |
| FIX-service-expiry (`services.py` back to `now + timedelta`) | the 20-hour pin, arm [tariff 15 min], arm [tariff 60 min] | n/a |
| FIX-build-cap (`build_override` cap back) | the 20-hour pin, the far-expiry pin, both tariff arms | n/a |
| FIX-step-end (`channel_pins` step end back) | the fold-step pin, both tariff arms | n/a |
| FIX-instants (`_instant` reads an aware stamp as wall clock) | the fold-step null control | n/a |

Mutation ledger: `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 4` at the head pinned the new sites (the `_instant` aware-stamp guard and naive return, two guards in `channel_pins`), 0 left unpinned, killed by `tests/manual_plan.py` and `tests/features.py`.

## Null control

The unmodified tree: main's 66 DST checks pass, and the tracer reads zero seams on the plain day in every arm (`NULL CONTROL arm [...]` lines). The new tests against main's production code (the arms' own control): 5 of 78 checks fail, and the override reads 21.0 h (autumn) and 19.0 h (spring), 20.0 h on the plain day.

## Figures

- Base: 66 DST checks pass, 16.8 s wall: `cd <git archive of 6793659c> && HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:tests:custom_components OPENBLAS_CORETYPE=Haswell python3 tests/dst_checks.py`
- Head `e26fa13b8af3359b633471f1ef0c7d220b97fc17`: 78 DST checks pass, 60.0 s wall on an idle runner, same command from the repo root. **Cost test correction:** the RCA estimated at most 20 s; measured, the three arm runs add about 43 s to a script that `tests/features.py` runs. At the RCA's roughly 380 runs a month that is about 4.4 h a month against about 119 h a month of P7 span, so it still passes; the estimate was low, not the verdict.
- New tests at base production: `python3 tests/dst_checks.py` from a tree of `origin/main`'s `custom_components` plus this head's `tests/dst_checks.py`: 5 of 78 fail (rc=1), `default override ... 20 true hours {'autumn': (21.0, 21.0), 'spring': (19.0, 19.0)}`.
- Seam enumerator (step 8): the tracer (arms above) is the runtime rule. Its static companion is the RCA's census, re-run as `rg -n --no-heading "\bnow (\+ timedelta|- self\._)" custom_components/heatpump_optimizer --glob "*.py"`: 12 hits at the base export, 10 at the head. The two it lost are the two override sites (closed in this diff). The 10 left, dispositions from a read of each function, inferred and not measured: wood_fuel `night_advice` and coordinator `_forecast_arrays` take only `.date()`; open_meteo `_should_refresh`, coordinator `_solar_forecast_view` operate on UTC stamps; power_guard `throttled` (10 s) and coordinator `simulate` (3 s) and `_write_frequency` (5 min) are rate limiters that misjudge only a call pair straddling a transition inside their window; coordinator `_update_snow_memory` compares against 2 days, a 1 h skew is 2 percent; coordinator `_on_meter_reading` (spacing 0 to 15 min) and pump_arbiter `_not_held` (5 min retry) misjudge one observation or one retry per transition. None is driven by an arm that straddles it, so none is closed here: they are the `barrier_gap` list in `tools/audit/bugclasses.json`.
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: `MODE: SCOPED -- 16 script(s) run, 12 scoped out`, 19 scripts passed, rc=0, run at `2ec138c5` (the last production and test change; the ledger commit above it adds only data files).
- Structure: `python3 tests/structure.py` passes, no budget moved.
- Typing: `python3 -m mypy --strict --follow-imports=skip --ignore-missing-imports custom_components/heatpump_optimizer/manual_plan.py`: `Found 6 errors` (all `[operator]`) on the file at `c05c635f`, `Success: no issues found` at the head.
- `node .claude/workflows/brief_lint.mjs` rc=0. `PYTHONPATH=tests/hastub python3 tests/ha_contract.py` passes against the stub (94 contracts). The real pinned HA (homeassistant 2026.9.3, Python 3.14.2 or later) could not be installed on the cloud seat (3.14.0rc2 is the newest offered), so the real-HA contract run is owed by the Mac or the nightly; the diff touches no stub symbol.

## Red checks

`typing` (the CI job running `typing_ruler --mypy`) was red at `c05c635f`: 6 `[operator]` errors in `manual_plan.py` against a recorded 0, because `_instant` returned `datetime | float` and `channel_pins` compared the union. Fixed at the head: `_instant` returns `float` on both branches (an aware stamp is epoch seconds, a naive one is read as UTC wall time, which keeps its order). The cheaper detector: `python3 -m mypy --strict --follow-imports=skip --ignore-missing-imports` on a changed production module reproduces the same 6 errors at `c05c635f` in seconds and reads 0 at the head, and it needs only mypy, not the pinned Home Assistant (2026.9.3 needs Python 3.14.2, which a cloud seat cannot install). Its standing cost is one command per changed module; it is not a gate, and the full count stays the `typing` job's. Whether `prepr.sh` should run it is a countermeasure decision for the orchestrator, not built here.

CI at the head has not run; the scoped gate, `brief_lint`, `structure.py` and the stub contracts pass locally.

## Forward-carry

The 10 census sites above and the same-zone wall compares the tracer does not judge (`build_override`'s `expires_ref > cap` and `_slots[-1][0] > cap`, and `ManualOverride.is_expired`) go to R9-F10.1d, named in `tools/audit/bugclasses.json` P7 `barrier_gap` (this diff), which lists the sites by file and function with the census command. Four of the 10 (pump_arbiter `_not_held`, coordinator `_on_meter_reading`, `_write_frequency`, `simulate`) read as rate-limit misfires once per transition; that reading is inferred, not measured.

## Friction

none
