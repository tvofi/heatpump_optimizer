R10-CI-SLIM: three cards of the slip study the owner accepted on 2026-11-05 (C2, C3, C7). This change makes main's critical-path ratchet report-only, stops edit runs holding a runner while the code run works, and stops product pull requests paying for machinery lanes, PR CodeQL and repeated pin measurement. No product file changes (`custom_components/` untouched).

**Hot-file order:** this group (R10-CI-SLIM) lands BEFORE R10-PROCESS-SLIM. That group edits `.github/workflows/governance.yml` and `tools/audit/seat/bus.sh` too. This change touches governance.yml's `on.workflow_call.inputs`, `instrument-self-tests` and `env-matrix`. The group brief already states that order, and card C7 already makes (a)'s saving wait for C1, so neither is a new carry.

**C2. `critical_path_minutes` is report-only.** `tests/ci_ratchet.py` adds a `REPORT_ONLY` set holding that one metric. `compare` prints it as `info critical_path_minutes: X (reference R; report-only, never graded)` and never counts it. Every other `ci_budgets.json` row stays graded at zero tolerance. The band machinery (`BAND_KEYS`, the band row `critical_path_minutes_band`) is deleted. The recorded value stays as the reference `orchestrator_tick.py`'s ETA check reads, and is not re-recorded. `tools/policy/budget_raise_gate.py` types that reference `free` and lets the retired band fall to `frozen`.

**C3 (option A). An edit run holds no runner.** `prelude.defer_to` checks for an unfinished code run at the same head and PR whose `pr-contract / pr-contract` has not started. When one exists, the edit run's workset is `arch-score budget-raise-gate`, with no wait. Those two judge the live body at once. `pr-contract` reads the body off the API when it starts, after every unit, so it is the code run's, and that run's gate judges the LATEST body. The edit run's gate gets the prelude's workset (`WORKSET` env, `gate.deferring`) and publishes its deferral at once, with no wait. It is never a source for a unit it skipped: a unit whose every job is `skipped` in another run is no source. A started `pr-contract`, a finished code run or no code run keeps today's wait. Why the deferring gate is red, not skipped: a skipped required check passes. Every deferral is decided while the code run's gate is not yet listed, so that gate is the later `gate` check at the head. A deferral read in a race is a false RED, which `gate-sweep.yml` re-judges. It is never a false green.

**C7.** (a) `prelude.machinery` reads the changed list. When every file is product (`custom_components/`, `docs/`, `README.md`, a script `tests/closures.json` measures, `tests/golden/`, `tests/mutation_ledger/`), these stand down: `tests / arch-instrument`, the `tests / closures` recording and its check, and `governance / env-matrix`. Each stands down at the step level and reports success, so no required name ends SKIPPED. `governance / instrument-self-tests`, which is not required, skips whole. tools/, .github/, dev/, policy files, tests infrastructure and unknown root files run them, and every push runs them. The closures lane keeps its `no-copies` scan. (b) `codeql_scope.decide` skips every leg of a pull request with nothing under `custom_components/` or `.github/`, and the codeql_scope.py program itself counts as `.github/` does. The stand-in reports success, and a push to main always analyzes. (c) `prelude.pins_due` gates `tests / mutation-pins` and `tests / mutation-autofix`: they run only when this push's own delta (`before...head`) touches the package, a golden fixture or a measured script. So a ledger-only pin commit or a tooling fix-up does not re-measure the survivors of the head before. An opened or reopened PR, or an unreadable delta, measures. A pull request's base copy of `prelude.py` has neither output, so both read as run on this PR's own CI.

Alternatives not taken: (C3, B) dropping `edited` and leaving body edits to the sweep was the card's other option; the owner picked A. (C7a) moving the stand-down to job level skips the runner start too, but a skipped required job is a SKIPPED source: `gate_satisfiable.py`'s null control below. (C7a) putting the rule in `gate.py` as a fifth event class: two deciders for one fact. (C2) deleting the whole critical-path derivation (window_work_minutes, the runner probe): about 500 lines across tests.yml, entities.py and four harnesses that replay it. The card asks for the metric to stay printed.

Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` read OK. numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`. No golden ran: the scope is MODE: FULL, CI's.

## Head

