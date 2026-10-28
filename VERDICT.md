Fix review: merge 45d083123c6f45482dae00bbef4b82bf6e50bc04

bus-nonce: 22113b0815e03ec312dbc1c5d13c5898

## Round

Delta review of #2753 at the same head 45d083123c6f45482dae00bbef4b82bf6e50bc04, after the delta verdict 1a906f40 that blocked it (body-figure): the added `## Head` line named origin/main 50af6174f. Only the body was patched. As briefed, the scope is the body's `## Head` section only. The claim-file resolution and the fix were not re-reviewed.

## Findings

None. The block in 1a906f40 is repaired, and this pass finds nothing new.

## Evidence

- (1) The live PR body's `## Head` opens: "`45d083123c6f45482dae00bbef4b82bf6e50bc04` merges origin/main `0825aee641c8` into this PR's previous head `bd1a5f31c7a25282420285197412882f4a40a162`". `git log -1 --format=%P 45d083123c6f` gives bd1a5f31c7a25282420285197412882f4a40a162 (first parent) and 0825aee641c8afb1e67be2a6af9d07e9c9dec9fa (second parent, main at #2780). The first 12 hex characters of the second parent are 0825aee641c8, which equals the body's figure. The previous head named is the first parent. Both match (ev/HEAD.txt, ev/body_live.md).
- (2) The live body's `## Head` section contains 36 hex tokens. A script extracted each one and checked it with `git cat-file -e <tok>^{commit}`. 31 resolved on the first pass. 7aa8fb23060e and d5276f9c2820 resolved after `git fetch origin <sha>`: each is an earlier merge of origin/main into fix/r10-thermal-power-option-pr, with second parents 0d1385e2f and 728018c34, as the body says. The other three are not commit ids: 6393281122 is a review id, and 58d790f9 and 51ece26b are carry_audit item ids (ev/head_section_shas.txt). Every short sha expands to the full sha the body pairs it with where it names both (for example 09aecd621, 1339cf925, ab00437c9, e6455b8fe, 0303eae44 and bab39f395).
- (3) Body diff. The body the merge verdict e3448262 (head bd1a5f31) reviewed is evidence/pr_body_at_review.md on verdict/2753. Diffing it against the live body shows exactly the one added `## Head` paragraph and its blank separator line, plus two trailing blank lines at the end of the body (whitespace only, no text). Nothing else changed (ev/body_diff_vs_bd1a5f31_review.txt). The block in 1a906f40 quoted the blocked paragraph's leading sentence (evidence/body_head_line.txt on verdict/2753). It differs from the live one only in `50af6174f` becoming `0825aee641c8`. So the patch since the blocked body is that one figure.
- (4) The PR head from the pulls API is 45d083123c6f45482dae00bbef4b82bf6e50bc04, with updated_at 2026-10-25T14:48:03Z (ev/pr_head_live.txt). The head has not moved.
- `git merge-tree --write-tree origin/main 45d083123c6f` at origin/main bc52ad2af1d0 gives rc=0 and tree e1e8dedce95e: it merges clean (ev/merge_tree.txt).
- CI on 45d083123c6f45482dae00bbef4b82bf6e50bc04 from the check-runs API shows 40 runs: 28 success, 5 skipped, 1 neutral and 0 failed. Six were in progress with no conclusion when read: tests / fast (3.14), tests / coverage, tests / mutation, codeql / Analyze (python) and two prelude runs. Their outcome is not verified here; the merge train reads it at merge time (ev/ci_checkruns.txt).
