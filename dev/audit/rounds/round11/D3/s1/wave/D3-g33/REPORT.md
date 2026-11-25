# D3-s1 round 11, box D3-g33: full gate for 16 D3.M3 full-net survivors (wave), baseline 92d38ecb

## Machine and controls

First container (null and gates 1-7):

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1073       13510          12        1802       15014
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.79
Sun Nov 22 21:44:11 UTC 2026
```

Re-fired container (gates 8-16 and the 0b6e291153f1d738 re-gate; the null reused from the checkpoint):

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         799       14012          12        1546       15287
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.45
Wed Nov 25 00:52:18 UTC 2026
```

Null control (`fullgate.py null`, comment-only marker): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, summary ['3 TEST SCRIPT(S) FAILED'], wall 3964.5 s, load1 0.69..0.98 (provisional). The three red scripts are artefact checks of the stripped tree. A mutant counts KILLED only when a script fails beyond this null; red with no script beyond it is RED-AS-NULL (read as survived).

Every wall, CPU and load figure is provisional (nproc 4; Intel Xeon @ 2.10GHz first container, @ 2.30GHz re-fire; the judge re-takes it); counts are final. Probes apply the mutant in memory to `git show <baseline>:sysid.py`, never to the gate's tree.

### Box artefact, set aside

Gate 0b6e291153f1d738 (2026-11-25 00:52-01:39Z) ran with the box's 16 step-4 probes present under wave/D3-g33/probes/
(restored there by `gate_wave.sh restore` on the re-fire). tests/harness_headers.py's check "every inlined walk matches the
canonical helper and no depth root remains" FAILED naming those probe files (4 FAIL lines vs the null's 3), so fullgate.py
read KILLED by python3 tests/harness_headers.py. Every earlier gate of this box, and the null, read that check `ok`.
The kill is an artefact of the box's own files in the gated tree, not of the mutant: the record is set aside here and the key is
re-gated with the probes held outside the tree (they stay in the checkpointed seat dir). Gate e38d4bea802156c3 was running when
the probes were moved out (01:55Z, before harness_headers.py ran); its log is checked for the same line.

## Tally

Gated 16 of 16 keys; verdicts {'RED-AS-NULL': 15, 'KILLED': 1}; classes {'candidate': 10, 'equivalent-candidate': 5, 'killed': 1}.

| key | site | function | full gate | killed by | wall s | load1 | class |
|---|---|---|---|---|---|---|---|
| 822c0c6477ed703e | sysid.py:1708 CMP_BOUND | SystemIdentification._unadoptable | RED-AS-NULL | - | 3784.1 | 0.92..0.92 | candidate |
| adc459d2db521041 | sysid.py:1708 CMP_BOUND | SystemIdentification._unadoptable | RED-AS-NULL | - | 3670.4 | 0.85..1.0 | candidate |
| a23ed12204379870 | sysid.py:1715 CMP_BOUND | SystemIdentification._unadoptable | RED-AS-NULL | - | 3600.7 | 0.92..1.0 | candidate |
| 6e67f128730b3ecd | sysid.py:1541 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 3713.1 | 0.85..0.92 | candidate |
| cf96494341270371 | sysid.py:1541 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 3761.2 | 0.72..0.92 | candidate |
| ad7a177d7ca99cad | sysid.py:1545 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 3500.8 | 0.8..0.96 | equivalent-candidate |
| b61d1402aad5a055 | sysid.py:1545 GUARD_OFF | SystemIdentification.conditions_met | RED-AS-NULL | - | 3572.4 | 0.74..1.25 | equivalent-candidate |
| 0b6e291153f1d738 | sysid.py:1546 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 3209.8 | 0.74..1.01 | equivalent-candidate |
| e38d4bea802156c3 | sysid.py:1546 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 2788.3 | 0.78..0.92 | equivalent-candidate |
| 20e001c48fb19330 | sysid.py:1549 CMP_BOUND | SystemIdentification.conditions_met | RED-AS-NULL | - | 2721.6 | 0.79..0.92 | candidate |
| d435f0054d7c9881 | sysid.py:1557 BOOLOP | SystemIdentification.conditions_met | RED-AS-NULL | - | 2715.5 | 0.86..0.94 | equivalent-candidate |
| 95090bc58c6535b2 | sysid.py:1913 CMP_BOUND | SystemIdentification.identify | RED-AS-NULL | - | 2707.3 | 0.87..0.92 | candidate |
| 505422349a01c3ff | sysid.py:1922 CMP_BOUND | SystemIdentification.identify | RED-AS-NULL | - | 2777.2 | 0.78..0.86 | candidate |
| 7dbbb95252ced538 | sysid.py:1922 CMP_BOUND | SystemIdentification.identify | RED-AS-NULL | - | 2978.4 | 0.75..0.92 | candidate |
| b413c17079bb8176 | sysid.py:1922 GUARD_OFF | SystemIdentification.identify | KILLED | python3 tests/structure.py | 3105.8 | 0.85..1.0 | killed |
| aa6d264aa0411bcd | sysid.py:1942 CMP_BOUND | SystemIdentification.identify | RED-AS-NULL | - | 3045.7 | 0.85..1.0 | candidate |

