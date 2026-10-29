# Proposal triage, session s7, batch 54 (P265)

This batch has one entry, V179, an owner-approved card filed at 2026-10-28T19:02:58Z and quoted
from `proposals.md` as it stands. It is its own batch because batch 53 was already open as a pull
request. Facts were read at origin/main `beb570c817c4efcae0d5f6f4bba52f3383baf8db` and at the live
roster, `origin/handoff/audit-r10-roster` `2ce021c6f19c4c4069d50994a271fd1e7b872834`.

## P265: the tick reconciles every open PR to exactly one bucket, and owes a line for any PR in none

Verdict: ACCEPT, narrowed, into **R10-ORCH-LEDGER** (stage `carries-open`). That group owns the
obligations ledger, which "replac[es] the relay's log scan and the tick's OWED scan", and states
that "an obligation with no ledger kind is a refusal". It names `orchestrator_tick.py` and
`cloud_relay.sh` among its files. An open PR with no bucket is exactly an obligation with no kind,
so existing-groups-first (P255) routes it here.

Source: `proposals.md` V179 (the orchestrator, an owner-approved card, 2026-10-28T19:02:58Z).

Instances. The filing names three, and this seat read each from git:
- **#2906** is at head `fb2f3de8624bbdcff8d1f801ada3d7c161f1af33`. Its `verdict/2906` tip is
  "Fix review: blocked fb2f3de86... carry-mi[ssing]", committed 2026-10-28T09:00:27Z. The newest
  verdict is a **block** at the live head, not a landed merge verdict as the filing says, and no
  repair head followed in about 9 h. So the PR owes a fixer round, and no line says so. #2906 is
  this seat's batch 47 (P235), so the owed repair is a triage fixer's.
- **#2917** (head `d4ec6fcce`) and **#2919** (head `755f141e7`) have no `verdict/<n>` ref.
- **What the tick already prints, and why the stalls still go unseen.** Per PR, the tick's
  PRS section already reports:
  - a RED check not answered in `## Red checks`;
  - DIRTY or BLOCKED mergeable state, as `#<n>: mergeable state DIRTY -- ...`
    (`tools/audit/seat/orchestrator_tick.py:855`);
  - a queue verdict whose head has moved.

  Its REPLAN section prints the throughput stall (line 1850) only for entries already in the
  train's queue file, and its OWED handoffs only from `bus.sh orphans`, that is from handoff
  refs. So #2917's DIRTY and #2919's red each show as a per-PR flag with no owner. #2906 shows
  nothing at all: it is not queued, it has no stranded handoff, and its block is not a check
  state.

Carry (narrowed):
1. In the tick's PRS pass, each open PR gets exactly one bucket, computed from data the pass
   already reads (head, check-run latest-per-name, mergeable state, the queue file) plus git refs
   (`verdict/<n>` tip subject, `handoff/<topic>`). It adds **no new GitHub calls**. The buckets:
   - `train`: in the queue at a verdict that is the head or carries to it.
   - `verdict-pending`: no verdict at the head, and a review dispatch or bus probe exists.
   - `fixer-round`: the newest verdict is `blocked` at the head, or a handoff ref is ahead of the
     head.
   - `waiting-on #N`: the roster's after-edge or a hot-file overlap names an open PR.
   - `owed`: none of these.
2. An `owed` PR prints one OWED line with its reason, for example "blocked verdict at head 9 h,
   no repair", "DIRTY, no handoff" or "red unanswered, no dispatch". The line is keyed on
   (kind, PR) in the ledger, and its disposal is written by the producer, as the group's design
   already requires.
3. Critical-path PRs are listed first, by `roster_lib`'s critical path.
4. Controls: three fixture PRs shaped like #2906, #2917 and #2919 each print one OWED line naming
   that reason. A mutant that drops the blocked-at-head arm leaves the #2906 fixture silent, and
   fails. Null: a queued PR at a verdicted head prints no OWED line, and every open PR has exactly
   one bucket.

Not carried: a separate per-pass board of all buckets. The OWED lines are what an orchestrator
must act on (tick-report-means-act). A bucket summary is one count line.

Cost: about 60-100 lines and three fixtures in `orchestrator_tick.py` (4066 lines), and no
additional API reads. The file is shared with R10-FLOW-WIP and R10-FLOW-DESIGN-STAGES, on distinct
seams: lane caps and design lines. The beat (R10-ORCH-BEATD) runs the tick as a job, so nothing
here needs a second schedule.

Binding: three open PRs stalled with no owed line, one of them for about 9 h, against a classifier
over facts the tick already holds. The group that already owns "no obligation without a kind" is
`carries-open`, so the carry lands before its build.
