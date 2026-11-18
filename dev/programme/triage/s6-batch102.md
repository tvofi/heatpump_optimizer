# Proposal triage, session s9, batch 102 (P358, P359)

The rolling batch after batch 101, which was pushed first and left at its head. Facts were read at
origin/main `c3b7c964f`, at the round's roster branch `origin/handoff/audit-r10-roster`
(`3f6dc470f`), on pull requests #3080 and #3090, and in the bus's local verdict store.

## P358: carry_audit reads `Carry: G | dismissed: <reason>` as a dismissal

Verdict: ACCEPT, narrowed to part (1), as one carry on R10-BODY-CONTRACT. Part (2), a later body
`Carry:` superseding a verdict's destination, is REJECTED.

Source: the orchestrator s9's queue line of 2026-11-01T14:15:58Z, from #3080. The train parked
#3080 on its verdict's item bd9082e1. The orchestrator merged it directly under the mandate.

Instances:
- **#3080.**
  - Verdict comment 6553573489 carries `Carry: R10-FLY-ABORT-OWN-MERGE | dismissed: suggestion
    for the fixer to state; no ruling change needed.`
  - `python3 -I tools/audit/carry_audit.py pr 3080` prints `BAD-DEST ... R10-FLY-ABORT-OWN-MERGE
    is done`, also after the body gained `Carry: R10-TRAIN-OVERLAP-GRADE (item bd9082e1)`:
    `1 routed, 0 unrouted, 1 bad destination(s)`.
- **Why it parks.**
  - `seg_dests` (`tools/audit/carry_audit.py` line 267) splits on `|` and keeps the group token.
  - Its next token, `dismissed:`, is neither a group, an issue nor a brief, so the scan stops
    there. The reviewer's dismissal is never read.
  - `Dests.check` then requires the group to be live, which a pointer to a finished group cannot
    be.
- **How common the form is.**
  - `grep -rhoE 'Carry: [A-Z0-9-]+ \| dismissed:'` over the bus's local verdict store (651 PR
    directories) finds 50 markers in 11 PRs.
  - Each such marker is a dismissal that names a group for context. It parks the PR whenever
    that group is done when the train reads it. One park has been observed, #3080.

Cost:
- **(1) as accepted.** About 5 lines in `seg_dests` and four self-test arms in
  `carry_audit.py --self-test` (1103 lines), with no new file and no new check.
  - `grep -n carry_audit tests/*_budgets.json` prints nothing, so no capped file is touched.
  - One S fixer on the group's model row.
- **(2) as proposed.** A body marker would override a reviewer's routing. That changes who may
  re-route a verdict's finding, a `finding-propagation.md` matter, which makes it a policy
  change and not a parser fix.
  - (1) alone clears the one observed instance, because that item was dismissed.
  - Nothing measured shows a verdict that routed a live carry to a done group and was not a
    dismissal.

Binding:
- **(1) clears the bar.** A handful of lines stops a dismissed note from parking a merge. The
  #3080 instance cost a train park and a mandate merge outside the train.
- **(2) has no measured instance.** Its cost is a policy surface, an author overriding the
  reviewer.
  - What would change the answer: a verdict whose live (non-dismissed) carry names a group that
    is done when the train reads it.
- **Why this group.** R10-BODY-CONTRACT is the live group that lists
  `tools/audit/carry_audit.py` in its `files`, and nothing of it is in flight.

Carry (R10-BODY-CONTRACT, `s7/carries/b102-P358.txt`):

