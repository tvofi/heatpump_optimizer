Design review: revise a202285df21a43e5f83601e0420d1a18c9f5e2b5 harness

Reviewed: `dev/programme/designs/R10-ORCH-BEATD.md` at `design/R10-ORCH-BEATD` a202285df, round 2 of 3. I read it from a detached worktree at that SHA. Code was read at the note's base `6349205b6`. Its `tools/audit/seat/` differs from current main `6d86acc90` only in `roster_lib.py` and `state_docs.py` (the FLOW-BOARD doc), and none of the fetch lines cited moves. The round-1 verdict read was `d93e1b1f2`. Token count: not reported by this harness.

## Round-1 points

1. **level_set race: answered.** `level_rmw` puts the flock inside `cloud_relay.sh`, the level's owner. It also covers the second writer, `dispose` at :262, which round 1 missed. `git grep 'mv -f "$lv'` finds exactly those two sites. Test (b)1 fails today, has a null control, and has two mutants. The remaining narrower gap is a carry below.
2. **Fetchers: the table is answered, the remedy is not** (revise point 1). The per-job checkout and fetch-site table matches the code at `6349205b6`: tick 418/643/707/1194/1559/2058, relay 190/204/313/413/427, wt_sync 26, roster_queue 110/123, and bus 443. One citation is wrong: :380 belongs to `review_freeze`, inside the handoff arm, so it is a handoff fetch, not a relay-probe one. The class assignment is sound. The `FETCH_HEAD` claim holds: the only reader is `cloud_dispatch.py`, in its own clone. Layer (i), the ref-lock retry that `handoff`, `pitch` and their children rely on, is falsified for the race that actually occurs.
3. **Loop modes: answered.** `tick_loop.sh` without `--once`, `cloud_relay.sh pass --loop` and `state_docs.py beat` without `--once` all refuse through `beatd.py held`. Each has a null control and a per-script mutant in (b)2. `heartbeat.sh --watch` is one check, not a loop, so it needs no refusal. The wt_sync hand loop is a separate miss (revise point 4).
4. **Handoff ahead > 20 min: shape answered, kind not wired** (revise point 2). Carrying `since=` correctly fixes round 1's suggestion, because a pass re-stamps its line.
5. **Arm order: answered for (a)→(b), recurs for (b)→(c)** (revise point 3).
6. **Cursor: answered.** `roster_queue.py` owns `--cursor` and `.inflight`, with per-op resolution and an `unresolved` stop. The registry serves as the dispatch consumed-set. `kind:"queue"` is gone, so `late` has one meaning, and an empty pass reads `ok`. Two edge cases are carries.

## Revise points

1. **harness / architecture-unsound: `core.filesRefLockTimeout` does not survive two real concurrent fetches. Layer (i) is what §3 relies on for `handoff`, `pitch`, `update_pr.sh`, the train and the fixer worktrees.**
   - **The reproduction** (`evidence/reflock_two_fetchers.sh` and `.out`, git 2.38.1):
     - Fetch A holds `refs/remotes/origin/main.lock` for 3 s through a `reference-transaction` hook, then commits the new value. Fetch B starts 1 s later.
     - With the note's `GIT_CONFIG_COUNT=2` env, B waits. It then exits **1** with `cannot lock ref 'refs/remotes/origin/main': is at <new> but expected <old>`, which is git's old-value check.
     - Without the env, B exits 1 with `File exists`.
   - **Effect.** The timeout changes the message and not the outcome. It helps only when a lock is freed with the ref unchanged, and that is exactly fixture (a)6, so (a)6 passes while the item-28 race persists.
   - **Where it still bites.** The tick (fetches `origin main` at 418, 707, 1559, 2058) and state-docs still collide with `pitch`, the train, `update_pr.sh` and `wt_sync`'s full fetch, all of which update the same remote-tracking refs.
   - **Note claims to drop or replace:** §1 row 7, §3 "Two layers close item 28", alternative 4's reason, risk 3, and §8.2.
   - **What does work:** a retry once after rc 1, in the same race, exits 0 at the right value (the appended arm of the evidence script).
   - **Fix wanted:** a mechanism measured against the two-real-fetcher race. Two options:
     - a `git` shim on the beat's `PATH` that retries a fetch once on `cannot lock ref`. There is a shims precedent at `tools/audit/seat/shims`, which `roster_queue.py` already prepends, and children inherit `PATH`;
     - or beat jobs fetch into job-private destination refspecs and read those.
   - **Test and controls for either:** replace (a)6 with the hook fixture above. Fixed: B exits 0 and the ref equals origin. Null: no beat env, rc 1. Mutant: drop the retry or shim. State which children the mechanism reaches.

2. **class-open / seam: the new `handoff-ahead` level kind misses its schema owner and the tick.**
   - **Unknown kind refused.** `ledger.py` `KINDS` (90-95) is the one schema of level kinds. `orchestrator_tick.py:749-754` prints `REFUSED: a level line of no ledger kind` for any line outside it, flagged, every pass. The note names neither `ledger.py` nor the tick for (b).
   - **Spurious OWED once added.** Once added as `derived`, the tick prints every line flagged `OWED:` from its first pass. The line is written at the :415 test, before the update. So every normal handoff, one that is updated in that same pass, puts a flagged OWED on the board until the next pass, and it never reaches 1200 s.
   - **Fix wanted:**
     - add the kind to `KINDS` in (b), with `ledger.py`'s self-test;
     - write the line only for a PR still ahead when its iteration ends: busy 75, failed, no body, or no update attempted;
     - state what the tick prints for it before 1200 s, either filtered or escalated on `since=`, with a fixture at each side.
   - **Test additions to (b)3:** a pass whose update succeeds leaves no `handoff-ahead` line (mutant: write at :415). (`evidence/handoff_ahead_kind.txt`)

