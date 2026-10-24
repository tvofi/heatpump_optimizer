BODY-ONLY repair, round 2, topic r10-rca-handoff-slip (PR #2545, branch fix/r10-rca-handoff-slip, PR head 6e12aeb5bd976a7520361dd05bf9300cb6c77a04). The code at refs/heads/handoff/r10-rca-handoff-slip (7b05b95f346d4bba88f799a23601def16d305c50) is final: do NOT change or re-push code.
The relay's update of 7b05b95f, with the body currently at refs/heads/handoff-body/r10-rca-handoff-slip, was refused by prepr:
- "PR-BODY: 2 error(s) ... no budget leaf raised over 5a755f53e...a7e877117";
- "RED UNANSWERED (nightly-status)".
Round 1 did not clear these.
Do this:
(1) git fetch origin handoff/r10-rca-handoff-slip handoff-body/r10-rca-handoff-slip; take the body from handoff-body.
(2) Read tools/pr/prepr.sh and the pr-body linter it calls, find exactly what raises "no budget leaf raised" (grep for that string), and reproduce both errors against a local merge of origin/main into 7b05b95f, with PREPR_SKIP_CLOSURES=1.
(3) Fix them with the smallest edit. If the body claims a budget raise the diff does not make, remove that claim. Answer nightly-status in ## Red checks (it grades main, not this PR).
(4) Re-run to 0 errors. carry_audit --roster-ref origin/handoff/audit-r10-roster check --body must show 0 unrouted. Standing rule 19 applies.
Return: bash tools/audit/seat/body_push.sh r10-rca-handoff-slip <body.md>. Do not push code. If body_push.sh insists on a code push, report that instead of pushing.
