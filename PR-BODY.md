R10-CI-SLIM: three cards of the slip study the owner accepted on 2026-11-05 (C2, C3, C7). This change makes main's critical-path ratchet report-only. Edit runs stop holding a runner while the code run works. Product pull requests stop paying for machinery lanes, PR CodeQL and repeated pin measurement. No product file changes (`custom_components/` untouched).

**Repair round 2.** The head 53e21a9b4 was red on five causes. Two were defects of this branch, and both are fixed here:
- `tests / fast (3.14)`: `tests/harness_headers.py` refused three fixed parent counts. These were `ROOT = Path(__file__).resolve().parents[4]` in `c7_replay.py`, `edit_runs.py` and `gate_satisfiable.py`. Commit 37474e097 replaces each with the canonical `repo_root` walk, copied from `tools/audit/repo_root.py`. The same commit drops a duplicated pathlib import in `c2_replay.py`. It was not the CPU limit (see `## Figures`).
- `tests / closures`: the INERT READS were under-approximated. Commit 1066ed961 re-records `tests/harness_headers.py` alone with `./tests/derive_closures.sh --single` on Linux. It adds exactly the four harness paths to `tests/closures.json`.

The other three causes are not defects of this diff: budget-raise-gate, delivery-status and nightly-status (see `## Red checks`).

**Hot-file order:** this group (R10-CI-SLIM) lands BEFORE R10-PROCESS-SLIM. That group also edits `.github/workflows/governance.yml` and `tools/audit/seat/bus.sh`. This change touches three parts of governance.yml: `on.workflow_call.inputs`, `instrument-self-tests` and `env-matrix`. The group brief already states that order. Card C7 already makes (a)'s saving wait for C1, so neither is a new carry.

**C2. `critical_path_minutes` is report-only.** `tests/ci_ratchet.py` adds a `REPORT_ONLY` set holding that one metric. `compare` prints it as `info critical_path_minutes: X (reference R; report-only, never graded)` and never counts it. Every other `ci_budgets.json` row is still graded at zero tolerance. The band machinery is deleted: `BAND_KEYS` and the band row `critical_path_minutes_band`. The recorded value stays as the reference that `orchestrator_tick.py`'s ETA check reads, and it is not re-recorded. `tools/policy/budget_raise_gate.py` types that reference `free` and lets the retired band fall to `frozen`.

**C3 (option A). An edit run holds no runner.** `prelude.defer_to` looks for an unfinished code run at the same head and PR whose `pr-contract / pr-contract` has not started. When it finds one, the edit run's workset is `arch-score budget-raise-gate`, with no wait, and those two judge the live body at once. `pr-contract` reads the body off the API when it starts, after every unit. So that check belongs to the code run, and that run's gate judges the LATEST body. The edit run's gate takes the prelude's workset (`WORKSET` env, `gate.deferring`) and publishes its deferral at once. That gate is never a source for a unit it skipped: a unit whose every job is `skipped` in another run is no source. A started `pr-contract`, a finished code run or no code run keeps today's wait.

Why the deferring gate is red, not skipped: a skipped required check passes. Every deferral is decided before the code run's gate is listed, so that gate is the later `gate` check at the head. A deferral read in a race is a false RED, which `gate-sweep.yml` re-judges. It is never a false green.

**C7.** (a) `prelude.machinery` reads the changed list. A file counts as product when it is `custom_components/`, `docs/`, `README.md`, a script `tests/closures.json` measures, `tests/golden/` or `tests/mutation_ledger/`. When every file is product, three lanes stand down: `tests / arch-instrument`, the `tests / closures` recording with its check, and `governance / env-matrix`. Each stands down at the step level and reports success, so no required name ends SKIPPED. `governance / instrument-self-tests` is not required, so it skips whole. Every other file runs them: tools/, .github/, dev/, policy files, tests infrastructure and unknown root files. Every push runs them too. The closures lane keeps its `no-copies` scan.

(b) `codeql_scope.decide` skips every leg of a pull request with nothing under `custom_components/` or `.github/`. The codeql_scope.py program itself counts as `.github/` does. The stand-in reports success, and a push to main always analyzes.

(c) `prelude.pins_due` gates `tests / mutation-pins` and `tests / mutation-autofix`. They run only when this push's own delta (`before...head`) touches the package, a golden fixture or a measured script. So a ledger-only pin commit or a tooling fix-up does not re-measure the survivors of the head before. An opened or reopened PR measures, and so does an unreadable delta. A pull request's base copy of `prelude.py` has neither output, so on this PR's own CI both read as run.

