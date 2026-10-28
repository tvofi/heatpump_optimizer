Fix review: blocked ad1ba9adb7341d31288d27648da09f0ce61def19 harness: design-trace-missing sigkill-escalation: SIGKILL 10 s after SIGTERM (design §2 Run) is never sent once the group leader exits on SIGTERM, so a TERM-ignoring descendant outlives its timeout after the job lock is released; mutant x1 (drop the SIGKILL) survives case (3)

bus-nonce: acf0604d60118fb96f235cad0ed2487f

## Round

This is round 1: PR #2916 has no earlier `Fix review:` comment. Measured head: ad1ba9adb7341d31288d27648da09f0ce61def19, still the PR head when this was written. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Block

The approved note, `dev/programme/designs/R10-ORCH-BEATD.md` §2 **Run**, at 32e249d2e, says: "At its timeout it gets SIGTERM, then SIGKILL 10 s later." `Beat.supervise` sends SIGKILL to the group only from inside `while p.poll() is None:`. When the direct child (the group leader) exits on SIGTERM, the loop ends and the SIGKILL is never sent. A descendant that ignores TERM, or traps it and keeps running, is left alive in the job's process group. `run_one` then drops `<job>.lock` and journals `outcome=timeout`, so the next instance of the job can start beside the orphan. The job lock exists to prevent exactly that overlap.

- **Probe** (`ev/probe-sigkill-escalation.sh`, output `ev/probe-sigkill-escalation.txt`). The job is `bash -c "bash -c 'trap \"\" TERM; …; exec sleep 300' & wait"` with `timeout_s: 2`. beatd returned after 2 s with `rc=-15 outcome=timeout`. 15 s after the timeout, which is past the 10 s grace, the grandchild's `/proc/<pid>/stat` state was `S` (alive). `stubborn.lock` was empty (released).
- **Null control** (`ev/probe-sigkill-null.sh`, output `ev/probe-sigkill-null-leader-ignores-term.txt`). This is the same job, except the leader also ignores TERM. beatd waited the grace and journalled `dur=12 rc=-9 outcome=timeout`, and the grandchild was gone. So the escalation works only while the leader survives SIGTERM.
- **Untested.** The mutant `x1_no_sigkill` replaces `os.killpg(p.pid, signal.SIGKILL)` with `pass`. It survives case (3), so no check in the self-test covers the SIGKILL clause the design names.

The fix is in scope for arm (a). On a timeout, deliver the group SIGKILL after the grace even when the leader has already exited (`killpg` raising `ProcessLookupError` means the group is empty). Then add a case (3) arm with a TERM-ignoring descendant, its null, and x1 as a `MUTANTS` entry.

## Findings

- The SIGKILL escalation does not reach the process group once the group leader has exited (see `## Block`): a TERM-ignoring descendant survives its timeout after its job lock is released. Owed: fixed in this PR's next round, pinned by a case (3) arm and mutant x1. Carry: R10-ORCH-BEATD
- Five reviewer mutants of authored lines survive their nearest case, so these behaviours stated in the docstring or §2 are unpinned (`ev/reviewer-mutants.txt`, harness `ev/xmut.py`, the reviewer's own and not the finder's):
  - `x4_no_heartbeat`: no `RUNNING … elapsed=` heartbeat line every `heartbeat_s`.
  - `x8_watch_as_periodic`: a watch job restarts `interval_s` after its instance ends, not on the periodic grid.
  - `x13_unreadable_staleness_clean`: `status` rc 2 when the staleness read fails.
  - `x15_sigterm_handler_off`: on SIGTERM, beatd stops scheduling and TERMs its running groups.
  - `x16_held_never_dead_clear`: a `RUNNING` line with no `PASS` under a free `beatd.lock` reads as a dead instance, not `running`.

  Each needs a case arm or an explicit deferral. dr3-heartbeat-argv defers only the heartbeat argv to (b), not the journal heartbeat line. Owed: owed in this PR's next round beside the block's fix. Carry: R10-ORCH-BEATD