## Survivors: the step-4 answer and the probe numbers

### 822c0c6477ed703e sysid.py:1708 CMP_BOUND (SystemIdentification._unadoptable): RED-AS-NULL, candidate

Patch `or self._baseline_temp is None or not 1e-3 < dt <= 2.0 -> or self._baseline_temp is None or not 1e-3 <= dt <= 2.0`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_822c0c6477ed703e.py [--mutant]`: metric consulted_tie 0 -> 1, null consulted_null 1 -> 1. Baseline: consulted_tie=0; refuses_tie=0; halfwidth_tie=[]; refuses_tie_stub=0; consulted_below=0; consulted_above=1; consulted_null=1. Mutant: consulted_tie=1; refuses_tie=1; halfwidth_tie=[0.145803120583144]; refuses_tie_stub=1; consulted_below=0; consulted_above=1; consulted_null=1.

Inputs tried: settle interval 0.001 h (the tie), 0.0009 h, 0.0011 h; null 0.25 h; real halfwidth and a stub returning 1.0 (> bar).

Reach: reachable only when two settle samples land exactly 3.6 s apart: a float tie a coordinator cycle rarely produces.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:1708; tests/entities.py too): no check drives _unadoptable with two settle samples exactly 1e-3 h apart asserting it returns None without reading the declared night; the nearest check, tests/dst_checks.py:2309-2329, drives it only at a 1.0 h interval

Candidate: **No check pins _unadoptable's lower settle-interval edge (dt == 1e-3 h); <-> <= is unseen** (low, class_guess I1). Perturbation direction up. Null: consulted_null: 1 -> 1 (an input where the edit cannot matter).

### adc459d2db521041 sysid.py:1708 CMP_BOUND (SystemIdentification._unadoptable): RED-AS-NULL, candidate

Patch `or self._baseline_temp is None or not 1e-3 < dt <= 2.0 -> or self._baseline_temp is None or not 1e-3 < dt < 2.0`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_adc459d2db521041.py [--mutant]`: metric consulted_tie 1 -> 0, null consulted_null 1 -> 1. Baseline: consulted_tie=1; refuses_tie=1; halfwidth_tie=[0.11157312536429365]; refuses_tie_stub=1; consulted_below=1; consulted_above=0; consulted_null=1. Mutant: consulted_tie=0; refuses_tie=0; halfwidth_tie=[]; refuses_tie_stub=0; consulted_below=1; consulted_above=0; consulted_null=1.

Inputs tried: settle interval 2.0 h (the tie), 1.99 h, 2.01 h; null 0.25 h; real halfwidth and a stub returning 1.0 (> bar).

Reach: reachable only when two settle samples are exactly 7200 s apart (a stalled cycle landing on the edge).

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:1708; tests/entities.py too): no check drives _unadoptable with settle samples exactly 2.0 h apart asserting the declared night is still read (here it refuses); tests/dst_checks.py:2309-2329 uses 1.0 h only

