# Proposal triage, session s7, batch 36 (P204)

One entry, cut on the orchestrator's order (s7, 2026-10-27T09:37Z relay) because a second
writer on the triage role is a live hazard on the stamp path: the orchestrator holds a hand
barrier that admits exactly one batch file newer than the `v7.0.5` tag. Numbering continues
after `s6-batch35.md` (P199-P203). Facts read at origin/main `524c1896b` on 2026-10-27.

## P204: two seats on one role are invisible and unstoppable (V124)
Verdict: DEFER. Route the item as prose into the carry text of **R10-ORCH-BEATD**
(`not-started`, L; the sweep/beat is its surface). P197 is deferred to that group and sits
in its carry 13 (index 12), the context-rotation paragraph, per `s6-batch34.md`; the roster
holds no `P197` string, proved by
`git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c P197` printing `0`.
Two arms of the proposed shape are REJECTED: per-pass renewal, and a sweep flag. The one
element that survives is a launch record written by whoever dispatches a seat, which is
dispatch practice already within the orchestrator's reach and needs no repository change.

Source: orch s7, 2026-10-27 — V124 assigned to this seat in the orchestrator's 09:37Z relay
(the `proposals.md` entry was not yet appended when this ruling was cut). Proposal text as
relayed: "a seat-start claim (`s7/<role>.claim`, or better a per-instance file so a second
claim cannot overwrite the first — role, pid, nonce, started_at, renewed per pass) that the
sweep reads, so two claims for one role are visible *without* anyone identifying the runaway
agent", with the constraint that it must be writable by a shell loop and by an agent seat
without either having to know the other exists.

Instances: one, measured end to end in this seat's own session, and the measurement is why
the verdict is DEFER rather than ACCEPT — the mechanism does not reach it.
- Two writers, one role. `grep -n 'triage s7:' seat-ledger.md`, in the orchestrator state
  directory, shows two cadences interleaved from 08:13:15Z. The second writer's lines are the plain
  `HOLD (no v7.0.5 tag)` form, 18 of them, at 5:00-5:01 intervals: 08:13:15, 08:18:16,
  08:23:16, 08:28:17, 08:33:18, 08:38:19, 08:43:20, 08:48:20, 08:53:21, 08:58:22, 09:03:22,
  09:08:23, 09:13:24, 09:18:24, 09:23:25, 09:28:26, 09:33:27, 09:38:27.
- Not an echo of this seat. This seat's ledger lines carry a `; main <sha>` annotation and
  stopped for 21 minutes (last line before the stall 08:54:25Z, next 09:15:38Z); the other
  writer produced four lines inside that window (08:58:22, 09:03:22, 09:08:23, 09:13:24) at
  its unbroken cadence, so it is a separate timer or process. Arrival order is unresolved:
  the whole-ledger series (`grep -n 'triage s7:' seat-ledger.md`) puts a plain-`HOLD`
  cadence starting at 20:56:28Z (ledger:1171, before this seat's first `; main <sha>`-annotated
  line at 08:12:52Z, ledger:1330) with no gap over 7 minutes, so the orchestrator's 09:30:39Z
  stand-down rests on the 08:13-09:38 window and does not settle which writer arrived first.
- Invisible to the liveness file. Both writers `touch` `s7/triage.alive`; its mtime can only
  say that someone is alive, never how many. (The orchestrator's board reads alive age only,
  and it was corrected today from 660 s to 1800 s after 22 beat gaps, median 57 s, max
  1235 s.)
- Unstoppable. The orchestrator's 09:30:39Z ruling records it as absent from ListAgents, with
  no shell it can see and no subagent transcript in its session; the stop measure it could
  take was a hand barrier on the stamp path, "exactly one batch file newer than the tag, or
  no stamp".
- The proposed claim would not have named it. The writer emits nothing but that one fixed
  line, so it reads neither this seat's brief nor the session preamble; a convention it does
  not implement cannot record its start. It is not one of the loop scripts in the tree either:
  the two running (`tick_loop.sh`, pid 7716, and `roster-loop.sh`, pid 99863) write `tick.txt`
  and `roster s7:` lines respectively — `roster-loop.sh` read in full this pass, no
  `triage`/`HOLD` write in it — and w71's `loop.sh`/`watch.sh` have no process at all, while
  `w71/loop.pid` names 76559, which is gone. Its source is unidentified.

Cost: read against all 34 of the destination group's carries, not one. P97(b), at index 21
(carry 22; `s6-batch21.md#P97`), already carries three parts of the filed shape: the
per-instance alive entry (one alive entry per seat id under each role, beside the per-role
file), the sweep arm that acts on it (step (1b) of `tools/audit/seat/sweep_template.md` stops
the older id and logs both), with that arm's self-test and mutation proof, and the `DUPLICATE
seat <role>: <id> <id>` print. What is genuinely new is the renewal on every pass, the second
liveness source (renewal age) that can disagree with the alive-age test and with P199's carried
arm ("no live pid and no `TRAIN DONE`/`STOPPED` line"), which already owns death detection, and
the noise a per-role line adds for every legitimate restart until a dead seat's claim is
retired — seat restarts and beat gaps are routine in this session (three seats restarted at
21:15Z, `seat-ledger.md:1149`; the merge seat restarted at 08:19:56Z after being dead since
22:16Z, `seat-ledger.md:1334`) — which lands on the board the orchestrator reads every pass.

Binding: a convention binds only the seats that implement it, and the instance that motivated
the proposal implements nothing; the benefit is therefore unmeasured against its own target
while its costs are immediate. What would change the answer: (i) the other writer identified
as a seat that reads its brief and acts, so a claim binds it and a pid inside the claim makes
it stoppable; (ii) a second episode in which a duplicate performs an act — a ruling, a roster
op, a merge — rather than writing a HOLD line; or (iii) the orchestrator adopting a launch
record at dispatch (role, nonce, started_at, supervisor pid — the data its launch ledger lines
already carry) and finding a double dispatch, in which case the countermeasure belongs at
dispatch and not in a seat claim.

What survives of the proposed shape, and why it is not an ACCEPT: a launch record written by
the launching side, one file per launch, carrying role, nonce, started_at and the supervisor's
pid. The fact that made the second writer unstoppable was that nothing recorded its launch at
all, and the launching side is the only party that always knows a seat started. It needs no
seat cooperation, no sweep arm, no renewal and no new liveness source, and the orchestrator can
adopt it in its own dispatch path now; if it wants that as repository work, it is a separate
proposal and will be ruled on its own cost.

No roster op: `roster_edit.py` refuses a carry whose cite is not an ACCEPT, so this item travels
in R10-ORCH-BEATD's carry text as prose, as P201's PR half does (s6-batch35.md).
