Closes #2509

Fold (e) of #1930, built in the brief's order: the replay first, the skip only
where a replay row says `never`, then the null control.

**(1) The replay.** The deferral's 595 is the `killed_by` row count of the
ledger at `b09e0b912284` (main at 2026-10-03T20:21+02:00), re-derived by
`git ls-tree -r --name-only b09e0b912284 tests/mutation_ledger/killed_by | wc -l`;
the same rule at `50af6174f53c` counts 2136, and the replay covers every
inventory site, not just the killed ones. `dev/audit/harnesses/r10_mutant_skip/replay.py`
traces every driver the net can hand a production site, on its own unmutated
worker tree. It uses the lane's own tracer: a `sys.monitoring` LINE callback,
disabled per location after the first hit, injected into every child through
`sitecustomize`. It writes `matrix.tsv` (checked in): one row per anchored
line, one state per driver.

**(2) The skip.** In `tests/mutation_table.py`, each shared driver's
baseline runs traced (`traced_baseline`). `drive` does not start a mutant run
when `reach_skip` reads that driver's row as `never` (`never_reaches`). A
pair with no row runs: an EXCLUSIVE driver (untraced, because it measures the
machine), a lazy or deferred driver, or a baseline the tracer could not keep
green, which is re-run untraced and keeps no row. A row is also refused, and
the pair runs, when the run:
- read the mutated file as text;
- started a non-Python child (git, tar, a type checker);
- started a Python child without the tracer's environment or PYTHONPATH;
- counted a child that left no record;
- was not green;
- or when the line has no instruction of its own.

Records are appended line by line before the traced instruction runs, so the
solve worker, which is SIGKILLed at exit, has already written its record.
`--no-reach-skip` drives every pair.

**Where it lives.** The tracer is in `mutation_table.py`, not in a sibling
module. `mutation-autofix` holds `contents: write`, restores only
`tests/closure.py` and `tests/mutation_table.py` from the base, and imports
`mutation_table` from `tests/`. A sibling module would therefore be the pull
request's copy, executing under the write grant. This is decision 0013's
pinned grader; the first cut had the sibling and was moved.

**What it is worth.** The dominant drivers can never skip, and the reasons are
measured: features, entities, structure, doc_claims, deployment_shape,
typing_ruler, env_drift and stress read production source as text, start git
or another non-Python process, or both. The skippable set is backtest,
block_duty, boost_drift_replay, debug_collect, edge, frontend, guard_pins,
manual_plan, open_meteo, optimality, plan_view, solar_alignment, validate and
wood_advisor. So the saving is real and bounded: about a tenth of a
survivor's sweep across the inventory (`## Figures`). It is not the most of
the lane's cost that the fold's wording implies.

**Alternatives that lost.**
- A checked-in matrix read at run time: stale on any production edit, so the
  rows the lane reads would describe another tree. Per-run tracing of the
  baseline the lane already pays for has no staleness.
- coverage.py: not installed in the CI venv, a new dependency, and no hook for
  source reads or child accounting.
- A hand list of skippable drivers: the class `tests/entities.py` already
  refuses (`DRIVER_EXCLUSIONS` is a derivation, not a preference).

## Head

`a7e41d646087efadd230b22634808f52da83fb38`. The replay and the null drives ran
against the production tree of the merge base `50af6174f53c`. This diff
touches no production file:
`git diff --stat 50af6174f53c a7e41d646 -- custom_components` prints nothing.
A row is a function of the production and driver trees, so the matrix
describes this head. Two runs used this branch before its last two edits:
- The lane A/B ran the branch's `tests/mutation_table.py` before the reach comment
  gained its one-run sentence. That delta is a comment.
- The real drives ran `null_drive.py` before it inlined `repo_root` in place of
  `parents[4]`. That delta is how `ROOT` is found, which resolves to the same
  directory.

`tests/entities.py`, `tests/harness_headers.py`, `tests/structure.py`, the scope
and the predictor were re-run at this head.

## Mutation proof

