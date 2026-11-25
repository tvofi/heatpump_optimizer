# D3-s1, box D3-g27: the full gate for 16 D3.M3 u1 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Round 11, seat D3-s1, wave box D3-g27 (keys.tsv: 16 keys, all optimizer.py). Counts final; every wall and load figure provisional.

## Machine and controls

```
date: 2026-11-22T21:43:33Z
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1014       13568          12        1802       15073
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.84
note: $HOME/venv-ci is a symlink to /opt/hpo/venv-ci (this container's venv-ci location)

re-fire 2026-11-25T00:51:25Z (new container, resumed from 4eb777948ba2)
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         783       14026          12        1549       15304
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.70
```

Null control (comment-only marker, `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], wall 3861.6 s, load1 0.65..0.92. A key is KILLED only when run.sh is red and a script fails beyond this null; red with no script beyond it is RED-AS-NULL (read as survived).

Procedure: gate_wave.sh (out of tree, shipped on the dispatch ref; summarised in gate_wave_procedure.md here) ran `fullgate.py run --src complete --key <key>` for each key in keys.tsv order, one gate at a time, capped at 4 h, checkpointing after every gate. Each probe applies its mutant in memory (the function re-compiled from source with the one line replaced, in a namespace copy; production solves see it through mock.patch.object on heatpump_optimizer.optimizer) and never touched the gate's tree.

Classing rule for a full-gate survivor: **candidate** when the probe's number moves on an input production can build (the probe's production-domain subset, or one of its four production solves); **equivalent-candidate** when it moves only on inputs production never builds (a pin of 0.5, eps 0, |x0| ~ 1e12 kW, mismatched lengths) or not at all. Every input tried is in the probe's RESULT lines.

## Tally

- gated: 16 of 16
- KILLED: 0
- SURVIVED: 0
- RED-AS-NULL: 16
- TIMEOUT: 0
- candidates: 9
- equivalent-candidates: 7

## Gate table

| key | site | verdict | killed_by | class | wall s | load1 |
|---|---|---|---|---|---|---|
| e58e8eb0f54fe274 | optimizer.py:2417 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate | 3492.2 | 0.72..1.01 |
| d128afa0c1ce3d28 | optimizer.py:2418 CLAMP_DROP | RED-AS-NULL | - | candidate | 3185.9 | 0.5..0.92 |
| 0a40fc8d3d37f2ba | optimizer.py:2111 GUARD_OFF | RED-AS-NULL | - | candidate | 3129.2 | 0.72..1.0 |
| 6af4c3b8f521e3d3 | optimizer.py:2111 CMP_BOUND | RED-AS-NULL | - | candidate | 3151.8 | 0.85..0.92 |
| 10e3ee99c90d4d48 | optimizer.py:1567 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate | 3148.3 | 0.78..0.92 |
| 06f2ef99e24e2e24 | optimizer.py:1571 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate | 3149.8 | 0.78..0.94 |
| c1e66052b2d8090c | optimizer.py:1577 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate | 3335.3 | 0.42..0.88 |
| f077d8a96cc1e3ed | optimizer.py:1577 CMP_BOUND | RED-AS-NULL | - | candidate | 3302.4 | 0.84..1.0 |
| 04bfd79fdf465dbf | optimizer.py:1578 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate | 3235.5 | 0.85..1.0 |
| 6a32950e7b3e62f2 | optimizer.py:1580 CMP_BOUND | RED-AS-NULL | - | candidate | 3265.2 | 0.85..0.92 |
| c5abe60d7c7ca966 | optimizer.py:1582 CMP_BOUND | RED-AS-NULL | - | candidate | 3264.0 | 0.85..0.92 |
| ef7b85a510c47950 | optimizer.py:1870 CLAMP_DROP | RED-AS-NULL | - | candidate | 3386.5 | 0.87..1.02 |
| 3067ff76235329e4 | optimizer.py:1871 CMP_BOUND | RED-AS-NULL | - | candidate | 3433.5 | 0.86..0.92 |
| 0560ccd4eaedbd09 | optimizer.py:2492 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate | 3498.8 | 0.86..0.92 |
| b94f040a7b0aed92 | optimizer.py:2494 GUARD_OFF | RED-AS-NULL | - | candidate | 3605.7 | 0.85..1.0 |
| efea9d49d605beaa | optimizer.py:2494 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate | 3516.0 | 0.85..1.02 |

## Survivors: the step-4 answer and the probe's numbers

**e58e8eb0f54fe274** optimizer.py:2417 CMP_BOUND `if pin >= 0.5: -> if pin > 0.5:` (_apply_pins_to_bounds), full gate RED-AS-NULL: **equivalent-candidate**. moves only at pin == 0.5 (a pin of exactly 0.5 becomes an off pin); production pins are 1.0/0.0/NaN, so 0 of 60 production-domain grid inputs and 0 of 4 production calls move. Example input pin=0.5,bounds=(0.0,0.3),min_on_power=0.0: baseline (0.0,0.3), mutant (0.0,0.0). Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/manual_plan.py (executes optimizer.py:2417 on the traced baseline; also tests/features.py, tests/optimality.py, tests/env_drift.py) has no _apply_pins_to_bounds check at pin == 0.5; none is owed through production, which never builds a 0.5 pin. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_e58e8eb0f54fe274.py`.

**d128afa0c1ce3d28** optimizer.py:2418 CLAMP_DROP `out[i] = (min(min_on_power, high), high) -> out[i] = ((min_on_power), high)` (_apply_pins_to_bounds), full gate RED-AS-NULL: **candidate**. moves on production inputs: 10 of 60 production-domain grid inputs give an inverted box, and the capped pinned production solve's objective moves by 18.0096 (plan max delta 3.05687 kW). Example input pin=1.0,bounds=(0.0,0.0),min_on_power=0.8: baseline (0.0,0.0), mutant (0.8,0.0). Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/manual_plan.py (executes optimizer.py:2418 on the traced baseline; also tests/features.py, tests/env_drift.py): no check pins a space step forced on where the step's upper bound (headroom under power_caps_extra or beside a DHW block) is below the pin's on-power, asserting lower <= upper or the plan's objective. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_d128afa0c1ce3d28.py`.
Candidate: *No check forces a step on whose headroom is below the pin's on-power; dropping the min() clamp in _apply_pins_to_bounds is unseen* (severity claimed medium, class guess I1).

**0a40fc8d3d37f2ba** optimizer.py:2111 GUARD_OFF `if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9): -> if False:` (_better_objective), full gate RED-AS-NULL: **candidate**. moves on production inputs: 51 of 121 finite value pairs flip; the kept objective for (10, 5) goes 5.0 -> 10.0. The probe's four manual_plan solves never call it (0 calls); features.py reaches it. Example input left=0.0,right=-3.0: baseline right, mutant left. Null arm: null_inputs_moved=0 count. Should have failed: tests/features.py (the one script that executes optimizer.py:2111 on the traced baseline, through _repair_throttled_buffer_caps at optimizer.py:5180) never asserts which plan _better_objective keeps when the second arm (the cap-tighten seeds) is lower. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_0a40fc8d3d37f2ba.py`.
Candidate: *No check makes the cap-tighten seed arm win _better_objective; disabling its right-wins branch is unseen* (severity claimed low, class guess I1).

