# Proposal triage, session s9, batch 92 (P331)

The rolling batch after batch 91 (#3043). Facts were read at origin/main `811112b78`.

## P331: the train SKIPs an approved pull request while the approval's review run is still settling

Verdict: ACCEPT, reframed, as one carry on R10-FLY-TRAIN-DEFAULTS (`carries-open`, size S; its
`files` name `tools/audit/seat/merge_train.py`).
- **The proposed mechanism is already built.** After the approval, the train already waits for
  something before the first merge attempt. `review_settle` (P86, `s6-batch17.md`) runs before
  attempt 1 and polls the head's `pull_request_review` runs (`merge_train.py` lines 2095-2110 at
  `811112b78`).
- **The two defects are its bound and the classifier after it.**
  - **The bound fits the 70-s runs P86 measured, not today's.** It is `polls` = 24 grains of
    `REVIEW_POLL_SECONDS` = 5 (lines 601 and 1026), about two minutes of sleep. The last 59
    completed `CI review pr=<n>` runs read at 2026-10-31T14:5xZ took 91 s at p50, 2388 s at p90,
    5549 s at p95 and 10626 s at most. 22 of the 59 ran over 150 s, which is the CI concurrency
    queue. The train log holds 13 `review run(s) ... (24/24)` lines, so the wait ran out with the
    run still open.
  - **The classifier reads the settling state as a missing review.** `policy_refusal` (lines
    2058-2093) returns "every required context is green, so the missing requirement is a review",
    with `wait` False, for `mergeStateStatus BLOCKED` and `reviewDecision APPROVED`. `land` then
    stops the entry as `[BRANCH-POLICY]` on that attempt, even though the approval at the head is
    the train's own. That holds both while the review run is open and in the seconds after it
    concludes, before GitHub recomputes mergeability.
- **Field instances, from `train/current.log`.** In each one a `review run(s)` wait comes before
  the SKIP:

  | PR | review-run wait | merge attempts | outcome |
  |---|---|---|---|
  | #3031 | ran out at `(24/24)`; run 41211188623, 14:40:04Z to 14:46:10Z | 6 | merged later at the same head, `811112b78` |
  | #3039 | ended at `(14/24)`; run 41196240353, 11:17:29Z to 11:18:48Z | 1, refused right after the run concluded | re-added unchanged at 49c16053, merged later at `ecca12ceb` |
  | #3013 | ran out at `(24/24)` | 2 | — |
  | #3000 | ended at `(19/24)` | 1 | — |

  #3013 touches a code-owned file (`away.py`), so part of its block may have been the owner's
  review. It is not counted as clean evidence. The other two BRANCH-POLICY SKIPs that day, #2989
  and #2968, read "no owner APPROVED review citing one mandate" and had no review-run wait. They
  are a different cause and stay untouched.
- **Proposed form, narrowed.** "Wait for the gate check-run" is replaced by the run the policy
  actually waits on, the head's `pull_request_review` run. That is what `review_settle` already
  lists. The policy refused #3031 and #3039 while `policy_refusal` read "every required context is
  green", so a poll of the `gate` rollup alone would have seen nothing to wait for.

Source: the orchestrator s9's triage-queue line of 2026-10-31T14:50:00Z (slip, recurring, two
instances today).

Instances: as tabled above. The run durations come from
`gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>` (2 calls), and the distribution from one
`gh api 'repos/tvofi/heatpump_optimizer/actions/runs?event=pull_request_review&per_page=60'` read:
59 completed, p50 91 s, p90 2388 s, p95 5549 s, max 10626 s, 22 over 150 s and 15 over 420 s.
`grep -c 'review run.*(24/24)' train/current.log` gives 13.

Cost: S inside `merge_train.py`. That is `review_settle`'s bound and one arm of `policy_refusal`,
about 20 lines, plus three self-test rows and one mutant. `merge_train.py` has no
`policy_lint.mjs --budgets` row and no `tests/structure_budgets.json` key; the `--budgets` output at
`811112b78` names it 0 times. No policy file changes. It adds no GitHub write. The extra reads are
the same `actions/runs?event=pull_request_review&head_sha=` listing `review_settle` already makes,
at `POLL_SECONDS` grain once the fast grain is spent.

Binding:
- Each SKIP costs a manual re-add by the orchestrator and the entry's batch slot. The re-add starts
  a fresh train, and a solo train in this log runs 48 to 67 minutes (P330).
- Two of the four instances today, #3031 and #3039, later merged at an unchanged head, so those
  stops were wrong.
- The fix is about 20 lines on a seam the train already owns, and no rule changes. Waiting on a
  settling review run costs at most the CI wait the train already accepts for a pending context.
- A wait is not a merge, so the existing gates are unchanged.

The carry:
1. **Bound `review_settle` by time, not by a 2-minute count.** Keep the 5-s grain for the first 24
   polls. Then poll at `POLL_SECONDS` while a `pull_request_review` run at the head is unfinished,
   up to the train's existing CI-wait budget (`polls` x `POLL_SECONDS`).
   - Log `review run ... still running` at most once per `POLL_SECONDS`.
   - When the budget runs out, the merge attempt proceeds as today.
2. **Treat a settling review run as a wait in `policy_refusal`.** In the branch that returns "the
   missing requirement is a review", return `wait` True instead when both of these hold:
   - a `pull_request_review` run at the head is unfinished, or concluded fewer than 120 s ago (one
     read of the same listing);
   - an approver APPROVED review sits at exactly that head.

   `land`'s existing `merge_tries` x 30-s loop bounds this. Every other branch is unchanged: a red
   context, CHANGES_REQUESTED, and a missing owner review with no review run open still park at
   once.
3. **Fixtures.**
   - #3031's shape: an approval at t0, the review run open past 24 fast polls, and the merge
     attempted only after the run concludes. It lands, with no SKIP.
   - #3039's shape: the run concludes, and the first merge is refused BLOCKED/APPROVED within
     120 s. That is a wait, and attempt 2 lands.
   - Null, still a park: BLOCKED/APPROVED with no review run at the head in the last 120 s
     (#2968's shape, the missing owner review).
   - Null, still a park: a required context red.
4. **One mutant.** Drop arm 2's run check, and the #3039 row SKIPs.

Rejected: polling the `gate` check-run as filed. In both clean instances the rollup already read
every required context green when the policy refused, so that poll would not have waited.
