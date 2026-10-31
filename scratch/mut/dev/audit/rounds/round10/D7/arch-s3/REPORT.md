# ARCH-s3 report (D7, round 10)

The 30% target cannot be reached in my cells: the honest maximum is delta_S = 0.0000. Both weighted cells are already at their floor on baseline `554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef`: `untyped_payload_keys` = 0 and `family_splits` = 0. The term `w·log2((0+1)/(c+1))` can never be positive, and the four tripwires carry weight 0. My cells weigh 12.3705 of 39.1841, and 30% of their share is 0.0000. I report no opportunity that moves the score.

What I found instead is three holes in the instruments for my own cells and one real defect behind a tripwire site. Each has a prototype, and every prototype reads delta_S = 0.0000 and admissible.

**REPORT.md was not written.** The harness refused the file ("Subagents should return findings as text"), so its full content is in this message. The orchestrator may commit it as `dev/audit/rounds/round10/D7/arch-s3/REPORT.md`. Harnesses and `.patch` files are committed at `e0a2e91bdf1f047a265b852c9a68b16295d786ff` and pushed only to `handoff/audit-r10-arch-s3`. The scratch branch `proto/arch-s3` is local only and not pushed (`52f0de63` = prototypes 01–03, `c402bce8` = plus 04); the patches are the artefact.

**Schema mismatch:** `finding.schema.json` requires ids like `^D7(-s[0-9]+)?-[0-9]{2}$` and a scope like `D7-s<n>`. The ids `D7-arch3-NN` your brief asked for fail that pattern. I kept your ids and used scope `D7-s3`; the orchestrator needs to map them.

