# D3-s1 round 11, box D3-top6 slice (D3.M3), baseline 92d38ecb

Seat D3-s1, box D3-top6 slice: D3.M3 T1-T3 of the box brief. Run locally on the orchestrator host (Apple M1, 8 cores, 8 GB, macOS), because the cloud fire was refused twice by the frugal guard. The cloud fire before that did PREPARE, R1 and T1 and started the T2 null; the local run re-took the traced baselines and controls, then ran the T2 full gates. T3 was split for cloud boxes D3-top6-t3-p1..p3 (T3-SPLIT.md at 8de22a18); those refs never moved past 21:44Z. The original cloud box D3-top6 kept running instead and pushed to this box's ref: it repeated T2 with the same six verdicts, ran the T3 full net (35 results, 16 SURVIVED, M22 KILLED) and full-gated 10 of the 15 remaining survivors (all SURVIVED, cloud null green). Its gate and full-net JSONs are merged into state/ here, and its log is state/cloud-box-PROGRESS.log. The local 8e82 gate waited over an hour for a heavy slot and was stopped; its verdict is the cloud gate's (KILLED by features.py, cloud null green). Harness corrections made in this run: tests/card.mjs runs out of memory at node 20.10's default heap on this host, so the gate sets NODE_OPTIONS=--max-old-space-size=5120 (D3S1_NODE_HEAP). HPO_GATE_LOCK_LABEL is exported, without which stress.py and harness_headers.py wait past their bound for the seat's own lease and are skipped. The worktree is reset by soft reset plus checkout, not --hard, so the finder-wall strip survives. Kills are counted by each script's own 'N of M FAILED' summary against the null. The first null and the fb16/4b37 gates ran with stress.py and harness_headers.py skipped; their KILLED verdicts stand, since a skipped script can only hide a kill. Every wall figure is provisional, on a host shared with other seats (load1 4-250).

## Coverage (D3.M3)