Candidate: **No check pins _unadoptable's upper settle-interval edge (dt == 2.0 h); <= -> < is unseen** (low, class_guess I1). Perturbation direction down. Null: consulted_null: 1 -> 1 (an input where the edit cannot matter).

### a23ed12204379870 sysid.py:1715 CMP_BOUND (SystemIdentification._unadoptable): RED-AS-NULL, candidate

Patch `if hw <= UA_ADOPTION_HALFWIDTH_BAR: -> if hw < UA_ADOPTION_HALFWIDTH_BAR:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_a23ed12204379870.py [--mutant]`: metric refuses_tie 0 -> 1, null refuses_below 0 -> 0. Baseline: refuses_tie=0; refuses_above=1; refuses_below=0; refuses_real=1; halfwidth_real_minus_bar=[0.015294384822610571]. Mutant: refuses_tie=1; refuses_above=1; refuses_below=0; refuses_real=1; halfwidth_real_minus_bar=[0.015294384822610571].

Inputs tried: halfwidth == bar (stubbed, the tie), nextafter above/below, the real halfwidth on the dst_checks plant.

Reach: a float tie of a computed halfwidth with log(1.10): the probe stubs _declared_night_halfwidth to the bar; the real one on the dst_checks plant sits 0.0153 above it.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:1715; tests/entities.py too): no check sets the declared night's halfwidth exactly at UA_ADOPTION_HALFWIDTH_BAR asserting _unadoptable returns None (the adoption gate's own <= at sysid.py:1263 admits the tie)

Candidate: **No check pins _unadoptable's tie at the adoption bar (hw == UA_ADOPTION_HALFWIDTH_BAR); <= -> < is unseen** (low, class_guess I1). Perturbation direction up. Null: refuses_below: 0 -> 0 (an input where the edit cannot matter).

### 6e67f128730b3ecd sysid.py:1541 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, candidate

Patch `if not (cfg.min_outdoor_temp <= outdoor_temp <= cfg.max_outdoor_temp): -> if not (cfg.min_outdoor_temp < outdoor_temp <= cfg.max_outdoor_temp):`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_6e67f128730b3ecd.py [--mutant]`: metric band_refused 0 -> 1, null band_refused_inside 0 -> 0. Baseline: band_refused=0; band_refused_inside=0; band_refused_scan=10000. Mutant: band_refused=1; band_refused_inside=0; band_refused_scan=11000.

Inputs tried: outdoor -5.0 (the tie), -5.1, -4.9, 0.0 (null), 10.0.

Reach: reachable: production builds the default band (-5.0, 10.0) and an outdoor sensor reading of exactly -5.0 C is an ordinary 0.1-resolution value.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:1541): no conditions_met check at outdoor_temp == SysIdConfig.min_outdoor_temp (-5.0 C) asserting the safe-band check passes

Candidate: **No check pins conditions_met's inclusive lower outdoor bound (-5.0 C); <= -> < is unseen** (low, class_guess I1). Perturbation direction up. Null: band_refused_inside: 0 -> 0 (an input where the edit cannot matter).

### cf96494341270371 sysid.py:1541 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, candidate

Patch `if not (cfg.min_outdoor_temp <= outdoor_temp <= cfg.max_outdoor_temp): -> if not (cfg.min_outdoor_temp <= outdoor_temp < cfg.max_outdoor_temp):`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_cf96494341270371.py [--mutant]`: metric band_refused 0 -> 1, null band_refused_inside 0 -> 0. Baseline: band_refused=0; band_refused_inside=0; band_refused_scan=00001. Mutant: band_refused=1; band_refused_inside=0; band_refused_scan=00011.

Inputs tried: outdoor 10.0 (the tie), 9.9, 10.1, 0.0 (null), -5.0.

Reach: reachable: an outdoor reading of exactly 10.0 C at the default band.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:1541): no conditions_met check at outdoor_temp == SysIdConfig.max_outdoor_temp (10.0 C) asserting the safe-band check passes

