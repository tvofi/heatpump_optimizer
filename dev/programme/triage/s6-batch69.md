# Proposal triage, session s8, batch 69 (P301-P303)

The rolling batch (V182) after batch 68 (#2985, open). Facts were read at origin/main
`b646e8306`, on the roster branch `origin/handoff/audit-r10-roster` (`4c91e6877`) and in the
orchestrator's `seat-ledger.md` (2471 lines).

## P301: the seat generation token stranded on a done group

Verdict: DEFER, recorded as a drop from R10-ORCH-BEATD. P63's carry (`s6-batch5.md#P63`, the
`seat_gen.py bump|check` generation token) is not re-routed to any live group. R10-ORCH-BEATD
closed without building it. The class it guards is covered today by a cheaper procedural step
and detector, and by the detector P299 adds. No roster op: dropping the carry text from a done
group changes nothing that runs, and the record is this entry.

Source: the orchestrator s8's message of 2026-10-30, item 4 of batch 68's owed list. P299
(`s6-batch68.md`) found R10-ORCH-BEATD `done` on the roster branch (`resume` `{'stage': 'done',
'pr': 2916}`). #2916 built arm (a) only, so P46, P63 and P97 were stranded. P299 re-routed P46
and P97 to R10-FLY-SEAT-ALIVE-ID and left P63 to this ruling.

Instances:
- **P63's basis (2026-10-24).** Three logged two-writer rotations: dispatch w14/w15, merge w3/w4,
  and the #2698 fixer against an update (`s6-batch5.md`, P63 Instances).
- **Since then, the harm P63 prevents has not recurred.** That harm is a superseded seat's
  background job writing through a tracked writer: roster apply, dispatch fire or the
  `merge_train` queue read. `grep -n -i 'duplicate\|double\|two writers\|second writer'
  seat-ledger.md` over lines 1100-2471 (2026-10-26 onward) finds one duplicate seat:
  `seat-ledger.md:1372` and `:1376`, the 2026-10-27 plain `HOLD (no v7.0.5 tag)` triage writer
  (P204). It wrote only ledger lines. It read no brief, so it would never have called
  `seat_gen.py check`: a generation token would not have stopped it.
- **What covers the class now.**
  - P97(a) (`s6-batch21.md`) has the restarting session `TaskStop` the predecessor before starting
    a replacement.
  - The orchestrator's `seat-launch.sh --dup` (P204) reports a second unstopped launch per role.
    It reads clean again since the orchestrator wrote the stop lines for `8741ed6a` and
    `ef0ff4b2` on 2026-10-30.
  - R10-FLY-SEAT-ALIVE-ID (P299) adds `DUPLICATE` and `FOREIGN` in `pulse.py`.

Cost of re-routing P63:
- One S group: a new `tools/audit/seat/seat_gen.py` with its self-test, and a `check` call in
  each tracked writer.
- Two of those writers are hot instrument files: `tools/audit/seat/bus.sh` and
  `tools/audit/seat/merge_train.py`. The third is `roster_queue.py`, which P300 already amends.
- Every standing brief would have to carry its generation, and every restart would have to bump
  it.
- About 2 to 3 opus seat-hours, plus a review round on `merge_train.py`.

Binding: no instance of the guarded harm in the five days since P63, against an S cost across
two hot files plus a per-restart obligation in every brief. The one duplicate seat since then
was of a kind the token cannot bind. An even or worse trade is not accepted, so the carry is
not re-routed.

What would change the answer: one instance, after R10-FLY-SEAT-ALIVE-ID lands, of a superseded
seat writing through a tracked writer. Examples are a duplicate roster apply, a second
`bus.sh dispatch` for one head, or a train queue read by a stopped merge seat, logged in the
seat ledger. That instance re-opens P63 as written, with this entry as its basis.

## P302: the orchestrator's session-local sweep diverges from the tracked one

