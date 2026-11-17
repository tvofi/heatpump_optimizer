# D2 verify-1 -- round 11, box V5 (seat D2-v1)

Every finding of this unit carries a planted-export scope (D2-s1, D2-s2): every number was taken in a private copy of the planted export (`../audit-r11-px-D2-1`, PYTHONPATH=tests/hastub). load1 0.4-1.0 on 4 cpu, thread_factor 1.000; counts are load-immune. Finder re-runs `$HOME/vout/D2-v1/v1/`, verifier harness `$HOME/vout/D2-v1/harness/v2_d2a.py`.

## D2-s1-01 -- verify (critical)

- metric: trajectory elements where simulate_trajectory_batch differs bitwise from simulate_trajectory (6 rows x 96 steps, all arms)
- method: V1 batch_parity.py base/--fix-lift, golden_identities.py; V2 v2_d2a.py: flow_lift_factor over a 35x41 flow/outdoor grid against my own Carnot ratio C(T)=(T+273.15)/(T-To), and call count >1 inside a real coordinator solve; tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 14314 mismatched elements (finder 14897); --fix-lift 3012 (finder 3674); golden lift>1 calls 1268 -> 0
- V2 independent: factor >1 in 1435 of 1435 grid points above the 35 C reference (max 2.0205); at outdoor 0 / flow 60: production 1.5856 vs Carnot ratio 0.6307; a real coordinator solve with a 200 l DHW tank called it 21 times, 21 > 1
- attacks: re-run gave 14314 total (finder 14897) and 3012 with --fix-lift (finder 3674): outside the 'exact' tolerance, likely a platform/BLAS bitwise difference in the random-row integration (the finder ran B4); direction and arm split hold (space_only 0, 1z valve arms 3047 -> 0, dhw/wood/coil/external_heat -> 0 under --fix-lift); golden replay reproduces exactly: flow_lift_factor >1 on 1268 calls, 0 under --fix-lift; null space_only 0; not a timing claim (load1 0.4-1.0)
- V3 reach: yes: every DHW charge and valved/direct-curve plant in a real HA solve (default install with a DHW tank reaches it); class: P2 (corrected from new: the lift fact is decided twice, scalar ref/flow vs batch flow/ref); seam_rule enumerates: yes: scalar (thermal_model 3345, coordinator 1225 health watch) and batch twin (4472-4493)

## D2-s1-02 -- verify (high)

- metric: two-zone valve trajectory elements where batch differs from scalar with the lift corrected; negative emitter deliveries on the golden replay
- method: V1 batch_parity.py --fix-lift / --fix-lift --fix-emitter, golden_identities.py; V2 v2_d2a.py emitter_delivery sign grid; tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 3012 (finder 3674) -> 0 under --fix-emitter; golden 496 calls / 87.52 kWh
- V2 independent: emitter_delivery negative in 15 of 110 grid cells (every mix < zone), e.g. mix 15 C, zone 22 C, ua 0.2 -> -1.400 kW; its docstring says never negative
- attacks: --fix-lift left 3012 (finder 3674, same platform caveat), --fix-lift --fix-emitter 0 (to_zero holds); null single-zone valve arms 0; golden replay: 496 negative deliveries / 87.52 kWh at baseline exactly as stated, 567 / 109.1 kWh with --fix-lift, 0 calls / 0 kWh with both fixes
- V3 reach: yes: two-zone valved plants' scalar step (thermal_model 2526/2536) in real HA solves and the published trajectory; class: P2 (corrected from new: the batch twin floors the delivery, the scalar sibling does not); seam_rule enumerates: yes: both scalar call sites; the batch twin floors separately

## D2-s1-51 -- verify (medium)

