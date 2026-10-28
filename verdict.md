Fix review: blocked ca2dc27d74252606afb264c514585f9ea0e405b5 mutation-vacuous: kill_group's grace poll (while time.time() < at -> while False) and KILL_GRACE_S 10.0 -> 0.5 each survive case (3); the 10 s SIGTERM-to-SIGKILL grace the repair claims to keep is unpinned

bus-nonce: fd7f49523c6e0b5146aaad9376619e5a

## Round

This is round 2. Round 1 was `Fix review: blocked ad1ba9adb7341d31288d27648da09f0ce61def19` (review/2916 at 803820f94). The measured head is ca2dc27d74252606afb264c514585f9ea0e405b5, and it was still the PR head when this was written. `git diff 593f57c44...origin/main -- dev/governance/roles/` is empty, so the role contract is current. The head merges code head 84e5684e5 with origin/main 593f57c44. `git diff 84e5684e5 ca2dc27d7` over the seven PR paths is empty, so the merge carries none of this PR's lines.

## Block

The round-1 repair adds `kill_group(pgid, at)`. It polls the group with `killpg(pgid, 0)` until `at` and only then sends SIGKILL. The body chose this design for its grace: "Sending SIGKILL at once when the leader exits drops the 10 s grace the note gives a trapping descendant to clean up. The poll keeps both." The approved note's §2 **Run** gives the same timing: "At its timeout it gets SIGTERM, then SIGKILL 10 s later." No check pins that grace:

- **y1_kill_group_no_grace.** The plant replaces `while time.time() < at:` with `while False:`, so a timed-out job's group gets SIGKILL the moment its leader exits. Cases (3) and (2) all stay green: `RESULT y1_kill_group_no_grace: SURVIVED` (`ev/ymut-head.txt`). The arm `a TERM-ignoring grandchild is killed after its leader exits` checks only that one PASS reads `outcome=timeout` and that the grandchild is gone. It never checks when the SIGKILL came.
- **y16_grace_half_second.** The plant sets `KILL_GRACE_S = 10.0` to `0.5`, which also shortens the live-leader path. It survives too (`ev/ymut-y16-head.txt`). The null `a leader ignoring TERM too is killed at the grace, rc -9` checks `rc=-9`, not the grace.

The behaviour itself is correct at this head. The round-1 finder probe, run unchanged against this head, gives `beatd rc=0 after 12s`, `PASS … dur=12 rc=-15 outcome=timeout`, then `grandchild … state: gone` and an empty owner-only `stubborn.lock` (`ev/probe-sigkill-escalation-head.txt`). What is unproven is the test: deleting the line the repair names fails nothing (fix-review.md step 1).

The fix is small and inside arm (a). In `_stubborn`, require the PASS `dur=` to be at least 10 on both arms, the stubborn one and the `both` null. Then add y1 and y16 as `MUTANTS` entries targeting those arms. The marker-based arm (`its process group took SIGTERM before any SIGKILL`) still covers TERM-before-KILL. A `dur` lower bound is safe against the zombie concern the body raises, because beatd measures `dur` itself.

## Findings