Verdict: ACCEPT narrowed. Retiring the local sweep is the orchestrator's own act, out of tree, and
is not carried. It is gated on one in-tree arm. The local script's only check that the tracked
sweep lacks is standing-seat liveness by alive file. That arm is R10-FLY-SEAT-ALIVE-ID (P299,
`s6-batch68.md`), and one carry here widens it from "the four standing seats" to every standing
seat the session runs. Two of the filing's in-tree additions are REJECTED as already owned.
- A main-CI arm in the sweep is rejected. `orchestrator_tick.py`'s main-red lane is the one
  owner, and R10-ORCH-BEATD's carry (5) reads "the tick and the sweep do not grow a third".
- Transcript selection by session id is rejected as a tree change.
  `tools/audit/seat/sweep_template.md` already takes `{{transcript}}` as a placeholder
  (line 45), so choosing the session's own transcript is a value in the orchestrator's overlay,
  not code.

Source: `s7/triage-queue-s7.txt` line 15 (orchestrator s8, 2026-10-30T09:49:22Z, s7 audit, class:
session-local sweep).

Instances:
- **The board read red most of the time.** `s7/orch_sweep.sh` is 256 lines and out of tree
  (`git ls-files | grep -c orch_sweep` = 0). `orch-sweep.log`, last written 2026-10-28, holds 31
  `board rc=` lines: 21 `rc=1` and 10 `rc=0`. The filing's (a), a state-beat check that read
  STALE on every pass until the beat was restarted with `--watch-ref main`, is one source of that.
  A board red on most passes trains the reader to ignore it, which is the false-`ok` failure of
  P299 in its other direction.
- **The false `ok`.** P299's instance (`seat-ledger.md:2463`) came from this script's
  mtime-only standing-seats loop.
- **Sibling local copies, read here.**
  - `s7/sweep_mech.sh:12-14` finds a loop's pid with `pgrep -f "$pat" | head -1` and kills it.
    That is a kill by pattern, which the seat preamble forbids because a pattern matches other
    seats.
  - `s7/refresh-orch-wt.sh:30-42` sends TERM, then `kill -9`, to six hard-coded PIDs
    (`PIDS="75660 49908 50095 50419 77035 77036"`). After any reboot or PID reuse, those numbers
    name unrelated processes.
  - `s7/sweep_mech.sh:43-44` still waits on `refs/tags/v7.0.5` and V119-V123.
  - `s7/wt-reap.sh` (94 lines) duplicates the tracked `tools/audit/worktree_gc.sh`.
- **The tracked sweep exists.** `tools/audit/seat/sweep_render.py` (274 lines) renders
  `sweep_template.md` steps (0)-(8): policy re-read, seats, handoffs, merges, the record beat,
  open PRs, queue priority, CI capacity, the tick watcher, verdicts, proposals and disk.

Cost:
- In tree: one carry on a group not yet started. It adds a `seat_alives` placeholder to
  `sweep_template.md`'s table, and step (1b) runs `--seat-alive` once per entry: about 3 lines.
- Out of tree: the orchestrator switches its sweep to the rendered template, with its overlay
  naming the session transcript, and deletes four local scripts (about 460 lines).
- The risk is losing a check only the local script had. The audit above finds liveness only,
  and the carry covers it.
- No capped file is touched. `sweep_template.md` is not capped.

Binding:
- The local sweep is wrong in both directions: red on 21 of 31 logged boards, and `ok` over a
  missing seat. Two of its siblings kill by pattern and by stale PID, which the seat preamble
  forbids.
- Retiring the local sweep removes about 460 untracked lines for a 3-line tree change.
- The kill sites are owed now, independent of the arm: delete `sweep_mech.sh`'s
  `pgrep -f | kill` path and `refresh-orch-wt.sh` before their next run.

Carry text (for `roster_edit.py append-carry R10-FLY-SEAT-ALIVE-ID`, citing
`triage: dev/programme/triage/s6-batch69.md#P302`): "From P302 (queue 2026-10-30T09:49Z, retire the
orchestrator's session-local sweep).
- Step (1b) of `tools/audit/seat/sweep_template.md` runs `pulse.py --seat-alive` once per
  standing seat the session runs, from a new `seat_alives` placeholder (`SEAT=FILE[:MIN]`
  entries, documented in the placeholder table). It does not hard-code four.
