# Round 9 judge (Phase C)

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1). Judge seat on the strongest model; runners R1 (haiku) and the judge's own box.
Contract: tools/audit/briefs/judge.md; brief /mnt/project-files/audit-r9/judge/J.md.

## Result

156 registered findings; 1 killed at the panel (D1-s2-01, three refutes on real-HA reach); 7 merged by dedup (DEDUP.md); **148 canonical findings judged**.

| verdict | count |
|---|---|
| verified | 119 |
| weakened | 26 |
| refuted | 3 |
| unreproduced | 0 |

Survivors (145) by severity: critical 0, high 6, medium 66, low 73.

## Exceptions and rules applied this round

- **Unanimous findings not re-run (tvofi decision 2026-09-26T13:39Z, round 9 only, "Contested only").** The 94 unanimous non-D3 findings in JUDGE-INPUT-B.json are judged on the three verifier reproductions. Batch A (JUDGE-INPUT.json, 46: split, disputed, verifier-flagged and provisional-timing) was measured.
- **D3 (tvofi 2026-09-26T11:37Z and 13:41Z).** No heavy D3 re-runs: no pre-screen, pool, full gate or quiet window. Each D3 finding at medium or above got one light sanity check (mutant applied in memory or in a temp package copy, production symbol called); lows rest on the recorded evidence and the votes. Quiet window not run (tvofi rule). Checks: D3-CHECKS.md. All 9 reproduce their behaviour change, every null and identity control holds.
- **Interpreter.** R1 ran CPython 3.11.15, not 3.14 (runner-1.md). Every solver-float and timing row of R1 that was void, empty, flagged or off was re-run by the judge on CPython 3.14.0rc2 (numpy 2.4.6, scipy 1.17.1, OpenBLAS 1 thread). R2 stalled on 3.11 and was stopped; the judge ran shard 2/2 itself on 3.14: its 8 solver/timing rows by hand and the other 15 through judge_batch.py (label judge-r9-j2, rows-j2.json).
- **Provisional CPU numbers** (J.md step 4): D9-s1-01..04, D9-s1-71, D9-s2-01, D9-s2-02, D9-s2-71 and D1-s2-05 re-taken on a quiet box (load1 0.3-1.3, thread_factor ~1.00). None falls inside its null band.
- **Browser rows.** D4-s1-02 and D4-s1-05 need a Playwright lane that neither box had (rc=1); both rest on the verifiers' reproductions (V1/V2/V3 counts in the notes).
- **Live GitHub API rows** (D11-s1-01, D11-s1-04) and the mutation-pool row (D7-s1-02) are by-hand echo rows; they rest on committed snapshots and the verifiers.
- **Severity** by COMMON.md item 7: a wrong published value is high; a defect with a workaround or bounded cost is medium; hygiene is low. Where verifiers split on severity alone, the judge sides with the measured consequence and records why.

## Classes and RCA

A class owes root-cause remediation (`rca: true`) when it has N >= 3 surviving instances this round, or when it already has a barrier. The barriered class is "user state not surviving restart" (RC2, merged). Refuted findings do not count.

| class | N | rca | findings |
|---|---|---|---|
| P2 | 27 | **yes** | D1-s2-51, D1-s2-91, D1-s3-01, D1-s3-02, D1-s4-02, D1-s5-01, D1-s5-03, D1-s5-52, D2-s1-02, D2-s2-01, D2-s2-03, D2-s3-01, D2-s4-02, D4-s2-06, D7-s1-71, D7-s2-02, D8-s1-02, D8-s1-03, D8-s2-02, D8-s2-03, D8-s3-61, D10-s1-01, D10-s1-02, D12-s2-01, D12-s2-02, D12-s3-01, D14-s2-01 |
| I5 | 19 | **yes** | D4-s2-09, D5-s1-01, D5-s1-02, D5-s1-03, D5-s1-05, D5-s2-01, D5-s2-02, D5-s2-03, D5-s2-51, D6-s1-01, D6-s1-02, D6-s1-03, D6-s2-01, D6-s2-02, D6-s2-03, D6-s2-04, D6-s2-05, D8-s3-02, D11-s2-04 |
| I1 | 11 | **yes** | D3-s1-01, D3-s1-91, D3-s2-01, D3-s2-02, D3-s3-01, D3-s3-02, D3-s3-03, D3-s3-04, D3-s3-05, D7-s1-02, D14-s5-02 |
| P1 | 9 | **yes** | D1-s1-01, D1-s1-02, D1-s2-03, D1-s3-03, D1-s3-06, D1-s4-01, D1-s4-03, D1-s5-02, D14-s1-01 |
| I3 | 7 | **yes** | D11-s1-01, D11-s1-02, D11-s1-03, D11-s1-04, D11-s2-01, D11-s2-02, D13-s1-03 |
| P11 | 6 | **yes** | D1-s1-51, D1-s1-52, D1-s2-71, D6-s1-81, D10-s1-03, D14-s4-02 |
| I4 | 5 | **yes** | D7-s3-02, D11-s1-71, D11-s1-72, D13-s1-01, D14-s2-03 |
| P6 | 5 | **yes** | D2-s1-51, D4-s2-01, D10-s2-01, D12-s1-01, D14-s1-02 |
| P9 | 4 | **yes** | D4-s1-01, D4-s1-02, D4-s1-03, D4-s1-05 |
| new: avoidable interpreter-bound recomputation in the solve | 4 | **yes** | D9-s1-01, D9-s1-02, D9-s1-04, D9-s1-71 |
| P3 | 3 | **yes** | D2-s2-81, D12-s2-03, D14-s3-01 |
| P5 | 3 | **yes** | D2-s4-01, D2-s4-81, D14-s3-03 |
| new: CPU gate blind to a regression outside its sampled work | 3 | **yes** | D9-s2-02, D9-s2-03, D9-s2-71 |
| P8 | 2 | no | D12-s3-81, D14-s2-02 |
| new: CPU work inline on the event loop | 2 | no | D9-s1-03, D9-s2-01 |
| new: live input with no physical-plausibility bound | 2 | no | D1-s1-03, D1-s2-02 |
| new: persisted future instant trusted without bound | 2 | no | D1-s1-04, D1-s3-05 |
| new: production member reached by no production code | 2 | no | D7-s3-01, D7-s3-72 |
| new: user state not surviving restart | 2 | **yes** | D1-s2-52, D1-s2-53 |
| I2 | 1 | no | D14-s5-01 |
| P4 | 1 | no | D0-s2-02 |
| P7 | 1 | no | D14-s4-01 |
| new: a sign floor on a price margin breaks the stated piecewise identity | 1 | no | D2-s3-02 |
| new: an approval bound to an exact head is re-bought on a diff-identical move | 1 | no | D13-s1-02 |
| new: an entity family whose names do not lead with a shared token splits under the name sort | 1 | no | D8-s3-01 |
| new: compatibility duplicate entity enabled by default | 1 | no | D8-s3-03 |
| new: error-translating try opened after the call it should cover | 1 | no | D1-s2-55 |
| new: explicit-Euler stability judged per store instead of on the coupled step matrix | 1 | no | D2-s1-01 |
| new: fit integrator differs from the simulated plant | 1 | no | D7-s2-01 |
| new: learned-correction clamp sized against an assumed range, not the model's curve | 1 | no | D2-s2-02 |
| new: markdown the renderer misplaces | 1 | no | D5-s1-04 |
| new: missing icons.json services block | 1 | no | D4-s2-08 |
| new: persistent failure swallowed at DEBUG | 1 | no | D1-s2-04 |
| new: pointer-only editing with no keyboard route | 1 | no | D4-s1-04 |
| new: return inside finally | 1 | no | D7-s3-51 |
| new: selector minimum off its own step grid | 1 | no | D4-s2-05 |
| new: series resolution inferred from the minimum gap | 1 | no | D1-s5-04 |
| new: service input without an upper-bound clamp | 1 | no | D1-s2-54 |
| new: shutdown reap waits on the lock a solve holds | 1 | no | D1-s2-05 |
| new: solve-scoped mutation of shared live config seen by a concurrent reader | 1 | no | D1-s3-04 |
| new: staleness limit shorter than a report-on-change sensor's quiet interval | 1 | no | D1-s5-51 |
| new: state-blind menu re-offers a completed path | 1 | no | D4-s2-07 |
| new: structure metric blind to a code shape | 1 | no | D7-s1-01 |
| new: text producer takes no language parameter | 1 | no | D4-s2-81 |
| new: translation leaf double-escaped | 1 | no | D4-s2-03 |
| new: whole-entity availability gated on an optional input | 1 | no | D8-s2-01 |

