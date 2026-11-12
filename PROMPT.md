CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-tick-selftest-checkout, at head 4145f2852642fd0b5ccb8b7af60d41e896a5eea3. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 4145f2852642fd0b5ccb8b7af60d41e896a5eea3 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-tick-selftest-checkout, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout, even with no code. Then push the code to refs/heads/handoff/r10-hotfix-tick-selftest-checkout, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-tick-selftest-checkout <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-tick-selftest-checkout; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout and refs/heads/handoff-wip/r10-hotfix-tick-selftest-checkout-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
Repair only. Third review round, second block of class class-open (caller environment reaching self-test rows; verdict in probe/revt-r10-hotfix-tick-selftest-checkout-f5be2c74, quoted verbatim below). Resume ref: fb218fa5f70d57a959f362da8074df1145656cf0. Close the class BY CONSTRUCTION, not by adding names to a drop list: the self-test of tools/audit/seat/tick_loop.sh must run its rows under an allowlisted environment (re-exec under env -i with only the variables it needs, each set explicitly: PATH, HOME, TMPDIR and what the rows themselves define), so a variable nobody enumerated cannot reach a row. Enumerate every variable the script reads (a grep over the script for parameter expansions, command and output in the body) and show for each that it is set by the self-test or absent. The verdict found that a URL in HPO_HEARTBEAT_REMOTE makes the self-test force-push heartbeat/orchestrator to it: add a row proving no network or remote-git call leaves the self-test with that variable set in the caller (tools/audit/seat/offline_spy.py is the instrument for that claim). Keep the two earlier repairs (the 2 MB pipefail pin, the nested row). One mutant per new guard. Loop production lines stay unchanged. Model opus.

Run body_push.sh with HPO_HANDOFF_LANDED="python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster" after git fetch origin handoff/audit-r10-roster, because body_push's default checks the roster on origin/main.

Blocked verdict, verbatim:

Fix review: blocked fb218fa5f70d57a959f362da8074df1145656cf0 class-open: caller environment still reaches self-test rows through HPO_HEARTBEAT_REMOTE, TICK_RC, RELAY_RC, HB_RC, SWEEP_RC, SWEEP_WORD; a URL in HPO_HEARTBEAT_REMOTE makes the self-test force-push heartbeat/orchestrator to it

bus-nonce: f5be2c7485f45e7ef0391974c2260967

## Block

Round 2 (a delta review over 81ea9ea2908ea83a012e3e42d694df56bb097c8c, fix-review.md step 12). The delta touches only `tools/audit/seat/tick_loop.sh`, its instrument page and the harness, with no production (`custom_components/`) change, so the scope does not widen.

Both round-1 items are repaired as claimed (see Evidence). The class they belong to is still open. The brief asks whether the caller's environment is closed, and the body names the class as "the caller's environment, enumerated from the script". The rule it uses for that, `grep -oE '\$\{?(HPO|GH|GIT|GITHUB)_[A-Z_0-9]+' tools/audit/seat/tick_loop.sh`, only matches those four prefixes and only reads `tick_loop.sh`. It misses names that the self-test's rows read from the inherited environment:

- `HPO_HEARTBEAT_REMOTE`, read by `heartbeat.sh` (`remote=${HPO_HEARTBEAT_REMOTE:-origin}`). The rows "a real pass moves heartbeat/orchestrator on the remote" and its null control run the real `heartbeat.sh`. Neither the scrub (which drops only `HPO_TICK_*` and `HPO_SWEEP_MANDATE`) nor `throwaway_git_env` drops it.
  - At the head, with `HPO_HEARTBEAT_REMOTE=nope`, the row fails (`ev/probes/headcls-HPO_HEARTBEAT_REMOTE.log`).
  - With `HPO_HEARTBEAT_REMOTE` set to the path of a scratch bare repository, the self-test **force-pushed `refs/heads/heartbeat/orchestrator` into that repository**, subject `TICK-PASS 2026-11-12T20:06:42Z relay=absent tick=0 code=none behind=unknown`, and failed both rows (`ev/probes/headcls-HPO_HEARTBEAT_REMOTE-url.log`, `ev/probes/victim-refs.txt`).
  - A seat that exports this documented override as its real remote's URL would therefore have the self-test overwrite the live liveness ref. That is the same harm this hotfix exists to remove: the self-test acting on something outside its scratch.