fee2c572fe4d9196addfb4458b8988eea78aef71: the measured code head 7cb0eb4306f44b1d2271953130dc54aacfe340a7 with origin/main 203b4dfc728af52a3607ca55da5fc8f9d4922cf5 merged at 2026-11-05T22:04Z. Main's delta is #3229 (`tools/audit/seat/bus.sh`, one delivery row) and touches no file of this diff. The figures below were taken at 7cb0eb430 on merge base 2dc960f4a, and `tools/pr/prepr.sh` ran clean at both heads.

## Mutation proof

Each mutant replaced a production line in place, ran the named self-test and was restored, through out-of-tree drivers; each mutant line is quoted here.
- C2: `if key in REPORT_ONLY:` -> `if False:` in `tests/ci_ratchet.py` `compare`. `python3 tests/ci_ratchet.py --self-test`: 2 of 65 FAIL, `critical_path_minutes growth (23.574 -> 99.0) is printed, never graded -- grew 1` and `both planted: only the graded row counts -- grew 2`.
- C3 M1: `bound = 0` (gate.judge, deferring) -> `pass`. `python3 tools/ci/gate.py --self-test`: 1 of 57 FAIL, `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner` (naps 60, 60, ...).
- C3 M2: `continue` (a deferred unit is no source) -> `pass`. 1 of 57 FAIL, `C3: a unit a run deferred is no source even under its full job name (skipped)`: got `FAIL pr-contract / pr-contract: SKIPPED (run 101)`.
- C3 M3: own-workset eligibility -> title workset. 2 of 57 FAIL, `C3: the deferred gate re-judged once the code run ended (green|its pr-contract red)`: got `ABSENT (this run)`.
- C3 M4: `if defer_to(...) is not None:` -> `if False:`. `python3 tools/ci/prelude.py --self-test`: 3 FAIL, `C3: beside a code run in its units / a queued code run / a queued pr-contract ... exits at once`: got `UNBOUNDED: waited past the frames`.
- C3 M5: the `STARTED` predicate -> `if True:`. 1 FAIL, `C3: beside a started pr-contract ... the edit run waits and owns pr-contract`.
- C7 M6: `if not any(f.startswith(ANALYZED_PREFIXES) ...)` -> `if False:`. `python3 tools/pr/codeql_scope.py --self-test`: 2 of 94 FAIL, `C7b: a tools/ .py diff skips python on a pull request` and `a roster PR skips javascript-typescript`.
- C7 M7: `machinery` -> `return True`. 2 FAIL, `C7a: a product-only diff ... idles the machinery lanes` and `C7a: the prelude's output on a product-only pull request`.
- C7 M8: `pins_due` -> `return True`. 2 FAIL, `C7c: a pin commit's delta (the ledger only) measures nothing again` and `C7c: a tooling or body-record delta measures nothing again`.
- Gate core: `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants` reads `RESULT mutants=16 survivors=0` at the head. M11's pattern follows gate.py's split source-eligibility line. Before the port it read `NOT RUN, pattern found 0 times` (survivors=1).

## Null control

- C2: `python3 dev/audit/harnesses/r10_ci_slim/c2_replay.py <merge-base worktree> dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json` at 2dc960f4a: the recorded window reads `GREW critical_path_minutes: 29.067 (budget 23.574, band 1.3)`, grew=1. At the head: `info ... 29.067 (reference 23.574; report-only, never graded)`, grew=0. The planted `script_runs_per_push` 54 -> 55 is GREW at both ends (grew=2 base, grew=1 head), so the ratchet still refuses a growth in another metric.
- C3: `edit_runs.py` with `--prelude` at the merge base's `tools/ci/prelude.py` (no `defer_to`) reads `127 runs, 0 deferred; job-minutes 4438 -> 4438`.
- C7: `c7_replay.py --tree <merge-base worktree>` reads (a) 0 idled, (c) 0 runs. It reads (b) as `51 analyzed legs now skipped`, saving 92. That is the replay's own noise: those legs already stood in at the base, and a stand-in's duration varies above the sample's shortest one. Net (b) below is 1191 - 92.
- Gate satisfiability: `gate_satisfiable.py` at 2dc960f4a, f76f55901 (C2), fa921fd59 (C3) and 63b5d2560 (C7) each read `GATE SATISFIABLE`. Its null control: a job-level stand-down planted on `arch-instrument` is reported (`job-level if reads inputs.machinery`), and the gate over a run listing it skipped reads `FAIL tests / arch-instrument: SKIPPED (this run)`.

## Figures

