# Proposal triage, session s9, batch 101 (P357)

The rolling batch after batch 100, which was pushed first and left at its head. Facts were read at
origin/main `c3b7c964f`, at the round's roster branch `origin/handoff/audit-r10-roster`
(`3f6dc470f`), and on pull request #3080.

## P357: move P353's and P354(a)'s carries off groups that are done

Verdict: ACCEPT, an amendment that changes two destinations and leaves each carry's ask and
controls as they were ruled:
- **P353** (batch 98) is re-routed to R10-TRAIN-OVERLAP-GRADE. Its `set-stage
  R10-FLY-ABORT-OWN-MERGE carries-open` is withdrawn, so no done group is reopened.
- **P354(a)** (batch 99) moves from R10-FLY-TRAIN-DEFAULTS to R10-TRAIN-MERGE-LOOP.

Source: orchestrator s9, by message, 2026-11-01. The train parked #3080, batch 98's record pull
request, because a finding is routed to a group that is done. The orchestrator ruled that a carry
goes to the live group owning the concern, never to a done group.

Instances:
- **#3080 is parked.**
  - `python3 -I tools/audit/carry_audit.py pr 3080` prints `BAD-DEST #3080 review 6553573489
    item bd9082e1: R10-FLY-ABORT-OWN-MERGE: R10-FLY-ABORT-OWN-MERGE is done (resume.stage done)`
    and `0 routed, 0 unrouted, 1 bad destination(s)`.
  - The item is the verdict's suggestion, `Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: ...`.
  - R10-FLY-ABORT-OWN-MERGE is `done` on origin/main's roster and on the roster branch.
- **P354(a) has already landed on a done group.**
  - On the roster branch, R10-FLY-TRAIN-DEFAULTS is `done` (#3010), and the P354 carry is its
    last `carry` entry (index 5). Queue line 1006 is `#done`.
  - That group's `resume.note` records the s9 carry-routing pass. The pass moved P331's carry,
    the train's verdict and approval reading named in P354's Binding, to R10-TRAIN-MERGE-LOOP,
    and moved the group's other open carries to R10-TRAIN-POSTMERGE. P354(a) was appended after
    that pass, so nothing moved it.

The new destinations:
- **R10-TRAIN-OVERLAP-GRADE owns P353's seam.**
  - It is `carries-open` on the roster branch and `in-review` on origin/main, so both readings
    count it as live.
  - It already carries remerge_main.sh: "Stale train holders (V104 slip, #2753, s40 -> s41). (a)
    `tools/audit/seat/remerge_main.sh` line 21 ...". It also owns the train's recarry-and-wait
    path, and that path is where remerge's stdout is quoted.
  - P353 passed over it because its part 2 was in flight. That part, #3063, has merged, and no
    pull request of this group is open (`gh pr list --state open`).
- **R10-TRAIN-MERGE-LOOP now owns P354(a)'s seam.** P354 sent (a) to R10-FLY-TRAIN-DEFAULTS
  because that group owned the train's verdict and approval reading, its P331 carry. That carry
  is now R10-TRAIN-MERGE-LOOP's (`not-started`, `merge_train.py`).
- **Both instances still hold at origin/main `c3b7c964f`.**
  - remerge_main.sh line 19 is `PL=$B.push.log; pr_exit_trap 'rm -f "$PL"'`, and line 39 is the
    `grep -E 'RECARRY|REFUSE|PUSHED'`.
  - `posted_verdict` in `merge_train.py` is unchanged since batch 99.

Cost:
- Two carry moves through `roster_edit.py`, plus one `drop-carry` and one withdrawn `set-stage`.
- No change to either fix's lines, files, model row or controls as batches 98 and 99 priced
  them. No capped file, no new file and no new check.

Binding:
- **What it buys.** Without the move, neither carry is ever dispatched, because a done group is
  not dispatched.
- **Reopening is no cheaper.** It would turn a finished group back into a lane for one S carry,
  against the orchestrator's ruling. A live owner of the same file already exists.
- **What this amendment cannot clear.** The verdict comment's own marker on #3080 still names
  R10-FLY-ABORT-OWN-MERGE. `carry_audit` adds every marker's destinations and keeps each one
  (`audit`: `r["dests"] + refs.get(...)`), so a body marker naming item bd9082e1 adds a live
  destination but does not drop the done one. Whether that marker is cleared is the
  orchestrator's call.

Carry (a), R10-TRAIN-OVERLAP-GRADE, `s7/carries/b101-P357a.txt`. It is P353's carry with only
the citation changed:

> From triage P353 (merge seat, #3052 recarry refused by prepr "REFUSE self-test 429 passed,
> 2 failed"), re-routed by P357 from R10-FLY-ABORT-OWN-MERGE (done) to this group, which owns the
> train's recarry path and already carries remerge_main.sh. tools/audit/seat/remerge_main.sh keeps
> only `grep -E 'RECARRY|REFUSE|PUSHED'` of app_push's output, and its EXIT trap deletes the push
> log `$B.push.log` on every exit. A prepr refusal therefore reaches merge_train.py's Stop message
> (which quotes remerge's stdout) without the FAIL lines that name the failing arms, and without
> prepr's `PRE-PR: ... full log: <path>` line. That full log survives in $TMPDIR, but nothing
> names it. Fix, in remerge_main.sh only; merge_train.py's parsing and remerge's exit status are
> unchanged:
> (1) also print app_push's FAIL lines and the `full log:` line;
> (2) when the output holds no PUSHED, keep `$B.push.log` and print
> `remerge: push log kept: <path>`, as pr_args.sh's pr_push_failed names its log; a PUSHED run
> still deletes it.
> Controls, as arms beside the existing remerge_main arms in pr_args.sh's self-test (stub
> app_push):
> - a stub that prints a REFUSE line, a FAIL line naming an arm and a `full log:` line, and
>   pushes nothing: remerge prints all three and the kept log's path, and the log exists after
>   exit;
> - null control, a stub that prints PUSHED: the output is unchanged and the log is deleted;
> - one mutant that restores the old grep leaves the first arm red.
> triage: dev/programme/triage/s6-batch101.md#P357

Carry (b), R10-TRAIN-MERGE-LOOP, `s7/carries/b101-P357b.txt`. It is P354(a)'s carry verbatim,
with a re-route clause after its source and the citation changed to this entry.

Roster ops (queued `#held`):
1. `drop-carry R10-FLY-TRAIN-DEFAULTS --match 'From triage P354 (merge seat'`, released with op 2.
2. `append-carry R10-TRAIN-MERGE-LOOP @.../s7/carries/b101-P357b.txt`, released when this file is
   on origin/main.
3. `append-carry R10-TRAIN-OVERLAP-GRADE @.../s7/carries/b101-P357a.txt`, released when this file
   and `s6-batch98.md` are both on origin/main.

Batch 98's two held lines, the `set-stage` and its `append-carry`, are marked `#superseded` and
never released.

Rule run on each instance:
- **#3080's item bd9082e1.** Under the move, its live destination is R10-TRAIN-OVERLAP-GRADE.
  Recorded in #3080's body as `Carry: R10-TRAIN-OVERLAP-GRADE (item bd9082e1)`.
- **The P354 entry on R10-FLY-TRAIN-DEFAULTS.** It is dropped. R10-TRAIN-MERGE-LOOP gains it
  beside P331's carry, and the done group keeps nothing that is still owed.
