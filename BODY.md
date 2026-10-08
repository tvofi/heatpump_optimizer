Every throwaway git repository a tracked script builds now goes through one shared helper, which turns git's auto-maintenance off. That follows the owner's decision (tvofi, 2026-10-08): a helper at every temp-repository site, not a CI-only workflow `env:`.

#2051 fixed stamp.py's two repositories. The root cause is in `dev/audit/rca/R9-RCA-stamp-race.md`: git 2.54 and later detaches a geometric repack after a commit or merge, and that repack can still be writing into `.git/objects/pack` when the caller removes the temporary directory. #2051's round-2 review found that its env-only fix can be undone. Git reads `GIT_CONFIG_PARAMETERS` after `GIT_CONFIG_COUNT`, so an inherited `-c maintenance.auto=true` beats the `false` the fix sets.

The helper is `tests/throwaway_git.py` (`throwaway_git_env`, `throwaway_git_init`, `throwaway_git_clone`), with a shell twin, `tests/throwaway_git.sh`. It works in two layers:

- **The environment.** It drops every repository-local variable git names (`git rev-parse --local-env-vars`, which includes `GIT_CONFIG_PARAMETERS` and `GIT_DIR`) and every inherited `GIT_CONFIG_KEY_*`/`VALUE_*` pair. It then sets a fixed identity and no global or system config, and sets `maintenance.auto=false` and `gc.auto=0` through `GIT_CONFIG_COUNT`. The variables are dropped, not overridden, because nothing set in the environment can outrank `GIT_CONFIG_PARAMETERS`.
- **The repository's own config.** `throwaway_git_init` writes the same two keys into the new repository's config, and `throwaway_git_clone` does it with `clone -c`. So a git call made without the environment still reads auto-maintenance as off, for example the production tool a self-test drives.

stamp.py's `_throwaway_git_env()` is deleted and its two sites take the helper. It is replaced rather than kept byte-compatible because a second copy is the duplication this change removes, and a delegating wrapper would only pass calls through. The helper is imported inside `self_test()`, so the release path never needs `tests/`.

All 38 `git init` lines and all 16 `git clone` lines that the rule below returns are converted. The helper's `--check` refuses a raw init or clone in a tracked script. Governance's `instrument-self-tests` runs that check and the helper's `--self-test`, next to `tmp_paths.py`, which is the step that already scans the same tracked-script scope. The RCA sentence the review found false is corrected in place, marked as a correction.

## Head

402b1f3ab172c096c13e2386fe1cd321aeacca8c