The checks are the four `R.check` blocks added to `tests/entities.py` beside
`_COV_JOB`. They drive a synthetic package through the real hook. Each
mutant below was applied to `tests/mutation_table.py` and run against those
four blocks, extracted verbatim; whole-file `entities.py` per mutant was not
run (about 440 s each here). The checks went red as listed, and each mutant
was restored (`cmp` against the saved copy: identical).

- M1, `rel in reach["reads"]` → `False`: red `and every way the row can be blind refuses the skip ...`
- M2, the non-Python-child refusal → `if False:`: red, the same check
- M3, the untraced-child refusal → `if False:`: red, the same check
- M4, `p["recorded"] < p["started"]` → `False`: red, the same check
- M5, `reach.get("rc") != 0` → `False`: red `and no row, a red run's row or an instruction-less line drives the pair`
- M6, `line not in executable` → `False`: red, the same check
- M7, `_importing()` returns True at once (every read counted as an import): red `and every way the row can be blind ...`
- M8, `after_in_child=_start` → `lambda: None`: red `and a forked child's executed line counts, the row still clean`
- M9, `traced_baseline` keeps a red run's reach: red `and every way the row can be blind ...` (its red arm asserts no row)

Two first-cut mutants survived and were replaced, not counted:
- `_fd or [...]` on fork is equivalent: the child writes into the inherited
  O_APPEND descriptor and still emits its start line.
- `co_name`-only `_importing` was too weak to change anything.

`sys.monitoring.DISABLE` → `None` survives as expected: it changes cost, not
verdicts.

The wiring line in `drive` (`if reach_skip(...)`) is pinned by no check. Its
effect is the lane A/B under `## Null control`: `REACH SKIP: 27 ...` against
`REACH SKIP: 0 ...` with `--no-reach-skip`.

## Null control

Three controls, each with the result a false skip would have printed.

- **The ledger.** Every `killed_by` row matching a current site is a measured
  kill. Its killer's row must not be `never`. Result: `LEDGER REPLAY: no killer
  is a never row`, with 2136 rows (363 on `reached` rows, 1773 on refused
  ones). The perturbation that shows the check can fail is real: the first
  cut's hook raised inside the interpreter's own open of a package-path main
  script. That broke the solve worker, features.py went red and stopped
  early, and the same replay then printed `319 killer(s) are never rows`. A red
  run now refuses its row.
- **Real drives of `never` rows.** `null_drive.py` drove 84 seeded `never`
  pairs, 6 per skippable driver, each mutant applied and run through its
  driver as the lane does, judged by `killed()`. Result: `killed 0, survived 84,
  timed out 0`. The positive control was 19 ledger kills held by the same
  drivers on `reached` rows, driven the same way: 18 killed. The one that was
  not, `tests/optimality.py` on `optimizer.py:HeatPumpOptimizer._optimize_space_only
  GUARD_OFF 6a3be0ea`, is a `reached` row the skip never touches. That makes it
  a ledger pin this box did not reproduce, outside this change.
- **The lane itself, A/B.** `tests/mutation_table.py --scope full --max 8
  --jobs 3 --seed 1930`, once as built and once with `--no-reach-skip`, ran
  with `--scripts` set to the default net less `tests/entities.py`, which is
  red in this container (`## Red checks`). Verdicts per mutant are
  byte-identical: `diff` of the `ok`/`LIVES` lines is empty, with 4 killed
  under the same named killers and 4 LIVES. That makes the kill set and the
  survivor set the same. The skip arm printed `REACH SKIP: 27 driver run(s)
  not started`, the other `REACH SKIP: 0`.

Determinism of the rows, as a fourth control: two replay passes give
byte-identical `matrix.tsv`. Raw hits moved in two drivers only,
config_flow_steps.py and finite_boundary.py. Both are refused already because
they read the files as text. The lines that moved are wall-clock-hour branches
in `dhw_schedule.py`; the comment beside the tracer states that limit.

## Figures

- Kill-row count, 595 at `b09e0b912284` and 2136 at `50af6174f53c`, rule as
  above: `git ls-tree -r --name-only <sha> tests/mutation_ledger/killed_by | wc -l`
