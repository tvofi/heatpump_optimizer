Fix review: merge 000c5c7d2efb8720476ee8bd7c19a808ea983217

bus-nonce: 0728b229e9b2fda03dc3fc3d1c3890f3

Round 1. Measured at 000c5c7d2efb8720476ee8bd7c19a808ea983217, which was the live head when this was posted. Brief contract diff is empty.

## RESULT lines

- RESULT pins: `BLAS_THREAD_PINS` is applied once, in `run_bounded` as `{**env, **BLAS_THREAD_PINS}`, so the pins win over the caller's env. The only other child, `dirty_registers`, runs git. Every harness goes through `run_harness` to `run_bounded`.
- RESULT self-check, my own probe (`ev/probe.py`, same expression as the PR's check, callers handed 8): head passes `['1','1','1']`. Deleting the merge line leaves `['8','8','8']`, which is the before-fix state, and it fails. Dropping OMP, OPENBLAS or MKL alone fails with `['8','1','1']`, `['1','8','1']`, `['1','1','8']`. Swapping the merge order fails. Killed 5 of 5, and the check cannot pass on ambient env since it hands 8.
- RESULT full `tests/harness_headers.py` at head under the R9-F11.4 venv: `ALL 95 HARNESS HEADER CHECKS PASSED`.
- RESULT thread-count dependence: the gate step that holds these headers green (`tests.yml` Run the suite, and the other run.sh steps) already exports all three pins as 1. The headers were therefore recorded and verified single-threaded, so the pin moves the nightly lane onto the gate's own environment and cannot change a printed RESULT. The frontier harness prints integer counts over seeded draws and spawns no threads. I did not prove independence from thread count across all 95; I rely on the gate's pinned environment.
- RESULT CI: `waitci.sh` DONE total=35, only `nightly-status` red. That is main's: this diff touches only `tests/harness_headers.py` and a delivery row, not the reporter, its job, the plan or HANDOVER. The body answers it.
- RESULT `git merge-tree --write-tree origin/main <head>`: rc=0. The body names this head. VERSION, manifest, notes and goldens are untouched.

## The CPU-time claim

The body is honest that it did not reproduce the inflation: unpinned 165.06 s user, pinned 173.11 s on Accelerate, "no difference beyond noise", and it quotes no CI saving. Two cautions for the record, neither blocking:
1. The Root cause section states the inflation as the cause ("several times faster"). The run's own numbers do not show it. A kill at 240 CPU-s after 293 s wall is CPU/wall of about 0.82, below one core. The mechanism that fits is OpenBLAS spin-waiting under `--jobs 3` oversubscription, which burns CPU without raising CPU over wall. That is plausible and unmeasured.
2. Pinned single-thread work is about 170 CPU-s on this Mac, against a 240 s limit. A slower runner could still exceed it. Whether the pin is sufficient is settled only by the next nightly dispatch. Do not close the nightly red on merge; dispatch Tests on main and read the lane's frontier line.

No forward-carry is owed.