Universe 35 survivors; examined 30; not reached 5. Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`

## Full-net and full-gate table

| src:key | site | kind | full net | killed by | full gate | killed by | gate wall s (provisional) | load1 |
|---|---|---|---|---|---|---|---|---|
| c2:0e172028a23d9372 | sysid.py:2246 | R10C2 | KILLED | tests/features.py | KILLED | python3 tests/entities.py,python3 tests/features.py,python3 tests/stress.py | 6700.5 | 6.98..5.78 |
| c2:2719aef4cbb8b464 | price_model.py:337 | R10C2 | SURVIVED | - | SURVIVED | - | 3388.4 | 0.08..- |
| c2:66f8a4fb50e0b1f3 | defrost.py:783 | R10C2 | KILLED | tests/features.py | - | - | - | -..- |
| c2:8e82d7a0b3617003 | sysid.py:1549 | R10C2 | KILLED | tests/harness_headers.py,tests/features.py | KILLED | python3 tests/features.py | 2994.0 | -..- |
| c2:95779f9d6d71c50d | grid_fee.py:355 | R10C2 | SURVIVED | - | - | - | - | -..- |
| c2:a0b3b28854fa500c | flow_lift.py:188 | R10C2 | SURVIVED | - | - | - | - | -..- |
| c2:aae7c9c380c3c5cf | sysid.py:1593 | R10C2 | KILLED | tests/features.py | - | - | - | -..- |
| c2:ad5900dadd86e9f9 | tariff.py:64 | R10C2 | KILLED | tests/features.py | - | - | - | -..- |
| c2:c38d53ab787ddbfa | price_model.py:252 | R10C2 | SURVIVED | - | - | - | - | -..- |
| c2:d931ab195b940b0c | tariff.py:744 | R10C2 | SURVIVED | - | RED-AS-NULL | - | 6820.6 | 8.08..246.46 |
| c2:fc395b83eeb1ddbf | price_model.py:532 | R10C2 | KILLED | tests/features.py | - | - | - | -..- |
| c3c6:0911281eca895664 | dhw_planner.py:1559 | R10C2 | SURVIVED | - | SURVIVED | - | 3447.6 | -..0.06 |
| c3c6:22b5ec8775d5bd50 | thermal_model.py:2593 | R10C2 | SURVIVED | - | SURVIVED | - | 3405.6 | 0.05..- |
| c3c6:5cc84148fa68bda1 | grid_fee.py:383 | R10C2 | SURVIVED | - | - | - | - | -..- |
| c3c6:5e8d48eff7e4fa8d | coordinator.py:8806 | R10C2 | SURVIVED | - | SURVIVED | - | 3288.6 | 0.66..- |
| c3c6:6e6026d857732e96 | tariff.py:595 | R10C2 | KILLED | tests/harness_headers.py,tests/features.py | - | - | - | -..- |
| c3c6:a4b00ac3ca662eec | thermal_model.py:835 | R10C2 | SURVIVED | - | - | - | - | -..- |
| pre:0318c921405fefbe | dhw_planner.py:473 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:050fdc4a20eba212 | thermal_model.py:169 | GUARD_OFF | SURVIVED | - | SURVIVED | - | 3589.3 | 0.41..- |
| pre:0c3e91a6a349409a | flow_lift.py:47 | CONST | SURVIVED | - | SURVIVED | - | 3530.5 | 0.07..- |
| pre:121362d48b408236 | grid_fee.py:173 | GUARD_OFF | SURVIVED | - | SURVIVED | - | 3298.1 | 0.08..- |
| pre:23621370731667b7 | defrost.py:559 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:3885e472b8297a90 | flow_lift.py:183 | GUARD_OFF | SURVIVED | - | SURVIVED | - | 3233.6 | -..- |
| pre:460217277822d5bd | sysid.py:610 | GUARD_OFF | SURVIVED | - | SURVIVED | - | 3187.7 | 0.05..- |
| pre:4b3795aece73ba73 | price_model.py:201 | GUARD_OFF | KILLED | tests/features.py | KILLED | python3 tests/features.py,python3 tests/structure.py | 4927.1 | 5.14..5.33 |
| pre:4e2df5f23e4eff29 | coordinator.py:422 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:61f74c4474262dad | coordinator.py:687 | GUARD_OFF | KILLED | tests/entities.py,tests/features.py | - | - | - | -..- |
| pre:639d439d71b731ce | dhw_planner.py:75 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:65f121eb047174ad | optimizer.py:773 | GUARD_OFF | SURVIVED | - | SURVIVED | - | 3151.1 | 0.11..- |
| pre:73bc722df73caecb | price_model.py:198 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:a0605da712a6a070 | defrost.py:419 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:a35e03bd09f563c7 | sysid.py:677 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:acc8fa3942789f45 | thermal_model.py:270 | GUARD_OFF | KILLED | tests/harness_headers.py | - | - | - | -..- |
| pre:bdcf7589b0a0a6df | coordinator.py:539 | GUARD_OFF | KILLED | tests/features.py | KILLED | python3 tests/features.py | 13388.1 | 3.95..7.15 |
| pre:fb16c7b0cbbfc63d | tariff.py:64 | GUARD_OFF | KILLED | tests/features.py | KILLED | python3 tests/features.py | 3968.4 | 7.17..6.36 |

Full-gate null control (comment-only marker in tariff.py): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/optimality.py', 'python3 tests/stress.py'], failed-check counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 2, 'python3 tests/optimality.py': 1, 'python3 tests/stress.py': 2, 'python3 tests/harness_headers.py': 4}, wall 3637.9 s (provisional).

## Findings

- D3-s1-02 (D3.M3, low): No suite check pins the k <= 0 guard of tariff._smooth_topk_sum; the scalar and batch top-k disagree at k = 0 unseen

## Non-findings

- T2 full gate: tariff.py:64 _window_slot GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py; wall 3968.4 s, load1 7.17..6.36 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key fb16c7b0cbbfc63d`)
- T2 full gate: price_model.py:201 PriceShapeModel.observe_day non-finite guard GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py,python3 tests/structure.py; wall 4927.1 s, load1 5.14..5.33 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key 4b3795aece73ba73`)
- T2 full gate: coordinator.py:539 _parse_ecl110_state nested command.displace GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py; wall 13388.1 s, load1 3.95..7.15 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key bdcf7589b0a0a6df`)
- T2 full gate: sysid.py:2246 R10 C2 M27 and -> or (drift refusal) is pinned by the suite (KILLED): killed_by=python3 tests/entities.py,python3 tests/features.py,python3 tests/stress.py; wall 6700.5 s, load1 6.98..5.78 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src c2 --key 0e172028a23d9372`)
- T2 full gate: sysid.py:1549 R10 C2 M26 hour >= start -> hour > start is pinned by the suite (KILLED): killed_by=python3 tests/features.py; wall 2994.0 s, load1 0.0..0.0 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src c2 --key 8e82d7a0b3617003`)
- T2 8e82 (sysid.py:1549 R10 C2 M26, hour >= start -> hour > start) is killed by the full gate: KILLED by tests/features.py, gate_rc=1, wall 2994 s (provisional); cloud null gate_rc=0 ALL TEST SCRIPTS PASSED (state/gates/cloud/null.json). The local repeat was stopped at boost_drift_replay.py, waiting for a heavy slot. (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src c2 --key 8e82d7a0b3617003 (cloud box D3-top6, Linux)`)
- T1: C3C6 M22 (tariff.py:595 mask_active, key 6e6026d857732e96) re-driven after its disk-full TIMEOUT; the TIMEOUT is dropped: SURVIVED 12 fast drivers in 293.0 s on cloud box D3-top6 (provisional); state/results/c3c6-redrive/6e6026d857732e96.json. It stays owed to T3. (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --mutants <M22 dict> --sub c3c6-redrive`)
- R1 controls on the local host: the prescreen null control LIVES and the positive control kills 2 of 2 ledger-pinned sites: null_verdict=LIVES (16 drivers); posctl 2/2 KILLED (tests/manual_plan.py) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py null; ... run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-D3-top6-local`)
- Full-gate null control (comment-only marker in tariff.py) on this host: gate_rc=1; red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/optimality.py', 'python3 tests/stress.py'] with failed-check counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 2, 'python3 tests/optimality.py': 1, 'python3 tests/stress.py': 2, 'python3 tests/harness_headers.py': 4}, all host artefacts: optimality's claimed cell closes under Accelerate, closure.py selftest and entities.py instrument checks differ on macOS, harness_headers.py flags this seat's own untracked harnesses, and stress.py budgets fail under load. wall 3637.9 s (provisional). A mutant counts as killed only when it fails more checks than this. (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`)

