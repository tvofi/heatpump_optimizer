# Round 9 · D3 · verifier V1 (reproduce): lc unit (D3-s1-91)

Evidence tree: origin/handoff/audit-r9-evidence at 79aa98ec (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1). Python 3.14.0rc2. Machine: 4 vCPU cloud container (box G1-V1). load1 2.21, thread_factor 1.0.

Tally: 1 verify.

No mutation pre-screen, mutant pool or full gate was run, and the quiet window was not run (tvofi rule). The finding's harness is a light in-memory probe (0.65 s) and is its whole evidentiary basis.

## D3-s1-91 — coordinator.py tzinfo guards dead under the gate's naive clock · VERIFY (medium)
- **Re-run** (`lc_tz_probe_coordinator.py`):
  - HASTUB_TZ unset: guard_on=0.0, guard_off=0.0, now_tzaware=0, so `immersion_margin_8384_differs_hastubtz_unset=0`.
  - HASTUB_TZ=Europe/Stockholm: guard_off raises "can't compare offset-naive and offset-aware datetimes", so `..._stockholm=1`.

  Exact match.
- **Perturbation:** GUARD_ON against GUARD_OFF, recompiled in memory, moves as stated once the clock is aware.
- **Null control:** the unset arm, differs=0.
- **Gate mode:** `grep HASTUB_TZ tests/*.py` finds only `tests/dst_checks.py`, which features.py runs in a subprocess with an aware clock. That file never calls `_immersion_dhw_margin` or `_detect_outage`, so no configured lane exercises the guarded branch.
- **Reach:** the stub's `dt_util.now()` is naive only because `DEFAULT_TIME_ZONE` is None unless HASTUB_TZ is set (`tests/hastub/homeassistant/util/dt.py:24-25`). Real HA's `now()` is always aware, so the guard runs on every real cycle. The gate is blind to a branch production always takes, which supports the test-gap claim.
- **Limit:** the harness emits a RESULT for the `:8384` site (`_immersion_dhw_margin`) only. The `:8112` site (`_detect_outage`) rests on the same gate-mode argument and the grep, not on an executed number here.
- **Metric:** whether the GUARD_ON and GUARD_OFF variants of `_immersion_dhw_margin` agree on one fixed three-naive-event scenario, under HASTUB_TZ unset and under Europe/Stockholm.
