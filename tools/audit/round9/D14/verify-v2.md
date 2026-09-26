# D14 round 9: verifier V2 (independent lens), box G3-V2

**Setup**
- Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Evidence tree: handoff/audit-r9-evidence at 6f51db2c.
- Interpreter: CPython 3.14.0rc2 (venv). Node 22.
- Machine: 4-core cloud container, shared with the D2 and D9 verifier sub-seats.
- Every number below is a count or a ratio, so contention cannot move it. load1 and thread_factor are quoted as the contract requires.

**How it was run**
- Finder harnesses re-run as their headers say, with this box's venv interpreter in place of the finder's `/home/claude/venv314`.
- Own harnesses are under `tools/audit/round9/D14/verify-v2/`, each with a header, the thread pin and RESULT lines.
- On-disk perturbations (D14-s5-01) were made in a detached worktree outside the repository, since removed.
- No mutation pool and no full-gate runs, per tvofi's rule.
- Machine-readable votes with the full value and attack strings: `tools/audit/round9/verify/votes-G3-v2.json`.

**Tally:** 11 verify, 1 weaken, 0 refute, 0 unresolved.

## D14-s1-01: P1, malformed store leaf escapes; naive legionella timestamp wedges refresh — **verify, medium**
- **Finder re-run:** `p1_store.py --barrier`: p1_escaping_mutants=11, seams 7, wedged 2, barrier_driven_escape_seams 0, clean fixture 0, null wedge 0 (load1 0.88, tf 1.000). Exact match.
- **Own number:** `v2_store_leaf.py`: v2_raising_cases=7 of 9, null 0. The 9 payloads are hand-written with own config and clock (golden coord_dhw, entity prices, 2026-02-03 09:40 Europe/Stockholm).
  - A naive last_attempt, or a naive last_cycle beside an aware last_attempt, fails 3 of 3 `_async_update_data` cycles. A naive last_cycle alone, or both naive, fails 0 of 3.
  - Other raising cases: boost naive until (restore_session TypeError), pump written "x" and 3.0 (AttributeError), snapshot bias "garbage" and [] (best_restore TypeError/ValueError).
- **Metric:** of hand-built one-leaf malformations, the count where the real loader plus its real consumer raises.
- **Attacks:** stub fidelity: HA's real as_utc semantics (`--ha-dt`) gives the same 7 of 9. `--guard` (coerce naive to aware in legionella) gives 5 of 9, legionella wedge 0 of 3. Refinement: the wedge needs *mixed* awareness. Reach: the product writes only aware stamps, so the trigger is a corrupt or hand-edited store; the loaders promise tolerance.

## D14-s1-02: P6, horizon_hours never produced; boost_calls probed only on the test double — **verify, low**
- **Finder re-run:** `p6_keys.py`: p6_unproduced_reads=2, p6_undefined_getattr=1, dangling ids 0 (load1 1.14). Match.
- **Own number:** `v2_keys.py`: 'horizon_hours' in the payload in 0 of 5 golden topologies; null key 'currency' 5 of 5. With `_opt_config.horizon_hours=48` and a rebuild, `data.get("horizon_hours", 24.0)` still reads 24 (misreport=1). `--fix`: 5 of 5 and 0. AST getattr probes of names no production code or real HA API defines: boost_calls (boost.py:212, defined only in tests/harness.py); the rule also flags `_finite_scrubbed`, a false positive (set with setattr).
- **Attacks:** the published value is right today only because the horizon is never assigned: hygiene.

## D14-s2-01: P2, two-zone and wood facts re-derived by proxy — **verify, medium**
- **Finder re-run:** `p2_facts.py`: 20/40, 20/40, wood 2/21, null 0 (load1 1.14). Match.
- **Own number:** `v2_facts.py`, exhaustive grid: `_derive_preset` depends on the proxy in 26 of 48 cells (null where proxy equals canonical: 0 of 22); `modbus_prefill.infer` offers or withholds the flow target against the canonical fact in 26 of 48; slab_thermal_mass moves 0.591x..1.692x; `describe_setup` wood.present disagrees with wood_furnace_on in 2 of 64 subsets (valve_outlet_temp_entity alone; dhw_wood_coil_enabled alone), explicit-flag null 0 of 128. `--fix`: 0 everywhere.
- **Attacks:** not a grid artefact (three independent mechanisms). Reach: the options flow at config_flow.py:3557 passes the effective config. Own house moves slab mass rather than house mass; same mechanism.

