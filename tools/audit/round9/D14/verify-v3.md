# Round 9 verify: box G3-V3, lens V3 (reach and class), dimension D14

- Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. The evidence tree `6f51db2c` has no diff from it under `custom_components/`, `tests/`, `.claude/`, `tools/audit/*.json` or `tools/audit/*.py`.
- Machine: cloud container, 4 vCPU Intel Xeon 2.10 GHz, 15 GB RAM, Linux 6.18.44, CPython 3.14.0rc2 (/home/claude/venv), numpy 2.4.6, scipy 1.17.1, node v22.22.2, strace present. Run on 2026-09-26.
- Two other sub-seats (D2, D9) shared the box. load1 was 0.41 to 3.82 while I measured. Every number below is a count or an objective value, so none of them depends on contention. Every RESULT block has thread_factor 0.996 to 1.001.
- My harness is `tools/audit/round9/D14/verify-v3/v3_arms.py`. It has one arm per finding and its header gives the metric, the command and the perturbation. Re-run outputs are in `verify-v3/out/rerun_*.txt` and my own arms are in `verify-v3/out/v3_*.txt`.
- The finders' harnesses name `/home/claude/venv314/bin/python`; I ran each one with `/home/claude/venv/bin/python`.
- Step 3's gate-mode attack ("gate mode wrong") applies to no finding in this unit. None rests on the golden check or on a mutant verdict. D14-s5-02 is a test-gap-shaped instrument finding, but it is a count of AST shapes, not a mutation kill. Under tvofi's 2026-09-26T11:37Z ruling I ran no mutation pool.

## D14-s1-01 (P1 store leaf escapes; legionella wedge)
- **Re-run:** `p1_store.py --barrier` reproduced every number exactly: p1_escaping_mutants=11, p1_escape_seams=7, p1_wedged_seams=2 (dhw_legionella last_attempt and last_cycle, 3/3 each), mutants=4027, clean_fixture_escapes=0, wedge_null_control_failed_cycles=0, barrier_driven_escape_seams=0. load1 2.37, thread_factor 1.000.
- **My number:** arm `p1leg` runs with HASTUB_TZ=Europe/Stockholm, so `dt_util.now()` is aware ZoneInfo as it is upstream. It builds the real coordinator on golden `coord_dhw` with legionella enabled, feeds `LegionellaGuard.async_load` one store payload per case, then calls hours_since, due_in_hours and `_build_data_dict`.
  - All-aware control: 0 raising calls.
  - naive last_cycle + aware last_attempt: 3 of 3 raise.
  - aware last_cycle + naive last_attempt: 3 of 3 raise.
  - naive last_cycle only: 0 raise.
  - naive in both leaves: 0 raise.
  - All raises are the same TypeError at `legionella.py:626` (`attempt > last`). `hours_since` itself survives a naive value because it routes through `as_utc`. The wedge therefore needs a *mixed* naive/aware pair, which is exactly what the finder's single-leaf mutant over a writer-seeded store produces. Result: 2 of 4 naive cases wedge.
- **Reach in real HA:** the path is real.
  - `ha_contract.py` gives `helpers.storage.Store` disposition S, an honest JSON round trip, so a stored naive string comes back naive. Upstream `now()` is always aware (the DEFAULT_TIME_ZONE contract, `expect="real"`).
  - The production writers (`async_save` from `dt_util.now()`) never write a naive value under the upstream clock. They do write one under the stub's default naive clock.
  - So in the field the precondition is a corrupted, hand-edited or foreign store leaf, which is the premise of class P1 and of QuarantiningStore.
  - The other five escaping seams (pump_arbiter written shape, snapshot accuracy/learners, boost until) likewise need a malformed leaf. None needs the stub.