> From triage P358 (#3080 parked by the train: verdict 6553573489's item bd9082e1 reads `Carry:
> R10-FLY-ABORT-OWN-MERGE | dismissed: ...`, and R10-FLY-ABORT-OWN-MERGE is done).
> tools/audit/carry_audit.py `seg_dests` keeps the group token of `Carry: G | dismissed: <reason>`
> and stops at `dismissed:`, so the dismissal is lost and `Dests.check` demands a live G. Change:
> when a segment's tokens are destinations followed by `| dismissed: <reason>`, return the
> dismissal alone. G is a pointer, valid when it is any group of the roster, live or done. A
> segment without `dismissed:` is read exactly as today.
> Controls, in `carry_audit.py --self-test`:
> - `Carry: <done group> | dismissed: two words` is routed;
> - null control: `Carry: <done group>` alone is still BAD-DEST;
> - `Carry: <unknown token> | dismissed: two words` is refused as not a group;
> - one mutant that drops the dismissal branch leaves the first arm red.
> triage: dev/programme/triage/s6-batch102.md#P358

Roster op (queued `#held` until this file is on origin/main):
1. `append-carry R10-BODY-CONTRACT @.../s7/carries/b102-P358.txt`

Rule run on the instance: under the carry, item bd9082e1 reads as `dismissed:` with the pointer
R10-FLY-ABORT-OWN-MERGE, which exists, so #3080's audit would read `0 bad destination(s)`.

## P359: four held carries aimed at R10-FLY-TRAIN-DEFAULTS

Verdict: ACCEPT. R10-FLY-TRAIN-DEFAULTS is not reopened. The four held carries go to
R10-TRAIN-MERGE-LOOP, verbatim, each under one re-route sentence.

Source: orchestrator s9, by message, 2026-11-01. The held lines are queue lines 778
(`census-3`), 879 (`strand-31`), 881 (`strand-32`) and 939 (`strand-60`). Each is `append-carry
R10-FLY-TRAIN-DEFAULTS`. The strand carries say "Fold into: R10-FLY-TRAIN-DEFAULTS (live)" as of
2026-10-31.

Instances:
- **The group is done, and its part 2 is in flight under the old name.**
  - On the roster branch, R10-FLY-TRAIN-DEFAULTS is `done` at `a44a740eb` (#3010). Its
    `resume.note` records the s9 carry-routing pass, which sent its open carries to
    R10-TRAIN-POSTMERGE ("Part 2 of R10-FLY-TRAIN-DEFAULTS"), R10-TRAIN-MERGE-LOOP and
    R10-FLY-STANDING-CONTRACTS.
  - #3090, "R10-FLY-TRAIN-DEFAULTS (part 2)", is OPEN at `41790e2b8`. It touches
    `postmerge.py`, `merge_pr.sh`, `merge_train.py`, `record_beat.py` and `train.sh`, which is
    R10-TRAIN-POSTMERGE's brief.
- **Reopening is the wrong repair.**
  - `set-stage R10-FLY-TRAIN-DEFAULTS carries-open` would make two live groups for one seam.
  - Its carries would also join a lane whose PR is already in review, which is why
    `census-3` was held until "the part-2 PR merges". After #3090 merges the group is done
    again, and the four would be stranded a second time.
- **R10-TRAIN-MERGE-LOOP is the train's live residue group.**
  - It is `not-started` on `merge_train.py`, and its brief says it "Runs after
    R10-TRAIN-POSTMERGE, which edits the same file".
  - So it is not in flight, and nothing of #3090 can be refused for a carry it never had. No
    hold on #3090 is needed.
  - Its brief already covers the train's GitHub reads (the review settle and one shared Actions
    job-log reader). `strand-31` (a git-transport retry in `merge_train.py`) and `strand-32` (a
    harness `pages()` retry) belong beside that reader. `census-3` (admit after the
    post-approval gate) and `strand-60` (undraft a proved head) are merge-step and admission
    steps in the same file.

Cost: four carry appends and four withdrawn lines; no file, check or capped file.

Binding: a carry on a done group is never dispatched, so leaving the four where they point
loses them. Reopening would create two live owners of one seam and strand them again at #3090's
merge.

Carries: `s7/carries/b102-P359-<name>.txt` for each of `census-3`, `strand-31`, `strand-32` and
`strand-60`. Each is the original file verbatim, under the first line "Re-routed by triage P359
from R10-FLY-TRAIN-DEFAULTS (done; part 2 #3090 in flight) to R10-TRAIN-MERGE-LOOP." and above a
last line `triage: dev/programme/triage/s6-batch102.md#P359`.

Roster ops (queued `#held` until this file is on origin/main): one `append-carry
R10-TRAIN-MERGE-LOOP @.../s7/carries/b102-P359-<name>.txt` per carry. Queue lines 778, 879, 881
and 939 are marked `#superseded`.
