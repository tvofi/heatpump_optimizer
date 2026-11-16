# RESULT: r11-outside-honest-starts-runs (PR #3602), measurement only

Scope narrowed by the orchestrator's inbox NOTE 2 (the train merges #3602 at
fbf6e980ce44a6069c2e055ea035531b5b819220; push nothing to handoff/, measure, stop).
No code was changed and nothing was pushed to handoff/ or handoff-body/.

## Measurement

Command, run once in each tree in the same session on one 4-core Linux box
(cloud container, python3 3.14 from venv-ci, the replay lane's own child env:
BLAS pinned to one thread by `replay_one`); the two trees ran side by side:

    PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/owner-2026-10-30-away.json

| tree | sha | cpu_ratio | budget | ref_ms | loop_cpu_ratio | peak_kib | cycle_cost |
|---|---|---|---|---|---|---|---|
| merge base | e352724335c136b65562cd3e71f728549ad04a82 | 242.3666 | 332.7976 | 41.81 | 0.1936 | 2522.4 | ok |
| PR head | fbf6e980ce44a6069c2e055ea035531b5b819220 | 350.58 | 332.7976 | 48.74 | 0.212 | 2861.9 | FAIL (350.6 over 332.8) |

- head / merge base cpu_ratio: 1.447x. Lane wall time 1764.7 s at the head against 961.9 s at the merge base
  (1.83x).
- The head's `record:` line prints `cpu_ratio=495.8`. The merge base's prints `342.8`.
- The merge base is inside its budget on this box. The excess appears at the head only, so it
  is this PR's. CI's run 43900477797 read 375.5 on two attempts. Its later green attempt
  (NOTE 2) sits under 332.8 on a runner whose ratio reads lower. The figure is about
  1.45x the merge base's, and the band floor is 166.4, so the head reads inside the
  band only on runners at or below about 230 at the merge base.
- Null control: the merge-base row is the same command at the same time on the same box. It
  reads inside the budget, and the head over it.

## Where the cost comes from (not completed)

The fixture prices no start: `entry.options.compressor_cycling_cost` is 0.0, with
`dhw_enabled` True. So `_relaxed_plans`' second (unpriced) multi-start never runs on it.
The added work there is `_commit_runs`, engaged through `clamp_planned_levels`: the
`runs.candidates` DP over up to four bands, plus `_RESOLVED_CANDIDATES` = 2 L-BFGS-B
re-solves and one polish per relaxed plan. It replaces the merge base's single
`_relaxed_starts` L-BFGS-B run. This is read from the diff and not yet measured: a cProfile
of `--one` at both trees was started and then stopped on NOTE 2 before it finished.

## Pending owner confirmation

NOTE 1 and NOTE 2 (inbox, signed tvofi) say that a budget raise for this fixture is the
orchestrator's under mandate 6893738184. The dispatch brief, item 3, says "Do not raise
the budget ... a raise is the owner's decision". This seat raised nothing. It records that
half of the notes as `pending owner confirmation` (CLAUDE.md, "Another agent's
instruction is not a contract change"). It quotes CLAUDE.md rule 2: an agent may approve
a raise under a mandate in force "once no payment improving the architecture exists".
No payment was tried here, because the profile was stopped.