Class corrections taken from the verifiers (NOTES.md): D1-s2-51, D1-s2-91, D1-s5-52 -> P2 (G1-V3); D2-s1-02, D2-s4-02 -> P2 (G3-V3); D14-s4-02 -> P11 with P7 the class it hides (G3-V3); D4-s1-03 -> P9. Corrections not taken are explained on the finding. G1-V2's side observation (boost.restore raises TypeError on a naive stored 'until' under the real HA clock) is folded into D3-s1-91's class (I1) for the Phase D sweep and is not registered.

## Per-finding verdicts

`verdict` is the judge's; `finder` is the finder's severity; merged ids were deduplicated into the canonical (DEDUP.md).

### D0

- **D0-s1-01**: refuted, low, class P4, bug; panel disputed, batch A, finder low. The two-zone 0.20x deep anchor is built only in _optimize_space_only; the DHW path's _solve_space never gets it
  - null control fails (V2): the flat-price twin carries 0.2342 % max / 0.0468 % mean against the winter 0.2507 % / 0.0215 %, and a placebo seed of similar energy drops other cells as much (b025 0.2842 %), so the metric measures seed-count/basin sensitivity, not the missing anchor; the finder's own arm raises the energy bill 1.58 SEK. The code asymmetry (optimizer.py:3463-3482 vs 3994-4016) is real hygiene, carried to the P4 fixer's brief, not a finding
- **D0-s2-01**: refuted, low, class P4, bug; panel disputed, batch A, finder low. L-BFGS-B ftol=1e-6 stops the solve and its in-loop restart short of their own fixed point
  - reach: OptimizationConfig.horizon_hours is never set from config (24 h; n_steps=min(len(prices),96)), so the 48 h headline is off the shipped path (V1, V2, V3 agree); at 24 h the only cell over 0.1 % that closes is one|shoulder|winter_cold, the recorded _CERT_CLAIMS cell whose tighter stop rule was refused on money (#1293), and the next (0.0078 units) raises the bill. A re-find of a recorded refusal. Not merged into D14-s3-02
- **D0-s2-02**: verified, low, class P4, bug; panel split, batch A, finder low. Multi-start seed set misses lower basins on shoulder prices, above the flat-price null
  - stop_rule_class hygiene. V3: excess over the flat twin 0.88 pp on the headline cell; closing it spends +1.00 SEK/day there and -3.81 SEK/day summed over 16 cells. The remedy the claims name (the production anchor ladder) is the #1294 refusal on cost, so the fixer owes a cheaper seed or a recorded refusal
### D1

- **D1-s1-01**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. A tz-naive persisted timestamp raises on every cycle at three sibling loader seams (snapshots, curve, comfort)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s1-02**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. A non-numeric snapshot temperature_bias makes best_restore raise and suppresses the accuracy_drift issue for good
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s1-03**: verified, medium, class new: live input with no physical-plausibility bound, bug; panel unanimous, batch B, finder medium. One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); same mechanism as D1-s2-02
- **D1-s1-04**: verified, low, class new: persisted future instant trusted without bound, bug; panel unanimous, batch B, finder low. A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D1-s3-05
- **D1-s1-51**: verified, low, class P11, bug; panel unanimous, batch B, finder low. hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G1-V2 on real HA 2026.2.3: 7/9 divergent
- **D1-s1-52**: verified, low, class P11, bug; panel unanimous, batch B, finder low. hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G1-V2 on real HA: 4/8 divergent
- **D1-s2-02**: verified, medium, class new: live input with no physical-plausibility bound, bug; panel unanimous, batch B, finder medium. Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s2-03**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. A sample count past 2**64 in the thermal-learning store fails every cycle, across restarts
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s2-04**: verified, medium, class new: persistent failure swallowed at DEBUG, bug; panel unanimous, batch B, finder medium. Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s2-05**: verified, medium, class new: shutdown reap waits on the lock a solve holds, bug; panel unanimous, batch A, finder medium. Home Assistant stop waits out an in-flight solve before reaping the solve worker
  - judge 3.14 re-take (load1 0.99): stop_latency_ratio 0.869 (min 0.775, max 0.904; finder 0.928, tolerance 0.1); --perturb unlocked_reap 0.015
