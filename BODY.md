`tools/audit/seat/tick_loop.sh` ran `cloud_relay.sh pass` and then `orchestrator_tick.py`, one after the other, every pass. A relay pass that drives `update_pr.sh` runs a full `app_push.sh` prepr. On 2026-10-21 that took 27+ min for #2525, and the board went unwritten the whole time: `tick.txt` was 66+ min stale while the loop was still alive. This PR makes the loop write the board every pass, whatever the relay is doing. The tick's owed-level reporting (R10-TICK-OWED-LEVEL) and the orchestrator-continuity root cause (R10-RCA-ORCH-CONTINUITY) are cited here, not redone.

What changes, in `tools/audit/seat/tick_loop.sh`:
- The relay runs detached under a small python holder (`RELAY_HOLDER`). The holder takes the flock `<out>.relay.lock` non-blocking (exit 75 when it is already held). It runs `cloud_relay.sh pass` with its output in `<out>.relay.log`, then writes `<rc> <started-utc>` to `<out>.relay.rc` (tmp file, then rename). Only the holder holds the lock fd, so the lock frees however the holder exits. This is the same flock(2)-holder shape as `update_pr.sh`'s per-branch lock.
- `relay_start` waits for the holder for at most `HPO_TICK_RELAY_WAIT` s (default 30). If the holder finishes in time, the pass reports `relay=ok|rc=N` as before, so a fast relay still runs before the tick. If it is still in flight, it is left running and never killed, because its `update_pr.sh` may be mid-push. The banner then says `relay=running`. A pass that finds the lock held starts no second relay (holder exit 75, `relay=running`), so relay passes never overlap.
- A relay that finished after its own pass's wait leaves its rc unreaped. The next holder refuses to start over it (exit 76). That pass reaps the result, printing the relay's log and `TICK-RELAY <utc> relay=<ok|rc=N> started=<utc>`, then starts its own relay.
- The banner grammar gains `running`: `TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc> out=<file>`. The header comment and `tools/audit/seat/INSTRUMENTS.md`'s entry say so.
- The self-test gains four arms (the brief's arm, plus the no-overlap, never-killed and reap properties the fix claims):
  1. A stub relay that sleeps 6 s, with `--interval 3` and `HPO_TICK_RELAY_WAIT=1`, must not delay the board: the board is written and the pass returns in under the interval, banner `relay=running`.
  2. A second pass while that relay is in flight starts none and still ticks.
  3. The in-flight relay finishes after its loop has exited.
  4. Null control: the next pass reaps the late relay with its log and a `TICK-RELAY` line, and a fast relay reports `relay=ok`.
- `dev/audit/harnesses/r10_seat_selftests_mutants.py` gains S31-S34, so the mutation proof below can be re-run from the tree (fixer step 18). S26's anchor text is unchanged: the reap keeps `[ "$rrc" = 0 ] && rrc=ok`.

Alternatives considered (fixer step 17):
- A plain background `&` with a pid file. Rejected: a stale pid after a crash or reboot needs a liveness guess, and pid reuse can read as a relay in flight. A flock frees on the holder's death with no guess.
- A `mkdir` lock dir. Rejected for the same staleness reason. `CLAUDE.md` also steers seats off `mkdir` locks for the gate lease.
- Starting the relay with no wait at all. Rejected: every pass would report `running`, even for a relay that takes a second, and the banner would no longer say whether the relay passed. The bounded wait keeps the old report for the common fast pass.
- Killing a relay that outlives the bound. Rejected by the brief: an `update_pr.sh` must never be killed mid-push.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01EPHAkAQjbcBBgY6Lom8V9a

## Head

`ab41f4a0f63a4c9bd6b7c58a1a0173ca064dbd4e`, cut from `origin/main` 0cc148b2f80fe224ffe2c504b29fd4f0908183df (the base this seat was given, and `origin/main`'s tip when the branch was cut). Two commits: the fix (99b176491) and the harness arms (ab41f4a0f). Everything below was measured at this head.

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S26 S31 S32 S33 S34` from the committed head. Per mutant, the harness first runs governance.yml's `tick_loop.sh --self-test` step on the unmutated file, then on the mutant, then restores the file's bytes:
- S31, the bounded wait's "still in flight -> `relay=running`" line (`# mut:detach`) deleted, so the pass waits for the relay: KILLED, `tick_loop self-test: 8 checks, 4 failed` (arms 1-4).
- S32, the holder's busy refusal (`except BlockingIOError: sys.exit(75)` -> `pass`), so relays overlap: KILLED, `8 checks, 3 failed` (arms 2-4).
- S33, the late-reap line (`# mut:reap`) deleted: KILLED, `8 checks, 1 failed` (arm 4).
- S34, **the current loop**: the base's serial `bash "$relay" pass` step put back in `tick_pass` in place of `relay_start`: KILLED, `8 checks, 4 failed`. The first failure is `a relay slower than the interval does not delay the board; the banner says relay=running`.
- S26 (existing, relay rc inverted): KILLED, `8 checks, 3 failed`.
- `RESULT survivors=0`.

The same five shapes were first run by hand from a scratch copy of the script. The base's whole `tick_pass` was swapped in under the new self-test, and it gave the same `4 failed` as S34.

## Null control

- The unmutated step at this head: `bash tools/audit/seat/tick_loop.sh --self-test` gave `tick_loop self-test: 8 checks, 0 failed`. The harness also re-runs this per mutant as its baseline (`NOT RUN` otherwise; none printed). Run time is about 7 s, most of it arm 1's stub sleep.
- A fast relay (the four pre-existing arms, and arm 4's second pass) behaves as on the base. The relay runs before the tick (`relay pass` then `tick --only PRS` in the order file), a failing relay reports `relay=rc=3`, and no relay script reports `relay=absent`. Exactly one banner line is printed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0` (every seat step in `instrument-self-tests`, as CI runs them) gave `M0: 0 seat step(s) red`. That run was at the fix's tree, before the harness commit.

## Figures

- `bash tools/audit/seat/tick_loop.sh --self-test`: `8 checks, 0 failed` at head. The base's self-test had 4 checks.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S26 S31 S32 S33 S34`: 5 KILLED, `RESULT survivors=0` (counts as listed under Mutation proof).
- Arm 1's timing rule: `SECONDS` elapsed for one `--once` pass must be under the 3 s interval while the stub relay sleeps 6 s. On the base loop (S34) the pass waits out the 6 s sleep and the arm fails. At head it passes with the wait bound at 1 s.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The changed files are `tools/audit/seat/tick_loop.sh`, `tools/audit/seat/INSTRUMENTS.md` and `dev/audit/harnesses/r10_seat_selftests_mutants.py`. `tick_loop.sh` is gated by governance.yml's `instrument-self-tests` step (above), not by a `tests/` closure.
- `run_always` lines, with `PYTHONPATH=tests/hastub`:
  - `python3 tests/env_drift.py --claims-only 0cc148b2f`: `claims hygiene: ... ok`.
  - `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
  - `python3 tests/layout.py`: `layout self-test: ok`.
  - `python3 tests/harness_headers.py` cannot run green in this container. `seat_venv.sh` failed with `No download found for request: cpython-3.14.7-linux-x86_64-gnu`, and the container's python is 3.11 without numpy. A scratch 3.11 venv with voluptuous gave `72 of 109 HARNESS HEADER CHECKS FAILED` at head, and the same 72 at `origin/main` 0cc148b2f. The diff of the 109 per-check ok/FAIL lines between base and head is empty. So this diff adds no harness-header failure, and CI's run is the proof.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: rc 0. The aggregate lines (always-loaded ~3410, corpus ~61152) are the same at base and head, because `INSTRUMENTS.md` is outside the policy corpus.
- Seams (fixer step 8). Rule: `git grep -n -e 'cloud_relay.sh" pass' -e '\$relay" pass' -e 'cloud_relay.sh pass' -- tools .github`. It enumerates every site that names a relay pass. It returned 6 at head:
  - `tools/audit/seat/tick_loop.sh:60`, the one site that runs a relay pass beside other work: closed in this diff (it was the serial call in `tick_pass` at the base).
  - `tools/audit/seat/tick_loop.sh:7` (header) and `:100` (a self-test arm's name): describe, do not run.
  - `tools/audit/seat/cloud_relay.sh:4`: the usage line. Its `--loop` runs only its own arms, so no board waits on it.
  - `tools/audit/seat/INSTRUMENTS.md:218` and `:551`: describe, do not run.

## Unpinned sites

none: every production line the diff adds is pinned by the self-test arms, and each predicate is mutated under Mutation proof (S31-S34). If `prepr.sh` step 6d lists a site, its disposition is the self-test arm named for that line above.

## Red checks

none

## Forward-carry

none: the change is local to `tick_loop.sh`'s driver. R10-TICK-OWED-LEVEL and R10-RCA-ORCH-CONTINUITY are cited, not reopened, and no later stage's brief changes.

## Friction

- seat_venv: cost: `seat_venv.sh` cannot build `venv-ci` in a cloud container whose uv proxy has no cpython-3.14.7 download, so `tests/harness_headers.py` cannot run green locally. Carry: tools/audit/seat/cloud-setup.sh
