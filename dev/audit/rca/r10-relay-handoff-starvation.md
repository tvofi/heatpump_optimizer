# R10-RCA-RELAY-HANDOFF-STARVATION: returned handoffs wait behind one serial relay pass, and a stale merge verdict freezes a DIRTY head

Root-cause seat, `dev/governance/roles/root-cause.md`, run beside the tick and relay and inside neither. Read
at `origin/main` 28596c569 and the PR heads and handoff refs as fetched at 2026-11-08T10:24Z. Trigger: the
third instance of one class on 2026-11-08 (`defect-root-cause.md`: a PR waited on a gate that a cheaper
detector, here a lag read from refs, could have flagged). No tool under `tools/` is edited here; the one file
added besides this record is the detector, `dev/audit/rca/relay_handoff_lag.py`.

**What was not readable.** The orchestrator's `tick-loop.log` and the relay log live in the orchestrator's state
directory, which is not in the tree and not reachable from this seat. Every claim about `relay=running` and
`TICK-STALE behind=13` is the orchestrator's record, not re-read here; the code that produces those lines is
read below. Each number in this record comes from git (`for-each-ref`, `log`, `merge-base`, `merge-tree`) and
says which.

## 1. The named cause

Two mechanisms, both in code read this session.

**A. One serial pass, and its first arm waits on the slowest update.** `cloud_relay.sh` `pass()` runs
`handoff_arm; probe_arm; confirm_arm; stuck_arm; noreturn_arm` in sequence, and `tick_loop.sh` starts that pass
under a non-blocking flock (`<out>.relay.lock`; "a pass that finds one in flight starts none"). Inside
`handoff_arm` the per-PR loop is `while read ... done < cloud-prs`, and each update is launched and then
`wait`ed (`wait "$PR_REAP_LEAD"`). `update_pr.sh` takes a per-branch lock and, unless the head qualifies for
`--row-only` or `--reuse`, runs the full `prepr`; its header and `tick_loop.sh`'s own comment record that one relay pass
"ran 27+ min (update_pr.sh's prepr, #2525)". So the handoff of PR B is not looked at until PR A's update returns,
and nothing after the handoff arm (verdict relay and confirm, stuck and no-return levels) runs either. The
ordering is a property of the loop and the lock, not of any one PR.

**B. The restart that would pick up fixed relay code refuses while a relay is in flight.** `fresh_check` sets
`stale=1` for a commit touching `cloud_relay.sh` or `tick_loop.sh` (`self>0`), and restarts only if
`LOCK_FREE` holds on the relay lock (`why="a relay is in flight (the lock is held)"`). So a long pass keeps
itself, and the code that could shorten it, out of reach: the tick prints `TICK-STALE` and skips the relay arm
(`relay=stale`) or reports `relay=running` for every pass while the one pass lasts.

**C. Why a DIRTY head with a merge verdict is frozen.** `review_freeze` returns `VERDICT` when
`verdict/<pr>`'s tip is `Fix review: merge <head>` at the PR's live head, and `handoff_arm` then prints
`HELD-VERDICT` and does nothing: "moving it voids the merge it is waiting on". The rule checks that the verdict
names the live head. It does not check that the head can still merge. #3297 is that case, measured:
`verdict/3297` tip `d91a3b36e` is `merge 2d010b09` (committed 2026-11-08T06:49+01:00); `fix/r10-hotfix-cop-unmeasured`
is still `2d010b09`; `git merge-tree --write-tree origin/main origin/fix/r10-hotfix-cop-unmeasured` exits 1 (a
conflict, the DIRTY predicate `fixer.md` and `update_pr.sh` use) and main is 367 commits ahead; the handoff
tip `68b0735be` (2026-11-08T08:51:39Z) is not in the head, so it sat at least 93 minutes at 10:24Z. A verdict at
a head that conflicts with main is void in effect: the PR cannot run CI (`claim-files.md`: a DIRTY PR "does not
go red, it cannot run") and `main-protect-checks` cannot pass it. The freeze protects a verdict nobody can use,
and only `<state>/cloud-handoff-release`, edited by the orchestrator, lifts it.

**Which side moved** (git, not an error text). #3297's head did not move after the verdict (`2d010b09` is the
verdicted head); main moved (367 commits) and made the head conflict. The relay's rule and the verdict stayed put.
For the lag, the handoff refs were pushed by the fixer seat and the PR heads were moved later by a merge commit
on the PR branch; table in section 3.