Candidate: **No check pins conditions_met's inclusive upper outdoor bound (10.0 C); <= -> < is unseen** (low, class_guess I1). Perturbation direction up. Null: band_refused_inside: 0 -> 0 (an input where the edit cannot matter).

### ad7a177d7ca99cad sysid.py:1545 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, equivalent-candidate

Patch `if cfg.start_hour <= cfg.end_hour: -> if cfg.start_hour < cfg.end_hour:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_ad7a177d7ca99cad.py [--mutant]`: metric open_hours_tie 0 -> 24, null open_hours_default 6 -> 6. Baseline: open_hours_default=6; open_hours_tie=0; open_hours_tie0=0; open_hours_flat=4; open_hours_wrap2=4. Mutant: open_hours_default=6; open_hours_tie=24; open_hours_tie0=24; open_hours_flat=4; open_hours_wrap2=4.

Inputs tried: windows (23,5) default, (3,3) tie, (0,0), (1,5) non-wrapping, (22,2); each over hours 0..23.

Reach: unreachable through production (open_hours_default 6 under both arms).

Should have failed (D3.M4): none through production: coordinator.py:4044 builds SysIdConfig without start_hour/end_hour, so the window is always (23, 5) and start_hour == end_hour never occurs; a direct unit call with start_hour == end_hour separates

### b61d1402aad5a055 sysid.py:1545 GUARD_OFF (SystemIdentification.conditions_met): RED-AS-NULL, equivalent-candidate

Patch `if cfg.start_hour <= cfg.end_hour: -> if False:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_b61d1402aad5a055.py [--mutant]`: metric open_hours_flat 4 -> 24, null open_hours_default 6 -> 6. Baseline: open_hours_default=6; open_hours_flat=4; open_hours_flat06=6; open_hours_tie=0; open_hours_wrap2=4. Mutant: open_hours_default=6; open_hours_flat=24; open_hours_flat06=24; open_hours_tie=24; open_hours_wrap2=4.

Inputs tried: windows (23,5) default, (1,5), (0,6), (3,3), (22,2); each over hours 0..23.

Reach: unreachable through production (open_hours_default 6 under both arms).

Should have failed (D3.M4): none through production: coordinator.py:4045 builds SysIdConfig without start_hour/end_hour, so the window is always the wrapping default (23, 5) and the non-wrapping branch never runs; a direct unit call with a non-wrapping window (1,5) separates (4 -> 24 open hours)

### 0b6e291153f1d738 sysid.py:1546 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, equivalent-candidate

Patch `in_window = cfg.start_hour <= hour < cfg.end_hour -> in_window = cfg.start_hour <= hour <= cfg.end_hour`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_0b6e291153f1d738.py [--mutant]`: metric open_hours_flat 4 -> 5, null open_hours_default 6 -> 6. Baseline: open_hours_default=6; open_hours_flat=4; end_hour_open=0; open_hours_flat06=6; open_hours_wrap2=4. Mutant: open_hours_default=6; open_hours_flat=5; end_hour_open=1; open_hours_flat06=7; open_hours_wrap2=4.

Inputs tried: windows (23,5) default, (1,5), (0,6), (22,2); each over hours 0..23.

Reach: unreachable through production (open_hours_default 6 under both arms).

Should have failed (D3.M4): none through production: coordinator.py:4045 builds SysIdConfig without start_hour/end_hour, so only the wrapping default (23, 5) runs and the non-wrapping branch at sysid.py:1546 never executes in production; a direct unit call with window (1,5) separates (4 -> 5 open hours)

### e38d4bea802156c3 sysid.py:1546 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, equivalent-candidate

Patch `in_window = cfg.start_hour <= hour < cfg.end_hour -> in_window = cfg.start_hour < hour < cfg.end_hour`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_e38d4bea802156c3.py [--mutant]`: metric open_hours_flat 4 -> 3, null open_hours_default 6 -> 6. Baseline: open_hours_default=6; open_hours_flat=4; start_hour_open=1; open_hours_flat06=6; open_hours_wrap2=4. Mutant: open_hours_default=6; open_hours_flat=3; start_hour_open=0; open_hours_flat06=5; open_hours_wrap2=4.