**6af4c3b8f521e3d3** optimizer.py:2111 CMP_BOUND `if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9): -> if np.isfinite(ro) and (not np.isfinite(lo) or ro <= lo - 1e-9):` (_better_objective), full gate RED-AS-NULL: **candidate**. moves on 4 of 121 finite value pairs, all at the exact tie margin; 0 production calls in the probe's solves. Example input left=0.0,right=-1e-09: baseline left, mutant right. Null arm: null_inputs_moved=0 count. Should have failed: tests/features.py (executes optimizer.py:2111) has no _better_objective case at the tie margin right == left - 1e-9. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_6af4c3b8f521e3d3.py`.
Candidate: *No check pins _better_objective's 1e-9 tie margin; < -> <= at it is unseen* (severity claimed low, class guess I1).

**10e3ee99c90d4d48** optimizer.py:1567 CMP_BOUND `sign_x0 = (x0 >= 0).astype(float) * 2 - 1 -> sign_x0 = (x0 > 0).astype(float) * 2 - 1` (_fd_steps), full gate RED-AS-NULL: **equivalent-candidate**. moves only on 74 crafted inputs with eps == 0 (x0 == 0); 0 of 4685 production-domain inputs, 0 of 19129 random inputs, 0 of 57 production _fd_steps calls and 0 gradients move. Example input x0=0.0,eps=0.0,lb=-inf,ub=-1.0: baseline -1.4901161193847656e-08, mutant 1.4901161193847656e-08. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers); none is owed through production: the sign only matters on the zero-probe fallback at x0 == 0, which needs eps == 0, and production passes 1e-4. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_10e3ee99c90d4d48.py`.

**06f2ef99e24e2e24** optimizer.py:1571 CLAMP_DROP `np.finfo(np.float64).eps ** 0.5 * sign_x0 * np.maximum(1.0, np.abs(x0)), -> np.finfo(np.float64).eps ** 0.5 * sign_x0 * (1.0),` (_fd_steps), full gate RED-AS-NULL: **equivalent-candidate**. moves only where x0 + eps rounds to x0 (eps 0, or |x0| >= 1e12); 0 of 4685 production-domain inputs, 0 production calls, gradients or plan kW move. Example input x0=3.7,eps=0.0,lb=-inf,ub=0.0: baseline -5.513429641723633e-08, mutant -1.4901161193847656e-08. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers); none is owed through production: the zero-probe fallback needs x0 + 1e-4 == x0 (|x0| > ~1e12 kW). Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_06f2ef99e24e2e24.py`.

