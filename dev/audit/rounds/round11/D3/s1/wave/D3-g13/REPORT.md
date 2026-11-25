# D3-s1 round 11, box D3-g13: full gate for 16 D3.M3 full-net survivors (wave), baseline 92d38ecb

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1116       13467          12        1801       14971
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.65
2026-11-22T21:39:21Z
python3: /opt/hpo/venv-ci/bin/python3 ($HOME/venv-ci symlinked to it)

re-fire (second seat, new container) 2026-11-25T00:47:34Z:
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         755       14043          12        1561       15331
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.34
python3: /opt/hpo/venv-ci/bin/python3 ($HOME/venv-ci symlinked to it)
note: CPU differs from the first fire (2.10GHz vs 2.30GHz, both 4 cores/16 GB); the restored null is reused as gate_wave.sh's restore intends; a KILLED verdict on a timing-sensitive script would be re-adjudicated against a null re-taken on this machine.
```

Null control (`fullgate.py null`, comment-only marker): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, summary ['3 TEST SCRIPT(S) FAILED'], wall 2955.8 s, load1 0.5..0.92 (provisional). A mutant counts KILLED only when a script fails beyond this null; red with no script beyond it is RED-AS-NULL (read as survived).

Every wall, CPU and load figure is provisional (nproc 4, Intel Xeon @ 2.30GHz for the null and the first 9 gates; a re-fired container, Intel Xeon @ 2.10GHz, for the last 7, the null reused: MACHINE.txt; the judge re-takes it); counts are final. Probes ran from a separate clean baseline worktree, never from the gate's tree.

## Tally

Gated 16 of 16 keys; verdicts {'RED-AS-NULL': 16}; classes {'candidate': 5, 'equivalent-candidate': 11}.

| key | site | function | full gate | killed by | wall s | load1 | class |
|---|---|---|---|---|---|---|---|
| 24d9995ccee4252e | defrost.py:642 CMP_BOUND | DefrostDerate.summary | RED-AS-NULL | - | 2823.1 | 0.78..0.93 | candidate |
| 7030f8259cc37dd4 | defrost.py:746 CMP_BOUND | DefrostWindow._accrue | RED-AS-NULL | - | 2850.7 | 0.79..0.93 | equivalent-candidate |
| 5941c09a9face079 | defrost.py:739 BOOLOP | DefrostWindow._elapsed | RED-AS-NULL | - | 2798.4 | 0.95..0.93 | equivalent-candidate |
| b020c93535a7f9e6 | defrost.py:795 GUARD_OFF | DefrostWindow.peek | RED-AS-NULL | - | 2859.3 | 0.86..0.85 | equivalent-candidate |
| 8297234e122897ff | defrost.py:802 GUARD_OFF | DefrostWindow.peek | RED-AS-NULL | - | 2835.1 | 0.72..0.92 | candidate |
| 681130c48add1573 | defrost.py:804 CLAMP_DROP | DefrostWindow.peek | RED-AS-NULL | - | 2845.4 | 0.72..0.94 | candidate |
| c61a89f42607c92b | defrost.py:169 CMP_BOUND | _bucket_index | RED-AS-NULL | - | 2817.6 | 0.95..0.92 | candidate |
| c0bd33b7c209982d | defrost.py:181 CMP_BOUND | _interp_position | RED-AS-NULL | - | 2789.8 | 0.86..0.93 | equivalent-candidate |
| 677019b333cfa304 | defrost.py:184 CMP_BOUND | _interp_position | RED-AS-NULL | - | 2869.6 | 0.72..0.92 | equivalent-candidate |
| 168e4035dbc9bb84 | defrost.py:204 CLAMP_DROP | derate_from_duty | RED-AS-NULL | - | 3152.4 | 0.24..0.93 | equivalent-candidate |
| 597d6753c0939797 | dhw_planner.py:2055 CMP_BOUND | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3091.0 | 0.94..0.92 | equivalent-candidate |
| df4de55e12588fdf | dhw_planner.py:2055 CMP_BOUND | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3012.7 | 0.85..0.92 | candidate |
| 72240d3f22ceb752 | dhw_planner.py:2057 CLAMP_DROP | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3029.1 | 0.78..1.07 | equivalent-candidate |
| 49dc3d36092b3943 | dhw_planner.py:2065 CLAMP_DROP | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3073.0 | 0.91..0.92 | equivalent-candidate |
| 111763243ac44278 | dhw_planner.py:2075 GUARD_OFF | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3125.5 | 0.87..0.85 | equivalent-candidate |
| af8d4fddad8f298f | dhw_planner.py:2075 CMP_BOUND | DhwPlanner._apply_dhw_min_run | RED-AS-NULL | - | 3140.9 | 0.89..1.0 | equivalent-candidate |

## Survivors: the step-4 answer and the probe numbers

### 24d9995ccee4252e defrost.py:642 CMP_BOUND (DefrostDerate.summary): RED-AS-NULL, candidate

Patch `if self.duty_counts[t][h] > 0: -> if self.duty_counts[t][h] >= 0:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_24d9995ccee4252e.py`: rows_total_baseline=1 count; rows_with_duty_baseline=0 count; rows_with_duty_mutant=1 count; mutant_row_fields=['duty', 'duty_samples', 'events']; mutant_row_duty=0.0 events=0 duty_samples=0; null_delta_rows=0 count; empty_rows_baseline=0 mutant=0 count; thread_factor=1.000; load1=0.80.

Inputs tried: one inferred observation at 3 C / 85 % (duty_counts 0); null: one counted duty at 3 C / 85 %; empty learner.

Should have failed (D3.M4): tests/features.py (its traced baseline executes defrost.py:642; the reach table also lists tests/finite_boundary.py): no assertion that a summary() row of a bucket with duty_counts == 0 carries no duty/events/duty_samples keys

Candidate: **No check pins that an inferred-only defrost bucket's summary row omits the measured-duty block** (low, class_guess new). Mutant 24d9995ccee4252e (defrost.py:642, duty_counts > 0 -> >= 0) survives the full gate (RED-AS-NULL), yet DefrostDerate.summary() on a learner with one inferred observation and no counted duty gains a duty=0.0 events=0 duty_samples=0 block on its row (rows_with_duty 0 -> 1). Perturbation direction: up. Null: a bucket with one counted duty sample carries the block in both arms (null_delta_rows=0).

### 7030f8259cc37dd4 defrost.py:746 CMP_BOUND (DefrostWindow._accrue): RED-AS-NULL, equivalent-candidate

Patch `if delta is not None and delta > 0: -> if delta is not None and delta >= 0:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_7030f8259cc37dd4.py`: on_then_peek: baseline=(1.0, 1, True, 600.0)/(1.0, 1, True, 600.0) mutant=(1.0, 1, True, 600.0)/(1.0, 1, True, 600.0); off_on_peek: baseline=(0.666666666667, 1, True, 900.0)/(0.666666666667, 1, True, 900.0) mutant=(0.666666666667, 1, True, 900.0)/(0.666666666667, 1, True, 900.0); on_off_peek: baseline=(0.333333333333, 1, True, 900.0)/(0.333333333333, 1, True, 900.0) mutant=(0.333333333333, 1, True, 900.0)/(0.333333333333, 1, True, 900.0); repeat_same_stamp: baseline=(1.0, 1, True, 300.0)/(1.0, 1, True, 300.0) mutant=(1.0, 1, True, 300.0)/(1.0, 1, True, 300.0); zero_length: baseline=(0.0, 1, True, 0.0)/(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0)/(0.0, 1, True, 0.0); backwards_clock: baseline=(0.0, 1, True, 0.0)/(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0)/(0.0, 1, True, 0.0); dark_then_on: baseline=(0.8, 1, False, 600.0)/(0.8, 1, False, 600.0) mutant=(0.8, 1, False, 600.0)/(0.8, 1, False, 600.0); carried_level_after_close: baseline=(1.0, 0, False, 600.0)/(1.0, 0, False, 600.0) mutant=(1.0, 0, False, 600.0)/(1.0, 0, False, 600.0); carried_level_reobserved: baseline=(1.0, 0, True, 600.0)/(1.0, 0, True, 600.0) mutant=(1.0, 0, True, 600.0)/(1.0, 0, True, 600.0); none_observed: baseline=(0.0, 0, False, 0.0)/(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0)/(0.0, 0, False, 0.0); direct_delta=0.0: baseline_seconds_on=3.0 mutant=3.0 same=1; direct_delta=-0.0: baseline_seconds_on=3.0 mutant=3.0 same=1; direct_delta=-5.0: baseline_seconds_on=3.0 mutant=3.0 same=1; direct_delta=1e-09: baseline_seconds_on=3.0 mutant=3.0 same=1; direct_delta=7.0: baseline_seconds_on=10.0 mutant=10.0 same=1; sequences_moved=0 of 15 (); thread_factor=1.000; load1=0.87.

Inputs tried: 10 observe/close sequences (on/off/dark/repeated stamp/zero length/backwards clock/carried level); direct _accrue delta 0.0, -0.0, -5.0, 1e-9, 7.0.

Should have failed (D3.M4): none: at delta == 0 the mutant adds 0.0 (or -0.0) to a non-negative float accumulator, bit-identically

Equivalent-candidate: delta == 0 contributes += 0.0; no input separates.

### 5941c09a9face079 defrost.py:739 BOOLOP (DefrostWindow._elapsed): RED-AS-NULL, equivalent-candidate

Patch `if isinstance(raw, (int, float)) and not isinstance(raw, bool): -> if isinstance(raw, (int, float)) or not isinstance(raw, bool):`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_5941c09a9face079.py`: stamp_aware_utc: baseline=600.0 mutant=600.0; stamp_aware_tz2: baseline=600.0 mutant=600.0; stamp_naive: baseline=600.0 mutant=600.0; stamp_mixed: baseline=None mutant=None; stamp_equal: baseline=0.0 mutant=0.0; stamp_negative: baseline=-600.0 mutant=-600.0; stamp_none_then: baseline=None mutant=None; stamp_none_now: baseline=None mutant=None; stamp_micro: baseline=1e-06 mutant=1e-06; production_shaped_moved=0 of 19 (); fabricated_bool_True: baseline=None mutant=1.0; fabricated_decimal_5: baseline=None mutant=5.0; fabricated_str_5: baseline=None mutant=5.0; fabricated_moved=3 of 3 (bool_True,decimal_5,str_5); thread_factor=1.000; load1=0.95.

