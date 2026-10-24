Fix reviewer for PR #2652, group R10-FLY-NO-FOOTERS-EMITTERS, head 0a6dff9438c3fccebf20efdd2224d9ced0afa841. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict. This review is on the critical path: it unblocks update_pr, the openers and the stamp.

Verify:
(1) delivery_row.sh commit_row and stamp.py stamp_message() emit no attribution trailer. Each self-test reads the produced message through ref_privacy.attribution, imported and not copied. Mutate each producer by putting the trailer back and show red.
(2) Sweep: git grep -n -i 'co-authored-by\|noreply@anthropic\|Generated with \[Claude\|Claude-Session' over tools/ .github/ .claude/ finds no other producer.
(3) The ## Red checks root-cause section answers the red-check trigger: a cause, a process state, and a countermeasure or a recorded refusal.
(4) The scoped gate MODE line, plus CI read with one bulk check-runs read.
(5) No footers in this PR's commits. A mid-line mention in the subject is prose.

Model for this review: claude-sonnet-5-5.
bus-nonce: ae629214c422ab4022142464b87ae34c
