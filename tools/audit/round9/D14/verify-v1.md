# D14 verify, lens V1 (reproduce)

Baseline 1936d5ca + round-9 evidence (worktree /home/claude/wt, HEAD 6f51db2c). Interpreter: `/home/claude/venv/bin/python` (CPython 3.14.0rc2, numpy 2.4.6); the finders' `/home/claude/venv314` does not exist on this box. Every command ran with `PYTHONPATH=tests/hastub` from the repository root. Numbers are counts unless marked otherwise, so contention does not affect them. load1 during the runs was 0.75 to 7.30; thread_factor was 0.985 to 1.002 throughout. My own probes: `tools/audit/round9/D14/verify-v1/v1_indep.py --arm <arm>`.

Votes: 11 verify, 1 weaken (D14-s4-01, high -> medium), 0 refute, 0 unresolved.

## D14-s1-01: P1 store leaf malformation — verify, medium
- **Re-run** (`p1_store.py --barrier`): p1_escaping_mutants=11, p1_escape_seams=7, p1_wedged_seams=2 (dhw_legionella last_attempt and last_cycle, 3/3 each), barrier_driven_escape_seams=0, mutants=4027. Exact match. load1 2.96, thread_factor 1.000.
- **Perturbation:**
  - snapguard: 11 -> 13 escapes, 7 -> 8 seams (up, as stated).
  - sanitize: poison 0 -> 388, escapes 11 -> 18.
- **Null control:** clean_fixture_escapes=0; wedge_null_control_failed_cycles=0.
- **Own measurement** (arm p1): LegionellaGuard.hours_since() after async_load, with the store's awareness mix varied:

  | Store contents | stub as_utc | HA naive-as-local as_utc |
  |---|---|---|
  | both aware | 0 | 0 |
  | naive last_cycle | 1 (TypeError) | 1 (TypeError) |
  | naive last_attempt | 1 (TypeError) | 1 (TypeError) |
  | both naive | 0 | 0 |

- **Attack, real-HA reach:** the raise is the aware-vs-naive `attempt > last` comparison in legionella.py hours_since. It is not a stub artefact. It needs one naive leaf beside one aware leaf.
- **Metric:** single-leaf store mutants where an exception escapes a real loader or consumer.

## D14-s1-02: P6 unproduced key and a test-double-only getattr — verify, low
- **Re-run** (`p6_keys.py`): p6_unproduced_reads=2, p6_undefined_getattr=1, dangling ids 0.
- **Perturbation:** 2 -> 5 (up).
- **Null control** (`--self-test`): clean 0, planted 1.
- **Own measurement** (arm p6):
  - horizon_hours_produced=0/5 across golden.coordinator_scenarios.
  - boost_calls is present on the real coordinator 0 times, on harness FakeCoordinator 1 time.
  - grep finds no assignment of horizon_hours apart from optimizer.py:1195, the dataclass default.
- **Metric:** distinct (consumer file:line, key) reads that no producer writes.

## D14-s2-01: P2 proxy-key re-derivation — verify, medium
- **Re-run:** derive_preset_disagree=20/40, prefill_refused_or_missed=20/40, wood 2/21, house-mass ratio 0.267..3.750. Seams: two_zone 2, dhw 11, wood 16.
- **Perturbation:** all three counts go to 0.
- **Null control:** 0/20. Selftest: clean 0, re-introduced 1.
- **Own measurement** (arm p2), a different grid of 4 modes x 3 presences:
  - derive_split_vs_canon=5/12, with every mode arm at 1 or more: off+upper, on+none, on+lower, None+lower, auto+lower.
  - wood_vs_canon=2/4: valve_outlet only is drawn but not modelled; dhw_wood_coil only is modelled but not drawn.
- **Grid-artefact attack:** the 20/40 is shaped by the grid, but the disagreement survives on an independent grid.
- **Metric:** configs on which the seam's delivered output disagrees with the canonical predicate on the saved config.