- Pairs, the census `PAIRS ... reached ..., never ..., run ...`: 122888 pairs
  over 6074 anchors and 26 traced drivers, 40044 of them `never`.
  Instrument: `python3 dev/audit/harnesses/r10_mutant_skip/replay.py --jobs 3 --out <dir>`
  (re-traces), or `--from <dir>/reach.json` to rebuild without re-tracing.
- Survivor-sweep bound, the census `SURVIVOR SWEEP` line, same instrument:
  the summed recorded solo seconds of every pair, against the same without the
  `never` rows, 10.5% less. Null: the `--no-reach-skip` lane drives every pair,
  so it saves nothing.
- Per-driver states and refusal reasons: the census lines of the same
  instrument (`tests/<driver>: rc=... never=... reached=... run=... [reason]`).
- Ledger replay, the census `LEDGER REPLAY` lines, same instrument.
- Real drives: `python3 dev/audit/harnesses/r10_mutant_skip/null_drive.py --matrix dev/audit/harnesses/r10_mutant_skip/matrix.tsv --per-driver 6 --positive 2 --seed 1930 --jobs 2`
  prints the `NULL ...`, `POSITIVE ...` and `NULL CONTROL:` lines.
- Lane A/B: the two `tests/mutation_table.py --scope full --max 8 --jobs 3 --seed 1930 --scripts <default less entities.py>`
  runs, with and without `--no-reach-skip`. Each prints its `REACH SKIP:` line
  and its verdict lines, and `diff` of the verdict lines is empty. The 27
  skipped runs cost at most the summed baseline seconds of the pool's `never`
  pairs, 1045 driver-seconds, of which the 510 on the 4 survivors is exact,
  since a survivor sweeps every driver. The arms' wall clocks, run in sequence
  on one 4-core box that was also running other seat work, are not a clean
  timing and are not claimed.
- Matrix file: `dev/audit/harnesses/r10_mutant_skip/matrix.tsv`, sha1
  `f4a3ad754d34a984e63c64294996bdf378adcd26`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
  prints `MODE: SCOPED -- 2 script(s) run`: tests/entities.py and
  tests/harness_headers.py. Both ran at this head (`## Red checks`), as did
  `run.sh`'s run_always steps `closure.py selftest`, `layout.py` and
  `env_drift.py --claims-only <merge-base>`, all green.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`:
  `no closures or fast red predicted`.

## Red checks

`tests/entities.py` is red in this container on two checks, both present
untouched at the merge base:
- `gate-sweep.yml: on CI's completion, ...` (U0c)
- `graders-head-copy's delivery_status step is red only when ...`

At `50af6174f53c` the result is `2 of 2425 ENTITY CHECKS FAILED`, the same two.
At this head it is `2 of 2429 ENTITY CHECKS FAILED`, the same two, with the
four new checks `ok`. Both run a workflow step under bash with a stand-in
`python3` first on PATH, and here the real interpreter answers instead:
`gate.py` prints `FAIL usage: ...` with and without the tracer. That is a
container property, not this diff, so no cheaper detector is owed by this PR.
`tests/harness_headers.py` at this head: `ALL 112 HARNESS HEADER CHECKS PASSED`. On the first run at this branch it went red, `1 of 112`, on `every inlined walk matches the canonical helper and no depth root remains`. The cause was this diff's two new harnesses taking `ROOT` from `parents[4]`; they now inline the canonical `repo_root`. The cheaper detector exists and was run: `harness_headers.inline_scan()`, in seconds, before the push.

## Forward-carry

none: no stage that has not started changes what it must do because of this
diff. The two facts a later editor of the lane needs are beside the code they
bind, in the reach comment of `tests/mutation_table.py`: the tracer must stay
inside the pinned program, and a row is one run's. R10-MUTATION-ANCHOR (the
`--anchor` entities pins) is unaffected, because entities.py keeps every pair:
it reads source as text and starts non-Python children.

## Friction

none
