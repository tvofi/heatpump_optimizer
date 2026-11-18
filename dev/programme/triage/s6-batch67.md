# Proposal triage, session s7, batch 67 (P298)

The rolling batch (V182) after batch 66 (#2982, merge verdict at `8fd2d73a`, not yet merged).
Facts were read at origin/main `aced25893`, at #2978's head `882da1e0`, and in the live train
log.

## P298: the train's add-dedupe drops re-added pull requests

Verdict: ACCEPT as already ruled. This is P129 (`s6-batch26.md`), amended by P189 (`s6-batch32.md`)
and given its field fixture by P291 (`s6-batch63.md`), all carries on R10-TRAIN-OVERLAP-GRADE.
The fix is built: #2978, "R10-TRAIN-OVERLAP-GRADE part 2: one admission rule for add and the batch
drain", merge-verdicted at its head, approved and CLEAN. The proposal's key, (PR, head, verdict
tip), is NARROWED to #2978's key, (PR, verdict head, skip class). No new group or carry.

Source: the orchestrator's message of 2026-10-30, P298. `train.sh add` prints ADDED, then the live
train drops the PR with "ALREADY #N: in this train already; not queued twice". It does this for
any PR the train skipped or parked earlier in the same run, even after a fresh verdict or carry
at a new head. Instances: #2917 (twice), #2976, #2980, #2872 and #2961. Each then waits for TRAIN
DONE and a fresh train.

Instances, from the live `merge_train/train.log`:
- **The ADDED/ALREADY disagreement, in the log.**
  - #2976 is `ADDED` at line 2922 and `ALREADY #2976: in this train already` at 2956.
  - #2980 is `ADDED` at 2903 and `ALREADY` at 2957.
  - #2917 is `ADDED` at 2542 and `ALREADY` at 2644. Lines 2339-2341 are the P291 batch-4 shape
    (#2917, #2872, #2961).
  Each `ADDED` line comes from `train_add`, and each `ALREADY` from the drain (`queue_take`): the
  two checks P129 found disagreeing.
- **The fix in #2978.** At `882da1e0`, `merge_train.py` has one predicate, `already_held(pr,
  verdict, seen, spooled)` (line 885), "the admission rule `add` (`train_add`) and the drain
  (`Train.queue_take`) both apply (P129, P189, P291)".
  - A PR is held when it is spooled, pending, or merged or run by this train.
  - A PR skipped at the same verdict is also held, unless its skip class is in
    `READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)` (line 685).
  - A skipped entry at a new verdict is admitted.
  - `add` and the drain now return the same answer, so `add` prints the ALREADY reason, not
    ADDED. That is the proposal's "refuse loudly".
- **#2978's state.** It reads `reviewDecision: APPROVED`, `mergeStateStatus: CLEAN`, head
  `882da1e0`. `verdict/2978` reads `Fix review: merge 882da1e01b3d`.

Cost and benefit:
- **The fix is built.** Its cost is #2978's merge. Benefit: the five PRs named each lost a whole
  train run to the disagreement.
- **The key, narrowed.** Keying on the head as well would re-admit a recarried head, which is a
  new head at the same verdict, after every skip. A head whose carry keeps failing would then loop
  inside one train. The verdict head is the reviewed identity. A re-add at the same verdict is
  admitted only for an environmental skip class, and #2978 has those as `HOLDER` and
  `BRANCH_POLICY`.

Binding:
- **The lever is #2978's merge.** It is merge-ready now. In the train it goes ahead of other
  instrument PRs, since every train run until then repeats the drop.
- **One residue, recorded and not carried.** A PR skipped at carry because of an instrument defect
  keeps its verdict. That is the claim-file class, cured by #2977 (P297). Under #2978 it stays
  ALREADY at that same verdict for the rest of the run. A fresh train re-admits it, because `seen`
  is per train. That is the available step for #2975 and #2976 once #2977 merges. The class is
  not carried, since one train restart is cheaper than a skip class keyed on an instrument
  defect.
- **#2980's shape.** It is `ADD REFUSED` (line 2873, the stale verdict tip), then `ADDED`, then
  `ALREADY`, so it was refused without ever running. Re-check it after #2978 merges. A PR that
  never ran in a train, held as ALREADY, is not one of #2978's held states, and would be a new
  mechanism to bring back here.
