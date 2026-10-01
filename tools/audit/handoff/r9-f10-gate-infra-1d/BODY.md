<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: F10.1c made the manual override last its stated length in true time, but ten raw wall-clock sites it listed in the P7 `barrier_gap` were never measured. Across the autumn fold, two stamps that share Home Assistant's one ZoneInfo subtract and compare as wall clock, so a limiter that should let a call through a true hour later saw a wall zero and kept blocking.

After: each of the ten sites, plus `build_override`'s two compares F10.1c's review named, is measured with a fold straddle (02:55 on 2026-10-25, a true hour apart, a wall zero apart). Eleven sites misfired and now read true elapsed time through `utc_elapsed_seconds`, `utc_shift` or `_instant`; the rest measured clean and are recorded as such in `barrier_gap`.

Closes #1756's carry (the 10 raw sites). No issue is closed by this PR beyond what F10.1c's body named.

What changed: `power_guard.throttled`, `open_meteo._should_refresh`, `pump_arbiter` (`_not_held` retry stamp, the `_write` retry gate, the `hold` echo grace), `coordinator` (`_update_snow_memory` decay and heavy-snow hold, `async_simulate`'s limiter, `_on_power_event`'s sample spacing, `_command_frequency`'s write limiter), and `manual_plan` (`build_override`'s expiry-in-the-future and expiry-cap compares, `ManualOverride.is_expired`). Measured clean, unchanged: `_forecast_arrays` and `night_advice` (calendar dates only), `_solar_forecast_view` (`dt_util.utcnow`), and `build_override`'s slot-start compare (`parse_channel` returns fixed-offset stamps, so it already orders instants).

How: new section "rate limiters, retry stamps and manual-plan compares across the fold (round-9 F10.1d)" in `tests/dst_checks.py`, 14 checks, each driving the real production seam at a fold stamp pair, with a plain-day null control where the seam takes a plain pair. No new files, no budget moved.

## Head

`e8cef66b5cde41501964773983b6ab39ed863bee` (code head: fix, checks, `barrier_gap` text and mutation ledger; this transport commit sits above it).

## Mutation proof

Instrument: `python3 tests/mutation_table.py --pin-killed --base origin/main --timeout 3500` at the head. The four old `killed_by` pins named lines this change rewrote and were removed; the run pinned the eight sites the diff now owns, each killed: `coordinator.py:6751` CLAMP_DROP (tests/features.py), `manual_plan.py:171` RETURN_DEL, `:291` GUARD_OFF (tests/manual_plan.py), `:301` GUARD_OFF (tests/features.py), `power_guard.py:86` RETURN_DEL (tests/structure.py, the cheapest killer), `pump_arbiter.py:502` GUARD_OFF (tests/structure.py), `:548` BOOLOP and GUARD_OFF (tests/features.py). Null control `coordinator.py:607` NULL_COMMENT survived every driver. Every baseline driver was green, including `tests/features.py` (1237 s here; it timed out at the default 1200 s on the first run, so `--timeout 3500` was passed).

The new checks go red when the fix is reverted: see Null control.

## Null control

The unmodified tree (a `git archive` of `787fe137`, `custom_components` and `tests` at main) with this head's `tests/dst_checks.py`: 11 of 92 checks fail, every one a fold-hour check (throttle, weather refresh, arbiter retry 65.0 true minutes where 5.0 are meant, snow decay 10.0 where 9.59 is meant, what-if limiter `{'rate_limited': True}`, meter fold `dt_hours` None where 1/6 is meant, frequency write 0 where 1 is meant, expiry clamp 20.75 h where 20.0 is meant, `is_expired` at 02:45 CEST, and the expiry-in-the-future refusal). The four plain-day null controls pass there and at the head. At the head, all 92 pass.

## Figures

- Fold checks at the head: `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components python3 tests/dst_checks.py`: `ALL 92 DST / QUARTER-GRID CHECKS PASSED` (78 at main, 14 new).
- Same command on the main tree plus this head's `tests/dst_checks.py`: `11 of 92 DST / QUARTER-GRID CHECKS FAILED`.
- Structure: `python3 tests/structure.py` passes, no budget moved.
- Brief lint: `node .claude/workflows/brief_lint.mjs` ends `CARRY ok`; its only ERROR lines are the pinned malformed-carry fixtures.
- Pre-PR: `tools/audit/prepr.sh` at the code head's parent chain ran every step it could and printed no failure (closures step skipped: the diff cannot be scoped, so CI re-records).
- Typing: `python3 -m mypy --strict --follow-imports=silent --ignore-missing-imports` on `power_guard.py` and `open_meteo.py`: `Success: no issues found` at the head and at main. With `--follow-imports=skip` both report one `no-any-return` that main does not, because `utc_elapsed_seconds` is then `Any`; the real run follows imports. Unrun here: `typing_ruler.py --mypy` against the pinned toolchain and `tests/ha_contract.py` against the real pinned HA (no Python 3.14.2 in this container); the Mac runs both.

## Red checks

none at the head. CI has not run on it; the scoped gate was not run end to end here (`prepr.sh` and the mutation drivers' baselines, which include `features.py`, `entities.py`, `env_drift.py`, `finite_boundary.py`, were green at the code head).

## Forward-carry

none. Every site the census listed is either fixed or recorded as measured clean in `tools/audit/bugclasses.json` P7 `barrier_gap`.

## Friction

none.
