Fix review: merge 6ef53d8a03cf86d506f749cf2769ca2f7a7aceb1

bus-nonce: 7778149c285cce63e18f7a619fe97814

Round 2 (this is the re-check of the round-1 block at 84a7c456f; not yet the fourth round). Measured head 6ef53d8a03cf86d506f749cf2769ca2f7a7aceb1. Its parents are 84a7c456f and the fixer's handoff 0440dfb4761f8dd11ab9f9c3791c4331b9238e0a. `git diff 0440dfb4 6ef53d8a` is empty, so the dispatch head's tree is the handoff's. The body's `## Head` names 0440dfb4. Merge base c679f4b69. origin/main has since moved to 5d75a576f. `git merge-tree --write-tree origin/main 6ef53d8a` gives rc=0, so there is no conflict. The role files are current: the three-dot `dev/governance/roles/` diff is empty.

## Round-1 block: resolved

The fixer dropped C7(c), and that settles the block. `prelude.pins_due`, the `pins` output, tests.yml's `pins` input and both `inputs.pins` conditions are gone.
- At the head, a `yaml.safe_load` comparison of `jobs.mutation`, `jobs.mutation-pins` and `jobs.mutation-autofix` against origin/main reads IDENTICAL for all three (`ev/head_tree.txt`).
- `git grep "pins_due|C7(c)|inputs.pins|outputs.pins"` names only the two harnesses.
- So there is no skip left that could survive where a previous head's pins never concluded. A replay at the head reads (c) 0 runs, saving 0, with 0 unreadable diffs (`ev/c7_replay_head.txt`).
- Round 2's rule is reproduced on the same sample. At 4ae9f7596 it reads 3 runs, 2234 -> 1756, saving 479. That is the round-1 figure, now the null control.
- The sound rule at 2c51d07b5 reads 0 runs and saving 0, with 39 runs whose previous head had not concluded (`ev/c7c_trees.txt`). So the body's claim that (c) saves 0 is honest, not deflated.
- Mutating the condition out: at 2c51d07b5, I replaced the `measured_at(...)` conjunct with `True`. The prelude self-test then reads 81 checks, 7 failed, the seven the body names (`ev/sound_rule_mutant.txt`).
- At the head the regression guard is `gate_satisfiable.gated_pins`. I added `&& inputs.machinery != 'false'` to the real job-level `if:` of `mutation-pins`, then of `mutation-autofix`. Each gives `GATE NOT SATISFIABLE`, rc=1. With `gated_pins` returning `[]`, its own null control fails, rc=1 (`ev/mutants.txt`).
- The `## Raise justification` and `## Owner constraint` sections now state C7(c) as dropped. Total (a)+(b)+(c) = 1191 of 28055 job-minutes (4.2%). Net of the base tree's 92-minute replay noise it is 1099, which I re-derived below.

## Owner constraint

For each change: the production path it touches, and the check that still guards it.
- **C2** (`tests/ci_ratchet.py`, `tests/ci_budgets.json`, `budget_raise_gate.py`)
  - Touches no production path. Every other ci_budgets row is still graded at zero tolerance.
  - The planted `script_runs_per_push +1` is GREW at both ends: grew=1 at the head, grew=2 at the base.
  - The recorded window reads grew=1 at the base and grew=0 at the head (`ev/c2_c3.txt`).
  - This is card C2 as written. It is the owner-approved loosening.
- **C3** (`prelude.defer_to`, `gate.deferring`, ci.yml `WORKSET`)
  - Skips no production unit. The code run's gate still judges every unit, and its `pr-contract` reads the latest body. Opus review dispatch is untouched.
  - This is card C3 option A. Live at this head: three code-run `pr-contract`s each succeeded, and the edit runs held no runner past their prelude.
- **C7(a)** (`prelude.machinery`)
  - Stands down only machinery lanes: arch-instrument, the closures recording, env-matrix and instrument-self-tests.
  - On a production diff these still run: `tests / fast`, `tests / mutation` with pins and autofix (byte-identical to main), goldens, features, CodeQL and review.
  - A push always runs the lanes. The self-test null control and a mutant pinning `machinery` to "false" kill it (1 of 62).
- **C7(b)** (`codeql_scope.ANALYZED_PREFIXES`)
  - Any PR reaching `custom_components/` or `.github/` analyzes on every leg, and every push to main analyzes. This is card C7 as written.
- **C7(c)**: dropped. Mutation testing on production changes is main's again.
- **Planted production defect** (`ev/planted_defect.txt`, `ev/planted_run.txt`): `total += v * seconds` -> `* seconds * 2` at `custom_components/heatpump_optimizer/open_meteo.py:156`.
  - At the head, `tests/solar_alignment.py` gives rc=1, 5 CHECK(S) FAILED. Unplanted it gives rc=0. Every CodeQL leg reads `analyze`, and `machinery` is False.
  - Null control at origin/main 5d75a576f: the same rc=1, 5 CHECK(S) FAILED (unplanted rc=0), with every leg `analyze`.
  - So production refusal is unchanged.
- The body states, per change, why the risk is acceptable, with a before and after. No cut goes beyond the approved cards. I found no measured large unforeseen risk.

## Findings