## 2. The process state: (d), and why the existing barrier unit did not reach it

State **(d): sound at design, preconditions changed underneath it.** The serial pass and the freeze were each
built for a small round: few open PRs, an update that is `--row-only` or `--reuse` (seconds), and a verdict
whose head stays mergeable until the merge. Round 10 runs many open PRs, main moves every 10 to 20 minutes
(the stamp v7.1.6 and PR merges between 08:00 and 10:25 local), every handoff therefore needs a merge of
`origin/main` (the three named handoffs are all `Merge origin/main (v7.1.6) into ...`), and that merge sends
`app_push.sh` to the full prepr, not the reuse path, whenever the live head moved too. Neither the pass nor the
freeze notices that its premise (short update; mergeable verdicted head) stopped holding. This is not (b): the
`r10-tick-relay-decouple` change and the HELD rules were followed and did what they say. It is not (c) for the
decouple either: it removed the relay from the board's critical path, which is the unit it set out to fix, and
the board is fresh; the relay pass's internal serialisation was outside its unit.

Why the barrier unit missed it (`root-cause.md` section 2). The nearest classes, `N-orphaned-handoff` (barrier
null, status `prototype-only`) and `N-silent-stop`, have units that do not reach this instance:
`N-orphaned-handoff`'s detector idea is a handoff ref with **no pull request** past a window; here every handoff
has an open PR and the obligation is recorded on the level (`handoff-update`, `handoff-held`), so that unit is green.
`N-silent-stop` is about a liveness level nobody can read; here the level is readable and printed on each pass
(`HELD-VERDICT`, `relay=running`) and nothing consumes its age. No existing unit measures **lag between a handoff
tip and the PR head that carries it**; that is the unit this record adds, as a detector. Neither class carries a
barrier, so no barrier existed to fail: the countermeasure is a new class, `N-relay-handoff-starvation`.

## 3. How far the class reaches

Searched: every reader of the relay lock, the freeze files and the serial pass (`grep` for `relay.lock`,
`cloud-handoff-release`, `cloud-handoff-hold`, `review_freeze`, `cloud_relay.sh pass`), over `tools`,
`.claude` and `dev/governance`.

- **Same serial pass** (mechanism A): `probe_arm` (verdict relay, `probe/rev-*` to `review/<pr>`), `confirm_arm`
  (posts the verdict on the PR through `bus.sh confirm`), `stuck_arm` and `noreturn_arm` all run after
  `handoff_arm` in the same flock-held pass. A verdict waiting to be relayed or posted waits behind a slow
  handoff update too, on every PR, not only the one being updated. `standing-dispatch.md` names exactly this
  pass as the verdict relay ("`cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts").
- **Same lock** (mechanism B): `tick_loop.sh` `fresh_check` (restart) and `relay_start` (no second relay) read it;
  `heartbeat`/TICK-PASS print `relay=running` for it, so a long pass shows as "alive" on the board.
- **Same freeze rule** (mechanism C): `bus.sh` (the merge train reads `cloud_relay.sh held`, the hold file only,
  not the freeze), `owed_unactioned.py` (its header records an earlier 1.7 h on `repair=review` while the relay
  printed `HELD-REVIEW` every pass) and `HELD-REVIEW`, which has the same shape: a review of a head that a
  later main move made DIRTY holds the update for a review whose verdict cannot be used.