- A seat in the overlay with no alive entry is UNREADABLE, never skipped.
- Basis: the local `orch_sweep.sh` watched 3 of 4 standing seats (merge, triage, roster; no tick,
  no dispatch). It is retired onto the rendered template once this group lands.
- Control: `sweep_render.py` over a fixture overlay with five seats renders five `--seat-alive`
  arguments. Null: an overlay with none renders step (1b) without the flag and does not fail.
- Mutant: hard-code four, and the five-seat row fails."

To the orchestrator, not carried:
1. Now: stop running `s7/sweep_mech.sh`'s restart path (`pgrep -f` then `kill`) and
   `s7/refresh-orch-wt.sh` (hard-coded `kill -9`). Delete both, or replace the restart with
   `daemonize.py` by recorded pid.
2. When R10-FLY-SEAT-ALIVE-ID lands, run the rendered sweep (`sweep_render.py` over the overlay,
   whose `transcript` names this session's own transcript by id), and delete `s7/orch_sweep.sh`
   and `s7/wt-reap.sh` (use `tools/audit/worktree_gc.sh`).

## P303: `bus.sh orphans` dies on macOS bash 3.2 on an empty array

Verdict: ACCEPT -> a new S fly-in, **R10-FLY-BUS-BASH32** (`groups/R10-FLY-BUS-BASH32.json`),
with the filing's fix plus a class barrier. The filing's self-test "under bash 3.2 semantics" is
REPLACED by a static check. CI runs bash 5, where an empty array under `set -u` expands cleanly, so
a run-time test there passes on the defect.

Source: `s7/triage-queue-s7.txt` line 16 (orchestrator s8, 2026-10-30T09:54:10Z, instrument
defect).

Instances:
- **The defect.** `tools/audit/seat/bus.sh` sets `set -uo pipefail` (line 135). Lines 645-649
  build `arms=()`, add a flag only for `--no-ancestry` or `--no-content`, and pass
  `"${arms[@]}"` to `ledger.py landed`.
- **Reproduced here.** `/bin/bash` is `GNU bash, version 3.2.57(1)-release`.
  `/bin/bash -c 'set -u; f(){ local arms; arms=(); echo x "${arms[@]}" y; }; f'` prints
  `arms[@]: unbound variable`, rc 127. With `${arms[@]+"${arms[@]}"}` it prints `x y`.
- **The cost of the defect.** `pulse.py`'s opener arm runs `bus.sh orphans` with neither flag, so
  it reads UNREADABLE on every pass on the orchestrator's Mac. A handoff with no pull request is
  invisible to pulse.
- **Since when.** `git log -S'arms+=(--no-ancestry)'` names `d0f6de273` (2026-10-28T11:57Z,
  "orphans: one landed classifier", R10-FLY-ORPHANS-REWRITTEN, done). That is about 46 h.
- **A class, not a one-off.** `bus.sh:134` itself says "Plain variables, no arrays: macOS
  /bin/bash 3.2 rejects an empty array under -u". The same sentence is in
  `body_push.sh:11` and `seat_venv.sh:41`. Each records an earlier instance, and
  `d0f6de273` broke the rule in the very file that states it.
- **Other sites the fixer must classify.** `git grep -nE '"\$\{[A-Za-z_]+\[@\]\}"' -- 'tools/**/*.sh'`
  lists more `"${x[@]}"` sites. Among them are `body_patch.sh:98` (`args`), `cloud_relay.sh:439`
  (`upd`), `pr_args.sh:172,239,242` and `cloud-setup.sh:64,103-119`. Each is either never empty
  or a latent instance.

Cost:
- S: one line in `bus.sh`, a static check of about 20 lines with fixtures, and a one-line
  classification of each listed site. Sonnet fixer, opus reviewer.
- At run time, one grep in an existing self-test family. No API call, no standing CPU.
- `bus.sh` is a hot file, but the edit is one line.

Binding:
- An instrument the sweep relies on has been blind on the orchestrator's host for about 46 h.
- The rule it broke is written in three files and is still broken. Prose is not holding, and
  this is at least the fourth instance, so a static refusal is the cheapest barrier that binds
  where CI runs.
- Rejected: the filing's run-time bash-3.2 self-test as the only control. It is green on Linux
  bash 5 at the defect.
