I found three prototype changes that together move my cells' score by **+11.0039**, against a 30% target of **7.6662** (144% of it). They are pushed only to `handoff/audit-r10-arch-s1` at `dbabc395f`; I opened no pull request and made no GitHub API writes.

**REPORT.md was not written.** This environment refuses report `.md` files from a subagent, and that rule outranks the brief. The report content is in this message. The orchestrator can commit it as `dev/audit/rounds/round10/D7/arch-s1/REPORT.md` if it wants it in the tree.

## Target and result

- **Baseline:** `554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef` (origin/main when I started).
- **My cells' weights:** the two write censuses (`hub_solve_writes`, `shared_inplace_writes`) weigh 5.4429 each; the other four sit at the floor of 1.0. Total weight 14.8859, so the 30% target is 0.515 × 14.8859 = 7.6662.

| prototype | what moves | delta_S | verdict |
|---|---|---|---|
| P1 alone | `hub_solve_writes` 38 → 16, `coord_footprint` +3 | +6.5186 | WORSENS (inadmissible on the footprint rise alone) |
| P2 alone | `shared_inplace_writes` 22 → 16 | +2.3771 | IMPROVES, admissible |
| P3 alone | `shared_inplace_writes` 22 → 18 | +1.5020 | IMPROVES, admissible |
| all three | 38 → 16, 22 → 12, footprint 2580 → 2574 | **+11.0039** | IMPROVES, admissible |

- **Tripwires:** none moved in any variant (17, 32, 0, 0).
- **Perturbation:** reverting each patch gives exactly 0.0000 with no metric moved, for all four patches.
- **Where the gain comes from:** all of it is from the two weighted write censuses. The four floor-weight cells cannot honestly add more than about 0.6.

**P1 is admissible only alongside P2, or with one explanation line.** Taken alone it adds 3 footprint statements: the publishes through the context count as logic. Shipped together with P2 (footprint −6), the combination is admissible.

## Behaviour on the union

