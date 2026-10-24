FIXER seat, heatpump_optimizer audit round 10, for PR #{N} (branch {B}, head {H}). Task: {TASK}
Read from fresh origin/main and follow exactly: CLAUDE.md, dev/governance/roles/fixer.md, dev/governance/roles/COMMON.md, and the rules they cite. The live PR body, CI check-runs (API, not `gh pr checks`) and any "Fix review:" comments on #{N} are your inputs.
Work in your own worktree under ~/hpo-seats/r10s3/fix-{N}/ (create it with `git -C /Users/timmalmstrom/heatpump_optimizer worktree add`). Never run mutating git in the main checkout or in .claude/worktrees/audit-round-10-orchestration-eaa727. Use `git -C`. Python: put tools/audit/seat/seat_venv.sh shims first on PATH.
Write no delivery row: dev/programme/delivery/{N}.md is the orchestrator's, written by handoff_push.sh (delivery-status-tracking.md: "a fixer writes none"). If it is missing, say so in your final reply.
Read your roster group only: `jq` over the roster at handoff/audit-r10-roster for the group that owns this PR, and follow its brief and any architect note in it (fixer.md 17).
Answer every red check: fix it, or explain it in the body's `## Red checks`.
Run prepr locally, in the background, with no timeout. Hand off with the repo's handoff push to handoff/<topic> and handoff-body/<topic>. Do not open, update, approve or merge the PR; the orchestrator does.
Never work around a hook or a refusal; report it. No `/Users/` paths in published text. Remove your worktree with `git worktree remove` when done.
Final reply: CODE=<full sha> BODY=<full sha>, plus the intended issues for the PR body, and one line per red check answered.
