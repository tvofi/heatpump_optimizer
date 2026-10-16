Fix review: merge 8fef39fc30e2e7700c6eac7303fa7c36d68c4673

bus-nonce: 2df24c8b56858a17e40131e8e62ec585

Round 2. Reviewer seat rev-2323 (fix-review.md). Round 1 returned `blocked <8fef39fc30e2> harness: class-open #2220 arm B`. The brief's job now is narrow and body-only: confirm the live body clears that block, and that nothing else moved. It does, and nothing else moved.

## The round-1 block, and its clearance

Round 1 blocked because the body wrote `Closes #2220` while naming only arm A, and #2220's own Enumerator names two arms (arm A, `D14/I3/hook_shape_seams.py`, this PR's; arm B, `D13/s1/yield.mjs`).

The live body now writes **`Part of #2220.`** and carries no closing keyword anywhere. evidence/body-keywords.txt is a case-insensitive `clos|fixe|resolv|part of` over the whole live body; its only matches are `Part of #2220.`, the word `Fixed` in the null-control prose, and the arm-B line. No `Closes`, no `Fixes`, no `Resolves`.

Arm B is dispositioned in the body:
- `- arm B of #2220 (yield.mjs, D13-s1-01) was addressed by #2294 (merged); this PR is arm A`

I re-derived that disposition rather than taking it from the body:
- #2294 is `MERGED`, mergedAt 2026-10-15T21:48:12Z (evidence/pr2294-state.json).
- #2294's own body says so at line 64: "#2220's I3 enumerator arm B is `yield.mjs`, replaced as above. Its arm A (`hook_shape_seams.py`) belongs to R10-PRE-EDIT-HOOK", and at line 15 writes `Part of #2220` (evidence/pr2294-armB.txt).

So both arms are accounted for, the roster's `fixes: []` for R10-PRE-EDIT-HOOK agrees with a body that closes nothing, and the orchestrator closes #2220 by hand after the merge. That is the reviewer's option (b), the one the orchestrator chose. The hand-close is the orchestrator's, not a defect in this work.

## Nothing else moved (the body-only claim is true)

- **Head re-read before posting: `8fef39fc30e2e7700c6eac7303fa7c36d68c4673`** (step 12), and it is still the remote tip of `fix/r10-pre-edit-hook` (evidence/remote-ref.txt). The code head under it is `e8adc1b560222cf605a0f664d61c2c0297cdbfe2` (evidence/head-commits.txt) — the same pair round 1 measured.
- **The diff is the same two files as round 1**: `.claude/hooks/pre-edit.sh` (+20/-2) and `dev/programme/delivery/2323.md` (+1), nothing else (evidence/diff-stat.txt). A head SHA commits the whole tree, so an unchanged SHA is an unchanged tree.
- **Step 13, re-taken now** (main may have moved since round 1): `git merge-tree --write-tree origin/main 8fef39fc30e2e7700c6eac7303fa7c36d68c4673` exits 0 with no conflicting path (evidence/merge-tree.txt).
- **Step 11**: every check-run at the head has concluded; none is red (evidence/check-runs.txt). `pr-contract` re-ran at 13:53:40Z, after the re-body, and concluded `success` at 13:54:01Z — so the trigger has no case here, and the body was in fact checked against the contract.
- **Step 7**: the head SHA the body names is the head I measured.

## RESULT lines — the round-1 measurements stand

I did not re-run the heavy harnesses, because the tree is byte-identical at both ends and a re-run would measure the same bytes. Round 1's lines, carried verbatim (evidence/round1-verdict.txt):

Base 7215e39df7a1:
- RESULT d11s1 escaped_heading_writes=1 control_refused=1; --perturb escaped=0
- RESULT d11s3 refused_heading_payloads=2 multiedit_refused=0 null_refused=0; --perturb 3/1/0
- RESULT sweep seams=16 escapes=1 (RELEASE_NOTES.md x MultiEdit); --clean 0; --perturb 2
- RESULT self-test 16 passed, 0 failed

Head 8fef39fc30e2:
- RESULT d11s1 escaped_heading_writes=0 control_refused=1
- RESULT d11s3 refused_heading_payloads=3 multiedit_refused=1 null_refused=0
- RESULT sweep seams=16 escapes=0
- RESULT self-test 21 passed, 0 failed

Likewise round 1's mutation proof (four mutants red as claimed; two survived, neither blocking, with M4's mixed-list case recorded as the one that would pin the filter), its attacks, its null controls and its escapes are unchanged by a body edit. The body's figures are unchanged and still re-derive to round 1's numbers (self-test 21/0, escapes 1 to 0, sweep 16 seams); no figure moved, so step 14 has nothing to judge.

## Standing gates

- **Owner gate:** `.claude/hooks/` is code-owned, so tvofi's approving review is still required; this verdict is not it.
- **Forward-carry:** none owed beyond the group carry, which round 1 confirmed met; the body's `## Forward-carry` still reads none.

Evidence: HEAD.txt, body-round2.txt, body-keywords.txt, check-runs.txt, diff-stat.txt, head-commits.txt, merge-tree.txt, pr-state.json, pr2294-state.json, pr2294-armB.txt, remote-ref.txt, round1-verdict.txt. Paths are scrubbed.
