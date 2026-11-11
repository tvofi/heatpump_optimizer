# Round 10 catch-up judgment

This rules on the 50 findings in `CATCHUP-VERIFY.json` (f6b810f7f), under `dev/governance/roles/judge.md`. Every header command and perturbation was re-run on `origin/main` d749c986d by the judge, serially, from one worktree. Prototype trees were extractions of `custom_components`, `tests` and `tools` with the patch applied. The verdicts are the judge's. The votes are quoted, not counted. The per-finding record (value, perturbation, void, null control, main-judge comparison, note) is `CATCHUP-JUDGE.json` beside this file.

- **Box.** macOS arm64, shared. Counts are contention-immune. Each timing row quotes its own `load1` and `thread_factor`. Timing rows ran at load1 3.3 to 6.2 and thread_factor 1.000 to 1.038. One arm read 1.062 and was re-taken at 1.032. The D9-s3 arms ran under the gate lease.
- **Void rule.** D9-s1-02's own perturbations do not move. The verifier's arms do not move it either, so it is refuted. D7-arch2-11 and D7-s3-81 rest on `--sign-blind`, which is void (3 → 3, 4 → 4), but the verifier's non-finite refusal and patch 03 move both, so they survive as weakened. The hot_water_pumps label has no perturbation of its own, and the verifier's `--mislabel` moves it.
- **Disputes.** D-2 is refuted. The finder's oracle feeds `adoption_decision` `(U+Lr)s`, which the production fit never returns. End to end, r 1.0 → 1.6 moves the adopted error −0.0008 → −0.0007. L4 is refuted: 0 of the keys the guard reads go stale, and the widened-fold control moves 0 → 1. D9-s1-02 is refuted on a quiet re-take: the shipped max gap is 11.8 ms, not ~124, and neither yield arm moves it in the stated direction.

## Dedup (perturbation-cross)

- **D7-s6-91 → D12-s3-01.** D12-s3-01's perturbation on `setpoint_unit.py` gives 42.222 → 0.000 K. P2 on `surface_units.py` gives 2 → 0 cells. Both nulls read 0. The real-HA oracle reads 42.222 → 0.000. ARCH3-s6-P2 is the fix prototype carried to #2243.
- **D7-s3-81 → D7-arch2-11 (D7-s2-61).** Patch 03 on arch2-11's harness reconciles 1e400 (3 → 2). `--sign-blind` moves neither harness.
- **ARCH3-s6-P1 → D7-s4-8x-layering.** s4-P1 takes store, notifier and debugger out of the solver closure on s6's `runtime_closure.py`, which is every cell s6-P1 claims. s6-P1 moves only 2 of 5 cells on s4's harness. ARCH3-s6-P4 (legionella) stays separate, because s4-P1 leaves legionella IN.
- **Already registered.** 20 rows carry main-register ids (D7-s2-51..61, D7-s3-51..54, D2-s3-71/72/73, D2-s1-71, D12-s2-71). They were re-measured, not re-filed. Where this ruling differs from the main judge, the row says so.

## Verdicts