Inputs tried: windows (23,5) default, (1,5), (0,6), (22,2); each over hours 0..23.

Reach: unreachable through production (open_hours_default 6 under both arms).

Should have failed (D3.M4): none through production: coordinator.py:4045 builds SysIdConfig without start_hour/end_hour, so only the wrapping default (23, 5) runs and the non-wrapping branch at sysid.py:1546 never executes in production; a direct unit call with window (1,5) separates (4 -> 3 open hours)

### 20e001c48fb19330 sysid.py:1549 CMP_BOUND (SystemIdentification.conditions_met): RED-AS-NULL, candidate

Patch `in_window = hour >= cfg.start_hour or hour < cfg.end_hour -> in_window = hour >= cfg.start_hour or hour <= cfg.end_hour`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_20e001c48fb19330.py [--mutant]`: metric open_hours 6 -> 7, null open_hours_flat 4 -> 4. Baseline: open_hours=6; end_hour_open=0; open_hours_flat=4; open_hours_wrap2=4. Mutant: open_hours=7; end_hour_open=1; open_hours_flat=4; open_hours_wrap2=5.

Inputs tried: default window (23,5) over hours 0..23; null (1,5); (22,2).

Reach: reachable: production builds the default wrapping window (23, 5); under the mutant the 05:00-05:59 hour is admitted.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:{line}): no conditions_met check at hour == SysIdConfig().end_hour (5) under the default window asserting it refuses with 'outside the night window'

Candidate: **No check pins conditions_met's exclusive night-window end (05:00) on the default window; < -> <= is unseen** (low, class_guess I1). Perturbation direction up. Null: open_hours_flat (non-wrapping window (1,5), branch not taken): 4 -> 4.

### d435f0054d7c9881 sysid.py:1557 BOOLOP (SystemIdentification.conditions_met): RED-AS-NULL, equivalent-candidate

Patch `if price_horizon is not None and len(price_horizon): -> if price_horizon is not None or len(price_horizon):`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_d435f0054d7c9881.py [--mutant]`: metric raised 0 -> 2, null ok_ramp 1 -> 1. Baseline: raised=0; ok_ramp=1; ok_flat=1. Mutant: raised=2; ok_ramp=1; ok_flat=1.

Inputs tried: price_horizon None, np.array([]), ramp 0.5..2.0 (24 steps), flat ones(24); price 0.5.

Reach: unreachable through production: the only caller (sysid.py:1756) runs after coordinator.py:6379 has returned 'no_prices' for any horizon of fewer than 4 steps, so neither None nor an empty horizon reaches it.

Should have failed (D3.M4): none through production; a direct unit call with price_horizon None or empty separates (raised 0 -> 2)

### 95090bc58c6535b2 sysid.py:1913 CMP_BOUND (SystemIdentification.identify): RED-AS-NULL, candidate

Patch `if len(usable) < 6: -> if len(usable) <= 6:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_95090bc58c6535b2.py [--mutant]`: metric reached_fit_6 1 -> 0, null reached_fit_7 1 -> 1. Baseline: reached_fit_5=0; reached_fit_6=1; reached_fit_7=1; reached_fit_21=1; reason_6='ok'. Mutant: reached_fit_5=0; reached_fit_6=0; reached_fit_7=1; reached_fit_21=1; reason_6='not enough samples'.

Inputs tried: 5, 6 (the tie), 7, 21 samples at 0.25 h on the tests/features.py _sid_samples plant.

Reach: reachable: an experiment that collects exactly six usable samples (a 1.5 h run at the 15-min cadence) is refused 'not enough samples' under the mutant.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:{line}): no identify check on exactly six usable samples asserting it gets past the sample-count gate (the documented minimum is six)

Candidate: **No check pins identify's six-sample minimum at the tie; < 6 -> <= 6 is unseen** (low, class_guess I1). Perturbation direction down. Null: reached_fit_7 (seven samples): 1 -> 1.

### 505422349a01c3ff sysid.py:1922 CMP_BOUND (SystemIdentification.identify): RED-AS-NULL, candidate