**Owner constraint (tvofi, 2026-11-05), per change.** For each production path, this names the check that still guards it, and why the risk to production quality and to future throughput is acceptable.
- C2: it guards no production code. `tests / ci-ratchet` still grades every other CI metric at zero tolerance (the planted `script_runs_per_push` 54 -> 55 is GREW at the head). The risk accepted is a slower critical path going ungraded. It stays printed and feeds `orchestrator_tick.py`'s ETA. Throughput gains: no more re-record and band-widening PRs (#2839, #3045, #3180, #3189, #3201, #3228). Measured before/after: `## Null control`, C2.
- C3: no check is skipped. The edit run defers `pr-contract` to the code run at the same head, and that code run judges the latest body. Every production unit is still judged by the code run's gate. A race gives a false red, never a false green. Opus review dispatch is not touched. Before/after: 4438 -> 660 edit-run job-minutes.
- C7a: a diff touching `custom_components/` keeps every production check, because the lanes it idles never read production code. Those lanes are arch-instrument, the closures recording and env-matrix, all of which measure machinery. `tests / fast`, `tests / mutation`, goldens, features, CodeQL and review are unchanged. `gate_satisfiable.py`'s production-only case reads `pins_due=True` with every CodeQL leg `analyze`. Before/after: 0 runs idled in the sample, so it pays only after C1.
- C7b: CodeQL still analyzes every pull request reaching `custom_components/` or `.github/`, and every push to main. The legs it skips are tools/dev-only diffs, which main's push analysis still covers before release. Before/after: 2955 -> 1797 job-minutes.
- C7c: mutation pins still run on every delta touching the package, a golden fixture or a measured script, and on every opened PR. The required `tests / mutation` check is not gated. Before/after: 2234 -> 1756 job-minutes.

Alternatives not taken:
- (C3, B) Dropping `edited` and leaving body edits to the sweep was the card's other option. The owner picked A.
- (C7a) Moving the stand-down to job level would also skip the runner start, but a skipped required job is a SKIPPED source: see `gate_satisfiable.py`'s null control below.
- (C7a) Putting the rule in `gate.py` as a fifth event class would make two deciders for one fact.
- (C2) Deleting the whole critical-path derivation (window_work_minutes and the runner probe) is about 500 lines across tests.yml, entities.py and four harnesses that replay it. The card asks for the metric to stay printed.
- (repair) Keeping `parents[4]` with an allow-list entry would blind the depth-seam pin at the shape it exists to catch (fixer.md step 14). The canonical walk is the tree's one mechanism, so the repair uses it.

Step ref: the previous round left `handoff-wip/r10-ci-slim` at a body commit off the code line (720694b1c), and its deletion was refused here. So the step ref advances by wip-only commits, and the code head carries none of them.

Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` read OK. numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`. No golden ran: the scope is MODE: FULL, so they are CI's.

## Head

