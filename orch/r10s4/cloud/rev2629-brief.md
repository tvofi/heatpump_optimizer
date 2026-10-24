Fix reviewer for PR #2629 (tvofi/heatpump_optimizer), group R10-RECORD-API-BUDGET (governance record beat; .github/workflows/governance.yml and tools). Head 3fd42d9539ee90e5bf409593ff681f748db76f6e. Read the group entry with `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` (the group whose "group" is R10-RECORD-API-BUDGET). Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness.

Adversarial judgement required (workflow and API-budget logic):
1. Verify the W+3P read-count claim against the old 3W+6P with a MEASURED count (run the counting instrument on both, not prose).
2. Mutate M0, M1 and M2 as the group brief defines them; each mutant must be caught by the check.
3. Check that the concurrency group cannot cancel a record run mid-write.
4. The body's ## Red checks answers nightly-status; that red is main's false ABSENT fixed by #2627. Do not treat it as a defect of this PR unless the diff reaches what that check reads.

Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