## D14-s2-02: P8 currency from the label source — verify, medium
- **Re-run:**
  - A_unflagged_mismatch=8/12 (perturbed: 0).
  - B off-instance: EUR 1, SEK 0, NOK 1.
  - Card with cfg EUR: 2 tokens, 3 off-install surfaces (price_axis, price_axis_drawn, whatif_delta). pre-R7-D4-03: 4 surfaces. perturbed: 0.
- **Null control:** SEK = 0; no_cfg = 0.
- **Own measurement** (arm p8), an EUR/kWh feed on an SEK instance:
  - normalize_price_per_kwh returns 0.10 unchanged.
  - _audit_price_units creates 0 issues.
  - CurrentPriceSensor unit is 'SEK/kWh'.
  - eur_feed_on_sek_unit=1; null (SEK feed) label ok=1.
- **Metric:** money surfaces whose currency token differs from the figure's denomination, with no repair issue.

## D14-s2-03: I4 class roster and intake grammar — verify, low
- **Re-run:** intake_admits_schema_refuses=11/22; ledger_ids_no_d14_seat=1 (P11); check_scopes_D14_ok=True.
- **Perturbation:** (a) -> False, 5 unowned lines; (b) 11 -> 0.
- **Null control:** 0/17.
- **Own measurement** (arm i4): P11 is absent from the D14 axis and from every seat. Of my own 6 cases, 4 are admitted by the intake and refused by the schema: P13, D14-s1-3, D14-s1-003, I9.
- **Attack, consequence:** audit-find.js:356 has the intake agent validate every accepted finding against finding.schema.json. The mechanical intake therefore has an agent backstop; the P11 gap has none.
- **Metric:** reader verdicts that differ from the ledger+schema verdict, plus ledger ids held by no seat.

## D14-s3-01: P3 floor at one seam, raw at a sibling — verify, low
- **Re-run:** 22 groups (6 raw-divisor, 1 capacity), 0.76 s.
- **Perturbation** (`--reintroduce`): 23 groups; buffer seam 0 -> 1.
- **Null control** (`--fixture`): 0.
- **Own spot check:** dhw_tank_thermal_mass is floored only at optimizer.py:5578 (1e-6) and read raw at 10 other sites.
- **Severity:** the floors sit at or below the schema minimum, so the seams are unreachable from the UI. Hygiene, low.
- **Metric:** quantities read both floored and raw as an operand.

## D14-s3-02: P4 non-stationary multi-start stop — verify, low
- **Re-run** (`--cells full`, 516 s wall provisional, load1 2.51, thread_factor 1.000): p4_tol_misses=12/30, p4_bracket_misses=12/30, max tgap 0.5224 %, max gap 0.8915 %, flat misses 3, cell gap -0.0177..0.8915 %, drop-best mean 0.0939 %. Exact match.
- **Perturbation** (`no_deep --no-tight --cells quick`, against the same grid unperturbed):
  - bracket misses 2 -> 3.
  - two|nodhw|winter_typical gap 0.3888 -> 0.5937 %; prod 77.884228, which re-finds R7 D0-01.
  - This moves the bracket metric. The tgap arm is skipped under `--no-tight`.
- **Null control:** the flat-price arm still misses in 3 of 4 topologies. The claim says the gap does not vanish at flat prices, so no money is claimed.
- **Leave-one-out** (own re-aggregation, arm p4): dropping one price profile gives 7/24 (drop shoulder) up to 12/26.
- **For the judge:** a 0.1 % gap against an ftol-1e-12 re-solve is close to the definition of a finite tolerance. Whether the stop-rule class is bug or tuning is the judge's call.
- **Metric:** (prod - own candidates at tight stop)/|prod| > 0.1 %.