Inputs tried: aware UTC / aware +02:00 / naive / mixed / equal / negative / None / 1 us stamps; 10 window sequences; fabricated stamps whose total_seconds() is True, Decimal('5'), '5'.

Should have failed (D3.M4): none through production: timedelta.total_seconds() is always a float; only fabricated non-datetime stamps (no production caller passes one) separate, by a direct _elapsed call

Equivalent-candidate: unreachable through production: separating inputs exist only as fabricated objects (fabricated_moved=3 of 3, production_shaped_moved=0 of 19).

### b020c93535a7f9e6 defrost.py:795 GUARD_OFF (DefrostWindow.peek): RED-AS-NULL, equivalent-candidate

Patch `if self._opened is None: -> if False:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_b020c93535a7f9e6.py`: fresh_aware: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); fresh_naive: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); fresh_none: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); fresh_int: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); fresh_str: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); inputs_moved=0 of 15 (); thread_factor=1.000; load1=0.71.

Inputs tried: 10 window sequences; fresh window peeked with aware, naive, None, int, str stamps.

Should have failed (D3.M4): none: with _opened None, _elapsed(now, None) raises AttributeError inside its try and returns None, and the next guard returns the same empty DefrostObservation()

Equivalent-candidate: the next line's `total is None` guard returns the identical empty observation.