- **D1-s2-51**: weakened(medium), medium, class P2, bug; panel unanimous, batch B, finder medium. A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G3-V3 class correction to P2 taken. Scope narrowed: the arbiter half is verified on real stored state (G1-V2, 4/4); the quiet-period half is unreachable from real state in 11 rig variants and rests only on the finder's injection, so it is not part of the verified claim
- **D1-s2-52**: verified, medium, class new: user state not surviving restart, bug; panel unanimous, batch B, finder medium. Five store writers do not wait for the startup read: a save in that window replaces persisted learned state
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); severity conflict settled at medium: on a real HA 2026.2.3 Store G1-V2 measured the loss in 2/30 race cells (it needs semaphore contention); the 5/5 behind G1-V3's high rests on a 0.2 s stub delay. G1-V3's P2 correction is the mechanism; the finding is classed under the barriered restart class because what is lost is persisted learned state across a restart
- **D1-s2-53**: verified, medium, class new: user state not surviving restart, bug; panel unanimous, batch B, finder medium. set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); restart loses 24 of 26 set_thermal_parameters fields
- **D1-s2-54** (merged: D6-s1-04): verified, low, class new: service input without an upper-bound clamp, bug; panel unanimous, batch B, finder low. apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps unenforced
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); merged D6-s1-04
- **D1-s2-55**: verified, medium, class new: error-translating try opened after the call it should cover, bug; panel unanimous, batch B, finder medium. A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s2-71**: verified, low, class P11, bug; panel unanimous, batch B, finder low. hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G1-V2 on real HA: 6/18 divergent
- **D1-s2-91**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. FlowCurveBias.observe raise aborts the cycle's accuracy pipeline and fails the whole update
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G1-V3 class correction to P2 taken; sibling of D1-s2-51 (same fence missing), not merged: a different call site whose fence is fixed separately
- **D1-s3-01**: verified, high, class P2, bug; panel unanimous, batch B, finder high. A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s3-02**: weakened(medium), medium, class P2, bug; panel split, batch A, finder high. Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump
  - V2: leaks in 1 of 31 unload offsets (only k=0, the event dispatched in the same loop step as the unload's non-yielding segment); the consequence when it happens is high (a released coordinator writes the pump every minute until restart), the trigger a sub-iteration window
- **D1-s3-03**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s3-04**: weakened(low), low, class new: solve-scoped mutation of shared live config seen by a concurrent reader, bug; panel split, batch A, finder medium. Climate entity publishes the away setback as the user's target while the solve is in the executor
  - V3 on real HA: real refreshes serialise (0 mid-solve writes); the value is visible only via the default-off peak-guard path during a >=20 s solve, and lasts until the refresh-end write
- **D1-s3-05**: weakened(low), low, class new: persisted future instant trusted without bound, bug; panel split, batch A, finder medium. Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound
  - V2: the overrun equals the backward clock step exactly (0/1/10/60/1440 min); the steps a Pi takes are forward or seconds-to-minutes; the boost is user-toggled and visible. Sibling D1-s1-04
- **D1-s3-06**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s4-01**: weakened(low), low, class P1, bug; panel split, batch A, finder medium. DefrostDerate.from_dict admits non-finite/out-of-range duty; the bucket pins at DERATE_MIN and never recovers
  - all three weaken: QuarantiningStore scrubs non-finite leaves, so the non-finite pin does not reach real HA (it takes the D1-s4-03 reset path); finite out-of-range cells survive but no writer produces them and they recover in 85-6932 folds
- **D1-s4-02**: verified, medium, class P2, bug; panel split, batch A, finder medium. A failed solve is returned as a plan with status 'failed (...)', so the coordinator counts it a success
  - V2's reach arm fences the non-finite-input trigger before the optimizer (0 of 3), leaving a solver/code exception as the trigger; the repair notice and an honest last-success stamp are lost on every such cycle, a defect with a workaround (ERROR log, status 'failed')
- **D1-s4-03**: verified, low, class P1, bug; panel unanimous, batch B, finder low. One unreadable cell in a v2 defrost store voids all 12 measured buckets and is labelled a pre-v5.3.0 upgrade
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s5-01**: verified, medium, class P2, bug; panel split, batch A, finder medium. inputs.age_of ignores last_reported and accepts future stamps, diverging from InputReader's freshness rule
  - V1's weaken (degrades to the fail-safe no-sensor fallback) not taken: two verifiers hold medium and the degradation is silent on a live sensor
- **D1-s5-02**: verified, medium, class P1, bug; panel split, batch A, finder medium. Learner-store loaders check finiteness but not the domain their own update path enforces (price shape, peak tracker)
  - V2's weaken not taken: the mechanism reaches real HA through QuarantiningStore (15/34 bad tail at load, silent); a corrupted store is the D1 dimension's own scenario
- **D1-s5-03**: weakened(low), low, class P2, bug; panel split, batch A, finder low. One huge JSON integer drops a whole price fetch (entity and Tibber) or Open-Meteo refresh instead of one row
  - V3 on real HA over real HTTP: orjson rejects 10**400 before the parser runs, so the Tibber and Open-Meteo seams are unreachable; the entity seam remains, reachable only through another integration's Python int above 1e308
- **D1-s5-04**: verified, low, class new: series resolution inferred from the minimum gap, bug; panel unanimous, batch B, finder low. One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D1-s5-51**: verified, medium, class new: staleness limit shorter than a report-on-change sensor's quiet interval, bug; panel unanimous, batch B, finder medium. A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D1-s5-01
- **D1-s5-52**: verified, high, class P2, bug; panel unanimous, batch B, finder medium. InputReader has no plausibility window: -127 and 85 degC sentinels deliver as ok readings
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G1-V3 class correction to P2 taken (_dhw_inlet_c carries a -5..35 guard, the sibling temperature paths do not); raised to high on G1-V3's measurement under COMMON.md item 7 (a wrong published value is high): a -127.0 sentinel is published as an available reading
### D2

- **D2-s1-01**: verified, medium, class new: explicit-Euler stability judged per store instead of on the coupled step matrix, bug; panel split, batch A, finder medium. Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge
  - V2's weaken not taken on severity: the divergence to 1e35 K is a wrong published value; reach is a typed config with a store mass below 1 kWh/K, which V2 finds implausible and records (0 of 902 plausible-mass samples escape)
- **D2-s1-02**: verified, low, class P2, bug; panel unanimous, batch B, finder low. DHW refill coil debits the wood tank the full coil heat but spares the DHW tank only its scaled share
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G3-V3 correction to P2 taken
- **D2-s1-51**: verified, low, class P6, bug; panel unanimous, batch B, finder low. DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D2-s2-01**: weakened(medium), medium, class P2, bug; panel split, batch A, finder high. Settlement caps (slab_settlement_cap, hold_demand_kw) ignore the learned house_heat_loss_scale the dynamics apply
  - V3: at learned scales 0.7-1.3 the savings error is at most 1.5 % and its sign varies; the headline figures need s=3 or 0.3. The seam rule misses coordinator.py:3647-3656 _space_demand_kw and the battery-view consumer coordinator.py:10601
- **D2-s2-02**: verified, medium, class new: learned-correction clamp sized against an assumed range, not the model's curve, bug; panel unanimous, batch B, finder medium. #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37%
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D2-s2-03**: verified, low, class P2, bug; panel split, batch A, finder low. DHW-path savings settle-up replays space schedule without the DHW coil: end state differs from published trajectory
  - perturbation replaced by G3-V1's coil-off arm (the finder's was tautological). V3: the 0.48 overstatement's sign depends on the counterfactual (two-sided accounting gives a 2.1-2.6 understatement); the identity breach is exact. The fixer must also cover the baseline_end sibling (:3987/:6194)
