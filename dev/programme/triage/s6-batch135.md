# Proposal triage, session s13, batch 135 (P424)

Facts read at origin/main `dee8b413f`, the roster branch `origin/handoff/audit-r10-roster`
(`a6c711360`), the remote dispatch and return refs (`git ls-remote origin` at 2026-11-07T21:13Z,
2011 refs), `s9/seat-dispatch/ledger-standin.txt`, `cloud-relay.log.level`, `tick.txt`, and the
session-local watcher `s11/seat_watch.sh` with its loop `s12/seat_watch_loop.sh` and output
`s9/events.txt`.

## P424: a cloud seat channel (CLOUD-SEAT-CHANNEL)

Verdict: ACCEPT, narrowed to part (1)'s detector, as the new group R10-CLOUD-SEAT-CHANNEL. The beat
refs of part (1) are REJECTED. Part (2) is DEFERRED. Part (3) is REJECTED, because it duplicates
R10-TICK-LEVELS carry 14 (P382).

Source: owner ask, queue `s7/triage-queue-s7.txt` line 98 (PROPOSAL 2026-11-07T21:12Z). Named
instance: f-3264-conflict, fired 19:33Z (topic r10-flow-toolkit-model), never returned.

Instances:
- **Return rate.** Script `nr.py` takes each `dispatch/fixer-<topic>` tip and finds the first commit
  after it on `handoff-wip/`, `handoff/`, `handoff-body/` or `fix/<topic>[-pr]`:
  - Last 48 h: 70 dispatches, 59 returned, 11 not. Seven of the 11 are under 1.1 h old and still in
    flight. The four that aged: r10-cop-gate-e 6.1 h, r10-relay-sweep 3.5 h, r10-train-merge-loop-2
    1.7 h (f-3288-r2, 19:32Z) and r10-why-now-widget 1.1 h.
  - Last 7 d: 140 dispatches, 12 not returned.
  - The ref is per topic, so a re-fire hides the run before it. f-3264-conflict (19:33Z) was
    overwritten by f-3264-conflict2 at 21:09Z. The ledger names three more by hand: f-3274-r3,
    p-3290-r3 (a reviewer) and #3055 r3.
  - Settled rate: about 4 to 5 of 65 fixer fires in 48 h, roughly 7%. Reviewers are uncounted
    because the tracked arm does not see them.
- **First-return time** (7 d, n=128): p50 7 min, p90 32 min. Count past each threshold: >45 min 8,
  >60 min 6, >90 min 3, >120 min 2. Maximum 198 min.
- **Detection delay today.**
  - Tracked: `noreturn_arm` (`cloud_relay.sh` lines 678-707 at dee8b413f) fires at
    `HPO_RELAY_NORETURN_SECS` 7200 plus one 120 s pass (line 712). It covers fixers only. Any
    `handoff-wip` move counts as a return, a `BLOCKED.md` tip included.
  - Session-local: `seat_watch.sh 45`, every 900 s, pid 56478, up 3 d. It has emitted 281 QUIET
    lines in `events.txt` since 11-04. A NO OUTPUT line arrives 45 to 60 min after the fire:
    cop-gate-e was flagged at 53 min and relay-sweep at 57 min.
- **The owner's instance is a masking defect, not a missing channel.** `seat_watch_loop.sh` keys
  QUIET on the dispatch ref name alone, through `cut -d: -f1` and `comm`. It does not include the
  dispatch sha, so once a topic is QUIET a later re-fire of that topic never re-emits.
  - `seat_watch.last` holds `fixer-r10-flow-toolkit-model`, from a BLOCKED.md line at 17:04:56Z,
    and `fixer-r10-train-merge-loop-2`, from 11-06 22:38Z.
  - So f-3264-conflict (19:33Z) and f-3288-r2 (19:32Z) were both silent. They are 2 of the 4 aged
    no-returns in 48 h.
  - It also reports a `BLOCKED.md` wip older than the newest dispatch as that run's state.