### 8297234e122897ff defrost.py:802 GUARD_OFF (DefrostWindow.peek): RED-AS-NULL, candidate

Patch `if self._state and self._since is not None: -> if False:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_8297234e122897ff.py`: on_then_peek: baseline=(1.0, 1, True, 600.0) mutant=(0.0, 1, True, 600.0); off_on_peek: baseline=(0.666666666667, 1, True, 900.0) mutant=(0.0, 1, True, 900.0); on_off_peek: baseline=(0.333333333333, 1, True, 900.0) mutant=(0.333333333333, 1, True, 900.0); repeat_same_stamp: baseline=(1.0, 1, True, 300.0) mutant=(1.0, 1, True, 300.0); zero_length: baseline=(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0); backwards_clock: baseline=(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0); dark_then_on: baseline=(0.8, 1, False, 600.0) mutant=(0.0, 1, False, 600.0); carried_level_after_close: baseline=(1.0, 0, False, 600.0) mutant=(0.0, 0, False, 600.0); carried_level_reobserved: baseline=(1.0, 0, True, 600.0) mutant=(0.0, 0, True, 600.0); none_observed: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); duty_baseline=1.0; duty_mutant=0.0; observed_baseline=1 mutant=1; any_defrost_baseline=1 mutant=0; sequences_moved=5 of 10 (on_then_peek,off_on_peek,dark_then_on,carried_level_after_close,carried_level_reobserved); null_delta=0 count; thread_factor=1.000; load1=0.85.