- **D2-s2-81**: verified, medium, class P3, bug; panel unanimous, batch B, finder medium. Two-zone comfort penalty halves each zone's floor price; shipped plans sit up to 0.46 K below min_temp
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D2-s3-01** (merged: D8-s1-01): verified, high, class P2, bug; panel unanimous, batch B, finder high. _current_spot_price reads a quarter up to 45 min stale under 15-minute price entries
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); merged D8-s1-01 (judge cross-run: D8 wrong_quarters 95 -> 0 under D2's perturbation)
- **D2-s3-02**: weakened(low), low, class new: a sign floor on a price margin breaks the stated piecewise identity, bug; panel split, batch A, finder medium. PV piecewise cost clipped by import_margin's zero floor wherever import price < export price
  - V2 and V3: no measured money or comfort loss (floored minus unfloored plan <= 0.08/day either sign); published predicted_cost understated up to 0.61/day on negative-price days
- **D2-s4-01**: weakened(low), low, class P5, bug; panel split, batch A, finder medium. sysid adoption interval misses the true UA on 14 of 22 fits it admits; admitted fits biased high
  - V3, inverse crime: the finder's plant is sysid's own rollout model at the same Euler step; against a 1-minute-substep plant the gate admits 0 of 144 noisy runs, so 14/22 is not reached in real HA for these presets. The fine-plant fit bias is D7-s2-01
- **D2-s4-02**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. sysid step sized to exactly the abort bound: sensor noise aborts 100 of 294 experiments, light_new 81 of 96
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G3-V3 correction to P2 taken
- **D2-s4-81**: verified, medium, class P5, bug; panel unanimous, batch B, finder medium. sysid cannot adopt its own exact noise-free fit on 43 of 80 preset houses, yet arms on all 80
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
### D3

- **D3-s1-01**: verified, low, class I1, hygiene; panel unanimous, batch D3 sanity (judge, by hand), finder low. No closure script fails when _dhw_inlet_c's lower plausibility bound moves (-5.0 <= value -> -5.0 < value)
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): behaviour.py C0043 behaviour_delta=1, --null 0
- **D3-s1-91**: verified, medium, class I1, bug; panel unanimous, batch B, finder medium. coordinator.py tzinfo guards (:8112, :8384) are dead under the gate's naive clock; unblinded they crash
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); judge re-ran lc_tz_probe_coordinator.py: 8384 differs 0 with HASTUB_TZ unset, 1 under Europe/Stockholm. G1-V2's side observation (boost.restore TypeError on a naive stored 'until' under the real HA clock) is folded into this class for the Phase D sweep, not registered
- **D3-s2-01**: weakened(low), low, class I1, bug; panel split, batch D3 sanity (judge, by hand), finder medium. Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): witness.py S05 1/3 corrupt payloads diverge, S17 12/288 and S18 3/288 zero-priced steps, M31 6/6 non-inert restores (orig arms 0). Weakened to low on G1-V2: through QuarantiningStore only M31 (flow_lift.py:210) stays reachable, 1 of 4 sites
- **D3-s2-02**: verified, low, class I1, bug; panel unanimous, batch D3 sanity (judge, by hand), finder low. PriceShapeModel residual_var restore can discard every stored variance with the gate green
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): witness.py S19 non-zero sigma 96/96 orig, 0/96 mutant
- **D3-s3-01**: verified, medium, class I1, bug; panel unanimous, batch D3 sanity (judge, by hand), finder medium. Every gate driver runs with process local time = UTC, so open_meteo's naive-stamp UTC guard is deletable
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): distinguish.py M02 differs=1 under TZ=Europe/Stockholm, 0 under --tz=UTC, 0 under --identity
- **D3-s3-02**: verified, medium, class I1, bug; panel unanimous, batch D3 sanity (judge, by hand), finder medium. DrawStats.from_dict can zero the open draw occurrence and no gate check notices
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): distinguish.py M19 1.5 -> 0.0 kWh, --identity 0
- **D3-s3-03**: verified, medium, class I1, bug; panel unanimous, batch D3 sanity (judge, by hand), finder medium. MonthlyLedger.add's non-finite guard is unpinned; one NaN amount loses the month on reload
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): distinguish.py M21 months kept 1 -> 0 (kwh nan), --identity 0
- **D3-s3-04**: verified, medium, class I1, bug; panel unanimous, batch D3 sanity (judge, by hand), finder medium. No gate check observes a positive draw folded by DhwProfileLearner.async_fold_draw_stats
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): distinguish.py M24 0.0 -> 0.4396 kWh folded, --identity 0
- **D3-s3-05**: verified, low, class I1, hygiene; panel unanimous, batch D3 sanity (judge, by hand), finder low. The disinfection write-failed notice memo is unpinned
  - judge D3 sanity check reproduces (mutant in memory, production symbol called); survival rests on the recorded pre-screen; quiet window not run (tvofi rule): distinguish.py M20 0 -> 5 deletes, --identity 0
