_Requested by **tvofi**_

`mutation-nightly` baseline failed on main (dispatch run 37050037132, job 110980930989): `tests/harness_headers.py: tools/audit/round4/D7/sysid_estimator_frontier.py exits 0 [rc=-24 ...]`, SIGXCPU. `RLIMIT_CPU` sums every thread's CPU; #1819 set it to 240 s without pinning BLAS threads, and the mutation steps in `tests.yml` pin none. `run_bounded` now pins `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` to `1` for every child (one place, overriding the caller's env); a self-check reads the pins back from a child. `CPU_LIMIT_S` is unchanged and `tests.yml` is untouched. Part of the nightly-mutation red on main.

## Root cause

Cause: #1819 (dd0f2ace3) bounded children by CPU seconds and sized the limit from a local measurement of the frontier harness (\"~100-143 CPU-s\"). `RLIMIT_CPU` bills all threads, so on a runner whose BLAS spawns a pool the same work spends the limit several times faster: the baseline passed in 260 s wall on 10-02 and was killed at 293 s here. Process state: (c), followed and did not produce the intended result. The measurement was made on a box whose BLAS did not inflate CPU time; I measured that locally (Figures), so the figure that sized the limit could not show the inflation. Why #1819's review missed it: its evidence was that one local CPU figure plus controls for the bound itself (idle, spin, wall); none varied thread count, and the review checked those controls rather than the environment the limit runs in. I did not read #1819's review thread; this is read from its commit and diff only. Countermeasure: the pin lives in the bounding function, so a CPU bound cannot be applied without it, and the self-check fails if any of the three is dropped.

## Head

e00f5d2cad0f29246058169a088fa124db471c38

## Mutation proof

Dropping each pin from `BLAS_THREAD_PINS` in turn and running `tests/harness_headers.py`'s `main()` with harness discovery stubbed (the pin check and the three bound controls only; command in Figures): the check `a bounded child runs with every BLAS pool pinned to one thread` fails each time (`['8','1','1']`, `['1','8','1']`, `['1','1','8']`), and passes with all three.

## Null control

Before the fix, the same check at the unmodified `run_bounded` fails: `FAIL a bounded child runs with every BLAS pool pinned to one thread [rc=0 OMP/OPENBLAS/MKL=['8', '8', '8']]` (full `tests/harness_headers.py` run, 1 of 95 failed), the caller's env of 8 reaching the child. The check hands the child 8, so it cannot pass by the ambient env already being 1.

## Figures

- Failing-first and fixed runs: `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/harness_headers.py` printed `1 of 95 HARNESS HEADER CHECKS FAILED` before and `ALL 95 HARNESS HEADER CHECKS PASSED` after.
- Frontier harness CPU, local macOS (Accelerate BLAS, not OpenBLAS), `time` on `tools/audit/round4/D7/sysid_estimator_frontier.py` with `PYTHONPATH=tests/hastub:custom_components:tests`: unpinned 165.06 s user + 2.90 s sys; pinned (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) 173.11 s user + 4.75 s sys. No difference beyond noise, so I could not reproduce the thread inflation here and cannot quote a CI-side saving; the CI numbers are the run's 260 s versus 293 s wall only, and the pin's effect there is unmeasured until the nightly reruns.
- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py`: `ALL 2081 ENTITY CHECKS PASSED`; `tests/structure.py`: `STRUCTURE RATCHET PASSED`, after merging origin/main (code head above).

## Red checks

`nightly-status`: red on main from the `mutation-nightly` baseline above. This diff touches neither `tests.yml`, `governance.yml`, the nightly scripts, the plan nor `HANDOVER.md`, so the exemption applies and the red is the orchestrator's: after this merges, dispatch Tests on main. Cheaper detector for the cause: none exists short of running the harness under the rlimit on an OpenBLAS box, which is the nightly lane itself (CI is the first such box); recorded, nothing built beyond the pin and its check.

## Forward-carry

none

## Friction

none