## Behaviour preserved (prototype `c402bce8`, all four applied)
The scoped gate printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out` and took 7458 s.
- **Golden drift:** `env_drift --all` reported NO UNCLAIMED DRIFT over 56 scenarios, with every coordinator fixture byte-identical.
- **Card:** `card_drift.mjs` was identical in all 40 states.
- **Score calibration:** `tests/arch_score.py` passed with prototypes 01–03 active.
- **`tests/entities.py`:** 1 of 2303 checks failed. The mutation ledger pins the two old `step_duty` BOOLOP lines (`296c284b`, `399c5f97`) that prototype 04 rewrites. This is a pinned-line artefact a fixer re-keys, not a behaviour change.
- **`tests/stress.py`:** I killed it after 14 minutes at load1 around 60. It is unrun and left to CI.

## Findings

**D7-arch3-01 — the score's payload census cannot see the ten `away_*` keys (low, hygiene, N-structure-blind)**
- Production publishes 169 keys at runtime and the census sees 166; the 10 `away_*` keys are invisible to it.
- They arrive through `_fold_away(state: away_mode.AwayState)`, which returns `state.as_dict()`. The role engine gives an annotated parameter no type, so that call resolves to nothing.
- I re-declared all ten keys `Any` in a temp copy and the score still read 0; it should read 10.
- Prototype: a parameter annotated with a package class is treated as an instance of that class. Census 166 → 176, blind keys 10 → 0, and the perturbation now reads 10.
- Size: small, 1 module (`tools/audit/archscore/metrics/untyped_payload_keys.py`).

**D7-arch3-02 — counter C1 accepts four spellings of `Any` as typed (low, hygiene, new)**
- I re-declared the six `EnergyTotals` keys in each spelling. `Any`, `object` and `NotRequired[Any]` correctly read 6.
- `Any | None`, `Optional[Any]`, `"Any"` and a module alias `_Untyped = Any` all read 0. Each states no type and still counts as typed.
- Prototype: `is_any` now parses string annotations, treats any union with an `Any` member as untyped, unwraps `Optional`/`Annotated`/`Required`/`NotRequired`/`ReadOnly`, and resolves aliases of `Any`. All four now read 6; baseline still 0; the C1 ablation switch still works.
- Size: small, same module. The fixer owes a new red-team case.

**D7-arch3-03 — counter C6 accepts an invented two-member family (low, hygiene, N-name-sort)**
- I planted a split, which reads 2. I then declared `optimization_status` and `solar_surplus_forecast` one family, `zzpair`, because they sort next to each other in both languages. The split reads 0 and `family_orphan_overrides` stays 0.
- Prototype: an override also counts as an orphan when its target is not the first word of the entity's own English name. The game now reads 2; the five real overrides still pass.
- What stays open: a gamer must now also rename the visible name, which shows up as a translation diff in review.
- Size: small, 1 module (`tools/audit/archscore/counters.py`). It redefines a tripwire, so a verdict re-record may be needed (calibration passed in the gate run).

**D7-arch3-04 — `step_duty` passes the plan's modulation floor through a function attribute (low, bug, N-shared-config)**
- `pump_arbiter.step_duty` sets `planned_draw_runs.modulation_floor` with `setattr`, and a decorator resets it afterwards.
- `planned_draw_runs` reads that attribute whenever a caller passes no floor, so every other caller can read another plan's floor (`optimizer.py:5489/5497`, `coordinator.py:2294`, `draw_range.py`).
- This is a real race when the solve falls back to the thread executor. In a two-thread run, 437,525 of 1,419,348 reads returned the wrong answer; with the writer idle, 0.
- Prototype: pass `modulation_floor=floor` as the argument the function already declares, and delete the fallback, the decorator and two unused imports. Wrong reads go to 0, and `reflective_writes` goes 17 → 15 with no other metric moving.
- This is a real removal of a hidden global channel, not a rename.
- Size: small, 2 modules (`pump_arbiter.py`, `thermal_model.py`). The fixer re-keys the mutation ledger.

## Non-findings and the gaming guard
- **Sort order:** `family_splits`' sort matches Node's `Intl.Collator` for en and sv (0 inversions, 0 splits), and moves to 1 under the perturbation.
- **Families:** the 16 families and 5 overrides make sense to a user.
- **Payload contract:** it is enforced, not just annotated, by checks EG-B3/EG-B3b in `tests/entities.py` plus mypy.
- **Still open after my prototypes:**
  - a key declared `dict[str, Any]` still reads as typed. `payload.py` uses that deliberately for three open reports, so closing it is a policy call.
  - a translation rename can still make unrelated names share a first word.
- **The remaining 15 `reflective_writes` and 32 `computed_attr_access` sites** are bounded field-table loops. Spelling them out would not be better code.
- **`unread_private_globals` and `family_orphan_overrides`** are both already 0.

## JSON report
```json
{"dimension":"D7","baseline_sha":"554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef","exposure":"",
"coverage":[{"step":"D7.M1","depth":"deep","evidence":"archscore vector + details for untyped_payload_keys, family_splits and the 4 GATE_ONLY tripwires; 6 harnesses under dev/audit/rounds/round10/D7/arch-s3/"}],
"unfinished":[{"step":"D7.M1","what":"stress.py on prototype c402bce8 unrun (killed under load); red-team cases and expected.json re-record for 02/03 are fixer work"}],
"findings":[
{"id":"D7-arch3-01","scope":"D7-s3","step":"D7.M1","title":"untyped_payload_keys census is blind to the 10 AwayView keys","severity":"low","claim":"The census misses 10 of 169 runtime payload keys, so untyping them reads 0.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py --perturb","harness_path":"dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py","value":10,"unit":"keys","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 macOS, tvofi audit box","cpu_or_wall":"count","contention_note":"shared box, counts only","tolerance":"exact","load1":45.78,"thread_factor":1.0},"instrumented_symbol":"archscore.metrics.untyped_payload_keys:Flow.returned_keys; heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict","perturbation":{"change":"apply D7-arch3-01 patch","expected_direction":"to_zero","observed_value":0},"metric_definition":"|runtime payload keys over golden coordinator scenarios minus census produced keys|","phenomenon_property":"every key _async_update_data publishes is in the census key set","seam_rule":"dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py (runtime_not_census list)","null_control":{"command":"same, --perturb arm","value":"untyped-AwayView headline 0 before, 10 after","note":"headline stays 0 at baseline"},"stop_rule_class":"hygiene","class_guess":"N-structure-blind","files":["tools/audit/archscore/metrics/untyped_payload_keys.py"],"proposed_fix_scope":"small: Flow.seed types a package-class-annotated parameter (+17 lines)"},
{"id":"D7-arch3-02","scope":"D7-s3","step":"D7.M1","title":"C1 reads Any|None, Optional[Any], \"Any\" and an Any alias as typed","severity":"low","claim":"Four spellings of an untyped field read untyped_payload_keys=0 where Any reads 6.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py","harness_path":"dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py","value":"4 spellings read 0 of 6","unit":"keys","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 macOS, tvofi audit box","cpu_or_wall":"count","contention_note":"shared box, counts only","tolerance":"exact","load1":40.99,"thread_factor":1.0},"instrumented_symbol":"archscore.metrics.untyped_payload_keys:is_any","perturbation":{"change":"apply D7-arch3-02 patch","expected_direction":"up","observed_value":"6 for all four"},"metric_definition":"untyped_payload_keys headline with EnergyTotals' 6 fields declared in a given spelling","phenomenon_property":"any annotation admitting every value reads untyped","seam_rule":"dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py","null_control":{"command":"same","value":"float 0; ablated C1 Any 0"},"stop_rule_class":"hygiene","class_guess":"new","files":["tools/audit/archscore/metrics/untyped_payload_keys.py"],"proposed_fix_scope":"small: is_any union/string/alias handling (+45 lines) plus a red-team case"},
{"id":"D7-arch3-03","scope":"D7-s3","step":"D7.M1","title":"C6 accepts an invented two-member family that cures a split","severity":"low","claim":"Homing two unrelated adjacent entities into a new family takes family_splits 2 to 0 with family_orphan_overrides 0.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py","harness_path":"dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py","value":0,"unit":"orphan overrides on the game tree","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 macOS, tvofi audit box","cpu_or_wall":"count","contention_note":"shared box, counts only","tolerance":"exact","load1":39.87,"thread_factor":1.0},"instrumented_symbol":"archscore.counters:family_orphan_overrides","perturbation":{"change":"apply D7-arch3-03 patch","expected_direction":"up","observed_value":2},"metric_definition":"family_orphan_overrides on plant+pair-override tree","phenomenon_property":"an override homes an entity only into the family its own name leads with","seam_rule":"dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py","null_control":{"command":"same, honest arm","value":"0 splits, 0 orphans"},"stop_rule_class":"hygiene","class_guess":"N-name-sort","files":["tools/audit/archscore/counters.py"],"proposed_fix_scope":"small: +6 lines; red-team case; expected.json re-record if any verdict moves"},
{"id":"D7-arch3-04","scope":"D7-s3","step":"D7.M1","title":"step_duty hands the modulation floor to planned_draw_runs via a function attribute","severity":"low","claim":"A concurrent planned_draw_runs caller reads another plan's floor while step_duty runs.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py","harness_path":"dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py","value":437525,"unit":"wrong reads of 1419348","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 macOS, tvofi audit box","cpu_or_wall":"count","contention_note":"shared box; race count is scheduler-dependent, claim is >0 vs 0","tolerance":">0 vs 0","load1":38.35,"thread_factor":1.001},"instrumented_symbol":"heatpump_optimizer.pump_arbiter:step_duty; heatpump_optimizer.thermal_model:planned_draw_runs","perturbation":{"change":"apply D7-arch3-04 patch","expected_direction":"to_zero","observed_value":0},"metric_definition":"planned_draw_runs(0.5) returning False on thread B while thread A loops step_duty(floor=5.0)","phenomenon_property":"no planned_draw_runs input travels through module-global state","seam_rule":"dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py (reflective_writes_pump_arbiter)","null_control":{"command":"same, writer idle arm","value":0},"stop_rule_class":"bug","class_guess":"N-shared-config","files":["custom_components/heatpump_optimizer/pump_arbiter.py","custom_components/heatpump_optimizer/thermal_model.py"],"proposed_fix_scope":"small: pass modulation_floor explicitly, drop attribute fallback and decorator; re-key mutation ledger pins 296c284b/399c5f97"}],
"non_findings":[
{"claim":"family_splits sort matches Intl.Collator en/sv","command":"python3 dev/audit/rounds/round10/D7/arch-s3/family_sort_collator.py --perturb","value":"0 inversions, 0/0 splits; perturb 1"},
{"claim":"delta_S of all prototypes is 0 and admissible; revert perturbation reads 0","command":"python3 dev/audit/rounds/round10/D7/arch-s3/score_delta.py 554e2ecfa <52f0de63|c402bce8|554e2ecfa>","value":"0.0000 each; c402bce8 reflective_writes 17->15"},
{"claim":"cells at floor, 30% target = 0","command":"same","value":"untyped_payload_keys 0, family_splits 0, cells_S_30pct 0.0000"}],
"harnesses":["dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py","dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py","dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py","dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py","dev/audit/rounds/round10/D7/arch-s3/family_sort_collator.py","dev/audit/rounds/round10/D7/arch-s3/score_delta.py"],
"leads":[{"owner_seat":"unknown","file":"custom_components/heatpump_optimizer/coordinator.py","symbol":"_ctx proxy, lines 1905-1920","what":"For ARCH-s1: __dict__ writes plus replace(ctx, **{n: value}) are 4 of the 17 reflective writes, the hub-handle shape C2b exists for"}]}
```

## Commands and return codes
| command | rc |
|---|---|
| `git fetch origin` | 0 |
| `git checkout -b audit/r10-arch-s3 origin/main` | 0 |
| `vector.py .` (baseline) | 0 |
| harnesses on baseline under the hpo python (`runall.sh base`: census, any, coll, pair, duty, score_null, score_instr) | all 0 |
| `score_delta.py 554e2ecfa c402bce8` | 0 |
| harnesses on the prototype (`runall.sh proto`) | all 0 |
| first gate, system python 3.11 | entities.py could not be parsed (environment); I killed it |
| gate under the hpo interpreter | 1 (the ledger pin and the killed `stress.py`) |
| first background `tests/arch_score.py` | 143 (killed by me; ran against a file I was still editing) |
| commit and `git push origin HEAD:refs/heads/handoff/audit-r10-arch-s3` | 0 |

No pull request was opened and nothing was written through the GitHub API.

Files are in `dev/audit/rounds/round10/D7/arch-s3/` in the worktree `~/heatpump_optimizer/.claude/worktrees/agent-a812ca38ac2ea7bed/`:
- D7-arch3-01-census-param-annotations.patch
- D7-arch3-02-c1-any-spellings.patch
- D7-arch3-03-c6-invented-family.patch
- D7-arch3-04-duty-floor-argument.patch
- payload_census_coverage.py
- payload_any_spellings.py
- family_pair_homing.py
- duty_floor_channel.py
- family_sort_collator.py
- score_delta.py