### D4

- **D4-s1-01**: verified, medium, class P9, bug; panel unanimous, batch B, finder medium. Status text coloured by HA's --success/--error/--warning-color fails WCAG AA on the default themes
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s1-02**: weakened(low), low, class P9, bug; panel split, batch A, finder medium. Lane slot menu is placed at the tap point unclamped; near the right edge it spills past its chart and the viewport
  - V3 by real taps: 2 of 36 openings spill (18.2 px past the chart, 0.0 px past the viewport); the finder's state came from a direct openMenu call; the menu stays operable and on screen
- **D4-s1-03**: verified, medium, class P9, bug; panel unanimous, batch B, finder medium. Setup picker: two identically named sensors render as identical options at 375 and 768 px
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G2-V3 class P9 taken over the finder's new
- **D4-s1-04**: verified, medium, class new: pointer-only editing with no keyboard route, bug; panel unanimous, batch B, finder medium. Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s1-05**: weakened(medium), medium, class P9, bug; panel split, batch A, finder high. Now-marker label prints over the measured-now reading on the live default view
  - all three weaken: the collision is the word 'now' over 'now', the reading 21.1 C stays legible, no value is hidden (V1, V2 medium; V3 low)
- **D4-s2-01**: verified, medium, class P6, bug; panel unanimous, batch B, finder medium. Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s2-03**: verified, medium, class new: translation leaf double-escaped, bug; panel split, batch A, finder medium. The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv)
  - V3's weaken to low (validation-only text) not taken: 9 Swedish leaves show a literal escape to the user
- **D4-s2-05**: verified, low, class new: selector minimum off its own step grid, bug; panel unanimous, batch B, finder low. 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s2-06**: verified, low, class P2, bug; panel unanimous, batch B, finder low. The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s2-07**: verified, low, class new: state-blind menu re-offers a completed path, bug; panel unanimous, batch B, finder low. After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s2-08**: verified, low, class new: missing icons.json services block, hygiene; panel unanimous, batch B, finder low. None of the 12 registered services has an icon in icons.json
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D4-s2-09**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m²
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); judge classes it I5 (help text drifts from the selector it sits beside) rather than a one-instance new class
- **D4-s2-81**: verified, medium, class new: text producer takes no language parameter, bug; panel unanimous, batch B, finder medium. Setup overview page and setup diagram publish English slot text on a Swedish install
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
### D5

- **D5-s1-01**: verified, medium, class I5, bug; panel unanimous, batch B, finder medium. configuration.md 'Initial setup' documents the pre-v6.6.5 flow: no finish menu, Tibber token required, 74 entities
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); siblings D6-s2-01, D6-s2-02
- **D5-s1-02**: verified, medium, class I5, bug; panel unanimous, batch B, finder medium. setup.md Quick setup promises buffer storage and two-tank physics that the quick-setup answers cannot produce
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D5-s1-03**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. dashboard-card.md says the card version lags the integration; the stamp keeps them equal every release
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D5-s1-04**: verified, low, class new: markdown the renderer misplaces, hygiene; panel unanimous, batch B, finder low. configuration.md has 9 lines a GFM renderer misplaces: 3 table rows as pipe text, 6 prose lines as rows
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D5-s1-05**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. Docs name 5 option fields by labels the options forms do not show
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D6-s1-02
- **D5-s2-01**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. Card comments cite 12 private members the card no longer has (17 mentions)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D5-s2-02**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. Three comments cite a number the code beside them does not deliver
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D5-s2-03**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. DHW_COLD_WATER_TEMP comment claims the draw model heats from it; the draw reads the configured inlet
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D7-s1-71
- **D5-s2-51**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
### D6

- **D6-s1-01**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s1-02**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. README puts the two-zone split and the orientation factor on the wrong options pages
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s1-03**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s1-81**: verified, low, class P11, hygiene; panel unanimous, batch B, finder low. README's SEK currency fallback is unreachable under Home Assistant core, which defaults Config.currency to EUR
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s2-01**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. configuration.md says 'All 74 entities'; the six platforms create 75
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s2-02**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. configuration.md: the weather page does not create the entry; the setup flowchart omits the menu and overview
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s2-03**: verified, low, class I5, bug; panel unanimous, batch B, finder low. Curve-bias 'at most 0.5 K per week' is false: 0.6 K in a 7-day window
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); D6-s1's non-finding on the same sentence ruled not comparable (a doc-reading count against this runtime measurement)
- **D6-s2-04**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. how-it-works.md: space solve 'from two starting points'; it runs four, each refined and polished
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D6-s2-05** (merged: D5-s1-06): verified, low, class I5, hygiene; panel unanimous, batch A, finder low. configuration.md simulate_plan field list omits the five wood fields
  - R1 row: 5 -> 0 under V3's own strip; perturbation is V3's own strip (D6/verify-v3/s2_05_own_perturb.py); merged D5-s1-06
