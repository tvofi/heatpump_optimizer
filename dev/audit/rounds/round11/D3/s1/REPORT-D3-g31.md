# D3-s1 box D3-g31: full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, wave box D3-g31, keys `dev/audit/rounds/round11/D3/s1/wave/D3-g31/keys.tsv` (price_model.py).

## Machine and controls

```
date: 2026-11-22T21:44:06Z
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1071       13512          12        1801       15015
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.73
python3: /opt/hpo/venv-ci/bin/python3 ($HOME/venv-ci symlinked to it; not present at $HOME/venv-ci in this container)
```

Walls, CPU and load numbers are provisional (nproc 4, Intel Xeon @ 2.10GHz); counts are final. Gates 1-6 ran in the predecessor container (same machine class), 7-16 in this one.

Null control: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null` -> gate_rc 1, red scripts python3 tests/closure.py selftest, python3 tests/entities.py, python3 tests/harness_headers.py with fail lines {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/harness_headers.py": 3}; wall 3735.7 s, load1 0.79 -> 1.01. Each is an artefact of the stripped, detached worktree (closure.py selftest scoped-merge rows, entities.py scoped-path row, harness_headers.py round-4 claims.py counts), none machine-caused; usable, not re-taken. A mutant counts KILLED only with a script beyond these or more FAIL lines in one of them.

Procedure: gate_wave.sh (dispatch ref dispatch/finder-r11-D3-g31 @ b51b9818): `null` runs fullgate.py null once; `run` runs fullgate.py run --src <src> --key <key> for each keys.tsv row in order, one at a time, 4 h cap (timeout -s INT), checkpoint after each gate. Gates 1-6 ran on the predecessor container (restored), 7-16 here; the first attempt at gate 7 was interrupted at start and its mutant reverted (git checkout) before the gate was re-run from scratch.

## Tally

- gated: 16 of 16
- KILLED: 0
- SURVIVED: 0
- RED-AS-NULL: 16
- TIMEOUT: 0
- candidates (gate survivors whose probe moves): 6
- equivalent-candidates: 10

| key | site | function | verdict | gate_rc | wall_s | class |
|---|---|---|---|---|---|---|
| `ba9f6b92f678ab10` | custom_components/heatpump_optimizer/price_model.py:303 GUARD_OFF | PriceShapeModel.quarter_factor | RED-AS-NULL | 1 | 3500.5 | equivalent-candidate |
| `c9f07b68ade152e6` | custom_components/heatpump_optimizer/price_model.py:303 CMP_BOUND | PriceShapeModel.quarter_factor | RED-AS-NULL | 1 | 3498.0 | equivalent-candidate |
| `45cd5752f930a064` | custom_components/heatpump_optimizer/price_model.py:357 GUARD_OFF | PriceShapeModel.sigma | RED-AS-NULL | 1 | 3684.4 | equivalent-candidate |
| `e72d16a241bfa7be` | custom_components/heatpump_optimizer/price_model.py:357 CMP_BOUND | PriceShapeModel.sigma | RED-AS-NULL | 1 | 3513.2 | equivalent-candidate |
| `3a064c11321daba7` | custom_components/heatpump_optimizer/price_model.py:417 CLAMP_DROP | PriceShapeModel.summary | RED-AS-NULL | 1 | 3546.4 | candidate |
| `efa02472a5a773bc` | custom_components/heatpump_optimizer/price_model.py:421 CLAMP_DROP | PriceShapeModel.summary | RED-AS-NULL | 1 | 3511.6 | candidate |
| `6743e8b3d654cd32` | custom_components/heatpump_optimizer/price_model.py:586 GUARD_OFF | _entries_by_day | RED-AS-NULL | 1 | 3247.1 | equivalent-candidate |
| `a38612ad3ad9cd34` | custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND | _in_domain | RED-AS-NULL | 1 | 3093.6 | candidate |
| `f06caefa38815e4f` | custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND | _in_domain | RED-AS-NULL | 1 | 3040.4 | candidate |
| `28de20de50a9540b` | custom_components/heatpump_optimizer/price_model.py:155 CMP_BOUND | _profile_index | RED-AS-NULL | 1 | 3065.5 | candidate |
| `e5eea05f4463602e` | custom_components/heatpump_optimizer/price_model.py:844 GUARD_OFF | _tibber_post | RED-AS-NULL | 1 | 3139.5 | candidate |
| `3ceb6a076659004f` | custom_components/heatpump_optimizer/price_model.py:510 GUARD_OFF | extend_price_series | RED-AS-NULL | 1 | 3269.1 | equivalent-candidate |
| `b434193b049a41c3` | custom_components/heatpump_optimizer/price_model.py:510 CMP_BOUND | extend_price_series | RED-AS-NULL | 1 | 3394.5 | equivalent-candidate |
| `29db99dee6a5debd` | custom_components/heatpump_optimizer/price_model.py:532 CLAMP_DROP | extend_price_series | RED-AS-NULL | 1 | 3419.4 | equivalent-candidate |
| `886591ca08e1d27e` | custom_components/heatpump_optimizer/price_model.py:535 CMP_BOUND | extend_price_series | RED-AS-NULL | 1 | 3587.5 | equivalent-candidate |
| `c1e06ebefdc5abad` | custom_components/heatpump_optimizer/price_model.py:541 CMP_BOUND | extend_price_series | RED-AS-NULL | 1 | 3519.5 | equivalent-candidate |

## Survivors: step-4 answers and probe numbers

### `3a064c11321daba7` custom_components/heatpump_optimizer/price_model.py:417 CLAMP_DROP (candidate)

Patch `round(float(np.sqrt(max(0.0, v))), 4)` -> `round(float(np.sqrt((0.0))), 4)` in `PriceShapeModel.summary`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/3a064c11321daba7.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_3a064c11321daba7.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_3a064c11321daba7.py`): baseline **weekday_sigma max=0.538 (24 of 24 bins non-zero after 28 observed days)**; mutant **weekday_sigma max=0.0 (24 of 24 bins zero)**. Inputs tried: 28 days folded by observe_day (seeded rng 11, Mon 2026-01-05..); null: a fresh model (residual_var 0).

