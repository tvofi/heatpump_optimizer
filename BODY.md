R11-CARRY-ROOM-LIFT hotfix: the #3803 features check "the lift may raise the plan's peak over the unlifted plan's ..." compares solver trajectories within 1e-3 K instead of bit for bit. This is a test-only change to `tests/features.py`.

Cause: OpenBLAS picks its kernel from the runner's CPU, and the solver's floats differ between kernels (`CLAUDE.md` rule 3). The check used `np.array_equal(zeros, none)` and a `>= 20.0 - 1e-6` floor on the lifted plan, so it passed only on the kernel it was written on. The `environment` block of `tests / fast (3.14)` names the kernel. Every run that failed used `blas SkylakeX`: #3805 job 135433688207 (AMD EPYC 9V45), #3729 job 135446716075 (Intel Xeon 6975P-C), #3738 job 135447271434 (AMD EPYC 9V45), #3808 job 135442171032, and merge-train batch b7db0ef486a14f5333766222d2321f9b211e2ccb job 135463547554 (AMD EPYC 9V74, `MODE: FULL`, 1 of 5922 FEATURE CHECKS FAILED). Every run that passed used `blas Haswell` (AMD EPYC 7763): main's push run at 99436a082c, job 135403196930, and #3803's own PR run, job 135400717795. #3729 changes no production code and does not touch `tests/features.py`, and it fails on the same merge base 99436a082c with main's 5922 checks, so no PR's change causes this. The failing figures, at 3 decimals, were `peak none=20.241 zeros=20.241 lift=20.453 lift min past 3 h=20.000`. They could not show which clause failed, so the check now prints 6 decimals and the null control's largest difference.

The change: a named tolerance `_RL_PEAK_TOL_K = 1e-3`, with its justification in the comment. The lifted plan's floor past the ramp is checked as `>= 20.0 - _RL_PEAK_TOL_K`. The peak rise must exceed `_RL_PEAK_TOL_K`. The null control is `np.allclose(zeros, none, rtol=0, atol=_RL_PEAK_TOL_K)`. The check's name is unchanged.

## Head

890a05e9cf6b6eb6898d84e4704a0e2da3eaf10d, cut from origin/main 1850e2e0da8c24886e4cc5f4d69601e834fb5023 (merge base), measured 2026-11-19 on macOS arm64.

## Mutation proof

Each of #3803's two pinned mutants of `custom_components/heatpump_optimizer/rooms.py` `lifted` was run against the changed block. The command was `PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1 python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" '# -- The plan peak under the lift'`, with the prelude from `--emit-prelude <prelude> '# -- The plan peak under the lift'`. `rooms.py` was restored after each mutant (`git diff --quiet`: clean).
- Headroom under the target, `]) - margins` -> `]) - margins - 0.1`: 2 of 2 FEATURES BLOCK FAILED. The changed check printed `[peak none=20.241412 zeros=20.241412 lift=20.370671 lift min past 3 h=19.899940 max |zeros-none|=0 K, tolerance 0.001 K]`. The floor misses by 0.1 K, 100 times the tolerance.
- Clip short of the target, `np.minimum(band, ramp)` -> `np.minimum(band * 0.5, ramp)`: 2 of 2 FEATURES BLOCK FAILED. The changed check printed `[peak none=20.241412 zeros=20.241412 lift=20.241412 lift min past 3 h=19.583225 max |zeros-none|=0 K, tolerance 0.001 K]`. Both the peak clause and the floor clause go red.
- Unmutated head: ALL 2 FEATURES BLOCK PASSED.

## Null control

On this machine the all-zero margin array still plans the unlifted plan exactly: `max |zeros-none|=0 K`, printed above under both mutants. The tolerance therefore relaxes nothing here, and it does not blind the check to either mutant. The SkylakeX figures were not measured locally, because no seat here has that kernel. This PR's own `tests / fast (3.14)` run prints them at 6 decimals whichever kernel it lands on.

## Figures

- Mutation proof block runs: the command and results above.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at the head.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` names `tests/entities.py` and `tests/features.py`. Locally only the changed `tests/features.py` block was run (hotfix scoping, host load about 50). The full `tests/features.py` and `tests/entities.py` are left to CI.

<!-- figure-block: scope-line mb=1850e2e0da8c24886e4cc5f4d69601e834fb5023 head=890a05e9cf6b6eb6898d84e4704a0e2da3eaf10d -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
