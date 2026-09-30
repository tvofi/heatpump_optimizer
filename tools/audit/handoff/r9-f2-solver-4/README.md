# R9-F2.4 evidence harnesses

Everything this PR's body cites, in the tree — a `/private/tmp` copy is not a
record, this directory is. Files under `tools/audit/` are outside every closure
by the INERT prefix, so this directory classifies itself and adds no gate
surface.

The finder's own harnesses are **not** copied here. They run from an export of
evidence commit `79aa98ec` (`$EX` in the body), because `fixer.md` step 3 asks
for the finder's instrument at its own sha1 and not for a retyped copy; each one
inserts `tests` and `custom_components` relative to the cwd, so running it with
the cwd at a tree measures that tree. The sha1s the body cites are recorded in
`ev/harness_env_base.log`. The class instruments — the P2 and P4 sweep
enumerators and the P2 RCA prototype's `owners_lint.py` — are run from their own
commits (`c44e7bcd60`, `6b65c9c4a8`, `3938c8ea`) planted at their canonical
paths inside each tree being measured, because an enumerator that resolves its
own location reads nothing from an export and prints the same zeros a fixed tree
does.

- `seed_price.py`: what ONE extra bang-bang seed costs and buys (D0-s2-02).
  `race.py --perturb add_emax_ladder` prices all 13 rungs at once; the finding's
  fix scope leaves the single-seed option open and #1294's refusal stands
  against the ladder, so the refusal had to be priced on the cheaper option. It
  imports `race.py` from the export, so the cell grid and the seed construction
  are the finder's and not a restatement, and reports the first
  `_multi_start_minimize` call's objective (`race.py`'s `f=`) beside
  `time.process_time()` around the whole `optimize()`. `ev/seed_price_base.log`.
- `basin_carry.py`: the P4 carry. F2.1 (#1694) disclosed a basin effect in the
  golden scenario `everything_on` as summed degree-steps below `config.min_temp`
  and this PR's brief asks for that number re-measured at its own merge base.
  Reports #1694's metric with #1694's caveat restated (it counts `min_temp` at
  every step, the night-setback window included, where the solver's own floor is
  `min_temp - 0.5`), beside `predicted_cost`, `compressor_starts`, the count of
  True in `heat_pump_on_schedule`, and a sha1 of the captured schedules so
  "the solve did not move" is a comparison. `ev/basin_carry_{base,head}.log`.
- `drift_leaves.py`: the complete leaf census behind the golden claims.
  `env_drift.py --all` prints at most five leaves per scenario, which cannot
  answer "is every moved leaf the on schedule, and does every one move the same
  way" — the question a claim asks a reviewer to accept 46 leaves on. `--out`
  captures the named scenarios from the tree it runs in as JSON; `--diff` is
  pure JSON and needs no solver. It carries the five coordinator captures as a
  control, because this PR's D8 arm gates a published value and a coordinator
  fixture that stays byte-identical is the measurement that the gate moves no
  published number. `ev/drift_leaves.log`.
- `run_block.py`: runs one `tests/features.py` block on its own — the suite's
  prologue plus the source between two markers, verbatim, so the checks are the
  suite's own bytes and a mutant that fools this runner fools the suite. A
  marker it cannot find is a refusal, not an empty run.
- `mutation_proof.py`: the mutation proof. Eight mutants (M1, M2, M2b, M3–M7),
  each restoring one seam of the fix to its base form, judged on the failing
  checks they ADD to the healthy arm's set so a red this box already has is not
  read as a kill — or, when the runner dies before its own summary, on the
  block's named checks that went red, with the runner's tail printed. It
  refuses to start on a dirty production file and refuses a mutant that restores
  clean but adds no failing check. `ev/mutation_proof_{host,container}.log`,
  `ev/mutant_m6_host.log`, `ev/mutant_m6_m7_host.log`.
- `rss_ab.py`: `winter/cycle`'s attributable RSS, base tree against head tree,
  N interleaved draws each, through `tests/stress.py`'s own `--memory-baseline`
  and `--memory-probe` entry points; prints every draw and min/median/max per
  tree and judges nothing. `ev/rss_ab_winter_cycle.log`.
- `ev/`: the runs the body quotes — the finder's three harnesses at base and
  head with their perturbation arms, the four class instruments at base and
  head, the drift lane and its census, the full `features.py` and `entities.py`
  at head in the container and on the host, and the gate, typing and mutation
  lanes.

Environment for every container run: `hpo-ci` (Linux amd64 under Rosetta, 4
CPU), CPython 3.14.7, numpy 2.4.6, scipy 1.17.1, scipy-openblas 0.3.31
DYNAMIC_ARCH, `OPENBLAS_CORETYPE=Sandybridge`, BLAS pinned to 1 thread,
`PYTHONPATH=tests/hastub`, each lane behind a host-side
`tests/gate_lock.py auto-lease` and never a lease nested inside the container.
Host runs say so where they are cited: CPython 3.11, numpy 2.4.6 on Accelerate,
which is a different basin — `basin_carry.py` reads a different `plan_sha1` for
the same tree on the two, and that sensitivity is one of the two grounds the
P4 refusal rests on.