- `governance / instrument-self-tests` took 26 min 01 s at this head (20:44:19Z to 21:10:20Z) against the new 30-min `timeout-minutes`, so about 4 min of headroom. The body's estimate was about 24.5 min. One slow runner, or the next self-test added to the job, cancels it again. Owed: answer in this PR's next round, by a cap with stated margin or by moving the sleep-bound beatd step to its own job. Carry: R10-ORCH-BEATD

## Evidence

- **Merge.** `git merge-tree --write-tree origin/main ad1ba9adb` exited 0 against origin/main b0b2d7697f8c5baaef2c082d9bf3242b57249e68 (`ev/merge-tree.txt`). No conflict, and no claim file is touched.
- **The PR's mutation proof, re-run.** The run used `HOME=<empty> GIT_CONFIG_GLOBAL=/dev/null /opt/hpo/venv-ci/bin/python -I tools/audit/seat/beatd.py --self-test` at the head (Linux, no committer identity). It printed `beatd self-test: 87 checks, 0 failed`, rc 0. That is 53 case, 17 anchor and 17 mutant `ok` lines (`grep -c`), the body's figure re-derived under its own rule (`ev/selftest-full.txt`).
- **Crash accounting.** The PR's mutant loop records a crashing case as `{target: False}`, so it counts a crash as a kill. `ev/xmut.py` reports a crash separately. None of the reviewer mutants crashed.
- **Reviewer mutants that killed.** x2 (drop `HPO_REAL_GIT` from the job env), x5 (DOWN), x6 (lock-owner-dead), x7 (STALE off by one), x9 (class lock waits 0), x10 (journal line unchecked), x11 (retry any failure), x12 (shim accepted as the real git) and x14 (running ignored).
- **x3 not run.** The anchor `GIT_CONFIG_VALUE_0="30000"` occurs twice (lines 284 and 697), so x3 (dropping `core.filesRefLockTimeout`) was not run. The design's own null has B fail with that env and no shim, so the setting carries no tested effect. This is evidence only.
- **Design §2 failing-test list.** Items 1 to 8 and their mutants and nulls are each present in the self-test and kill.
- **The `named-docs` exclusion.**
  - At the head, `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 50 policy file(s)`, rc 0, and `git diff origin/main -- tools/policy/policy_lint.mjs` is empty (`ev/policy_lint.txt`).
  - Null: with `tools/audit/seat/beatd_shims/git` removed from `corpus_excluded.json`, it printed the `[named-docs] tools/audit/seat/beatd_shims/git` error, `TOTAL: 1 error(s)`, rc 1 (`ev/policy_lint-null-no-exclusion.txt`).
  - Step 14: the movement is earned. The file is an executable that the bare-name pass matched to the English word `git`, which is the exclusion list's stated purpose.
- **Cheap checks at the head** (`ev/cheap-checks.txt`):
  - `throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
  - `selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - Three-dot `git diff --stat b6f6ceca4...HEAD -- VERSION tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt custom_components RELEASE_NOTES.md`: empty. VERSION, the notes and the claim files are untouched, and no manifest change is in the 7-file diff.
  - `PYTHONPATH=tests/hastub tests/entities.py`: `ALL 2467 ENTITY CHECKS PASSED`.
- **CI on this head** (check-runs API, `ev/check-runs.txt`):
  - Green: `governance / instrument-self-tests`, `governance / policy-docs`, `governance / env-matrix`, `tests / closures`, `tests / fast (3.14)`, `tests / mutation`, `arch-score`, `budget-raise-gate`, `codeql / Analyze (actions)` and `codeql / Analyze (javascript-typescript)`.
  - Still running when read: `tests / coverage`, `codeql / Analyze (python)` and the `prelude` of run 40765787881.
  - No `pr-contract` or `gate` run exists on this head yet. The body's `## Red checks` names and answers each check that went red at e09b123f9.
  - The verdict does not rest on CI: the block is a measured defect.
- **Body figures not re-derived** (they are other SHAs or hosts): the macOS bash 3.2 run at f008c2b75, prepr's 29/9/0 counts, and the earlier 16-plant history.
- **The finder's harness.** The packet names none. The design note's §2 test list is the harness, and it is in the self-test. The probes above are the reviewer's own instruments, disclosed as such.
