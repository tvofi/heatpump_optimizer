# D10 — verifier V2 (independent), round 9

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; tree handoff/audit-r9-evidence at 6f51db2c. Machine: G2-V2 cloud container, 4 cores shared by 3 seats, CPython 3.14.0rc2 at /home/claude/venv (the finders used /home/claude/venv314). All metrics are counts, so they are immune to contention; load1 is quoted per run. Every perturbation is in memory; no production file was edited on disk.

| id | finder re-run (baseline / perturbed) | my number | vote |
|---|---|---|---|
| D10-s1-01 | dup_accepted 3, stale_refused 3 / 0, 0 (load1 2.70, tf 1.000) | stale_pairs 31/31; controls 0; restamp 0 | verify, medium |
| D10-s1-02 | silent_presses 2 / 0 (load1 2.73, tf 1.000) | silent_presses 3/3; 2 still available; raise 1 | verify, medium |
| D10-s1-03 | auth_as_transient 3, transient_ok 2 / 0, 2 (load1 2.73, tf 0.999) | auth_indistinct 2/2; raise sites 0; rewraps 1; authraise 0 | verify, low |
| D10-s2-01 | untranslated 2 (en, sv, strings), uniconed 2 / translate 0, eco 1 (load1 2.73, tf 1.000) | untranslatable 2 in 4 files; eco 1 | weaken, medium to low |

## D10-s1-01 — unique id not re-derived after reauth or options edit

- Finder harness `s1/unique_id_drift.py`: arms reauth, options_token and options_indoor accept a duplicate. `--fix` gives 0/0. control_none and reconfigure give 0.
- Mine: `verify-v2/uid_invariant.py [--perturb restamp]`.
  - Metric: over every (write seam, identity key) pair, count pairs after which `entry.unique_id != entry_identity({**data, **options})`.
  - The seams are `async_step_reauth_confirm` plus each identity field enumerated at run time from `_OPTION_FIELDS`: 15 fields on entities, entities_metering and entities_pump. Each field is saved in menu mode and in close mode; close mode applies the result as options, as the real OptionsFlowManager does.
  - Result: 31/31 stale, unapplied 0. Controls: non-identity price_vat in both modes, and reconfigure with a new token, give 0 stale. Restamp perturbation: 0. load1 3.11, tf 1.000.
- My metric checks the invariant; the finder's is the duplicate-abort behaviour. The two are consistent: the finder's `uid_follows=False` column is my invariant on 3 of the 31 pairs. My enumeration widens the seam set the fix is held to, from 3 arms to all 15 option identity fields in both save modes. The derived schema of quick_setup is not in my enumeration.
- Attacks:
  - Real-HA reach: upstream `async_update_entry(data=…/options=…)` leaves unique_id alone. Reachable.
  - Null control: holds.
  - Severity: a second add-integration by the user creates a second entry driving one pump. A defect with a workaround: medium.
- Vote: **verify, medium**.

## D10-s1-02 — Optimize-now press silent when the solve did not run

- Finder harness `s1/press_vs_service.py`: silent in the stale_prices and feed_down arms, 0 in the prices_ok control. `--fix` gives 0.
- Mine: `verify-v2/press_reason.py [--perturb raise]`.
  - The outcome is injected by `mock.patch.object` on `async_run_optimization` (None, no_prices or solve_failed) or on `_fetch_tibber_prices` (UpdateFailed). The weather, solar and price-shape steps are no-ops.
  - Result: press returns normally in 3/3 not-run arms. In the no_prices and solve_failed arms `last_update_success` stays True, so nothing else surfaces the not-run press either.
  - Perturbation: raising in `async_force_optimization` on a reason gives 1; the remaining arm is fetch_failed, which carries no reason code.
  - Control arm: 0. load1 3.74, tf 1.000.
- In my fetch_failed arm the service twin is not comparable: the service calls `async_run_optimization` directly, and I patched that to return None. That arm is counted on the press alone.
- Attacks:
  - Real-HA reach: upstream refresh also swallows UpdateFailed, and `async_request_refresh` is debounced (an extra silent path upstream).
  - Severity: two arms give no signal anywhere. Medium holds.
- Also observed, not scored: in comfort, boost and off modes `_async_update_data` never calls `async_run_optimization`. A press there runs no solve, while the service always calls it.
- Vote: **verify, medium**.

## D10-s1-03 — Tibber auth refusal delivered as ConfigEntryNotReady/UpdateFailed

- Finder harness `s1/auth_failed.py`:
  - Baseline: 3/3 auth arms transient; 500 and connection-error controls correctly transient (2).
  - `--fix`: 0; controls stay 2.
  - `stub_has_ConfigEntryAuthFailed=False`.
- Mine: `verify-v2/auth_class.py [--perturb authraise]`, driven through the full `_async_update_data` wrapper, which the finder did not use.
  - 401 and 403 both escape as UpdateFailed, the same type as the HTTP-500 control: auth_indistinct 2/2.
  - An AST census finds 0 raise sites of ConfigEntryAuthFailed.
  - Probe: an auth-class exception raised inside the fetch escapes the wrapper as UpdateFailed (rewraps 1). This confirms the claim that the fix needs the wrapper change.
  - Perturbation (fetch raises auth-class, wrapper passes it through): 0.
  - load1 3.61, tf 1.000.
- The continued-polling consequence is not measured: `tibber_posts_after_verdict=3` over cycles 2..4 is the same in both modes. The stub has no auth arm (grep AuthFailed in `tests/hastub/homeassistant/helpers/update_coordinator.py` = 0), so upstream's stop-scheduling cannot be separated in-process. This is the P11 half of the claim, confirmed by that grep.
- Severity: reauth is still offered (the finder's reauth_flows_started=1). The cost is continued polling and SETUP_RETRY instead of SETUP_ERROR. Low holds.
- Vote: **verify, low**.

## D10-s2-01 — climate presets auto/economy untranslated and uniconed

- Finder harness `s2/climate_presets.py`: 2 in each of strings, en and sv; uniconed 2. `--perturb translate` gives 0; `--perturb eco` gives 1.
- Mine: `verify-v2/preset_lookup.py [--perturb economy_eco]`.
  - Values are the ones the production `preset_mode` actually publishes as `coordinator.mode` is driven through every MODE_*; off publishes None.
  - The lookup is looser than the finder's: any `entity.climate.*` translation key counts.
  - Result: 2 (auto, economy) in strings.json, en.json, sv.json and icons.json.
  - The same two words are already translated under `entity.sensor.optimization_mode.state`: the words exist in the integration but are not wired to the climate entity.
  - economy→eco perturbation: 1. load1 3.50, tf 1.000.
- The standard preset list is hard-coded from core `climate/const.py`, because there is no HA core in the venv.
- Attack, severity: the consequence is the raw English tokens in the preset selector and default icons. There is no wrong value and no control effect, which is hygiene under COMMON.md item 7. Renaming economy to eco would also change a value that automations already use, so the fix should translate rather than rename.
- Vote: **weaken, low**.
