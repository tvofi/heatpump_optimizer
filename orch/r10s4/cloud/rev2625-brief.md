Fix reviewer for PR #2625 (tvofi/heatpump_optimizer), group R10-RCA-BODY-LINT (RP lane, policy, class instrument). Read the group entry with `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` (jq the group whose "group" is R10-RCA-BODY-LINT). Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head SHA 10a490f9bc77f1bf148b3774eb6b830eadd3d4c8. Use the finder harness the group brief names, never the fixer harness.

This is an RCA countermeasure PR. Besides the normal review, apply dev/governance/roles/root-cause.md's demonstration requirement for a check-shaped countermeasure: show a null control (the check passes on a clean body/head) and a planted defect (a body that fails the offline lint and a mismatched body_push head) that the new check catches. Verify the countermeasure refuses at prepr (--body-check) and body_push.sh, and that the session-link trailer drop is answered.

A red nightly-status grades main and is not this PR unless its diff reaches what that check reads.
Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
