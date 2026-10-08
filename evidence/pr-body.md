Every throwaway git repository a tracked script builds now goes through one shared helper, which turns git's auto-maintenance off. This follows the owner's decision (tvofi, 2026-10-08) to put a helper at every temp-repository site rather than a CI-only workflow `env:`.

#2051 fixed stamp.py's two repositories; the cause is in `dev/audit/rca/R9-RCA-stamp-race.md`. Git 2.54 and later detaches a geometric repack after a commit or merge, and the repack can still be writing into `.git/objects/pack` while the caller removes the temporary directory. The #2051 review then found that its env-only fix can be undone: git reads `GIT_CONFIG_PARAMETERS` after `GIT_CONFIG_COUNT`, so an inherited `-c maintenance.auto=true` wins.

The helper is `tests/throwaway_git.py`, which provides `throwaway_git_env`, `throwaway_git_init`, `throwaway_git_clone` and `throwaway_git_environ`. Its shell twin is `tests/throwaway_git.sh`. There are two layers:

- **The env.** The helper drops every variable `git rev-parse --local-env-vars` names, which includes `GIT_CONFIG_PARAMETERS` and `GIT_DIR`. It also drops every inherited `GIT_CONFIG_KEY_*`/`VALUE_*` pair. It then sets a fixed identity, no global or system config, and `maintenance.auto=false` plus `gc.auto=0` through `GIT_CONFIG_COUNT`. The inherited variables are dropped rather than overridden, because nothing set in the environment can outrank `GIT_CONFIG_PARAMETERS`.
- **The repository's own config.** `throwaway_git_init` writes the same two keys into the new repository, and `throwaway_git_clone` does the same through `clone -c`.

The repository layer does not hold against an inherited `GIT_CONFIG_PARAMETERS`. Command-scope config outranks a repository's own config: the review measured 63 maintenance spawns at roster_edit with that layer alone. So every site whose own runner or code under test makes git calls without `env=` now runs its whole self-test under the env:

- roster_edit and state_docs use `with throwaway_git_environ():` at the self-test dispatch.
- prepr, bus, app_approve and the stop hook call `throwaway_git_env` for the self-test's shell.

stamp.py's `_throwaway_git_env()` is deleted, and its two sites now use the helper. A delegating wrapper would only pass calls through to a second copy. The import sits inside `self_test()`, so the release path never needs `tests/`.

All 38 `git init` lines and 16 `git clone` lines that the rule returns are converted. `--check` refuses a raw init or clone in a tracked script, and its rule is stated in the module docstring. Governance's `instrument-self-tests` runs `--check` and `--self-test`, next to `tmp_paths.py`, which scans the same scope. The RCA's §4 claim that the primary key has no inherited-config dependency is corrected in place.

**Behaviour notes** (from the round-1 review)

