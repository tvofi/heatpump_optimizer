Builds outside pull request #3437 (Bankaifan, accepted into round 10; its commit is adopted with the author's authorship, its tool-attribution trailers dropped). A failed price fetch in `_fetch_tibber_prices` always raised `UpdateFailed`, so every entity went unavailable and the optimizer stopped steering, though the last fetched prices still covered the current step. Now, while `_known_prices_for` still returns a price for the current plan step, the failure is a WARNING plus the `price_feed_stale` repair and the update carries on; once no published price covers now, the update fails as before (D10-07) and the repair stays until a fetch succeeds. A refused token always fails and raises no repair. Closes nothing.

Design, against the alternatives:
- `issues.note_price_outage` owns the outage's logging and the repair, and returns whether planning goes on; the coordinator passes the post-increment outage count and the covering prices. The author's version stored `bridged` in the coordinator and passed `not cycles`: two counted statements, `coord_footprint` 2497 -> 2499, inadmissible under `score.py`. Returning the verdict pays both.
- The coverage decision stays a coordinator read (`_known_prices_for`), not a copy in `issues.py`: no price concept duplicated, and `issues.py` keeps no price import (its leaf contract).
- `price_model.py`, which owns `pull_prices`, was refused as the home: it imports no `homeassistant`, and a repair call there would add the issue registry to a model module (fixer step 17).
- The recovery clear runs inside the latch's own branch (`if self._tibber_outage_cycles:`), not on every healthy cycle as the author's did; the repair is not persistent, so no restart leaves one behind.
- Corrected claims: `_fetch_tibber_prices`'s and `_tibber_fetch_failed`'s docstrings and the update loop's comment said every failed fetch raises; they now state the coverage condition. `README.md`'s repair-notice list gains the new notice (`doc_claims.py` refused it with no home). The strings.json/en text, de and sv say the same four things: no new prices (with the error), planning goes on on the last published prices covering now, unavailable once they run out, clears on a successful fetch.

## Head

`311ee9f3fa20ebcb2de65e873cd0c889481a0360`. Production code, tests and the gate run were measured at `65b6d1ba3beab46ded68cce918cd2fa30426e157`; the one commit after it, `311ee9f3fa`, only deletes the stale pin and adds the seven ledger pins under `tests/mutation_ledger/` (`git diff --stat 65b6d1ba3b 311ee9f3fa`). Measured against `origin/main` `86953c6d99ecf7aa86c7bc9d57fec9a991daad07` at 2026-11-11T06:39Z. `git merge-tree --write-tree origin/main HEAD` against `a7628041dc` reports no conflict.

## Mutation proof

