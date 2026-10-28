Design review: revise fa8200ec0c24cecce1b508148251b03c2bc44a98 architecture-unsound

Reviewed: `dev/programme/designs/R10-ORCH-BEATD.md` at `design/R10-ORCH-BEATD` fa8200ec0, round 1 of 3, from a detached worktree at that SHA (a fast-forward of main aaf8af512 plus the note only). Code was read at aaf8af512. Carries were read on `origin/handoff/audit-r10-roster` aed3322bb, which differs from the note's b36710478 only in other groups' stage and pr fields (`evidence/roster_carries_aed3322bb.txt`). Token count: not reported by this harness.

Checked and holding: the premise table (`_seat_procs` at orchestrator_tick.py:469-485 has no `--self-test` exclusion; `tick_loop.sh:117` calls `heartbeat.sh --once`; `selftest_wiring.py --check` reads 99/99; the `daemonize.py` counts are 2, 3 and 1); archscore dS = 0 (`vector.py:98` reads only `custom_components/heatpump_optimizer`); the carry dispositions for items 10, 30, 34 and 35; the item 23 roster-queue job, the item 28 dead-loop surface (`late`, `DOWN`, `pulse-silent`, and the owner decision routed), and P230/V144 (the job table is the loop list, and `handover_prompt.py` renders it). The section 2 scope finding stays routed as `decision: orchestrator` and is not a revise point.

## Revise points

1. **architecture-unsound: splitting the relay into two concurrent jobs creates a lost-update race on state `cloud_relay.sh` owns.** In note §3, the job table has `relay-probe` (`--arms probe,confirm,stuck`) and `handoff` (`--arms handoff`), each with its own `job` lock. That lets the two run at once. `level_set` (cloud_relay.sh:166-171) is an unlocked read-modify-write of the whole `<log>.level`: it runs `awk` over the old file, writes `$lv.$$`, then `mv`. Both arms call it: handoff at 394-396, 457, 458 and 463, probe at 300, confirm at 337, stuck at 501. When two passes interleave, one kind's OWED lines are dropped from the level the tick reads until that arm next runs. Today `pass` runs the four arms serially in one process (cloud_relay.sh:510), so the race does not exist yet. **Fix wanted:** pick one of these and give it a failing test.
   - Put both relay jobs in one shared lock class (`relay`).
   - Or make `level_set` take a flock on `<log>.level.lock` inside `cloud_relay.sh`, its owner. Its failing test is two concurrent `level_set` calls of different kinds, where one kind is lost today. The null control is the serial pass.
   - Say which, and drop the "no job delays another" claim for the pair if they share the class. (`evidence/relay_level_and_pass.txt`)

2. **class-open: the fetch-race serialisation covers 2 of the at least 8 jobs that fetch.** §3 says "only jobs that fetch in the shared checkout wait", but only `state-docs` and `wt-sync` get the `orch-checkout` class. Many other jobs fetch too:
   - The tick fetches (orchestrator_tick.py:1183 and 1194, 9 sites).
   - The handoff job fetches a plain `refs/heads/$br` (cloud_relay.sh:413). That also updates `refs/remotes/origin/$br`, which is the exact ref lock that killed the state beat in item 28.
   - `relay-probe` (cloud_relay.sh:204), `pitch` (merge_train.py, 18 sites), `roster-queue` (2) and `dispatch` (bus.sh, 12) fetch as well.

   Today they run serially in `tick_loop.sh`. Under the beat they run on parallel threads, so the design widens the race it says it closes.

   **Fix wanted:** for every job, state the checkout it runs in, and say whether it fetches there (measured, per job). Assign `orch-checkout` to every job that fetches in the shared checkout, or give it its own checkout and say why item 8's stale-code objection does not apply. Add an arm (a) failing test: two fetching jobs in one checkout never overlap. The mutant is a job left out of the class. (`evidence/fetchers.txt`)

3. **class-open: the double start is refused only for `tick_loop.sh`'s loop mode.** Other in-scope loops (note §5) can still be started by hand beside the beat with nothing refusing them:
   - `cloud_relay.sh pass --loop` (cloud_relay.sh:504-510);
   - `state_docs.py beat` without `--once` (state_docs.py:444-455; it loops by default).

   Each would run a second relay or state beat. The beat's per-job lock does not stop them, because the scripts never take it. **Fix wanted:** in arm (b), each script's loop mode refuses with rc 75 while `beatd.lock` is held, with a null control when the lock is free and one mutant per script. Alternatively, each script takes its own job's lock itself. (`evidence/queue_and_loops.txt`)

4. **carry not designed: item 18's first alarm.** Item 18 asks for three alarms. These two are designed:
   - lock owner dead (§3, `ALERT lock-owner-dead`);
   - self-test older than 1 h (arm (d)).

   The first is designed nowhere: a handoff tip ahead of its PR head for over 20 minutes. `grep -n -i 'ahead\|20 min'` on the note matches only the §2 sentence (`evidence/item18_grep.txt`). The ledger's 4 h `DISPATCH` aging is a different bound. **Fix wanted:** add it as a status alarm, `ALERT handoff-ahead <pr> age=`, read from the handoff job's `handoff-update` level line age, with a fixture at 21 min, a null control at 19 min and a mutant on the bound. Or route it explicitly to an owner with `roster_edit.py`.

5. **evidence plan, order: arm (a) lands a job table whose argv do not exist until arm (b).** The table names `tick_loop.sh --no-relay --no-heartbeat` and `cloud_relay.sh pass --arms`, both added in (b). At (a)'s head, `pass` refuses an unknown option with rc 2 (cloud_relay.sh:508). A beat started between the two merges also double-runs the relay and the heartbeat, because the tick still runs both. **Fix wanted:** (a) ships the engine with a fixture table only, and the production rows land in (b) with their flags. Or (a)'s self-test runs every row's argv in a dry-run form, and (a) and (b) merge together. State which.

6. **seam: the queue jobs' cursor has no owner.** `roster_queue.py run FIRST LAST` (roster_queue.py:3-5 and 226-230) applies a line range. Today the standing seat chooses that range. The `roster-queue` row elides it (`run …`), and the `dispatch` row says only "per `REVIEW OWED:` line". Neither says who records which lines were consumed (beatd, or the script), where that record lives, or what happens to a partly applied range after a timeout kill (the SIGKILL at timeout+10 s). The status rule `late` = age > interval + timeout is also undefined for `interval: queue`. **Fix wanted:** name the cursor's owner and file. Add a failing test: a range killed mid-op is neither re-applied nor skipped on the next pass. The null control is an empty queue, which reads `ok`, not `late`.

## Notes for the fixer (carries)

- Item 14 says the 60 s floor lives inside `ci-watch.sh` and `proof_watch.py`. The note puts it in beatd's table validation only, so a watcher started outside the beat keeps `proof_watch.py --poll` with no floor. Add the floor in the script as well, with one mutant. Carry: R10-ORCH-BEATD (item dr1-watch-floor-in-script)
- The `heartbeat` job's message is `BEAT <status line>`. Say whether the job calls `beatd status` itself, so a hung status call is bounded by the job's 60 s timeout and never by the beat's own thread. Carry: R10-ORCH-BEATD (item dr1-heartbeat-status-call)
