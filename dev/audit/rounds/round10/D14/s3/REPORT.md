# D14-s3 — recurring bug classes, nightly-replay axis (round 10)

Baseline 17f1c55fad1b. Box B7 (macOS arm64, shared; load1 20-112 during the run).
Every number below is a count (contention-immune); no timing claim is made.

## Method
- M1: read `dev/audit/config/bugclasses.json`. Open production classes: P8, P10,
  N-name-sort, N-step-grid, N-reap-lock, N-staleness.
- M2: picked P8 (6 rounds, 8 instances), P10 (6 rounds, 7 instances) and
  N-staleness (R9, whose detector_idea is replay-shaped). The axis is the
  nightly replay (`tests/replay.py`), so each detector drives the real
  coordinator cycle through `replay.run_fixture` and reads what `replay.sweep`
  reads off every published entity.
- M3: two detectors committed here; P10 already has a replay detector+barrier
  (`tests/replay.py:kernel_checks`, run by `tests/entities.py`), re-run as a non-finding.
- M4/M5: one finding per class with a live seam, barrier proposed below.

## Findings

### D14-s3-01 (P8, medium, bug): the plan narrative names the instance currency over feed-denominated money
`coordinator.py:_narrative_view` passes `resolve_currency(hass)` (instance) to
`narrative.render`, while every other money surface uses `coordinator.currency`
(feed-declared since #1657). `narrative.py:render`'s docstring says the two "are
the same decision"; since #1657 they are not.
- Command: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/p8_replay_currency.py`
- base (EUR/kWh feed, SEK instance): 14 money seams, **1 mismatched**:
  `sensor.heat_pump_optimizer_plan_narrative attr.lines[]` says SEK.
- clean (EUR feed, EUR instance): 0. narrative_fixed (render handed coordinator.currency): 0.
- reintroduce (`coordinator.declared_currency -> None`): 14/14.
- Pre-fix commit 82667c41a^ (5dfa6684f, before #1657's F1.8): base 14/14 mismatched,
  narrative_fixed 14 — the detector re-finds R9 D14-s2-02/#1657 at its pre-fix tree.
- Property: every published money label (unit, `currency` attribute, rendered text)
  names `coordinator.currency`. Rule: the harness's seam walk (every ISO code in any
  published unit/state/attribute string on a EUR-feed/SEK-instance replay).
- Barrier: add the EUR-feed/SEK-instance arm as a replay invariant `currency`
  (per-cycle, cheap: 6 cycles ≈ 15 s on this box, provisional) in `tests/replay.py`,
  with the reintroduce arm as its control; plus a grep-class lint refusing
  `resolve_currency(` in coordinator/sensor outside `_feed_currency` fallbacks.
  Config-flow uses (`config_flow.py:553,3736-3796`) label user-entered money and are a
  separate, arguable seam (lead).

### D14-s3-02 (N-staleness, medium, bug): a report-on-change heat-pump power meter is declared stale 39 of 48 cycles
`const.INPUT_MAX_AGE_MINUTES[CONF_POWER_ENTITY] = 30` (and mode select 60) is shorter
than a push-on-change source's legitimate quiet interval (power holds 0 W for
hours while the pump is idle; a select changes only when the mode does).
- Command: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/staleness_on_change.py`
  (output kept in `staleness_on_change.out`).
- polling day (clean fixture): 0 stale cycles.
- report-on-change twin per input: heat_pump_power_entity 39/48 stale cycles, and
  `measured_power` + `compressor_starts` unavailable on 39 cycles each (78 entity-cycles)
  that are available on the polling day; heat_pump_mode_entity 47/48 stale (no entity
  goes unavailable; downstream mode-fallback consequence not measured);
  indoor/dhw (360 min) and outdoor (180 min): 0.
- Perturbation: `const.INPUT_MAX_AGE_MINUTES[key] = 1e9` drops each seam to 0.
- Seams listed: 2 (heat_pump_power_entity, heat_pump_mode_entity) of 5 guarded inputs
  the fixture carries.
- Limitation: at the R9 instance's pre-fix tree (3e9f1878b^, indoor/dhw limit 60) the
  detector does NOT re-find D1-s5-51 (indoor 0 stale): the synthetic day's indoor
  probe changes every ~10 min, so its on-change twin has no >60 min gap. The detector's
  reach is bounded by the fixture's quiet intervals (`staleness_on_change.prefix.out`).
- Barrier: an `on_change` replay arm in `tests/replay.py` that rewrites each input as
  its report-on-change twin and requires no newly-unavailable entity; plus a quiet
  synthetic fixture (a still room overnight) so quiet-store limits are exercised.
  Power: key staleness on a liveness signal, not the value's age, as pump_signals does.

## Non-findings
- P10: `python3 tests/replay.py --kernels base` → worker 9277, loop 0, executor 0 over 6
  cycles. Already barriered by `tests/entities.py` → `replay.kernel_checks`; the ledger
  still says `open` (lead).

## Harnesses
- `p8_replay_currency.py` (+ `.out`), `staleness_on_change.py` (+ `.out`, `.prefix.out`).

## Unfinished
- N-name-sort, N-step-grid, N-reap-lock not picked (M2 picks 2-3).
- N-staleness: the mode-select seam's downstream effect (MODE_LAST_GOOD 180 min →
  full capability on a DHW-only pump) not measured; fixture lacks quiet store gaps.

## Exposure
Read `dev/audit/config/bugclasses.json` (P8, P10, N-staleness entries and the class
list) and git history: `git log` of `currency.py` (F1.8 commits 82667c41a, 7cccba3a7,
e76686d2d, f12c00b91) and `git log -S QUIET_STORE_MAX_AGE_MINUTES` (3e9f1878b); ran the
harnesses in detached worktrees at 82667c41a^ and 3e9f1878b^ (removed afterwards).
No gh, no registers.