`PYTHONPATH=tests/hastub python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'python3 tests/features.py' --in-place`, in a detached worktree at the head (the `--copy-tree` default killed NULL on the #363 `recorded_at` check, as fixer step 2 records). Each mutant, `name: file: old -> new`:

- `M1_bridge_off`: `issues.py`: `    bridged = bool(covering)` -> `    bridged = False`
- `M2_auth_bridged`: `coordinator.py`: `not auth and self._known_prices_for(` -> `self._known_prices_for(`
- `M3_always_raise`: `coordinator.py`: `        if not issues.note_price_outage(` -> `        if True or not issues.note_price_outage(`
- `M4_coverage_not_now`: `coordinator.py`: `self._known_prices_for([plan_step_start(dt_util.now())])` -> `self._known_prices_for([plan_step_start(dt_util.now()) + timedelta(hours=12)])`
- `M5_no_clear_on_recovery`: `coordinator.py`: `            issues.clear_issue(self.hass, "price_feed_stale")` -> `            pass`
- `M6_no_repair`: `issues.py`: `    if bridged:  # once raised` -> `    if False:  # once raised`
- `M7_bridged_logs_error`: `issues.py`: `    elif bridged:\n        _LOGGER.warning(` -> `    elif False:\n        _LOGGER.warning(`
- `M8_first_cycle_debug`: `issues.py`: `    if cycles > 1:` -> `    if cycles > 0:`

```
# batch 1 (M1-M8 spec; stopped by the seat's 30-min background limit after M2, files restored by mutant_guard)
SURVIVED NULL
KILLED M1_bridge_off
KILLED M2_auth_bridged
# batch 2 (M3-M5), worktree detached at 65b6d1ba3b
SURVIVED NULL
KILLED M3_always_raise
KILLED M4_coverage_not_now
KILLED M5_no_clear_on_recovery
# batch 3 (M6-M8), worktree detached at 65b6d1ba3b
SURVIVED NULL
KILLED M6_no_repair
KILLED M7_bridged_logs_error
KILLED M8_first_cycle_debug
```

Failing test first: the author's two checks, applied alone to a `git archive` of `origin/main` `86953c6d99`, fail there:

```
  FAIL a failed price fetch while the last prices still cover now does not fail the update  [raised UpdateFailed('Unexpected error fetching prices: no HTTP session available in the test stub'), cycles 1]
  FAIL …and raises the price_feed_stale repair  [issues []]
```

The head's version of the test at the same base: the three bridge checks fail (`a failed price fetch while the last prices still cover now does not fail the update`, `...and raises the price_feed_stale repair, logging a WARNING and no ERROR`, `null control: prices that no longer cover now fail the update again, and the repair stays` on its repair half), and the healthy-fetch, no-covering-prices and refused-token null controls pass.

## Null control

At the head, `tests/features.py`:
- `null control: a healthy price fetch neither fails the update nor raises the price_feed_stale repair` — ok (also ok at the base).
- `null control: prices that no longer cover now fail the update again, and the repair stays` — ok: `UpdateFailed`, as at the base.
- `null control: an outage with no covering prices logs ERROR on its first cycle and raises no repair` — ok (also ok at the base).
- `null control: a refused token fails the update although prices still cover now, and raises no price_feed_stale repair` — ok (also ok at the base); `M2_auth_bridged` is its perturbation.
- The NULL mutant survives the same command (above).

## Figures

- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` at the head prints `MODE: SCOPED`, every script it runs passing, exit 0.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `dS +0.0000 NULL` at the head; at `b22ca9298a`, before the payment, it read `WORSENS (inadmissible: coord_footprint 2497->2499)`.
- Structure: `python3 tests/structure.py` passes; `class_excess_loc` and `max_class_loc` are recorded down (commits `43b81fb56a`, `d560522ddd` name the rows). `coordinator.py` shrinks against main: `git diff --stat origin/main...HEAD -- custom_components/heatpump_optimizer/coordinator.py`.
- Seam census, failure signalling of the update loop's fetches. Rule: `grep -n "await self._fetch_[a-z_]*()" custom_components/heatpump_optimizer/coordinator.py` enumerates the three fetchers both refresh paths call. Dispositions: `_fetch_tibber_prices` — closed in this diff; `_fetch_weather_forecast` — already guarded: `_weather_fetch_failed` has no raise and the held forecast is kept; `_fetch_solar_forecast` — already guarded: `OpenMeteoSolar.async_refresh` catches every exception ("never break the update cycle"). Null control: the same command at `origin/main` enumerates the same three, and `_fetch_tibber_prices` there is the one whose failure raises.
- Translations: `cmp custom_components/heatpump_optimizer/strings.json custom_components/heatpump_optimizer/translations/en.json` is silent; each of de, en, sv carries the `{error}` placeholder in `price_feed_stale`'s description.

## Unpinned sites

Each site `prepr.sh` step 6d listed is pinned by `python3 tests/mutation_table.py --pin-killed --base 86953c6d99ecf7aa86c7bc9d57fec9a991daad07 --jobs 3` at this head (`PIN KILLED: 7 pinned, 0 left unpinned`), each killed by `tests/features.py`; the stale `_tibber_fetch_failed GUARD_OFF 53f8da35` pin on the moved `if auth:` line is deleted by hand:

- `custom_components/heatpump_optimizer/coordinator.py:6967 BOOLOP` — pinned (also the named mutant `M2_auth_bridged`)
- `custom_components/heatpump_optimizer/coordinator.py:6968 GUARD_OFF` — pinned
- `custom_components/heatpump_optimizer/issues.py:81 CMP_BOUND` — pinned (also `M8_first_cycle_debug`)
- `custom_components/heatpump_optimizer/issues.py:81 GUARD_OFF` — pinned
- `custom_components/heatpump_optimizer/issues.py:83 GUARD_OFF` — pinned (also `M7_bridged_logs_error`)
- `custom_components/heatpump_optimizer/issues.py:87 GUARD_OFF` — pinned (also `M6_no_repair`)
- `custom_components/heatpump_optimizer/issues.py:89 RETURN_DEL` — pinned

## Red checks

none

## Forward-carry

none

## Friction

none