3. **evidence plan, order: round-1 point 5 recurs between (b) and (c).**
   - **Contradiction.** (b) says `beatd.jobs.json` "lands here with every row", and its self-test asserts every row's flags are accepted. But the `roster-queue` row's `--cursor` lands in (c), and `roster_queue.py run` has no such option at `6349205b6`. The `dispatch`, `ci-watch` and `proof-watch` jobs are listed under (c) too. (b)'s own self-test would fail at (b)'s head.
   - **Undefined key.** The table key `phase` (`b|c`) is defined nowhere.
   - **Not an argv.** The `dispatch` row (`bus.sh dispatch` "for each `REVIEW OWED:`…") names no argv, and no script that owns parsing the board. `beatd.py` owns only the schedule (§2), so that loop needs an owner.
   - **Fix wanted:**
     - (b)'s table holds only rows whose argv exist at (b);
     - (c) appends the other four with their flags;
     - define `phase` or drop it;
     - name the dispatch job's argv and the script that owns iterating the owed lines. (`evidence/arm_b_c_rows.txt`)

4. **class-open: a hand launch of a beat job's script survives the beat.**
   - **The instruction.** `dev/governance/roles/nudge.md:113` tells the orchestrator: "If no sync loop is running, start one detached with `tools/audit/seat/wt_sync.sh` … Do not start a second."
   - **Why nothing refuses it.** Under the beat, `wt-sync` is a one-shot job that runs every 900 s, so no sync loop is ever visible. `wt_sync.sh` has no loop mode for (b)2's refusal.
   - **Why §5 missed it.** §5's hand-launch class keys on `daemonize.py` (2, 3 and 1 hits) and does not catch this line.
   - **Fix wanted:** grep the policy corpus for every job's script name, not for `daemonize.py`. (c)'s policy text then rewrites each hand launch, `nudge.md:113` included, to "the beat runs it", with a rendered-text control. (`evidence/hand_launch_sibling.txt`)

5. **harness / evidence plan: arm (d1) and (d3) are not concrete against arm (c)'s retirement.**
   - **(d1).** (d1) builds `--seat-alive` and `DUPLICATE` for the standing seats (`pulse.py` `STANDING`: tick, merge, dispatch, roster). But (c) retires tick, roster and dispatch (carries 11, 23, 33). The tree also has no writer of a `<seat>.alive` file, nor of "one entry per seat id": the only `--alive` in the tree is `roster_queue.py`'s, which the beat replaces.
   - **(d3).** (d3) leaves "measure the tracked writers per standing seat at main" to the fixer. Two of item 19's three writers, the roster apply and the dispatch fire, become single-instance beat jobs in (c).
   - **Fix wanted:**
     - name the seats that survive (c);
     - give (d1)'s alive-file layout and who writes it, for those seats only;
     - for (d3), do the measurement in the note: list each writer that remains seat-driven after (c), with file:line;
     - wire `check` there, or record a two-word-plus dismissal per retired writer. (`evidence/arm_d.txt`)

   (d2) is concrete as written.

## Notes for the fixer (carries)

- Fixture (a)8's mutant `≥ 1260` survives the 21-min (1260 s) fixture: both alarm. Use fixtures at 1201 s and 1200 s, or a mutant the 21-min case kills, such as `> 1260`. Carry: R10-ORCH-BEATD (item dr2-ahead-boundary)
- The confirm arm copies an existing `confirm-owed` line from a read at cloud_relay.sh:315 to its `level_set` at :337. A hand `dispose` in between is undone, and `level_rmw` does not cover that window. Check `disposed` before carrying the line, as the probe arm does at :275. Carry: R10-ORCH-BEATD (item dr2-confirm-carry-dispose)
- The `level_rmw` holder: `STUCK_PY` (:477) is a lock probe, not a holder. The pattern to reuse is `tick_loop.sh`'s `RELAY_HOLDER` (48-60), which takes the lock and runs a child under it. Carry: R10-ORCH-BEATD (item dr2-holder-pattern)
- An `.inflight` line re-applied after a kill can meet the killed run's `--worktree` left behind, and would then read `refused`, so the cursor advances past it. Remove the stale worktree before re-applying. Carry: R10-ORCH-BEATD (item dr2-inflight-worktree)
- `bus.sh dispatch` appends the registry with no lock (:479). The unclassed `handoff` job's dispatch (cloud_relay.sh:452) and the `dispatch` job can both mint for one (pr, head). Add a concurrent case to (c)4, or lock the registry in `bus.sh`. Carry: R10-ORCH-BEATD (item dr2-dispatch-double-mint)
- §3's table cites cloud_relay.sh:380 under `relay-probe`. It is `review_freeze`, called by the handoff arm. Carry: R10-ORCH-BEATD (item dr2-380-citation)