### D7

- **D7-s1-01**: verified, low, class new: structure metric blind to a code shape, bug; panel unanimous, batch B, finder low. Structural ratchet does not price coordinator state reached via module-level _helper(self, ...)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D7-s1-02**: weakened(low), low, class I1, bug; panel split, batch A, finder medium. Drift-gate comparison and stress per-scenario budget verdict are deletable with every runnable check green
  - V2 and V3: verdict lines sit in __main__/main(), unreachable by import; no wrong value at baseline; both files are code-owned by @tvofi; scenario_budget is executed 0 times under both drivers, contrary to 'pinned'
- **D7-s1-71**: verified, low, class P2, hygiene; panel unanimous, batch B, finder low. Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); judge classes the thrice-held default as P2 (one fact decided at divergent sites); sibling D5-s2-03
- **D7-s2-01**: verified, medium, class new: fit integrator differs from the simulated plant, bug; panel unanimous, batch B, finder medium. sysid two-state fit rolls the candidate one Euler step per sample: UA 17-25% low, 0/3 presets adopt
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sysid sibling of the P5 group, a different mechanism (the fit is biased; the gate refuses correctly)
- **D7-s2-02**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. Defrost derate fallback folds meter ratios _cop_fold_blocked refuses to the COP learner
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D7-s3-01**: verified, low, class new: production member reached by no production code, hygiene; panel unanimous, batch B, finder low. 10 class members are reached by no production code; 9 are kept only by tests that pin them
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D7-s3-02**: verified, low, class I4, hygiene; panel unanimous, batch B, finder low. structure.py dead_methods reads 0 while 9 members are dead: properties skipped, bare-name loads count
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D7-s3-51**: verified, low, class new: return inside finally, bug; panel unanimous, batch B, finder low. nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D7-s3-72**: verified, low, class new: production member reached by no production code, hygiene; panel unanimous, batch B, finder low. 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
### D8

- **D8-s1-02**: verified, low, class P2, bug; panel unanimous, batch B, finder low. DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D8-s1-03**: verified, low, class P2, bug; panel unanimous, batch B, finder low. Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off'
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D12-s2-01, fix D12-s2-01 at both seams first
- **D8-s2-01**: weakened(medium), medium, class new: whole-entity availability gated on an optional input, bug; panel split, batch A, finder high. Climate entity is unavailable with no indoor thermometer, taking the thermostat control with it
  - all three weaken: the switch, set_mode service and options flow still control the optimizer and nothing is actuated wrongly; the gate is the owner's recorded A3(e) decision (tests/entities.py:3345), so the fix is the owner's call
- **D8-s2-02**: verified, high, class P2, bug; panel split, batch A, finder high. Climate hvac_action publishes off while an active boost runs the pump in optimizer mode off
  - V3's weaken not taken: hvac_action publishing off while a boost runs the pump is a wrong published value (COMMON.md item 7) for up to the 2 h boost. Sibling D8-s2-03, whose fix conflicts
- **D8-s2-03**: weakened(low), low, class P2, bug; panel disputed, batch A, finder medium. Mode actions publish a state that mixes the live mode with the stale payload mode
  - disputed. V2 and V3: the off direction runs no solve (0 solves), so the window is fetch time plus up to 10 s, not 30-70 s; hvac_action matches the running actuation until the refresh; only the switch's mode attribute is a stale label. The finder's fix would reintroduce D8-s2-02
- **D8-s3-01**: weakened(low), low, class new: an entity family whose names do not lead with a shared token splits under the name sort, hygiene; panel split, batch A, finder low. Accuracy and Energy-dashboard meter families split in both English and Swedish name sort
  - V2 and V3: on the device page the accuracy split is a category split the rename does not move; the energy-meter half stands (3 runs en, 4 sv)
- **D8-s3-02**: verified, low, class I5, hygiene; panel unanimous, batch B, finder low. Swedish name of Sensor-Gap Advisor reads 'sensor gap in the currency' and drops the advisor role
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D8-s3-03**: verified, low, class new: compatibility duplicate entity enabled by default, hygiene; panel unanimous, batch B, finder low. Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D8-s3-61**: verified, low, class P2, bug; panel unanimous, batch B, finder low. Valve Target Recommendation ships disabled where a mixing valve is set, and available-but-unknown where none is
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
### D9

- **D9-s1-01**: verified, medium, class new: avoidable interpreter-bound recomputation in the solve, bug; panel unanimous, batch A, finder medium. Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here
  - judge 3.14 re-take (load1 1.28-1.33): comfort share 0.3133 (finder 0.3206, tolerance 0.03), 0.0379 with the vectorized twin, plan sha e55e6b6677dbfdc9 unchanged, 0 mismatched rows; flat 0.3174. G3-V1: the fix loses parity on Fortran-order batches
- **D9-s1-02**: verified, medium, class new: avoidable interpreter-bound recomputation in the solve, bug; panel unanimous, batch A, finder medium. L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve
  - judge 3.14 re-take (load1 1.1): scalar objective share 0.1536 (finder 0.1505, tolerance 0.02), 0.0057 fused; flat 0.1514
- **D9-s1-03**: verified, low, class new: CPU work inline on the event loop, bug; panel unanimous, batch A, finder low. The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve)
  - judge 3.14 re-take: max step() call 2.55x reference solve (finder 2.46, tolerance 25 %), 0.3 ms with the fit stubbed
- **D9-s1-04**: verified, low, class new: avoidable interpreter-bound recomputation in the solve, bug; panel unanimous, batch A, finder low. DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve
  - judge 3.14 run: 7758 simulate_dhw_step calls (exact), 4780 with the early exit; share 0.228 -> 0.164; G3-V2: 1z shoulder share 0.023