Patch `if dt_h <= 1e-3 or dt_h > 2.0: -> if dt_h < 1e-3 or dt_h > 2.0:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_505422349a01c3ff.py [--mutant]`: metric reached_fit_tie 0 -> 1, null reached_fit_null 1 -> 1. Baseline: reached_fit_tie=0; reached_fit_below=0; reached_fit_above=1; reached_fit_zero=0; reached_fit_null=1; ua_31=None reason='fitted gains outside plausible bounds'; ua_31_null=0.11999999998433901 reason='ok'. Mutant: reached_fit_tie=1; reached_fit_below=0; reached_fit_above=1; reached_fit_zero=0; reached_fit_null=1; ua_31=None reason='fit gave implausible signs'; ua_31_null=0.11999999998433901 reason='ok'.

Inputs tried: interval 0.001 h (the tie), 0.0009 h, 0.0011 h, 0.0 h; null all 0.25 h; ua_31 on tests/features.py's 31-sample series with one 3.6 s interval.

Reach: reachable only when two samples land exactly 3.6 s apart: a float tie a coordinator cycle rarely produces.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:{line}): no identify check with an interval exactly 1e-3 h asserting it is dropped as unusable

Candidate: **No check pins identify's exclusive 1e-3 h minimum interval at the tie; <= -> < is unseen** (low, class_guess I1). Perturbation direction up. Null: reached_fit_null (all 15-min intervals): 1 -> 1.

### 7dbbb95252ced538 sysid.py:1922 CMP_BOUND (SystemIdentification.identify): RED-AS-NULL, candidate

Patch `if dt_h <= 1e-3 or dt_h > 2.0: -> if dt_h <= 1e-3 or dt_h >= 2.0:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_7dbbb95252ced538.py [--mutant]`: metric reached_fit_tie 1 -> 0, null reached_fit_null 1 -> 1. Baseline: reached_fit_tie=1; reached_fit_below=1; reached_fit_above=0; reached_fit_null=1; ua_31=None reason='fit gave implausible signs'; ua_31_null=0.11999999998433901 reason='ok'. Mutant: reached_fit_tie=0; reached_fit_below=1; reached_fit_above=0; reached_fit_null=1; ua_31=None reason='fit gave implausible signs'; ua_31_null=0.11999999998433901 reason='ok'.

Inputs tried: interval 2.0 h (the tie), 1.99 h, 2.01 h; null all 0.25 h; ua_31 on tests/features.py's 31-sample series with one 2.0 h interval.

Reach: reachable only when two samples are exactly 7200 s apart (a stalled cycle landing on the edge).

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:{line}): no identify check with an interval exactly 2.0 h asserting it is kept as usable

Candidate: **No check pins identify's inclusive 2.0 h maximum interval at the tie; > -> >= is unseen** (low, class_guess I1). Perturbation direction down. Null: reached_fit_null (all 15-min intervals): 1 -> 1.

### aa6d264aa0411bcd sysid.py:1942 CMP_BOUND (SystemIdentification.identify): RED-AS-NULL, candidate

