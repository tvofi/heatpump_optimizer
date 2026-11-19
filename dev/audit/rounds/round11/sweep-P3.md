# Round 11 class sweep: P3

The P3 mechanism is "a capacity floor or divisor applied inconsistently across sibling formulas". The only finding in this class is D16-s2-04.

## Limits on this sweep
The sweep worktree could not be created because the disk was full: `git worktree add` failed with "No space left on device", and 166 MiB was free. Every read used `git show handoff/audit-r11-register:<path>`. Because of that, none of the controls below were run. The positive control, the null control and the perturbation are stated but unexecuted, and they are owed before this sweep can be called barriered.

## Enumerator
`git grep` over custom_components/heatpump_optimizer (const.py excluded) for these symbols: start_flow_min_lift_k, configured_flow_min_lift_k, FLOW_MIN_LIFT_K, modulation_floor_flow_c, runs.floor_kw, power_floor_kw, duty_floor_kw and min_electrical_power.
- Positive control (stated, not run): it must return pump_arbiter.py:950-952, the D16-s2-04 site.
- Null control (stated, not run): it must return zero on a fixture that has none of these symbols.
- Perturbation (stated, not run): adding one line that calls configured_flow_min_lift_k in place of start_flow_min_lift_k must add a hit.

## Dispositions
| seam | disposition |
|---|---|
| pump_arbiter.py:946-952, space floor_c (inlet + start_flow_min_lift_k) against the optimizer's booked floor runs.floor_kw(min_electrical_power) | **instance, finding site** (D16-s2-04). Probe: the finder's k_lift 30 harness, where the measured start draw of 0.602 kW is below the 1.0 kW booked. |
| optimizer.py:521, 539, 619 and 630, runs.floor_kw(p_min / min_electrical_power) | guarded: all four go through the single helper runs.floor_kw. |
| thermal_model.start_flow_min_lift_k / configured_flow_min_lift_k | guarded: start_flow_min_lift_k is the only lift reader for the floor write, and pump_arbiter is its only caller. |
| draw_range.power_floor_kw, accuracy.py:922 and 1077, coordinator.py:971 | not applicable: this is the evidence floor (0.8 x min_electrical_power), a different quantity. accuracy.py:1066 documents that it is distinct from duty_floor_kw. |
| pump_arbiter.py:881, _full_draw_c headroom against fixed FLOW_MIN_LIFT_K | not applicable: this is the top-draw headroom test, not a capacity floor. A configured lift does not change what commands the maximum draw. |
| optimizer duty_floor_kw → pump_arbiter.py:535-537 planned_draw_runs(modulation_floor=floor) | guarded: a single value is passed through from the plan result. |

The sweep found no instances beyond the finding.
