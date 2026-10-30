CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-flow-design-stages-p2, at head 9256af6a009806c2ae38b6f6b8d2ba01f5af3b2a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9256af6a009806c2ae38b6f6b8d2ba01f5af3b2a for the base you were given.
Output: push the code to refs/heads/handoff/r10-flow-design-stages-p2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-flow-design-stages-p2 <body.md>`, which pushes refs/heads/handoff-body/r10-flow-design-stages-p2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (handoff repair: body only), group R10-FLOW-DESIGN-STAGES part 2, topic r10-flow-design-stages-p2. The code handoff is handoff/r10-flow-design-stages-p2 at 9256af6a009806c2ae38b6f6b8d2ba01f5af3b2a, but origin has no handoff-body/r10-flow-design-stages-p2, so the orchestrator cannot open the PR (open_pr.sh refuses: "origin has no handoff-body/... (the body ref)"). Contract: dev/governance/roles/fixer.md at origin/main.

Do this:
1. Fetch that head, merge origin/main in if it moved, and run tools/pr/prepr.sh. Repair any refusal it names.
2. Write the PR body to .github/PULL_REQUEST_TEMPLATE.md's headings for what this part delivers. The group's residual brief is the roster's R10-FLOW-DESIGN-STAGES; this part is items A and B, the payload stub and the carries in the dispatch. Include each control's measured result, the mutants, `## Red checks`, and `Carry:` markers.
3. Publish it with bash tools/audit/seat/body_push.sh r10-flow-design-stages-p2 <file>. If the code head moved, push it to handoff/r10-flow-design-stages-p2 first.
Never open a PR.
