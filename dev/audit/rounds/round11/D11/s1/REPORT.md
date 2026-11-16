# D11-s1, round 11: the D11.M1 mechanism inventory

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B6 (shared, load1 between 4 and 10).
Cells: `python3 tools/audit/check_scopes.py --repo . --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 --seat D11-s1`
prints 1387 lines, every one under step M1. This seat examined all 1387. Redispatched items C1 and C2 were both examined.

## Method
1. `inventory.py` classifies every cell: its role, where it runs, its control and whether it refuses. The result is `inventory.tsv`, one row per cell. Its control column is a screen. The CI-required rows and every row named in the C2 hand-over were then read and driven by hand.
2. API rows: the three active rulesets were read live (snapshots in `api/`). `required_map.py` resolves the ruleset's required context `gate` and each of the 21 names `gate.py:gate_required()` can require to a workflow job.
3. Controls were driven, not read:
   - `policy_lint_mutants.mjs`, plus `class_controls.mjs` for the two per-file classes it does not cover.
   - Each hook's `--self-test`, `policy_lint --hooks` and `selftest_wiring.py`.
   - `brief_lint.mjs` in a clean baseline worktree.
   - `structure_control.py`, `claim_control.py`, `rules_sync_control.py`, `stop_hook_reach.py`, `ruleset_reach.mjs` and `required_sites_reach.mjs`.
   - `seat_selftest_sweep.py`, which runs all 113 `tools/audit/seat` scripts under git/gh/curl/sleep shims, with every github.com URL rewritten to a dead path.
   - `meter_boundary.py`.

## Mechanism inventory
| row | refuses | runs | positive control | uncovered |
|---|---|---|---|---|
| ruleset 23698884 main-protect-checks | a merge without 1 approval, a code-owner review and a green `gate` | main | `counts.mjs` drift against `required-contexts.json` | DeployKey and App 5094721 bypass it `always`; `dismiss_stale_reviews_on_push=false` (owner-declined) |
| ruleset 22628467 main-protect | deleting or force-pushing main | main | none (D11-s1-02) | any change to it |
| ruleset 23937752 release-tags-protect | creating, updating or deleting a `v*` tag | tags | none (D11-s1-02) | any change to it |
| `gate` -> ci.yml `gate` -> `tools/ci/gate.py` | a red or absent required unit (16-19 per event class) | PR, push, merge_group, dispatch | `gate.py --self-test` | ci.yml is the PR's own copy (owner-owned) |
| `policy_lint.mjs`, 19 classes | policy rot and the PR body contract | `policy-docs` and `pr-contract` (required) | mutants: 25 arms PIN; the acceptance fixtures | `citations` and `no-gh` have no mutant arm, but the acceptance refuses both when emptied |
| `brief_lint.mjs` | an unresolvable citation | `tests / briefs` (required) | embedded fixture arms on every run | no `--self-test` by that name |
| `tests/structure.py` | structural growth | `tests / fast` and `arch-instrument`, from the PR's copy | `self_check`; `structure_control.py` 15/15 | the meter is neither owned nor pinned (D11-s1-05) |
| claim files, `env_drift.py` claimnotes driver | a bad drift claim | fast; the merge driver | `claim_merge_mutants.py` | that control is dead, 0/16 (D11-s1-04) |
| `rules_sync.mjs --check` | drift in the generated rules | `policy-docs` (required) | none; `--self-test` rewrites the files (D11-s1-03) | the refusal |
| `tools/pr/prepr.sh` | the pre-PR gate | seat; self-test in `instrument-self-tests` | `--self-test` | its self-test is report-only |
| `tools/plan/` | projection inputs | seat | `--self-test` | `durations.json` |
| `tools/audit/seat` (113 scripts, merge train included) | admission, approval at head, caps | seat and beat jobs | `--self-test` | 18 give no self-test verdict; `wt_sync.sh` pushes (D11-s1-06) |
| the 4 wired hooks | risky shell, policy edits, a red end of turn | sessions | `--self-test` 46/22/24/29 passed | the Stop hook misses 2 of 65 corpus files (D11-s1-01) |
| `instrument-self-tests` | each instrument's self-test | PR (scoped), push | `selftest_wiring --check` 144/144 | not a required name (by design, decision 0013) |

The per-file table is `inventory.tsv`.

## Findings
- D11-s1-01, low: the Stop hook misses `AGENTS.md` and `dev/audit/README.md`. `stop_hook_reach.py` reads missed=2; under `--perturb` it reads 0.
- D11-s1-02, medium: the ruleset drift detector reads 1 of 3 rulesets. `ruleset_reach.mjs` reads unmonitored=2; under `--perturb` it reads 1.
- D11-s1-03, medium: `rules_sync --check` has no control, and `--self-test` rewrites the drifted files. Control red on drift reads 0; under `--perturb` it reads 1.
- D11-s1-04, medium: the claim merge driver's mutation control is dead, reaching 0 of 16 mutants; under `--perturb` it reaches 16.
- D11-s1-05, medium: `tests/structure.py` is unowned and unpinned in the required jobs that run it. `meter_boundary.py` reads 1; under `--perturb` it reads 0.
- D11-s1-06, medium: `wt_sync.sh --self-test` force-pushes from the real repository. Real-repo writes read 1, and 18 scripts give no self-test verdict; under `--perturb` the writes read 0.

## Non-findings, harnesses, leads
These are listed in REPORT.json.

## Unfinished
None. `prepr.sh --self-test` was not driven separately; its CI step is credited. An earlier unshimmed self-test run in this session was stopped after a mutant driver edited a production file in this seat's private worktree. The file was restored and every process was killed by PID.

## Exposure
- The GitHub API rulesets endpoints, unauthenticated.
- Comments in `counts.mjs` and `field_coverage.mjs` naming round-9 D11 ids.
- One grep line each from `dev/audit/rca/R9-I3.md` and `dev/programme/plan-2026-09-open-issues.md`.
- This seat's own checkpointed findings 01-04 from this round, written before a box restart, all re-run.