Claim: Replacing price_model.py:417 sqrt(max(0, v)) by sqrt(0) in PriceShapeModel.summary publishes an all-zero weekday_sigma after 28 learned days (0.538 -> 0.0) and the full GATE_SCOPE=full GOLDEN_MODE=drift gate stays green

Should have failed: tests/features.py, which drives the coordinator's _grid_view (price_prior: PriceShapeModel.summary()) on the traced baseline (carried full-net scripts_ran), lacks an assertion that price_prior.weekday_sigma equals sqrt(residual_var) after observed days; no check in tests/ names weekday_sigma at all (grep count 0)

Severity claimed medium, class guess I1; metric: max over the 24 bins of PriceShapeModel.summary()['weekday_sigma'] after 28 observe_day folds (seeded); perturbation direction to_zero.

### `efa02472a5a773bc` custom_components/heatpump_optimizer/price_model.py:421 CLAMP_DROP (candidate)

Patch `round(float(np.sqrt(max(0.0, v))), 4)` -> `round(float(np.sqrt((0.0))), 4)` in `PriceShapeModel.summary`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/efa02472a5a773bc.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_efa02472a5a773bc.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_efa02472a5a773bc.py`): baseline **weekend_sigma max=0.4726 (24 of 24 bins non-zero after 28 observed days)**; mutant **weekend_sigma max=0.0 (24 of 24 bins zero)**. Inputs tried: 28 days folded by observe_day (seeded rng 11, Mon 2026-01-05..); null: a fresh model (residual_var 0).

Claim: Replacing price_model.py:421 sqrt(max(0, v)) by sqrt(0) in PriceShapeModel.summary publishes an all-zero weekend_sigma after 28 learned days (0.4726 -> 0.0) and the full GATE_SCOPE=full GOLDEN_MODE=drift gate stays green

Should have failed: tests/features.py, which drives the coordinator's _grid_view (price_prior: PriceShapeModel.summary()) on the traced baseline (carried full-net scripts_ran), lacks an assertion that price_prior.weekend_sigma equals sqrt(residual_var) after observed days; no check in tests/ names weekend_sigma at all (grep count 0)

Severity claimed medium, class guess I1; metric: max over the 24 bins of PriceShapeModel.summary()['weekend_sigma'] after 28 observe_day folds (seeded); perturbation direction to_zero.

### `a38612ad3ad9cd34` custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND (candidate)

Patch `if low > 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):` -> `if low >= 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):` in `_in_domain`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/a38612ad3ad9cd34.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_a38612ad3ad9cd34.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_a38612ad3ad9cd34.py`): baseline **all-zero persisted weekday shape restored as all 1.0 (one warning); guessed 17:00 price at level 1.0 = 1.0**; mutant **restored as all 0.0 (no warning); guessed 17:00 price = 0.0**. Inputs tried: persisted weekday shapes: all zero, one zero bin, a negative bin, exactly at the guard's bound, nextafter above/below it, flat ones, the learner's cone edge [0.2]*23+[3.0].

