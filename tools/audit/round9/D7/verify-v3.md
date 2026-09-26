# D7 round 9 — verifier V3 (reach and class)

Worktree /home/claude/wt, baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus the round-9 evidence commits (HEAD 6f51db2c). Python /home/claude/venv314 with PYTHONPATH=tests/hastub, thread pin set in every harness. My harnesses are under `tools/audit/round9/D7/verify-v3/`: `outline_reward.py`, `verdict_reach.py`, `sysid_cadence.py`, `derate_cycle.py` and `member_trace.py`. Votes are in `votes.json`. Every number below is a count or a ratio, so contention does not affect it. load1 ranged 0.50–2.71 and thread_factor 1.000–1.007 across the runs.

## Vote summary

| id | vote | severity | class | seam_rule enumerates |
|---|---|---|---|---|
| D7-s1-01 | verify | low | null (new) | partial |
| D7-s1-02 | weaken | medium → low | I1 | false |
| D7-s2-01 | verify | medium | null (new) | partial |
| D7-s2-02 | verify | medium | P2 | true |
| D7-s3-01 | verify | low | null (new) | partial |
| D7-s3-02 | verify | low | I4 | partial |

## D7-s1-01 — the ratchet does not price `_helper(self, ...)`
- **Finder's harness, re-run:** `inline__fold_flow_lift_cut_delta=8`, `rows_up=4`. The four rows are cross_seam_edges, cut_grid, cut_learning and internal_call_edges, and structure.py's own `ok` lines put all four at zero headroom. The perturbation arm `--helper _warm_seeded` gives cut_delta=0 (load1 2.71 and 2.65).
- **My measurement (`outline_reward.py`):** I made the refused move in the opposite direction. Of 108 eligible coordinator methods, outlining each into `_name(coord, ...)` lowers sum(cut_*)+cross_seam_edges for 83, by 513 in total. 24 methods are neutral, which is the null control: their bodies cross no seam. One rises (`_init_thermal_learning`, +19). load1 2.65.
  - Metric: over sync, undecorated methods called only as `self.<name>(`, the count whose outlining lowers sum(cut_*)+cross_seam_edges in `structure.measure()`, and the summed fall.
- **Reach:** instrument only. tests/structure.py runs in the gate, never in Home Assistant, and no hastub symbol is involved.
- **Consequence:** the budget pays for exactly the move `docs/HANDOVER.md:33` refuses. The `state_root_bindings` docstring shows the same hole was closed only for `self._ctx`.
- **Severity:** low holds.
- **Seam rule:** partial. `helper_escape.py` enumerates 11 helpers with 30 refs. It sees only plain-name callees, so it misses the module-attribute callees the class passes `self` to: boost.apply, boost.restore_session, pump_arbiter.apply/own/release, setpoint_check.evaluate and away.persist_override. It also misses transitive callees such as `setpoint_check._evaluate`. Package-wide, 52 module functions take `coord` as their first parameter, with 92 `coord.<attr>` loads.
- **Class:** no bugclasses.json class fits. I2 covers gate closure scope, not structure metrics.
- **Vote:** verify, low.

## D7-s1-02 — the drift and stress verdicts can be deleted with every runnable check green
- **Finder's harness, re-run** (`--only drift_leaf,drift,stress`): `survivors=2`. The drift mutant survived entities.py and features.py, and so did the stress mutant. The drift_leaf control was killed by entities.py ("and every one of those moves is still counted for the nightly"). load1 1.05.
- **My measurement (`verdict_reach.py`):** I traced the verdict lines themselves with sys.monitoring LINE events, with no mutation.
  - `env_drift.py:2452` and `stress.py:3664` executed 0 times under entities.py and 0 times under features.py.
  - The control line `_diff_leaves` (`elif a != b:`) executed 1622 times under entities.py.
  - The `--self-probe` perturbation moves both verdict counts from 0 to 1, so the tracer can see those lines.
  - Metric: the number of the two verdict lines that a runnable driver executes at least once.
- **Reach:** instrument only. The stress verdict sits inside stress.py's `if __name__ == '__main__'` block (lines 2736–4947) and the drift verdict inside `env_drift.main`, so no import can reach either.
- **Correction to the finder:** it calls `stress.scenario_budget` pinned, but that function's first body line executed 0 times under both drivers.
- **Severity, weakened from medium to low:**
  - No wrong value ships at baseline.
  - The edit that survives is a call-site deletion in `tests/env_drift.py` or `tests/stress.py`. Both are code-owned by @tvofi in `.github/CODEOWNERS`, which is a review barrier, not a check.
  - The more likely regression, one frame down in the comparator itself (drift_leaf), is killed.
