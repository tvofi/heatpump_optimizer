R10-CI-SLIM: two of the three slip-study cards the owner accepted on 2026-11-05 land here (C2, C3), and C7 lands as (a) and (b). (c) is dropped, because once its premise is checked its saving measures 0. This change does four things. Main's critical-path ratchet becomes report-only. Edit runs stop holding a runner while the code run works. Product pull requests stop paying for machinery lanes. Tools-only pull requests stop paying for PR CodeQL. No product file changes (`custom_components/` untouched).

**Repair round 3.** The review at 84a7c456f blocked C7(c). `prelude.pins_due` skipped `tests / mutation-pins` and `tests / mutation-autofix` on a non-product delta from `before`. The rule never checked that the previous head's pins had concluded. cancel-superseded cancels them, and in the PR's own sample that held in 3 of 3 skips.

The repair is in two commits:
- 2c51d07b5 adds the reviewer's sound rule. The delta counts only from a head whose code run concluded the measurement (`prelude.pins_measured`): `tests / mutation` success, or failure with every pins shard and the autofix succeeding. Anything else measures. Eleven self-tests were added. On round 2's rule, 7 of them fail: previous pins cancelled, autofix failed, pins still running, pins skipped on a failed mutation, one shard of several cancelled, an unreadable runs listing, and no run at the previous head.
- 4056a2c5e drops C7(c). With the premise checked, `c7_replay.py` reads (c) as 0 runs and a saving of 0. Even with the read moved to the latest moment it could happen (each run's prelude end), the saving is still 0. One reason is that the autofix's own pin commit lands while that autofix is still running, so the previous head is never concluded at the next prelude.

The card asked for a measurement guaranteed at review-ready, and a saving that is not real is not kept. So `prelude.pins_due`, the `pins` output, tests.yml's `pins` input and both `inputs.pins` job conditions are removed. The `mutation`, `mutation-pins` and `mutation-autofix` jobs are YAML-identical to main's again. `gate_satisfiable.py` now refuses any caller input in either pins job's `if:`, and it reads `GATE NOT SATISFIABLE` on round 2's workflows.

Alternatives not taken:
- Keeping 2c51d07b5's rule: it is sound, but it costs one runs read and one jobs read per synchronize for a measured saving of 0. Per fixer.md step 17, the simpler tree wins.
- Taking the delta from the last concluded head, the reviewer's equivalent form: it walks history for the same 0 saving.

**C2. `critical_path_minutes` is report-only.** `tests/ci_ratchet.py` adds a `REPORT_ONLY` set holding that one metric. `compare` prints it as `info critical_path_minutes: X (reference R; report-only, never graded)` and never counts it. Every other `ci_budgets.json` row is still graded at zero tolerance. The band row `critical_path_minutes_band` and `BAND_KEYS` are deleted. The recorded value stays as the reference that `orchestrator_tick.py`'s ETA reads. `tools/policy/budget_raise_gate.py` types that reference `free`.

**C3 (option A). An edit run holds no runner.** `prelude.defer_to` finds an unfinished code run at the same head and PR whose `pr-contract / pr-contract` has not started. When it finds one, the edit run's workset is `arch-score budget-raise-gate` and the run does not wait. `pr-contract` reads the body off the API when it starts, after every unit, so the code run's gate judges the LATEST body. The edit run's gate takes the prelude's workset (`WORKSET`, `gate.deferring`), and a unit skipped in a deferring run is no source. If `pr-contract` has started, the code run is finished, or there is no code run, today's wait applies. A deferral read in a race is a false RED, which `gate-sweep.yml` re-judges. It is never a false green.

**C7.** (a) `prelude.machinery`: a pull request whose every changed file is product stands down three lanes at step level, each reporting success: `tests / arch-instrument`, the `tests / closures` recording and `governance / env-matrix`. `governance / instrument-self-tests`, which is not required, skips whole. Product means `custom_components/`, `docs/`, `README.md`, a script that `tests/closures.json` measures, `tests/golden/` or `tests/mutation_ledger/`. Any other file runs the lanes, and so does every push. (b) `codeql_scope.decide` skips every leg of a pull request with nothing under `custom_components/` or `.github/`. The stand-in reports success, and a push to main always analyzes.

**Owner constraint (tvofi, 2026-11-05), per change.** For each change: the check that still guards each production path, and why the risk to production quality and to future throughput is acceptable.
- C2: no production path. `tests / ci-ratchet` still grades every other CI metric at zero tolerance (a planted `script_runs_per_push` 54 -> 55 is GREW at the head). The accepted risk is that a slower critical path goes ungraded. It is still printed and still feeds the ETA. Throughput gain: no more re-record and band-widening PRs (#2839, #3045, #3180, #3189, #3201, #3228). Before: grew=1. After: grew=0 (`## Null control`).
- C3: no check is skipped. The code run's gate still judges every production unit, and its `pr-contract` reads the latest body. Opus review dispatch is not touched. A race gives a false red, never a false green. Before: 4438 edit-run job-minutes. After: 660.
- C7(a): the idled lanes measure machinery only. On a diff that touches `custom_components/`, these still run: `tests / fast`, `tests / mutation` with its pins and autofix, goldens, features, CodeQL and review. `gate_satisfiable.py`'s production-only case reads every CodeQL leg as `analyze`. Before: 4988 job-minutes. After: 4988 (0 runs idled in the sample, so it pays after C1, as the card says).
- C7(b): CodeQL still analyzes every pull request reaching `custom_components/` or `.github/`, and every push to main. It skips only tools/dev-only pull requests, which main's push analysis covers. Before: 2955 job-minutes. After: 1764.
- C7(c) dropped: mutation testing on production changes is main's again, byte for byte (YAML comparison, `## Figures`). Throughput risk removed: the skip that left `mutation` red with no pins table at a head the seat could not re-trigger is gone.

Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` read `OK python3 is /opt/hpo/venv-ci/bin/python3`. No golden ran: the scope is MODE: FULL, so the goldens are CI's.

## Head

0440dfb4761f8dd11ab9f9c3791c4331b9238e0a. It is the PR head 84a7c456f2a682f76e285921c26d4b05044391e6, plus four commits in order:
- origin/main b0135d07d21c44ea7a98ca91b258aaf1beb0658f merged as 2ed14c5eb, with no conflict;
- 2c51d07b5, the sound C7(c) rule;
- 4056a2c5e, which drops C7(c);
- origin/main c679f4b692f483959769ec5b5147aa4d624c45f4 merged as 0440dfb47, with no conflict.

The figures below were taken at 4056a2c5e on merge base b0135d07d, unless a line names another tree. The main delta b0135d07d..c679f4b69 touches only `dev/programme/delivery/3214.md` and `dev/programme/triage/s6-batch124.md`, and no figure reads either file (`git diff --name-only b0135d07d c679f4b69` lists those two). At 0440dfb47 these were re-taken: the five self-tests (same counts), `tests/structure.py` (PASSED) and `tools/pr/prepr.sh` with this body.

## Mutation proof

Each mutant replaced one line in place, ran the named check and was restored (`git diff --quiet` held after each).
- Round 3 guard: `gated_pins` returns `[]` (in `dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py`). `python3 dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py` reads `null control: round 2's pins gate planted -> []`, `GATE NOT SATISFIABLE`, rc=1.
- Round 3 rule, the failing-first test at 2c51d07b5: the `measured_at(...)` conjunct was replaced by `True`, which is round 2's rule. `python3 -I tools/ci/prelude.py --self-test` read `81 checks, 7 failed`, the seven listed above.
- C7(a): `machinery` returns `True`. The prelude self-test fails 3 of 62: `C7a: a product-only diff (package + a measured script) idles the machinery lanes`, `C7a: ... and so do its docs, golden fixtures and ledger pins` and `C7a: the prelude's output on a product-only pull request`.
- C3: `if defer_to(ctx, pr, get) is not None:` -> `if False:`. The prelude self-test fails 3 of 62: `C3: beside a code run in its units, the edit run exits at once without pr-contract`, `C3: beside a queued code run (nothing listed), it exits at once` and `C3: a queued pr-contract has not read the body: exits at once`.
- Gate core: `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants` reads `RESULT mutants=16 survivors=0`.
- C2, C3 (gate.py) and C7(b) mutants are those the review re-ran at 84a7c456f (C2 2 of 65, C3 1 of 57, C7b 2 of 94). `git diff 84a7c456f HEAD -- tests/ci_ratchet.py tools/ci/gate.py tools/pr/codeql_scope.py` is empty.

## Null control

- C2: `python3 dev/audit/harnesses/r10_ci_slim/c2_replay.py <tree> dev/audit/harnesses/r10_hotfix_ci_critpath_4/runs.json`.
  - At merge base b0135d07d: `recorded window: grew=1; GREW critical_path_minutes: 29.067 (budget 23.574, band 1.3)`.
  - At the head: `grew=0; info critical_path_minutes: 29.067 (reference 23.574; report-only, never graded)`.
  - The planted `script_runs_per_push +1` is GREW at both ends (grew=2 at the base, grew=1 at the head).
- C3: `edit_runs.py` with `--prelude <merge-base>/tools/ci/prelude.py` reads `127 runs, 0 deferred; job-minutes 4438 -> 4438`.
- C7: `c7_replay.py --tree <merge-base worktree>` reads (a) 0 idled and (c) 0 runs. It reads (b) as `51 analyzed legs now skipped`, saving 92. That is the replay's noise: those legs already stood in at the base, and a stand-in runs above the sample's shortest one. So the net (b) is 1191 - 92 = 1099 job-minutes.
- C7(c) rule: the round-2 tree 4ae9f7596 reads `3 runs ... 2234 -> 1756 (saving 479)`, which is the review's figure. 2c51d07b5 reads `0 runs ... saving 0` with `39` runs whose previous head had not concluded.
- Pins guard: at the head, `pins jobs gated on a caller input: none`. With the workflows of 2c51d07b5 it reads `tests / mutation-pins: job-level if reads inputs.pins` and `tests / mutation-autofix: job-level if reads inputs.pins`, then `GATE NOT SATISFIABLE`.

## Figures

- Sample: `dev/audit/harnesses/r10_ci_slim/sample.json`, 349 ci.yml runs created 2026-11-04T22:25Z..2026-11-05T18:35Z, 28055 job-minutes. Every PR head commit was fetched first (`git fetch origin '+refs/pull/*/head:...'`, plus each sha still missing).
- C7: `python3 dev/audit/harnesses/r10_ci_slim/c7_replay.py dev/audit/harnesses/r10_ci_slim/sample.json` reads `121 pull_request code runs (0 diffs unreadable, left as run)`. Rule: the harness docstring.
  - (a) `0 product-only runs idled: 4988 -> 4988`. All 8 PRs reaching `custom_components/` also carried machinery files, which the script lists.
  - (b) `150 analyzed legs now skipped: 2955 -> 1764 job-minutes (saving 1191, 4.2% of the sample)`. This retakes round 2's figure (105 legs, 1159), which had 27 diffs unreadable.
  - (c) `0 runs ... 2234 -> 2234 (saving 0, 0.0%)`.
  - together: `saving 1191 of 28055 job-minutes (4.2%)`, or 1099 net of the base's noise.
- C7(c) with the read moved to each run's prelude end, the latest moment production could read it: a probe environment switch on c7_replay.py at 2c51d07b5, not kept in the tree. It read `(c) ... 0 runs ... saving 0`, with 33 previous heads unconcluded.
- C3: `python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py dev/audit/harnesses/r10_ci_slim/sample.json` reads `127 runs, 117 deferred; job-minutes 4438 -> 660 (prelude 3769 -> 64, pr-contract before 77); saving 3778 of 28055 ci.yml job-minutes (13.5%)`. Its code-run control reads `156 runs, 20 deferred`, saving 13.
- Gate satisfiability: `python3 dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py` reads:
  - `required names whose job-level if reads machinery: none (over 22 names)`;
  - `idled-whole names inside REQUIRED: none`;
  - production-only, machinery-only and mixed each `gate PASS`;
  - the job-level null control `FAIL tests / arch-instrument: SKIPPED (this run)`;
  - `pins jobs gated on a caller input: none`;
  - `GATE SATISFIABLE`.
- Pins jobs against main: a `yaml.safe_load` comparison of `jobs.mutation`, `jobs.mutation-pins` and `jobs.mutation-autofix` in tests.yml at b0135d07d and at the head reads `IDENTICAL` for each. `git grep -n "pins_due\|C7(c)\|inputs.pins\|outputs.pins"` names only `c7_replay.py`, which replays any tree that has the rule.
- Self-tests at the head:
  - `tests/ci_ratchet.py` 65/0;
  - `tools/policy/budget_raise_gate.py` 273/0;
  - `tools/ci/prelude.py` 62/0 (round 2's 70, less its 9 C7(c) checks, plus the merge of main);
  - `tools/ci/gate.py` 57/0;
  - `tools/pr/codeql_scope.py` 94/0.
- Scope: `python3 tests/closure.py select --diff b0135d07d --workdir D` reads `MODE: FULL -- every test script runs, nothing is scoped out`, so the suite is CI's.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `git diff b0135d07d...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty.
- `bash tools/pr/prepr.sh` on the committed 4056a2c5e reads `PRE-PR: 4056a2c5e21f9cef42974437c51d7e4c62826e74 ... rc=0`. Its body check (`--body-check PR-BODY.md`) reads `PR-BODY: 0 error(s)` and `CARRY-AUDIT: 0 finding item(s)`. main then moved to c679f4b69. It was merged, and prepr.sh was re-run with this body at the head (`## Head`).

## Architecture score

`python3 tools/audit/archscore/score.py --diff b0135d07d` at 4056a2c5e: Architecture score: dS +0.0000 NULL.

## Raise justification

This is an owner-approved LOOSENING, not a raise. tvofi's ruling in chat on 2026-11-05 accepted slip-study card C2 under CLAUDE.md rule 2: `critical_path_minutes` stays printed but stops failing `tests / ci-ratchet`. It overturns the 2026-10-31 ruling that added the band. `python3 -I tools/policy/budget_raise_gate.py --base b0135d07d --head HEAD --pr 3230` reads `RAISE tests/ci_budgets.json: critical_path_minutes_band: 1.3 -> None`, `RESULT budget_raises=1 count`, `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. It is still the one raise.
Payments tried: none exists, because the change is the removal the ruling asks for. Re-recording the reference (a figure the hosted runners' draw moves) and widening the band are each the cost chain the card measured (#2839, #3045, #3180, #3189, #3201, #3228).
Architecture score: dS +0.0000 NULL

## Unpinned sites

none: no `custom_components/` site changes.

## Red checks

The concluded reds of the PR head 84a7c456f2a682f76e285921c26d4b05044391e6. All 55 check runs fit on one page (`total_count` 55, per_page 100). The new head 4056a2c5e has no CI yet: the orchestrator moves the PR head.
- `budget-raise-gate / budget-raise-gate` (jobs 127655012356, 127667935713): the C2 loosening. Reproduced locally at 4056a2c5e as `RAISE tests/ci_budgets.json: critical_path_minutes_band: 1.3 -> None`, `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. This is by design: it stays red until tvofi's approving review at the head. No cheaper detector exists, because this gate is the detector.
- `gate` (jobs 127667663510, 127668840956): it follows the required budget-raise-gate red. The review read its log as `FAIL budget-raise-gate / budget-raise-gate: failure (run 42145816190)`, its one reason.
- `tests / nightly-status` (job 127655012336): `NIGHTLY FAILED: slow failed 1 night ago`, scheduled run 41943946464, 2026-11-05T00:47Z, head 499162c on main (`python -I -S tests/nightly_status.py`, local, same output class). The cause is main's `slow` lane, outside this diff, and the nightly owner holds it. The job and `tests/nightly_status.py` are outside this diff. This seat dispatched no nightly, because it may write no ref outside its return refs.

An earlier commit of this branch was also red on one check, `prepr.sh`'s ancestry read:
- `governance / delivery-status` (job 127578682473, at the round-1 head 53e21a9b4). It listed overdue delivery rows of other PRs (#3174, #3091, #3089, #3192 among them) and printed `This check is NOT a required context`. It grades main's ledger, not this diff.
- At 84a7c456f the same check is green (job 127655012666).
- At this head, `python -I -S tests/delivery_status.py --check` reads `DELIVERY STATUS OK — 46 rowed, 5 pending, 0 overdue (overdue at 12 commits)`, rc=0.
- A `yaml.safe_load` comparison of `jobs.delivery-status` in governance.yml at origin/main c679f4b69 and at this head reads IDENTICAL.
- The cause was the orchestrator's delivery-row drain on main, now drained. No cheaper detector is owed: the grader runs in about 1 s and was run here.

No other check at that head is red. Every required unit succeeded, and `pr-contract` was green.

## Forward-carry

none

## Friction

none
