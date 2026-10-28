# RESUME: R10-ORCH-BEATD arm (a), repair round for #2916

- Code head: handoff/r10-orch-beatd at f0f8c3b6011d607f1fb08d41a08d39da92bb7222, a fast-forward of c991d64cd. It merges origin/main beb570c81 and adds two commits:
  - `Lock.take` creates its file 0o600, for CodeQL alert 45; case (2) gains a mode arm and the mutant m2_lock_world_readable.
  - case (7)'s git calls run under throwaway_git's identity;
  - case (3) reads a zombie grandchild as killed;
  - instrument-self-tests' timeout-minutes goes from 20 to 30.
- Re-taken at that head (Linux, venv-ci Python 3.14.7):
  - beatd self-test with no global git identity: 87 checks, 0 failed, 478 s;
  - prepr (PREPR_SKIP_CLOSURES=1): rc 0, 0 REFUSE;
  - entities.py and harness_headers.py both passed;
  - the structure ratchet passed, archscore dS 0, and selftest_wiring printed 0 unwired.
- Every #2916 red is named in `## Red checks`: CodeQL, alert 45, env-matrix, policy-docs, instrument-self-tests, gate and pr-contract.
- Open (not built, outside arm (a)): a throwaway_git rule for fixture git calls made outside the throwaway env, owed to a root-cause seat.
- Next: the orchestrator runs update_pr for #2916, then the fix review runs on f0f8c3b60.
