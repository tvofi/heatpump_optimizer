Design review: approve 21f4fbfe972378044e366d62c13559ec491d08db

Reviewed: `git diff e23ace899 7cbb7031f`, which is the note plus `dev/programme/designs/R10-HEAT-METER-probes/time_span_probe.py`/`.out`. This is round 3 of 3, from a detached worktree at 7cbb7031f. The verdict covers **21f4fbfe9**, the orchestrator-ordered amendment on top of 7cbb7031f. `git diff 7cbb7031f 21f4fbfe9` touches only the note, 3+/3-, in three spots: the re-anchor's `unread` wording, the `files` list re-admitting `store.py` for that string only, and the decision note recorded as ruled. Nothing else moved. Code was read at 8a133f390. Settled points are not reopened. Token count: not reported by this harness.

## Round-2 points

- **A, closed.** The span now closes on elapsed time between read instants: at `elapsed_h >= max(MIN, MAX - interval_h - 0.05)`, and a span past `MAX` is refused with the learner's own strict comparison (coordinator.py:5387). In `time_span_probe.py`, the cadence is the interval plus the solve time, following Home Assistant's `_schedule_refresh`, and an event-driven refresh resets the schedule. With the allowance, the time rule accepts 20000 of 20000 spans in all six rows (solve times 2.5, 25 and 120 s; event rate 0 and 0.05), with `dt_h` from 0.950 to 1.483.
  - **The null moves:** the K = 3 cycle rule accepts 0 spans at an event rate of 0 at every solve time, and 2269-2783 with events.
  - **Without the allowance:** the time rule refuses 2, 27 and 128 spans.
  - The probe is a model of the cadence, not the owner's bundle; the note hands that re-measurement to the fixer.
- **B, closed.** Each learner's per-cycle gate block (freeze over `_learning_frozen`, boost, `vent_only`, a `None` `_interval_space_power`, and the min/max `dt_h`) is ANDed into its own `span_clean` flag.
  - The ventilation detector keeps its per-cycle replay.
  - The "which path folds" rule means no window is counted twice: the per-cycle fold runs until the basis is earned, and only the span fold runs after.
  - Tests and mutation targets for all three are named.
- **C, closed.** `space_heat_kw(heat_kw, a, integrated)` time-splits only a counter span's mean. A point source on an observed interval returns `heat_kw` only when `dhw_frac == 0`, and otherwise `None`. The test for a `heat` → `DHW` interval on a thermal-kW install is named.
- **D, closed.** There is no version bump and no migration. The earned basis is written to the existing `house_heat_loss_basis` choice field, and a missing value reads as not earned. At 21f4fbfe9 the note re-admits `store.py` for the one `unread` string, as the orchestrator ruled.

## Notes for the fixer (carries)

- `_heat_loss_anchors` runs on every save. It must read the learner's in-memory earned state, not the stored dict, which exists only at load. Otherwise a save can write `metered` over an earned basis, and the next load voids the scale again. Test it with a save, a reload and a save after earning. Carry: R10-HEAT-METER (item dr3-earned-in-memory)
- The close threshold at the 30 min default is 0.95 h, so a span is about 2 cycles, not 3. The probe's 0.6 kW refusal row and the resolution bound in `fixed_span_probe.py` used K = 3 (1.5 h). Re-measure the bound at the time-closed span, for example 1.5 kW with an integer counter over 1.0 h, so `q/expected` is about 0.67 > EPS 0.5 and the span is refused. State which loads the counter can serve at the default. Carry: R10-HEAT-METER (item dr3-eps-at-span)