**c1e66052b2d8090c** optimizer.py:1577 CMP_BOUND `violated = (x < lb) | (x > ub) -> violated = (x <= lb) | (x > ub)` (_fd_steps), full gate RED-AS-NULL: **equivalent-candidate**. moves only for x0 outside its box or a negative fallback step at |x0| ~ 1e17; 0 of 4685 production-domain inputs, 0 production calls, gradients or plan kW move. Example input x0=0.0,eps=0.0001,lb=0.0001,ub=0.00010000000000000002: baseline 0.0001, mutant -0.0001. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers); none is owed through production: x0 + h lands exactly on lb only for a negative fallback step or an x0 below its lower bound. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_c1e66052b2d8090c.py`.

**f077d8a96cc1e3ed** optimizer.py:1577 CMP_BOUND `violated = (x < lb) | (x > ub) -> violated = (x < lb) | (x >= ub)` (_fd_steps), full gate RED-AS-NULL: **candidate**. moves on 30 of 4685 production-domain inputs (x0 + 1e-4 == ub exactly); 0 of 57 production calls in the probe's solves. Example input x0=0.0,eps=0.0001,lb=0.0,ub=0.0001: baseline 0.0001, mutant -0.0001. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers) lacks an iterate exactly eps below its upper bound (x0 + 1e-4 == ub). Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_f077d8a96cc1e3ed.py`.
Candidate: *No check differences a variable exactly eps below its upper bound; x > ub -> x >= ub in _fd_steps is unseen* (severity claimed low, class guess I1).

