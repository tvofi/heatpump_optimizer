Design review: revise e23ace899802d0dbb2303231278ed3c360df8e3b architecture-unsound

Reviewed: `dev/programme/designs/R10-HEAT-METER.md` and `dev/programme/designs/R10-HEAT-METER-probes/` at `design/R10-HEAT-METER` e23ace899, round 2 of 3. The worktree was detached at that SHA, and the design ref has not moved. Code was read at 8a133f390 (#2753's head). Token count: not reported by this harness. Settled points are not reopened. The orchestrator's rulings under mandate 6329234399 are taken as given:
- a combination mode gets #2753's rule;
- the mode entity is optional;
- the re-anchor is earned;
- #2698 is carried to R10-RATIO-ANCHOR.

## Round-1 points

1. **Closed.** Per the ruling, the selector semantics are stated, a combination mode, a last-good reading and an unobserved mode all take #2753's rule, and the refusal is gone.
2. **Closed for bias.** I read `fixed_span_probe.py`/`.out`. Acceptance keys on an independent figure, so the quantised value is not selected. The new span mechanics are defective (points A and B below).
3. **Closed.** `_settle_interval_diag` is in scope, on the ledger's split.
4. **Closed.** `attribution()` plus `space_heat_kw`, `cop_duty` and `dhw_share` live in `heat_energy.py`, and the five coordinator sites pass their plan split and compute nothing. One rule inside it is wrong (point C).
5. **Closed.** The `config_flow` golden claim is named. All five `tests/golden/coord_*.json` files hold mode `"Unknown"` once each (`grep`), as the note says.

## Revise points

A. **architecture-unsound: the span counts cycles, not time** (note, "Counter rule" and "Span-aligned learners"). The note sets `K = floor(HOUSE_LOSS_MAX_SAMPLE_HOURS / interval_h)`, which is 3 at the default, so a span lasts exactly 1.5 h on paper. But:
   - `HOUSE_LOSS_MAX_SAMPLE_HOURS = 1.5` (coordinator.py:1362), and the learner refuses `dt_h > HOUSE_LOSS_MAX_SAMPLE_HOURS` (:5387) with a strict comparison.
   - Home Assistant schedules the next refresh only after a refresh ends: `next_refresh = int(loop.time()) + self._microsecond + update_interval` (`homeassistant/helpers/update_coordinator.py:276`, venv-ha). Three cycles therefore last 90 min plus three solve times.
   - So every span on a counter install is refused.
   - An event-driven refresh adds cycles, which shortens a K-cycle span.
   - "`dt_h` equals `span_h` by construction" is therefore false.
   **Fix wanted:**
   - Close the span on elapsed time measured between read instants, with a target strictly inside `[HOUSE_LOSS_MIN_SAMPLE_HOURS, HOUSE_LOSS_MAX_SAMPLE_HOURS]`. For example, close at the first read whose elapsed time reaches `MAX - interval_h`, and refuse a span past `MAX`.
   - Divide by the measured elapsed time.
   - Add a test with a jittered cadence and an extra event-driven cycle.
B. **architecture-unsound: the house learners on a span lack the per-cycle gates** (note, "Span-aligned learners"). The AND of the per-cycle gates is stated for the COP fold only. `_async_learn_house_heat_loss` (coordinator.py:5319 onwards) does three things that a span-close sample changes:
   - it judges `replay_freeze`, stale sensors, boost and ventilation at the current cycle only;
   - it snapshots every cycle (:5359-5362);
   - its ventilation detector "needs the residual to see the window close" (:5367-5372).
   On a span, a frozen or boosted middle cycle would be folded. **Fix wanted:**
   - Apply the same per-cycle AND to the house and lower-floor learners: one gated cycle refuses the span.
   - Either keep the ventilation detector's residual at cycle cadence, or state and test its change of cadence.
C. **architecture-unsound: a point sample is time-split** (note, `space_heat_kw`). The observed arm returns `heat_kw * space_frac` for every source. A thermal-kW source "stays per cycle", as a point sample taken at the read. In a `heat` → `DHW` interval that read is hot-water heat, and the product books half of it as space heat. A dwell fraction applies only to energy integrated over the same window. **Fix wanted:**
   - Time-split only a counter span.
   - For a point source, the observed arm returns `heat_kw` only when `dhw_frac == 0`, and otherwise `None`.
   - Add a test with a `heat` → `DHW` interval on a thermal-kW install.
D. **architecture-unsound: the store migration is unneeded and harmful** (note, "Re-anchor" and "Hot files"). The learner store's `_async_migrate_func` (store.py:716-737) is the base hook, which migrates nothing. Bumping the store's version would mean:
   - a subclass override;
   - the `tests/finite_boundary.py` sweep refuses a version above 1 without one (#1740);
   - a major mismatch on downgrade starts the loader afresh, which wipes all learned state.
   An earned flag needs none of this. The existing `house_heat_loss_basis` field (store.py:326) already persists the basis. Write the earned basis there and change its `unread` text from "re-derived from the configured meters" to "earned at the first measured-heat fold". Alternatively, add an optional key with a `Domain` default. **Fix wanted:** remove "the store's versioned migration". `store.py` stays in `files` for the `Domain` text only.

## Checked and holding

- **Hold on #2753.** The note now states it, together with step 9's revalidation. decision: orchestrator, already ruled.
- **Size.** L against #2753's head holds after A-D: each fix is a rule inside files the note already lists.
- **Attribution has one owner** (`attribution()`). The plan arm is bit-identical to today at every site, because each site passes its own split.
- **Earned re-anchor.** Running the void path at the first fold that used measured heat is consistent with `heat_loss_basis_voids` and `reanchor_heat_loss` at confidence 0. The carry `dr1-basis-mix` correctly records the mixed-basis residue.
- **Files growth.** Of the other groups listing the added files, only R10-ARCH-SHAPES and R10-UX-HEALTH are not done. This is unchanged from round 1.