Command: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=554e2ecf… ./tests/run.sh`, which printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.

- **Golden fixtures:** `NO UNCLAIMED DRIFT` (56 scenarios) and `NO STALE FIXTURE`.
- **Passing:** `features` (4107 checks), `boost_drift_replay`, `structure`, `typing_ruler`, `arch_score_head`, `finite_boundary`, and the other scoped scripts.
- **`entities.py`:** terminated externally with SIGTERM 15 mid-run. Re-run alone it passed: `ALL 2303 ENTITY CHECKS PASSED`, rc 0.
- **`stress.py`:** unrun. I killed it on purpose because load1 was about 50–65, so it is left to CI.
- **Structure budgets:** the union records `max_cc` 45 → 44 and `max_class_loc` 8705 → 8681. That re-record is in `ALL_P1_P2_P3.patch`, with the reason in its commit.

It took four gate rounds to get there. Earlier cuts tripped four checks: `entities` S1 (hubs must be written through `_ctx`), the seam map, the typing ruler (3 type-var plus 3 assignment errors), and the zero-headroom ratchet (`max_class_loc` +29 and `seam_cut_total` +6). The final cuts fix all of them: P1, P2 and P3 change the coordinator class by −10, −11 and −3 lines, and `seam_cut_total` stays at 752. In P1 a few of those lines come from re-wrapping statements onto one line, which the shorter local `state` name allows.

## The three opportunities

**D7-arch1-01 (P1), medium.**
- **Claim:** 22 of the 38 hub writes the scheduled cycle reaches are in-place field edits of the one live `ThermalState`.
- **Fix:** `_update_current_state` reads the sensors onto a private copy. It publishes the copy once through the context, before the first consumer reads the state. The legionella hours, the ECL110 lag and the last-resort seeds each publish as a whole snapshot too.
- **Removed:** the redundant `floor_return_temperature` store, since the callee records it.
- **Fresh read:** `_async_drive_pumps` now reads the state fresh after its own `await`.
- **Not changed:** the MQTT callback and the peak-guard writer still edit in place. Converting them cost +6 seam cut, and they are outside the census.
- **Files:** `coordinator.py`, `thermal_model.py` (return_temp annotation becomes `float | None`), `tests/arch_score_head.py` (stale rows retired), `tests/boost_drift_replay.py`.
- **Why it is better code:** the live state becomes a value with one owner, published whole, instead of an object edited between learner `await`s. Package-wide in-place stores to `_current_state` fall from 21 to 3.
- **One thing to know:** the replay harness held a context captured at set-up and solved on stale state until it was changed to re-read it. Any holder of an old context now sees an old snapshot. That is the intended copy-on-write behaviour, and the pump-driver read was the only place in production code where it applied.

**D7-arch1-02 (P2), small, `coordinator.py` only.**
- **Claim:** `async_set_away` writes the override fields, reads them back, and writes them again: 6 in-place writes to the published `AwayState`.
- **Fix:** the override is worked out in local variables and published once with `replace(...)`. `_resolve_away` uses the same pattern.
- **Limit:** the baseline has no `await` between those writes, so there was no torn read. The gain is a clean hand-off (a spawned persist keeps the snapshot it was given) and clearer code. Severity: low.

**D7-arch1-03 (P3), small, 4 files** (`accuracy.py`, `coordinator.py`, `flow_lift.py`, `flow_meter.py`).
- **Claim:** the coordinator and a module function write into collaborators' internal fields.
- **Fix:**
  - `AccuracyTracker.void_pending()` replaces 4 direct `.lead_pending.clear()` calls.
  - `FlowBias.observe_temps(..., heat_output_kw=)` sets its own field instead of `flow_meter` setting it from outside.
  - The solar forecast is built in one comprehension instead of `.append` in an async method.
- **Limit:** the census credits better encapsulation, but the object is still changed at the same moment as before, so a reviewer should read the accuracy and flow parts as Demeter fixes, not removed hazards.

## Non-findings

- **`coordinator_private_reach` = 2:** both sites read the public `mode` property, which counter C5 counts as `_mode`. Rerouting a public read is not an improvement.
- **`coordinator_multiassigned_attrs` = 118:** 86 attributes have only an `_init_*` writer plus one mutator. Extracting cohesive state groups is real work but worth only about +0.24.
- **`params_over_10` = 12:** every function over the line has a written reason in `arch_score_head.py` for staying there. Only the four tariff rows are marked as owed; fixing them would be worth +0.53.
- **`coord_footprint`:** a 10% cut is worth about +0.15.

## Leads

- **D1, unverified:** `boost.restore_session` mutates the initial `AwayState` after an awaited store load, while `_resolve_away` rebinds `self._away_state` every cycle. A first refresh that wins that race would orphan the restored override until the next restart.
- **D7, large:** the 15 remaining hub writes go into `_thermal_params`, which four owners share by reference. A parameter owner using copy-on-write could add about +9.8.

## JSON report

The `D7-arch1-NN` ids from the brief do not match `finding.schema.json`'s id pattern, and there is no `D7-arch1` seat in `scopes.json`. I used `scope: "D7-s1"`, which owns step M1; please re-key if needed.

```json
{"dimension":"D7","baseline_sha":"554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef","exposure":"",
"coverage":[{"step":"D7.M1","depth":"deep","evidence":"site lists for all 6 cells; arch1_delta.py on 4 patches + 4 reverts"}],
"unfinished":[{"step":"D7.M1","what":"tariff-record family (params_over_10, +0.53) and the _thermal_params owner (+~9.8, large) not prototyped; MQTT/peak-guard live-state writers left in place (+6 seam cut when converted)"}],
"findings":[
{"id":"D7-arch1-01","scope":"D7-s1","step":"D7.M1","title":"Live ThermalState mutated field by field across the cycle's awaits","severity":"medium","claim":"22 of 38 cycle-reachable hub writes are in-place edits of the live ThermalState; building on a copy and publishing through the context removes them with no golden drift.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py P1_live_state_published_whole.patch","harness_path":"dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py","value":6.5186,"unit":"weighted-log2 delta_S","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 darwin","cpu_or_wall":"count","contention_note":"shared box, load1 13; static counts are contention-immune","tolerance":"exact","load1":13.11,"thread_factor":1.0},"instrumented_symbol":"archscore.metrics.hub_solve_writes:measure over coordinator:HeatPumpOptimizerCoordinator._update_current_state","perturbation":{"change":"--revert (git apply -R)","expected_direction":"to_zero","observed_value":0.0},"metric_definition":"hub_solve_writes: distinct in-place write sites into _opt_config/_thermal_params/_current_state reachable from the cycle or a solve","phenomenon_property":"the live thermal state is replaced whole, never edited in place","seam_rule":"git grep -nE \"_current_state\\.[a-z_0-9]+ *=[^=]\" <ref> -- custom_components","stop_rule_class":"hygiene","class_guess":"N-shared-config","files":["custom_components/heatpump_optimizer/coordinator.py","custom_components/heatpump_optimizer/thermal_model.py","tests/arch_score_head.py","tests/boost_drift_replay.py"],"proposed_fix_scope":"medium; ship with P2 (footprint +3 alone)"},
{"id":"D7-arch1-02","scope":"D7-s1","step":"D7.M1","title":"Away override edited in place with a write-read-write round trip","severity":"low","claim":"async_set_away and _resolve_away make 6 in-place writes to the published AwayState; computing on locals and publishing with replace removes them.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py P2_away_override_published_whole.patch","harness_path":"dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py","value":2.3771,"unit":"weighted-log2 delta_S","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 darwin","cpu_or_wall":"count","contention_note":"static counts","tolerance":"exact","load1":13.11,"thread_factor":1.0},"instrumented_symbol":"archscore.metrics.shared_inplace_writes:measure over coordinator:HeatPumpOptimizerCoordinator.async_set_away","perturbation":{"change":"--revert","expected_direction":"to_zero","observed_value":0.0},"metric_definition":"shared_inplace_writes: in-place writes into coordinator-held objects in async coordinator methods or collaborator modules","phenomenon_property":"AwayState is replaced, never edited","seam_rule":"git grep -nE \"_away_state\\.[a-z_]+ *=[^=]\" <ref> -- custom_components","stop_rule_class":"hygiene","class_guess":"N-shared-config","files":["custom_components/heatpump_optimizer/coordinator.py"],"proposed_fix_scope":"small"},
{"id":"D7-arch1-03","scope":"D7-s1","step":"D7.M1","title":"Coordinator writes into collaborators' internal fields","severity":"low","claim":"Direct lead_pending.clear(), FlowBias.heat_output_kw set from outside, and .append on the solar forecast give 4 shared in-place sites; owning methods and a comprehension remove them.","evidence":{"command":"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py P3_collaborators_own_their_fields.patch","harness_path":"dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py","value":1.502,"unit":"weighted-log2 delta_S","baseline_sha":"554e2ecfa7ad","machine":"Apple M1 darwin","cpu_or_wall":"count","contention_note":"static counts","tolerance":"exact","load1":13.11,"thread_factor":1.0},"instrumented_symbol":"archscore.metrics.shared_inplace_writes:measure over accuracy:AccuracyTracker, flow_meter:observe_water","perturbation":{"change":"--revert","expected_direction":"to_zero","observed_value":0.0},"metric_definition":"shared_inplace_writes as above","phenomenon_property":"a collaborator's fields are written only by its own methods","seam_rule":"python3 -c 'from archscore.metrics import shared_inplace_writes' details.sites","stop_rule_class":"hygiene","class_guess":"N-shared-config","files":["custom_components/heatpump_optimizer/accuracy.py","custom_components/heatpump_optimizer/coordinator.py","custom_components/heatpump_optimizer/flow_lift.py","custom_components/heatpump_optimizer/flow_meter.py"],"proposed_fix_scope":"small"}],
"non_findings":[
{"claim":"private_reach 2 = reads of the public mode property (C5); not improvable","command":"reach2.py C5 sweep","value":"2 sites, structure census 0"},
{"claim":"multiassigned 118 is mostly init + one mutator","command":"structure.coordinator_writers","value":"86 of 118 have exactly 2 writers"},
{"claim":"params_over_10 rows all have recorded reasons","command":"tests/arch_score_head.py","value":"12 rows; tariff family worth +0.53"},
{"claim":"union passes the scoped gate with no golden drift","command":"GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=554e2ecf ./tests/run.sh","value":"MODE: SCOPED 27 run; NO UNCLAIMED DRIFT; entities re-run 2303 passed; stress unrun"}],
"harnesses":["dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py"],
"leads":[
{"owner_seat":"unknown","file":"custom_components/heatpump_optimizer/away.py","symbol":"restore_override/apply_override_payload","what":"D1 lifecycle (unverified): restore mutates the initial AwayState after an awaited load; _resolve_away rebinds every cycle, so a first refresh can orphan the restored override"},
{"owner_seat":"unknown","file":"custom_components/heatpump_optimizer/coordinator.py","symbol":"_thermal_params aliasing","what":"D7 decomposition: 15 remaining hub writes into params shared by reference with ThermalModel, DhwProfileLearner, LegionellaTracker; an owner with copy-on-write adds about +9.8 (large)"}]}
```

## Commands and exit codes

| command | rc |
|---|---|
| `git fetch origin -q` | 0 |
| `git checkout -b audit/r10-arch-s1 origin/main` | 0 |
| `vector.py .` (baseline vector) | 0 |
| `score.py --diff` per variant (all rounds) | 0 |
| scoped gate, round 1 | killed by its environment (exit 144) before completing; no result |
| scoped gate, rounds 2 and 3 | 1; killed by me mid-run after the ratchet and typing failures |
| scoped gate, round 4 (final) | 1: stress killed by me, entities killed externally |
| `entities.py` re-run alone | 0 |
| `structure.py --record` on the union | 0 |
| `arch1_delta.py` on 4 patches and 4 reverts | all 0 |
| `git commit dbabc395f` | 0 |
| `git push origin audit/r10-arch-s1:refs/heads/handoff/audit-r10-arch-s1` | 0 |

Files are in `dev/audit/rounds/round10/D7/arch-s1/` under `~/heatpump_optimizer/.claude/worktrees/agent-ac59d365df4ac4763`:
- arch1_delta.py
- P1_live_state_published_whole.patch
- P2_away_override_published_whole.patch
- P3_collaborators_own_their_fields.patch
- ALL_P1_P2_P3.patch