- **D9-s1-71**: verified, low, class new: avoidable interpreter-bound recomputation in the solve, bug; panel split, batch A, finder low. Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU
  - R1 row (3.11, load1 1.00) 0.1035 and judge 3.14 re-take (load1 1.00) 0.1028, leave-best-out 0.0786, null arm 0; above V3's null band (-0.07..+0.05), so V3's weaken is not needed; plans identical in 5 of 5
- **D9-s2-01**: verified, low, class new: CPU work inline on the event loop, bug; panel unanimous, batch B, finder low. sensor_advisor ranking re-simulated on the event loop at every plan-sensor write: ~32% of loop CPU
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); judge quiet re-take (load1 0.31): 384 simulate steps per read, advisor_share_of_loop 0.331 (finder 0.316); null arm 0 and 0.0011
- **D9-s2-02**: verified, medium, class new: CPU gate blind to a regression outside its sampled work, bug; panel unanimous, batch A, finder medium. No budgeted check sees a 2x of the coordinator's loop-thread work; stress.py reaches none of it
  - judge 3.14 run: loop2x.offenders 0 (exact); --scale 4 gives loop5x.offenders 1; G3-V1 paired harness 1.149x / 0 offenders; G3-V2: x5 did not turn red
- **D9-s2-03**: verified, medium, class new: CPU gate blind to a regression outside its sampled work, bug; panel unanimous, batch B, finder medium. stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G3-V3 class I1 not taken: the gate is blind to where the work sits, not to a deleted guard
- **D9-s2-71**: verified, medium, class new: CPU gate blind to a regression outside its sampled work, bug; panel unanimous, batch B, finder medium. stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); judge quiet re-take (load1 0.48): stress_sweep_valve_cases 0 of 51; valve step-equivalents max 9,426,048 -> 5,439,456 under --perturb novalve, controls unchanged exactly. Batch A omitted this provisional-timing row; the count is exact and the step-equivalent ratio is deterministic, so the CPU ratio is not load-bearing
### D10

- **D10-s1-01**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); G2-V3: the fix must also cover services.py:629 assign_entity
- **D10-s1-02**: verified, medium, class P2, bug; panel split, batch A, finder medium. Optimize-now button press returns normally when the solve did not run; the run_optimization action raises
  - V3's weaken to low not taken: the press reports success when the solve did not run, a defect with a workaround
- **D10-s1-03**: verified, low, class P11, bug; panel unanimous, batch B, finder low. Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D10-s2-01**: weakened(low), low, class P6, bug; panel split, batch A, finder medium. Climate presets auto and economy are non-standard and have no translation or icon in any language
  - all three weaken: the entity publishes a correct raw token; the consequence is two untranslated preset labels with the default icon
### D11

- **D11-s1-01**: weakened(medium), medium, class I3, bug; panel split, batch A, finder high. A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false)
  - all three weaken: a governance bypass on test-infrastructure files (2 of 201 merges), one-setting fix, no product effect
- **D11-s1-02**: weakened(medium), medium, class I3, bug; panel split, batch A, finder high. A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator
  - all three weaken: capability, not incident (0 of 16 direct pushes); needs the deploy key held by the stamp seat; a push to main forces the full gate
- **D11-s1-03**: weakened(low), low, class I3, bug; panel split, batch A, finder medium. Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write
  - all three weaken: a same-repo pull_request run already executes the PR's own workflow YAML, so the three scripts add 0 jobs of privilege; the proposed restore fix moves 3 -> 0 and one tests.yml edit moves it back to 3 (V3); the real seam is the pull_request trigger
- **D11-s1-04** (merged: D11-s2-03): verified, medium, class I3, bug; panel split, batch A, finder medium. Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record
  - merged D11-s2-03 (judge cross-run: seat_counted 6 -> 0 under D11-s1-04's perturbation); by-hand, GitHub API rows not re-run in the cloud (recorded snapshot)
- **D11-s1-71**: verified, low, class I4, bug; panel unanimous, batch B, finder low. Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D11-s1-72**: verified, low, class I4, bug; panel unanimous, batch B, finder low. entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D11-s2-01**: weakened(low), low, class I3, bug; panel split, batch A, finder medium. Per-file policy caps count lines, so a capped rule file grows in prose with its per-file budget check green
  - all three weaken: per-file caps count lines by design; joined growth is bounded by the aggregate bands (about 184-245 tokens); V3 widens the seam to 41 of 41 caps
- **D11-s2-02**: weakened(low), low, class I3, bug; panel split, batch A, finder medium. policy_lint --hooks never reads a hook's matcher: a PreToolUse matcher naming no edit tool passes as wired
  - V1 and V2: pre-edit.sh is a local early detector whose rules CI still gates, and .claude/settings.json is code-owned
- **D11-s2-04**: weakened(low), low, class I5, hygiene; panel split, batch A, finder low. CLAUDE.md rule 1 quotes a mode line the gate does not print, and says FULL prints a zero it does not
  - V3: claim (a) holds on the real select output; claim (b) has an exit-status reading under which it is true, so only (a) stands
### D12

- **D12-s1-01**: verified, high, class P6, bug; panel unanimous, batch B, finder high. Hot water without a tank probe: every solve starts from the 55 C ThermalState default, never advanced
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D12-s2-01**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. On an on/off pump, the switch path switches off steps whose planned heat the plan books as delivered
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D12-s2-02**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. The pump-duty arbiter writes the operating mode with select.select_option whatever domain the mode slot holds
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D12-s2-03**: verified, medium, class P3, bug; panel unanimous, batch B, finder medium. On an on/off pump every full-power step publishes as 'eco' and power_normalized runs to -60
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D12-s3-01** (merged: D4-s2-04, D12-s1-02): verified, medium, class P2, bug; panel unanimous, batch B, finder medium. Full config-flow wizard invents a DHW tank and a second zone the user never affirmed
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); merged D4-s2-04 and D12-s1-02 (judge cross-run: two_zone_expert_defaults 1 -> 0; phantom DHW steps 9 -> 0)
- **D12-s3-81**: verified, medium, class P8, bug; panel unanimous, batch B, finder medium. Grid-fee bounds are SEK numbers: a 0.05 EUR/kWh fee is unenterable in HUF, ISK, JPY and KRW
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); sibling D14-s2-02
### D13