**04bfd79fdf465dbf** optimizer.py:1578 CMP_BOUND `fitting = np.abs(h) <= np.maximum(lower_dist, upper_dist) -> fitting = np.abs(h) < np.maximum(lower_dist, upper_dist)` (_fd_steps), full gate RED-AS-NULL: **equivalent-candidate**. moves on 7 crafted inputs, all with eps == 0 and a negative x0; 0 of 4685 production-domain inputs, 0 random inputs, 0 production calls, gradients or plan kW move. Example input x0=-0.5,eps=0.0,lb=-0.5000000149011612,ub=-0.4999999850988388: baseline -1.4901161193847656e-08, mutant 1.4901161193847656e-08. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers); none is owed through production: at |h| == max(distance) the forward/backward overrides rebuild the same step. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_04bfd79fdf465dbf.py`.

**6a32950e7b3e62f2** optimizer.py:1580 CMP_BOUND `forward = (upper_dist >= lower_dist) & ~fitting -> forward = (upper_dist > lower_dist) & ~fitting` (_fd_steps), full gate RED-AS-NULL: **candidate**. moves on 29 of 4685 production-domain inputs (centred boxes narrower than 2e-4); 0 of 57 production calls. Example input x0=0.5,eps=0.0001,lb=0.499999999999,ub=0.500000000001: baseline 9.999778782798785e-13, mutant 0.0001. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers) lacks a free variable at the exact centre of a box narrower than 2*eps. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_6a32950e7b3e62f2.py`.
Candidate: *No check differences a variable centred in a box narrower than 2*eps; the forward tie in _fd_steps is unpinned* (severity claimed low, class guess I1).

