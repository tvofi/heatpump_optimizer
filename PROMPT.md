CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-codeql-dependabot, at head fa4dad4a75eef5d8db3d8f1c35e6ae15dd57583a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch fa4dad4a75eef5d8db3d8f1c35e6ae15dd57583a for the base you were given.
Output: push the code to refs/heads/handoff/r10-codeql-dependabot, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-codeql-dependabot <body.md>`, which pushes refs/heads/handoff-body/r10-codeql-dependabot; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Continue from origin/handoff/r10-codeql-dependabot 5832d8c6 (body b207c883); do not restart from main. Merge origin/main into your worktree first. The opener's prepr refused two checks; repair both:
(1) field coverage: `pinned tools/policy/dependabot_contract.mjs` is unregistered. Register dependabot_contract.mjs in the field_coverage registry: DECLARED must name the arm for its input, or none with a reason.
(2) agreement lane: a grammar is written twice and unregistered. Write the grammar once and register it in the agreement lane rather than duplicating it.
Re-run tools/pr/prepr.sh to a pass at your head. #2678 (dependabot) waits on this PR, so keep it small. Push refs/heads/handoff/r10-codeql-dependabot and run body_push.sh for refs/heads/handoff-body/r10-codeql-dependabot.