- `tools/ci/prelude.py:98` still adds `"before": ev.get("before")` to the context. That field was added for C7(c), and nothing reads it any more. It is dead and harmless. Carry: dismissed: one unused context key with no behaviour; fixer.md step 17 judges it too small to re-cut a round for
- `gate_satisfiable.gated_pins` catches only an `inputs.*` read in the pins jobs' `if:`. A skip expressed another way would pass it. The jobs are YAML-identical to main today, and any later edit to them is opus-reviewed. Carry: dismissed: instrument scope is round 2's failure shape, and the identical-to-main comparison is the stronger check at this head

## Evidence

- RESULT self-tests at the head (`ev/checks.txt`): ci_ratchet 65/0, budget_raise_gate 273/0, prelude 62/0, gate 57/0, codeql_scope 94/0. `r10_ci_gate_core.py mutants` reads `RESULT mutants=16 survivors=0`. `tests/structure.py` reads STRUCTURE RATCHET PASSED.
- RESULT gate satisfiability (`ev/checks.txt`): `GATE SATISFIABLE`, rc=0.
  - The production-only, machinery-only and mixed diffs each give gate PASS.
  - The job-level null control gives `FAIL tests / arch-instrument: SKIPPED (this run)`.
  - `pins jobs gated on a caller input: none`. No required name ends SKIPPED live either: every required unit at this head succeeded (`ev/checks_live.txt`).
- RESULT mutants re-run at the new head (`ev/mutants.txt`). Each was restored, and the tree was clean after each.
  - C2 REPORT_ONLY -> False: 2 failed.
  - C3 `bound = 0` -> no-op: 1 of 57.
  - C3 `defer_to` -> `if False:`: 3 of 62.
  - C7b skip -> `if False:`: 2 failed.
  - C7a `machinery` -> True: 3 of 62.
  - C7a output forced to "false": 1 of 62.
  - pins guard: two mutants, each GATE NOT SATISFIABLE.
  - My first two tests.yml mutants were vacuous (a duplicate `if:` key, which the job's own `if:` overrides). They are marked VACUOUS in the file and superseded by `mut2.py`.
- RESULT C7 (`ev/c7_replay_head.txt`, `ev/c7_replay_base.txt`): 121 pull_request code runs, 0 unreadable after fetching every PR head and the 26 missing shas.
  - (a): 0 idled, 4988 -> 4988.
  - (b): 150 legs, 2955 -> 1764, saving 1191 (4.2%).
  - (c): 0.
  - Together: 1191 (4.2%).
  - Base-tree control: (b) 51 legs, saving 92, so net 1099. Every figure matches the body.
- RESULT C3 (`ev/c2_c3.txt`): 127 runs, 117 deferred, 4438 -> 660 (saving 3778, 13.5%). The code-run control reads 156 runs, 20 deferred, saving 13. With the base prelude it reads 0 deferred, 4438 -> 4438. All match the body.
- Claim files, VERSION, the manifest, RELEASE_NOTES and `custom_components/` are untouched in the three-dot diff. The only budget-file change is `tests/ci_budgets.json`: the band is deleted and the reason is updated.
- Budget-raise gate (`ev/red_logs.txt`): CI runs main's gate, which prints `RAISE tests/ci_budgets.json: critical_path_minutes_band: removed at 1.3 (a removed cap is no cap)`, `RESULT budget_raises=1 count`, `REFUSED: no decisive review by tvofi`.
  - The head's own gate words the same single raise as the body quotes it, `1.3 -> None`.
  - It is the one C2 loosening the owner approved, under `## Raise justification`, and it waits on tvofi's review.
- CI at this head (`ev/classify.txt`, `ev/classify_log.txt`): `merge_train.py classify` rc=1, `RED 6ef53d8a03cf86d506f749cf2769ca2f7a7aceb1 pending: none red: gate`.
  - I read all three gate jobs' logs (127716027534, 127715091088, 127714135055, in `ev/gate_logs.txt`). Each logs one reason: `FAIL budget-raise-gate / budget-raise-gate: failure`.
  - In substance this head is APPROVAL-OWED, as round 1's was, although classify printed RED (rc=1), not rc=4. I judged it as GREEN on that basis.
- All 68 check runs were read (page 2 is empty, `ev/checks_live.txt`). Every required unit succeeded: fast, coverage, closures, arch-instrument, mutation, browser, typing, briefs, closure-scope, the three CodeQL legs, env-matrix, policy-docs, hassfest, validate, arch-score and three pr-contracts.
- `tests / nightly-status` is red: `NIGHTLY FAILED: slow failed 1 night ago`. That is main's slow lane, and this diff does not reach it.
- Rule 11: `pr-contract` job 127715567294 started at 04:40:05Z, after the last budget-raise-gate red concluded (04:39:34Z), and succeeded. The body names each red name at this head (budget-raise-gate, gate, nightly-status) and answers it.
- The body's figures were taken at 4056a2c5e/0440dfb4. I re-took every one at 6ef53d8a, whose tree equals 0440dfb4.
- Instruments: the group names no finder's harness (packet: "Finder's harness: none named"). The replays are the fixer's committed harnesses. The mutant drivers `ev/mut.py` and `ev/mut2.py` are mine.
