# D3-s1 round 11, box D3-top6 slice (D3.M3), baseline 92d38ecb

Seat D3-s1, box D3-top6 slice: D3.M3 T1-T3 of the box brief. Run locally on the orchestrator host (Apple M1, 8 cores, 8 GB, macOS), because the cloud fire was refused twice by the frugal guard. The cloud fire before that did PREPARE, R1 and T1 and started the T2 null; the local run re-took the traced baselines and controls, then ran the T2 full gates. T3 (the full net over the 33 owed survivors) moved to three cloud boxes, D3-top6-t3-p1..p3, at the orchestrator's instruction (owner rule: D3 runs on cloud boxes). Their results are collected from handoff-wip/finder-r11-D3-top6-t3-p{1,2,3}. Harness corrections made in this run: tests/card.mjs runs out of memory at node 20.10's default heap on this host, so the gate sets NODE_OPTIONS=--max-old-space-size=5120 (D3S1_NODE_HEAP). HPO_GATE_LOCK_LABEL is exported, without which stress.py and harness_headers.py wait past their bound for the seat's own lease and are skipped. The worktree is reset by soft reset plus checkout, not --hard, so the finder-wall strip survives. Kills are counted by each script's own 'N of M FAILED' summary against the null. The first null and the fb16/4b37 gates ran with stress.py and harness_headers.py skipped; their KILLED verdicts stand, since a skipped script can only hide a kill. Every wall figure is provisional, on a host shared with other seats (load1 4-250).

## Coverage (D3.M3)