- **Seam rule:** false. It is a hand-written list of four mutants, not an enumerator. An AST census finds 130 check or sys.exit verdict calls inside main() or `__main__` blocks across 19 tests/*.py scripts (89 in stress.py alone). No test can call any of them directly.
- **Class:** I1 confirmed.

## D7-s2-01 — the sysid fit takes one Euler step per 30-minute sample
- **Finder's harness, re-run:**
  - `continuous_presets_bias_gt5pct=3`, adopted=0. Biases on the 30-substep truth: light_new −0.16823, heavy_old −0.25461; typical_slab is refused.
  - `--substep-rollout`: 3 → 0 biased, adopted 0 → 2.
  - The sub1 null control reproduces bias 0.00000 for heavy_old and typical_slab.
- **My measurement (`sysid_cadence.py`):** the same production step driver, imported, run at every cadence the config flow allows, with the truth plant integrated at 1-minute steps.
  - Biased or refused, per cadence of 10/15/30/60/120 min: 0/0/3/3/3 presets (9 of 15).
  - Adopted: 2/0/0/0/0.
  - Under the finder's substep perturbation: 4 of 15 biased, 7 adopted. load1 2.14.
- **Reach in real HA:**
  - The sample interval is the coordinator's update interval: `DEFAULT_OPTIMIZATION_INTERVAL = 30` (const.py:1321), allowed range 10–120 (config_flow.py:1669). So the default setting and every longer cadence hit 3 of 3.
  - A real house is continuous, so the 30-substep truth is the realistic arm.
  - No divergent symbol from tests/ha_contract.py is on the path.
  - Sysid is opt-in (`DEFAULT_SYSID_ENABLED = False`) and is armed by the button.
- **Severity:** medium holds.
  - `adopted_biased=0`, so no wrong UA is adopted.
  - The consequence is an experiment that never adopts at the default cadence, plus a biased `heat_loss_kw_per_c` left in the published `system_identification` dict.
  - The workaround is a 10-minute cadence.
- **Seam rule:** partial. The sysid.py grep finds both roll sites (:284 and :627). It misses the passive house heat-loss learner, which rolls `simulate_step` over one sample at `dt_hours=dt_h`, up to `HOUSE_LOSS_MAX_SAMPLE_HOURS = 1.5` (coordinator.py:4271 and :4451). The property covers that learner; I did not measure its bias.
- **Class:** not P5, because the gate does refuse the biased fit. This is a new discretization mechanism.
- **Vote:** verify.

## D7-s2-02 — the derate fallback folds intervals that `_cop_fold_blocked` refuses
- **Finder's harness, re-run:**
  - `derate_ingests_distorted=3` of 3.
  - Factor after 24 intervals: 0.8738 for immersion and backup heater, 0.9769 for capacity_limited.
  - `--gate-derate`: 3 → 0, and the clean control still folds.
- **My measurement (`derate_cycle.py`):** full `_async_update_data` cycles, with the contamination delivered only as entity states. The harness sets no internal attribute.
  - Backup-heater arm: 25 of 25 folds happen while blocked.
  - The published factor at 2 °C with no humidity falls from 1.0 to 0.9422 after 26 cycles, with 7.5 kW metered against 6 kW commanded.
  - The real immersion detector latched in the flag-off arm too (24 blocked folds).
  - `--gate-derate`: 0 blocked folds.
  - The null control at a 6.0 kW meter gives 0 blocked folds in the off arm.
- **Reach:** real, through `pump_signals.read_electric_heat` and the coordinator's own immersion latch. No timing or executor dependence, and no divergent stub symbol on the path (HASTUB_TZ unset).
- **Severity:** medium holds. A wrong learned derate feeds the plan's COP. The cost is bounded: DERATE_ALPHA is 0.05 and the factor recovers on clean intervals.
- **Seam rule:** true. The coordinator.py grep (36 lines) reaches every learner that folds the meter ratio, because every meter read goes through `_measured_power`. The readers outside that file fold no learner: pump_arbiter.py:488 is a run verdict and accuracy.py:275 is the published power_ratio.
- **Class:** P2 confirmed.
- **Vote:** verify.

## D7-s3-01 — ten members no production code reaches
- **Finder's harnesses, re-run:** `reach.py` gives `dead_reachability_total=9`. `sentinel.py` gives 0 of 10 called from production, live controls 6 of 6, 12 update cycles.
- **My measurement (`member_trace.py`):** a sys.monitoring start event on each member's own code, split by the calling frame's file, over a whole driver run.
  - entities.py: 0 of 10 called from production, 0 called from tests, live controls 3 of 4.
  - features.py: 0 of 10 called from production, 7 of 10 called from tests (the pins), live controls 2 of 4.
  - `--perturb`: next_optimization production calls go 0 → 8.
- **Reach in real HA:** none of the ten names is on Home Assistant's read surface. Every production string of these names is a `coordinator.data` key (coordinator.py:7094–7096, sensor.py:779–799, climate.py:169). The dynamic getattr sites use other literals.
- **Severity:** low (hygiene) holds.
- **Seam rule:** partial. `reach.py --list` finds 9 of the 10; DefrostDerate.samples is hidden by the name collision, which the finder disclosed.
- **Class:** new; no class covers dead code.
- **Vote:** verify.

## D7-s3-02 — `dead_methods` reads 0 while members are dead
- **Finder's harness, re-run:** 0 at baseline; 5 with `--no-property-exclusion`; 1 with `--attribute-only`; 11 with both.
- **My check:** my runtime trace shows 0 production callers for all six members the screen hides.
- **Design attack:** structure.py:303–311 documents the property exclusion as the screen's deliberate boundary, and :405–414 calls the name screen coarse by choice. The rules act as written. The finding stands on consequence: no budgeted metric screens an unread property, and the budget reads 0 beside 6 dead members.
- **Severity:** low holds.
- **Seam rule:** partial. It lists 11: 9 are truly dead, and 2 are false positives. hvac_mode and preset_mode are read by real HA's ClimateEntity, but the hastub ClimateEntity never reads them (a holder in tests/ha_contract.py). It also misses DefrostDerate.samples.
- **Class:** I4 as the nearest fit.
- **Vote:** verify.