Inputs tried: 10 observe/close sequences; headline: flag ON carried over a close at 1800 s, re-observed ON at 1800 s, peek at 2400 s.

Should have failed (D3.M4): tests/features.py (its traced baseline executes defrost.py:802; also boost_drift_replay.py, config_flow_steps.py, entities.py): no assertion on DefrostWindow.peek(now).duty while the flag is still on at the peek (the open on-period)

Candidate: **No check peeks a DefrostWindow while the defrost is still on; dropping the open on-period is unseen** (low, class_guess new). Mutant 8297234e122897ff (defrost.py:802, the open-on-period guard -> if False) survives the full gate (RED-AS-NULL), yet DefrostWindow.peek() on an interval whose flag is still on reports duty 0.0 instead of 1.0, and with the level carried over a close any_defrost flips 1 -> 0, which opens the frost-band COP fold at coordinator.py:5344-5347 during a live defrost. Perturbation direction: down. Null: a sequence whose flag switched off before the peek (on_off_peek): same observation both arms (null_delta=0).

### 681130c48add1573 defrost.py:804 CLAMP_DROP (DefrostWindow.peek): RED-AS-NULL, candidate

Patch `seconds_on += max(0.0, open_for) if open_for is not None else 0.0 -> seconds_on += (0.0) if open_for is not None else 0.0`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_681130c48add1573.py`: on_then_peek: baseline=(1.0, 1, True, 600.0) mutant=(0.0, 1, True, 600.0); off_on_peek: baseline=(0.666666666667, 1, True, 900.0) mutant=(0.0, 1, True, 900.0); on_off_peek: baseline=(0.333333333333, 1, True, 900.0) mutant=(0.333333333333, 1, True, 900.0); repeat_same_stamp: baseline=(1.0, 1, True, 300.0) mutant=(1.0, 1, True, 300.0); zero_length: baseline=(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0); backwards_clock: baseline=(0.0, 1, True, 0.0) mutant=(0.0, 1, True, 0.0); dark_then_on: baseline=(0.8, 1, False, 600.0) mutant=(0.0, 1, False, 600.0); carried_level_after_close: baseline=(1.0, 0, False, 600.0) mutant=(0.0, 0, False, 600.0); carried_level_reobserved: baseline=(1.0, 0, True, 600.0) mutant=(0.0, 0, True, 600.0); none_observed: baseline=(0.0, 0, False, 0.0) mutant=(0.0, 0, False, 0.0); duty_baseline=1.0; duty_mutant=0.0; observed_baseline=1 mutant=1; any_defrost_baseline=1 mutant=0; sequences_moved=5 of 10 (on_then_peek,off_on_peek,dark_then_on,carried_level_after_close,carried_level_reobserved); null_delta=0 count; thread_factor=1.000; load1=0.97.

Inputs tried: 10 observe/close sequences; headline: flag ON carried over a close at 1800 s, re-observed ON at 1800 s, peek at 2400 s.

Should have failed (D3.M4): tests/features.py (its traced baseline executes defrost.py:804; also config_flow_steps.py): no assertion on DefrostWindow.peek(now).duty while the flag is still on at the peek (the open on-period)

Candidate: **No check peeks a DefrostWindow mid-defrost; zeroing the open on-period's seconds is unseen** (low, class_guess new). Mutant 681130c48add1573 (defrost.py:804, max(0.0, open_for) -> 0.0) survives the full gate (RED-AS-NULL), yet DefrostWindow.peek() on an interval whose flag is still on reports duty 0.0 instead of 1.0 and any_defrost 0 instead of 1 on the carried-level sequence: the same phenomenon as mutant 8297234e122897ff at the adjacent line. Perturbation direction: down. Null: a sequence whose flag switched off before the peek (on_off_peek): same observation both arms (null_delta=0).

### c61a89f42607c92b defrost.py:169 CMP_BOUND (_bucket_index): RED-AS-NULL, candidate

Patch `return len(edges) - 2 if value >= edges[-1] else 0 -> return len(edges) - 2 if value > edges[-1] else 0`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c61a89f42607c92b.py`: bucket_temp_at_top_edge baseline=5 mutant=0; direct_inputs_moved=2 of 20 (temp:40.0,hum:101.0); observe_duty_40C_bucket baseline=(5, 0) mutant=(0, 0); observe_duty_40C_moved=1 count; cold_bucket_factor baseline=0.784729 mutant=0.92494; null_delta=0 count  (20 C: inside the edges, line 169 never runs); frost_band=0.0..5.0 C; thread_factor=1.000; load1=0.89.