| id | register | verdict | severity | stop | class | target | value (judge) |
|---|---|---|---|---|---|---|---|
| D9-s1-01 |  | weakened | low | bug | N-solve-recompute | class exists, no R10 issue: proposed issue (not filed) | cont sse/grad 192 (+96 cont_fun) -> 97 fused, total SSE 62121 -> 53717; capture CPU 1379-1395 -> 1307-1323 ms (-5.5 %), 3 interleaved reps, load1 4.6-4.8, thread_factor 1.000 |
| D9-s1-02 |  | refuted | low | bug | P10 | none (refuted) | max loop gap at load1 3.3-5.2: shipped 11.7-11.8 ms (finder ~124 ms); noyield 11.6-14.1; realsleep 11.5-11.8 (gil.py, 2 runs x 3 reps, thread_factor 1.024-1.038, one 1.062 arm re-taken at 1.032). Interleaved gil_null.py 5 reps, load1 4.89, thread_factor 1.030: shipped 20.6, noyield 11.8, realsleep 11.7, idle 2.2, process 1.3 ms |
| D9-s3-01 |  | verified | medium | bug | I1 | #2219 | flagged_solve_arm 0 of 5 at 2x solve CPU (median x1.984); budget margins 0.62-0.86; load1 3.80, thread_factor 1.002 |
| D7-arch2-01 | D7-s2-51 | weakened | low | hygiene | P2 | #2238 | escapes 0 at baseline, 17 with patch 01 alone, 0 with 00+01; probe_scrub_mixin nan_published 1 -> 0 under 00, mixin_supplied 0 |
| D7-arch2-02 | D7-s2-52 | verified | low | hygiene | P2 | #2238 | delta_S +2.6888, duplication 68 -> 55 |
| D7-arch2-03 | D7-s2-53 | verified | low | hygiene | P2 | #2238 | delta_S +0.9689, 68 -> 63 |
| D7-arch2-04 | D7-s2-54 | verified | low | hygiene | P2 | #2238 | delta_S +0.3789, 68 -> 66 |
| D7-arch2-05 | D7-s2-55 | verified | low | hygiene | P2 | #2238 | delta_S +0.1880, 68 -> 67 |
| D7-arch2-06 | D7-s2-56 | verified | low | bug | P2 | #2238 | delta_S +1.1717 (68 -> 62); probe_rerender: 9 cleared stored slots re-render the stored entity at baseline, 0 patched |
| D7-arch2-07 | D7-s2-57 | verified | low | hygiene | P2 | #2238 | implementations 5, disagreeing hours 2 (23.999, 24.0) |
| D7-arch2-08 | D7-s2-58 | verified | low | hygiene | P3 | #2239 | implementations 9, disagreeing inputs 10 of 17 |
| D7-arch2-09 | D7-s2-59 | verified | low | hygiene | P2 | #2238 | tokens 522, mismatches 0; delta_S +0.1880 |
| D7-arch2-10 | D7-s2-60 | verified | low | hygiene | P6 | #2242 | implementations 35, families 4, driven 26, answer vectors 5, disagreeing probes 3 |
| D7-arch2-11 | D7-s2-61 | weakened | low | bug | P1 | #2236 | 4 parsers, 3 disagreeing states (-0.4, 0, 1e400 kW); inf/1e400 -> silent cap 6.0 kW = p_max, identical to a finite 100 kW |
| R10-ID-01 | D2-s3-71 | verified | medium | bug | N-confounded-learner | #2223 | slopes P0 +0.1795, P1 +0.2536, P2 +0.0940, P3 +0.2206, P4 +0.1614, P5 +0.1907 (20 jobs rc 0); drop-most-favourable (P1) +0.0940..+0.2206; thread_factor 1.000 |
| R10-ID-02 | D2-s3-72 | verified | medium | bug | P5 | #2241 | vent_tripped_share 0.187 (P0) / 0.172 (P1) at delivery 0.4, 0 at 1.0; production _learning_frozen: 0.984 / 0.983 frozen at 0.4, learner stalls at UA bias +0.19 / +0.18 |
| D-1 | D2-s1-71 | verified | low | bug | P3 | #2239 | space_demand_rel_diff 0.4367 (7.741 vs model-consistent 11.122 kW); V2 -0.2213 at r=1.6 |
| D-2 | D2-s3-73 | refuted | low | hygiene | P3 | none (refuted); remove from #2239 | end to end (production sysid.step + identify_slab + adoption_decision, s=1.0): adopted/true effective UA - 1 = -0.0007 at r=1.6, -0.0006 at r=1.3, -0.0008 at r=1.0; fit heat_loss_kw_per_c 189.9 W/K = (U+L)s |
| D-3 | D12-s2-71 | verified | medium | bug | P3 | #2239 | options reseed: upper 0.3681, lower 0.2145, house 0.0011 (ratio kept 1.922, scale re-anchored 0.632); V2 lower +0.1816, upper -0.2615 |
| D7-s1-82 | D7-s1-82 | verified | low | hygiene | N-shared-config | #2232 | main: holder_mutated 1, torn_at_await 6, unclamped_at_await 1 (room_thermal_mass 0.1 < floor); V2 mixed 3/3, unclamped_hub 3, unclamped_solve 0 |
| D7-s1-83 | D7-s1-83 | verified | low | hygiene | N-structure-blind | #2235 | proto: via_live_model, via_guard_reader, via_learner_reader unseen (23 -> 23); main: all seen (38 -> 39) |
| ARCH2-s2-P1 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.0588; 0 shared sites (coord_footprint + multiassigned_attrs only) |
| ARCH2-s2-P2 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.3513; 1 shared site removed |
| ARCH2-s2-P3 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.3519; 1 shared site removed |
| ARCH2-s2-P4 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.0011; 0 shared sites; event_hub_inplace_writes 3 -> 0 |
| ARCH2-s2-P5 |  | verified | low | hygiene | _unclassified | none: architecture-score gain with no defect mechanism (bugclasses _unclassified) | delta_S +0.5305; 0 sites (params_over_10 only) |
| ARCH2-s2-P6 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.7300; 2 shared sites removed |
| ARCH2-s2-P7 |  | verified | low | hygiene | N-shared-config | #2232 | delta_S +0.7652; 2 shared sites removed |
| D7-arch3-01 | D7-s3-51 | verified | low | hygiene | N-structure-blind | #2235 | blind_keys 10 (census 166, runtime 169); fixture_blind 10 |
| D7-arch3-02 | D7-s3-52 | verified | low | hygiene | N-structure-blind | #2235 | Any/object/NotRequired[Any]/typing.Any/Required[Any] 6; Any\|None, Optional[Any], 'Any', alias, Union[Any,None], Annotated[Any], 'Optional[Any]', Any\|int 0 |
| D7-arch3-03 | D7-s3-53 | verified | low | hygiene | N-name-sort | #2228 | plant splits 2 / C6 0; game splits 0 / C6 0; 4 of 4 further victims evade |
| D7-arch3-04 | D7-s3-54 | weakened | low | hygiene | N-shared-config | #2232 | synthetic race leaks 700284 of 2130323 reads (1 us switch), 1077088 of 3876621 at the default 5 ms; production: in_optimize_floorless 0 over 50 solves, off_main_thread 0, loop_floorless 2 (both on the loop) |
| D7-s3-8x-tariff |  | verified | low | hygiene | P2 | #2238 | delta_S +0.3789 (01, 68 -> 66) / +0.1880 (01b); equiv_tariff 0 of 8160 mismatches on both |
| D7-s3-8x-slotfloor |  | verified | low | hygiene | P2 | #2238 | implementations 4, disagreeing 0 of 10; patch 02: 3 implementations; delta_S 0.0000; V2 0 of 24686 instants |
| D7-s3-81 |  | merged | low | bug | P1 | #2236 (as D7-s2-61) | silent cap 6.0 kW on inf and 1e400 -> 3.6 kW with patch 03; implementations 4 -> 2 |
| D7-s4-8x-layering |  | verified | low | hygiene | N-leaf-imports-solver | new class (proposed, not filed) | static closure store 28 (optimizer IN) -> 21 out, snapshots 29 -> 22, setpoint_check 22 -> 13, quiet_windows 21 -> 11, silent_mode 20 -> 8; runtime store 29 -> 22, optimizer 1 -> 0 on all five |
| D7-s4-81 |  | verified | low | bug | P1 | #2236 | load_prelude raising_seams 1 (Notifier.async_load, AttributeError on 'x'); real HA 2026.9.3: setup_raises 2 of 2 non-mapping arms |
| D7-s4-8x-fabric |  | verified | low | hygiene | N-order-coupling | new class (proposed, not filed) | main: production order lower 12/12, swapped order lower 0/12; P3: 12/12 both orders |
| ARCH2-s5-C1..C4 |  | verified | low | hygiene | P2 | #2238 | card shapes 33 -> 9, dead 1 -> 0 (C1 31, C2 31, C3 18, C4 28); union: card_drift 40/40 identical, card_pages_drift 18/18, card.mjs ALL PASSED |
| ARCH2-s5-F1 |  | verified | low | hygiene | P2 | #2238 | spelled_twice 44, disagree 0 at main; F1: spelled_twice 0 |
| ARCH2-s5-hot_water_pumps-label |  | verified | low | hygiene | I5 | #2222 | menu_disagree 1 of 23 (advanced.hot_water_pumps), en label_vs_title 1 of 23 |
| D7-s6-91 |  | merged | high | bug | P8 | #2243 (as D12-s3-01) | setpoint_unit defect 42.222 K, null 0.000 (load1 6.18, thread_factor 1.004); real HA 2026.9.3 imperial: payload 55.0 -> device 12.778 C |
| ARCH3-s6-P1 |  | merged | low | hygiene | N-leaf-imports-solver | new class (proposed, not filed) | runtime store 29 -> 20, notifier/debugger 30 -> 21, solver IN -> out, import 396 -> 180 ms (K=3, load1 5.4-5.7, thread_factor 1.000); delta_S +0.0006 |
| ARCH3-s6-P2 |  | verified | high | bug | P8 | #2243 (fix prototype for D12-s3-01) | P1+P2 delta_S +0.0028 (P2 alone +0.0022); setpoint defect 42.222 -> 0.000 |
| ARCH3-s6-P3 |  | verified | low | hygiene | P2 | #2238 | store_report_equiv 36279 pairs, 0 mismatches; e2e debugger.store_report 10506 pairs, 0 mismatches, 0 exceptions |
| ARCH3-s6-P4 |  | verified | low | hygiene | N-leaf-imports-solver | new class (proposed, not filed) | legionella runtime closure 31 -> 22 modules, solver+scipy IN -> out, import 399 -> 182 ms (load1 5.5, thread_factor 1.000); private_reach 21 -> 17 over P1..P4 |
| L1-smart-write-unit |  | verified | medium | bug | P8 | #2243 | valve target on a degF climate and on a degF-declared number: written 21.0 for 69.8 (abs err 48.8); _command_valve_target has no unit conversion |
| L2-bounded-climate-keys |  | verified | low | bug | P6 | #2242 | _bounded on a climate {min_temp 7, max_temp 50}: 3 of 4 values out of range; reach: desired(duty='dhw') commands 55.0 to a 50-max climate |
| L3-restore-session-race |  | weakened | low | bug | N-restore-race | new class (proposed, not filed) | 3 of 3 interleavings (away-off, boost cancel, _resolve_away replace) differ from serial order |
| L4-legionella-stale-config |  | refuted | low | hygiene | N-shared-config | none (refuted) | in-process replace leaves 3 quiet-window keys stale in the guard's context (M1 3) but 0 keys the guard reads (M2 0); options path reloads (1 reload) |