- The 10 s SIGTERM-to-SIGKILL grace in `kill_group` and in `supervise`'s live-leader path is unpinned (see `## Block`). Owed: a `dur` bound on case (3)'s two stubborn arms, with plants y1 and y16, in this PR's next round. Carry: R10-ORCH-BEATD
- Seven of my own plants survive their cases (`ev/ymut.py`, my harness and not the finder's; output in `ev/ymut-head.txt`). Each one is a behaviour the docstring or the note's §2 states but no check pins. None is a defect at this head:
  - `y2_drop_keeps_pid`: `Lock.drop` skips its `ftruncate`. The docstring says "emptied on release"; without the truncate, `status` would print a false `ALERT lock-owner-dead` for every lock once a beat exits cleanly. Survives (2), (3) and (8).
  - `y3_no_state_subst`: the `$S` substitution in `argv` is dropped. Survives (1), (4) and (5).
  - `y6_shim_no_pull`: the shim retries `fetch` only, though §2 says "fetch or pull". Survives (6).
  - `y7_shim_no_export`: the shim no longer exports `HPO_REAL_GIT` ("so that children never walk again", §2). Survives (6).
  - `y9_duplicate_name_ok`: duplicate job names are accepted, against the docstring's refusal. Survives (1).
  - `y13_idle_hides_failure`: a watch job whose last outcome was not `ok` reads `idle` with no alarm. Survives (7).
  - `y14_shim_skip_no_c`: the shim stops skipping `-c <value>` (§2's option skip). Survives (6).

  Each needs a case arm and a `MUTANTS` entry, or a stated deferral, in the next round, since that round reopens the self-test anyway. Owed: in this PR's next round. Carry: R10-ORCH-BEATD
- The beat's own SIGTERM handler TERMs its running groups but never escalates. A TERM-ignoring descendant of a job that is running when beatd is stopped can therefore outlive the beat, and its lock drops as beatd exits. The body defers this "to (b)" as a design question, but its `## Forward-carry` reads `none`, so (b)'s brief does not yet state it. Owed: written into arm (b)'s brief on the R10-ORCH-BEATD roster group as a precondition (finding-propagation.md). Carry: R10-ORCH-BEATD

## Evidence

- **Self-test re-run at head.** Command: `HOME=<empty> GIT_CONFIG_GLOBAL=/dev/null /opt/hpo/venv-ci/bin/python -I tools/audit/seat/beatd.py --self-test` (Linux, Python 3.14.7, no committer identity). It printed `beatd self-test: 115 checks, 0 failed`, rc 0, in 4 min 28 s of wall time. The `grep -c` counts are 65 `ok   (`, 25 `ok   anchor` and 25 `ok   mutant`, which re-derives the body's 115 under its own rule (`ev/selftest-head.txt`). The body's mutation proof stands: all 25 named plants kill, and none crashes.
- **Round-1 items answered.** The SIGKILL escalation now fires after the leader exits: the finder probe gives `dur=12`, the grandchild is gone, and the lock is empty. The round-1 mutants x4, x8, x13, x15 and x16 are each now a `MUTANTS` entry that kills in the run above.
- **The instrument-self-tests cap.** It moved from 20 to 30 min, and the self-test now takes about 4.5 min, matching this host's 4 min 28 s. The job was still in progress when CI was read, so its wall time at this head is not verified here.
- **My other plants that killed.** These were y4 (relative argv), y5 (env_pass), y8 (watch under 60 s), y10 (non-ok outcome reads ok), y11 (HPO_BEATD_JOB), y12 (`GIT_CONFIG_COUNT=0`, killed by case (6b)'s env check) and y15 (`--for` ignored).
- **Merge.** `git merge-tree --write-tree origin/main ca2dc27d7` exited 0 against origin/main 593f57c44 (`ev/merge-tree.txt`). No claim file is in the diff.
- **Cheap checks at head** (`ev/cheap-checks.txt`):
  - `selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired`.
  - `throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`, and `policy_lint.mjs` is byte-identical to main.
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `entities.py` (venv-ci 3.14.7): `ALL 2470 ENTITY CHECKS PASSED`. That is 2470 at this head against the body's 2467 at 84e5684e5; the body's figure was taken before main moved, so it was not re-derived at its own SHA.
  - `harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `closure.py select --diff 593f57c44`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
  - `archscore --diff 593f57c44 HEAD`: `Architecture score: dS +0.0000 NULL`.
  - The three-dot diff over VERSION, `tests/golden`, `custom_components` and `RELEASE_NOTES.md` is empty.
- **CI on this head** (`ev/check-runs.txt`). There is no failure or cancellation. Twenty runs are green, among them policy-docs, env-matrix, mutation, arch-score and budget-raise-gate. Still in progress at read time: closures, coverage, fast (3.14), instrument-self-tests and codeql python. No `pr-contract` or `gate` run had concluded. The block does not rest on CI.
- **Figures not re-derived.** These are the macOS bash 3.2 run at f008c2b75, prepr's 29/9/0 counts, the 688 s serial control, and #2873's 16 min 32 s.
- **Step 6, the class.** The body enumerates `supervise`'s exits and dispositions each one. I agree with that enumeration for the timeout clause; the SIGTERM-handler gap is carried above.
- **Harnesses.** The packet names no finder harness. The round-1 probe (`ev/probe-sigkill-escalation.sh`, copied from 803820f94) is the block's finder harness, and it reproduces the fix. `ev/ymut.py` is my own instrument, disclosed as such: it reuses beatd's `_mutant_copy` and runs the unmutated module's case functions against each planted copy, with a baseline run of the same cases. Every baseline check was true.