- `GIT_CONFIG_GLOBAL=/dev/null` now also applies to the clones of the real checkout (prepr's `--shared .` clones, `dual_path.py`, `ci-version-edit/`). A seat whose checkout is owned by another uid loses a global `safe.directory` there. CI's ubuntu runners are unaffected.
- In the stop hook, a `tests/throwaway_git.sh` that fails to source turns its 10 end-to-end cases into `SKIP`, as a failed `git init` already did, not into `FAIL`.

## Head

`b34eaf56ded7cc1eff6d62bc0663cb13386b28f7` merges the authored code head `e7c14d3d2de9bf601e05fba463be11f82913f27b` and then merges origin/main `13b6d121` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`9795cc9db2294d284619bf0f863f21231799244a` merges the authored code head `e7c14d3d2de9bf601e05fba463be11f82913f27b` and then merges origin/main `dcc77dd0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

e7c14d3d2de9bf601e05fba463be11f82913f27b

The round-1 review commits are:

- 70819a01 widens the clone rule, routes the remaining site calls through the env, and adds `throwaway_git_environ`.
- 9ddea090 answers the first CI run at 4d40002e. The shell-clone regex was a CodeQL `py/redos` alert, so it is now a token scan. The scope is now a prefix and suffix test, which removes the second copy of `tmp_paths.py`'s scope regex. Because of that, the `agreement.mjs` registration from round 1 is reverted: the pinned base copy that `wave-script` runs cannot see a registration added on the branch.

f9b24cc8 merges the PR branch, including the bot's `ci: re-record closures` commit 285b175f. e7c14d3d then merges origin/main `dcc77dd0`. The only conflict was `tests/closures.json`, which `ledger_merge.py` resolved. Every figure below was taken at e7c14d3d.

## Mutation proof

**The guard.** Each mutant is a commit built off the head with `git commit-tree`, checked with `python3 -I tests/throwaway_git.py --check --ref <mutant>`:

- K2 (the review's mutant): roster_edit's stale clone reverted to `run(["git", "clone", str(origin), str(stale)])` prints `REFUSE tools/audit/seat/roster_edit.py:668 ...` and `1 raw git init or clone site(s) refused`, rc 1.
- K4: prepr's clone written as `("$GIT" --no-pager clone -q --shared . "$PDX/r"` prints `REFUSE tools/pr/prepr.sh:1569 ...` and `1 ... refused`, rc 1.
- Removing the token scan (`_shell_clone`) from `is_site` turns 4 shell-clone rows red: `a shell clone`, `through a git variable`, `after a global option`, and `after -C and -c`.
- Deleting the widened clone pattern (`["']clone["']\s*[,\]]`) turns 7 of the self-test's clone rows red, including `FAIL refused: a positional list clone (the #2054 review's K2)` and `FAIL refused: execFileSync clone`.

**The env routing**, on real git 2.55.0, with `throwaway_git_sites.sh 1 hostile`:

- Without roster_edit's `with throwaway_git_environ():`: `site=roster_edit ... maintenance_spawns=63`.
- Without prepr's `throwaway_git_env` line: `site=prepr ... maintenance_spawns=16`.
- Each was restored with `git checkout`; the restored head reads 0 at both sites, as in the table below.

**The helper's layers**, under `--self-test`:

- Removing `GIT_CONFIG_PARAMETERS` from `LOCAL_ENV` makes 3 checks fail.
- Stopping the repository-config write makes `FAIL a caller WITHOUT the env still reads both off` fail.
- In the shell twin, dropping the `GIT_CONFIG_PARAMETERS` unset fails the parity check, and dropping the config write fails `the shell twin's init writes both keys`.
- Leaving only the `gc.auto` belt makes 4 checks fail.

## Null control

At the head:

- `--check` prints `0 raw git init or clone site(s) refused, 0 stale allow entries`.
- `--self-test` prints `44 checks, 0 failed`.
- The ReDoS null control is `"git " + "-c -a " * n + "x"`. The removed regex took 0.014 s at n=14, 0.248 s at n=16, 0.759 s at n=18 and 1.873 s at n=20, roughly tripling every two steps. The token scan takes 0.014 s at n=5000.

The self-test has an arm that keeps an inherited `GIT_CONFIG_PARAMETERS` in a hand-built environment. It reads `maintenance.auto` as `true` through both layers. That shows the precedence the helper's drop relies on. A new arm checks that a call passing no `env=` inside `throwaway_git_environ()` reads `false` under that same inherited value, and that `os.environ` is restored afterwards.

On real git 2.55.0, `dev/audit/harnesses/throwaway_git_sites.sh` counts maintenance spawns (`run_command: git maintenance run --auto` lines in `GIT_TRACE`) for one run per site. The `hostile` arm sends `maintenance.auto=true` plus the forced repack through `GIT_CONFIG_PARAMETERS`. The base column is #2051's head, dda217b3, from round 1. Both head columns were re-taken at e7c14d3d.

| site | plain, base | plain, head | hostile, head |
|---|---|---|---|
| stamp | 0 | 0 | 0 |
| ledger_merge | 2 | 0 | 0 |
| layout | 1 | 0 | 0 |
| budget_raise_gate | 0 | 0 | 0 |
| bus | 53 | 0 | 0 |
| merge_train | 215 | 0 | 0 |
| roster_edit | 74 | 0 | 0 |
| state_docs | 3 | 0 | 0 |
| app_approve | 34 | 0 | 0 |
| stop_hook | 2 | 0 | 0 |
| prepr | 57 | 0 | 0 |

Two sites cannot discriminate in this table. stamp was already fixed by #2051, and budget_raise_gate's site already ran under an env that kept maintenance off, so both read 0 at both ends of the plain arm.

stamp also ran 10 times on the hostile arm. At base dda217b3 it printed `directory_not_empty=5 nonzero_exit=10 maintenance_spawns=70`, with `OSError: [Errno 66] Directory not empty`. At e7c14d3d it printed 0, 0 and 0. The forced arm without `maintenance.auto` printed 0 at both ends, so #2051's fix holds when nothing overrides it.

The review re-took the base column: prepr read 41 there with a non-zero exit, while the disk was at 99%. Mine reads 57.

## Figures

- `python3 -I tests/throwaway_git.py --check --ref 470bbd60` printed `54 raw git init or clone site(s) refused, 2 stale allow entries`. Of the 54 lines, 38 are init and 16 are clone. The 2 stale entries are the helper's own files, which are absent at that ref.
- The same command at the head printed `0 ... refused, 0 stale`. The rule is `_SITE` in `tests/throwaway_git.py`. Its scope is `tools/ tests/ .claude/ dev/audit/harnesses/`, less `tools/audit/round<n>/`. Every line the rule returns at 470bbd60 is converted in this diff.
- The brief's rule, `git grep -n -E '"git", "init"|git init|"init", "-q"' -- tests tools .claude .github dev`, also returns lines outside that scope:
  - code lines under `dev/audit/rounds/**` and `dev/archive/**`, which are records, not reruns;
  - prose;
  - `dev/audit/harnesses/git_auto_maintenance_race.sh`, which runs `"$REAL_GIT" init` on purpose to measure git's default. The docstring names that shape, a git binary held in a variable whose name lacks `git`, as uncaught.
- `python3 tests/closure.py select --diff <merge base>` printed `MODE: FULL`. `tests/closure.py`, `tests/run.sh` and `tests/closures.json` are gate files, so the heavy scripts are CI's.
- Each command below was run locally at e7c14d3d and exited 0, under the CI venv's Python 3.14 with `PYTHONPATH=tests/hastub`:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`, with no budget raise
  - `tests/closure.py selftest`: `ALL 39 closure shrink pins PASSED`
  - `tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`
  - `tests/layout.py`: `layout self-test: ok`
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `tests/doc_claims.py`: `ALL 160 checks PASSED`
  - `tests/entities.py`: `ALL 2212 ENTITY CHECKS PASSED`. The first run printed `1 of 2212 ENTITY CHECKS FAILED`, the mutation driver's scaled-timeout check (`fits=124`): a 1.6 s fixture overran its 2 s limit at load average 88. The re-run printed all passed. This diff does not touch `tests/mutation_table.py`
- Each site's own self-test also exited 0 at e7c14d3d:
  - stamp: `RESULT stamp_self_test=pass`
  - ledger_merge: `all passed`
  - budget_raise_gate: `budget_raise_gate self-test: 206 checks, 0 failed`
  - merge_train: `merge_train self-test: 80 checks, 0 failed`
  - roster_edit: `roster_edit self-test: 37 checks, 0 failed`
  - state_docs: `state_docs self-test: all checks passed`
  - bus: `bus self-test: 45 checks, 0 failed`
  - app_approve: `app_approve self-test: 145 checks, 0 failed`
  - stop hook: `26 passed, 0 failed`
  - prepr: 210 passed, 0 failed
- Two more checks exited 0 at e7c14d3d:
  - `tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow entries at HEAD`
  - `codeowners_gap.py --check`: `RESULT uncovered_files=0 count`
- Classification:
  - `tests/throwaway_git.py` is on `NOT_A_TEST`, is skipped in both of `run.sh`'s loops, is in the recorded closures of `entities.py`, `layout.py` and `doc_claims.py`, and is CODEOWNED. stamp.py, layout.py and budget_raise_gate.py import it.
  - `tests/throwaway_git.sh` is INERT, because only shell self-tests that governance runs source it. It is CODEOWNED.
- CI at this head: see `## Red checks`.

## Red checks

These were red at 4d40002e, which was CI's first run on this pull request:

- `CodeQL`: 1 high alert, `py/redos` at `tests/throwaway_git.py:166`. The shell-clone regex backtracked exponentially on repeated `-c -a`. This diff caused it, and 9ddea090 fixes it with a linear token scan, measured in `## Null control`. A cheaper detector exists: CodeQL runs on every pull request in about 25 min. No local equivalent was run, and none is in the tree.
- `wave-script`: `AGREEMENT REFUSED ... unregistered=1`, the scope regex shared with `tmp_paths.py`. The job runs the base's pinned `agreement.mjs`, so the branch's registration could not reach it. Fixed in 9ddea090 by removing the duplicate grammar. The cheaper detector is `node tools/policy/agreement.mjs` run from the base. Locally I ran the branch's copy, which already carried the registration, so it could not show this.
- `closures`: `INERT READS UNDER-APPROXIMATED`. The Linux recording saw `tests/harness_headers.py` open the `dev/audit/harnesses/*.sh` files, including the new `throwaway_git_sites.sh`. `closures-autofix` repaired it in bot commit 285b175f (`ci: re-record closures`), and this head merges that commit. This is the `ci-autofix.md` case: no Darwin detector can see an inert read, because only `strace` records it.
- `pr-contract`: it refused the previous body for not naming the four reds above. This body names them.
- `delivery-status`: `UNCHECKED — 74 rowed, 0 pending, 0 overdue`. This job grades `main`'s merge window, not this diff, and it is not a required context.
- `nightly-status`: `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix` on scheduled run 37595831734, at main's be0cb82 from 2026-10-07, before this branch existed. It is main's, and its owner is the nightly lane.
- `nightly-ha (2025.2.0)` and `nightly-ha (stable)`: these ran at the bot commit 285b175f, in a `workflow_dispatch` Tests run. They fail on `FAIL a16:debug_inline` and `FAIL a16:debug_capped` (`bundle 9376014B against the 8388608B cap`), then on `run:exit_status`. The same `a16` arms fail in main's own scheduled run 37753990323 at 816547ef. This diff touches nothing under `custom_components/`, which is empty in the three-dot diff from the merge base, so the red belongs to main's debug-bundle lane and that lane's owner.
- `budget-raise-gate`: one run of its pair was `cancelled`, not failed, and this diff touches no `*_budgets.json`. The cancelled twin needs a rerun, which is the orchestrator's to do.

## Forward-carry

none. RCA §4's correction and §6's note land in this diff. The guard in `instrument-self-tests` refuses a new raw init or clone site, so no later stage's brief changes.

## Friction

none

## Approval

This diff touches code-owned and policy paths: `tools/release/stamp.py`, `.github/workflows/governance.yml`, `.github/CODEOWNERS`, `.claude/hooks/stop-selfcheck.sh`, `tests/closure.py`, `tests/run.sh`, `tests/layout.py`, and the two new CODEOWNED helper files. It merges only on the owner's approving review, or under the orchestrator's mandate procedure where one is in force.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
