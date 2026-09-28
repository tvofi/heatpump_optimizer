# Evidence for ALT-ENDGAME-PLAN.md

Every file here was produced at origin/main `31394964` (Merge PR #1734). Python scripts run from the
repository root with `PYTHONPATH=tests/hastub:custom_components` and the CI pins
(`tests/requirements-ci.txt`); the two `.sh` controls edit and restore source files, so run them only in a
throwaway detached worktree. Each lead names its measured arm and its null control; a lead whose check
failed is recorded as refuted in the plan and was not filed.

| lead | script | output | arm vs control |
|---|---|---|---|
| M1 hub writes per solve | `m1_hub_writes.py` | `m1_hub_writes.out` | 23 hub fields written on the solve path vs 6 restored by its `finally`; the five in-code notes of prior fixes |
| M2 untyped payload | `m2_payload.py` | `m2_payload.out` | surfaces' top-level reads vs the golden producer set (`tests/golden/coord_*.json`) |
| M3 reach-through | `m3_reach.py`, `m3_ratchet_control.sh` | `m3_reach.out`, `m3_ratchet_control.out` | six private reads in `pump_arbiter.py` move no metric; the same six in a coordinator method move `cut_dhw` +5 |
| M4 store version | `m4_store_version.py`, `ha_storage_dev.py.txt` | `m4_store_version.out` | stub returns data across v1 -> v2; Home Assistant re-raises `NotImplementedError` (no package override) |
| M5 per-module duplication | `m5_dup_control.sh` | `m5_dup_control.out` | a 32-line copy in another module: `duplication_blocks` 14; in the same module: 16 |
| M6a step-start twins | `m6a_step_starts.py` | `m6a_step_starts.out` | 18/18 reachable grids agree (the rounding divergence is unreachable: `dt_hours` is `time_step_minutes / 60`) |
| M7 `classes_over_300` | — | `m7_classes_over_300.out` | definition plus the #750 precedent: every row fell but this one |