## D14-s3-03: P5 adoption gate keyed on half-width — verify, medium
- **Re-run:** p5_admitted_over_bar=3/39 admitted, worst 21.431 %, blended 7.970 %, gains 3, others 0, drop_worst 2, monotone breaks 0/15.
- **Perturbation:** prior_true 3 -> 0; bar_tight 3 -> 0, but only by refusing all 39 admissions.
- **Null control:** 0.
- **Own measurement** (P5_JSON rows, arm p5):
  - Re-count gives 3.
  - Leave-one-out by preset: dropping heavy_old gives 2, light_new 3, typical_slab 1.
  - In typical_slab, hw rises 0.0531 -> 0.0685 while err_log goes 0 -> -0.241 (-21.4 %). The gated quantity stays under the bar ln 1.1 = 0.0953.
- **Metric:** admitted cells with |ln(UA_fit/UA_true)| > ln 1.10.

## D14-s4-01: P7 wall-clock datetime arithmetic across DST — weaken, high -> medium
- **Re-run:** wrong_sites=9 (5 aware-shared-zone, 4 add-shared-zone), sites_reached 10.
  - Grid skewed on 42/48 cycles at 60 min on each of the 6 transition days 2025-2027.
  - Wrong sites per transition day: spring 8, autumn 9. Cycle errors 0.
  - 56.6 s, load1 7.30 (contended), thread_factor 0.997.
- **Perturbation:** `--fix-grid` gives 8 sites and 0/48 skew; `--reintroduce` gives 10.
- **Null control:** plain and plain_autumn days give 0 sites and 0/48.
- **Own measurement** (arm p7): _forecast_arrays called on a namespace self, with the step-0 label built by _utc_step_starts from production's own (midnight, step_offset). The label is 60 min off on 42/48 half-hour instants on 2026-03-29 and 2026-10-25, and 0/48 on 2026-03-22.
- **Real-HA reach:** HA's now() and now.replace() share one ZoneInfo, so the subtraction is wall-clock in CPython. It is reachable outside the stub.
- **Severity:** the misaligned grid lasts about 21 h on 2 days a year. That is bounded and recurring, so medium.
- **Metric:** production sites whose datetime difference differs from the UTC truth on a DST day.

## D14-s4-02: replay lane freezes a fixed-offset clock — verify, medium
- **Re-run:** replay_wrong_sites=0; `--zone-clock` gives 10 (spring 10, autumn 9, plain 0). load1 5.15 / 4.48, thread_factor 0.997.
- **Own measurement** (arm rp): replay._ts returns tzinfo `datetime.timezone` (fixed offset). Across the spring transition, wall minus UTC is 0 s on the fixed clock and 3600 s on the ZoneInfo clock.
- **Metric:** sites with a datetime difference != UTC truth under run_fixture on the DST days.

## D14-s5-01: Python closures miss child-process reads — verify, medium
- **Re-run:** seams=31 (doc_claims 9, deployment_shape 22, all python-child reads).
- **Perturbation:** union -> 0; drop -> 32.
- **Null control:** 0.
- **stub_scope_probe:** control green 1, edited red 1, red_and_skipped 1; union -> 0.
- **Own measurement** (arm s5): select([tests/hastub/homeassistant/helpers/update_coordinator.py]) is scoped with 13 scripts and skips deployment_shape.py. That script's closure holds 0 tests/hastub files.
- **Mitigation:** a push to main forces FULL, so the miss shows red on main one merge later. Medium stands.
- **Not re-run:** the heavy 883-seam set (about 10 min, provisional).
- **Metric:** (script, file) pairs read by a child, absent from the closure, with select() skipping the script.

## D14-s5-02: mutation inventory blind to guard shapes — verify, medium
- **Re-run:** uncovered=528/2313 (EXIT 52/1346, CLAMP 246/668, TERN 230/299). Ratchet delta 1 and refusal for a visible guard; 0 and no refusal for an invisible one.
- **Perturbation** (widen): 528 -> 476; EXIT 52 -> 0.
- **Null control:** fixture clean 0, re-introduced 1.
- **Own measurement** (arm s5g): 169 of 184 np.clip/np.minimum/np.maximum call lines carry no candidates() site.
- AST only; no mutant pool was run, per the D3 rule.
- **Metric:** guard seams with no candidates() site of the covering kind on that line.