## D14-s2-02: P8, currency from the label source, not the feed — **verify, medium**
- **Finder re-run:** `p8_currency.py`: A=8 of 12 unflagged, B=1, card 3 (pre-R7-D4-03: 4) (load1 1.14). Match.
- **Own number:** `v2_currency.py`: the real CurrentPriceSensor labels the unconverted feed number with hass.config.currency in 9 of 12 cells, `_audit_price_units` raises 0 issues; null (feed equals instance) 0 of 3; `--fix` 0. Of 3 money widgets built at an EUR instance, 1 is off-instance: wood_price_sek_m3 'SEK/m³'.
- **Attacks:** realistic configuration. The plan is scale-invariant to the label, but the wood-versus-electricity comparison and money labels are wrong: medium. The card arm was not measured independently.

## D14-s2-03: I4, class roster and finding grammar have disagreeing readers — **verify, low**
- **Finder re-run:** `i4_roster.py`: intake_admits_schema_refuses=11, P11 unowned 1, check_scopes D14 ok True (load1 1.14). Match.
- **Own number:** `v2_roster.py`: P11 held by no D14 seat (16 ledger ids vs 15 axis ids). The intake predicate extracted from audit-find.js and executed in node admits 10 of own 14 boundary cases that the schema refuses; null 0 of 6; `--fix` 0.
- **Attacks:** consequence limited to audit tooling.

