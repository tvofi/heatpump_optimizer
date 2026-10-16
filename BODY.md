# Summary

R9 D9-s2-02's nightly `loop_cpu_ratio` divided the coordinator cycle's
loop-thread CPU — an interpreter-bound measure — by `tests/stress.py`'s
`reference_solve`, a BLAS-bound solve. The two move with the runner class at
different rates, so the figure tracked the runner, not the code: over the
nightly series `corr(loop_cpu_ratio, ref_ms) = -0.943` and it read
0.2441-0.4050 (1.659x), the fast runners high and the slow ones low.

This group adds a fixed pure-Python reference workload (`reference_loop`) and
normalises the loop figure by it, on the same clock the loop is measured on
(`time.thread_time`), so the ratio is the loop's work over the reference's and
does not move with the runner. The budget is re-centred 0.426 -> 0.111 (a
lowering, not a raise). Part of #2270.

The class narrowing is a CONSTRUCTION claim, and the body says so: one box
cannot vary the runner class, so what is measured here is that the new figure
does not follow `ref_ms` where the old one did (`## Null control`). The
`--series` half of the harness re-derives the class factor the old ruler
imposed; the new figure it prints nightly is what the next timed week compares
across runners. No raise is owed either way (the budget moved down).

## Head

`9d20cc2d6b18ebf7fe20115292a28f18b81d7fae` (branch `fix/r10-replay-loopnorm`),
measured at main `81ae048e8bbdf2335fe2016e987ec2739481f293`.

## Mutation proof

The fix's predicate is the loop figure's denominator in `cost_figures`
(`tests/replay.py`): the added lines read

    lref = sorted(loop_ref)[len(loop_ref) // 2] if loop_ref else 0.0
    out["loop_cpu_ratio"] = (round(sum(loop_cpu) / len(loop_cpu) / lref, 4)
                             if loop_cpu and lref > 0 else float("nan"))

Reverting them to the solve reference
(`... / ref ...`, the line the fix replaced) and running `tests/replay.py`
reds two checks:

    FAIL control:cycle_cost:loop_normaliser  [ratio 0.22: solve x3 moved=True, loop_ref x2 moved=False]
    FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.3032 over its budget 0.111]
    2 of 93 replay checks FAILED

The first is the control the fix adds (the figure must not follow the solve
reference); the second is the clean run reading on the solve's scale again, far
above the new cap. The closure is `tests/entities.py`, which imports `replay`
and runs `replay.controls()` (its "The replay lane" block): the same
`control:cycle_cost:loop_normaliser` reds there.

Restored; the head's lane prints `ALL 92 replay checks PASSED`.

## Null control

The claim is that the new figure does not move with the BLAS reference and the
old one did. Both are measured on this box by
`dev/audit/harnesses/r10_replay_loopnorm.py`, which prints, per run, the loop
CPU, both references and the old and new figures. Across the sixteen runs in
`## Figures`, `corr(old, ref_ms) = -0.579` and `corr(new, ref_ms) = +0.120`:
the same `ref_ms` variation that the old figure followed, the new one does not.
Where the box classed two runs apart — `ref_ms` 44.3 vs 57.1 (1.29x) with the
loop CPU flat (15.45 vs 15.37 ms) — the old figure moved 1.296x
(0.3485 -> 0.2690) and the new one 1.047x (0.0841 -> 0.0803). The null of the
fix is the mutated tree above, whose figure *is* the old figure.

## Figures

One line per stated figure, with the command that printed it.

- Old figure over the nightly series, 18 timed slow lanes (2026-10-01..10-16):
  `corr(loop_cpu_ratio, ref_ms) = -0.943`, spread 0.2441-0.4050 (1.659x) —
  `python3 dev/audit/harnesses/r10_replay_loopnorm.py --series`.
- The series split into two classes by `ref_ms`, slow (ref>45, n=11)
  `ref_mean=53.13`, `loop_cpu_mean=13.69`, `old=0.2441..0.2742`; fast
  (ref<=45, n=7) `ref_mean=30.70`, `loop_cpu_mean=10.39`, `old=0.3094..0.4050`;
  class factors `blas=1.731x interpreter=1.317x old_figure_shift=0.761x` — same
  command.
- New figure on this box: 0.0618-0.0903 (1.461x), median 0.0786; old on the
  same runs 0.2690-0.3502 (1.302x), median 0.3153 —
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_loopnorm.py 16`
  over the sixteen runs above (twelve from a batch and four the harness printed).
- The lane's own clean run and band: loop_cpu_ratio 0.0849, `record:` line
  `loop_cpu_ratio=0.1201` against the cap 0.111 —
  `PYTHONPATH=tests/hastub python3 tests/replay.py`; `ALL 92 replay checks
  PASSED`.
- The budget: sqrt(2) x the median 0.0786 = 0.111, inside the previous 0.426
  (a lowering) — the arithmetic of the two lines above.

## Red checks

`harness_headers` went red on this branch mid-development and is answered in
the branch, not deferred. Its inlined-walk census compares every `repo_root`
copy to `tools/audit/repo_root.py`; the new harness's copy was missing the
canonical docstring and its local `from pathlib import Path`, and the census
named it (`python copies=105 differ=[...r10_replay_loopnorm.py]`). Corrected to
the canonical text; at the head the census passes (verified against
`harness_headers._fn_text`). The head's checks are otherwise green:

- `tests/entities.py` — ALL 2331 ENTITY CHECKS PASSED (runs `replay.controls()`)
- `tests/features.py` — ALL 4138 FEATURE CHECKS PASSED
- `tests/structure.py` — STRUCTURE RATCHET PASSED
- `tests/harness_headers.py`, `tests/layout.py`, `tests/closure.py selftest`,
  `tests/env_drift.py --claims-only origin/main` — pass

No other check turned red.

## Forward-carry

none — no later stage's brief depends on the loop figure's ruler: `R10-DIAG-REPLAY`, this group's `after`, consumes `run_fixture`, whose signature is unchanged, and `cost_figures` gained an optional `loop_ref` with its one caller in the tree.

## Friction

none
