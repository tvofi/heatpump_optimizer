# Proposal triage, session s8, batch 69 (P301)

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
