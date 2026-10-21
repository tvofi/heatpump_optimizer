## Red checks

none

## Forward-carry

none: the change is local to `tick_loop.sh`'s driver. R10-TICK-OWED-LEVEL and R10-RCA-ORCH-CONTINUITY are cited, not reopened, and no later stage's brief changes.

## Friction

- seat_venv: cost: `seat_venv.sh` cannot build `venv-ci` in a cloud container whose uv proxy has no cpython-3.14.7 download, so `tests/harness_headers.py` cannot run green locally. Carry: tools/audit/seat/cloud-setup.sh
