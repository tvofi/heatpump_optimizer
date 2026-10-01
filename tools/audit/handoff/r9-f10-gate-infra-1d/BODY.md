<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: F10.1c made the manual override last its stated length in true time, but ten raw wall-clock sites it listed in the P7 `barrier_gap` were never measured. Across the autumn fold, two stamps that share Home Assistant's one ZoneInfo subtract and compare as wall clock, so a limiter that should let a call through a true hour later saw a wall zero and kept blocking.

After: each of the ten census sites, plus `build_override`'s compares F10.1c's review named, is measured with a fold straddle (02:55 on 2026-10-25, a true hour apart, a wall zero apart). The ones that misfire now read true elapsed time through `utc_elapsed_seconds`, `utc_shift` or `_instant`; the rest measured clean. The census rule turned out narrower than the class: a widened rule finds 14 more misfiring sites (probed, not fixed here), which `barrier_gap` lists and gives to R9-F10.1e, so P7 stays open.

Completes the carry F10.1c left in its barrier_gap (#1756, already closed): the 10 raw sites.

What changed: `power_guard.throttled`, `pump_arbiter` (`_not_held` retry stamp, the `_write` retry gate, the `hold` echo grace), `coordinator` (`_update_snow_memory` decay and heavy-snow hold, `async_simulate`'s limiter, `_on_power_event`'s sample spacing, `_command_frequency`'s write limiter), and `manual_plan` (`build_override`'s expiry-in-the-future and expiry-cap compares, `ManualOverride.is_expired`). Measured clean, unchanged: `_forecast_arrays` and `night_advice` (calendar dates only), `_solar_forecast_view` (`dt_util.utcnow`), `open_meteo._should_refresh` (its one production caller passes `dt_util.utcnow`; my first edit to it broke `tests/open_meteo.py` and is reverted), and `build_override`'s slot-start compare (`parse_channel` returns fixed-offset stamps, so it already orders instants).

How: new section "rate limiters, retry stamps and manual-plan compares across the fold (round-9 F10.1d)" in `tests/dst_checks.py`, a dozen checks plus null controls, each driving the real production seam at a fold stamp pair, with a plain-day null control where the seam takes a plain pair. No new files, no budget moved.

## Head

`CODEHEAD` (code head: fix, checks, `barrier_gap` text and mutation ledger; transport commits sit above it).

## Mutation proof

Round 1 of the review found three rewritten sites no check pinned. Each now has a fold check, and the one-line revert of each to main's wall-clock form turns `tests/dst_checks.py` red (the other 95 pass):
- `pump_arbiter.hold`, `(now - at).total_seconds() < ECHO_GRACE_S`: red on "a pump write read back a true 60 s later across the fold is past its 20 s echo grace".
- `pump_arbiter._write`, `now < held.retry[slot]`: red on "a pump write retry stamped 5 true minutes after a 02:58 CEST failure still holds at 02:58 CEST".
- `coordinator._update_snow_memory`, `(now - self._last_heavy_snow).total_seconds() < (`: red on "the roof-snow hold has lapsed 2 days 30 true minutes after the last heavy fall".
- `power_guard.throttled` back to `(now - self._last_event).total_seconds()`: red on the fold-hour throttle check and on the new spring-gap check ("a meter event a true 5 s after the last is throttled").

The mutation ledger (`python3 tests/mutation_table.py --pin-killed --base origin/main --timeout 3500`) pins the sites the diff owns as killed; the first run at the round-1 head pinned eight, killed by tests/features.py, tests/manual_plan.py and tests/structure.py, with every baseline driver green. The null control `coordinator.py:607` NULL_COMMENT survived every driver. At this head the same command reports `nothing to pin`.

## Null control

The unmodified tree (a `git archive` of `787fe137` with this branch's `tests/dst_checks.py`): every fold-hour check for a fixed site fails and the plain-day null controls pass. At the head all of `tests/dst_checks.py` passes.

## Figures

- Fold checks: `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components python3 tests/dst_checks.py` prints `ALL 96 DST / QUARTER-GRID CHECKS PASSED` at the head (78 at main).
- Structure: `python3 tests/structure.py` passes, no budget moved.
- Brief lint: `node .claude/workflows/brief_lint.mjs` ends `CARRY ok`; its only ERROR lines are the pinned malformed-carry fixtures.
- The census-missed sites: probes and the table are in the shared folder at `audit-r9/fix/evidence/1809-f10-1e-probes/` (README.md lists each site, its verdict and its one-line fix); the widened rule is `census.rx` beside them and is quoted in `barrier_gap`.
- Typing: `python3 -m mypy --strict --follow-imports=silent --ignore-missing-imports` on `power_guard.py`: `Success: no issues found` at the head and at main. Unrun here: `typing_ruler.py --mypy` against the pinned toolchain and `tests/ha_contract.py` against the real pinned HA (no Python 3.14.2 in this container); the Mac runs both.

## Red checks

`fast (3.14)` was red at `e8cef66b`: `tests/open_meteo.py` loads `open_meteo.py` with a stub that has no `homeassistant.util`, and my new `from .accuracy import utc_elapsed_seconds` imports `homeassistant.util`, so the module failed to import. Root cause: I changed a site that cannot misfire (`_should_refresh`'s one production caller passes `dt_util.utcnow`), and ran `prepr.sh` and the mutation drivers but not `tests/open_meteo.py`, which is in the closure of the file I changed. Fixed by reverting `open_meteo.py` to main's. Cheaper detector: the scoped gate or the one script `python3 tests/open_meteo.py` (under a second), an existing check that sat in none of my local paths; no new countermeasure is worth building, since `prepr.sh`'s scoped step names the scripts a diff reaches and I did not run them. At this head I ran the scoped gate (see Figures when it finishes).

## Forward-carry

`tools/audit/bugclasses.json` P7 `barrier_gap` names R9-F10.1e as owner of the 14 misfiring census-missed sites, with probes and fixes in the shared folder above. The Mac adds that roster group.

## Friction

none.