- The stubs' own controls: `TICK_RC`, `RELAY_RC`, `HB_RC`, `SWEEP_RC` and `SWEEP_WORD`. Rows set these per command, but every row that leaves one unset inherits the caller's value through `${X:-0}`. Each was set alone in the caller's environment at the head (outer rows only, `HPO_TICK_SELFTEST_NESTED=1`):

  | variable | rows failed |
  |---|---|
  | `TICK_RC=1` | 14 of 31 |
  | `RELAY_RC=1` | 3 |
  | `HB_RC=1` | 3 |
  | `SWEEP_RC=2` | 1 |
  | `SWEEP_WORD=X` | 1 |

  `RELAY_SLEEP=10` failed none (`ev/probes/summary.txt`).

Repair shape, for the fixer to judge:
- Drop `HPO_HEARTBEAT_REMOTE` in the same scrub line.
- Either rename the stub controls under a prefix the scrub drops, or unset them there.
- Widen the body's enumeration rule to every name the rows and the children they run for real read, not only `tick_loop.sh`'s `HPO|GH|GIT|GITHUB` names.

## Findings

## Evidence

- Head reviewed: fb218fa5f70d57a959f362da8074df1145656cf0. The body's `## Head` names the same SHA.
- No pull request exists and no review packet was issued. There is no CI to read, so step 11 has nothing to answer at this head (`merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`, none of them run).
- `review_carry.py 81ea9ea2 fb218fa5` printed `FRESH-REVIEW`, so this is a delta round.
- Role files unchanged between the merge base and origin/main: the `dev/governance/roles/` diff is empty.
- Merge: `git merge-tree --write-tree origin/main fb218fa5` exited 0, printing tree `3668d6f67116cb1a9502e4fef69b0b6e7c9d15f0`. A LEDGER-MERGE line printed while the tree was written: it resolved `tests/closures.json`, merging the `tests/harness_headers.py` inert-read entries as a set. There is no conflict (`ev/merge-tree.txt`). origin/main is now 4145f2852642fd0b5ccb8b7af60d41e896a5eea3, not the body's 3254c38b; the head is behind and merges cleanly.
- `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff from merge base 8c10361eb1.
- RESULT self-test at head: `tick_loop self-test: 36 checks, 0 failed`, rc 0, 78 s (`ev/selftest-head.log`).
- RESULT pipefail mutant: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh fb218fa5 pipefail` printed `pipefail: tick_loop self-test: 36 checks, 6 failed rc=1`. The 2 MB row fails in the outer run and in every nested run, matching the body. The round-1 survivor is killed (`ev/harness-pipefail.log`).
- RESULT envscrub mutant: the harness `envscrub` arm printed `36 checks, 1 failed rc=1`. The failing row is the every-variable nested row, and 12 nested rows are named (`ev/harness-envscrub.log`).
- Each of the ten loop variables was set alone, with the scrub line deleted (outer rows only):

  | variable | rows failed |
  |---|---|
  | `HPO_TICK_RESTARTED=1` | 5 (round 1's figure) |
  | `HPO_TICK_STALE_BOUND=0` | 7 (round 1's figure) |
  | `HPO_TICK_RELAY_WAIT=0` | 6 |
  | `HPO_TICK_SWEEP_EVERY=0` | 1 |
  | `HPO_TICK_CODE_DIR`, `HPO_TICK_CMD`, `HPO_TICK_RELAY`, `HPO_TICK_HEARTBEAT`, `HPO_TICK_SWEEP_CMD`, `HPO_SWEEP_MANDATE` | 0 (each overwritten or harmless per row) |

  The null run with the scrub deleted and no variable set printed `31 checks, 0 failed`.
- Each of the ten loop variables was set alone at the head, full run: every one printed `36 checks, 0 failed`, rc 0. These ten are closed.
- The scratch clone named by `HPO_TICK_CODE_DIR` stayed at its HEAD.
- `HPO_TICK_SELFTEST_NESTED=1` in the caller's environment skips the five nested rows and still prints `0 failed`. That matches the body's disposition. A run with it set is silently shorter but cannot fail falsely.
- RESULT wall-clock row: S31 (the detach line deleted) printed `31 checks, 4 failed` and S34 (serial relay) printed `31 checks, 7 failed`. Both include "a relay slower than the interval does not delay the board". This matches the body's 4 and 7 (`ev/probes/wallclock-S31.log`, `ev/probes/wallclock-S34.log`). The row now asserts that the relay is unfinished, read from the relay's log, and no longer uses a whole-second bound.
- Figures not re-derived:
  - the body's load-average timings (103 s and 96 s) and its 4 of 13 flake count;
  - CI step times;
  - `entities.py`'s `1 of 2708`, which was not run here: it is not in this delta and the run is long.
- Every probe and mutant ran in scratch copies or scratch clones. No live checkout was moved: the worktree at fb218fa5 is still at fb218fa5.
