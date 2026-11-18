# Proposal triage, session s14, batch 201 (P627)

Sources:
- Roster `handoff/audit-r10-roster` at `b4a41e1e3b`, where the groups owning `open_driver.py`,
  `tick_loop.sh` and `open_pr` were read.
- origin/main `60413046e3`.
- The opener driver's log, `$HPO_STATE_DIR/open-driver/open-driver.log`: 5735 lines, from
  2026-11-10T08:50:33Z to 2026-11-11T13:54Z (about 29 h), with 66 RESULT lines.
- The orchestrator's session-local beat script, `beat_extras.sh` in its session dir: arm (d).

## P627: open_driver backs off on an environment refusal (STALE CHECKOUT)

Verdict: ACCEPT narrowed. (a) becomes a new group, R10-FLY-OPENER-STALE-ENV (S, fixer sonnet,
reviewer opus). (b) is ACCEPTED as an orchestrator-local change with no roster group, because
`beat_extras.sh` is a session script, not a tracked tool.

Source: triage queue line 305, 2026-11-11T13:52:29Z, orchestrator s14: INSTRUMENT GAP (a local
workaround was applied).

Measured from the driver log, over 29 h:
- **The opens.** 66 open results: 44 rc 0 and 22 failures.
- **The STALE CHECKOUT refusals.** 14 of the 22 failures are `open_pr: REFUSE: STALE CHECKOUT`,
  across 11 topics. That is 64% of all failures and 21% of all open attempts.
  - The time from each refusal to the topic's next result has a median of about 17 min and sums to
    371 min. The range is 7-140 min.
  - Those intervals already include hand clears of `fails.json`, as today's at 13:52Z.
  - Without the hand clears, the code's backoff is 1800 s doubling to 7200 s (`BACKOFF_S`). After
    `MAX_TRIES = 3` a topic goes stuck. r10-process-slim-p2 took 4 STALE refusals on its way to
    stuck.
  - Today the refusals hit a merge-stopping hotfix, R10-HOTFIX-GATE-REDISPATCH-LOOP: refused
    13:34:54Z, opened 13:54Z.
- **The null class.** The other 8 failures are branch-side: a merge of origin/main conflicts, or a
  push fails. Those are the branch's own, and backoff is correct for them. The change must leave
  them unchanged.

Cost/benefit:
- The refusal is the environment's, and rotating the tools checkout cures it.
- It delays every opener after each main merge that touches tools/audit/seat or tools/pr. That is
  8 of 25 main first-parent merges in the last 24 h.
- It can push a topic to stuck. A stuck merge-stopping hotfix is a defect that stops merges, which
  meets the owner's bar.
- The fix costs nothing at run time: no extra REST reads, and one string match on the reason the
  driver already parses.

Narrowing of (a): "retried next pass" alone would spin, because each pass re-refuses until the
checkout rotates. So the retry is keyed on the tools checkout's HEAD.
- A STALE CHECKOUT result records the HEAD it was refused at. It neither counts toward `MAX_TRIES`
  nor sets a backoff.
- The topic is retried on the first pass after that HEAD changes.
- This matches how merge_train treats a [HOLDER] skip: the environment's, and not the PR's.

(b) The beat's freshness arm (d) in `beat_extras.sh` is at most hourly. It should rotate the tools
checkout on the first 15-min pass after origin/main gains a commit touching tools/audit/seat or
tools/pr. That is the same predicate open_pr refuses on, so the bound drops from 60 min to 15 min.
- The cost is one `git log` over a fetched ref per pass.
- The orchestrator owns the session script and applies this itself, recorded in its handover. It
  needs no roster group.
- If the arm is later promoted into tracked tooling, it goes as a carry on R10-SEAT-IDENTITY-P5,
  which owns the beat job table and `open_driver.py`.

Placement of (a): R10-SEAT-IDENTITY-P5 owns `open_driver.py`. It is not started, holds 7 carries,
and waits on R10-TICK-RESIDUE, which is carries-open with 33 carries. A carry there would hold a
fix to an S-sized opener behind both. So it is a new S group, with overlap admitted on
`open_driver.py` (P5's seam is the generation token and the opener stand-in, which is distinct).

Acceptance for (a), in `open_driver_selftest.py`:
- (i) A STALE CHECKOUT result with an unchanged checkout HEAD is not retried, does not back off,
  and does not count toward stuck.
- (ii) After the HEAD changes, it is retried on the next pass.
- (iii) Null control: a merge-conflict rc 1 still backs off for 1800 s and still counts toward
  `MAX_TRIES`.
- (iv) Mutation: treating every rc 1 as environmental turns (iii) red, and dropping the HEAD key
  turns (i) red.
- (v) Replaying the 13:34:54Z refusals of the three topics in the log against a HEAD change at
  13:44:40Z retries them on the first pass after 13:44:40Z.
