Fix review: blocked fbde1675681fb1f8f86e971b923070e8a62b382f class-open: SPY_REAL_GIT carried from the caller lets a caller's git run inside the offline_spy row and reach a remote while that row prints network=0 remote_git=0; HPO_STATE_DIR (off the allowlist) reaches every row through the PATH computed before the env -i re-exec

bus-nonce: e37fc82251df41bf64e5648719428115

## Block

Round 3, a delta review of fb218fa5f7..fbde167568 (no production `custom_components/` change, so the scope stays the delta). The repair closes the class by construction only for names that are not on the allowlist and are read after the re-exec. Two channels from the caller still reach rows, both measured at this head from a detached worktree, each beside the plain run as its control (`ev/selftest_plain.txt`: 39 checks, 0 failed, real 1m30s, no attacker script referenced):

- **`SPY_REAL_GIT` (on `SELFTEST_ENV`, carried from the caller).** `offline_spy.py:159` takes `real_git = os.environ.get("SPY_REAL_GIT") or shutil.which("git")`, and its PATH git wrapper ends `exec "$SPY_REAL_GIT" "$@"`. So the row that is supposed to prove "no network or remote-git call leaves it" runs every git call through whatever the caller named.
  - `SPY_REAL_GIT=/tmp/evil/netgit bash tools/audit/seat/tick_loop.sh --self-test`: the attacker's git ran 148 times, and each run tried `/usr/bin/git ls-remote https://127.0.0.1:9/hb.git` (148 `attempted-remote rc=128`, `ev/netgit_log.txt`). The row `...passes under offline_spy.py: no network call, no remote git call, its git calls seen` printed `ok`, and the self-test printed `39 checks, 0 failed` with rc 0 (`ev/attack_spy_netgit.txt`). A remote call left the self-test and the row meant to rule that out stayed green. The spy counts what its wrapper parses, not what the binary it execs does.
  - `SPY_REAL_GIT=/bin/false`: that row went `FAIL`, giving `39 checks, 1 failed` with rc 1 (`ev/attack_spy_false.txt`). A caller variable changes a row's verdict.
  - `SPY_REAL_GIT=/tmp/evil/git` (a logging pass-through): 148 calls of caller code inside the row, 19 of them push, fetch or ls-remote, with a green result (`ev/attack_spy_real_git.txt`).
  - Repair direction (not prescribed): the spy row runs `offline_spy.py` with `SPY_REAL_GIT` and `SPY_LOG` unset, or carries them only when the self-test is itself running under a spy wrapper. Add a row that sets `SPY_REAL_GIT` in the caller to a git that reaches a remote, and require the spy row to stay sound.
- **`HPO_STATE_DIR` (off the allowlist) and `HOME`, through `PATH`.** `tick_loop.sh:63-65` prepends `${HPO_STATE_DIR:-$HOME/.local/state/hpo}/bin` to PATH at the script's top, in the caller's environment, before `selftest_allowlisted` runs. `env -i PATH="$PATH"` then carries that directory into every row.
  - `HPO_STATE_DIR=/tmp/evil/state` (`bin/git` a logging pass-through): the caller's git ran 943 times across the rows, including 114 fetches and the nested clones, and the self-test printed `39 checks, 0 failed` (`ev/attack_state_dir.txt`, `ev/state_dir_git_log.txt`).
  - The body dispositions `HPO_STATE_DIR` as "read at the script's top for PATH ... Every nested row sets it". That covers the nested runs, not the outer rows, which inherit the caller-derived PATH. So `tools/audit/seat/instruments/tick_loop.sh.md`'s "no caller variable ... reaches a row" is false at this head.
  - Repair direction: the self-test computes its rows' PATH from the caller's PATH before the seat-bin prepend, or strips that prefix. Pin it with a caller `HPO_STATE_DIR` whose `bin/git` is detectable.

This seat built the attack scripts (`/tmp/evil/{git,netgit}`), not the finder. Their text is `ev/attack_evil_git.sh` and `ev/attack_netgit.sh`.

## Evidence

- Head reviewed: fbde1675681fb1f8f86e971b923070e8a62b382f (`ev/HEAD.txt`). It was re-read before return: `handoff/r10-hotfix-tick-selftest-checkout` and `handoff-wip/...` both point at it, and BODY.md's `Code:` line names it (handoff-body ec0df4aeba).
- Round: third. Scope: the delta `git diff fb218fa5f7 fbde167568`, which touches `tools/audit/seat/tick_loop.sh`, its instrument page and the harness. There is no production delta, so no widening.
- Mutation proof, re-run with the fixer's in-tree harness `dev/audit/harnesses/r10_tick_selftest_checkout.sh` at the head:
  - `envi`: 2 rows FAIL, the every-variable nested row and the spy row (`ev/mut_envi.txt`).
  - `allowlist`: `39 checks, 1 failed`, the refusal row (`ev/mut_allowlist.txt`).
  - Both match the body. The guards are not vacuous. The block is about channels the guards do not cover.
- `git merge-tree --write-tree origin/main fbde167568`: rc 0, no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched against the merge base (`ev/version_untouched.txt` is empty).
- No pull request exists and no CI has run at this head. There is no review packet, no check run to read, and no red that `merge_train.py owed-reds` could name.
- `env -u BASH_ENV python3 tests/entities.py` could not run in this container: venv-ci lacks `homeassistant`, and venv-ha lacks `paho` (`ev/entities.txt`). It is unverified here and left to CI.
- I did not re-derive the body's other figures (load-average timings near 40, the S31 and S34 counts, CI step times): they are host-specific to the fixer's host. The plain self-test time here is real 1m30s, which matches the body's quoted `real 1m30s`.
