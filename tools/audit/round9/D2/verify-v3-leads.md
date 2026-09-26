Box G3-V3, lens V3 (reach and class), dimension D2 (leads unit)
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, evidence commit 96b8916318513c3617254c3ce43b10570eb16307
Worktree /home/claude/ev2, machine: 4-vCPU Linux container (shared with other sub-seats), CPython 3.14 at /home/claude/venv/bin/python, PYTHONPATH=tests/hastub
Date 2026-09-26

=====================================================================
D2-s1-51 -- DHW setpoint sweep prices at the 5.0 degC ThermalState
default when no outdoor thermometer is mapped
=====================================================================

Method: re-ran tools/audit/round9/D2/leads/dhw_sweep_outdoor.py exactly as its
header commands, both arms; also wrote an independent check
(tools/audit/round9/D2/verify-v3-leads/v3_dhw_cop_direct.py) that calls
`ThermalModel.compute_cop_dhw` directly at the same two outdoor readings (5.0 default vs -15.0
forecast) on a representative 55C tank candidate, without ever calling `_dhw_setpoint_sweep`.

Number (mine, baseline arm):
  RESULT F-15: off=7 of_7 worst_rel_err=0.527
  RESULT F-5:  off=7 of_7 worst_rel_err=0.265
  RESULT F+5:  off=0 of_7 worst_rel_err=0.000
  RESULT off_total_cold=14 of_14
  load1=0.04, thread_factor=1.000
Exact bitwise match to the finder's record (14 of 14, worst 0.527/0.265, same_recommendation=1
in every cell). Perturbation (--forecast, the fix's own input) drives every cell to
off=0/worst_rel_err=0.000 -- confirmed, direction "to_zero" as claimed.

Independent check (v3_dhw_cop_direct.py, calling compute_cop_dhw directly, never touching
_dhw_setpoint_sweep): at outdoor 5.0C (default) vs -15.0C (forecast), a 55C tank candidate's COP
is 2.7930 vs 1.3230, a 111% relative difference -- confirms, by an entirely separate code path,
that pricing at the un-overwritten 5.0C default materially distorts the modelled COP the sweep's
cost is built from (the sweep's own blended cost_per_day error is smaller than this raw COP error
because standby loss is a COP-independent additive term, which is consistent with the sweep's
52.7% worst case being less than the 111% COP-only figure).

Attacks (verifier.md step 3):
- Contention: load1=0.04, thread_factor=1.000, this is a pure count (not a timing number), so
  contention is not a factor; the metric is exact and reproduced exactly.
- Gate mode: not a test-gap/mutation claim; N/A.
- Grid artefact: the claim covers all 7 candidates x 2 cold forecasts (14 cells); dropping any
  one forecast still leaves 7 of 7 off in the surviving one, so it is not an artefact of one cell.
- Null control: F+5=0 of 7 (forecast equals the constructor default) reproduces exactly; the
  finding is honest about when the bug is invisible.
- Reachable in real Home Assistant: yes, and not only through tests/hastub. The read path
  (coordinator.py:5318 `_update_current_state`, line 5348-5350: `outdoor = reader.read(...)`,
  `if outdoor.ok: ctx._current_state.outdoor_temperature = outdoor.value`) and the write path
  (coordinator.py:6835 `"dhw_advisor": self._dhw_setpoint_sweep()`, part of the coordinator's
  published data dict) are both plain production Python with no HA-stub-only branch. Nothing in
  tests/ha_contract.py records a stub/real divergence on `HomeAssistant.async_add_executor_job`
  or on sensor reads that would make this path stub-only; `_dhw_setpoint_sweep` and
  `_update_current_state` touch none of the divergent symbols in ha_contract.py's HOLDER/DIVERGENT
  tables. FakeHass's serialised (non-threaded) executor (tests/harness.py:168,
  `async def async_add_executor_job(self, func, *args): return func(*args)`) changes only which
  thread runs the call, not the arithmetic the sweep does -- irrelevant to this claim.
  Confirmed reachable in real HA.