- C3 edit-run cost on a recorded sample (349 ci.yml runs created 2026-11-04T22:25Z..2026-11-05T18:35Z, the card's window): `python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py dev/audit/harnesses/r10_ci_slim/sample.json`: `127 runs, 117 deferred; job-minutes 4438 -> 660 (prelude 3769 -> 64, pr-contract before 77); saving 3778 of 28055 ci.yml job-minutes (13.5%)`. Rule: the harness docstring (prelude.defer_to replayed on the Actions state at each prelude's start; a deferred prelude priced at the code runs' median prelude). It prints, without asserting, the same predicate over code runs as if they were edits: 20 of 156, saving 13 (code runs re-run at one head).
- C3, a body edited after the code run's gate passed is still judged: gate self-test `C3: a body edited after the code run's gate passed is still judged (this run's own pr-contract)` reads `FAIL pr-contract / pr-contract: failure (this run)`. Prelude self-test `C3: beside a finished code run, the full edit workset and no wait`.
- C7 on the same sample: `python3 dev/audit/harnesses/r10_ci_slim/c7_replay.py dev/audit/harnesses/r10_ci_slim/sample.json`: 121 pull_request code runs, 28055 job-minutes in all.
  - (b) 150 analyzed legs now skipped, CodeQL on PRs 2955 -> 1764, saving 1191 (4.2%).
  - (c) 3 runs whose delta had nothing that can change a kill, mutation-pins plus autofix 2234 -> 1756, saving 479 (1.7%).
  - (a) 0 product-only runs: all 8 PRs reaching `custom_components/` also carried dev/audit, dev/programme, tests/closures.json, tests/structure_budgets.json, tests/seam_map.json, tools/ or .github/ files (the script prints the list). The card's own condition holds: (a) pays after C1.
- Gate satisfiability: `python3 dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py`: `required names whose job-level if reads machinery/pins: none (over 22 names)`, `idled-whole names inside REQUIRED: none`. production-only, machinery-only and mixed diffs each read `gate PASS`, then `GATE SATISFIABLE`.
- Self-tests at the head: `python3 tests/ci_ratchet.py --self-test` 65 checks, 0 failed. `python3 tools/policy/budget_raise_gate.py --self-test` 271, 0. `python3 tools/ci/prelude.py --self-test` 70, 0. `python3 tools/ci/gate.py --self-test` 57, 0. `python3 tools/pr/codeql_scope.py --self-test` 94, 0. `python3 dev/audit/harnesses/r10_ci_gate_core.py replay` and `sim`: output IDENTICAL to 1371a0a6's recordings.
- Scope: `python3 tests/closure.py select --diff 2dc960f4a92b1ebf56ed5aa33f55400d8e269a10 --workdir D` reads `MODE: FULL` (`.github/workflows/ci.yml changes the gate itself`). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `PYTHONPATH=tests/hastub python3 tests/entities.py` read 1 of 2632 failed before the fix to its governance `with:` null control, which now names `machinery`. That one check re-derived: `[] ['base', 'machinery']`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 2dc960f4a92b1ebf56ed5aa33f55400d8e269a10`: Architecture score: dS +0.0000 NULL.

## Raise justification

An owner-approved LOOSENING, not a raise. tvofi's ruling in chat on 2026-11-05 accepted slip-study card C2 under CLAUDE.md rule 2: `critical_path_minutes` stays printed but stops failing `tests / ci-ratchet`. It overturns the 2026-10-31 ruling that added the band. `budget_raise_gate.file_raises` reads this diff as `tests/ci_budgets.json: critical_path_minutes_band: 1.3 -> None (a pinned value the gate cannot sign as routine)`.
Payments tried: none exists, because the change is the removal the ruling asks for. Re-recording the reference (a figure the hosted runners' draw moves) and widening the band are each the cost chain the card measured (#2839, #3045, #3180, #3189, #3201, #3228).
Architecture score: dS +0.0000 NULL

## Unpinned sites

none: no `custom_components/` site changes.

## Red checks

- `budget-raise-gate` (predicted by `tools/pr/ci_predict.py`; no check has run at this head, as no pull request exists): `tests/ci_budgets.json: critical_path_minutes_band: removed at 1.3 (a removed cap is no cap)`. It is red by design until tvofi's approving review at the head, which is the owner approval C2's ruling gives (see `## Raise justification`). No cheaper detector exists: this gate is the detector, and the red is the signal it exists to give.

## Forward-carry

none

## Friction

none
