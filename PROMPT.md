CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-arch-docs-wiring, at head 2352b3d28983880c90f6a7620bf55ab98189ede0. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 2352b3d28983880c90f6a7620bf55ab98189ede0 for the base you were given.
Output: push the code to refs/heads/handoff/r10-arch-docs-wiring, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-arch-docs-wiring <body.md>`, which pushes refs/heads/handoff-body/r10-arch-docs-wiring; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (handoff repair), group R10-ARCH-DOCS-WIRING, topic r10-arch-docs-wiring. Current handoff head 2352b3d28983880c90f6a7620bf55ab98189ede0, body at handoff-body/r10-arch-docs-wiring df4eb222. Contract: dev/governance/roles/fixer.md at origin/main.

The orchestrator's open was refused by tools/pr/prepr.sh with: `REFUSE agreement lane: AGREEMENT REFUSED: one concept, readers that disagree or a grammar written twice and unregistered`. Every other step passed: self-test 429/0, ref privacy, temp paths, field coverage.

Do EXACTLY this:
1. Fetch your head, merge origin/main in, and run tools/pr/prepr.sh to read the agreement lane's full output (tools/policy/agreement.mjs).
2. Fix it at its seam. If your checker or resolver parses a grammar another reader already parses (target markers, doc paths, event kinds), reuse that reader or register the grammar once in tools/policy/agreement.mjs, with its fixture. Never weaken the lane.
3. Re-run prepr clean: agreement, unpinned sites and CI predict.
4. Push the new head to handoff/r10-arch-docs-wiring and the updated body via body_push.sh. Never open a PR.
