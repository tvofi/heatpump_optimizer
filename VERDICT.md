Fix review: blocked cd2def5ed3f1dc8d700e4e295775e8d59112f2be harness: guard-gap ["git", "clone", <src>, <dst>] passes --check; hostile residual at 4 sites undisclosed
bus-nonce: c7c30668b6f2cf9cb9aab0876da9d490

Round 1. Review SHA cd2def5ed3f1dc8d700e4e295775e8d59112f2be, measured from a detached worktree. The head was re-read at 09:13Z and had not moved; mergeStateStatus is DIRTY. Merge base 470bbd60. Real git 2.55.0 via GIT_BIN. Evidence: /Users/timmalmstrom/hpo-seats/review-2054/evidence/

## Blocking

1. **The guard refuses less than the body and docstring say.** The body says `--check` "refuses a raw init or clone in a tracked script". The docstring defines a SITE as including "`clone` as its subcommand". The most ordinary Python form is not refused:
   - `subprocess.run(["git", "clone", str(a), str(b)])` is MISSED.
   - So are `["git", "clone", "--depth", "1", ...]`, `execFileSync('git', ['clone', src, dir])`, `"$GIT" clone ...` and `git --no-pager clone`.
   - A commit-tree mutant (evidence/mutation/K2.txt) reverts roster_edit.py:663 to `run(["git", "clone", str(origin), str(stale)])`. `--check` prints `0 raw ... refused`, rc=0.
   - The same line with `-q` (K1) is refused. The clone regex only catches the list form when one of the listed options follows `"clone"`.
   - The docstring's "WHAT IT DOES NOT CATCH" list does not name this shape (evidence/guard-gaps.txt).
   - Fix: let regex 2 accept the list separator, e.g. `(?i:\bgit\b)["']?\s*,\s*\[?\s*["']clone["']`. Add a self-test row for the positional list clone. Then either cover `"$VAR" clone` or name it in the docstring.

2. **The hostile arm is closed only at stamp, but the body's figures read as closing the round-2 finding.** Under `throwaway_git_sites.sh 1 hostile` at the head, these sites still spawn:
   - roster_edit: maintenance_spawns=63
   - prepr: 24
   - stop_hook: 2
   - state_docs: 1

   The cause is the site's own git calls, which do not pass the env. Examples: roster_edit's `run()` (line 81) has no `env=`, and the stop hook's `git -C "$T" commit`. GIT_CONFIG_PARAMETERS `maintenance.auto=true` beats the repository-config layer at those calls. The docstring does name this limit, but for "the tool under test", not the site's own seed commits. The body reports the hostile arm for stamp only.
   - Fix: route those sites' own git calls through the env, or disclose the per-site hostile figures and the residual in the body.
   - At the base, the hostile arm already went red at merge_train (`Directory not empty: 'objects'`, 1/1). At the head merge_train reads 0.

## Verified (RESULT lines)

**Enumeration**
- RESULT check_base=54 refused (38 init / 16 clone, re-derived; app_approve.sh:483 is an init line naming a `clone` directory), 2 stale.
- RESULT check_head=0 refused, 0 stale.
- RESULT check_mergetree_with_main_816547ef=0 refused (tree a54ad21b).
- My own broad enumeration (evidence/broad-grep-head.txt) is wider than the PR's rule: every tracked non-md file, any `init` or `clone` with git or a quoted subcommand. In scope, it finds no unconverted site at HEAD except the disclosed `"$REAL_GIT" init` in git_auto_maintenance_race.sh. The diff's class is closed; the forward guard is not (item 1).

**Env layer**
- LOCAL_ENV equals `git rev-parse --local-env-vars` at 2.55.0, plus GIT_INTERNAL_SUPER_PREFIX (evidence/local-env-vars-255.txt).
- The RCA §4 correction holds on 2.55.0, 2.50.1 and 2.38.1: COUNT=false with PARAMETERS=true reads `true`.
- No converted site relied on an inherited GIT_DIR or GIT_WORK_TREE. bus.sh's production code and prepr's `ra()` set their own GIT_DIR after the helper.
- No converted site depends on the default branch name, and none depends on the identity the env now forces. prepr RA re-exports `st`; entities `_cm_git` and merge_train never read the author.