Universe 35 survivors; examined 7; not reached 28. Enumerator: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`

## Full-net and full-gate table

| src:key | site | kind | full net | killed by | full gate | killed by | gate wall s (provisional) | load1 |
|---|---|---|---|---|---|---|---|---|
| c2:0e172028a23d9372 | sysid.py:2246 | R10C2 | - | - | KILLED | python3 tests/entities.py,python3 tests/features.py,python3 tests/stress.py | 6700.5 | 6.98..5.78 |
| c2:2719aef4cbb8b464 | price_model.py:337 | R10C2 | - | - | - | - | - | -..- |
| c2:66f8a4fb50e0b1f3 | defrost.py:783 | R10C2 | - | - | - | - | - | -..- |
| c2:8e82d7a0b3617003 | sysid.py:1549 | R10C2 | - | - | - | - | - | -..- |
| c2:95779f9d6d71c50d | grid_fee.py:355 | R10C2 | - | - | - | - | - | -..- |
| c2:a0b3b28854fa500c | flow_lift.py:188 | R10C2 | - | - | - | - | - | -..- |
| c2:aae7c9c380c3c5cf | sysid.py:1593 | R10C2 | - | - | - | - | - | -..- |
| c2:ad5900dadd86e9f9 | tariff.py:64 | R10C2 | - | - | - | - | - | -..- |
| c2:c38d53ab787ddbfa | price_model.py:252 | R10C2 | - | - | - | - | - | -..- |
| c2:d931ab195b940b0c | tariff.py:744 | R10C2 | - | - | RED-AS-NULL | - | 6820.6 | 8.08..246.46 |
| c2:fc395b83eeb1ddbf | price_model.py:532 | R10C2 | - | - | - | - | - | -..- |
| c3c6:0911281eca895664 | dhw_planner.py:1559 | R10C2 | - | - | - | - | - | -..- |
| c3c6:22b5ec8775d5bd50 | thermal_model.py:2593 | R10C2 | - | - | - | - | - | -..- |
| c3c6:5cc84148fa68bda1 | grid_fee.py:383 | R10C2 | - | - | - | - | - | -..- |
| c3c6:5e8d48eff7e4fa8d | coordinator.py:8806 | R10C2 | - | - | - | - | - | -..- |
| c3c6:6e6026d857732e96 | tariff.py:595 | R10C2 | - | - | - | - | - | -..- |
| c3c6:a4b00ac3ca662eec | thermal_model.py:835 | R10C2 | - | - | - | - | - | -..- |
| pre:0318c921405fefbe | dhw_planner.py:473 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:050fdc4a20eba212 | thermal_model.py:169 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:0c3e91a6a349409a | flow_lift.py:47 | CONST | - | - | - | - | - | -..- |
| pre:121362d48b408236 | grid_fee.py:173 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:23621370731667b7 | defrost.py:559 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:3885e472b8297a90 | flow_lift.py:183 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:460217277822d5bd | sysid.py:610 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:4b3795aece73ba73 | price_model.py:201 | GUARD_OFF | - | - | KILLED | python3 tests/features.py,python3 tests/structure.py | 4927.1 | 5.14..5.33 |
| pre:4e2df5f23e4eff29 | coordinator.py:422 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:61f74c4474262dad | coordinator.py:687 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:639d439d71b731ce | dhw_planner.py:75 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:65f121eb047174ad | optimizer.py:773 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:73bc722df73caecb | price_model.py:198 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:a0605da712a6a070 | defrost.py:419 | GUARD_OFF | KILLED | tests/features.py | - | - | - | -..- |
| pre:a35e03bd09f563c7 | sysid.py:677 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:acc8fa3942789f45 | thermal_model.py:270 | GUARD_OFF | - | - | - | - | - | -..- |
| pre:bdcf7589b0a0a6df | coordinator.py:539 | GUARD_OFF | - | - | KILLED | python3 tests/features.py | 13388.1 | 3.95..7.15 |
| pre:fb16c7b0cbbfc63d | tariff.py:64 | GUARD_OFF | - | - | KILLED | python3 tests/features.py | 3968.4 | 7.17..6.36 |

Full-gate null control (comment-only marker in tariff.py): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/optimality.py', 'python3 tests/stress.py'], failed-check counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 2, 'python3 tests/optimality.py': 1, 'python3 tests/stress.py': 2, 'python3 tests/harness_headers.py': 4}, wall 3637.9 s (provisional).

## Findings

- D3-s1-02 (D3.M3, low): No suite check pins the k <= 0 guard of tariff._smooth_topk_sum; the scalar and batch top-k disagree at k = 0 unseen

## Non-findings

- T2 full gate: tariff.py:64 _window_slot GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py; wall 3968.4 s, load1 7.17..6.36 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key fb16c7b0cbbfc63d`)
- T2 full gate: price_model.py:201 PriceShapeModel.observe_day non-finite guard GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py,python3 tests/structure.py; wall 4927.1 s, load1 5.14..5.33 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key 4b3795aece73ba73`)
- T2 full gate: coordinator.py:539 _parse_ecl110_state nested command.displace GUARD_OFF is pinned by the suite (KILLED): killed_by=python3 tests/features.py; wall 13388.1 s, load1 3.95..7.15 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key bdcf7589b0a0a6df`)
- T2 full gate: sysid.py:2246 R10 C2 M27 and -> or (drift refusal) is pinned by the suite (KILLED): killed_by=python3 tests/entities.py,python3 tests/features.py,python3 tests/stress.py; wall 6700.5 s, load1 6.98..5.78 (provisional) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src c2 --key 0e172028a23d9372`)
- T1: C3C6 M22 (tariff.py:595 mask_active, key 6e6026d857732e96) re-driven after its disk-full TIMEOUT; the TIMEOUT is dropped: SURVIVED 12 fast drivers in 293.0 s on cloud box D3-top6 (provisional); state/results/c3c6-redrive/6e6026d857732e96.json. It stays owed to T3. (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py run --mutants <M22 dict> --sub c3c6-redrive`)
- R1 controls on the local host: the prescreen null control LIVES and the positive control kills 2 of 2 ledger-pinned sites: null_verdict=LIVES (16 drivers); posctl 2/2 KILLED (tests/manual_plan.py) (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py null; ... run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-D3-top6-local`)
- Full-gate null control (comment-only marker in tariff.py) on this host: gate_rc=1; red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/optimality.py', 'python3 tests/stress.py'] with failed-check counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 2, 'python3 tests/optimality.py': 1, 'python3 tests/stress.py': 2, 'python3 tests/harness_headers.py': 4}, all host artefacts: optimality's claimed cell closes under Accelerate, closure.py selftest and entities.py instrument checks differ on macOS, harness_headers.py flags this seat's own untracked harnesses, and stress.py budgets fail under load. wall 3637.9 s (provisional). A mutant counts as killed only when it fails more checks than this. (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`)

## Unfinished

- D3.M3: T3: the full net over the 33 owed survivors is assigned to cloud boxes D3-top6-t3-p1..p3 (T3-SPLIT.md at 8de22a18). The full gate on each T3 survivor is owed after their results are collected.

## Leads