Patch `if len(rows) < 5: -> if len(rows) <= 5:`. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_aa6d264aa0411bcd.py [--mutant]`: metric reached_fit_6 1 -> 0, null reached_fit_7 1 -> 1. Baseline: reached_fit_6=1; reached_fit_7=1; reached_fit_7_gap=1; reason_6='ok'. Mutant: reached_fit_6=0; reached_fit_7=1; reached_fit_7_gap=0; reason_6='not enough usable intervals'.

Inputs tried: 6 samples (5 intervals, the tie), 7 samples, 8 samples with one 3.6 s interval (5 usable).

Reach: reachable: six usable samples give five usable intervals, which the mutant refuses 'not enough usable intervals'.

Should have failed (D3.M4): tests/features.py (traced, executes sysid.py:{line}): no identify check on exactly five usable intervals asserting it gets past the interval-count gate

Candidate: **No check pins identify's five-interval minimum at the tie; < 5 -> <= 5 is unseen** (low, class_guess I1). Perturbation direction down. Null: reached_fit_7 (six intervals): 1 -> 1.

## Killed (non-findings)

- b413c17079bb8176 sysid.py:1922 GUARD_OFF `if dt_h <= 1e-3 or dt_h > 2.0: -> if False:`: KILLED by ['python3 tests/structure.py'] (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key b413c17079bb8176`); {'python3 tests/structure.py': ['gain max_cc 43 (budget 44, -1; not yet recorded -- see below)', '1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED', '>>> FAILED: python3 tests/structure.py']}. KILLED by the structural ratchet only: if False: removes one decision point from identify (sysid.py:1890, cc 44 -> 43, the tree's max_cc), and structure.py refuses an unrecorded improvement (#350). No behavioural check failed: every other red script is the null's own (closure.py selftest 2, entities.py 1, harness_headers.py 3 FAIL lines, equal to the null). The step-4 probe still moves (raised_dup 0 -> 1: a duplicated timestamp makes identify raise ZeroDivisionError; reached_fit_gap 0 -> 1). Carried as a lead: a GUARD_OFF that keeps the decision count (e.g. `if dt_h != dt_h:`) might escape the ratchet (untested hypothesis, not gated).

## Leads

- D3, custom_components/heatpump_optimizer/sysid.py SystemIdentification.identify: b413c17079bb8176 (sysid.py:1922 GUARD_OFF, if dt_h <= 1e-3 or dt_h > 2.0: -> if False:) is KILLED only by the tests/structure.py max_cc ratchet, not by a behavioural check: KILLED by the structural ratchet only: if False: removes one decision point from identify (sysid.py:1890, cc 44 -> 43, the tree's max_cc), and structure.py refuses an unrecorded improvement (#350). No behavioural check failed: every other red script is the null's own (closure.py selftest 2, entities.py 1, harness_headers.py 3 FAIL lines, equal to the null). The step-4 probe still moves (raised_dup 0 -> 1: a duplicated timestamp makes identify raise ZeroDivisionError; reached_fit_gap 0 -> 1). Carried as a lead: a GUARD_OFF that keeps the decision count (e.g. `if dt_h != dt_h:`) might escape the ratchet (untested hypothesis, not gated).
- orchestrator (gate_wave.sh), gate_wave.sh restore restore: a re-fire's `gate_wave.sh restore` copies the checkpointed probes/*.py back into the gated tree, where tests/harness_headers.py's inlined-walk check fails on them and fullgate.py reads the next gate KILLED; on this box it hit 0b6e291153f1d738 (record set aside under gates-artefact/, key re-gated with the probes held outside the tree)

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/build_records.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/build_report.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_0b6e291153f1d738.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_20e001c48fb19330.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_505422349a01c3ff.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_6e67f128730b3ecd.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_7dbbb95252ced538.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_822c0c6477ed703e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_95090bc58c6535b2.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_a23ed12204379870.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_aa6d264aa0411bcd.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_ad7a177d7ca99cad.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_adc459d2db521041.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_b413c17079bb8176.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_b61d1402aad5a055.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_cf96494341270371.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_d435f0054d7c9881.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g33/probes/probe_e38d4bea802156c3.py`

Procedure: gate_wave.sh (shipped on dispatch/finder-r11-D3-g33): null once, then for each key of keys.tsv in order: reset the tree to the baseline, `timeout -s INT -k 300 14400 python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` (apply the one-line mutant, commit, take the gate_lock lease, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh, record, reset), checkpoint after every gate

## Exposure

No docs/ or GitHub read. Two seats on this box: the first (stalled) took the null, gated 7 keys and wrote the probes and 6 records; the re-fire resumed from its checkpoint and read COMMON.md, D3.md, finding.schema.json's location, REPORT-D3-u1b.json's coverage rows, the production lines under test (sysid.py, coordinator.py:4045 and :6379), and box D3-g13's returned build_report.py and wave_boxes/ key lists (handoff/audit-r11-find-D3-g13; key lists and the report builder only, not its results). No register, round11/J/ or verifier report read.