**Behaviour notes (non-blocking)**
- GIT_CONFIG_GLOBAL=/dev/null now also applies to the clones of the real checkout: prepr CLM/PDX `--shared .`, dual_path, and ci-version-edit. A seat whose checkout another uid owns loses a global `safe.directory`. CI runs on ubuntu-latest with no container, so CI is unaffected.
- In the stop hook, a failed `. throwaway_git.sh` turns 10 end-to-end cases into SKIP, not FAIL.
- RCA §6's new sentence says "every `git init` site". The diff also covers clone.

**stamp.py**
- The import is inside `self_test()` only (line 577). `_throwaway_git_env` has no remaining code reference. main() does not import tests/.

**Classification**
- `throwaway_git.py` is on NOT_A_TEST, skipped in both run.sh loops, and in the closures of entities, doc_claims and layout. entities and doc_claims import it at top level. entities runs stamp's and ledger_merge's self-tests.
- `throwaway_git.sh` is INERT. No tests/*.py sources it; entities only reads workflow text about the shell self-tests.
- CODEOWNERS for both files is needed: pinned graders run them (budget_raise_gate self-test, and prepr.sh after merge).
- The closures.json diff adds only those three entries plus timing noise. I did not re-record; CI's closures lane never ran at this head.

**Mutation proof** (evidence/mutation/)
- RESULT guard_mutants: K1 (list clone with -q) and K3 (layout raw init) are refused. K2 (positional list clone) and K4 (`"$GIT" clone`) are NOT refused.
- RESULT helper_mutants: all 8 are killed under `--self-test`. M2: 3 FAIL. M3: 1. M5: 1. M6: 4. M7: 1. M8: 1. M9: 2.
- RESULT site_mutant ledger_merge reverted to raw init, plain arm, 2 runs: maintenance_spawns=4. Restored: 0.

**Real git** (finder harness and fixer harness; evidence/realgit_reviewer.log and realgit_head_rerun.log)
- RESULT finder realgit-forced, 5 runs: base 470bbd60 directory_not_empty=0 nonzero=0; head 0/0. Flat at both ends, as the body says for the forced arm.
- RESULT sites hostile stamp, 5 runs: base directory_not_empty=2 nonzero=5 spawns=36; head 0/0/0.
- RESULT plain spawns, 1 run each:

  | site | base | head |
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
  | prepr | 41 | 0 |

  The base matches the body's table except prepr: I read 41 with base nonzero_exit=1, the body reads 57. The disk was at 99% during the base runs and hit ENOSPC on the first head pass. The head numbers were re-taken after the ENOSPC.
- RESULT doc_claims plain spawns: base 0, head 0. That site only runs init and add, so it is flat by design.

**Other checks**
- VERSION, the manifest version, RELEASE_NOTES.md, the claim files and the budgets are untouched.
- `env_drift --claims-only`: ok.
- structure.py: PASSED.
- `throwaway_git.py --self-test`: 36 checks, 0 failed.

**CI.** No check-runs exist at cd2def5e (total_count=0 at 08:52Z and 09:13Z), because the PR is DIRTY.
- Conflict measurement: `git merge-tree origin/main(816547ef) cd2def5e` with the repo's driver prints `LEDGER-MERGE: resolved tests/closures.json`. Only the seconds differ (entities 196.6 vs 179.0, doc_claims 4.6 vs 6.3). There is no other conflict and nothing refused.
- GitHub runs no driver, so the orchestrator or fixer must merge main before any CI exists.
- Step 11 cannot be answered at this head: the heavy lanes (entities, closures, mutation, governance instrument-self-tests) have not run.
