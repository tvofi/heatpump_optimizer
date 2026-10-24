Fix reviewer for PR #2622, group R10-CI-LAYOUT-P2 (read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json, group "R10-CI-LAYOUT-P2"). Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head 67942203677a3a416fc84e25161a614390c67a99. Use the finder harness the group brief names, never the fixer harness.

Scope note from the orchestrator: P2a is the umbrella engine under tools/ci. Route B: ci_probe.py checks SHAs via `git rev-parse --verify`; agreement.mjs is unchanged from main. Verify that the agreement lane is green against the BASE copy, as the wave-script runs it. nightly-status is the known transition red: a red nightly-status grades main and is not this PR unless its diff reaches what that check reads.

Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.
