# Proposal triage, session s12, batch 119 (P383)

The rolling batch after batch 118. Facts were read at origin/main `d1e7dbbbb`, at the round's roster
branch `origin/handoff/audit-r10-roster` (`37843c16d`), at #3085's code handoff `5e6d43ae1`, at #3197's
head `fe2077441`, in the design note at `21210036`, in the session's logs and in session 11's
transcript.

**Queue.** `s7/triage-queue-s7.txt` has no unruled line. Its last three lines, filed as P372 to P374,
are `s6-batch117.md#P379` to `#P381`. The highest number ruled is P382 (`s6-batch118.md`, #3204). This
entry is the proposal the orchestrator owed from session 11's handoff, and it takes the next free
number.

## P383: a loop whose working directory is gone reads ALIVE

Verdict: ACCEPT, narrowed to two carries. R10-CLOSEOUT-CLEANUP stops the removal: `worktree_gc.sh`
applies its existing `cwd_inside` guard to every removal arm. R10-FLY-STANDING-CONTRACTS part 3 adds
one digest row for the long-lived loops that are outside the beat's job table. The filed form, a
check inside the session-start hook, is left to the orchestrator as a local patch, because that hook
is not tracked and it fired at the right moment on 2026-11-04 and was not acted on.

Source: session 11's handoff to session 12 and the orchestrator's brief of 2026-11-04. orch-wt and
orch-wt2 were found removed under live loops at 18:36Z, and the sweep had been dead for about 2 h. It
proposes that a liveness check read a loop whose cwd directory is gone as DEAD, and asks whether
`worktree_gc` removed them.

Instances:
- **Did `worktree_gc` remove orch-wt2? Probably, but its name is not on record.**
  - #3184 merged at 16:44:33Z (`gh pr view 3184 --json mergedAt`) through `s11/direct_merges.sh`,
    which runs `merge_pr.sh`. The run's output reads `worktree_gc: summary -- eligible 2, removed 2,
    kept 13` (session 11's task output `bzfjtmeas`).
  - `merge_pr.sh` line 301 pipes the tool through `tail -1`, so the two removed paths were discarded.
    `train.log` holds no line of the tool's output either (`grep -c 'worktree_gc: summary'` finds 0).
  - The timing fits. `cloud-relay.daemon.log` holds 57 failing passes before the 18:37Z restart (the
    `could not list handoff refs` lines, lines 7438 to 7824). At `--interval 120` the first of them
    falls no later than about 16:45:50Z. `runner.log` line 326 is the sweep's last pass, at 16:44:20Z.
  - No local seat ran a removal in that window: no tool call between 16:15Z and 17:05Z, in any session
    transcript modified in the last 30 h, names `worktree remove`, `worktree prune`, `worktree_gc.sh`,
    `upd-gc` or orch-wt2.
  - **Not established:** whether orch-wt2 was detached at the time, and why the train's collection
    after #3194 at 16:36:53Z did not take it first.
- **orch-wt was not `worktree_gc`, and no running process had its cwd there.** Session 11 removed it by
  hand at 05:18:07Z (`git worktree unlock` then `git worktree remove --force`, in its transcript). Its
  read at 05:16:10Z shows all six daemon cwds in orch-wt2: pids 262, 15485, 18077, 27798, 61422 and
  61489. One script did depend on the path: `~/bin/power-sync.sh`, which runs on battery only, `cd`s to
  orch-wt on each pass. `power-sync.log` shows 12 passes refused with `cd: ... No such file` on
  2026-11-04, from 05:38Z to about 16:3xZ. It holds no cwd between passes, so this rule cannot see it.
- **The tool removes a held worktree: reproduced.** On a throwaway repository, a detached worktree at
  a proper ancestor of main, clean, with `sleep`'s cwd inside it (`--dry-run`,
  `WORKTREE_GC_MIN_AGE=0`):

  | tool | held worktree | locked worktree |
  |---|---|---|
  | main `d1e7dbbbb` | `remove` | `keep locked` |
  | #3085 `5e6d43ae1` | `remove` | `keep locked` |

  #3085 adds `cwd_inside` (line 545) but consults it only on the `on-remote` arm (line 752).
- **The reader had the fact at 16:52:11Z and acted at about 18:36Z.** The post-compact hook printed
  `ALIVE` for sweep_runner, tick_loop, cloud_relay, opener_driver and head_watcher, `fresh 58s` for
  `tick.txt`, and `MISSING checkout` for both orch-wt and orch-wt2 (session 11's transcript line
  6486). The orchestrator's own account at 18:37:58Z: it read all five loops as alive and moved on.
  - The MISSING line for orch-wt had already printed at 07:38Z and 14:11Z, and that checkout had been
    removed on purpose, so the orch-wt2 line arrived beside one already passed over.
  - The same output's `DEAD triage_loop` was also false: pid 77123 runs as `bash loop.sh` (ledger,
    16:53:56Z).
  - An `ALIVE` loop printed at 16:52:11Z contradicted the true line, and that is the part this rule
    changes.
- **What it cost.**
  - `cloud-relay.log` has no `POSTED` line between 16:25:45Z and 18:40Z, then 5 in the 18:4x ten
    minutes (`awk` over the log, by ten-minute bucket).
  - The relay failed 57 passes; the sweep ran no pass from 16:44:20Z to 18:39:47Z (`runner.log` lines
    326 to 328).
  - The plan's closure read 2026-11-09T18:02Z before and 2026-11-10T03:52Z after. That jump is not all
    this outage's, and it is not attributed further here.
- **Recurrence: 3 events in 9 days, 4 checkouts.** Orchestrator memory
  `live-loop-worktree-collected-under-it` (2026-10-27, a roster loop's checkout) and
  `detached-worktrees-are-collected` (2026-10-30, orch-wt2 and the roster loop's checkout, with 15 ops
  refused from 21:30Z to 23:35Z under a fresh beat), and this one.
- **Rule run: a process's cwd inode against a `stat` of the path `lsof` names.**

  | case | `lsof` inode | `stat` of the path | rule |
  |---|---|---|---|
  | fixture, directory live | 546264970 | 546264970 | ok |
  | fixture, directory removed | 546264970 | no such file | gone |
  | fixture, directory recreated at the same path | 546264970 | 546264987 | gone |
  | fixture, pid exited | none | not read | unread, never DEAD |
  | sweep, relay, tick, opener, heads now (5 loops) | 545239954 | 545239954 | ok, the null control |

  A path test alone misses the recreated row. `lsof` keeps printing the old path, which is why session
  11's read at 18:37:06Z, taken after it recreated the checkouts, showed four loops still on the dead
  directory with a path that resolved.
- **The rule found a live instance.** Across all 387 processes on the host (`lsof -a -d cwd -Fpin`, 0.5
  s with the `stat`s), two read gone: pid 18077, the `wt_sync.sh` loop, and its `sleep 900` child, pid
  85884. `restart_loops.sh` had not restarted it. `s10/wt-sync.log` then ended in `fatal: Unable to read
  current working directory` and held 28 getcwd or "Unable to read" lines. The hook does not list
  wt_sync, so nothing had reported this. The orchestrator restarted it as pid 93480 on this report.
  - Crash snapshots did not stop entirely. `power-sync.sh` is a second caller of `wt_sync.sh`, and
    `power-sync.log` shows it pushing `wip-sync` refs at 19:3xZ and 19:5xZ, on battery. It ended at about
    16:3xZ and its next pass is at 19:3xZ, so this figure does not price the gap. The two writers are not
    carried here: no conflict between them was measured.
- **Carry 1's guard, on the reproduction.** With #3085's `on-remote` condition dropped from the
  `cwd_inside` arm, in a scratch copy: the held worktree reads `keep cwd-inside`, an idle one at the
  same head still reads `remove` (the null control), and the locked one still reads `keep locked`.
  Class A was not run.
- **The beat needs no cwd rule for its own jobs.** `beatd.py`'s `supervise` spawns each pass with
  `cwd=` the checkout (line 336), so a missing checkout is `OSError`, outcome `unreadable`, a `status`
  alarm, and a recreated path heals on the next pass. All 9 rows of `beatd.jobs.json` at #3197's head
  are `orch` jobs. `cloud_relay.sh --loop`, `tick_loop.sh` and `wt_sync.sh` are not rows, and they are
  3 of the loops above.

Cost:
- Carry 1: about 4 lines in `tools/audit/worktree_gc.sh` (701 lines on main, on #3085's own seam) and
  three self-test arms. `cwd_inside` is already built and costs 0.18 s per call here (`time lsof -a -d
  cwd -Fn`, 1167 lines), and only a worktree otherwise eligible pays it. It can only keep more; the
  disk floor is the exposure, at 14 GiB free against the sweep's 15 (`df -g`).
- Carry 2: one row of about 12 lines in `tools/audit/seat/beat_jobs.py`, one row in
  `tools/audit/seat/beatd.jobs.json` and three fixture arms, in a part not yet built. Standing cost:
  `lsof -a -p` at 0.015 s, 6 loops, every 900 s, on the orchestrator host and not on the Pi-class
  target. No GitHub API call.
- Neither file is a policy file, so neither has a `policy_lint.mjs --budgets` row. No new check and no
  new file.

Binding:
- **Why ACCEPT.** The benefit is measured: about 104 min from a true read to action in one outage, 3
  events in 9 days, and one more loop found failing while this ruling was being written. Against it stand about
  16 lines, on seams two open groups already own.
- **Why the removal comes first.** At three events this class owes a barrier, and detection after a
  deletion still costs a restart of every loop. The reproduction shows the guard already written does
  not cover the arm that most plausibly fired.
- **Why not the filed hook check alone.** The hook prints at session start and compaction only, about
  three times on 2026-11-04 by its MISSING lines. It held the fact at 16:52Z, so a tracked copy of it
  adds no earlier signal. A row every 900 s reaches the wake on its own.
- **Refused: logging the removed paths.** It would have shortened this attribution, but with the guard
  in place the tool no longer takes a live loop's checkout, so its benefit is unmeasured.
- **The locks hold until carry 1 lands.** Session 11 locked orch-wt, orch-wt2 and orch-wt11 at
  18:48:19Z, and every live loop's cwd is in one of them. `gc.txt` and the reproduction both read `keep
  locked`. A new tools checkout needs the same lock, and no hotfix is owed.
- **Carry text for R10-CLOSEOUT-CLEANUP:** `worktree_gc.sh` keeps any worktree a live process has its
  cwd in, on every removal arm. Call `cwd_inside` on classes A and B as well as `on-remote`: today only
  the `on-remote` arm consults it (line 752 at `5e6d43ae1`), and a clean detached worktree at a proper
  ancestor of main prints `remove` with a process's cwd inside it (2026-11-04: `worktree_gc: summary --
  eligible 2, removed 2` at #3184's merge, with orch-wt2 under six live loops). Keep the
  `cwd-inside` and `cwd-unread` lines as they are. Fixture arms: (a) class B with a holder keeps
  (`cwd-inside`); (b) class B without one removes (the null control); (c) class A with a holder keeps.
  Mutant: restoring the `onremote` condition fails (a). Answer it in #3085's next repair if that PR is
  still open at dispatch, otherwise in a part 2; do not hold #3085 for it. triage:
  dev/programme/triage/s6-batch119.md#P383
- **Carry text for R10-FLY-STANDING-CONTRACTS, part 3:** add a `loop-cwd` row to `beat_jobs.py` and
  `beatd.jobs.json`, every 900 s, for the long-lived loops outside the job table, named by a new overlay
  key of `pgrep -f` patterns (a lacking key prints `UNREADABLE`, as every row does). For each pid: read
  `lsof -a -p <pid> -d cwd -Fin`, then `stat` the named path. An inode that differs, or a path that does
  not resolve, writes `DEAD <name> pid=<p> cwd gone` to the digest. An `lsof` that returns nothing writes
  `UNREADABLE`, never DEAD. Compare inodes, never only the path: `lsof` keeps printing the old path, and
  a recreated checkout resolves (four loops on 2026-11-04 at 18:37:06Z). A process absent from `pgrep`
  is not this row's line. Fixture arms with a real child process: (a) directory removed writes DEAD; (b)
  directory recreated at the same path writes DEAD; (c) directory live writes nothing (the null
  control). Mutant: comparing only that the path exists fails (b). triage:
  dev/programme/triage/s6-batch119.md#P383
- **What stays with the orchestrator, session-local and no roster op:**
  - in the local liveness hook's `chk`, print DEAD when the same inode rule reads gone, so `ALIVE` stops
    contradicting a true MISSING line; drop a checkout from the hook's list when it is retired on
    purpose;
  - the same rule as a line in the wake's 15-minute blind-spots pass, covering the listed loops plus
    wt_sync, until the beat runs. It retires with carry 2.
