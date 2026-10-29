CLOUD FIXER seat for PR #2925 of tvofi/heatpump_optimizer, at head 2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c for the base you were given.
Output: push the code to refs/heads/handoff/r10-fix-2925-r6, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fix-2925-r6 <body.md>`, which pushes refs/heads/handoff-body/r10-fix-2925-r6; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Fixer seat, PR #2925 (tvofi/heatpump_optimizer), round 6, under dev/governance/roles/fixer.md.

The r5 fix review at head 2c62c682d180b6270a42d8c3a9a010fb6dd1ac4c returned blocked (verdict/2925):
class-open: budget-raise-gate.yml's budget-raise-gate job restores and runs the base's budget_raise_gate.py, outside restore_jobs and undispositioned.

This is past the three-round rule: re-cut minimal. Either bring that job into restore_jobs (or disposition it explicitly in the same mechanism the other restore jobs use), with a failing test first and mutation proof, or narrow the PR's claim so that job is out of its scope and say so in the body. Do not widen the PR otherwise.

Push via tools/pr/app_push.sh (hpo-author), update the body's evidence at the new head, and stop at handoff.
