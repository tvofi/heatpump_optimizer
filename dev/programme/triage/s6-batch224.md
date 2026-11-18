# Proposal triage, session s14, batch 224

Sources: the orchestrator's message to the triage seat (2026-11-12T01:00Z), ruled as P677, P678 and
P679. Line numbers are at origin/main 47788534da. Roster read at handoff/audit-r10-roster 97a9e7a857.

## P677: a false `mark-carry implemented` could only be cured by dropping the entry

Verdict: REJECT (a) evidence-checked marks and (b) an `unmark-carry` op. The live owner of
roster_edit.py residue is R10-TICK-RESIDUE-P3 (not started, L, severity medium; its `files` list
roster_edit.py). Nothing is carried there from this proposal.

Source: the orchestrator. A `mark-carry R10-STANDING-CONTRACTS-P2 ... implemented 47788534da` was
queued without checking the merge. The #3464 merge did not touch dev/programme/HANDOVER.md, which
carry e8e05480 asked for. The drain applied the mark (roster a3c0451c5f). The cure was to move the
carry to R10-TICK-RESIDUE-P3 (append-carry, cd930f21eb) and drop the false entry (97a9e7a857).

Instances:
- False implemented marks: 1. Over the roster branch log, 11 drop-carry commits removed a line
  carrying `[implemented:` (`git log --grep=drop-carry` plus each diff's removed lines). 10 are the
  2026-11-10 carry-drain cleanup: queue lines 1695, 1960 and 4041-4115 are dedupe and legacy drops,
  not corrections. The 11th, 97a9e7a857, is this one.
- Denominator: 283 `mark-carry ... implemented` lines in the roster queue
  (`grep -c 'mark-carry .* implemented' roster-queue-s7.txt`). That gives 1 false mark in 283
  (0.35%).
- roster_edit.py:138-146 states the design: `implemented` "records that the sha is on main; it is
  not a verification".
- roster_lib.py:498-518: carries-open is outside the carry-destination set by owner ruling
  (R10-CARRY-SINK-BARRIER, tvofi 2026-11-10), so append-carry and `moved` refuse it on purpose.

Rejected (a), an evidence-checked mark (a path the merge touched, or `--evidence <cmd>`):
- It adds a required argument to every mark, for 283 marks so far, to catch a 0.35% error rate.
  That is far under the 20% bar.
- A path check is also the wrong test. Many carries are satisfied by a change in a file other than
  the one they name, or by a text that a diff stat cannot read. Such a check would refuse true marks
  and pass any false mark whose merge touched the named file for another reason.
- The countermeasure that would have caught this instance is the reading itself: `git diff --stat
  M^1 M -- <file>` plus reading the text. It is already binding in the triage seat's handoff (rules
  learned, 2026-11-12).

Rejected (b), `unmark-carry --match`:
- On P2 it would have put the carry back on a carries-open group. By roster_lib.py:498-518 that is
  a stage no seat builds a carry in, so it recreates the sink the barrier closed.
- If the false mark had discharged the last pending carry, `close_discharged` (roster_edit.py:647-
  659) would already have written `done`. An unmark would then also have to reverse a stage
  closure: new logic in a 3074-line file, for 1 instance.
- The cure that exists costs 2 queue ops: append-carry to the live owner, then drop-carry --match.
  It ran correctly at cd930f21eb and 97a9e7a857. The extra cost that night was 4 refused ops
  (queue 4636-4639, index-keyed or onto carries-open), and the seat handoff now records the route.

Cost avoided: one op and its self-test arms in roster_edit.py (not on a capped list in
tests/structure_budgets.json); none incurred.

Binding: the 0.35% rate, and carry_receivable's carries-open exclusion. A second false mark that
the seat's reading rule does not prevent reopens (a) as a check on the triage seat's own queue
lines, not on roster_edit.py.

## P678: the opener's backoff held a hotfix behind a host failure

Verdict: ACCEPT (b) an `open_driver.py retry <topic>` verb, as a carry on
R10-FLY-OPENER-STALE-ENV. REJECT (a) the 5-minute floor for hotfix, outside and critical topics.

Source: the orchestrator. r10-hotfix-opener-unblock failed on Darwin's wc padding (P676), and the
orchestrator reset open-driver/fails.json by hand.

Instances (open-driver/open-driver.log, 2026-11-10T08:50Z..2026-11-12T00:25Z):
- r10-hotfix-opener-unblock 80779d2e:
  - RESULT rc=1 at 00:00:11Z, START again at 00:10:11Z, opened rc=0 at 00:25:11Z.
  - n=1 backs off 1800 s (open_driver.py:78 and :146-147), so the driver alone would have retried
    at 00:30:11Z.
  - The hand reset cut the hold from 30 min to 10 min. The log does not support a 70-minute hold
    attributable to the backoff.
