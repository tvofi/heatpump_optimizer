# Proposal triage, session s14, batch 173 (P590)

This batch rules queue line 269 (the orchestrator's merge-train intake), 2026-11-11.

Sources:
- origin/main `e67b79c9fc`. Every line number below is at that commit.
- The merge train's log, `~/.local/state/hpo/merge_train/train.log`, lines 19707-19850 (batch
  `20261111-002834-b4`).
- The jobs of code run 42969771406 at 141f8af1, read once from the Actions API (41 jobs).

## P590: TRAIN-DEFER-WAIT-UNDER-RUN and POLICY-REFUSAL-REVIEW-MISREAD

Verdict: ACCEPT, re-pointed, as a carry on R10-GATE-DEFER-BARRIER (stage not-started, size M).
That group owns the seam: its brief has every reader of the gate conclusion, `merge_train`'s
`policy_refusal` first, treat a deferral red as provisional, and it holds the moved
R10-HOTFIX-TRAIN-DEFER-WAIT carries. R10-TRAIN-RESIDUE, which owns `merge_train.py`, is
`carries-open` since PR 3424 merged at 07:47:51Z. It is therefore not `carry_receivable`, and the
drain refused the first queue line (4391) on that ground. The proposal's remedy "count the wait from the code run's START" is rejected:
the run started before the wait did, so counting from its start makes the wait shorter.

Source: the orchestrator's queue line 269, 2026-11-11. It reports that #3398 was skipped as
`ci red TIMEOUT` although its code run concluded success minutes later, and that the train first
logged "the missing requirement is a review" while two approvals stood at that head.

### Defect 1: the deferral wait is bounded by `polls`, and a legitimate code run outlasts it

- **What happened.** `wait_ci` (`merge_train.py:1905`) loops `for k in range(1, self.polls + 1)`
  (`:1934`), with `polls: int = 24` (`:1512`), and returns `["TIMEOUT"]` (`:2000`). The log shows
  the deferral read at 141f8af1 ("gate red ... is a deferral while ci.yml run(s) [42969771406]
  are unfinished"), then beats at t+244 s through poll 24 at t+5589 s, then
  `#3398 141f8af1 ci red=['TIMEOUT']` and `SKIP #3398`. The beats are about 243 s apart, not
  305 s.
- **The run.** Code run 42969771406 was created at 06:03:35Z and completed `success` at
  07:41:18Z, 5863 s in all. The wait ran out after about 5589 + 243 s. Its critical path:
  - `prelude` queued 305 s, ran 36 s;
  - `tests / mutation` queued 74 s and **ran 5282 s**;
  - `pr-contract`, `gate` and `sweep-self` took about 160 s together.
- **The proposal's question: job-cap queueing against the wait budget.** The queue time on the
  critical path was about 385 s, or 6.6% of the run. Queue time over all 41 jobs was 3853 s, but
  it was spread over jobs running in parallel. So the job cap did not cause the miss. The cause
  is that a fixed 24-poll budget (about 97 min) is shorter than a healthy code run. One
  mutation job ran 88 min, and `tests.yml` sets job ceilings of 90, 160 and 350 minutes.
- **What the miss cost.** The skip is per verdict. The log reads "ALREADY #3398: skipped by this
  train at this same verdict 141f8af1b1a5; a new verdict head re-admits it". An outside PR,
  which ranks first in the queue, lost its batch.
- **Frequency.** The train log holds 6 `ci red=['TIMEOUT']` lines (#2872, #3006, #3304, #3358,
  #3355, #3398). The last three came within two days.
- **The fix.**
  - While the deferral is read and the sibling ci.yml run at this head reports `in_progress` (it
    has started), bound the wait by that run's own deadline: its `run_started_at` plus a ceiling,
    such as the longest `timeout-minutes` among the jobs still running, or one named constant.
    Do not bound it by `polls`.
  - A run still `queued`, or past its deadline, keeps the `polls` bound and ends as TIMEOUT. The
    self-test check "defer-wait bound: a code run that never finishes ends in TIMEOUT within
    `polls`, never merges" (`:6695`) is kept, with its fake clock run past the new deadline. The
    R10-HOTFIX-TRAIN-DEFER-WAIT bound is never removed, only aimed at the run's own clock.
  - The cost is that the record beat holds longer behind such a wait (`TRAIN HOLD ... the record
    beat waits` was logged 24 times here). That is bounded by the same deadline.

### Defect 2: `policy_refusal` names a review when the deferral is the block

- **The code.** `policy_refusal` (`merge_train.py:2792`) collapses `statusCheckRollup` into
  `last[name]` (`:2813`). The last same-named entry wins. Here, a `CI review` run's `gate` is
  success, and it hides the edit run's deferral `gate`. With nothing red or pending, `BLOCKED`
  becomes "every required context is green, so the missing requirement is a review" (`:2829`).
  That holds even under `reviewDecision APPROVED`.
- **Measured over the whole train log.**
  - 66 lines carry that inference, and all 66 say `reviewDecision APPROVED`.
  - In 8 of the 66 (12.1%), the train's own deferral read ("is a deferral") follows within 6
    lines.
  - **Null control:** 1.4% of all log lines are followed by a deferral read within 6 lines. Of
    the 9 park lines with any other reason, none is.
  - So the inference over-fires where the deferral is the block. It does not account for all 66:
    the ruleset's last-push approval is a real cause, as the docstring says.
- **The fix.**
  - Before naming a review, read the head's same-named required contexts, not the collapsed
    `last`. Where any of them is a deferral-shaped red, or its sibling ci.yml run is unfinished,
    return `wait` with the deferral reason. Use the predicate `wait_ci` already uses at `:1951`.
  - Under `reviewDecision APPROVED`, word the remaining case as a last-push approval at the moved
    head, never as "a review".
  - The self-test seeds a rollup that holds both a success `gate` (review run) and a failure
    `gate` (edit-run deferral) at one head. It asserts `wait` and no review wording.

### What it costs and what it saves

- **Cost:** one carry in a not-started group that already owns the deferral seam. It is two bounded edits plus two self-test cases in
  one file, about 1-2 fixer hours.
- **Benefit:** 3 TIMEOUT skips in two days, each losing a batch of hours. The latest one was an
  outside PR, which the queue ranks first. The 8 misread parks also mislead a seat into chasing an
  approval that already stands.
- The benefit clears the 20% bar. It is accepted as a carry, not as a permanent new mechanism.

### Operational, not part of the carry

#3398 stays out of this train until a new verdict head re-admits it. That re-add is the
orchestrator's call.