- metric: preset cells where derive()'s house_heat_loss_coefficient for low_energy is not below post_2005
- method: V1 leads/era_loss_order.py base/--perturb; V2 v2_d2a.py: own cells (every structure x foundation x area 100/200 x emitter), presets.derive; tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 36 of 36 inverted; null 0; perturb 0
- V2 independent: 48 of 48 cells; low_energy/post_2005 = 1.545
- attacks: perturb 36->0; null (first four eras) 0; mine 48 of 48 cells, ratio 1.545 in every cell (table: low_energy 0.85 W/m2K vs post_2005 0.55, 1980_2005 0.80); a constant ratio, no grid artefact
- V3 reach: yes: the building questionnaire (config and options flow) writes this coefficient into the entry; class: new (confirmed; a data-table value, no listed class fits); seam_rule enumerates: no seam_rule supplied with the lead; _ERA_LOSS_W_PER_M2K has one reader (presets.py:239), so the one seam is the phenomenon's

## D2-s2-01 -- verify (critical)

- metric: adjacent flow/tank grid pairs where compute_cop(valve) or compute_cop_dhw rises with flow, 5 climates
- method: V1 m2_cop_laws.py base/--perturb=lift; V2 as D2-s1-01 (own Carnot ratio grid, real-solve call count); tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 156650 pairs; lift_max 2.0205; perturb 0
- V2 independent: factor >1 on 1435 of 1435 points above reference, max 2.0205; 21 of 21 real-solve calls >1
- attacks: perturb lift 156650 -> 0 (lift_over1 84350 -> 0, carnot_frac_over1 21320 -> 0, batch maxabs 8.009 -> 0.0), reproduced exactly; no null in the finding -- my null: at/below the reference flow the factor is 1.0 on every point; same root as D2-s1-01 (one line, thermal_model.py:3391)
- V3 reach: yes, as D2-s1-01; class: P2 (duplicate root of D2-s1-01); seam_rule enumerates: yes

## D2-s2-02 -- verify (high)

- metric: duty points in linspace(0, 0.30, 61) where derate_from_duty differs from clip(1 - 1.5 d, 0.55, 1)
- method: V1 m2_cop_laws.py base/--perturb=defrost; V2 v2_d2a.py: derate_from_duty at 0, .05, .1, .2, .3 vs the module docstring law; tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 60 of 61; frost_cop_ratio 1.0 (documented 0.70)
- V2 independent: derate 1.000 at duty 0.05..0.30 (law 0.925..0.550)
- attacks: perturb 60 -> 0 and frost_cop_ratio 1.0 -> 0.70 on winter_mild (73 frost steps) and shoulder (41), reproduced exactly; null: duty 0 and frost-free climates match; mine: 1.000 at every duty vs 0.925/0.850/0.700/0.550
- V3 reach: yes: the measured defrost learner (defrost.py:305/454/635) feeds the solve's frost-band COP in real HA once duty is trusted; class: new (confirmed); seam_rule enumerates: yes: derate_from_duty's three callers and the constant

## D2-s2-03 -- verify (high)

- metric: space_setpoint_unit x compressor_modulation cells whose derived clamp contradicts the declared modulation
- method: V1 m2_priced_surface.py base/--perturb; V2 declared_modulation per mode and an own coordinator solve (on_off vs modulating, min 1.5 kW in entry data) via $HOME/vout/D17-v1/harness/v2_d17.py s1-04 run in this copy; tree: planted export copy ../audit-r11-px-D2-1 (PYTHONPATH=tests/hastub)
- V1 reproduced: 3 of 9 cells; perturb 0
- V2 independent: declared_modulation('on_off') True; on_off sub-min steps 6/96 == modulating 6/96
- attacks: perturb 3 -> 0 reproduced; null auto/modulating 0 of 6; mine: declared_modulation(on_off)=True, (modulating)=True, (auto)=None; own solve 6 of 96 sub-min steps under on_off, identical to modulating (6 of 96). Same root as D17-s1-04
- V3 reach: yes: thermal_model options page in real HA; class: new (same root as D17-s1-04); seam_rule enumerates: yes: the three readers thermal_model.py:1454, 1570, 1633
