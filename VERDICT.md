Fix review: merge 80779d2e7492c8aaf1b4b4608d3f6b93a45dcffd

bus-nonce: 636931f74ab1aa4556b6afeb6df78740

## Evidence

Round 1, a handoff review: there is no pull request yet, so there is no review packet and no CI to read. Head 80779d2e7492c8aaf1b4b4608d3f6b93a45dcffd is the tip of refs/heads/handoff/r10-hotfix-opener-unblock and is the head BODY.md names (ev/HEAD.txt). Merge base 61afd4f2db. Since then origin/main has moved to 6d16af36c, and `git merge-tree --write-tree origin/main <head>` exits 0 with tree a3b698b8f6, so the head merges cleanly. Between the base and main, roles/ changed only fixer.md, and fix-review.md is unchanged.

- Mutation proof, Part A: `beatd.py --self-test 9` at the head prints `beatd self-test: 34 checks, 0 failed`, and each of the 10 named m9_* mutants turns its named check red (ev/beatd_st9_head.txt).
- Mutation proof, Part B: `r10_open_driver_mutants.py` at the head prints `RESULT mutant=M0 failed=0 verdict=null-ok`, `RESULT mutant=M-livetip failed=2 verdict=killed` and `RESULT mutant=M-moved-gone failed=1 verdict=killed`, then `ABORT M-exact: pattern occurs 0 times` with rc 2, as the body discloses (ev/r10_mutants_head.txt).
- My own mutants on open_driver.py: deleting `sha = live_tip` gives 2 failed of 93, the two live-tip checks. Deleting the RETIP log line gives 1 failed of 93 (ev/own_mutants2.txt).
- open_driver `--self-test`: 91 checks, 0 failed at the base; 93 checks, 0 failed at the head. Both match the body.
- gate_lock `_priority_cases` (ev/gate_lock_priority.txt), with my own RESULT lines:
  - base, HPO_GATE_PRIORITY=2: 2 failed of 14, naming the two arms the body names
  - base, variable unset: 0 failed of 14
  - head, HPO_GATE_PRIORITY=2: 0 failed of 14
  - head, variable unset: 0 failed of 14
  These match the body. Its HPO_GATE_PRIORITY=1 figure I did not re-run.
- `HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py` at the head prints `ALL 2705 ENTITY CHECKS PASSED`, rc 0. `doc_claims.py` prints `ALL 315 checks PASSED`.
- `closure.py select --diff <base>` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` `structure.py` prints `STRUCTURE RATCHET PASSED`. archscore prints `Architecture score: dS +0.0000 NULL`.
- The diff does not touch VERSION, the manifest, RELEASE_NOTES.md, the claim files, the golden fixtures or any budget, so there was no env_drift comparison to make. No metric moves.
- Figures I could not re-derive:
  - the full `beatd.py --self-test` count of 153, not run here
  - the `prepr.sh` rc 0, not run
  - the field figures from the beat host's open-driver.log, which this container does not have
- Red checks: there is no PR, so there are no runs. I printed the owed-reds set (ev/owed_reds.txt), and no red exists to answer. The body's `## Red checks: none` therefore stands unverified against CI.
- The class is one seam per part (P581: the beat's own checkout; P603: the opener's sha choice). The body names no multi-seam issue, so step 6 owes no class rule.
- Forward-carry: none claimed. The body's one Friction line carries to R10-SEAT-IDENTITY-P5.

## Findings

- Follow-up: in beatd.py `fresh()`, deleting `self.stop.set()` survives `--self-test 9` (34 checks, 0 failed). Case 9 always runs with a bounded `--for`, so `run` returns whether or not the restart stops it. A production beat runs unbounded, so without the stop it would never reach the execve, and Part A would silently not restart. No check pins that the restart itself ends the run (ev/own_mutants2.txt, no_stop). Carry: R10-SEAT-IDENTITY-P5
- Follow-up: in beatd.py `cmd_run`, replacing the exec environment `{**os.environ, RESTARTED_ENV: beat.restart}` with `dict(os.environ)` survives `--self-test 9`. The m9_guard_off mutant pins the guard's read, but nothing pins that the re-exec sets the guard. So the loop guard against repeated restarts is untested end to end (ev/own_mutants2.txt, no_guard_env). Carry: R10-SEAT-IDENTITY-P5
- Follow-up: three more beatd.py `fresh()` mutants survive on behaviour:
  - Deleting the `self.stale_n = 0` reset survives outright, 0 failed.
  - `stale_n >= 1` instead of `>= 2` turns red only the self-test's own anchor check for m9_stale_never.
  - Counting untracked files in the dirty check turns red only the anchor check for m9_dirty_ignored.
  So no behaviour check covers BEAT-STALE on the first refusal, the reset after a fresh pass, or an untracked-only tree (ev/own_mutants.txt, ev/own_mutants2.txt). Carry: R10-SEAT-IDENTITY-P5
