Group R10-MUTANT-SKIP, issue #2509 (the group's one roster issue). The body
carries no closing keyword: the update that refused the last body did not list
#2509 as intended, and naming it at merge is the orchestrator's.

Fold (e) of #1930, built in the brief's order: the replay first, the skip only
where a replay row says `never`, then the null control.

**(1) The replay.** The deferral's 595 is the `killed_by` row count of the
ledger at `b09e0b912284`, re-derived by
`git ls-tree -r --name-only b09e0b912284 tests/mutation_ledger/killed_by | wc -l`;
the same rule at this merge base `fe5884445452` counts 2146, and the replay
covers every inventory site, not just the killed ones.
`dev/audit/harnesses/r10_mutant_skip/replay.py` traces every driver the net can
hand a production site, on its own unmutated worker tree, with the lane's own
tracer: a `sys.monitoring` LINE callback, disabled per location after the first
hit, injected into every child through `sitecustomize`. It writes `matrix.tsv`
(checked in, re-traced on this merged tree): one row per anchored line, one
state per driver.

**(2) The skip.** In `tests/mutation_table.py`, each shared driver's baseline
runs traced (`traced_baseline`). `drive` does not start a mutant run when
`reach_skip` reads that driver's row as `never` (`never_reaches`). A pair with
no row runs: an EXCLUSIVE driver (untraced, because it measures the machine), a
lazy or deferred driver, or a baseline the tracer could not keep green, which
is re-run untraced and keeps no row. A row is also refused, and the pair runs,
when the run read the mutated file as text, started a non-Python child (git,
tar, a type checker), started a Python child without the tracer's environment
or PYTHONPATH, counted a child that left no record, or was not green; or when
the line has no instruction of its own. Records are appended line by line
before the traced instruction runs, so the solve worker, SIGKILLed at exit, has
already written its record. `--no-reach-skip` drives every pair.