This is the authored commit 4e2a56ec, with origin/main `470bbd60` (#2051's merge) merged in by 3859bc20, plus 402b1f3a. That last commit registers the tracked-script scope regex, which `tmp_paths.py` and `throwaway_git.py` now share, in `tools/policy/agreement.mjs`. `prepr.sh`'s agreement lane had refused it as an unregistered grammar. The merge base is 470bbd6087e5978eae594e616a76e207336b289c. Every figure below was taken at this head, after that merge, at 2026-10-08 about 08:30Z.

## Mutation proof

**The guard.** Each mutant is a commit built off HEAD with `git commit-tree` (HEAD does not move), checked with `python3 -I tests/throwaway_git.py --check --ref <mutant>`:

    M1: tests/layout.py, the helper call reverted to subprocess.run(["git", "init", "-q"], ...)
      REFUSE tests/layout.py:641: subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
      throwaway_git: 1 raw git init site(s) refused ... rc=1
    M1b: tools/pr/prepr.sh, one subshell's throwaway_git_init reverted to git init -q -b main .
      REFUSE tools/pr/prepr.sh:1718: set -e; throwaway_git_env; cd "$TR"; git init -q -b main .
      ... rc=1

These two mutants were taken before the clone extension, so the summary line there still reads `init`.

**The helper's layers.** Each is an in-place edit after a commit, restored with `git checkout`, under `python3 -I tests/throwaway_git.py --self-test`:

- M2: `GIT_CONFIG_PARAMETERS` is removed from `LOCAL_ENV`. Three checks fail: `FAIL the env drops every repository-local variable ...`, `FAIL the env survives the same hostile parameters ...` and `FAIL the shell twin's throwaway_git_env sets exactly the same GIT_ variables`.
- M3: the init stops writing the repository config. `FAIL a caller WITHOUT the env still reads both off: the repository's own config`.
- M4: the shell twin stops unsetting `GIT_CONFIG_PARAMETERS`. `FAIL the shell twin's throwaway_git_env sets exactly the same GIT_ variables`.
- M5: the shell init stops writing the config. `FAIL the shell twin's init writes both keys ...`.
- M6: `maintenance.auto` is dropped from `CONFIG`, leaving only the `gc.auto` belt. Four checks fail.

**Real git.** git 2.55.0 is built from git/git v2.55.0 and used through `GIT_BIN`. The run is `dev/audit/harnesses/throwaway_git_sites.sh`, and the base tree is #2051's head dda217b3. In the `hostile` arm, `GIT_CONFIG_PARAMETERS` carries `maintenance.auto=true` plus the forced geometric repack. stamp, 10 runs:

    base dda217b3:  last: OSError: [Errno 66] Directory not empty: 'info'
                    site=stamp arm=hostile git=2.55.0 runs=10 directory_not_empty=5 nonzero_exit=10 maintenance_spawns=70
    head:           site=stamp arm=hostile git=2.55.0 runs=10 directory_not_empty=0 nonzero_exit=0 maintenance_spawns=0

That is the #2051 round-2 finding reproduced on real git and closed.

## Null control

At the head, `--check` prints `0 raw git init or clone site(s) refused, 0 stale allow entries`, and `--self-test` prints `36 checks, 0 failed`.

The `forced` arm drives stamp, 10 runs, with the repack forced and no `maintenance.auto` override. It printed `directory_not_empty=0 nonzero_exit=0 maintenance_spawns=0` at both base and head. #2051's own fix holds when nothing overrides it, so the hostile arm is what tells the two apart.

The self-test also has an arm that must fail on any git: a hand-built environment that keeps `GIT_CONFIG_PARAMETERS` reads `maintenance.auto` as `true` through both layers. That is the reason the helper drops it.

The `plain` arm forces nothing on real git 2.55.0. It counts `run_command: git maintenance run --auto` lines in a `GIT_TRACE` file over 1 run per site. Git spawns that after every commit or merge unless auto-maintenance is off, so the count does not depend on timing:

| site | base dda217b3 | head |
|---|---|---|
| stamp | 0 | 0 |
| ledger_merge | 2 | 0 |
| layout | 1 | 0 |
| budget_raise_gate | 0 | 0 |
| bus | 53 | 0 |
| merge_train | 215 | 0 |
| roster_edit | 74 | 0 |
| state_docs | 3 | 0 |
| app_approve | 34 | 0 |
| stop_hook | 2 | 0 |
| prepr | 57 | 0 |

stamp and budget_raise_gate read 0 at the base too. stamp was already fixed by #2051, and budget_raise_gate's site already ran with an env that kept maintenance off, so the plain arm cannot tell its two ends apart. The head column for roster_edit, state_docs and prepr was re-taken after the clone sites were converted. Before that, the same head read 66, 2 and 16 with every init converted, and those spawns came from their `git clone` repositories. That residual is why the clone class is in this diff.

## Figures

- `python3 -I tests/throwaway_git.py --check --ref 470bbd60` printed `54 raw git init or clone site(s) refused, 2 stale allow entries`. Of the 54 lines, 38 are init and 16 are clone. The 2 stale entries are the helper's own files, which are absent at the base.
- The same command at HEAD printed `0 ... refused, 0 stale`. This is the class enumeration step 8 asks for. The rule is the regex in `tests/throwaway_git.py` (`_SITE`), over `tools/ tests/ .claude/ dev/audit/harnesses/`, less `tools/audit/round<n>/`. Every line it returns at the base is converted in this diff.
- The brief's rule, `git grep -n -E '"git", "init"|git init|"init", "-q"' -- tests tools .claude .github dev`, finds lines this rule leaves out, each with a disposition:
  - Round evidence and the archive (`dev/audit/rounds/**`, `dev/archive/**`): 6 code lines. They are records, not reruns, and are out of scope by rule.
  - Prose: `stop-selfcheck.sh:152` (a comment), the RCA, and the round reports.
  - Its `.claude/hooks/stop-selfcheck.sh:94` (`git -C "$T" init`) is in scope and converted.
  - `dev/audit/harnesses/git_auto_maintenance_race.sh` runs `"$REAL_GIT" init` on purpose, because its `spawn` arm measures git's default. The rule does not match `$REAL_GIT`. It is left as is.
- `python3 tests/closure.py select --diff 470bbd60 --workdir "$D"` printed `MODE: FULL`, because `tests/closure.py` changes the gate itself. `tests/run.sh` and `tests/closures.json` are gate files too. Under `fixer.md` step 5, the heavy scripts (features, golden, stress, optimality and the rest) are left to CI's `fast` and `slow` jobs at this head.
- Run locally at this head, all under the CI venv's Python 3.14 with `PYTHONPATH=tests/hastub`. Every one exited 0:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`, with no budget raise and no re-record.
  - `tests/closure.py selftest`: `ALL 39 closure shrink pins PASSED`.
  - `tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
  - `tests/layout.py`: `layout self-test: ok`, guard 0.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 160 checks PASSED`.
  - `tests/entities.py`: `ALL 2210 ENTITY CHECKS PASSED`, re-run at 402b1f3a.
  - `tools/pr/prepr.sh <this body>`: exit 0, with the agreement lane at `unregistered=0`.
- Each converted site's own self-test also passed at this head:
  - stamp.py: `RESULT stamp_self_test=pass`.
  - ledger_merge.py: `all passed`.
  - budget_raise_gate.py: 202 checks, 0 failed.
  - merge_train.py: 80 checks, 0 failed.
  - roster_edit.py: 37 checks, 0 failed.
  - state_docs.py: `all checks passed`.
  - bus.sh: 45 checks, 0 failed.
  - app_approve.sh: 145 checks, 0 failed.
  - stop-selfcheck.sh: 26 passed, 0 failed.
  - prepr.sh: 210 passed, 0 failed.
  - `tools/audit/seat/tmp_paths.py --check`: 0 refused.
  - `dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- Classification: `tests/throwaway_git.py` is on `NOT_A_TEST`, is skipped in both of `run.sh`'s loops, and is recorded into the closures of `entities.py`, `layout.py` and `doc_claims.py`. Those three were re-recorded with `derive_closures.sh --single`; Python lanes record through the audit hook, which is sound on Darwin. `tests/throwaway_git.sh` is INERT. Only shell self-tests source it, and governance runs those, never this gate. Both files are CODEOWNED. `codeowners_gap.py` had refused the `.py` file as UNCOVERED, since stamp.py, layout.py and budget_raise_gate.py import it.
- The evidence is in `/Users/timmalmstrom/hpo-seats/r9-gittmp/evidence/`. It holds one file per run named above, `realgit_base_vs_head.log` and `realgit_clone_sites_head.log`.

## Red checks

none at the time of writing. CI has not yet run on this head.

## Forward-carry

The correction to `dev/audit/rca/R9-RCA-stamp-race.md` §4 and its §6 note land in this diff. They record that the CI-only `env:` barrier is superseded by the helper. No later stage's brief changes: the guard in governance's `instrument-self-tests` now refuses a new raw init or clone site.

## Friction

none

## Approval

This diff touches code-owned and policy paths: `tools/release/stamp.py`, `.github/workflows/governance.yml`, `.github/CODEOWNERS`, `.claude/hooks/stop-selfcheck.sh`, `tests/closure.py`, `tests/run.sh`, `tests/layout.py`, and the two new CODEOWNED helper files. It merges only on the owner's approving review, or on the orchestrator's mandate procedure where one is in force.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