Inputs tried: _bucket_index on 40.0, 101.0, -30, -31, 41, +-inf, nan, 39.999999, 3.0 for both edge sets; observe_duty at 40.0 C / 50 %; null: observe_duty at 20 C.

Should have failed (D3.M4): none of the closure scripts executes defrost.py:169 on its traced baseline (no traced run feeds a value on or beyond the top edge); the check that should exist: tests/features.py, beside its DefrostDerate bucket cases, asserting _bucket_index(TEMP_EDGES[-1], TEMP_EDGES) == len(TEMP_EDGES) - 2 (or an observe_duty at 40.0 C landing in the top bucket) The probe reaches line 169 through the production fold DefrostDerate.observe_duty, which coordinator._settle_defrost (coordinator.py:9981) calls at ANY outdoor temperature once the defrost flag is legible: an outdoor reading of exactly 40.0 C reaches it. The line is reachable; it is a test gap, not an unreachable finding.

Candidate: **No check feeds _bucket_index a value on the top edge; a 40.0 C duty folding into the coldest bucket is unseen** (low, class_guess new). Mutant c61a89f42607c92b (defrost.py:169, value >= edges[-1] -> >) survives the full gate (RED-AS-NULL), yet one measured duty at exactly 40.0 C folds into bucket (0, 0) (-30..-5 C) instead of (5, 0), and ten such zero-duty settlements raise the coldest bucket's factor from 0.784729 to 0.92494. Perturbation direction: down (bucket index 5 -> 0); cold-bucket factor up. Null: a 20 C sample lands in the same bucket in both arms (null_delta=0): line 169 is not reached inside the edges.

### c0bd33b7c209982d defrost.py:181 CMP_BOUND (_interp_position): RED-AS-NULL, equivalent-candidate

Patch `if value <= centers[0]: -> if value < centers[0]:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c0bd33b7c209982d.py`: at_first_centre baseline=(0, 0.0) mutant=(0, 0.0); interp_tuple_moves=0 of 76 count; factor_max_abs_delta=0.0 over 8892 (t,h) pairs x 6 learners; thread_factor=1.000; load1=0.86.

Inputs tried: every temperature and humidity centre, +-1e-9 around each, its negation, +-100, 0, +-inf, nan, on 6 fully learned learners (8892 factor pairs).

