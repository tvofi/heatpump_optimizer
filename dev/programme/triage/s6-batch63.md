# Proposal triage, session s7, batch 63 (P291)

The rolling batch (V182) after batch 62 (#2972, merge verdict at `9742a6e5d`, not yet merged).
Facts were read at origin/main `2ab53fe90590dee8376e800af2f09fd94bc75703` and in the live train
log.

## P291: a re-add of a skipped pull request is dropped as ALREADY

Verdict: ACCEPT, as already ruled. The fix is P129 (`s6-batch26.md`) as amended by P189
(`s6-batch32.md`), which sit as accepted carries on R10-TRAIN-OVERLAP-GRADE but are not built. This
ruling adds one carry with the new instances, which give the fixer a failing test from the field.
Dispatch is the lever, and it does not wait on this batch: the rulings that specify the fix are
already on main.

Source: the orchestrator's triage-queue line of 2026-10-29T23:39:17Z. `merge_train` `add` drops a
re-add as "ALREADY in this train" when the earlier entry was skipped, or was left out of a formed
batch (#2917, #2872, #2961 and #2970 in batch `20261029-193537-b4`). The proposal: dedupe only
against entries still pending or in the live batch, and re-queue a skipped entry on an explicit
re-add.

Instances, from the live `merge_train/train.log` (train pid 34197):
- **Three entries dropped when batch 4 formed.** These lines come straight after
  `SKIP REPORT: 5 skipped of 10`:
  - `ALREADY #2917: in this train already; not queued twice`
  - `ALREADY #2872: ...`
  - `ALREADY #2961: ...`
  The batch then took `#2971 #2972 #2964 #2969 #2955`. #2917 had been skipped 4 times at carry,
  and #2872 at ci (`SKIP #2872 ci: ... TIMEOUT`).
- **#2970 was refused from the pending layer.** It was skipped at merge (`SKIP #2970 merge: not
  merged after 8 attempts`). Its two re-adds logged `ALREADY #2970: queued in the live train (pid
  34197); nothing added`. That is the `QUEUE_PENDING` arm P189 removes for a skipped entry.
- **The fix is specified and unbuilt.** R10-TRAIN-OVERLAP-GRADE (`carries-open`, next step
  "dispatch a fixer") carries P129's one shared admission predicate for `train_add` and
  `queue_take`. A skipped entry re-added at a new verdict head is admitted to the next batch.
  P189 adds three things: `Train.skip` leaves `QUEUE_PENDING`, the same-head HOLDER exception
  applies, and that exception lives in the shared predicate (the #2846 round-2 carry).
  `merge_train.py` still has the two separate checks (`train_add`, `Train.queue_take`), and both
  `ALREADY` spellings above come from them.
- **The rule run on each instance.**
  - #2970: skipped at merge and re-added at the same verdict. Under P189 it is ALREADY unless
    the skip class was HOLDER. So the instance shows a gap: a merge-step refusal by branch
    policy is environmental, like HOLDER, and should re-admit at the same head.
  - #2917: skipped at carry. It re-enters at a new head (`a361e454`), so P129 admits it.
  - #2872: skipped at ci. It re-enters at its new head after the fixer, so P129 admits it.
  - #2961: blocked, and re-enters at the fixer's new head, so P129 admits it.

Cost: no new group. One carry on R10-TRAIN-OVERLAP-GRADE, and the fixer's run of the existing
admission carries, which are S within that M group. `merge_train.py` has no `policy_lint.mjs
--budgets` row. Benefit, measured: 4 verdicted heads, critical-path #2917 among them, out of
batch 4 of one train. Each waits for the train to end.

Binding: dispatch order on R10-TRAIN-OVERLAP-GRADE, not this batch. Until the fix lands, a new
train re-admits every entry, because `seen` is per train. That is the available workaround for a
critical-path entry dropped this way.

The carry: the field fixture is the batch-4 shape above, with three skipped entries dropped as
ALREADY when a batch forms, plus one merge-skipped entry refused from the pending layer.
1. P189's HOLDER exception also covers a `merge` skip whose last refusal is GitHub's branch
   policy, which is environmental and not the head's.
2. Control: re-added at the same verdict, such an entry joins the next batch. ADDED is logged on
   both sides.
3. Null control: a `carry` skip at the same verdict stays ALREADY.
