Fix review: blocked 916d0e08cd69e35dc3a19f8381e29e142c32ea41 scope-rule-widened: step 12's exception is "in full ... that the delta reaches code that review relied on", broader than the owner's custom_components/-only, CI-undetectable-risk exception, and it drops the path-and-risk naming

bus-nonce: a094c5a5e766ffea331ecf2dea1f23fe

## Block

Head measured: 916d0e08cd69e35dc3a19f8381e29e142c32ea41 (ev/HEAD.txt). The check was R10-HOTFIX-DELTA-REVIEW: does the role text encode the owner's 2026-11-09 rule in substance and nothing broader?

What the PR gets right: a later round is `git diff <reviewed-head> <head>` (a main merge: its resolution). Each prior finding must be resolved. The live required checks must be read. The old "any other move is re-reviewed" is gone. The packet, bus.sh and cloud_dispatch carry `--reviewed-head` through to a delta packet.

What it gets wrong. fix-review.md step 12 (ev/step12-at-head.txt) and the packet text at review_packet.py:592 both say: "in full only on a reason the verdict names, that the delta reaches code that review relied on" (the packet: "a full re-review only on a named reason the delta reaches code that review relied on"). Against the owner's rule:
1. Wider trigger. The owner's exception is a delta touching production code (custom_components/) that puts already-reviewed code's functionality at risk in a non-obvious way CI would not detect. The PR's text has no custom_components/ restriction, so an instrument, test, policy or body delta that "reaches code review relied on" justifies a wider review. That is the widening the brief says to block.
2. Wider scope. The owner's exception extends the review to exactly the affected code. The PR's text says "in full".
3. No path and risk. The owner requires the verdict to name the path and the risk. The PR requires only "a reason the verdict names".
4. The CI-undetectable qualifier and the explicit "instrument, test, policy and body deltas never justify a wider review" are absent. The text is open-ended, so "anything the reviewer doubts" fits it.

Duties kept: confirm-previous-findings and live-check-state are present in step 12 and in the packet's delta section.

Required fix: reword step 12, the packet's scope line (review_packet.py:592), cloud_dispatch.py:224 where it paraphrases the scope, and the instrument docs. The exception becomes: only a delta touching custom_components/ in a way that puts already-reviewed code's functionality at risk of being affected in a way CI would not detect. The review then extends to exactly that affected code, and the verdict names the path and the risk. State that instrument, test, policy and body deltas never justify a wider review. Add a mutant or self-test check that the wider-trigger wording is absent.

Side note, not the block: the PR also compresses unrelated wording in steps 6, 8, 9, 12 and 13. Step 9 loses "not the finder's". Please keep the diff to the rule.

## Findings

- Residual: the same too-broad exception wording is also in tools/audit/seat/review_packet.py:592 (the packet's delta section) and cloud_dispatch.py:224 (the reviewer prompt). It is fixed in the PR above. Carry: dismissed: part of this PR's own block, to be fixed on this branch

## Evidence

- merge-tree origin/main with the head: rc 0, no conflict (ev/ci.txt).
- CI at classify: WAIT, pending, "gate red: none". Not a block reason. This block is substantive and independent of CI.
- Packet: the carry_audit and figure_lint (14 resolved, 0 refused) lines were clean at render. No refusals, no advisories.
- I did not run the mutant harness; the block is on the policy text, which the harness does not test. Carry: dismissed: evidence, not a finding
- `merge_train.py owed-reds` rejected `--pr/--head` (usage error), so the owed-reds set was not read. Carry: dismissed: evidence, not a finding