## Where this ruling differs from the main judge (JUDGE.json on handoff/audit-r10-register)

- **D7-arch2-11 (D7-s2-61).** unreproduced low hygiene P3 -> now weakened, re-classed P1 (an out-of-domain power reading crosses into the cap unguarded; inf_changes_decision=1)
- **R10-ID-02 (D2-s3-72).** verified HIGH -> medium: reach starts below delivery 0.5 (0 at 0.6 and above on both houses), i.e. a meter or COP off by 2x
- **D7-arch2-06 (D7-s2-56).** verified low hygiene -> bug: a cleared entity slot re-renders as the stored entity on a rejected options form (9 of 9 slots, 0 patched, null 0)
- **D-1 (D2-s1-71).** verified MEDIUM -> low: the only consumer of _space_demand_kw is the external-heat detector's evidence (coordinator.py:4460); the solve and the model do not read it
- **D-2 (D2-s3-73).** verified medium P3 -> REFUTED (conflict: the main judge re-ran the finder's oracle, which is the wrong basis)
- **D7-arch3-04 (D7-s3-54).** verified low BUG -> hygiene: no production reader of the floorless channel runs on another thread, so the race is not reachable today

## Survivors by target issue

- **#2219.** D9-s3-01 (medium)
- **#2222.** ARCH2-s5-hot_water_pumps-label (low)
- **#2223.** R10-ID-01 (medium)
- **#2228.** D7-arch3-03 (low)
- **#2232.** D7-s1-82 (low), ARCH2-s2-P1 (low), ARCH2-s2-P2 (low), ARCH2-s2-P3 (low), ARCH2-s2-P4 (low), ARCH2-s2-P6 (low), ARCH2-s2-P7 (low), D7-arch3-04 (low)
- **#2235.** D7-s1-83 (low), D7-arch3-01 (low), D7-arch3-02 (low)
- **#2236.** D7-arch2-11 (low), D7-s4-81 (low)
- **#2238.** D7-arch2-01 (low), D7-arch2-02 (low), D7-arch2-03 (low), D7-arch2-04 (low), D7-arch2-05 (low), D7-arch2-06 (low), D7-arch2-07 (low), D7-arch2-09 (low), D7-s3-8x-tariff (low), D7-s3-8x-slotfloor (low), ARCH2-s5-C1..C4 (low), ARCH2-s5-F1 (low), ARCH3-s6-P3 (low)
- **#2239.** D7-arch2-08 (low), D-1 (low), D-3 (medium)
- **#2241.** R10-ID-02 (medium)
- **#2242.** D7-arch2-10 (low), L2-bounded-climate-keys (low)
- **#2243.** L1-smart-write-unit (medium)
- **#2243 (fix prototype for D12-s3-01).** ARCH3-s6-P2 (high)
- **class exists, no R10 issue: proposed issue (not filed).** D9-s1-01 (low)
- **new class (proposed, not filed).** D7-s4-8x-layering (low), D7-s4-8x-fabric (low), ARCH3-s6-P4 (low), L3-restore-session-race (low)
- **none: architecture-score gain with no defect mechanism (bugclasses _unclassified).** ARCH2-s2-P5 (low)

## New classes proposed (not filed)

- **`N-leaf-imports-solver`.** A leaf module (store, notifier, debugger, legionella, setpoint helpers) reaches the solver and scipy through one misplaced symbol, so importing the leaf loads the optimizer (~400 ms in a fresh interpreter) and couples it to the solve. Nearest `I2`. It differs because I2 is a measured closure that diverges from the real dependency graph; here the graph itself is wrong (a production import edge into the solver), and the closure measures it faithfully.
- **`N-restore-race`.** A restore applies persisted state after an await during which a writer changed the same state, so the stale snapshot overwrites the live write (or the write lands on an object the restore then replaces). Nearest `N-restart`. It differs because N-restart loses a user-set state because the setter persisted too late or not at all; here persistence is correct and the defect is restore-vs-writer ordering inside the load await.
- **`N-order-coupling`.** Two sibling updaters consume one shared interval and the first closes it destructively, so correctness depends on call order that only a comment and a source-order test hold. Nearest `P2`. It differs because P2 is one fact decided twice by divergent predicates; here there is one predicate and one consumer starves the other through a shared, destructively-read state.

`N-solve-recompute` exists in `bugclasses.json` but has no round-10 issue. D9-s1-01 is its only survivor here, so an issue is proposed, not filed.

## Residuals to propagate (finding-propagation.md), not survivors

- **D-2.** The published `heat_loss_kw_per_c` (189.9 W/K) is the `(U+L)s` basis, not the effective UA the model uses (244.0 at r=1.6). This goes to the D5/D12 briefs as a display-basis question.
- **L4.** `CoordinatorContext` is documented write-once but is replaced at coordinator.py ~5901. Three quiet-window keys go stale in the guard's copy. This goes to the D7 brief.
- **D7-arch2-01 patch 00.** The verifier's probe reads `nan_published_outside_pkg` 0 → 1 under patch 00, which goes to the fixer brief.
- **D7-arch2-11 fix.** A finite absurd reading (100 kW) still gives the 6.0 kW cap after patch 03, so the fix needs a range bound.
- **D7-s1-82.** P1's delta_S is partly the D7-s1-83 census blind spot. Re-derive it after the census is extended.
- **ARCH2-s2-P6.** The cursor now advances before the await, so a cancellation skips a spec.
