CLOUD FIXER seat for PR #2872 of tvofi/heatpump_optimizer, at head 9b24795b242862ac8ea4f5f9f1c798cf087fbde7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9b24795b242862ac8ea4f5f9f1c798cf087fbde7 for the base you were given.
Output: push the code to refs/heads/handoff/r10-cop-partload, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-cop-partload <body.md>`, which pushes refs/heads/handoff-body/r10-cop-partload; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Fixer seat (dev/governance/roles/fixer.md), R10-COP-PARTLOAD, PR #2872 of tvofi/heatpump_optimizer, head 9b24795b242862ac8ea4f5f9f1c798cf087fbde7.
The round-3 re-review (verdict ref verdict/2872 at acfe798c, read it with `git show acfe798c:VERDICT.md`) blocked class-rule-missing on the BODY ONLY; it found no open seam in code. Repair the body; push no code.
1. Add `## Round 3 delta`: 5534a0ac9 (failing first), 9e60fcf77 with its mutation proof, and the bot pin 2b215e01e.
2. Name a writer-enumeration rule for heat_pump_min/max_power and the part-load derate, with the command and its output, and disposition each writer it returns. The verdict's own enumeration is a starting point; re-run it, don't copy it.
3. Rewrite `## Head` so it describes the merges cfe368316 and 9b24795b2.
4. Refresh the `mutation` line under `## Red checks`.
5. Keep the `tests / nightly-status` main-graded line.
Publish the body to the handoff body ref as before, so update_pr.sh can apply it. Put no Claude footers anywhere.