Claim: With price_model.py:141 `low > 0.0` -> `low >= 0.0`, PriceShapeModel.from_dict keeps an all-zero persisted shape (max |shape delta| 1.0, warning count 1 -> 0) so every guessed price past the published horizon is 0.0 instead of the level, and the full gate stays green

Should have failed: tests/features.py and tests/finite_boundary.py (carried should_have_failed; both restore PriceShapeModel via from_dict on the traced baseline) lack a restore of an all-zero persisted shape asserting the D1-s5-02 clip (shape renormalised to 1.0, a warning); tests/entities.py:42270 only counts _in_domain's call sites

Severity claimed low, class guess I1; metric: max |restored shape - mutant restored shape| for a persisted all-zero weekday shape, and predict(Wed 17:00, level 1.0); perturbation direction to_zero.

### `f06caefa38815e4f` custom_components/heatpump_optimizer/price_model.py:141 CMP_BOUND (candidate)

Patch `if low > 0.0 and high <= low * (hi / lo) * (1.0 + 1e-9):` -> `if low > 0.0 and high < low * (hi / lo) * (1.0 + 1e-9):` in `_in_domain`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/f06caefa38815e4f.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_f06caefa38815e4f.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_f06caefa38815e4f.py`): baseline **profile [0.5]*23+[bound] restored unchanged, 0 warnings; guessed 17:00 price at level 1.0 = 0.5**; mutant **clipped and renormalised (max |delta| 2.53448), 1 warning; guessed 17:00 price = 0.827586**. Inputs tried: persisted weekday shapes: all zero, one zero bin, a negative bin, exactly at the guard's bound, nextafter above/below it, flat ones, the learner's cone edge [0.2]*23+[3.0].

Claim: With price_model.py:141 `high <= bound` -> `high < bound`, PriceShapeModel.from_dict clips and renormalises a persisted profile whose max sits exactly at low*(hi/lo)*(1+1e-9) (max |delta| 2.53448, warnings 0 -> 1) and the full gate stays green

Should have failed: tests/features.py and tests/finite_boundary.py (restore PriceShapeModel via from_dict on the traced baseline) lack a restore of a profile whose max/min ratio sits exactly at the guard's bound asserting it is returned unchanged and unwarned

Severity claimed low, class guess I1; metric: max |restored shape delta| and warning count for a persisted shape [0.5]*23+[0.5*(3.0/0.2)*(1+1e-9)]; perturbation direction up.

### `28de20de50a9540b` custom_components/heatpump_optimizer/price_model.py:155 CMP_BOUND (candidate)

Patch `return PROFILE_WEEKEND if when.weekday() >= 5 else PROFILE_WEEKDAY` -> `return PROFILE_WEEKEND if when.weekday() > 5 else PROFILE_WEEKDAY` in `_profile_index`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/28de20de50a9540b.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_28de20de50a9540b.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_28de20de50a9540b.py`): baseline **weekend days 2, weekday days 5 after one Mon..Sun week; Saturday 03:00 guessed price at level 1.0 = 0.737143**; mutant **weekend days 1, weekday days 6; Saturday 03:00 guessed price = 0.564779**. Inputs tried: one week of hourly rows Mon 2026-01-05..Sun 01-11 folded by PriceShapeLearner.fold with distinct weekday/weekend shapes; null: Mon-Fri and Sunday profile indices.

Claim: With price_model.py:155 `weekday() >= 5` -> `> 5`, one folded week learns 1 weekend day instead of 2 and the Saturday 03:00 guessed price at level 1.0 moves 0.737143 -> 0.564779, and the full gate stays green

Should have failed: tests/features.py, which folds price days through PriceShapeLearner on the traced baseline, lacks a check folding a Saturday and asserting it lands in PROFILE_WEEKEND (no check in tests/ names _profile_index or PROFILE_WEEKEND; grep count 0)

Severity claimed medium, class guess I1; metric: model.days[PROFILE_WEEKEND] after folding one Mon..Sun week, and predict(Sat 03:00, level 1.0); perturbation direction down.

### `e5eea05f4463602e` custom_components/heatpump_optimizer/price_model.py:844 GUARD_OFF (candidate)

