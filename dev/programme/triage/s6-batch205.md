# Proposal triage, session s14, batch 205 (P636)

Sources:
- Roster `handoff/audit-r10-roster` at its tip, 2026-11-11T14:50Z.
- origin/main `0e28afd38b`.
- The live merge-train log, `~/.local/state/hpo/merge_train/train.log`.
- The beat's roster drain: `roster_drain` in `tools/audit/seat/beat_jobs.py` (:339) and its digest
  state.

## P636: postmerge's stage write goes through the roster drain queue

Verdict: ACCEPT, as a carry on R10-TICK-RESIDUE-P3, which owns `postmerge.py` and
`roster_sync.py`.

Source: triage queue line 313, 2026-11-11, orchestrator s14 via triage s14-21, PROPOSAL postmerge
stage write.

Instances:
- train.log holds 6 `OWED stage: rc 2: roster_sync: REFUSED: lost the race for
  handoff/audit-r10-roster 3 times` lines in all: #3244, #3315, #3409, #3401, #3425 and #3447.
- Today (from line 19380) postmerge attempted 2 stage writes, for #3425 and #3447. Both were lost
  (`grep "OWED stage"`).
- R10-OUTSIDE-DIAG-REDACT-LOCATION (#3447) and R10-WORKTREE-GC-LIVE (#3423) still read
  `in-progress` at the roster tip. The orchestrator re-routed both by hand through the roster
  queue: lines 4558-4560.
- Why the retries cannot win:
  - `roster_edit`'s push loop (`PUSH_ATTEMPTS = 3`, :210) re-applies the edit on the new tip
    after each loss.
  - The window between fetch and push includes the lint gate, about 4 min on this box. That is
    about the drain's own cadence: 4521-4524 landed at 14:11:53Z, 14:15:33Z, 14:35:25Z and
    14:40Z.
  - So under a backlogged drain, each of the 3 attempts finds the tip moved.
- The same class bit the drain itself. This seat's direct triage-record push (a23a1b67a5,
  14:20:52Z) moved the tip under queue line 4523. 4523's commit 5b8e97ad94 was refused and the
  worktree was left on no origin ref, so the beat printed `CASCADE 1 op(s)`. The op landed on its
  retry at about 14:40Z.

Classification:
- A lost record write: the roster misreads a merged group as in-progress. That holds the group's
  dependents in the plan and costs an orchestrator hand-route per merge.
- Severity medium, so the machinery bar does not apply.
- The fix replaces the code path; it adds no machinery.

Design, narrowed:
- On a refused or raced sync, `postmerge.py`'s `stage` step appends the derived op to the beat's
  `roster-drain.queue` (the file `roster_drain` reads, under the beat state dir) as one
  newline-terminated line. That is `set-stage <GROUP> done --at-sha <merge>`, or `carries-open`
  where carries remain, plus any keyed `mark-carry` lines, exactly as `set-stage owed` prints
  today.
- It logs `stage QUEUED <line>`.
- Enqueue on the first loss, or always: the fixer chooses, with the measured win rate of the
  first attempt.
- The drain then makes the roster branch's single writer for merge stages.
- The append must be atomic and newline-terminated, because the drain runs only terminated lines
  (beat_jobs.py:345-347). It must also be idempotent per merge sha, so a re-run postmerge does not
  queue a second copy that the drain would apply as a new occurrence.

Out of scope, recorded: the triage seat's own `batch.sh` record push is a third direct writer.
It is a file commit, not a `roster_edit` op, so it cannot be queued as one. Until a queued form
exists, this seat runs it only between drain ops: no roster_edit or roster_queue pid live.

The carry's acceptance:
- (i) A raced sync queues exactly one well-formed drain line per merge sha, and prints
  `stage QUEUED`.
- (ii) A second postmerge run for the same sha queues nothing.
- (iii) Null control: an unraced sync pushes as today and queues nothing, if the fixer keeps
  the direct first attempt.
- (iv) Mutation: dropping the newline (or the idempotence key) makes (i) or (ii) red.
- (v) Replay: #3447's derived op, queued, is accepted by `roster_queue.parse_line` and
  `replay_unsafe`.

Binding: 2 of 2 merge stage writes lost today, each a stale roster row plus a hand-route.

Bar re-check (2026-11-11, orchestrator's question; proposal-triage.md lines 9-19). A carry on an existing group is still added instrument work, so the same bar applies to it. No ratchet-budgets.md cap is touched: every change here is code under tools/ and moves no policy_budgets.json measure, so the 20% figure below is read on the proposal's own benefit measure.

Bar: severity medium (R10-TICK-RESIDUE-P3's roster severity). Figure: 2 of 2 postmerge stage writes lost today, 100%, over 20%. Accepted both as over-20% and as a severity-exempt defect repair (a lost record write).
