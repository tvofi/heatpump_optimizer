# Proposal triage, session s14, batch 146 (P554 to P555)

This batch rules `s7/triage-queue-s7.txt` lines 238 and 239, which arrived after batch 145. The bar
and the denominators are batch 141's.

Sources: the roster at `origin/handoff/audit-r10-roster` `5b62466d83` and origin/main
`d08ed31049`.

## P554: S14-PULSE-VERDICT-WHILE-TRAIN-LIVE

Verdict: ACCEPT, narrowed. It repairs an observed wrong behaviour: an alarm that mixes held work
with owed work. The source's own premise ("zero actionable") was wrong, so the narrowing changes
which train file counts as held.

Source: queue line 238 (2026-11-11T01:05:53Z, orchestrator friction).

Instances:
- **The arm.** `pulse.py`'s `judge_verdict` counts every verdict at an open head older than
  `--verdict-h` (2 h) as STOPPED. It never reads the merge train.
- **The snapshot.** `beatd/pulse.txt` at about 01:10Z listed 13 STOPPED verdicts, 12 of them
  merge verdicts.
  - The train's `queue.pending.json` (01:48Z) held five of them: 3374, 3381, 3382, 3387 and 3388.
  - Six were in no train queue: #3392 (CLEAN, 24.1 h), #3389, #3390 and #3391 (BLOCKED, 23.9-26.3
    h), #3379 (DIRTY, 13.7 h) and #3419 (a blocked verdict, 12.3 h). Their states come from
    `gh pr view --json mergeStateStatus`.
  - So the line carried real owed work as well as the held verdicts.
- **The wrong file.** `queue.seen.json` lists 3383 and 3386, which this train already skipped.
  Counting `seen` as held would hide two owed verdicts.
- **The local filter.** `s9/wake.sh` drops the headline whenever a train pid is alive. Per-PR lines
  still wake when they are new.
- **The cost.** The source counts four wakes in 30 min. That figure is the source's own.

Cost: about 15 lines in `pulse.py`.
- While `train.pid` is alive, a verdict whose PR is in the train's `queue.pending.json` reads
  `held by train` and is left out of the STOPPED count.
- Every other verdict, `seen`-but-skipped ones included, is counted as today.
- A dead train pid counts all of them.
- Self-test:
  - a pending PR with a live pid is held;
  - the same PR with a dead pid is STOPPED;
  - the null control: a `seen`-only PR is STOPPED;
  - a mutant on the file read.

Binding: one carry, R10-STANDING-CONTRACTS-P2, which lists `tools/audit/seat/pulse.py`; the source
proposed R10-TICK-RESIDUE part 2. Carry file: `b146-P554.txt`. Once this lands, the `s9/wake.sh`
headline filter is the orchestrator's to retire.

## P555: S14-DRAIN-REFUSAL-NOT-DURABLE

Verdict: ACCEPT. It repairs an observed wrong behaviour: a refused append-group left no durable
trace, and a dispatch waited on a group that did not exist for about 35 min.

Source: queue line 239 (2026-11-11T01:07:38Z, the orchestrator and the diagnosis seat).

Instances:
- **The mechanism.** `beat_jobs.py` `roster_drain` adds an op to `done` after it is applied or
  refused alike ("applied or refused: never retried past the lint gate"). It writes its lines only
  to `digest/jobs/roster-drain`.
  - `write_job` replaces that file on the next pass that runs an op.
  - `roster_queue.py --mark` rewrites the `#refused` mark into the one-line `state/roster-one.queue`,
    never into the queue file.
- **The record that stopped.** Earlier drains wrote the outcome into the queue file itself.
  - `grep -c '^#refused'` over `s7/roster-queue-s7.txt` gives 261; the last is at line 3979 of
    4269. Refusal `#note` lines give 171.
  - The beat drain's first run was 2026-11-09T07:52:35Z (`beatd/journal.log`). Its refusals reach no
    file that outlives the next pass. Neither `digest/state/roster-done.json` nor
    `digest/gone.txt` (0 lines) holds one.

Cost: about 15 lines in `roster_drain`, and no new file.
- Each refusal, with its occurrence key and the refused line, appends one line to
  `digest/events.txt`. The orchestrator's wake already treats growth of that file as a wake.
- Refused keys move to a `roster-refused.json` memory beside `roster-done.json`, so applied and
  refused are told apart. A refusal is still never retried automatically.
- Self-test:
  - a refused op writes one events line, which survives a following applied pass;
  - the null control: an applied op writes none;
  - a mutant on the append.

Binding: one carry, R10-TICK-RESIDUE (`beat_jobs.py` is in its files). Carry file:
`b146-P555.txt`.
