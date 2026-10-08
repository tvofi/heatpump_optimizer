Fix review: merge b34eaf56ded7cc1eff6d62bc0663cb13386b28f7
bus-nonce: 2a704b031e08ce0ddee0771e533ec20b

Round 2. Review SHA: b34eaf56ded7cc1eff6d62bc0663cb13386b28f7, measured from a detached worktree.
- Merge base: 13b6d121, current origin/main.
- Real git 2.55.0, used through GIT_BIN.
- Evidence: /Users/timmalmstrom/hpo-seats/review-2054/r2/
- Round-1 evidence: /Users/timmalmstrom/hpo-seats/review-2054/evidence/
- The head was re-read before posting.

## Round-1 blockers

1. Guard gap: closed.
   - The test commit that reverts roster_edit.py:668 (formerly 663) to `run(["git", "clone", str(origin), str(stale)])` is now refused: rc=1, 1 refused (r2/mutation/K2.txt).
   - Also refused now:
     - `"$GIT" clone` in prepr.sh (K4).
     - `execFileSync('git', ['clone', SRC, dir])` in policy_lint_envmatrix.mjs (K5).
     - `--depth`, `--no-pager`, `${GIT:-git}` and `-c`/`-C` before clone (r2/guard-gaps.txt).
   - Forms still missed, all but two named in the docstring's new list:
     - Named: `"$BIN" clone`, `"$REAL_GIT" init`, `g(d, "init")`.
     - Not named: `git --git-dir x clone` with the value as a separate token, and GitPython `Repo.clone_from`, which nothing in the tree uses.
     - Non-blocking.
   - One false positive: a tuple `("clone", "fetch")` is refused. It refuses loudly and has an ALLOW escape. Non-blocking.
   - The CodeQL redos fix holds: `is_site('git ' + '-c -a '*5000 + 'x')` returns in 0.1 s.

2. Hostile-arm residual: closed. Inherited GIT_CONFIG_PARAMETERS carries `maintenance.auto=true` plus the forced repack.
   - `throwaway_git_sites.sh 1 hostile`, all 11 sites at the head: maintenance_spawns=0 everywhere, 0 directory_not_empty, 0 nonzero exits.
   - The four sites from round 1, before and after:

     | site | round 1 | head |
     |---|---|---|
     | roster_edit | 63 | 0 |
     | prepr | 24 | 0 |
     | stop_hook | 2 | 0 |
     | state_docs | 1 | 0 |

   - stamp in the hostile arm, 5 runs: 0/0/0.
   - Plain arm: 0 at every site.
   - Mutation: dropping the `throwaway_git_environ()` wrapper from roster_edit's main brings back maintenance_spawns=63 in the hostile arm (r2/realgit_r2.log).
   - A no-op `throwaway_git_environ` fails the new self-test check (r2/mutation/M10-environ-noop.txt).

3. CI settled at b34eaf56: 40 check-runs, 24 success, 14 skipped, 2 failure (r2/checkruns-final.tsv, 14:01Z).
   - `pr-contract`, `wave-script`, CodeQL and its three Analyze runs, `closures`, `fast (3.14)`, `coverage`, `mutation`, `instrument-self-tests` and both `budget-raise-gate` runs: success.
   - The only reds are `nightly-status` and `delivery-status`. The body names both and answers that they grade main's nightly and main's merge window, not this diff.
   - The body names every red from the first run at 4d40002e and answers each: CodeQL py/redos, wave-script agreement, the closures inert read (answered by ci-autofix), pr-contract, nightly-ha (main's a16 cap, #2056) and the cancelled budget-raise-gate twin.

## Re-verified at this head

- `--check`: 0 refused, 0 stale at HEAD. At the merge base 13b6d121: 54 refused, 2 stale.
- `--self-test`: 44 checks, 0 failed.
- Local self-tests:
  - structure.py: PASSED.
  - stop-selfcheck: 26 passed, 0 failed.
  - roster_edit: 37 checks, 0 failed.
  - state_docs: all checks passed.
- `env_drift --claims-only`: ok.
- VERSION, the manifest version, the release notes, the golden fixtures and the budgets are untouched.
- The closures diff adds only the three throwaway_git.py closure entries and an inert_reads entry for dev/audit/harnesses/throwaway_git_sites.sh, from CI's Linux autofix.
- Dropping the agreement.mjs registration is consistent with the new scope test, which uses a prefix and suffix and is no longer a second copy of tmp_paths' regex. wave-script is green.

## Non-blocking notes still open

- The real-checkout clones in prepr, dual_path and ci-version-edit now read GIT_CONFIG_GLOBAL=/dev/null. A seat whose checkout another uid owns loses its global safe.directory. CI is unaffected.
- prepr's and the stop hook's self-tests now export the helper's env for the whole drive, so their calls against the outer checkout also run without global config. Every lane is green on that.
- RCA §6 now says init and clone, which resolves the round-1 note.