Patch `if resp.status != 200:` -> `if False:` in `_tibber_post`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/e5eea05f4463602e.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e5eea05f4463602e.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e5eea05f4463602e.py`): baseline **401/403 text/html body -> verdict reauth; 502 text/html -> fail**; mutant **401/403/502 text/html -> aiohttp.ContentTypeError raised out of pull_prices (the coordinator catches it as an ordinary ClientError fetch failure, no reauth)**. Inputs tried: fake aiohttp session: 401, 403, 502 with a text/html body (resp.json() raises ContentTypeError), 500 and 401 with JSON error bodies, 200 with no homes.

Claim: With price_model.py:844 `if resp.status != 200:` -> `if False:`, pull_prices raises ContentTypeError instead of returning reauth for a 401/403 whose body is not JSON (3 of 6 reply shapes move), and the full gate stays green

Should have failed: tests/features.py's 'a refused token asks for REAUTH while a broken API is an ordinary failure' (_g8_pull) replaces _tibber_post with a scripted stub, so no check drives the real _tibber_post with a non-200 response; it lacks a case whose resp.json() raises

Severity claimed medium, class guess I1; metric: pull_prices' verdict per scripted Tibber reply (status, body) through the real _tibber_post; perturbation direction sign_flip.

### `ba9f6b92f678ab10` custom_components/heatpump_optimizer/price_model.py:303 GUARD_OFF (equivalent-candidate)

Patch `if trust <= 0.0:` -> `if False:` in `PriceShapeModel.quarter_factor`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/ba9f6b92f678ab10.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_ba9f6b92f678ab10.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_ba9f6b92f678ab10.py`): baseline **prod_differ=0 of 900; direct nan factor at trust 0 -> 1.0**; mutant **prod_differ=0 of 900; direct nan factor at trust 0 -> nan**. Inputs tried: from_dict-loaded models, quarter factor in {0.25,0.5,1.0,1.3,4.0,nan,inf,-1,0} x quarter_days {0,1,3,5,9} at 20 instants (weekday and weekend, every quarter mark); direct-constructed factors nan, inf, -inf, 1.3, 0.25 at trust 0.

Equivalent-candidate: At trust 0 the mutant returns 1 + (f - 1) * 0 == 1.0 for every finite factor; only a non-finite stored factor separates, and from_dict's _stored_rows rejects non-finite bins and _in_domain clips the rest to [0.25, 4.0], while the learner writes clipped finite factors. Equivalent through every load and learn path.

Check that would be owed if a distinguishing input is found: none through production; a direct unit call of quarter_factor on a constructed model with a non-finite factor at quarter_days 0 asserting 1.0 would

### `c9f07b68ade152e6` custom_components/heatpump_optimizer/price_model.py:303 CMP_BOUND (equivalent-candidate)

Patch `if trust <= 0.0:` -> `if trust < 0.0:` in `PriceShapeModel.quarter_factor`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/c9f07b68ade152e6.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c9f07b68ade152e6.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c9f07b68ade152e6.py`): baseline **prod_differ=0 of 900; direct nan factor at trust 0 -> 1.0**; mutant **prod_differ=0 of 900; direct nan factor at trust 0 -> nan**. Inputs tried: from_dict-loaded models, quarter factor in {0.25,0.5,1.0,1.3,4.0,nan,inf,-1,0} x quarter_days {0,1,3,5,9} at 20 instants (weekday and weekend, every quarter mark); direct-constructed factors nan, inf, -inf, 1.3, 0.25 at trust 0.

Equivalent-candidate: At trust 0 the mutant returns 1 + (f - 1) * 0 == 1.0 for every finite factor; only a non-finite stored factor separates, and from_dict's _stored_rows rejects non-finite bins and _in_domain clips the rest to [0.25, 4.0], while the learner writes clipped finite factors. Equivalent through every load and learn path.

Check that would be owed if a distinguishing input is found: none through production (trust = min(1, quarter_days/5) with quarter_days floored at 0 is never negative); only the direct non-finite-factor call separates

### `45cd5752f930a064` custom_components/heatpump_optimizer/price_model.py:357 GUARD_OFF (equivalent-candidate)

Patch `if var <= 0.0:` -> `if False:` in `PriceShapeModel.sigma`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/45cd5752f930a064.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_45cd5752f930a064.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_45cd5752f930a064.py`): baseline **prod_differ=0 of 840; direct var -1e-3 -> 0.0**; mutant **prod_differ=0 of 840; direct var -1e-3 -> nan**. Inputs tried: from_dict-loaded models, residual_var in {0,-0.0,1e-12,0.04,-0.01,-5} x days {0,1,5,9} x level {0,-0,0.5,2,-0.3,1e-300,1e300} at 5 instants; direct-constructed var -1e-3, var 0 with level inf/nan, var -0.0 with level inf.