Should have failed (D3.M4): none: at value == centers[0] the loop's first cell returns (0, (c0 - c0)/span) = (0, 0.0), the tuple the guard returns

Equivalent-candidate: identical (i, u) at the boundary; factor_max_abs_delta 0.0.

### 677019b333cfa304 defrost.py:184 CMP_BOUND (_interp_position): RED-AS-NULL, equivalent-candidate

Patch `if value < centers[i + 1]: -> if value <= centers[i + 1]:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_677019b333cfa304.py`: at_interior_centre baseline=(2, 0.0) mutant=(1, 1.0); interp_tuple_moves=4 of 76 count; factor_max_abs_delta=0.0 over 8892 (t,h) pairs x 6 learners; thread_factor=1.000; load1=1.10.

Inputs tried: every temperature and humidity centre, +-1e-9 around each, its negation, +-100, 0, +-inf, nan, on 6 fully learned learners (8892 factor pairs).

Should have failed (D3.M4): none at the observable output: the (i, u) tuple moves at the four interior temperature centres ((i+1, 0.0) -> (i, 1.0)), but _factor_uncached, its only reader, weights the same neighbour by exactly 1.0 and the other by exactly 0.0 either way

Equivalent-candidate: interp tuple moves 4 of 76, factor_max_abs_delta 0.0 over 8892 pairs: equivalent at the only consumer.

### 168e4035dbc9bb84 defrost.py:204 CLAMP_DROP (derate_from_duty): RED-AS-NULL, equivalent-candidate

