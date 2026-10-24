Fix reviewer for PR #2645, group R10-FLOW-TOOLKIT-MEASURE, round 2, head 05b9c1d5383cf9ca7e2cd5310914897960244301. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json; if none, review against the PR body and say so. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Round history: round 1 was blocked as mutation-vacuous (probe/rev-2645-da7eafe3, head ad62bf63): the ci_critpath --event/--branch run-list filter dropped survived the self-test. Verify at this head:
(a) The new check kills the c10 mutant (`q = ""` in ci_critpath Api.runs), and the new seat mutant is KILLED. Show the kill output for each.
(b) c9-git-first is pinned by a reads check. c7 is judged equivalent; say whether that is right, with the reasoning.
(c) Forward-carry states the --drop-edge limit: it refuses only when both jobs survive the graph change. Check the text against the code.
(d) The ## Red checks section answers every red at the head, including fast (3.14).

Model for this review: claude-opus-5-5.
bus-nonce: a96f1712ed4f4075e30975a04ce2def5