Equivalent-candidate: from_dict floors residual_var at 0 (and the learner's EWMA of squares is >= 0), and extend_price_series passes a finite level (finite known prices over a shape mean > 1e-6), so var < 0 and a non-finite level never reach sigma; at var == 0 with a finite level the mutant's level*sqrt(0)*conf is 0.0 (or -0.0, equal). Equivalent through production.

Check that would be owed if a distinguishing input is found: none through production; a direct sigma call with a negative variance or a non-finite level asserting 0.0 would

### `e72d16a241bfa7be` custom_components/heatpump_optimizer/price_model.py:357 CMP_BOUND (equivalent-candidate)

Patch `if var <= 0.0:` -> `if var < 0.0:` in `PriceShapeModel.sigma`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/e72d16a241bfa7be.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e72d16a241bfa7be.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_e72d16a241bfa7be.py`): baseline **prod_differ=0 of 840; direct var 0, level inf -> 0.0**; mutant **prod_differ=0 of 840; direct var 0, level inf -> nan**. Inputs tried: from_dict-loaded models, residual_var in {0,-0.0,1e-12,0.04,-0.01,-5} x days {0,1,5,9} x level {0,-0,0.5,2,-0.3,1e-300,1e300} at 5 instants; direct-constructed var -1e-3, var 0 with level inf/nan, var -0.0 with level inf.

Equivalent-candidate: from_dict floors residual_var at 0 (and the learner's EWMA of squares is >= 0), and extend_price_series passes a finite level (finite known prices over a shape mean > 1e-6), so var < 0 and a non-finite level never reach sigma; at var == 0 with a finite level the mutant's level*sqrt(0)*conf is 0.0 (or -0.0, equal). Equivalent through production.

Check that would be owed if a distinguishing input is found: none through production; a direct sigma call at var 0 with a non-finite level asserting 0.0 would

### `6743e8b3d654cd32` custom_components/heatpump_optimizer/price_model.py:586 GUARD_OFF (equivalent-candidate)

Patch `if not np.isfinite(value):` -> `if False:` in `_entries_by_day`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/6743e8b3d654cd32.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_6743e8b3d654cd32.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_6743e8b3d654cd32.py`): baseline **ingress: (1,0) learned for a quarter day with one nan quarter; direct: (1,0)**; mutant **ingress: (1,0); direct: (0,0) (the nan quarter makes its hour mean nan and observe_day rejects the day)**. Inputs tried: quarter-resolution day with a nan / inf / -inf quarter, an hourly day with a nan hour, an all-finite quarter day; each fed raw and through prices_from_tibber_payload; apply_price_adjustments on a nan total.

Equivalent-candidate: Defence in depth behind the ingress filters (#2236): 0 of 5 cases move through ingress (nonfinite rows after Tibber and entity ingress: 0 and 0); 3 of 5 move on raw rows (days learned 1 -> 0). Equivalent through production.

Check that would be owed if a distinguishing input is found: none through production: both ingress paths (prices_from_tibber_payload via _raw_value/finite_float, apply_price_adjustments) drop non-finite totals before self._prices, the only list PriceShapeLearner.fold reads; a direct fold of raw rows separates

### `3ceb6a076659004f` custom_components/heatpump_optimizer/price_model.py:510 GUARD_OFF (equivalent-candidate)

Patch `if known_count >= n_steps:` -> `if False:` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/3ceb6a076659004f.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_3ceb6a076659004f.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_3ceb6a076659004f.py`): baseline **prod_differ=0 of 192; direct_differ=0 of 6**; mutant **identical**. Inputs tried: production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than the horizon or the known run (len 0,1,2), known longer than n_steps.

Equivalent-candidate: Equivalent through the coordinator's call shape: none: with known_count >= n_steps the general path computes the same level and its fill loop is empty

Check that would be owed if a distinguishing input is found: none: with known_count >= n_steps the general path computes the same level and its fill loop is empty

### `b434193b049a41c3` custom_components/heatpump_optimizer/price_model.py:510 CMP_BOUND (equivalent-candidate)

Patch `if known_count >= n_steps:` -> `if known_count > n_steps:` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/b434193b049a41c3.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_b434193b049a41c3.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_b434193b049a41c3.py`): baseline **prod_differ=0 of 192; direct_differ=0 of 6**; mutant **identical**. Inputs tried: production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than the horizon or the known run (len 0,1,2), known longer than n_steps.

