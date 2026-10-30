# Review packet #2983
head: fdc625099581f2f29f88caf2cc1dfddc94190645
base: aced258937628590b92265eea4c01276cac43b24

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123969425266 success
arch-score / arch-score id=123969326865 in_progress
arm id=123969222049 skipped
budget-raise-gate / budget-raise-gate id=123969326830 success
cancel-superseded id=123969162608 success
codeql / Analyze (actions) id=123969326831 success
codeql / Analyze (javascript-typescript) id=123969326838 success
codeql / Analyze (python) id=123969326858 success
governance / delivery-status id=123969326846 success
governance / delivery-status-publish id=123969329444 skipped
governance / env-matrix id=123969326910 in_progress
governance / instrument-self-tests id=123969326780 in_progress
governance / policy-docs id=123969326679 success
governance / record id=123969328936 skipped
governance / wave-script id=123969326779 success
hassfest / hassfest id=123969326577 success
kernel-points id=123969328117 skipped
prelude id=123969162352 in_progress
refresh id=123969162179 success
tests / arch-instrument id=123969495548 in_progress
tests / briefs id=123969326728 success
tests / browser id=123969495346 in_progress
tests / closure-scope id=123969326773 success
tests / closures id=123969495479 in_progress
tests / coverage id=123969495316 in_progress
tests / fast (3.14) id=123969495434 in_progress
tests / mutation id=123969326856 success
tests / mutation-autofix id=123969615832 skipped
tests / mutation-pins id=123969615292 skipped
tests / nightly-ha id=123969497437 skipped
tests / nightly-status id=123969327059 success
tests / replay id=123969497319 skipped
tests / typing id=123969495325 in_progress
validate / validate-hacs id=123969326616 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show 882da1e01:tools/audit/seat/merge_train.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         gh pr view 2978
             gh pr view: every long flag accepted

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2983.md b/dev/programme/delivery/2983.md
new file mode 100644
index 000000000..a0a806003
--- /dev/null
+++ b/dev/programme/delivery/2983.md
@@ -0,0 +1 @@
+- [#2983](https://github.com/tvofi/heatpump_optimizer/pull/2983) — **open**, triage: s7 batch 67 (P298 ruling) (R10-TRAIN-OVERLAP-GRADE)
diff --git a/dev/programme/triage/s6-batch67.md b/dev/programme/triage/s6-batch67.md
new file mode 100644
index 000000000..f1879ae79
--- /dev/null
+++ b/dev/programme/triage/s6-batch67.md
@@ -0,0 +1,62 @@
+# Proposal triage, session s7, batch 67 (P298)
+
+The rolling batch (V182) after batch 66 (#2982, merge verdict at `8fd2d73a`, not yet merged).
+Facts were read at origin/main `aced25893`, at #2978's head `882da1e0`, and in the live train
+log.
+
+## P298: the train's add-dedupe drops re-added pull requests
+
+Verdict: ACCEPT as already ruled. This is P129 (`s6-batch26.md`), amended by P189 (`s6-batch32.md`)
+and given its field fixture by P291 (`s6-batch63.md`), all carries on R10-TRAIN-OVERLAP-GRADE.
+The fix is built: #2978, "R10-TRAIN-OVERLAP-GRADE part 2: one admission rule for add and the batch
+drain", merge-verdicted at its head, approved and CLEAN. The proposal's key, (PR, head, verdict
+tip), is NARROWED to #2978's key, (PR, verdict head, skip class). No new group or carry.
+
+Source: the orchestrator's message of 2026-10-30, P298. `train.sh add` prints ADDED, then the live
+train drops the PR with "ALREADY #N: in this train already; not queued twice". It does this for
+any PR the train skipped or parked earlier in the same run, even after a fresh verdict or carry
+at a new head. Instances: #2917 (twice), #2976, #2980, #2872 and #2961. Each then waits for TRAIN
+DONE and a fresh train.
+
+Instances, from the live `merge_train/train.log`:
+- **The ADDED/ALREADY disagreement, in the log.**
+  - #2976 is `ADDED` at line 2922 and `ALREADY #2976: in this train already` at 2956.
+  - #2980 is `ADDED` at 2903 and `ALREADY` at 2957.
+  - #2917 is `ADDED` at 2542 and `ALREADY` at 2644. Lines 2339-2341 are the P291 batch-4 shape
+    (#2917, #2872, #2961).
+  Each `ADDED` line comes from `train_add`, and each `ALREADY` from the drain (`queue_take`): the
+  two checks P129 found disagreeing.
+- **The fix in #2978.** At `882da1e0`, `merge_train.py` has one predicate, `already_held(pr,
+  verdict, seen, spooled)` (line 885), "the admission rule `add` (`train_add`) and the drain
+  (`Train.queue_take`) both apply (P129, P189, P291)".
+  - A PR is held when it is spooled, pending, or merged or run by this train.
+  - A PR skipped at the same verdict is also held, unless its skip class is in
+    `READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)` (line 685).
+  - A skipped entry at a new verdict is admitted.
+  - `add` and the drain now return the same answer, so `add` prints the ALREADY reason, not
+    ADDED. That is the proposal's "refuse loudly".
+- **#2978's state.** It reads `reviewDecision: APPROVED`, `mergeStateStatus: CLEAN`, head
+  `882da1e0`. `verdict/2978` reads `Fix review: merge 882da1e01b3d`.
+
+Cost and benefit:
+- **The fix is built.** Its cost is #2978's merge. Benefit: the five PRs named each lost a whole
+  train run to the disagreement.
+- **The key, narrowed.** Keying on the head as well would re-admit a recarried head, which is a
+  new head at the same verdict, after every skip. A head whose carry keeps failing would then loop
+  inside one train. The verdict head is the reviewed identity. A re-add at the same verdict is
+  admitted only for an environmental skip class, and #2978 has those as `HOLDER` and
+  `BRANCH_POLICY`.
+
+Binding:
+- **The lever is #2978's merge.** It is merge-ready now. In the train it goes ahead of other
+  instrument PRs, since every train run until then repeats the drop.
+- **One residue, recorded and not carried.** A PR skipped at carry because of an instrument defect
+  keeps its verdict. That is the claim-file class, cured by #2977 (P297). Under #2978 it stays
+  ALREADY at that same verdict for the rest of the run. A fresh train re-admits it, because `seen`
+  is per train. That is the available step for #2975 and #2976 once #2977 merges. The class is
+  not carried, since one train restart is cheaper than a skip class keyed on an instrument
+  defect.
+- **#2980's shape.** It is `ADD REFUSED` (line 2873, the stale verdict tip), then `ADDED`, then
+  `ALREADY`, so it was refused without ever running. Re-check it after #2978 merges. A PR that
+  never ran in a train, held as ALREADY, is not one of #2978's held states, and would be a new
+  mechanism to bring back here.