**Where it lives.** The tracer is in `mutation_table.py`, not a sibling module:
`mutation-autofix` holds `contents: write`, restores only `tests/closure.py`
and `tests/mutation_table.py` from the base, and imports `mutation_table` from
`tests/`, so a sibling would be the pull request's copy executing under the
write grant (decision 0013's pinned grader).

**What it is worth.** The dominant drivers can never skip, for measured
reasons: features, entities, structure, doc_claims, deployment_shape,
typing_ruler, env_drift and stress read production source as text, start git
or another non-Python process, or both (the census lines in `## Figures`). The
saving is real and bounded at about a tenth of a survivor's sweep, not the most
of the lane's cost the fold's wording implies.

**Alternatives that lost.**
- A checked-in matrix read at run time: stale on any production edit. Per-run
  tracing of the baseline the lane already pays for has no staleness.
- coverage.py: not in the CI venv, a new dependency, and no hook for source
  reads or child accounting.
- A hand list of skippable drivers: the class `tests/entities.py` already
  refuses (`DRIVER_EXCLUSIONS` is a derivation, not a preference).

**The posix_spawn fix.** CPython 3.13+ starts a default `subprocess.Popen`
child through `os.posix_spawn` when `os.POSIX_SPAWN_CLOSEFROM` exists, and
raises that audit event after `subprocess.Popen` for the same child; the hook
counted it as a second, foreign child and refused every traced row on CI's
runner. The hook now skips an `os.posix_spawn` raised from `subprocess`'s own
`_posix_spawn`, and a bare `os.posix_spawn` still refuses the row
(`## Red checks`).

## Head

`d3524d062cbde725bd83c7f5bc4e756fa4a8009c`, measured at `origin/main`
`fe58844454525da612f7a06e44700287b55d0275` (2026-10-25T01:50Z). On top of the
handed-off `1813740bc926` it carries a merge of `origin/main` at
`fe5884445452` (no conflict) and two commits:
- `b6853003c`: `matrix.tsv` re-traced on the merged tree.
- `d3524d062`: `null_drive.py` prints the red checks of a `never` row it kills
  (`## Null control` says why).
`tests/mutation_table.py` is byte-identical to `1813740bc926`'s; the merge
brought main's own edits to `tests/entities.py`. This diff touches no
production file: `git diff --stat origin/main HEAD -- custom_components`
prints nothing. Every figure below was re-taken on this tree; none is carried
from an earlier head.

## Mutation proof

The checks are the five `R.check` blocks beside `_COV_JOB` in
`tests/entities.py`, which drive a synthetic package through the real hook.
They were extracted verbatim from this head's `tests/entities.py` and run
against each mutant of `tests/mutation_table.py`, on two interpreters: the CI
venv's Python 3.14.7, which has no `POSIX_SPAWN_CLOSEFROM`, and the system
Python 3.13.17, which has it, as CI's 3.14.8 does. The unmutated copy is green
on both. Each mutant was restored (`cmp` against this head's file: identical).

- M1, `rel in reach["reads"]` → `False`: red `and every way the row can be blind refuses the skip ...` on both
- M2, the non-Python-child refusal `if foreign:` → `if False:`: red, the same check, on both
- M3, the untraced-child refusal → `if False:`: red, the same check, on both
- M4, `p["recorded"] < p["started"]` → `False`: red, the same check, on both
- M5, `reach.get("rc") != 0` → `False`: red `and no row, a red run's row or an instruction-less line drives the pair` on both
- M6, `line not in executable` → `False`: red, the same check, on both
- M7, `_importing()` returns True at once: red `and every way the row can be blind ...` on both
- M8, `after_in_child=_start` → `lambda: None`: red `and a forked child's executed line counts, the row still clean` on both
- M9, `traced_baseline` keeps a red run's reach: red `and every way the row can be blind ...` on both
- N1, `_popen_spawn()` returns True at once, so a bare `os.posix_spawn` is not recorded: red `and every way the row can be blind ...` on both
- N2, the posix_spawn guard removed (`if True:`), the code before the fix: on 3.13.17 red `the reach tracer reads a clean run's row ...`, `and a Popen child started through os.posix_spawn reads the same clean row` and `and a forked child's executed line counts ...`, the two CI failed plus the new one; on 3.14.7 red only the new check, which is why that check exists.

`sys.monitoring.DISABLE` → `None` changes cost, not verdicts, and was not
counted. The wiring line in `drive` (`if reach_skip(...)`) is pinned by no
check; its effect is the lane A/B under `## Null control`.

## Null control

All on this head, `BASH_ENV` unset.

- **The ledger.** Every `killed_by` row matching a current site is a measured
  kill, so its killer's row must not be `never`. The replay prints
  `LEDGER REPLAY: no killer is a never row` over 2146 rows (363 on `reached`
  rows, 1783 on refused ones). Had the skip been wrong on a killed site, the
  same line prints the count of killers that are `never` rows; a red traced
  run printed 319 of them on the first cut, before a red run refused its row.
- **Real drives of `never` rows.** `null_drive.py` drives a seeded sample of
  84 `never` pairs, 6 per skippable driver, each mutant applied and run
  through its driver as the lane does, judged by `killed()`. The first pass
  printed `killed 3`: three `tests/boost_drift_replay.py` pairs
  (`dhw_schedule.py:parse_day_overrides RETURN_DEL b4c5be4b`,
  `price_model.py:extend_price_series GUARD_OFF 4c916e3a`,
  `optimizer.py:HeatPumpOptimizer.get_current_action BOOLOP f18d7d5c`), each
  `rc=1 failed=1` against a green baseline, and the harness kept no line naming
  the red check. Each was re-driven through `run_script` beside an unmutated
  run, all four at once: all four `ALL 46 BOOST DRIFT CHECKS PASSED`. So the
  three are not reproducible, and the cause of their red is not established.
  The harness now prints the red checks of a null kill. The second full pass,
  same seed and sample, printed `NULL never rows driven 84: killed 0, survived 84,
  timed out 0` and `NULL CONTROL: no never row was killed`. The positive
  control, 19 ledger kills held by the same drivers on `reached` rows, killed
  18 in both passes. The one not reproduced, `tests/optimality.py` on
  `optimizer.py:HeatPumpOptimizer._optimize_space_only GUARD_OFF 6a3be0ea`,
  is a `reached` row the skip never touches.
- **The lane itself, A/B.** `tests/mutation_table.py --scope full --max 8
  --jobs 3 --seed 1930 --scripts <the default net less tests/entities.py>`,
  once as built and once with `--no-reach-skip`. The skip arm printed
  `REACH SKIP: 32 driver run(s) not started`, the other `REACH SKIP: 0`. The
  verdict lines of the two arms are byte-identical (`diff` of the `ok`/`LIVES`
  lines exits 0): 4 killed under the same named killers, 4 LIVES. So the kill
  set and the survivor set are the same with and without the skip.

**MUTATION TABLE BREACHED, settled.** Both arms print `4 survivor(s) of 8
evaluated = 50.0%, cap 30.0%` and the breach. It is not this diff's.
- The survivors are `dhw_learning.py:DhwProfileLearner.normalize_profile CMP_BOUND 2049cabe`,
  `frontend.py:_register_lovelace_resource BOOLOP 82edf9b6`,
  `legionella.py:LegionellaGuard.async_track_cycle CMP_BOUND bb4d484e` and
  `pv.py:summarize CMP_BOUND 032d7707`. None carries a `killed_by` or
  `survivor_triage` entry at the merge base, so all four are sites main
  already leaves unpinned, counted in main's `unpinned_sites`.
- The production tree is main's own (the diff above), and the `--no-reach-skip`
  arm, which is main's lane on main's production, prints the same four. The
  breach is identical with the skip off, so the skip did not cause it.
- `tests/entities.py` was out of the A/B net (`## Red checks`, the container
  note). Driven against the four mutants beside an unmutated run, it killed
  none of them. One run went red on `gate lease priority: concurrency control:
  two waiters released in one poll, exactly one holds the slot`, a lease-timing
  check unrelated to the mutated `dhw_learning.py` line, under five concurrent
  runs; the unmutated run was green. So leaving entities.py out did not make
  these survivors.
- The cap reads a seeded 8-site sample of the whole tree. The recorded `full`
  measurement is 12 of 40 (`last_measured.full` in
  `tests/mutation_budgets.json`), and at that rate a sample of 8 shows 4 or
  more survivors with probability 0.194. This PR's own lane runs
  `--scope changed`, which draws only from production files the diff touches,
  and it touches none.

The four are real gaps in main's tests, but pinning them would mean adding
tests for four unrelated modules, outside this group's scope. The deterministic
`unpinned_sites` ratchet already carries them, and the nightly's burn-in is the
owner of pinning them.

## Figures

- Kill-row count, 595 at `b09e0b912284` and 2146 at `fe5884445452`:
  `git ls-tree -r --name-only <sha> tests/mutation_ledger/killed_by | wc -l`
- Pairs, the census `PAIRS ... reached ..., never ..., run ...`: 122960 pairs
  over 6076 anchored sites and 26 traced drivers, 40092 of them `never`.
  Instrument: `python3 dev/audit/harnesses/r10_mutant_skip/replay.py --jobs 3 --out <dir>`
  (re-traces), or `--from <dir>/reach.json` to rebuild without re-tracing.
- Survivor-sweep bound, the census `SURVIVOR SWEEP` line, same instrument: the
  summed recorded solo seconds of every pair against the same without the
  `never` rows, 10.5% less. Null: the `--no-reach-skip` lane drives every pair,
  so it saves nothing.
- Per-driver states and refusal reasons: the census lines of the same
  instrument (`tests/<driver>: rc=... never=... reached=... run=... [reason]`).
- Ledger replay, the census `LEDGER REPLAY` lines, same instrument.
- Real drives: `python3 dev/audit/harnesses/r10_mutant_skip/null_drive.py --matrix dev/audit/harnesses/r10_mutant_skip/matrix.tsv --per-driver 6 --positive 2 --seed 1930 --jobs 2`
  prints the `NULL ...`, `POSITIVE ...` and `NULL CONTROL:` lines.
- Lane A/B: the two `tests/mutation_table.py --scope full --max 8 --jobs 3 --seed 1930 --scripts <default less entities.py>`
  runs, with and without `--no-reach-skip`; each prints its `REACH SKIP:` line,
  its verdict lines and its `survivor(s) of ... evaluated` line. The arms ran
  in sequence on one 4-core box; their wall clocks are not claimed.
- Breach odds, 0.194: the binomial tail P(X ≥ 4) for n = 8, p = 12/40.
- Matrix file: `dev/audit/harnesses/r10_mutant_skip/matrix.tsv`, sha1
  `77f604ec18584c690ed5d76addb201654cac44cf`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
  prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`: tests/entities.py
  (`ALL 2434 ENTITY CHECKS PASSED`) and tests/harness_headers.py
  (`ALL 112 HARNESS HEADER CHECKS PASSED`), both green at this head, as were
  `run.sh`'s run_always steps `env_drift.py --claims-only <merge-base>`,
  `closure.py selftest` and `layout.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`:
  `no closures, fast, wave-script or instrument red predicted`.

## Red checks

Read at the PR's live head `b1f77ff7db58` and its parent merge `a82287a5f4ff`.
Neither carries the posix_spawn fix: `1813740bc926` was handed off and never
pushed. `tools/audit/seat/failure_logs.sh 2749` printed `NO-LOG` for every job
in this container, so the lines below are from the same job logs read through
`gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`.

**`tests / fast (3.14)`**, red at `b1f77ff7db58`, job 120937928647 of run
40115389027, and at `a82287a5f4ff`, job 120931076805 of run 40113804067:
`2 of 2429 ENTITY CHECKS FAILED`:
- `the reach tracer reads a clean run's row: ...`, with `never={2: False, 6: False, 10: False}`
  and `problems=['starts a non-Python process: os.posix_spawn .../bin/python3']`
- `and a forked child's executed line counts, the row still clean`, with the same problem.

This is not the `BASH_ENV` stand-in effect. That effect turns
`gate-sweep.yml: on CI's completion, ...` and
`graders-head-copy's delivery_status step ...` red in this container only,
and CI sets no `BASH_ENV`. CI's two reds are the posix_spawn defect this head
fixes (`## Mutation proof`, N2 on 3.13.17 reproduces exactly these two). It is
not inherited: main's run at `806aa2ce89ae` was green (run 40110905829).
*Cheaper detector:* the five check blocks, extracted, run in about 10 s, but
before the fix every seat box ran them on an interpreter without
`POSIX_SPAWN_CLOSEFROM`, where `Popen` takes `fork_exec` and the failing route
is unreachable. The countermeasure is the check
`and a Popen child started through os.posix_spawn reads the same clean row`:
`close_fds=False` takes the `posix_spawn` route on every 3.13+, so it turns red
under N2 on 3.14.7 too. Standing cost: one more traced run inside
`entities.py`, about 1 s. Process state (d): a precondition (the seat
interpreter's build) differed from CI's under a sound process.

**`tests / closures`**, red at `a82287a5f4ff`, job 120931076859 of run
40113804067: `INERT READS UNDER-APPROXIMATED` for `tests/harness_headers.py`
on `dev/audit/harnesses/r10_mutant_skip/null_drive.py` and
`dev/audit/harnesses/r10_mutant_skip/replay.py`. That is the `UNDER-SCOPED`
class `ci-autofix.md` repairs: `closures-autofix` pushed `b1f77ff7db58`
(`ci: re-record closures`), and `tests / closures` is green there (job
120937928521). Answered by naming it.

**`pr-contract / pr-contract`** and **`gate`** at `b1f77ff7db58` grade the
body on the PR, which is the body this one replaces.

## Forward-carry

n/a: no stage that has not started changes what it must do because of this
diff. The two facts a later editor of the lane needs are beside the code they
bind, in the reach comment of `tests/mutation_table.py`: the tracer must stay
inside the pinned program, and a row is one run's. R10-MUTATION-ANCHOR (the
`--anchor` entities pins) is unaffected, because entities.py keeps every pair:
it reads source as text and starts non-Python children.

## Friction

none