## D14-s3-01: P3, floored at one read, raw at a sibling — **verify, low**
- **Finder re-run:** `p3_floors.py`: 22 groups, 6 raw-divisor groups, 1 capacity group (load1 1.14). Match.
- **Own number:** `v2_floors.py`: 8 groups under a stricter rule (name-keyed, divisor only), 22 raw divisor sites; `--fixture` 0; `--reintroduce` (R7 D2-01's `/ max(C_buf, 0.01)`) 8 → 9.
- **Metric difference:** divisor-only and name-keyed against the finder's per-quantity rule with `*`; the judge decides comparability. The name key over-merges unrelated uses, so neither count is exact.
- **Attacks:** floors sit at or below the schema minimum, so the seams are latent: a barrier proposal.

## D14-s3-02: P4, multi-start seams stop at non-stationary points — **weaken, low**
- **Finder re-run:** `p4_seeds.py --cells quick`: p4_tol_misses=2 of 9 (flat 3), max tgap 0.5224 % (load1 2.70, tf 1.000, 181.6 s). two|nodhw|winter_typical: prod 77.723993 vs tight-from-candidates 77.427490. `--cells full` not re-run (heavy).
- **Own number:** `v2_polish.py`, a tight L-BFGS-B polish from the *shipped* x on 9 calls: 0 of 9 improve by more than 0.1 %; max gain 0.0001 % with the production gradient, 0.0769 % with a fine-eps gradient (a lower bound: evaluation-limited). The same cell polishes only to 77.711468. Flat prices: 0.036 %.
- **Metric:** relative gap between the shipped fun and a polish from the shipped x; miss above 1e-3.
- **Attacks:** the shipped point is locally near-stationary. The finder's 0.38–0.52 % gaps are inter-basin: another candidate run tighter finds a lower minimum (ranking under early stop / seed dependence). The count reproduces; the stated mechanism ("ships a non-stationary point") overstates. The flat-price gap survives in both, so no money claim.
- **Vote:** weaken on the mechanism; severity stays low.

## D14-s3-03: P5, sysid gate blind to unmodelled free heat — **verify, medium**
- **Finder re-run:** `p5_gate.py`: 3 admitted over bar, worst 21.431 %, blended 7.97 %, null 0 (load1 1.37). Match.
- **Own number:** `v2_sysid.py`, own plant and bias route (extra external heat at −5 °C): 8 of 10 cells admitted over the bar (the two houses resolve to identical parameters, so 4 of 5 distinct cells); error +15.2 % at 0.15 kW, +50.18 % at 0.8 kW; gated half-width only 0.051 → 0.068; null 0; `--bar-tight` 0.
- **Attacks:** coordinator.py:2365 wires gains_prior_kw from declared gains. The error sign is opposite to the finder's because the bias route differs; the phenomenon is the same.

## D14-s4-01: P7, DST wall-clock arithmetic; forecast grid 60 min off — **verify, high**
- **Finder re-run:** `p7_dst_seams.py`: wrong_sites 9 (union), grid_skewed 42 of 48 on all four transition days, plain 0 (load1 2.03, tf 0.997). Match.
- **Own number:** `v2_dst_grid.py`: grid step 0 differs from `_solve_anchor(now)` and prices[0] comes from the wrong UTC hour on 84 of 92 quarter-hours of 2026-03-29 and 88 of 100 of 2026-10-25; plain days 0 of 96 each; `--fix` (UTC step_offset at coordinator.py:6206) 0.
- **Attacks:** keyed on a delivered value (the price the solve sees at step 0); real ZoneInfo clock. Twice a year, about 21 h each, silently wrong pricing: high. Only the grid seam was measured independently.

## D14-s4-02: replay lane's fixed-offset clock cannot see P7 — **verify, medium**
- **Finder re-run:** `p7_replay_clock.py`: replay_wrong_sites=0 (load1 1.88, tf 0.996). Match.
- **Own number:** `v2_replay_clock.py`: the replay-built clock's UTC offset differs from ZoneInfo on 80 of 96 (spring) and 76 of 96 (autumn) cycles; the D14-s4-01 seam fires 0 of 96 under the replay clock vs 84 of 96 under ZoneInfo; `--zone-clock-ts` 84 of 96.
- **Attacks:** the only committed replay fixture is a January day. **Constraint on the fixer:** the proposed `_ts` fix alone leaves run_fixture stepping wall-clock (`t += timedelta` on a ZoneInfo value), which still shows 8 of 96 and 4 of 96 offset mismatches; the fix must step in UTC.

## D14-s5-01: Python closures miss child-process reads — **verify, medium**
- **Finder re-run:** `closure_divergence.py`: seams=31 (doc_claims 9, deployment_shape 22), all python-child (load1 2.07). Match.
- **Own number:** 2 of 2 independent one-line hastub probes red and skipped; both scripts rc 0 on the clean tree. A raise appended to issue_registry.py turns deployment_shape.py red (rc 1) while `select()` returns scoped with 14 run, deployment_shape.py not among them. A raise appended to storage.py turns doc_claims.py red (rc 1), and `select()` skips it. deployment_shape.py's closure holds 0 of its 79 entries under tests/hastub.
- **Attacks:** the forced full gate on main bounds the cost: medium. The heavy 883-seam set was not re-run.

## D14-s5-02: mutation inventory blind to 528 guard seams — **verify, medium**
- **Finder re-run:** `guard_inventory.py --history --list`: 528 of 2313 (EXIT 52, CLAMP 246, TERN 230), fixture 0/1, ratchet visible +1 vs invisible 0 (load1 1.90). Match.
- **Own number:** `v2_guard_ratchet.py`: the guard's own lines yield sites only for a one-line if (1) and a two-arg min (1); a split-test if, an elif, np.clip and a ternary each yield 0 (4 of 6 shapes invisible). 85 of 98 np.clip lines in the package carry no site. `--widen` makes the split-test if visible.
- **Attacks:** adding a split-test guard can still raise the file's total by +1 through an incidental site (the trailing return stops being the sole statement), so "delta 0" is situational; the guard itself stays unpinnable.
- **Production mutation (no pool run, per tvofi):** the finder's recorded #1316 np.clip line in custom_components/heatpump_optimizer/curve_learning.py (`_step_down`) and #1312's ternary.

**Not run:** p4_seeds `--cells full`, closure_divergence's heavy set, any mutation pool or full gate.