Patch `duty = min(max(float(duty), 0.0), DEFROST_DUTY_MAX) -> duty = min((float(duty)), DEFROST_DUTY_MAX)`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_168e4035dbc9bb84.py`: derate(-1000000000.0) baseline=1.0 mutant=1.0; derate(-1.0) baseline=1.0 mutant=1.0; derate(-0.3) baseline=1.0 mutant=1.0; derate(-1e-12) baseline=1.0 mutant=1.0; derate(-0.0) baseline=1.0 mutant=1.0; derate(0.0) baseline=1.0 mutant=1.0; derate(1e-12) baseline=0.9999999999985 mutant=0.9999999999985; derate(0.1) baseline=0.85 mutant=0.85; derate(0.3) baseline=0.55 mutant=0.55; derate(0.31) baseline=0.55 mutant=0.55; derate(1.0) baseline=0.55 mutant=0.55; derate(5.0) baseline=0.55 mutant=0.55; derate(inf) baseline=0.55 mutant=0.55; derate(-inf) baseline=1.0 mutant=1.0; derate(nan) baseline=0.55 mutant=0.55; inputs_moved=0 of 15 (); DERATE_MAX=1.0; posctl_derate_max_1_05 baseline=1.0 mutant=1.05; thread_factor=1.000; load1=0.94.

Inputs tried: duty -1e9, -1, -0.3, -1e-12, -0.0, 0.0, 1e-12, 0.1, 0.3, 0.31, 1, 5, +-inf, nan; positive control: DERATE_MAX patched to 1.05.

Should have failed (D3.M4): none while DERATE_MAX == 1.0: a negative duty gives 1 + |duty|*1.5, which min(DERATE_MAX, .) caps to exactly 1.0, the baseline's value at duty 0; observe_duty also refuses duties outside [0, 1] before they reach the grid

Equivalent-candidate: inputs_moved 0 of 15; the harness separates under DERATE_MAX=1.05 (posctl 1.0 vs 1.05).

### 597d6753c0939797 dhw_planner.py:2055 CMP_BOUND (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, equivalent-candidate

Patch `weak = np.where((plan > 1e-6) & (plan < min_run_power))[0] -> weak = np.where((plan > 1e-6) & (plan <= min_run_power))[0]`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_597d6753c0939797.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; tie_at_min_run_moved=0 of 2; direct_min_run_above_pmax_moved=64 of 144; reach_caller_min_run_le_pmax=1 count; thread_factor=1.000; load1=0.91.

Inputs tried: 144 production-shaped fixtures (12 seeds x 4 tank states x 3 sizes; 48 take the joint shortcut); a slot exactly at min_run_power alone and beside a weak slot, tank with room and full; 144 direct fixtures with min_run_power 1.2 > p_dhw_max 1.0.

Should have failed (D3.M4): none through production: a slot at exactly min_run_power is raised to the value it already holds; the plan moves only when min_run_power > p_dhw_max, which the only caller forbids (dhw_planner.py:1141 min_run_power = min(p_dhw_run, ...))

Equivalent-candidate: unreachable through production: production_shaped_moved 0 of 144, direct_min_run_above_pmax_moved 64 of 144.

### df4de55e12588fdf dhw_planner.py:2055 CMP_BOUND (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, candidate

Patch `weak = np.where((plan > 1e-6) & (plan < min_run_power))[0] -> weak = np.where((plan >= 1e-6) & (plan < min_run_power))[0]`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_df4de55e12588fdf.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; slot_at_1e-06_tank_room baseline=1e-06 mutant=0.6; slot_at_9.999999999999997e-07_tank_room baseline=9.999999999999997e-07 mutant=9.999999999999997e-07; slot_at_1.0000000000000002e-06_tank_room baseline=0.6 mutant=0.6; slot_at_1e-06_tank_full baseline=1e-06 mutant=0.0; slot_at_9.999999999999997e-07_tank_full baseline=9.999999999999997e-07 mutant=9.999999999999997e-07; slot_at_1.0000000000000002e-06_tank_full baseline=0.0 mutant=0.0; slot_kw_at_1e-6_baseline=1e-06; slot_kw_at_1e-6_mutant=0.6; boundary_inputs_moved=2 of 6; thread_factor=1.000; load1=0.88.

Inputs tried: a 24-step plan with one slot at exactly 1e-6 kW and at its float neighbours, tank with room (35 C, ceiling 55) and full (50/50); 144 production-shaped fixtures.

Should have failed (D3.M4): tests/features.py (its traced baseline executes dhw_planner.py:2055; also block_duty.py, manual_plan.py, optimality.py, plan_view.py, validate.py): its #1230 and min-run cases never plan a slot at exactly the 1e-6 kW weak floor

Candidate: **No check plans a DHW slot at exactly the 1e-6 kW weak floor; moving the floor's comparison is unseen** (low, class_guess new). Mutant df4de55e12588fdf (dhw_planner.py:2055, plan > 1e-6 -> plan >= 1e-6) survives the full gate (RED-AS-NULL), yet a slot planned at exactly 1e-6 kW is returned as a 1e-6 kW trickle on the baseline and raised to 0.6 kW (tank with room) or zeroed (tank full) under the mutant; its float neighbours agree in both arms. Perturbation direction: up (1e-6 -> 0.6 kW). Null: the float neighbours of 1e-6 (nextafter either side) give the same answer in both arms; the 144 production-shaped fixtures do not move.

### 72240d3f22ceb752 dhw_planner.py:2057 CLAMP_DROP (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, equivalent-candidate

Patch `unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max) -> unchanged: np.ndarray = (plan)`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_72240d3f22ceb752.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; no_weak_in_range baseline=[2.0, 0.0] mutant=[2.0, 0.0]; no_weak_above_pmax baseline=[3.0] mutant=[3.5]; no_weak_negative baseline=[0.0] mutant=[-0.5]; no_weak_nan baseline=[nan] mutant=[nan]; direct_no_weak_moved=2 of 4 (above_pmax,negative); reach_cheapest_first_returns=['np.clip(plan, 0.0, p_dhw_max)', 'plan']; thread_factor=1.000; load1=0.88.

Inputs tried: 144 production-shaped fixtures; no-weak plans: in range, a slot at 3.5 > p_max, a slot at -0.5, a nan slot.

Should have failed (D3.M4): none through production: the only caller feeds _plan_dhw_cheapest_first's result, whose every return is clipped to [0, p_dhw_max] (dhw_planner.py:2191-2195, 2307), so the no-weak clip is a no-op there; a direct call with an out-of-range plan separates

Equivalent-candidate: unreachable through production: production_shaped_moved 0 of 144, direct_no_weak_moved 2 of 4 (above_pmax, negative).

### 49dc3d36092b3943 dhw_planner.py:2065 CLAMP_DROP (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, equivalent-candidate

Patch `run_power = min(min_run_power, p_dhw_max) -> run_power = (min_run_power)`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_49dc3d36092b3943.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; direct_min_run_above_pmax_moved=56 of 144; reach_caller_min_run_le_pmax=1 count; thread_factor=1.000; load1=0.88.

Inputs tried: 144 production-shaped fixtures; 144 direct fixtures with min_run_power 1.2 > p_dhw_max 1.0.

Should have failed (D3.M4): none through production: min(min_run_power, p_dhw_max) == min_run_power whenever min_run_power <= p_dhw_max, which dhw_planner.py:1141 guarantees

Equivalent-candidate: unreachable through production: production_shaped_moved 0 of 144, direct_min_run_above_pmax_moved 56 of 144.

### 111763243ac44278 dhw_planner.py:2075 GUARD_OFF (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, equivalent-candidate

Patch `if bool(np.all(joint_temps <= joint_limit + 1e-9)): -> if False:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_111763243ac44278.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; dhw_steps_baseline=4608 count  (48 joint-shortcut fixtures); dhw_steps_mutant=22560 count; thread_factor=1.000; load1=0.88.