- **Severity by consequence:** once reached, every `_async_update_data` fails until the store is deleted, which takes the integration down. It needs corruption and has a workaround (delete the store), so **medium** is earned. It is not critical.
- **seam_rule:** it enumerates. `p1_store.py` seeds 13 of 13 store constructions (grep of `QuarantiningStore(`/`Store(` outside store.py gives 13) and substitutes every leaf. The downstream consumer set (publish, best_restore, restore service, roll_month, savers) is a named list, not enumerated. A consumer outside it would be missed.
- **Class:** P1 confirmed.
- **Vote:** verify, medium.
- **Metric:** raising calls, on the real-HA clock shape, per single-leaf naive legionella store payload.

## D14-s1-02 (P6 horizon_hours unproduced; boost_calls probe)
- **Re-run:** `p6_keys.py` gave p6_unproduced_reads=2, p6_undefined_getattr=1 and p6_dangling_entity_ids=0, all exact. load1 0.41, thread_factor 1.000.
- **My number:** arm `p6` ran an AST scan of the package. It found 0 writes of a `horizon_hours` attribute, subscript or dict key outside sensor.py, and 0 `horizon_hours=` keywords. So `OptimizationConfig.horizon_hours` holds its default 24.0 (`optimizer.py:1195`) on every install. The sensor fallback of 24.0 (`sensor.py:1482`, `:1515`) therefore publishes the true value today. The defect is latent: it is a silent fallback that would go wrong the day the horizon becomes configurable.
- **boost_calls:** `getattr(coord, "boost_calls", None)` (`boost.py:212`) finds nothing on the real coordinator. In real HA, `persist()` always runs. Only `tests/harness.py:348` defines `boost_calls`, so the suite skips `persist()` on every `set_channel` call. That is a test-double divergence with no production consequence.
- **Reach:** both reads are reachable in real HA, and neither publishes a wrong value there today.
- **Severity:** **low** (hygiene) is earned.
- **seam_rule:** does not enumerate. `p6_keys.py` records reads made by PLATFORM_LIST entity properties and diagnostics over 10 driven cells. It does not cover `hass.data` reads (the class's own detector_idea names them) or the card's reads of published attributes.
- **Class:** P6 is confirmed for horizon_hours. The boost_calls seam is P11 (a test double shaped to what the code needed), not P6.
- **Vote:** verify, low.
- **Metric:** production writes of the horizon_hours key or attribute (AST).

## D14-s2-01 (P2 two-zone / wood predicates re-derived at sibling seams)
- **Re-run:** `p2_facts.py` gave derive_preset_disagree=20/40, prefill_refused_or_missed=20/40, wood 2/21, null_control_disagree=0/20, 0 on every perturbed arm and house_mass_ratio 0.267 to 3.750. `--seams` gave two_zone 2, wood 16, dhw 11. All exact. load1 0.76, thread_factor 1.000.
- **My number:** arm `p2preset` calls production `config_flow._derive_preset` with default answers, against the same function recompiled with `two_zone := ThermalParameters.from_config(current).two_zone_enabled`.
  - It disagrees on 3 of 3 reachable shapes: mode=off with an upper key, mode=on with no key, and auto with a lower key only. Both controls agree (0 differing keys).
  - On default answers, `house_thermal_mass` is equal (ratio 1.000). The split still differs: slab_thermal_mass is 10.85 against 14.0, slab_heat_transfer is 0.7 against 1.4, and 6 zone keys are written or omitted.
  - So the finder's 0.267x/3.75x house-mass figures depend on the answers given (timber_slab, no foundation, radiators). The disagreement itself does not.
- **Reach in real HA:** the path is real.
  - The options-flow `building_preset` page derives from `{**entry.data, **options}`.
  - `thermal_model.py:997-1000` says the initial flow writes the zone keys into entry.data, where the options flow cannot erase them. So mode=off plus a surviving upper key is the designed state of every downgraded two-zone entry, not a contrived one.
  - Pure config-flow code: nothing in the path goes through hastub.
- **Severity:** the model silently gets the wrong slab and zone physics until the user re-derives. **Medium** is earned, and not inflated.
- **seam_rule:** enumerates. `--seams` extracts the proxy keys from the canonical predicates and lists every decision-context read of them (29 sites over 3 facts). It is also re-runnable with `--ref`.
- **Class:** P2 confirmed.
- **Vote:** verify, medium.
- **Metric:** reachable current-config shapes on which `_derive_preset` output differs from the canonical-predicate derivation.

## D14-s2-02 (P8 currency label from instance, not feed)
- **Re-run:** `p8_currency.py` gave A_unflagged_mismatch=8/12 (perturbed 0), B off-instance widgets 1 of 4 for EUR and NOK and 0 for SEK, card surfaces off-install currency 3 (4 before R7-D4-03), and 42 `--seams` sites. All exact. load1 1.40, thread_factor 1.000.
- **My number:** arm `p8cur`, with `hass.config.currency="SEK"` and a price entity whose unit is `EUR/kWh`.
  - `inputs.normalize_price_per_kwh(0.10, "EUR/kWh")` returns 0.1 unchanged.
  - `currency.resolve_currency` returns SEK, so the label mismatches (1).
  - `coordinator._audit_price_units` raises 0 issues, because the unit parses.
  - There is 1 literal `'SEK/m³'` unit in config_flow.py (line 1645).
- **Reach in real HA:** the path is real, and hastub plays no part.
  - `hass.config.currency` is upstream core config. `ha_contract.py` has no currency contract, and the harness pins SEK (`tests/harness.py:299,327`), so the suite only ever runs with label currency equal to feed currency.
  - Any price entity whose unit carries an ISO code different from the instance currency takes this path. The code comment "The currency itself is never converted" states the behaviour.
- **Severity:** a money sensor carries a wrong unit label while its number is internally consistent. The workaround is to set the feed or the instance currency to match. **Medium** is earned.
- **seam_rule:** enumerates. `--seams` lists every `resolve_currency` call, every `.currency` read, every unit parse that drops the money code, every literal unit in strings and translations, and every card resolver: 42 sites.
- **Class:** P8 confirmed.
- **Vote:** verify, medium.
- **Metric:** money surfaces whose currency token differs from the feed's declared code, with no repair issue.

## D14-s2-03 (I4 roster/grammar readers disagree)
- **Re-run:** `i4_roster.py` gave intake_admits_schema_refuses 11 of 22 (perturbed 0), ledger_ids_no_d14_seat=1 (P11), check_scopes_D14_ok=True (False once the axis equals the ledger) and null control 0 of 17. `--seams` gave 31 reader sites. All exact. load1 0.76, thread_factor 1.000.
- **My number:** arm `i4` loads bugclasses.json (16 ids) and walks scopes.json's D14 subtree directly. 1 ledger id, P11, is absent.
- **Reach:** not a Home Assistant path. This is an instrument in the audit workflow, and it is reached on every round's intake (audit-find.js).
- **Severity:** a class with no finder seat, and malformed ids admitted at intake that the schema refuses downstream. That is bounded process cost, so **low**.
- **seam_rule:** does not enumerate. `--seams` greps for class_guess, CLASS_GUESS, bugclasses.json and axis tokens. The finding-id grammar half is listed only where it shares a line with those tokens (audit-find.js:304). Other id-pattern readers are not listed: `finding.schema.json:71` appears only for its class enum. `--dims` covers the dimension roster separately.
- **Class:** I4 confirmed.
- **Vote:** verify, low.
- **Metric:** ledger class ids absent from scopes.json's D14 subtree.

## D14-s3-01 (P3 22 floor/raw quantity groups)
- **Re-run:** `p3_floors.py` gave 22 groups, 6 raw-divisor and 1 capacity, all exact. load1 0.76, thread_factor 1.000.
- **My number:** an independent AST count found 173 builtin `max(Q, c>0)` two-argument sites, plus numpy floors the rule does not parse: 11 `np.maximum(Q, c>0)` and 4 `np.clip(Q, c>0, …)`, 15 sites in all.
- **Reach:** the finder's own spot-check says no floor sits above its schema minimum, so no seam is reachable from the UI. I found nothing that contradicts that. The dt/dt_hours groups at 1e-6 are guards on quantities floored at 1 minute upstream.
- **Severity:** **low**/hygiene is earned.
- **seam_rule:** does not enumerate. `p3_floors.py` matches only `ast.Name` `max` with two arguments (`p3_floors.py:121`), so a new floor written as `np.maximum`/`np.clip`/`np.fmax` would not appear.
- **Class:** P3 confirmed.
- **Vote:** verify, low.
- **Metric:** positive-constant floor sites by call form (builtin max vs numpy).

## D14-s3-02 (P4 non-stationary multi-start stops)
- **Re-run:** `p4_seeds.py --cells full` reproduced every figure bit for bit: 30 seam calls, 12 bracket misses, 12 tol misses, 3 flat misses each, max tgap 0.5224 %, max gap 0.8915 %, drop-best mean 0.0939 %. wall 584.5 s provisional, load1 2.20, thread_factor 1.000.
- **My number:** arm `p4alt` ran the finder's quick grid with the tight arm at a *moderate* stop (ftol 1e-9, gtol 1e-7) instead of 1e-12/1e-9.
  - It gave p4_tol_misses 2 of 9 seam calls, the same max tgap of 0.5224 %, and 3 flat misses. load1 2.41, thread_factor 1.000.
  - So a stop 1000 times tighter than production's ftol 1e-6 already moves the shipped point by the full gap. The non-stationarity is not an artefact of an extreme tolerance.
- **Null control:** it fails (3 of 4 topologies still miss at flat prices), and the finder says so. That is why no money is claimed. The gap is objective-level (cost plus comfort terms).
- **Reach:** the solver is pure numpy/scipy, and the same code runs in the HA executor worker.
- **Severity:** at most 0.52 % of objective, no money claim. **Low** is earned.
- **seam_rule:** enumerates. Every scipy `minimize` in the package goes through `_scoped_minimize` inside `_multi_start_minimize` (`optimizer.py:322-324`, `:494`, `:635`), whose two callers (`:3484`, `:4019`) are both hooked. The cells sampled only winter_cold weather.
- **Class:** P4 confirmed, on its stop-tolerance half.
- **Vote:** verify, low.
- **Metric:** seam calls whose production score exceeds the same candidates re-solved at ftol 1e-9/gtol 1e-7 by more than 0.1 %.

## D14-s3-03 (P5 sysid gate keyed on half-width)
- **Re-run:** `p5_gate.py` gave 72 cells, 39 admitted, p5_admitted_over_bar=3 (all from the gains source), null 0, worst error 21.431 %, worst blended shift 7.970 % and monotone_breaks 0/15. `--seams` gave 19 sites in 13 functions. All exact. load1 1.40, thread_factor 1.000.
- **My number:** arm `p5grid` drives the finder's plant driver over a magnitude grid the finder did not run: 0.3, 0.5, 0.6, 1.0 and 1.2 kW of undeclared free heat.
  - typical_slab first admits over the bar at **0.5 kW** (error -13.38 %, hw 0.0617), and at 1.2 kW it admits -32.20 % with hw 0.0805. That is still under ln 1.1 = 0.0953.
  - heavy_old first admits over the bar at **0.6 kW** (error -9.11 %, log error 0.0955 > 0.0953), and at 1.2 kW it admits -18.21 % with hw 0.0368.
  - Admission is 1 at every magnitude, so the gated quantity never approaches the bar while the error grows without bound in this range.
- **Reach in real HA:** the path is real. The prior is wired from the declared internal_gains in production (`coordinator.py:2365`, `gains_prior_kw=float(ctx._thermal_params.internal_gains)`). The fit and gate are pure Python with no stub symbol in the path. A few hundred watts of night-time free heat missing from the declaration is ordinary.
- **Severity:** a biased UA is adopted at partial weight, giving a blended heat-loss shift of up to -8 %. **Medium** is earned.
- **seam_rule:** enumerates. `--seams` lists all 19 sites writing learned thermal parameters. The sweep drives only the UA adoption seam; the other 12 functions are listed but not measured.
- **Class:** P5 confirmed.
- **Vote:** verify, medium.
- **Metric:** the smallest undeclared free heat (kW) at which `adoption_decision` admits |ln(UA_fit/UA_true)| > ln 1.10.

## D14-s4-01 (P7 wall-clock datetime arithmetic across DST)
- **Re-run:** `p7_dst_seams.py` gave wrong_sites=9 (spring 8, autumn 9), grid_skewed_cycles 42 of 48 on all six transition days with a 60 min maximum skew, plain days 0, and cycle_errors 0. `p7_static_sites.py` gave 74 candidates, 9 reached and 1 reached site missing from the candidate list. All exact. load1 2.77, thread_factor 0.997.
- **My number:** arm `p7grid` calls production `HeatPumpOptimizerCoordinator._forecast_arrays` directly, with `now` built on the real `zoneinfo.ZoneInfo("Europe/Stockholm")` rather than the hastub clock. It captures the `(midnight, step_offset)` handed to `_price_series` and compares step 0 of production `_utc_step_starts` with now floored to 15 min in UTC, at every real 15-minute instant of each day.
  - 516 of 672 transition-day instants are skewed: 84 of 92 on each spring day, 88 of 100 on each autumn day, 60 min maximum.
  - The plain day gives 0 of 96.
  - Perturbation: the same instants with tz=UTC give 0 of 672, and with a fixed +01:00 tzinfo 0 of 672. The skew exists only under a ZoneInfo whose instance is shared, which is exactly the tzinfo upstream hands.
- **Reach in real HA:** the path is real, and more reachable there than in the suite.
  - `ha_contract.py` records `util.dt.DEFAULT_TIME_ZONE` and `as_local` as D (divergent, #577). The stub has no zone unless HASTUB_TZ is set, while upstream always carries the instance zone.
  - So every default-mode lane runs on a naive clock where this path cannot misbehave, and every real install runs on the ZoneInfo clock where it does, twice a year.
- **Severity:** a wrong published value. The price and weather grid is misaligned by 60 min for about 21 h per transition day, and `next_optimization` is off by 1 h. That is **high**. It is not critical, because it is bounded to 2 days a year.
- **seam_rule:** does not enumerate.
  - The dynamic rule lists only the sites the synthetic day drives.
  - The static list is a heuristic that missed 1 reached site. It also lists shape-identical candidates that were never driven: `pump_arbiter.py:372` `now - held.dhw_since`, where both come from `dt_util.now()` (`pump_arbiter.py:519`), and `snapshots.py:77`. These are candidates, not measured instances.
- **Class:** P7 confirmed.
- **Vote:** verify, high.
- **Metric:** 15-minute instants on DST days where step 0 of the production grid differs from now floored to 15 min in UTC.

## D14-s4-02 (replay lane freezes a fixed-offset clock)
- **Re-run:** `p7_replay_clock.py` gave replay_wrong_sites=0 on all three days. `--zone-clock` gave replay_wrong_sites=10 (spring 10, autumn 9, plain 0, cycle failures 0). Both exact. load1 3.82 / 2.40, thread_factor 0.996.
- **My number:**
  - `grep -n 'dt_util.freeze(' tests/*.py` (the finding's seam rule) gives 56 non-None freeze calls in 7 files.
  - It misses aliased freezes of the same module in `tests/features.py` (`_bo_dt.freeze(` at :11825 and `_dt5.freeze(` at :15937 and :16934).
  - `tests/replay/` holds 1 fixture, `synthetic-dhw-only.json`, and no DST day.
- **Reach:** the defect is real in the instrument: `replay._ts` is `datetime.fromisoformat`, a fixed-offset tzinfo that upstream never hands. With no DST-day fixture in the lane, however, it currently has no observable consequence. The blindness bites only once a DST export is added, which the finding's own fix scope proposes.
- **Severity:** I would give **low**. The claimed medium rests on the D14 stop rule leaning on a replay that has no DST day to replay whatever its clock.
- **seam_rule:** does not enumerate. The grep misses aliased `freeze` calls, as above.
- **Class:** corrected from P7 to P11. The defect is a test double's clock whose tzinfo identity is not what Home Assistant hands; P7 is the class it hides. The finder's mechanism names this shape itself.
- **Vote:** weaken, low.
- **Metric:** DST-day fixtures in the replay lane, plus freeze call sites the grep rule misses.

## D14-s5-01 (Python closures blind to child processes)
- **Re-run:**
  - `closure_divergence.py` gave seams=31 (doc_claims 9, deployment_shape 22, all python-child reads of measured files) and 0 for guard_pins/structure/typing_ruler.
  - `stub_scope_probe.py` gave control_green=1, edited_red=1 and red_and_skipped=1. It edits a `mkdtemp` copy, not the shared tree.
  - All exact. load1 3.41, thread_factor 1.000.
- **My number:** arm `closure` calls production `tests/closure.py:select([f])` for every tracked `tests/hastub/**.py` file.
  - 32 of 32 files come back mode `scoped` with `tests/deployment_shape.py` skipped.
  - Perturbation: with deployment_shape's closure unioned with those files in memory (a temp copy of closures.json), the count is 0.
- **Reach:** this is the real CI path, not a Home Assistant path. `GATE_SCOPE=auto` on every PR branch selects through this function. The cost is bounded by CLAUDE.md rule 1: a push to main forces full, so main turns red within one merge instead of the PR.
- **Severity:** **medium**, bounded cost as defined in COMMON.md.
- **seam_rule:** enumerates. `closure_divergence.py --scripts <every selectable script>` records every child read under `strace -f`, and the heavy set was run too (883).
- **Class:** I2 confirmed.
- **Vote:** verify, medium.
- **Metric:** tracked hastub .py files whose single-file change is selected `scoped` with deployment_shape.py skipped.

## D14-s5-02 (mutation inventory blind to multi-line / numpy / ternary guards)
- **Re-run:** `guard_inventory.py --history --list` gave uncovered=528 of 2313 (EXIT 52/1346, CLAMP 246/668, TERN 230/299). The fixture gave 0 clean and 1 re-introduced, and the ratchet probe gave delta 1 against 0 with refusal 1 against 0. All exact. load1 1.10.
- **My number:** arm `guards`, with my own shape definitions, against production `tests/mutation_table.py:candidates`.
  - (a) `ast.If` with a test spanning more than one line and a body ending in return/raise/continue/break: 46, all 46 without a GUARD_OFF candidate. That equals the finder's multi-line-test count.
  - (b) `np.clip(...)` calls: 98, of which 93 have no CLAMP_DROP.
- **Attack:** is a multi-line guard still reached by another operator on its body (for example RETURN_DEL)? Only 3 of the 46 have any candidate on a body line (RETURN_DEL 1, GUARD_OFF 2), so 43 are wholly invisible and the gap stands.
- **Recorded evidence:** the finder's `--history` arm places two of the six ledger I1 guard instances in the invisible shapes: #1312 ternary and #1316 np.clip.
- **Reach:** instrument only. The consequence is a ratchet that does not count a new undispositioned guard of these shapes.
- **Severity:** **medium**, bounded.
- **seam_rule:** enumerates. `guard_inventory.py --list` walks the AST of the whole package for the three shapes the property names.
- **Class:** I1 confirmed.
- **Vote:** verify, medium.
- **Metric:** multi-line-test exit-ifs and np.clip calls with no covering `candidates()` site on their line.

## Tally
11 verify, 1 weaken (D14-s4-02, medium to low), 0 refute, 0 unresolved.
