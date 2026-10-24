Fix reviewer for PR #2632, group R10-LOOP-CPU, round 3, head 577ec62dbb35f2353902b5bbe5adb37b69805af2. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json; if none, review against the PR body and say so. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Round history and note for this round: round 2 was merge, but CI went red on coverage. That was 740 leaked worker children at tests/features.py's exit, from un-picklable closure jobs, so coverage recorded no data for the script. Round 3 serialises each job whole before the pipe and reaps a child on a stream fault.

Verify, and cite the evidence for each item:
(a) The new tests fail at a4ccf176 and pass at the head 577ec62d. Mutate the pre-pipe serialise and the fault reap back, and show each mutation turns red.
(b) tests/features.py ends with 0 leaked children, and the coverage lane records data for it. Read CI at the head for coverage, mutation and fast.
(c) The mutation red at 5b068048 (job 120230312005, the bot's main merge before round 3) is answered in a ## Red checks section of the PR body, or is gone at this head.
(d) `Closes #2237` is intended: #2237 is the R10-P10 CPU-on-loop issue.

Model for this review: claude-opus-5-5.
bus-nonce: 0d5b2b364ff8c8e510778510c8fdba8e
