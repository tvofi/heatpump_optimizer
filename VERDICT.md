Fix review: merge c4080d7bde673c71c59acfd6f18f699e7ff539ab

bus-nonce: cdf09988245590d51f5337ab21019eb4

# Fix review — #2339 R10-REPLAY-LOOPNORM

Head measured and re-read: `c4080d7bde673c71c59acfd6f18f699e7ff539ab` (frozen
by the fixer's handoff; unchanged at posting — the body's `## Head` names the
same). Merge base `81ae048e8`. Contract copy current (roles dir diff vs
`origin/main` empty). Measured from detached worktrees at both ends
(`/private/tmp/fxrv-loopnorm-head`, `/private/tmp/fxrv-loopnorm-base`), with the
seat venv (CPython 3.14.7, numpy 2.4.6, scipy 1.17.1). The reviewer built its
own two instruments from the finder's recipe (R10-RCA-2205.md "Reproduce");
neither is the fixer's `dev/audit/harnesses/r10_replay_loopnorm.py`.

## Step 1 — mutation proof (re-run): reproduced

Reverted the two added lines to the pre-fix denominator (`/ lref` -> `/ ref`),
ran `tests/replay.py`, restored.

    FAIL control:cycle_cost:loop_normaliser  [ratio 0.22: solve x3 moved=True, loop_ref x2 moved=False]
    FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.3187 over its budget 0.111]
    2 of 93 replay checks FAILED

Body quoted `0.3032` for the second (its run); mine reads `0.3187` and `0.3512`
across two runs (load noise, same shape — the clean run back on the solve's
scale, far over 0.111). The first line is exact. Restored: `ALL 93 replay checks
PASSED`. The named closure
holds: `tests/entities.py` imports `replay` and runs `_replay.controls()` in its
"replay lane" section (`tests/entities.py:34714`), so the same control reds
there. Mutation is non-vacuous.

## Step 2 — both ends, FINDER's harness

The finder is the owner answer 4 / R10-RCA-2205; its recipe is a gh series read
plus interleaved `tests/replay.py --one`. My instrument `both_ends.py`, 6
interleaved rounds base-then-head:

    RESULT base_old min0.2832 max0.3112 factor1.099 median0.2979 corr_ref=-0.480
    RESULT head_new min0.0619 max0.0707 factor1.142 median0.0645 corr_ref=+0.112

The body's local pair is 0.2690-0.3502 (1.302x) old / 0.0618-0.0903 (1.461x)
new on ITS box; the two boxes differ in absolute level (my interpreter is
faster: `loop_ref_ms` 104-128 here against the body's 154-195), but the shipped
property replicates: the OLD figure tracks `ref_ms` (negatively), the NEW one
does not, and the new figure's local noise is not lower than the old's
(mine 1.142x vs 1.099x; the body's 1.461x vs 1.302x). I confirm the body's
`corr(new, ref_ms)=+0.120` independently at `+0.112`. The class factor is
removed by construction (new = loop_cpu / a pure-Python reference on the same
`time.thread_time` clock, so the interpreter-speed factor cancels); that
construction is sound: the numerator `loop_cpu` (replay.py:1105) and
`reference_loop` (replay.py:405) are both `time.thread_time` on the main thread,
and both scale with interpreter speed.

## Step 3 — null control: reproduced

The null is the mutated tree above, whose figure IS the old figure. It reds
`control:cycle_cost:loop_normaliser` (solve x3 moves it; loop_ref x2 does not).
The head's companion control `control:cycle_cost:cpu_normaliser` (new) asserts
the sibling `cpu_ratio` DOES move with the solve — green at the head, so the
class is enumerated, not silently widened. `control:cycle_cost:loop_thread`
(doubled loop) still fires green; the doubled-loop arm reads `loop_cpu_ratio`
0.1572 against the 0.111 cap on my clean run.

## Step 8 — figures re-derived

Series (my `series.py`, same recipe): 20 rows, spread 0.2441-0.4050 (1.659x),
`corr_ref_ms=-0.945`; slow n=13 ref_mean 53.12 loop_cpu_mean 13.62 old
0.2441..0.2742; fast n=7 ref_mean 30.70 loop_cpu_mean 10.39 old
0.3094..0.4050 — class factors blas 1.730x, interpreter 1.311x, old_figure_shift
0.758x. The body quotes 18 rows, `corr=-0.943`, factor 1.659, slow n=11 with
identical means and range; the series window has grown by two slow runs since
the body was written, so its counts are a stale snapshot while its range and
correlation are confirmed. Budget arithmetic confirmed: `sqrt(2) x 0.0786 =
0.1112 -> 0.111`, band `(0.0555, 0.111]`.

## Step 10 — forward-carry: satisfied (no raise)

The carry is "if the spread does not narrow, report back BEFORE any raise; a
raise needs tvofi." The budget moved `0.426 -> 0.111` — a LOWERING, not a raise,
and earned by the change (the denominator grew about 4x, so the figure drops
about 4x). The body discloses that the class narrowing is a CONSTRUCTION claim
one box cannot measure, and that the empirical series comparison is deferred to
next week's timed runs; it does not overstate a measured narrowing. No raise
occurred, so the carry's report-back trigger never fired. Destination named by
the body ("none") checked: `R10-DIAG-REPLAY` (this group's `after`) consumes
`run_fixture`, whose parameters are unchanged (its returned dict gained only the
`loop_ref_ms` key), so no later brief is constrained. No carry owed.

## Other obligations

- Class (step 6): issue #2270 states one seam (the loop figure's ruler). The
  body names no enumeration rule; the PR's own control enumerates the one
  sibling (`cpu_ratio`) and dispositions it correct-by-design. The class is one
  seam, so no rule is missing.
- Claims/versions (steps 4-5): diff is four paths —
  `dev/audit/harnesses/r10_replay_loopnorm.py`, `dev/programme/delivery/2339.md`,
  `tests/closures.json`, `tests/replay.py`; no `VERSION`, manifest,
  `RELEASE_NOTES` or claim file. `env_drift.py --claims-only origin/main`: "ok".
- Conflict (step 13): `git merge-tree --write-tree origin/main <head>` rc=0, no
  path conflicts.
- Metrics (step 14): the only figures the diff moves are the `loop_cpu_ratio`
  budget (lowered, earned) and one `inert_reads` entry under
  `tests/harness_headers.py` (earned — that census reads every `repo_root`
  copy, including the new harness, which is why it reded the fixer mid-run).
- Red checks (step 11): all 45 head check-runs green; no branch commit shows a
  red gate check (the authored head `9d20cc2d6`'s jobs are `cancelled`, not
  failed, superseded by the record commit). The body volunteers a mid-development
  `harness_headers` red and answers it in-branch; verified —
  `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED` at
  the head with `tests/hastub`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED` (no budget raised).
- Architecture (step 15): the ruler lives beside `reference_solve` in
  `tests/replay.py`; no HA import added; the reference call sits outside the
  timed cycle (replay.py:1113-1115, after the CPU append at 1103-1107), so it
  cannot contaminate the numerator; no un-migrated `cost_figures` caller (every
  caller is in-file; the finder's `m2_loop_blind.py` passes its own figure to
  `cost_offenders` and is unaffected by the new optional parameter). Architect
  note: none, so no departure to check.

Round 1 of review. Verdict: merge.