- **D13-s1-01**: verified, medium, class I4, bug; panel unanimous, batch B, finder medium. --stats API-mode enumerator silently drops 52 of 253 window merges whose /commits/<sha>/pulls answers []
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D13-s1-02**: weakened(medium), medium, class new: an approval bound to an exact head is re-bought on a diff-identical move, bug; panel split, batch A, finder high. 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits
  - all three weaken: 0/22 blocked has p=0.14-0.19 at the first-verdict block rate; only 3-4 of 22 rounds kept the branch diff unchanged, so the proposed carry saves 3-4 rounds, not 12
- **D13-s1-03**: weakened(medium), medium, class I3, bug; panel split, batch A, finder high. Body-answer blocks (8) exceed every engineering block class (max 1); record-and-body 12 vs engineering 7
  - V2 and V3: the pre-review check the finding asks for exists (pr-contract lists failing check runs since #956, over every head since a07dd57d/#1144); the claim is narrowed to the measured residual, an ordering gap: pr-contract runs about 15 s after a push and is not re-triggered when the named reds finish (typing completed after the last pr-contract run at 6 of 6 final heads). 7 of 8 blocks fall on one day
### D14

- **D14-s1-01**: verified, medium, class P1, bug; panel unanimous, batch B, finder medium. P1: a malformed store leaf raises out of a loader or consumer; a naive legionella timestamp wedges every refresh
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s1-02**: verified, low, class P6, hygiene; panel unanimous, batch B, finder low. P6: horizon_hours read from coordinator.data but never written; boost probes a field only a test double defines
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s2-01**: verified, medium, class P2, bug; panel unanimous, batch B, finder medium. P2: the two-zone and wood-furnace facts are re-derived from a proxy key at three seams beside their canonical predicate
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s2-02** (merged: D4-s2-02): verified, medium, class P8, bug; panel unanimous, batch B, finder medium. P8: a money figure's currency comes from the label source, never from the price feed that denominates it
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only); merged D4-s2-02 (same measured cell)
- **D14-s2-03**: verified, low, class I4, bug; panel unanimous, batch B, finder low. I4: class roster and finding grammar have disagreeing readers (P11 on no D14 seat; intake admits schema-refused ids)
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s3-01**: verified, low, class P3, hygiene; panel unanimous, batch B, finder low. P3: 22 quantities are read through a positive floor at one seam and raw at a sibling; no check enumerates them
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s3-02**: refuted, low, class P4, bug; panel split, batch A, finder low. P4: both multi-start seams stop at non-stationary points; 12 of 30 seam calls ship >0.1 % above reachable
  - the headline metric does not move under the finder's own perturbation: judge 3.14 runs give p4_tol_misses 12 -> 12 on the full grid and 2 -> 2 on the quick grid under --perturb no_deep (only the sibling p4_bracket_misses moves, 2 -> 3, max gap 0.389 -> 0.594 %), and the flat-price arm carries 3 misses; V2 measured the claimed mechanism false (a fine-gradient polish from the shipped x leaves at most 0.0001 % with the production gradient, 0.08 % with scipy FD), so the shipped points are near-stationary and the residual gaps are between basins, which is D0-s2-02's verified seed-set phenomenon
- **D14-s3-03**: verified, medium, class P5, bug; panel unanimous, batch B, finder medium. P5: sysid adoption gate keys on the UA half-width, which barely moves while unmodelled free heat biases UA to -21 %
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s4-01**: verified, high, class P7, bug; panel split, batch A, finder high. Eight production seams still do wall-clock datetime arithmetic across DST; the forecast grid lands 60 min off
  - V1's weaken to medium not taken: the forecast grid lands 60 min off on 42 of 48 cycles on every transition day, a wrong published plan (COMMON.md item 7), though only two days a year
- **D14-s4-02**: weakened(low), low, class P11, bug; panel split, batch A, finder medium. The replay lane freezes a fixed-offset clock, so a DST-day replay reports zero P7 seams
  - V3: tests/replay/ holds one fixture and no DST day, so the fixed-offset clock has no present consequence; class P11 (a test-double clock whose tzinfo differs from HA's), with P7 the class it hides. G3-V2: the fix must also step run_fixture in UTC (8/96 left otherwise)
- **D14-s5-01**: verified, medium, class I2, bug; panel unanimous, batch B, finder medium. Python closures miss every file a spawned child process reads; select() skips the script on a change to it
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)
- **D14-s5-02**: verified, medium, class I1, bug; panel unanimous, batch B, finder medium. Mutation ratchet inventory cannot see 528 of 2313 production guard seams; a new guard of those shapes raises it by 0
  - judged on the three verifier reproductions (tvofi decision 2026-09-26T13:39Z, round 9 only)

## Yield (rotation.json rounds['9'].yield)

Judge-surviving canonical findings per step; the machine form is yield.json.

- D0: M2 1
- D1: M1 5, M2 9, M3 5, M4 1, M5 5, M6 7
- D2: M1 2, M2 2, M3 3, M4 2, M5 3
- D3: M2 3, M3 4, M4 2
- D4: M1 5, M2 4, M3 4
- D5: M1 2, M2 1, M3 2, M4 4
- D6: M1 1, M2 8
- D7: M1 2, M2 1, M3 1, M5 1, M6 4
- D8: M2 5, M3 2, M4 2
- D9: M1 6, M2 3
- D10: M1 4
- D11: M1 2, M2 2, M3 4, M4 1
- D12: M2 1, M3 3, M4 2
- D13: M1 2, M3 1
- D14: M3 5, M4 6

## Files

- JUDGE.json: per finding: id, merged ids, verdict, severity, class, stop-rule class, note, evidence rows.
- CLASSES.json: the class list with N and rca.
- yield.json: the per-step yield.
- DEDUP.md, D3-CHECKS.md, JUDGE-INPUT.json (batch A), JUDGE-INPUT-B.json (batch B), rows-1.json/.md (R1), rows-j2.json/.md (judge, shard 2 remainder).