- Severity by consequence: the recommended setpoint does not change (same_recommendation=1 in
  every cell, both arms) -- confirmed. The consequence is a wrong *displayed* cost_per_day
  (up to 52.7 % off), not a wrong decision. Low severity, as the finder gave, is the correct call.

seam_rule: `grep -n '_current_state.outdoor_temperature\|state.outdoor_temperature'
custom_components/heatpump_optimizer/*.py` -- I ran it: 25 hits in coordinator.py, 3 in
battery.py, 2 in pump_arbiter.py, 1 in topology.py (31 total). This is every read site of the
field the phenomenon concerns, not only `_dhw_setpoint_sweep`'s -- it enumerates the phenomenon's
seams (every consumer of the un-overwritten default), and coordinator.py's own docstring at
line 592-600 (`forecast_outdoor_now`) documents that the *plan* itself was moved off this exact
default in an earlier fix (#282) while the DHW advisor's sweep was not. seam_rule_enumerates:
true.

Class: class_guess P6 ("A consumer reads a key or field no producer writes, with a silent
fallback") confirmed. `ThermalState.outdoor_temperature` defaults to 5.0 and is only overwritten
by `_update_current_state` when an outdoor thermometer reads ok; `_dhw_setpoint_sweep` reads it
unconditionally. Textbook P6.

Metric definition (mine, identical to the finder's): candidates of the DHW setpoint sweep whose
published cost_per_day differs by more than 5% from the same sweep priced at
forecast_outdoor_now, at F in {-15, -5, 5} degC.

Vote: verify. Severity: low. Value: 14 of 14 (both cold forecasts).

=====================================================================
D2-s2-81 -- Two-zone comfort penalty halves each zone's floor price;
shipped plans sit up to 0.46 K below min_temp
=====================================================================

Method: re-ran tools/audit/round9/D2/leads/l4_zone_floor.py, both arms, on the stock two-zone
house across the full 12-cell grid (2 DHW x 6 price profiles), winter_cold, 24h; also wrote an
independent unit-level check (tools/audit/round9/D2/verify-v3-leads/v3_comfort_floor_unit.py)
that calls `_comfort_terms` directly with synthetic undershooting trajectories (no optimize()
solve at all) to isolate the L1 floor term's per-zone, per-step price in the two-zone vs
single-zone branch.

Number (mine, baseline arm) -- bitwise identical to the finder's:
  RESULT two_zone_floor_deg_steps_sum=2.4672 degree-steps
  RESULT two_zone_cells_breaching=2 of 12
  RESULT two_zone_floor_deg_steps_max=1.3144 degree-steps
  RESULT single_zone_floor_deg_steps_sum=0.1471 degree-steps (null arm)
  RESULT two_zone_flat_sum=0.0000
  load1=0.88-0.93, thread_factor=1.000
Perturbation (--perturb, _COMFORT_FLOOR_L1 2.0->4.0 in memory):
  RESULT two_zone_floor_deg_steps_sum=0.8574 degree-steps
Exact match to the finder's expected 2.4672 / 0.1471 / 0.8574. This is a deterministic count
(degree-steps summed from the solver's own returned trajectory), not a timing number, so exact
reproduction is the strong result here -- no BLAS-build tolerance was needed on this box.

Independent check (v3_comfort_floor_unit.py, calling _comfort_terms directly, no solve): at a
tiny undershoot (X=1e-4, where the quadratic term is negligible next to the linear L1 term), the
per-zone per-step L1 price in the two-zone branch is exactly half the single-zone branch's price
(5.0025 vs 10.0050, ratio 0.5000) -- confirms the 0.5x divisor on the L1 term by direct
construction, independent of running any full solve or grid.

Attacks (verifier.md step 3):
- Contention: irrelevant, this is a deterministic optimizer output, not a timing measurement.
- Grid artefact: 2 of 12 cells breach (both price cells that reward buying back the floor); the
  10 flat/uncontested cells are 0, exactly as the finder's null control states -- confirmed this
  is price-driven, not a grid-wide effect.
- Null control: single-zone (same house) floor breach is 0.1471, an order of magnitude below the
  two-zone 2.4672 -- confirmed the effect is two-zone-specific, not a general floor-pricing issue.
- Reachable in real Home Assistant: yes. `optimizer.py:HeatPumpOptimizer.optimize` and
  `_comfort_terms`/`_comfort_terms_batch` are pure numeric production code invoked on every real
  coordinator solve (this is the same `optimize()` the coordinator calls each update cycle);
  nothing here touches Home Assistant's API surface, so there is no stub-vs-real divergence to
  check in ha_contract.py -- the arithmetic runs identically in a real installation.
- Severity by consequence: shipped plans (not merely an internal candidate) sit up to 1.3144
  degree-steps (~0.46 K over one step, summed across the horizon) below the user's configured
  min_temp on the coldest cells -- a real, if modest, comfort-floor violation the user did not
  ask for and the constant's own comment says exists specifically to prevent. Medium, as the
  finder gave, is right: it is a real breach of a stated user guarantee, but bounded and confined
  to price-incentivized cold cells.

seam_rule: `grep -n "0.5 \* weight\|_COMFORT_FLOOR_L1" custom_components/heatpump_optimizer/optimizer.py`
-- I ran it: 6 hits (the constant's definition at line 230, both scalar and batched two-zone
sites using `0.5 * weight * (...)`, and both scalar and batched single-zone sites using the
undivided `_COMFORT_FLOOR_L1`). This is the complete set of formula sites the phenomenon depends
on -- both the affected sibling (two-zone, halved) and its unaffected twin (single-zone, whole) --
so it enumerates the phenomenon's seams, not only the demonstrated instance.
seam_rule_enumerates: true.

Class: class_guess P3 ("A capacity floor or divisor applied inconsistently across sibling
formulas") confirmed. The 0.5x zone-average divisor is applied to the L1 floor term exactly as it
is to the quadratic terms it was designed for (to avoid double-counting `comfort_weight`), but the
L1 floor constant was tuned as "the smallest L1 that removes residual floor violations" for the
*single-zone* (undivided) formula -- so the sibling two-zone formula silently halves a
floor-removal constant that was never re-derived for the halved case. Textbook P3.

Metric definition (mine, identical to the finder's): sum over steps and zones of
max(0, min_temp - T_zone) of the shipped trajectory, over 6 price profiles x DHW on/off at
winter_cold, 24h, stock two-zone house.

Vote: verify. Severity: medium. Value: 2.4672 degree-steps (2 of 12 cells breach, max 1.3144).

=====================================================================
D2-s4-81 -- sysid cannot adopt its own exact noise-free fit on 43 of 80
preset houses, yet arms on all 80
=====================================================================

Method: re-ran tools/audit/round9/D2/leads/l4_sysid_null_refusal.py, both arms, across all 80
preset cells (4 structures x 5 eras x 2 emitters x 2 pump sizes); also wrote an independent
unit-level check (tools/audit/round9/D2/verify-v3-leads/v3_sysid_gate_unit.py) that calls
`adoption_decision` directly with a synthetic, hand-built `SysIdResult` whose
`heat_loss_kw_per_c` is set EXACTLY equal to the declared UA (constructed zero bias, not fitted),
at varying interval widths -- independent of driving any preset's arm/step/_finish experiment at
all.

Number (mine, baseline arm) -- exact match to the finder's:
  RESULT cells=80
  RESULT null_refused=19
  RESULT null_admitted=37
  RESULT null_aborted=24
  RESULT unarmed=0
  load1=0.64-0.67, thread_factor=1.000
Perturbation (--perturb, UA_ADOPTION_HALFWIDTH_BAR ln(1.10)->ln(1.20)):
  RESULT null_refused=2
Exact match to the finder's expected 19/37/24/80 and the perturbed 2. This is a deterministic
admit/refuse/abort classification on an exact, noise-free fit -- not a timing number -- so exact
reproduction is the strong signal, and load1/thread_factor are reported only because the standing
rule asks for them beside every number; they carry no weight here since nothing is timed.

Independent check (v3_sysid_gate_unit.py, calling adoption_decision directly with a constructed
zero-bias result, no experiment driven at all): at hw=0.0477 and hw=0.0944 (both below the bar
0.0953) the gate admits; at hw=0.0963 and hw=0.1906 (both above) it refuses with
"heat-loss interval (...) is wider than the ... adoption bar" -- for a result whose
`heat_loss_kw_per_c` is set EXACTLY to the true declared UA (constructed zero error) in all four
calls. This independently confirms, by direct construction rather than by running any preset's
noisy drive, that admission is a pure function of the reported interval width and never consults
the fit's actual accuracy.

Attacks (verifier.md step 3):
- Contention: irrelevant to a deterministic count.
- Grid artefact: the refusals are structure-dependent (timber_crawlspace 8, timber_slab 4,
  concrete_slab 5, masonry 2 -- confirmed by re-running), so this is not one bad cell; dropping
  the worst structure (timber_crawlspace) still leaves 11 refused across the other three.
- Null control: 37 of 80 cells are admitted by the identical drive -- confirmed the mechanism can
  admit, so the 19 refusals are not an artefact of the drive itself being broken.
- Reachable in real Home Assistant: yes. `coordinator.py:10478` (`self._sysid.arm(...)`),
  `:10512` (`self._sysid.step(...)`) and `:10556` (`adoption_decision(result, params,
  self._sysid.config)`) are the real coordinator's own sysid wiring, driven from its update cycle,
  not test-only code. No HA-stub divergence applies -- this is pure numeric fitting/gating code
  with no Home Assistant API surface.
- Severity by consequence: 24 of 80 cells never even reach a completed fit ("fitted parameters
  outside plausible bounds") and a further 19 complete with a perfect, noise-free fit and are
  still refused adoption -- 43 of 80 (54%) of the preset structure/era/emitter/pump-size
  combinations the tree ships presets for can never adopt learning, in the best case the gate will
  ever see, while the coordinator arms (and presumably runs) the experiment on all 80 anyway. This
  is a systemic, not incidental, gap in a feature the tree advertises across its full preset
  matrix. Medium, as the finder gave, is defensible; I would not raise it higher without a
  measurement of how often real installations fall in the refused/aborted preset cells, which is
  out of this unit's scope.

seam_rule: `grep -n "UA_ADOPTION_HALFWIDTH_BAR\|plausible bounds\|def adoption_decision"
custom_components/heatpump_optimizer/sysid.py` -- I ran it: 10 hits, covering both mechanisms the
finding names as entangled (the halfwidth-bar gate at lines 472/862/1021/1022/1043, and the
plausibility-box abort at lines 752/757/1749/1822, plus the gate's own definition at 998). The
finding is explicit that it has not separated "true parameters outside the box" from "a fit that
misses them" -- the seam_rule's enumeration supports that: it surfaces every site of both
mechanisms rather than only the one the harness demonstrates, so a follow-up could attribute each
of the 24 aborts and 19 refusals to a specific site. seam_rule_enumerates: true.

Class: class_guess P5 ("A sysid/adoption gate keyed on a quantity other than the bias it gates")
confirmed. `slab_ua_adoption_halfwidth` is set by the window/prior design (profile-likelihood
width plus intercept-prior width in quadrature), not by the fit's achieved error -- at zero bias
and zero noise the fit error is exactly 0.0000 in every refused cell, yet the gate refuses on
width alone. Textbook P5, and the module's own docstrings (#1410, D7-01) confirm this was already
a known, named design choice rather than an accident -- which does not change the class, only that
it was made with eyes open.

Metric definition (mine, identical to the finder's): preset cells (4x5x2x2=80) whose
exact-plant, noise-free sysid drive completes and adoption_decision refuses.

Vote: verify. Severity: medium. Value: 19 of 80 refused (plus 24 of 80 aborted before a decision).
