R10-HOTFIX-OPENER-UNBLOCK: the opener's two blockers, in two seams and disjoint files. Hotfix by owner ruling (tvofi, 2026-11-11T20:13Z).

- **Part A, BEAT-STALE-CHECKOUT (P581), `tools/audit/seat/beatd.py`.** After every PASS (never under `--once`), the beat counts origin/main's commits over its own checkout on `tools/audit/seat` and `tools/pr`. Those are `pr_args.sh` `pr_tools_fresh`'s paths, whose STALE CHECKOUT refused the opener. If the checkout is behind, no job instance is running, the tracked tree is clean, `git rev-list origin/main..HEAD` is empty, origin/main's `beatd.py` compiles, and the beat has not already restarted to that origin/main sha (guard `HPO_BEATD_RESTARTED`), the beat restarts. It runs `git checkout -q -B <branch> origin/main` (`--detach` on a detached head), journals STOP, prints `BEAT-RESTART`, and re-execs itself in place with the same arguments. Once the restart is taken, `run_one` starts no new instance. Any other outcome prints `beatd: NO-RESTART behind=<n> code=<sha12>: <why>`, and from the second consecutive refusal also `BEAT-STALE <utc> ...`. A running instance only defers the restart to the next PASS. STATUS's `STALE-CODE`, which counts every commit, stays the alarm. The checkout path does not change, so beatd.tools, the orch checkout and the launch files are untouched. There is no separate rotate instrument (rejected in the ruling).
- **Part B, OPENER-LIVE-TIP (P603), `tools/audit/seat/open_driver.py`.** When origin's handoff tip differs from the board line's sha, the pass logs `RETIP <topic> <board sha8> -> <tip sha8>`. It then runs every candidate check (batched, no-body, seen, landed, fix-branch, live, stuck, backoff) and the open at the live tip. `SKIP moved` stays only when origin has no handoff ref for the topic. `ct` stays the board line's, so STARVED ages from the line's commit.

- **Test hermeticity, `tests/gate_lock.py` `_priority_cases`.** `prepr.sh` exports `HPO_GATE_PRIORITY` from the branch name, and it is 2 on a hotfix branch. The arms `priority_first` and `slot_priority` started their normal waiter outside `_Env`, so it inherited 2, both waiters were urgent, and the queue released them in FIFO order. As a result, `tests/entities.py` failed under prepr's closures recording (`2 of 2705 ENTITY CHECKS FAILED`, three runs of three on this branch), but not when run standalone. Each normal waiter now enters under `_Env(None)`.

Alternatives considered: Part A could poll on a timer thread instead of after each PASS. That lost because it adds a second scheduler beside the job loops, and "between passes" is exactly the PASS boundary. Part A could also exec from inside `Beat.run`. That lost because `cmd_run` must drop `beatd.lock` first, which its `finally` does.

## Head

80779d2e7492c8aaf1b4b4608d3f6b93a45dcffd. Merge base and origin/main are both 61afd4f2db10341ab9b86583944402b206eb4c78, at 2026-11-11T20:37Z.

## Mutation proof

Part A, `python3 -I tools/audit/seat/beatd.py --self-test 9`. Each of the 10 mutants turns its named case-9 check red:
- `m9_paths_unfiltered` (drop the path filter) -> `null: behind only off the seat paths does not restart`
- `m9_guard_off` -> `the guard: already restarted to this origin/main refuses with its why`
- `m9_dirty_ignored` -> `dirty: refuses with its why`
- `m9_local_commit_ignored` -> `local: refuses with its why`
- `m9_compile_unchecked` -> `broken: refuses with its why`
- `m9_running_ignored` -> `a running instance defers the restart to the next pass`
- `m9_stale_never` (BEAT-STALE from the third refusal) -> `dirty: a refusal persisting into a second pass prints BEAT-STALE`
- `m9_no_exec` -> `behind on the seat paths and idle: checks out origin/main and re-execs`
- `m9_once_restarts` -> `--once never restarts`
- `m9_no_start_gate` -> `once a restart is taken no job instance starts`

