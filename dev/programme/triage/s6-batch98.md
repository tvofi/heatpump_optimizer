# Proposal triage, session s9, batch 98 (P353)

The rolling batch after batch 97, which was pushed first and left at its head. Facts were read at
origin/main `61b0076f4`, at the round's roster branch `origin/handoff/audit-r10-roster`
(`5cfbe719e`), and in the merge seat's logs under `s9/seat-merge/`.

## P353: remerge_main.sh drops the failing arms of a prepr refusal

Verdict: ACCEPT, narrowed, as one carry on R10-FLY-ABORT-OWN-MERGE, reopened to `carries-open`.

Source: orchestrator s9, by message, 2026-11-01. The merge seat found it on #3052's recarry.

What is narrowed:
- **The premise is half right.** The failing arms are not lost.
  - prepr writes its full log with `mktemp "${TMPDIR:-/tmp}/prepr-log.XXXXXXXX"`
    (`tools/pr/prepr.sh` line 3502) and never deletes it. Its result line names that file:
    `PRE-PR: ... full log: $PREPR_LOG` (line 3508).
  - The run #3052 refused is `$TMPDIR/prepr-log.h6GW1PlY`, which is still on disk. It matches on
    three readings: the refusal `REFUSE   self-test   429 passed, 2 failed` (its line 18), the
    heavy-slot line `slot=2 ... expires_at=2026-11-01T01:41:03Z`, and a modification time of
    01:32:48Z, against `rm3052.log`'s 01:32:54Z.
  - Its line 19 names both failing arms:
    - "and pushes a body the lint passes (null control: the same body without the session
      link) (got 1, wanted 0)";
    - "and that body's commit names the handoff head it describes in a Code: trailer (V147)
      (got 1, wanted 0)".
- **What is lost is the pointer.** `remerge_main.sh` (40 lines at `61b0076f4`) does two things:
  - it prints only `grep -E 'RECARRY|REFUSE|PUSHED'` of app_push's output (line 39). That drops
    both the FAIL line and the `full log:` line;
  - it deletes that output, `$B.push.log`, in its EXIT trap on every exit
    (`pr_exit_trap 'rm -f "$PL"'`, line 19).

  `merge_train.py` quotes remerge's stdout in its Stop message (`o.strip()[-2000:]`, at the
  `raise Stop("recarry", ...)` after line 1837), so the train's stop carries the same gap.
- **The ask is narrowed to what restores the pointer.** The fix prints the FAIL lines and the
  `full log:` line, and keeps the push log only when nothing was pushed. Keeping the log on every
  non-zero exit would also keep it for a stop that pushed, which is what the trap's deletion
  prevents. The pattern already exists in `pr_args.sh`: `pr_push_failed` (line 180) greps REFUSE
  and names the log it keeps.

Instances:
- **One remerge prepr refusal in the logs.** `grep -rl 'RECARRY: prepr RUNS'` over
  the session state directory finds 6 logs:
  - four are direct `app_push` runs for #2854, under `s7/fix-2854-conflict/`, each keeping its
    own log;
  - one is #3052's refused remerge (`s9/seat-merge/rm3052.log`). Its stdout is 5 lines and no FAIL
    line;
  - one is the re-run now in flight (`s9/seat-merge/body3052.md.push.log`, merge base
    `61b0076f4`).
- **The cost of that one instance.**
  - The refused run took 2 h 19 min of wall time: the daemonize banner is 23:13:32Z, and the
    log's modification time is 01:32:54Z.
  - Of that, it held a heavy slot for about 22 min. The lease is 1800 s and expired at
    01:41:03Z, so it was taken at 01:11:03Z.
  - The merge seat then started a re-run under `bash -x` (`rm3052b.log` and `rm3052c.log`,
    03:38Z). That re-run holds slot 0 now, to recover the two lines quoted above.
- **How often a remerge runs prepr at all.** Rarely: `app_push.sh --recarry` skips prepr on a
  clean two-parent merge under the live body, and the train's recarries mostly are that. The
  benefit is therefore per refusal, not per merge: one re-run (here 2 h 19 min of wall time,
  queued behind the slot) is avoided each time.

Cost:
- One S fixer on sonnet with an opus reviewer, which is the group's own model row.
- About 6 lines in `tools/audit/seat/remerge_main.sh` (40 lines), and three arms beside the
  existing `remerge_main` arms in `pr_args.sh`'s self-test (lines 705-717, which already stub
  app_push).
- No capped file. `grep -n 'pr_args\|remerge' tests/*_budgets.json` prints nothing.
- No new file, no new check and no API call. `merge_train.py`'s parsing (`MERGE CONFLICT`,
  `PUSHED`, `RECARRY:`) and remerge's exit status are unchanged.

Binding:
- **Why it clears the bar.** A handful of lines and three arms recover a diagnosis that today
  costs a full re-run in a heavy slot. The one measured instance cost 2 h 19 min of wall time and
  a second slot.
- **Why this group.** The owning seam is `remerge_main.sh`. R10-FLY-ABORT-OWN-MERGE owns exactly
  that file and `pr_args.sh` (its `files`), and no pull request of it is in flight.
- **Why not the alternatives.**
  - R10-FLY-OPENPR-ATOMIC owns `open_pr.sh`, a different runner.
  - R10-TRAIN-OVERLAP-GRADE and R10-FLY-TRAIN-DEFAULTS own `merge_train.py`. Each has a second
    part in flight (#3063, and the census-3 hold), and the fix does not touch the train.

Carry (R10-FLY-ABORT-OWN-MERGE, `s7/carries/b98-P353.txt`):

> From triage P353 (merge seat, #3052 recarry refused by prepr "REFUSE self-test 429 passed,
> 2 failed"). tools/audit/seat/remerge_main.sh keeps only `grep -E 'RECARRY|REFUSE|PUSHED'` of
> app_push's output, and its EXIT trap deletes the push log `$B.push.log` on every exit. A prepr
> refusal therefore reaches merge_train.py's Stop message (which quotes remerge's stdout) without
> the FAIL lines that name the failing arms, and without prepr's `PRE-PR: ... full log: <path>`
> line. That full log survives in $TMPDIR, but nothing names it. Fix, in remerge_main.sh only;
> merge_train.py's parsing and remerge's exit status are unchanged:
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
> triage: dev/programme/triage/s6-batch98.md#P353

Roster ops (queued #held until this file is on origin/main):
1. `set-stage R10-FLY-ABORT-OWN-MERGE carries-open`
2. `append-carry R10-FLY-ABORT-OWN-MERGE @.../s7/carries/b98-P353.txt`

Rule run on the instance: #3052's refusal, `rm3052.log`. Its stdout has no FAIL line and no
`full log:` line, and `$B.push.log` was deleted. Under the carry, both lines and the kept log's
path would have been printed, and the re-run under `bash -x` would not have been needed.
