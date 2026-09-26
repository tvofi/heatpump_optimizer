# Round 9, D10 — verifier V1 (reproduce)

Tree: /home/claude/wt/D10, evidence commit 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus tools/audit/round9/).
Python 3.14 venv. PYTHONPATH=tests/hastub. 4-core shared container.
All metrics are counts, so they are immune to contention. load1 was 0.35–4.76 over the session and thread_factor was 1.000 on every run.
No production file is left modified: the one on-disk edit (config_flow.py) was reverted with `git checkout --`.

## D10-s1-01 — unique id not re-derived after reauth or an options edit (vote: verify, medium)
- Metric: arms in which a fresh config flow that submits the entry's current effective identity answers is not aborted as `already_configured`.
- Re-run of `s1/unique_id_drift.py`: dup_accepted=3, stale_refused=3, over 5 arms. The finder's numbers are 3 and 3, so exact.
- Perturbation `--fix`: 3→0 and 3→0.
- Production-seam perturbation: a one-line on-disk edit to `async_step_reauth_confirm` adds `unique_id=entry_identity({**data, **options, token})`. dup 3→2 and stale 3→2, and only the reauth arm flips. Reverted afterwards.
- Null control: control_none and reconfigure are 0 in every run.
- Leave-one-out: each arm is binary, and dropping any positive arm gives 2.
- A seam the finder did not drive: the options `after_save=close` path (`_save` → `async_create_entry`). `verify-v1/uid_close_path.py` gives dup_accepted_close_path=2/2 with control_close=0, and `--fix` (re-stamp) gives 0.
  - The finder's `--fix` wraps `async_update_entry`, so it would not cover this path.
  - The finding's seam_rule grep does list `async_create_entry`.
  - The stub's OptionsFlow does not apply create_entry data, so the harness applies it the way real HA's OptionsFlowManager does.
- Real-HA reach: the stub's duplicate guard compares `entry.unique_id`, as upstream does.
- Severity: medium rests on dup_accepted, which means two entries actuate one pump. stale_refused has near-zero consequence, because the refused answers belong to a revoked or superseded configuration.

## D10-s1-02 — Optimize-now press returns normally when the solve did not run (vote: verify, medium)
- Metric: arms in which `handle_run_optimization` raises HomeAssistantError while `ForceOptimizationButton.async_press` on the same state returns normally.
- Re-run of `s1/press_vs_service.py`: silent_presses=2/3. The finder's number is 2, so exact.
- Perturbation `--fix`: 2→0. prices_ok is 0 in every run.
- Own measurement, `verify-v1/press_signal.py`: press_returned_ok=2 and fully_silent=1.
  - In stale_prices the solve reason is `no_prices`, 0 repair issues are created, and last_update_success stays True.
  - In feed_down, last_update_success=False, so entities go unavailable, which is a visible signal.
  - Perturbation `--fresh` (current prices in the stale arm): 2→1 and 1→0.
- Leave-one-out: dropping stale_prices gives 1, and dropping feed_down gives 1.
- Not measured: real HA debounces `async_request_refresh` (cooldown), so a second press inside the cooldown is a further silent path. The stub does not model it.

## D10-s1-03 — Tibber auth refusal delivered as ConfigEntryNotReady/UpdateFailed (vote: verify, low)
- Metric: auth-refusal arms (HTTP 401/403) in which the exception escaping `async_setup_entry` or `_fetch_tibber_prices` is not ConfigEntryAuthFailed.
- Re-run of `s1/auth_failed.py`: auth_as_transient=3/3 and transient_ok=2/2. The finder's numbers are 3 and 2, so exact.
- Perturbation `--fix`: 3→0, and transient_ok stays 2.
- `grep ConfigEntryAuthFailed` over custom_components/ and tests/hastub: 0 hits.
- Own measurement, `verify-v1/auth_polls.py`, 6 steady cycles:

| status | revoked_posts | reauth_started | auth_class |
|---|---|---|---|
| 401 | 5 | 1 | 0 |
| 403 | 5 | 1 | 0 |
| 500 | 0 | 0 | 0 |
| 200 | 0 | 0 | 0 |

  - The 500 and 200 rows are the perturbation and the null control.
- Leave-one-out: dropping any auth arm gives 2.
- Consequence: the reauth flow still starts once. The cost is continued polling with a revoked token, where upstream's auth arm stops scheduling, and setup retries instead of a reauth-required state. Low is earned.

## D10-s2-01 — climate presets auto and economy untranslated and uniconed (vote: weaken, low)
- Metric: the climate entity's preset_modes that are neither HA-standard presets nor in `entity.climate.<translation_key>.state_attributes.preset_mode.state`.
- Re-run of `s2/climate_presets.py`: strings, en and sv are 2 each, and uniconed is 2. The finder's numbers are 2, so exact.
- `--perturb translate` gives 0, and `--perturb eco` gives 1.
- Own measurement, `verify-v1/preset_tables.py`, a key-agnostic scan: 0 preset_mode leaf keys under any key in strings.json, icons.json, translations/en.json or translations/sv.json, and uncovered=2 in each file.
  - Perturbation `--perturb en_only`: en 2→0 while the other three files stay 2.
- Null control: the standard presets comfort and boost count 0.
- Leave-one-out over the 4 files: range 2–2.
- Why weaken: the consequence is display-only.
  - The published token is correct.
  - The effect is an untranslated label and a default icon for 2 of 4 presets.
  - No money, comfort or published-value consequence.
  - `strings.json` does translate `sensor.optimization_mode` state `economy`.
  - `quality_scale.yaml` marks entity-translations and icon-translations as done, which is a claim-accuracy matter.

## Harnesses written (under tools/audit/round9/D10/verify-v1/)
- `uid_close_path.py`
- `press_signal.py`
- `auth_polls.py`
- `preset_tables.py`

## Not done
- The real-HA debounce path for D10-s1-02 is not measured; the stub has no Debouncer cooldown.
- No gate run was needed: none of the findings touches a golden fixture or stress.