Failing test first: case 9 run against the production code of the merge base printed 9 FAIL of 10. The one pass was the null control.

gate_lock arms: with `_Env(None)` removed (the merge base's form) and `HPO_GATE_PRIORITY=2` exported, 2 of 14 `_priority_cases` fail: `priority: an urgent waiter takes before an older normal one, after its ticket rewrite` (order `['normal', 'urgent']`) and `priority: the heavy-slot pool orders by the same rule`. At the head, 0 of 14 fail.

Part B, `python3 dev/audit/harnesses/r10_open_driver_mutants.py`:
- `M-livetip` restores `SKIP moved` on a mismatched tip. Verdict `killed failed=2`: `live tip: a board line at A with origin's clean tip B opens at B` and `live tip: the checks run at B, so a landed B is skipped landed, never opened`.
- `M-moved-gone` drops the gone-ref skip. Verdict `killed failed=1`: `null: a line whose handoff ref is gone still prints SKIP moved`.
- `M0` (nothing mutated): `null-ok`.

Failing test first: the new checks against the merge base's `open_driver.py` printed those two FAIL lines (93 checks, 2 failed).

## Null control

- Part A: on a checkout behind origin/main only off the seat paths (`docs/zz.md`), the beat does not restart. It keeps one START at C1 with HEAD unchanged, and prints neither BEAT-RESTART nor NO-RESTART. `--once` never restarts. With no restart taken, the gated `run_one` runs its job.
- Part B: a board line whose handoff ref is gone prints exactly `SKIP r10-cp <sha8> moved` and opens nothing.
- On the merge base, the beat never restarts. In the case-9 fixture its journal holds one START at C1, and the opener skips every mismatched line as `moved`.

## Figures

- `python3 -I tools/audit/seat/open_driver.py --self-test`: 93 checks, 0 failed at the head. The merge base has 91 checks; the head adds 3 and replaces 1.
- `python3 -I tools/audit/seat/beatd.py --self-test 9`: 34 checks, 0 failed at the head, mutants included.
- `python3 -I tools/audit/seat/beatd.py --self-test`: 153 checks, 0 failed at the head (every case and mutant).
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: M0 `null-ok`, M-livetip `killed`, M-moved-gone `killed`. Then `ABORT M-exact: pattern occurs 0 times`, rc 2. The harness aborts the same way on a `git archive origin/main` copy at the merge base, so the abort predates this diff (see Friction).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/doc_claims.py`, `tests/entities.py`).
- `HPO_GATE_PRIORITY=2 python3 -c '... gate_lock._priority_cases(gate_lock) ...'` (run from `tests/`): 2 failed of 14 at the merge base, 0 failed of 14 at the head. With the variable unset: 0 failed of 14 at both. With `HPO_GATE_PRIORITY=1` at the base: 0 failed of 14, so only an inherited urgent priority breaks the arms.
- `HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2705 ENTITY CHECKS PASSED`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 315 checks PASSED`.
- `tools/pr/prepr.sh` at the head: rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- Field figures: re-measured on the beat host, not here, because this container holds no `open-driver.log`. The enumerators are:
  - moved skips: `grep -E '^<day>' open-driver.log | grep -cE 'SKIP \S+ \S+ moved'`
  - STALE CHECKOUT refusals: `grep -cF 'STALE CHECKOUT' open-driver.log` over the RESULT lines of the same window

  After this merge, moved skips count only topics whose handoff ref is gone, and a STALE CHECKOUT refusal no longer persists past the beat's next PASS.

## Red checks

none

## Forward-carry

none

## Friction

- harness-stale: stale: `dev/audit/harnesses/r10_open_driver_mutants.py` aborts with `ABORT M-exact: pattern occurs 0 times`, rc 2, at the merge base 61afd4f2db. Four plants no longer occur once in `open_driver.py`: M-exact, M-body and M-triageB now live in `topic_grammar.py` (since a7fd743e5), and M-crit matches neither file. So the harness's `survived=0` claim has not been runnable since that extraction. This diff's two plants are placed ahead of them and run. Carry: R10-SEAT-IDENTITY-P5