- **Part (2), measured as far as this seat can.** SendMessage to `cse_0189ZDZDQAhPNhYpnfGHBzMf`
  (an ended 11-01 reviewer session) was refused: "No agent named ... is reachable". The
  `session_` spelling was refused too. This seat has no RemoteTrigger tool, so `list_runs`,
  `last_event_at` and `get_run_log` on trig_013SmQwQRNq9AJ8tvipLAbgD and
  trig_01LCcaHeKwTrSXYsn91fzhz7 were **not read**. A live session id is untested.
- **Part (3) is already owned.** R10-TICK-LEVELS carry 14 (P382, `s6-batch118.md#P382`) is the
  outbound question route, `BLOCKED.md` on `handoff-wip/<topic>`, plus its reader. It has not
  landed: `git show origin/main:tools/audit/seat/orchestrator_tick.py | grep -c BLOCKED.md` reads 0.

Rule run, on the 48 h set. The rule: a dispatch tip whose sha has had no output from its role's
return refs for 3600 s owes a line, keyed by ref and sha.
- It owes r10-cop-gate-e, r10-relay-sweep, r10-train-merge-loop-2 and r10-why-now-widget. That
  includes the two the session watcher masked.
- It would owe flow-toolkit-model at 20:33Z, before its 21:08Z re-fire.
- The 59 returned topics print nothing; that is the null control.
- On 7 d, 6 of 128 seats that did return would have been flagged first. Each flag costs the
  orchestrator one `last_event_at` read.

Cost:
- **Accepted part.** About 60-90 lines in `cloud_relay.sh` (1611 lines, a hot file). The arm
  widens the existing ls-remote from `dispatch/fixer-*` to `dispatch/*` (918 refs). Return refs
  are asked by name per role, so there is no API call and no REST quota cost.
  - Also: one level kind in `ledger.py` `KINDS`, the instrument guide `cloud_relay.sh.md`, and
    self-test arms.
  - No policy file is touched, so there is no `policy_lint.mjs --budgets` row.
  - Once it merges, the orchestrator retires `s11/seat_watch.sh` and its loop.
- **Part (1) beats, rejected.**
  - Every seat would force-push a parentless ref every ~10 min: about 95 fixer fires on 11-07,
    times run length, makes hundreds of pushes a day.
  - It also needs a `ref_privacy.py` disposition, a `prune_refs.py` family, a new write limit in
    the `cloud_dispatch.py` role tail (pinned by its self-test), and a relay arm.
  - A model seat beats only between tool calls. A seat hung in a command therefore stops beating
    exactly when it stops pushing wip, so the beat adds nothing that wip age and the runner's
    `last_event_at` do not already give.
- **Part (3), rejected.** A `seat-msg/` family costs the same ref plumbing as the beats and
  duplicates carry 14.

Binding:
- **Why the narrowed part clears the bar.**
  - Delay falls from 2 h (fixers only) to 1 h for every role.
  - It closes the masking defect that hid the owner's named instance and one other in 48 h.
  - It moves the only working detector out of an untracked /tmp-class script into the tracked
    relay.
  - The cost is about 80 lines with no standing API cost.
- **What changes part (2).** The orchestrator, who holds RemoteTrigger, runs `list_runs` on one
  live trigger. It then sends one SendMessage to that run's session id and reads `get_run_log`
  for whether the seat acted on it. If the message is accepted and acted on, re-file it as a
  `cloud_dispatch.py` brief sentence; there is no ref family to build. If `last_event_at`
  separates live from dead runs on the 6 slow returns, a mid-run silence arm becomes worth
  building on it. Without that read, mid-run "output N min ago" lines stay noise: 39 of 345 wip
  step gaps over 7 d exceed 45 min.
- **What changes part (3).** Nothing until carry 14 lands. Then the question is only whether a
  reply route is needed, which P382's binding already prices.

## P424 part 2, measured by the orchestrator (2026-11-07T21:25Z)
ListAgents from the orchestrator lists no cloud sessions. SendMessage to the live run session_0189ZDZ98Qnzj4zL2MwRqEPB (trig_013SmQwQRNq9AJ8tvipLAbgD, status active/running at 21:04:58Z) was refused: "No agent named ... is reachable." In this host, inbound messages to a cloud seat are unavailable. Part 2: REFUSE (not offered). The detector group stands as ruled.
