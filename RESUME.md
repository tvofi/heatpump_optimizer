# RESUME: R10-ORCH-BEATD arm (a)

- Code head: handoff/r10-orch-beatd at c991d64cdaef342d282d1a8e991dadc2671f917d: f8bb14aad plus the INERT READS entry, throwaway_git fixtures (d72c4a982), and the named-docs exclusion in dev/governance/config/corpus_excluded.json (policy_lint.mjs back to main's copy; CI restores pinned check sources from the base). PR #2916.
- The worktree is /Users/timmalmstrom/hpo-seats/r10s6/fix-beatd-a, on branch fix/r10-orch-beatd, and it is clean.
- Done:
  - beatd.py and beatd_shims/git;
  - the INSTRUMENTS.md entries;
  - the governance.yml self-test step;
  - the self-test, which printed 84 checks, 0 failed at f008c2b75 (prepr rc 0 there too). It ran cases (a)1-8 with their nulls and 16 in-tree mutants, all killed;
  - archscore dS 0, the structure ratchet passed, and selftest_wiring printed 0 unwired.
- Not run locally: tests/entities.py and tests/harness_headers.py, the two scripts scope.run names. Two attempts died, one to a stop and one to the 12:42Z reboot. CI runs both.
- The full self-test takes about 9 min here under load and about 2-3 min expected on CI. That is inside instrument-self-tests' 20 min timeout.
- Gotcha: `.git/info/exclude` holds `seat/`, so new files under tools/audit/seat need `git add -f`.
- Next: the orchestrator opens the PR (handoff_push.sh), then the fix review runs. Arm (b) starts only after (a) merges.
