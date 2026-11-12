CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-tick-selftest-checkout, at head a18e2e9d00b17a0349f29938a469d1bc3edd1ae3. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch a18e2e9d00b17a0349f29938a469d1bc3edd1ae3 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-tick-selftest-checkout, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout, even with no code. Then push the code to refs/heads/handoff/r10-hotfix-tick-selftest-checkout, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-tick-selftest-checkout <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-tick-selftest-checkout; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout and refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
Topic: r10-hotfix-tick-selftest-checkout. Round 4 repair, opus.
Resume ref: handoff/r10-hotfix-tick-selftest-checkout @ fbde1675681fb1f8f86e971b923070e8a62b382f.
Model: claude-opus-5-5.

Repair, round 4: a minimal re-cut (the body carries a `## Re-cut` note saying what was cut and why). Third block of class class-open, verdict on probe/revt-r10-hotfix-tick-selftest-checkout-e37fc822, quoted in full below: SPY_REAL_GIT carried from the caller lets a caller's git run inside the offline_spy row and reach a remote while the row prints network=0 remote_git=0; HPO_STATE_DIR, off the allowlist, reaches every row through the PATH computed before the env -i re-exec. Three rounds extended a list and each review found the next name, so the list is the defect. Re-cut to this shape and nothing more:

(1) the self-test's FIRST executable statement re-execs itself under `env -i` with an EMPTY carry list: PATH is a literal built from absolute system directories plus the interpreter directory resolved by absolute path inside the script, HOME and TMPDIR are fresh temp directories, and no caller variable is copied at all; anything a row needs (SPY_REAL_GIT included) the row sets itself to a value the self-test created; nothing is computed from the caller's environment before the re-exec.

(2) One generic poison row replaces the per-name rows: derive mechanically (a grep over tick_loop.sh and every file it sources or runs in the self-test, command and output in the body) every environment variable name read, export each in the CALLER to a unique sentinel (a URL-shaped one for anything used as a remote or a path), run the self-test, and assert no sentinel appears in any row's environment dump, argv or output, and that offline_spy counts zero network and zero remote-git calls; the row fails if the derived list is empty.

(3) Mutants: one that drops the re-exec, one that copies a single caller variable through, one that moves a PATH computation above the re-exec; each must fail the poison row.

Keep the earlier repairs (the 2 MB pipefail pin, the nested row). Loop production lines stay unchanged. No other scope.

Verdict, quoted in full (probe/revt-r10-hotfix-tick-selftest-checkout-e37fc822, verdict.md at c1aa1f74b201dfbe8b4e08a6910ed286106e0264):

----- BEGIN VERDICT -----
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
----- END VERDICT -----
