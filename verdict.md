Fix review: merge ad9ce7f526b47202bb3ca5e10050b7b48262fc19

bus-nonce: cc29f544b631a348a6615dfc6e953faa
pending-ci: gate

Round 2 (delta re-review after the round-1 block at 7cbfa680134ea1ddb34d202ef1ab11e0efb93807). Measured head ad9ce7f526b47202bb3ca5e10050b7b48262fc19 (merge of code head 2ca01646b7de3856de2e19c2301489db48134436 into 7cbfa680; empty tree diff between the two), merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444. review_carry.py 7cbfa680 ad9ce7f5 prints FRESH-REVIEW; the delta is self-test arms only (tools/audit/seat/gh_calls.py +9/-1, tools/ci/codescan_wait.py +4), no production line moved.

## Findings

- Follow-up: tests/ci_ratchet.py `gather_runs.api` empty-stdout-is-a-failure branch (round-1 M4c) is still unpinned at this head; the behaviour predates this PR and was moved verbatim, and the delta does not touch it. Carry: dismissed: pre-existing unpinned branch moved verbatim, not introduced by this PR (round-1 verdict's disposition, restated in the body's repair section)

## Evidence

- RESULT self-tests at head (ev/mutants.txt): codescan_wait 25 checks 0 failed; gh_calls 206 checks 0 failed. Both body figures re-derived.
- RESULT M2b (seat-gh `git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1` replaced by `true`): gh_calls 206 checks, 2 failed: `second tree: null control: a registered worktree whose script is not tracked` and the in-test tracked-predicate mutant arm. Killed. The pin is not vacuous: t5 is a `git worktree add` of the baked tree (so it passes the registration loop) with gh_comment.py `git rm --cached` (still on disk), so the run reaches the tracked-file predicate; the null control itself turns red under the mutant, not only the self-carried mutant arm. Matches the body's figure.
- RESULT M3b (` and "steps" not in j` dropped from `carried_over`): codescan_wait 25 checks, 1 failed: `BAD 23b null: a completed success job with a lagging or empty steps list ...`. Killed. Arm 23b builds jobs with status completed, conclusion success and `steps` of `[]` or a lagging row, so the conclusion clause is satisfied and only the steps clause separates. Matches the body's figure.
- Carries 1-4 are named `Carry 1`..`Carry 4` in the body's Mutation proof section, and the opening line states "Carries 1-4 of R10-GH-READ-RESIDUE (roster numbering, from 1)".
- PR body head SHA = ad9ce7f526b47202bb3ca5e10050b7b48262fc19, the head measured (step 7); the body names the authored code head 2ca01646 it merges, and the round-1 trailing bare SHA is gone.
- Merge with main: `git merge-tree --write-tree origin/main ad9ce7f5` rc 0 (ev/merge-tree.txt).
- Three-dot diff vs the merge base: the same 6 files as round 1; VERSION, the manifest, RELEASE_NOTES.md, tests/golden/, tests/closures.json and every *budgets.json untouched.
- dev/governance/roles/ moved on main since the merge base (fix-review.md and fixer.md: owed reds narrowed to `merge_train.py owed-reds`); this review followed main's text via role_pack.py.
- Finder's harness: none committed (round-1 finding stands as disclosed; the figures are the fixer's self-test arms). The body's carry-3 instance count is stated as not re-derived; this seat did not re-derive it either.
- Forward-carry: three body items, all `dismissed:` with reasons; carry_audit at the head (ev/review-packet.md) reads them as routed.
- Review packet refusal `red-unanswered: gate` read a gate run (id 130322588976) concluded failure at render; classify reads `gate` pending with red none, and classify decides (packet advisory). CI line below.
- CI: `merge_train.py classify ad9ce7f526b47202bb3ca5e10050b7b48262fc19 --pr 3427` polled 04:36 to 05:07 UTC (ev/classify.log), every run `WAIT ... pending: gate red: none`; no required red at this head, so no `## Red checks` answer is owed by this read. Returned with `pending-ci: gate` for the relay to post once CI is green at this head.