Equivalent-candidate: Equivalent through the coordinator's call shape: none: at known_count == n_steps the general path's fill loop is empty and returns the same arrays

Check that would be owed if a distinguishing input is found: none: at known_count == n_steps the general path's fill loop is empty and returns the same arrays

### `29db99dee6a5debd` custom_components/heatpump_optimizer/price_model.py:532 CLAMP_DROP (equivalent-candidate)

Patch `for i in range(min(known_count, len(step_start_times)))` -> `for i in range((known_count))` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/29db99dee6a5debd.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_29db99dee6a5debd.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_29db99dee6a5debd.py`): baseline **prod_differ=0 of 192; direct short step_start_times (len 1 < known 3 < n 5) -> prices**; mutant **prod identical; direct -> IndexError**. Inputs tried: production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than the horizon or the known run (len 0,1,2), known longer than n_steps.

Equivalent-candidate: Equivalent through the coordinator's call shape: none through production (coordinator._price_series passes len(step_starts) == n_steps > known_count); a direct extend_price_series call with fewer step_start_times than known prices would

Check that would be owed if a distinguishing input is found: none through production (coordinator._price_series passes len(step_starts) == n_steps > known_count); a direct extend_price_series call with fewer step_start_times than known prices would

### `886591ca08e1d27e` custom_components/heatpump_optimizer/price_model.py:535 CMP_BOUND (equivalent-candidate)

Patch `if shape_mean > 1e-6:` -> `if shape_mean >= 1e-6:` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/886591ca08e1d27e.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_886591ca08e1d27e.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_886591ca08e1d27e.py`): baseline **prod_differ=0 of 192; direct shape mean exactly 1e-6 -> tail 0.0**; mutant **prod identical; direct -> tail 0.45**. Inputs tried: production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than the horizon or the known run (len 0,1,2), known longer than n_steps; plus a model whose shape_for is exactly 1e-6.

Equivalent-candidate: Equivalent through the coordinator's call shape: none through production (shape_for >= SHAPE_MIN 0.2: from_dict and the learner clip shapes to [0.2, 3.0]); only a model reading exactly 1e-6 separates

Check that would be owed if a distinguishing input is found: none through production (shape_for >= SHAPE_MIN 0.2: from_dict and the learner clip shapes to [0.2, 3.0]); only a model reading exactly 1e-6 separates

### `c1e06ebefdc5abad` custom_components/heatpump_optimizer/price_model.py:541 CMP_BOUND (equivalent-candidate)

Patch `if i < len(step_start_times)` -> `if i <= len(step_start_times)` in `extend_price_series`. Full gate: RED-AS-NULL (gate_rc 1, red only as the null), `dev/audit/rounds/round11/D3/s1/wave/D3-g31/gates/c1e06ebefdc5abad.json`.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c1e06ebefdc5abad.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_c1e06ebefdc5abad.py`): baseline **prod_differ=0 of 192; direct short step_start_times (len 2 < n 4) -> last start reused**; mutant **prod identical; direct -> IndexError (2 of 6)**. Inputs tried: production: 192 coordinator-shaped calls (n_steps 0,1,4,96,192; step offset 0,37; known lengths 0,1,n-1,n,n+3,n/2 with negative prices; models None, fresh, young (2 days), trusted from_dict); direct: step_start_times shorter than the horizon or the known run (len 0,1,2), known longer than n_steps.

Equivalent-candidate: Equivalent through the coordinator's call shape: none through production (i < n_steps == len(step_starts)); a direct call with a horizon longer than step_start_times would

Check that would be owed if a distinguishing input is found: none through production (i < n_steps == len(step_starts)); a direct call with a horizon longer than step_start_times would

## Coverage

D3.M3: enumerator `awk -F'\t' '$6=="gate"' SURVIVORS.tsv`, universe 742, examined 16 on this box; the rest are assigned to boxes D3-g01..D3-g47 (listed in REPORT.json). D3.M1, D3.M2, D3.M4, D3.M5 and their C-items are carried verbatim from REPORT-D3-u1b.json.

Findings: none numbered here; candidates are returned under `gate_survivors` for the consolidation step to number.

Unfinished: none