4ae9f7596c751d06d27d246f51e7f09277928f6b. It is the previous head 53e21a9b4eadb48027e634cc0bf109b960997824, plus three things in order:
- origin/main 7d95405e384e1ebf8223f04657c85996af55f3d9 merged as 498f0cab9 (no conflict);
- the two repair commits 37474e097 and 1066ed961;
- origin/main 785c2b604ba4c01891737a5285f4f4f49394c18f merged as 4ae9f7596 at 2026-11-06T01:11Z. That merge auto-merged `tools/policy/budget_raise_gate.py` (#3223) and had no conflict.

`tools/pr/prepr.sh` read `rc=0` at 1066ed961. main moved during that run, so it ran again at 4ae9f7596. After the second merge, these were re-taken at 4ae9f7596 on merge base 785c2b604: the self-tests, structure, the depth seams, the architecture score, the scope and `budget_raise_gate.py` against PR 3230.

The rest was taken at 1066ed961 on merge base 7d95405e3: the harness replays, the harness_headers timings and the two status graders. The main delta 7d95405e3..785c2b604 touches no file those read. Its names matched against `tools/ci/`, `tests/ci_ratchet`, `tools/pr/codeql_scope`, `.github/workflows/`, `dev/audit/harnesses/r10`, `tests/harness_headers`, `tests/delivery_status`, `tests/nightly_status` and `tests/closures.json` count 0.

## Mutation proof

Each mutant replaced one production line in place, ran the named self-test, and was restored. These were taken at 7cb0eb430; no line they mutate changed since (`git diff 7cb0eb430 HEAD -- tests/ci_ratchet.py tools/ci tools/pr/codeql_scope.py` is empty).
- C2: `if key in REPORT_ONLY:` -> `if False:` in `tests/ci_ratchet.py` `compare`. `python3 tests/ci_ratchet.py --self-test` fails 2 of 65: `critical_path_minutes growth (23.574 -> 99.0) is printed, never graded -- grew 1` and `both planted: only the graded row counts -- grew 2`.
- C3 M1: `bound = 0` (gate.judge, deferring) -> `pass`. `python3 tools/ci/gate.py --self-test` fails 1 of 57: `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner`.
- C3 M2: `continue` (a deferred unit is no source) -> `pass`. Fails 1 of 57: `C3: a unit a run deferred is no source even under its full job name (skipped)`.
- C3 M3: own-workset eligibility -> title workset. Fails 2 of 57: `C3: the deferred gate re-judged once the code run ended (green|its pr-contract red)`.
- C3 M4: `if defer_to(...) is not None:` -> `if False:`. `python3 tools/ci/prelude.py --self-test` fails 3, each `C3: beside a code run in its units / a queued code run / a queued pr-contract ... exits at once`.
- C3 M5: the `STARTED` predicate -> `if True:`. Fails 1: `C3: beside a started pr-contract ... the edit run waits and owns pr-contract`.
- C7 M6: `if not any(f.startswith(ANALYZED_PREFIXES) ...)` -> `if False:`. `python3 tools/pr/codeql_scope.py --self-test` fails 2 of 94: `C7b: a tools/ .py diff skips python on a pull request` and `a roster PR skips javascript-typescript`.
- C7 M7: `machinery` -> `return True`. Fails 2: `C7a: a product-only diff ... idles the machinery lanes` and `C7a: the prelude's output on a product-only pull request`.
- C7 M8: `pins_due` -> `return True`. Fails 2: `C7c: a pin commit's delta (the ledger only) measures nothing again` and `C7c: a tooling or body-record delta measures nothing again`.
- Gate core: `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants` reads `RESULT mutants=16 survivors=0` at 1066ed961.
- Repair (depth seams): the pre-fix tree 498f0cab9 is the mutant. `depth_root_seams()` (tests/harness_headers.py) returns 3 there, one per harness at its `parents[4]` line. It returns 0 at 1066ed961 and 0 at the merge base 7d95405e3. CI's job 127578956992 read that check as `FAIL every inlined walk matches the canonical helper and no depth root remains`.

## Null control

- C2: run `python3 dev/audit/harnesses/r10_ci_slim/c2_replay.py <tree> dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json` on each tree. At merge base 7d95405e3 the recorded window reads `GREW critical_path_minutes: 29.067 (budget 23.574, band 1.3)`, grew=1. At the head: `info critical_path_minutes: 29.067 (reference 23.574; report-only, never graded)`, grew=0. The planted `script_runs_per_push` 54 -> 55 is GREW at both ends (grew=2 at the base, grew=1 at the head), so the ratchet still refuses growth in another metric.
- C3: `edit_runs.py` with `--prelude` at the merge base's `tools/ci/prelude.py` (no `defer_to`) reads `127 runs, 0 deferred; job-minutes 4438 -> 4438`.
- C7: `c7_replay.py --tree <merge-base worktree>` reads (a) 0 idled and (c) 0 runs. It reads (b) as `6 analyzed legs now skipped`, saving 59. That is the replay's own noise: those legs already stood in at the base, and a stand-in's duration varies above the sample's shortest one. So the net (b) below is 1159 - 59.
- Gate satisfiability: its null control is a job-level stand-down planted on `arch-instrument`. It is reported (`job-level if reads inputs.machinery`), and the gate over a run listing it skipped reads `FAIL tests / arch-instrument: SKIPPED (this run)`.
- harness_headers time: the same command at origin/main is the control (see `## Figures`).

## Figures

- C3 edit-run cost on a recorded sample: 349 ci.yml runs created 2026-11-04T22:25Z..2026-11-05T18:35Z, the card's window. `python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py dev/audit/harnesses/r10_ci_slim/sample.json` reads `127 runs, 117 deferred; job-minutes 4438 -> 660 (prelude 3769 -> 64, pr-contract before 77); saving 3778 of 28055 ci.yml job-minutes (13.5%)`. Rule: the harness docstring, where prelude.defer_to is replayed on the Actions state at each prelude's start and a deferred prelude is priced at the code runs' median prelude. It also prints the same predicate over code runs, as if they were edits: `156 runs, 20 deferred`, saving 13.
- C7 on the same sample: `python3 dev/audit/harnesses/r10_ci_slim/c7_replay.py dev/audit/harnesses/r10_ci_slim/sample.json` covers 121 pull_request code runs (27 diffs unreadable, left as run), 28055 job-minutes.
  - (b) 105 analyzed legs now skipped; CodeQL on PRs goes 2955 -> 1797, saving 1159 (4.1%).
  - (c) 3 runs whose delta had nothing that can change a kill; mutation-pins plus autofix go 2234 -> 1756, saving 479 (1.7%).
  - (a) 0 product-only runs. All 8 PRs reaching `custom_components/` also carried machinery files, which the script lists. The card's own condition holds: (a) pays after C1.
- Gate satisfiability: `python3 dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py` reads `required names whose job-level if reads machinery/pins: none (over 22 names)` and `idled-whole names inside REQUIRED: none`. The production-only, machinery-only and mixed diffs each read `gate PASS`, then `GATE SATISFIABLE`.
- harness_headers is not over its limit. Each run was `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`, timed by `date +%s`, in sequence on this box. The head 1066ed961 read 175 s wall, `ALL 112 HARNESS HEADER CHECKS PASSED`. origin/main 7d95405e3 read 180 s, 112 passed. The head again (null control) read 175 s, 112 passed. The frontier harness, the only one near a bound, read cpu=146.7 s at the head and 150.2 s at main, of its 480 s bound. The four new harnesses are not `live-header`, so harness_headers executes none of them: the 112 count is the same at both ends. CI's 185 s (job 127578956992) sits beside its own run's 180 s-class figures. Its one FAIL was the depth-seam check.
- Closure recording: `./tests/derive_closures.sh --single tests/harness_headers.py` read `done tests/harness_headers.py (exit 0)` and `updated 1 closure(s)` (401 files). `git diff --numstat 498f0cab9 1066ed961 -- tests/closures.json` reads `4 0`: the four `dev/audit/harnesses/r10_ci_slim/*.py` paths. It dropped none: the recorder kept the 3 files the committed closure listed and this run did not open.
- delivery-status grader. Two arms show this diff does not change what it grades:
  - `python -I -S tests/delivery_status.py --check` at merge base 7d95405e3 and at the head prints identical output with the per-row commit counts masked. Both exit 1 with 22 `overdue` lines, none naming #3230.
  - A YAML comparison of `jobs.delivery-status` in governance.yml at 7d95405e3 and at the head reads IDENTICAL. `git diff 7d95405e3 HEAD -- tests/delivery_status.py tests/layout.py` is empty.
- nightly-status grader. Two arms again:
  - `python -I -S tests/nightly_status.py` at both trees prints byte-identical output, `NIGHTLY FAILED: slow failed last night.` for scheduled run 41943946464 (2026-11-05T00:47Z, head 499162c on main).
  - `jobs.nightly-status` in tests.yml reads IDENTICAL, and `tests/nightly_status.py` is outside the diff.
  - The jobs this diff changes are `env-matrix` and `instrument-self-tests` (governance.yml), `arch-instrument`, `closures`, `mutation-autofix` and `mutation-pins` (tests.yml), and `gate`, `governance`, `prelude` and `tests` (ci.yml), all by the same YAML comparison.
- Self-tests at 4ae9f7596:
  - `python3 tests/ci_ratchet.py --self-test`: 65 checks, 0 failed.
  - `python3 tools/policy/budget_raise_gate.py --self-test`: 273, 0 at 4ae9f7596 (main's #3223 added two).
  - `python3 tools/ci/prelude.py --self-test`: 70, 0.
  - `python3 tools/ci/gate.py --self-test`: 57, 0.
  - `python3 tools/pr/codeql_scope.py --self-test`: 94, 0.
- Scope: `python3 tests/closure.py select --diff 785c2b604ba4c01891737a5285f4f4f49394c18f --workdir D` reads `MODE: FULL` (`.github/workflows/ci.yml changes the gate itself`), so the suite is CI's. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `git diff origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` is empty.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 785c2b604ba4c01891737a5285f4f4f49394c18f` at 4ae9f7596: Architecture score: dS +0.0000 NULL.

## Raise justification

This is an owner-approved LOOSENING, not a raise. tvofi's ruling in chat on 2026-11-05 accepted slip-study card C2 under CLAUDE.md rule 2: `critical_path_minutes` stays printed but stops failing `tests / ci-ratchet`. It overturns the 2026-10-31 ruling that added the band. CI's `budget-raise-gate` read this diff as `RAISE tests/ci_budgets.json: critical_path_minutes_band: removed at 1.3 (a removed cap is no cap)`. `python3 -I tools/policy/budget_raise_gate.py --base 785c2b604 --head 4ae9f7596 --pr 3230` reads `RAISE tests/ci_budgets.json: critical_path_minutes_band: 1.3 -> None`, `RESULT budget_raises=1 count` at the merged head. It is still the one raise.
Payments tried: none exists, because the change is the removal the ruling asks for. Re-recording the reference (a figure the hosted runners' draw moves) and widening the band are each the cost chain the card measured (#2839, #3045, #3180, #3189, #3201, #3228).
Architecture score: dS +0.0000 NULL

## Unpinned sites

none: no `custom_components/` site changes.

## Red checks

The concluded reds of the previous head 53e21a9b4. All 55 check runs fit on one page (`total_count` 55), with seven distinct red names. Each is listed with its cause from the log and its state at 4ae9f7596:
- `tests / fast (3.14)` (job 127578956992): `1 of 112 HARNESS HEADER CHECKS FAILED`, from `FAIL every inlined walk matches the canonical helper and no depth root remains [FAIL depth seams: ...parents[4]]`. A defect of this branch, fixed in 37474e097. 112 of 112 pass locally at the head. It was not the CPU limit: see the harness_headers figure. Cheaper detector: `tools/pr/prepr.sh` does not run harness_headers' depth-seam scan. It costs about 1 s as `python3 -c 'import harness_headers; harness_headers.depth_root_seams()'`, and it would have caught this before the handoff. `fixer.md` step 18 names the closures red a new harness predicts, but not this one. A change to that contract is policy and the owner's, so this seat names the gap here and does not edit it.
- `tests / closures` (job 127578956756): `INERT READS UNDER-APPROXIMATED` for the four new harnesses that `tests/harness_headers.py` opens. Fixed in 1066ed961 by `--single` re-recording on Linux. Cheaper detector: `tools/pr/ci_predict.py` predicts this red, which `prepr.sh` step 6d prints. Last round's handoff did not repair it.
- `tests / closures-autofix` (job 127589755936): this follows from the closures red, because the bot does not re-record an under-approximation. Fixed by the same commit, so no new detector is owed.
- `budget-raise-gate / budget-raise-gate` (jobs 127578682257, 127599140792): `RAISE tests/ci_budgets.json: critical_path_minutes_band: removed at 1.3 (a removed cap is no cap)`, `RESULT budget_raises=1 count`, `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. This is by design: it is the C2 loosening the owner approved in chat on 2026-11-05 (see `## Raise justification`). It stays red until tvofi's approving review at the head. No cheaper detector exists, because this gate is the detector.
- `governance / delivery-status` (job 127578682473): it lists overdue delivery rows of other PRs (#3174, #3091, #3089, #3192 among them) and prints `This check is NOT a required context and a red here blocks no merge`. It grades main's ledger, not this diff. The same grader reads identical output at the merge base and at the head, and its job definition and script are unchanged (`## Figures`). The owner of the cause is the orchestrator's delivery-row drain, not this PR.
- `tests / nightly-status` (job 127578682562): `NIGHTLY FAILED: slow failed last night` for scheduled run 41943946464 (2026-11-05T00:47Z, main at 499162c, before this branch). The same grader reads byte-identical output at base and head, and its job definition and script are unchanged. The cause is main's `slow` lane, outside this diff, and the nightly owner holds it. This seat dispatched no `gh workflow run nightly.yml`, because it may write no ref outside its return refs.
- `pr-contract / pr-contract` (jobs 127598648612, 127599692754) and `gate` (jobs 127599033118, 127600079786): last round's `## Red checks` named only a predicted budget-raise-gate. This body names every red above. `gate` follows the required reds: at this head it waits on `budget-raise-gate` (owner review) and on CI re-running `tests / fast` and `tests / closures` at 4ae9f7596.

## Forward-carry

none

## Friction

none
