Fix review: merge 69646cefda47d1c9734d42b56d64cc124888268f

Scope: 8a0ca90a..69646cef is one commit touching only tools/audit/seat/bus.sh, inside self_test (lines 554-560). No production line changes. No transport files in the ancestry (prepr.sh transport check ok).
Portability: the arm uses only POSIX constructs (subshell with exec, $!, kill -0, kill, wait, sleep 3, test -s); no GNU-only tool, nothing bash 4+; `t` is already a declared local. LibreSSL is not involved in this arm.
Runs (Linux, bash 5.2): with a `timeout` shim exiting 127 on PATH (the Mac's condition) 45 checks, 0 failed; system PATH 5 runs, 45 checks, 0 failed each.
Mutants: A (fixer's) `[ $once = 1 ] && return 0` -> `return 0`: 45 checks, 1 failed, this arm. B (new) watch prints "quiet" each idle pass: 45 checks, 1 failed, this arm.
prepr.sh on the body at 86697f38: clean, no refusal, rc 0.
Non-blocking: killing the watcher bash leaves its current `sleep 1` child (or an in-flight git ls-remote) running reparented to init for at most one interval; observed one `sleep 1` orphan just after the test. Self-limiting, writes only to the unlinked wait.out, and cannot change the asserted result, which is read before rm -rf.