**c5abe60d7c7ca966** optimizer.py:1582 CMP_BOUND `backward = (upper_dist < lower_dist) & ~fitting -> backward = (upper_dist <= lower_dist) & ~fitting` (_fd_steps), full gate RED-AS-NULL: **candidate**. moves on 29 of 4685 production-domain inputs (centred narrow boxes); 0 of 57 production calls. Example input x0=0.5,eps=0.0001,lb=0.499999999999,ub=0.500000000001: baseline 9.999778782798785e-13, mutant -9.999778782798785e-13. Null arm: null_inputs_moved=0 count, null_plan_max_abs_delta_kw=0 kW. Should have failed: tests/features.py::_grad_parity (features.py:6394; per-variable parity with scipy's approx_derivative over uniform, capped and DHW-pinned-headroom bounds at rng.uniform(0, 3) powers) lacks a free variable at the exact centre of a box narrower than 2*eps. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_c5abe60d7c7ca966.py`.
Candidate: *No check differences a variable centred in a box narrower than 2*eps; the backward tie in _fd_steps is unpinned* (severity claimed low, class guess I1).

**ef7b85a510c47950** optimizer.py:1870 CLAMP_DROP `scale = max(abs(prior), 1e-12) -> scale = (abs(prior))` (_lbfgsb_restart), full gate RED-AS-NULL: **candidate**. moves on 57 of 245 finite grid pairs (all at prior == 0, -0.0); 0 of 12 production decisions. Example input prior=0.0,score=-2e-17: baseline best, mutant polished. Null arm: null_inputs_moved=0 count. Should have failed: tests/features.py::_d0_restart_keeps_only_a_real_drop (features.py ~6800-6850: an ftol-tick restart is not adopted, a 5e-2 relative drop is) has no case at a prior objective of exactly 0. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_ef7b85a510c47950.py`.
Candidate: *No check restarts from a zero objective; dropping _lbfgsb_restart's 1e-12 scale floor is unseen* (severity claimed low, class guess I1).

**3067ff76235329e4** optimizer.py:1871 CMP_BOUND `if np.isfinite(score) and (prior - score) > _LBFGSB_RESTART_KEEP_REL * scale: -> if np.isfinite(score) and (prior - score) >= _LBFGSB_RESTART_KEEP_REL * scale:` (_lbfgsb_restart), full gate RED-AS-NULL: **candidate**. moves on 3 of 245 finite grid pairs, all at exact threshold equality; 0 of 12 production decisions. Example input prior=0.0,score=-2e-17: baseline best, mutant polished. Null arm: null_inputs_moved=0 count. Should have failed: tests/features.py::_d0_restart_keeps_only_a_real_drop (features.py ~6800-6850: an ftol-tick restart is not adopted, a 5e-2 relative drop is) has no case at a drop of exactly the keep threshold. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_3067ff76235329e4.py`.
Candidate: *No check restarts with a drop of exactly the keep threshold; > -> >= in _lbfgsb_restart is unseen* (severity claimed low, class guess I1).

**0560ccd4eaedbd09** optimizer.py:2492 CLAMP_DROP `for i in range(min(len(out), len(pins))): -> for i in range((len(out))):` (_mark_manual_reasons), full gate RED-AS-NULL: **equivalent-candidate**. moves only on a pins array shorter than the reasons (IndexError, 12 of 54 grid inputs); 0 of 18 production-domain inputs, 0 of 6 production calls had a length mismatch, 0 labels changed. Example input reasons=['idle', 'idle', 'idle'],pins=[1.0]: baseline ('ok',('idle','idle','idle')), mutant ('raised','IndexError'). Null arm: null_inputs_moved=0 count, null_reason_labels_changed=0 count. Should have failed: tests/manual_plan.py (executes optimizer.py:2492; also tests/block_duty.py, tests/features.py, tests/optimality.py); none is owed through production, where both arrays are n_steps long. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_0560ccd4eaedbd09.py`.

**b94f040a7b0aed92** optimizer.py:2494 GUARD_OFF `if _pin_is_free(pin) or pin < 0.5: -> if False:` (_mark_manual_reasons), full gate RED-AS-NULL: **candidate**. moves on production inputs: 4 of 18 production-domain grid inputs and the published reasons of 2 of 4 production solves (REASON_MANUAL 2 -> 190). Example input reasons=['idle_coasting'],pins=[0.0]: baseline ('ok',('idle_coasting',)), mutant ('ok',('manual_plan',)). Null arm: null_inputs_moved=0 count, null_reason_labels_changed=0 count. Should have failed: tests/manual_plan.py::test_pins_change_schedule (executes optimizer.py:2494) asserts only that a forced-on step reads manual_plan; no check asserts that a free (NaN) or forced-off step keeps its own reason. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_b94f040a7b0aed92.py`.
Candidate: *No check asserts free or forced-off steps keep their reason under a manual plan; disabling _mark_manual_reasons's guard is unseen* (severity claimed medium, class guess I1).

**efea9d49d605beaa** optimizer.py:2494 CMP_BOUND `if _pin_is_free(pin) or pin < 0.5: -> if _pin_is_free(pin) or pin <= 0.5:` (_mark_manual_reasons), full gate RED-AS-NULL: **equivalent-candidate**. moves only at pin == 0.5 (2 of 54 grid inputs); 0 of 18 production-domain inputs and 0 of 6 production calls move. Example input reasons=['idle_coasting'],pins=[0.5]: baseline ('ok',('manual_plan',)), mutant ('ok',('idle_coasting',)). Null arm: null_inputs_moved=0 count, null_reason_labels_changed=0 count. Should have failed: tests/manual_plan.py (executes optimizer.py:2494) has no pin == 0.5 case; none is owed through production, which never builds a 0.5 pin. Probe: `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_efea9d49d605beaa.py`.

## Leads

- D16 (actuator writes against the plan) / D0: custom_components/heatpump_optimizer/optimizer.py _space_scope / _apply_pins_to_bounds: in probe_d128afa0c1ce3d28's capped pinned solve (space pinned on at step 36 under a 0.05 kW power_caps_extra), the baseline plan's step-36 total (space + DHW) is 0.1 kW, above the 0.05 kW total cap the fuse guard promises to hold; outside this seat's cell, not measured further

## Findings

None numbered here: finding ids are assigned at the orchestrator's consolidation; candidates are under `gate_survivors` in REPORT.json.
