# Fix-review evidence — PR #2114, head f19851987a55fb6ac53d1b40935f2c13838f49ab

Reviewer: r9rev-2114. Branch `fix/r9-blas-kernel-red`. Measured head
`f19851987a55fb6ac53d1b40935f2c13838f49ab`; merge base `7cd5a588c`.

Worktrees: head `/Users/timmalmstrom/hpo-seats/r9rev-2114/wt` (detached at the
head); baseline `/Users/timmalmstrom/hpo-seats/r9rev-2114/base` (detached at
`7cd5a588c`). Interpreter `~/.local/state/hpo/venv-ci/bin/python3` (3.14.7,
numpy 2.4.6 / Apple Accelerate), the tree's own seat venv.

## RESULT lines (my own runs)

    RESULT block_head_two_zone=1 j_plain=110.436632 j_continuation_off=111.267093 continuation_gain=+0.830461 j_seeded_half_price=110.129674  -> ok ; ALL 14 FEATURES BLOCK PASSED ; rc=0
    RESULT block_head_single_zone_null: j_plain=67.730056 j_continuation_off=67.730056 continuation_gain=+0.000000  -> ok (exact: schedules array-equal)
    RESULT block_base_two_zone=1 : FAIL R9-F2.1 P3 [shipped 110.4366, seeded 110.1297] ; 1 of 14 FEATURES BLOCK FAILED ; rc=1
    RESULT mutation_two_zone=1 j_plain=111.267093 j_continuation_off=111.267093 continuation_gain=+0.000000 : FAIL ; 1 of 14 FAILED ; rc=1
    RESULT finder_harness_patched_two_zone_margin=-0.2070 (j_plain=110.4366, j_seeded=110.1297)
    RESULT finder_harness_patched_single_zone_margin=+0.0995
    RESULT old_arm_under_the_same_mutation = 110.129674 + 0.1 - 111.267093 = -1.037
    RESULT fixer_harness_two_zone: j_plain=110.436632 continuation_gain=+0.830461 threads_pinned identical=1 (14 solves, 110.8s wall)
    RESULT fixer_harness_ladder_gain: 0.25=+0.840025 0.50=+0.830461 0.75=+0.000000 1.00=+0.000000  (cliff, not slope)
    RESULT closures_repair: +1 line to inert_reads['tests/harness_headers.py'] (sorted, 541); ci_predict --base 7cd5a588c at head = no predicted red
    RESULT merge_tree_exit=0 ; VERSION/manifest/RELEASE_NOTES untouched ; head ref still f19851987
    RESULT head_red_checks=none (be7dc8be1's 9 are `cancelled`, superseded by the head push)
    RESULT carry_destination: dev/governance/dimensions/D0.md byte-identical to origin/main; no carry-*.json added; the finding is absent from the tree

## Logs (this directory)

- `features_block_head.log`    — head P3 block, `ALL 14 ... PASSED`, rc=0
- `features_block_mutant.log`  — continuation deleted, `1 of 14 ... FAILED`, rc=1
- `features_block_base.log`    — merge base, old check FAILS on Accelerate, rc=1
- `k1725_finder_head.log`      — finder's harness VERBATIM at head: crashes (`TypeError` simulate_trajectory, stale API at head and at main)
- `k1725_finder_patched_head.log` — finder's harness, ONE stale call patched (disclosed): margin -0.2070 / +0.0995
- `fixer_harness_head.log`     — fixer's harness at head; reproduces the body's Figures table
- `optimizer_head_backup.py`   — pre-mutation copy of optimizer.py

## Arms I could NOT reproduce

1. **The cross-kernel axis.** This box is Apple M1 / Accelerate; `OPENBLAS_CORETYPE`
   selects nothing (the harness's own env line: `core=(unset) -- no OpenBLAS
   Core: line`). The Linux rows (+0.1000/+0.0905/+0.0904) are cited from the
   tree, never re-taken — the container lane was retired and `gate-scoping.md`
   forbids re-deriving off Linux. So the claim "the new key does not move across
   BLAS builds" is verified only as: on Accelerate the new arm reads +0.830461,
   and the ladder shows the gain is a CLIFF (0.75/1.00 -> exactly +0.000000),
   so a kernel change toggles 0/0.83 and cannot land on a thin margin. The
   actual Linux values of the NEW arm are unverified here (Haswell prints them
   only in CI's own log).
2. **The finder's harness verbatim.** `dev/audit/harnesses/k1725_blas_kernel_gap.py`
   does not run at this head: `score()` calls `m.simulate_trajectory(st, pw, ot,
   wi, ra, so, DT)`, but the live signature is `simulate_trajectory(initial_state,
   power_schedule, weather, *, dt_hours=)`. This is pre-existing — the file is
   byte-identical to the merge base and is untouched by the diff. I patched that
   ONE line (marked `# REVIEWER PATCH: stale API` in a restored-then-reverted
   working copy) to run its P3 arm; the margin it prints, -0.2070, matches
   #1726's null control and is independently reproduced by the check's own
   printed `j_seeded_half_price`/`j_plain`.

## The block

`carry-missing: not carried to D0`. The body's `## Forward-carry` names
`dev/governance/dimensions/D0.md`, and the in-tree comment in `tests/features.py`
states the optimality question "is carried to D0's brief" — but D0.md is
byte-identical to `origin/main`, no `dev/programme/carries/carry-*.json` was
added, and the finding (`110.129674`, "0.307 left on the table") appears nowhere
in the tree outside the two authored files.
