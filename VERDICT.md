Fix review: merge e01e66f0d00bdc2acfcdef725b2d4c53ff0455ac

bus-nonce: a0685f3c6703caded71d04b97f68f62d
Round: 2. Reviewer: rev-2305, from a detached worktree at e01e66f0d00bdc2acfcdef725b2d4c53ff0455ac. The fix-review.md preamble diff is empty. I judged the delta from the round-1 head 3c807ab5b. The authored code is a46805de2: four commits. The two merges from main touch none of this PR's files, and merge-tree against origin/main exits 0.

## Delta judged
- One production change: `_owner_at_head` now passes `justify=lambda: g.justification(self._body(pr))`, the gate's own `decide` reading, and `_body` fails closed when the body cannot be read. That resolves round 1's note that its reading was looser than the gate's.
- Everything else is new self-test arms, plus the in-tree harness dev/audit/harnesses/r10_tick_train_mutants.sh, plus its entry in the closures inert reads.

## My mutants, re-run by my own runner (one detached worktree per mutant), not the fixer's table
- Baseline: merge_train self-test reports 180 checks, 0 failed.
- 20 mutants planted, 18 killed. The killed set: R1, R3, R4, R5, R6, R7, R8, R9, R9b, R10, R11, R12, R13, R14, R15, R16, R17 and J1.
- Every round-1 survivor now fails a named arm:
  - R14 by the batch/ rehearsal arm, which looks nothing up and merges no record PR.
  - R4 by the --skip-bad arm run with --main-moved-tries 3.
  - R15 by the arm that re-reads main green before the first merge on a re-proof.
  - R16 by the arm where the record PR merges before the base is read, so the proof carries its commit.
  - R11 by the arm that carries an approval from the middle of the chain.
  - R1, R6 and R8 each by a named arm.
- R2 survives and is equivalent: `n == tries` raises before the extra range is reached.
- J2 is my own extra mutant: the `_body` read failure is not raised. It survives, but the outcome does not change. The error text carries no justification, so the entry still stops; only the stop message differs. It is not blocking.
- I also drove the in-tree harness for J1 and R2. J1 is killed, R2 survives, and the tree is clean afterwards.
- train.sh is unchanged since round 1, where T1 to T4 were killed.

## Body and record
- `## Unpinned sites` now matches the mutation lane: the lane's scope is empty for tools/, the pinned sites are named, and R2 is marked equivalent.
- The forward-carry routes the record-beat yield to #2302 (R10-TRAIN-HOLD). That group is in dev/programme/rosters/wave-r10-groups.json on origin/main and the issue is open.
- `## Head` says "origin/main is not merged in" in the paragraph about the authored head a46805de2, which is true of that head. Its first paragraph says the PR head merges origin/main 8087e8576. That is readable, not a defect.

## Checks
- All 17 required checks concluded success at e01e66f0d00bdc2acfcdef725b2d4c53ff0455ac.
- No check is red on any commit in 957633266..e01e66f0d.
- There is no budget, claim, golden or VERSION movement in the three-dot diff.

Evidence: the pub2 directory under the rev-2305 scratch dir (RESULTS.txt, mut-*.txt, baseline.txt, check-runs.txt, harness-J1-R2.txt, mutants.py, run_mut2.sh, train-mutants.txt)
