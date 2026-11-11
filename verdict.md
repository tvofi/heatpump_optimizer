Fix review: blocked d68d307421b117a807b0734ccea1e9d57f8b09b6 class-open: fork cap misses descendants that leave the process group (counted, never killed) or the session (never counted)

bus-nonce: 6b2ac7fd24492517b506aa24d3a707d6

Round 1. Handoff review from a detached worktree at the handoff tip d68d307421b117a807b0734ccea1e9d57f8b09b6 (`ev/HEAD.txt`), merge base ee64358be7eeccaec5178a923cb3b83a18a924a0.

## Block

- Process-group escape: the cap counts the whole session (`session_pids`, by `/proc/<pid>/stat` field 6), but the FORKCAP branch kills only the leader's process group (`_killpg` -> `os.killpg(p.pid, SIGKILL)`). A descendant that calls `setpgid` stays in the session, so it counts toward the cap, and survives the kill. `ev/escape_test.txt` chainB: a 150-deep chain whose levels call `os.setpgid(0,0)`, `--fork-cap 32`. It reports `FORKCAP m` in 3 s, then leaves 38 processes running, and 83 three seconds later, still forking. This breaks the brief's acceptance ("leaves no process of its session") and the docstring's "SIGKILLed whole". The fix is to SIGKILL every pid `session_pids` returns, repeating until the list is empty, plus a self-test chain that changes its group.
- Session escape: a descendant that starts its own session (`setsid`, `start_new_session=True`) is never counted. `ev/escape_test.txt` chainA: a 150-deep `setsid -w` chain under `--fork-cap 32` reports `SURVIVED m` after 8 s, never FORKCAP. In-tree commands a mutant run drives do this: `mutant_run.py` itself (its `--self-test` re-runs the driver, and each `run_cmd` setsids), `merge_train.py`, `tests/gate_lock.py`, `tests/entities.py`, `daemonize.py`, `beatd.py`, `open_driver.py`, `judge_batch.py` and `stamp.py`, listed by grep for `start_new_session=True|setsid|os.setpgrp|process_group=` under tools/ tests/ dev/audit/harnesses. So a re-entering mutant in any of them runs past the cap: the incident's class, not its one instance (cloud_relay.sh does not setsid, so the instance the brief names is covered). Either bound the tree by something sessions cannot leave (for example a per-run cgroup `pids.max`, or counting by ancestry from `p.pid`), or disposition this domain in the body with its rule.
- Surviving mutants on the fix's own lines (self-test at the head, 47 checks; output in `ev/mut_<name>.txt`):
  - `forkcap_no_kill` (FORKCAP branch with `_killpg(p)` removed): SURVIVED. The self-test chain (120 deep, 0.02 s per step) finishes on its own inside the 20 s bound, so neither "stopped within seconds" nor "no process left" pins the kill. Without the kill, a truly endless chain blocks forever in `p.wait()`, with no timeout either.
  - `diff_forkcap_branch` (`if rc == FORKCAP_RC:` in `run_diff` -> `if False:`): SURVIVED. A diff-mode FORKCAP then reads as killed and prints nothing, which is exactly "never KILLED", and diff mode has no test for it.
  - `null_forkcap` (`FORKCAP NULL` branch in `run_spec` -> `if False:`): SURVIVED. The documented `FORKCAP NULL` line has no test.
  - `headtail` (STMT_DEL's shared-line skip -> `if False:`): SURVIVED. Nothing exercises `a = 1; b = 2` or `if x: y = 1`. Without the skip, `a = 1; b = 2` becomes `pass` plus EOL and silently deletes `b` too.
  - `session_field` (`split()[3]` -> `split()[2]`, pgrp in place of sid): SURVIVED. The self-test cannot tell group from session, which is the same blind spot as the process-group escape above.

## Findings

none

## Evidence

- RESULT self-test at head: 47 checks, 0 failed, rc 0 (`ev/selftest_head.txt`, run under `ulimit -u ps+300`, timeout 230). This re-derives the body's figure of 47 and 0 failed.
- RESULT body's named mutants: `cap_off` KILLED (1 fail: "forkcap: an endless-style chain past a cap of 32..."); `stmt_dispatch` KILLED (4 fails, the same four checks the body names). Both match the body.
- RESULT extra mutants KILLED: `cap_ge` (cap x100), `spec_forkcap_as_killed`, `print_skip`, `const_skip`, `dedupe`, `argparse_cap`. The ones that SURVIVED are listed under Block. Driver: `/home/user/mut/muts.py`, the reviewer's own loop (one worktree per mutant, the self-test under `ulimit -u` and `timeout 400`). It is not the finder's harness. The brief names the self-test as the harness, and it is what was run.
- RESULT null controls the body claims: bounded 10-process chain unaffected, `--fork-cap 0` SURVIVED, comment/docstring diff lists no STMT_DEL. All three are self-test checks that passed at the head. chainC in `ev/escape_test.txt` (a plain 150-deep chain, cap 32) is FORKCAP in 2 s with 0 left over, the control showing that chains A and B differ only in leaving the group or session.
- RESULT `git merge-tree --write-tree origin/main <head>`: rc 0, no conflict (`ev/merge_tree.txt`).
- RESULT VERSION, manifest version and RELEASE_NOTES.md: untouched. The diff is 2 files, `tools/audit/seat/mutant_run.py` and `tools/audit/seat/instruments/mutant_run.py.md`.
- RESULT `tests/structure.py` at head: STRUCTURE RATCHET PASSED (`ev/structure.txt`). The body's `prepr.sh` rc 0 / MODE: SCOPED was not re-run, so it is not verified here.
- RESULT claim files: the diff does not touch them, and it changes no fixture-producing code, so `env_drift.py --all` was not run.
- RESULT body head line matches the handoff tip.
- No pull request exists yet, so there is no review packet and no CI to read. `merge_train.py owed-reds` was read (`ev/owed_reds.txt`), but with no check runs there is no red to answer.
- Not verified: the body's statement that the carry's acceptance over 23 reviewer-named sites is unmeasured (>=14, today 7). The reviewer has no heads.tsv either. The body routes it to #3394.
- Escape reproduction ran under `ulimit -u ps+400` and `timeout 120`. The chainB leftovers were killed by PID afterwards (`ev/escape_test.txt` last line).
