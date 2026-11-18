# Proposal triage, session s14, batch 144 (P550 to P551)

This batch rules `s7/triage-queue-s7.txt` lines 234 and 235, which arrived after batch 143. The bar and the
denominators are batch 141's.

## P550: S14-LIVENESS-STALE-PATTERNS, an amendment to P506

Verdict: ACCEPT, narrowed. It rides P506's owner-directive route (tvofi 2026-11-09: "keep the local
one, but propose an update to the live one to cover the gaps"), as a constraint on the arms P506
adds.

Source: queue line 234 (2026-11-11T00:38:32Z, orchestrator friction).

Instances:
- **The session-local hook.** It and its `compact_done.sh` proof hard-code a session path
  (`s13/beat_extras.sh`) and demand a standalone `cloud_relay.sh pass` process.
- **Where the relay actually runs.** `tick_loop.sh` runs the relay as one step of each pass (header
  line 7, since #2419). So after each compaction:
  - the local hook restarts a duplicate of a dead-path companion;
  - the proof refuses on a healthy relay;
  - the recorded relay launch line (a flattened `python -c`) cannot run.
- **What the tracked hook already does right.** `hooks/liveness.py` takes its loop list from
  `beatd.py status`, which is the job table (`instruments/hooks_setup.py.md` line 7). That half of
  the proposal is built.
- **What it lacks.** A relay-liveness read, and the read-proof and restart arms P506 adds. P506's
  arms must not import the local hook's literal paths or process patterns.

Cost: constraints on P506's own arms, so no new arm.
- The restart arm relaunches only `beatd` (the one supervisor) and never replays a recorded launch
  line for any other loop.
- The relay is judged live by the age of `cloud_relay.sh`'s log against the tick pass cadence,
  never by a standalone process match.
- The read-proof arm names no session path.
- Self-test: a planted stale relay log is `DEAD`; the null control, a fresh relay log with no
  standalone relay process, is live; and a mutant on each.

Binding: one carry, R10-STANDING-CONTRACTS-P2, beside P506's carry. Carry file:
`b144-P550.txt`.

## P551: S14-BRIEF-OVER-FIVE

Verdict: ACCEPT, narrowed. It repairs an observed wrong behaviour: a fixer brief that breaks
`fixer.md`'s limit ("at most five findings", line 3) and names no part. The orchestrator answered
the one stop with a split an instrument can print.

Source: queue line 235 (2026-11-11T00:40:21Z, the R10-PREPR-RESIDUE fixer's blocked stop).

Instances:
- **The stop.** `tick.txt` line 115: `OWED blocked-stop r10-prepr-residue 87c3ba7353c9`, "the brief
  holds 21 carries ... against the fixer contract's limit of five findings per group".
- **The window.** Four fixers were published with more than five carries and no part named.
  - The `dispatch/fixer-*` tips are tick-residue 00:14:40Z (22 carries), prepr-residue 00:14:51Z
    (21), plan-page-residue 00:15:19Z (6) and train-residue 00:15:59Z (14). gh-read-residue
    00:15:10Z held 4.
  - One of the four stopped. That is 25 % of over-five dispatches not right first time, over the
    20 % bar, on a sample of four.
- **The answer was mechanical.** The re-dispatch `dispatch/fixer-r10-prepr-residue` `4c83df2f4a`
  carries the orchestrator's ruling: "serial parts of at most five carries on its one seam",
  - carries 0-4, 5-9, 10-14, then 15-20 ("six, the last two are one-line");
  - each part dispatched at the previous part's handoff;
  - topic `r10-prepr-residue-p2` for part 2.
- **Who it reaches next.** At roster `38db9e1130`, 14 of 41 live groups hold more than five
  pending carries (`roster_lib.pending_carries`). Six of them hold more than 11: ROUND-PLAYBOOK-FINAL
  27, TICK-RESIDUE 22, STANDING-CONTRACTS-P2 22, PREPR-RESIDUE 21, ARBITER-OFF-RESTORE 16 and
  TRAIN-RESIDUE 14.

What is narrowed out:
- **A silent auto-part.** Rendering part 1 whenever no part is named would re-dispatch part 1's
  carries at part 1's own handoff, because they stay pending until its merge.
- **Replan's 11.** `tools/plan/durations.json`'s `carries_per_part` 11 is a duration measure,
  not a scope rule. The limit is the contract's five, as the orchestrator's ruling applied it.

Cost: `cloud_dispatch.py`'s `dispatch_group`, fixer role only, takes a new `--part <k>`. About
30 lines, no new file, and no `structure_budgets.json` key names the file.
- **Without `--part`.** When the group holds more than five pending carries, it refuses and prints
  the split: index-ordered fives over the pending carries, with a remainder of one or two folded
  into the last part.
- **With `--part k`.** It renders a generated brief line: "Part k of N: build carries a-b; the
  others are later parts dispatched at this part's handoff; answer none of them". The topic is
  `<topic>-p<k>` for k over 1, which `roster_lib.group_for_branch` already maps to its group.
- **Five or fewer.** A group with five or fewer pending carries renders byte-identically.

Self-test:
- 21 pending carries refuse with the split `0-4, 5-9, 10-14, 15-20`;
- `--part 2` renders carries 5-9 and the topic `-p2`;
- the null control: five carries render unchanged, with no refusal;
- a mutant on the count, and a mutant on the fold.

Binding: one carry, R10-REVIEW-DISPATCH-RESIDUE, which already lists
`tools/audit/seat/cloud_dispatch.py` in its files. Carry file: `b144-P551.txt`.