## Unfinished

- D3.M3: Full gate owed on 5 full-net survivors: c2:95779f9d6d71c50d grid_fee.py:355, c2:a0b3b28854fa500c flow_lift.py:188, c2:c38d53ab787ddbfa price_model.py:252, c3c6:5cc84148fa68bda1 grid_fee.py:383, c3c6:a4b00ac3ca662eec thermal_model.py:835. Cloud box D3-top6 was gating them one per ~55 min when this report was assembled; blocker: this host's heavy-slot pool held 4/4 by other seats, so no local gate could start.
- D3.M3: Finding write-up (probe + perturbation + null arm) owed for the 10 T3 survivors that SURVIVED a full gate on the cloud box (keys in state/gates/, cloud null green): 050fdc4a20eba212, 0911281eca895664, 0c3e91a6a349409a, 121362d48b408236, 22b5ec8775d5bd50, 2719aef4cbb8b464, 3885e472b8297a90, 460217277822d5bd, 5e8d48eff7e4fa8d, 65f121eb047174ad. A surviving mutant without a perturbation-moving harness is not a finding under COMMON.md, so they are carried as leads, not findings.

## Leads

- D3-s1 custom_components/heatpump_optimizer/thermal_model.py line 169: mutant 050fdc4a20eba212 ('if not spec:' -> 'if False:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/dhw_planner.py line 1559: mutant 0911281eca895664 ('shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)' -> 'shortfall_price = 1000.0 * (float(np.min(np.abs(prices))) + 1.0)') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/flow_lift.py line 47: mutant 0c3e91a6a349409a ('FLOW_BIAS_ALPHA = 0.1' -> 'FLOW_BIAS_ALPHA = 0.2') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/grid_fee.py line 173: mutant 121362d48b408236 ('if not sep:' -> 'if False:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/thermal_model.py line 2593: mutant 22b5ec8775d5bd50 (') / max(dt_hours, 1e-6)' -> ') / min(dt_hours, 1e-6)') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/price_model.py line 337: mutant 2719aef4cbb8b464 ('if not day_types or not np.isfinite(level) or level <= 0.0:' -> 'if not day_types or not np.isfinite(level) or level < 0.0:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/flow_lift.py line 183: mutant 3885e472b8297a90 ('if not np.isfinite(measured_supply) or not np.isfinite(curve_supply):' -> 'if False:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/sysid.py line 610: mutant 460217277822d5bd ('if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):' -> 'if False:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/coordinator.py line 8806: mutant 5e8d48eff7e4fa8d ('if tariff.enabled and factor > 0.0:' -> 'if tariff.enabled or factor > 0.0:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
- D3-s1 custom_components/heatpump_optimizer/optimizer.py line 773: mutant 65f121eb047174ad ('if not holiday_dates:' -> 'if False:') SURVIVED the full gate on cloud box D3-top6 (cloud null green); probe and perturbation owed before it is a finding
