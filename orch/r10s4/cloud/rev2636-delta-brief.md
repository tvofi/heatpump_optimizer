Fix reviewer for PR #2636, group R10-FLY-NO-FOOTERS, DELTA review, head 4e1c57d5af1326cd61578d3bbf8751f7865a4ffb. Sonnet. Round 1 was merge at 328e222fe8d3b4fe92ad9e37724fcc62bad55da8 (comment 6355280029). The train's carry refused to carry it: the main merge a7cf60cf folded main's edits into files this PR also touches (tools/policy/policy_lint.mjs, field_coverage.mjs, tools/pr/*, .claude/settings.json). Review only the delta: git diff 328e222f 4e1c57d5. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) git diff 328e222f 4e1c57d5 is exactly main's changes since the old base. Every hunk of this PR's own change survives unaltered, and no main hunk is dropped. Check each overlapping file hunk by hunk.
(2) The merged files still do what the PR claims at the new head. Run policy_lint's self-test and fixtures, field_coverage, prepr's attribution fixtures (attribution.md refused, good-claude-ai.md accepted), and ref_privacy and cloud_dispatch self-tests.
(3) CI at 4e1c57d5 is green on the required checks, including policy-docs, with one bulk read.

Model for this review: claude-sonnet-5-5.
bus-nonce: 9329e3e04f3dab9017782b1f82a8fc34