- All hotfix and outside topics: 12 rc≠0 results.
  - 5 are STALE CHECKOUT. R10-FLY-OPENER-STALE-ENV already re-keys those to the tools checkout
    HEAD.
  - 1 is this host failure.
  - The rest are conflicts or push refusals, whose p1.log has since been overwritten by the
    successful run.
  - Fail-to-restart gaps: 31, 5, 30, 73, 17, 17, 30, 28, 113 and 10 min.
- Hand resets of fails.json: 3 in 40 h. Two left backups (fails.json.bak, 2026-11-11 08:27Z;
  fails.json.bak-s14-1352, 13:52Z), and the third is tonight's 00:10:11Z restart, 20 min before the
  backoff expired.

Rejected (a), the floor:
- The backoff keys on (topic, sha) (open_driver.py:247), so a new head is never held. A same-sha
  retry fails again until something outside the branch changes: here, the wc shim on PATH.
- At a 5-minute floor, each retry before the cure is a full prepr run. START to RESULT was 15 min
  here.
- The best case saves 20 min once in 40 h. The cost is a wasted 15-minute local prepr for each
  retry made before the cure.
- The environment-keyed retry that removes the failure class without spinning is the STALE
  CHECKOUT rule already briefed on R10-FLY-OPENER-STALE-ENV.

Accepted change (b), carry on R10-FLY-OPENER-STALE-ENV (not started, S, severity high, sonnet; it
owns the backoff seam in open_driver.py; no overlap with R10-HOTFIX-OPENER-UNBLOCK, whose brief
names no backoff):
- Add `open_driver.py retry <topic> [<sha>]`. It removes that topic's fails.json entry, or the
  (topic, sha) entry when a sha is given, and prints the removed n, next and why.
- It refuses a topic with no entry. It writes the file the same way a pass does (open_driver.py:249)
  and reads it back after its write.
- The instrument doc names it as the cure once an environment failure is fixed, replacing a hand
  edit of a file a live loop rewrites every pass.
- Acceptance in open_driver_selftest.py:
  - (i) After `retry`, the next pass starts the topic inside its backoff window.
  - (ii) Null control: without `retry`, the same pass skips it as backoff.
  - (iii) Mutation: a verb that writes nothing turns (i) red.
  - (iv) A topic with no entry is refused and writes nothing.
- Figure against 20%: it replaces 3 hand edits in 40 h of a state file with one verb. The basis is
  the destination's severity (high), which skips the machinery bar, and a hand edit's lost-write
  risk: pass() loads fails.json at :225 and rewrites it at :249.

Cost: about 20 lines in open_driver.py and 4 self-test arms. Neither file is on a capped list in
tests/structure_budgets.json. The group stays S.

Binding: the sha-keyed backoff (:247), which makes a same-sha floor retry repeat a failure until a
human acts, and the 3 hand resets.

## P679: a direct merge while a train batch proof is in flight

Verdict: REJECT.

Source: the orchestrator. #3355 and #3464 merged directly while batch 20261111-183624-b2 was
inside its proof, and the train re-proves.

Instances:
- The b2 proof (batch/20261111-183624-b2-1 at b6870648) is built on 046736a49f
  (`git merge-base --is-ancestor`).
- Before #3355 (68d34ce0ab) and #3464 (47788534da), main had already moved past that base by
  #3482 (6d16af36c2) and the bot's #3480 (d8768cde3e). Neither is in the proof.
- One move is enough to owe the batch its MAIN-MOVED re-prove (merge_train.py:2660-2691; one
  re-prove whatever the count of moves). The marginal re-prove cost of the two direct merges is
  therefore 0.
- Since the first 2026-11-11 batch (train.log:19383): 6 proofs pushed, and 3 `[MAIN-MOVED] before
  #N's merge: re-proving` events.
- Median proof time is 1936 s (p90 2904 s) over 43 proofs (the max `t+` per `waiting proof` line).

Rejected:
- A print in merge_pr.sh appears when the merge is already executing, not when it is chosen, so
  it changes no decision.
- The decision point already has the information: the live train's spool and its train.log
  `waiting proof ... t+` line.
- The cheaper route already exists: `merge_train.py` add joins the live train after the running
  batch (train.log: `ADDED #3485 to the live train`).
- Measured benefit tonight: 0 re-proves avoidable.

Cost avoided: about 8 lines in merge_pr.sh and a self-test arm.

Binding: the zero marginal re-prove; a print at execution time cannot price a decision.