- **Measured reach by ref lag.** `python3 -I dev/audit/rca/relay_handoff_lag.py --repo . --since <2026-11-04>`
  (run at 2026-11-08T10:24Z; refs only) scores 10 carried handoffs and 4 uncarried: lags (minutes, handoff-tip
  commit to first carrying commit) 717, 421, 394, 334, 158, 129, 61 (`r10-min-power-floor`, the named #3308),
  45, 35, 9. This is an **upper bound on starvation, not a measure of it**: the interval also holds a fixer
  waiting for review and orchestrator choices, and the tip time is the commit's, not its push's. Only #3308 is
  both named in the trigger and measurable here (61 min). #3299 (`r10-generic-heat-curve`) and #3310
  (`r10-fly-triage-bar`) read `uncarried` today: their handoff tips are not ancestors of the PR heads, so the
  hand updates the orchestrator recorded were not by merging that tip, or have been superseded since; the
  20 to 60 minute figure for them is the orchestrator's record and is not re-derived. The author is the same
  App identity for relay and hand updates, so the lag table cannot split relay from hand; the log can.
- **Null control for the detector.** `--self-test` builds a synthetic origin with a handoff carried after
  2 min, one after 40 min and one never; it reads 2 and 40 and scores the third as `uncarried`, not as late:
  `self-test ok: fast=2m (green), slow=40m (LATE at 15m), never=uncarried (not scored)`. Red on the defect
  (40 min and the real 61 min row at the 15 min limit, exit 1) and green on the control (2 min, `late=0`
  on a tree of carried-fast handoffs).

## 4. Cost test (`cost(countermeasure) < cost(defect) x P(recurrence)`)

Unit: wall-clock minutes per occurrence over the current release cycle.

- **cost(defect).** Per instance: measured 61 min on #3308 (ref times above); the orchestrator's record gives 20 to
  60 min on the other two; #3297 held at least 93 min at 10:24Z and released by hand. Per instance one PR idle
  and one hand intervention (`update_pr` or an edit of `cloud-handoff-release`) by the orchestrator; four
  interventions on 2026-11-08 alone. While the pass is long, the verdict relay and confirm for every other PR
  wait too (section 3), which this seat cannot count without the log.
- **P(recurrence).** One in every pass whose handoff arm meets a non-reuse update, with main moving every 10 to 20
  minutes: on the day's evidence, four of the day's handoffs. The refs lag table: 9 of 10 carried handoffs since
  2026-11-04 exceed 15 min (upper bound). Taken as roughly 4 per day through round 10.
- **cost(countermeasure, recurring).**
  1. *Auto-release of a verdict whose head conflicts with main.* `git merge-tree --write-tree origin/main <head>`
     once per `VERDICT` or `REVIEW` hold, one command on already-fetched objects, about 0.1 to 0.5 s per held PR
     per pass and no REST call (the owner's API order). Removes mechanism C entirely and is the rule `fixer.md`
     already states for when main is merged.
  2. *Per-PR parallel or bounded-time handoff arm*: run each update in the background under its existing
     per-branch lock (`update_pr.sh` already refuses a second run on a branch with 75), at most 2 at once, and
     give `pass()` a wall limit so `probe_arm` and `confirm_arm` always run. Standing cost: one extra prepr
     of CPU on a shared host while two run; no extra API call. Removes A and, by a shorter lock hold, B.
  3. *Lag level on the board*: this record's detector over refs, one line per handoff older than 15 min, ~1 s per
     tick. Detects, does not fix.
- **Result.** Taking 4 x about 45 min = about 180 min of idle PR time and 4 hand steps per day against a standing
  cost of seconds per pass (1, 3) and one extra concurrent prepr (2): all three pass the test. The
  countermeasures belong to the relay and tick, which this seat does not edit, so they are **proposals for the
  fixer seat and the owner** (a change to `cloud_relay.sh` and `tick_loop.sh` is a tool change that takes a
  mutation proof and a review; the freeze rule's change touches a documented policy in
  `cloud_relay.sh`'s header and, if the verdict rule changes, `fix-review.md`, so the owner approves it).

## 5. Countermeasures, by state (d)

For (d) the countermeasure is making the process notice its own precondition change, not a new rule.

1. **The freeze checks its premise** (mechanism C): `review_freeze` returns not-frozen when
   `git merge-tree --write-tree origin/main <head>` conflicts, because a verdict or a review at a conflicting head
   cannot be used. The `HELD-*` line then says `DIRTY: not frozen`. State (d). Proposal, owner approval (policy text in
   the relay header).
2. **The pass notices its own length** (mechanisms A and B): a per-update wall bound and `probe_arm`/`confirm_arm`
   run before or independently of `handoff_arm`, or handoff updates run concurrently under the per-branch lock.
   State (d). Proposal, tool change.
3. **A lag level**: `relay_handoff_lag.py` as a tick-board line (`OWED ... handoff-lag <topic> <min>`), the unit no
   current class measures. State (d) (it makes the drift visible). Built here as a detector, **not wired**.
4. **Refused:** a firmer instruction to the orchestrator to release by hand. The hand release is what happened four
   times; the instruction would be obeyed, not effective.

Not built here: edits to `cloud_relay.sh`/`tick_loop.sh` (the brief fences this seat to `dev/audit/rca` and
`bugclasses.json`). The class is recorded in `dev/audit/config/bugclasses.json` as `N-relay-handoff-starvation`,
status `detector`, with the three instances as non-round instances and no barrier; reopen on a fourth, which
(`defect-root-cause.md`) then owes a barrier decision from the owner.