Inputs tried: 144 production-shaped fixtures, 48 of which take the joint shortcut on the baseline.

Should have failed (D3.M4): none at the output: when every weak slot raised jointly fits, the per-slot pass raises each slot too and returns the same plan; the shortcut is a cost saving (simulate_dhw_step 4608 -> 22560 over the 48 shortcut fixtures), which no check budgets at this site

Equivalent-candidate: production_shaped_moved 0 of 144; cost-only difference (4608 -> 22560 tank steps).

### af8d4fddad8f298f dhw_planner.py:2075 CMP_BOUND (DhwPlanner._apply_dhw_min_run): RED-AS-NULL, equivalent-candidate

Patch `if bool(np.all(joint_temps <= joint_limit + 1e-9)): -> if bool(np.all(joint_temps < joint_limit + 1e-9)):`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_af8d4fddad8f298f.py`: production_shaped_moved=0 of 144 []; baseline_paths joint_shortcut=48 per_slot=96 count; shortcut_always_off_moved=0 of 144; thread_factor=1.000; load1=0.47.

Inputs tried: 144 production-shaped fixtures (48 joint-shortcut); bound: the same sweep with the shortcut disabled outright.

Should have failed (D3.M4): none: the mutant only skips the joint shortcut on an exact float tie joint_temps == joint_limit + 1e-9, and skipping it always moves no plan (shortcut_always_off_moved 0 of 144)

Equivalent-candidate: production_shaped_moved 0 of 144; bounded by shortcut_always_off_moved 0 of 144.

## Killed (non-findings)


## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/build_records.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/build_report.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_111763243ac44278.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_168e4035dbc9bb84.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_24d9995ccee4252e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_49dc3d36092b3943.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_5941c09a9face079.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_597d6753c0939797.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_677019b333cfa304.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_681130c48add1573.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_7030f8259cc37dd4.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_72240d3f22ceb752.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_8297234e122897ff.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_af8d4fddad8f298f.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_b020c93535a7f9e6.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c0bd33b7c209982d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c61a89f42607c92b.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_df4de55e12588fdf.py`

## Exposure

No docs/ or GitHub read. Read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json, bugclasses.json ids, the carried slice reports (REPORT-D3-u1{a,b,c,d}, REPORT-u1a, REPORT-D3-top6, REPORT-D3-rem) and their M4 answers for this box's keys, the production lines under test, and the keys.tsv of the sibling dispatch refs dispatch/finder-r11-D3-g01..g47 (key lists only, for the not_reached rows). No register, round11/J/ or verifier report read.

