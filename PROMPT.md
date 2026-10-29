CLOUD FIXER seat for PR #2962 of tvofi/heatpump_optimizer, at head 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e for the base you were given.
Output: push the code to refs/heads/handoff/r10-fly-packet-red-paths, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-packet-red-paths <body.md>`, which pushes refs/heads/handoff-body/r10-fly-packet-red-paths; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Fixer seat (dev/governance/roles/fixer.md), PR #2962 of tvofi/heatpump_optimizer (R10-FLY-PACKET-RED-PATHS), head 34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e. The review blocked it as mutation-survivor: dropping --existing-file from the call goes unanswered. Read the whole verdict with `git fetch origin verdict/2962 && git show FETCH_HEAD:VERDICT.md`.
Kill that mutant with a test that fails when the flag is dropped, or show that the flag is dead and remove it. Keep the null control: a diff touching nightly.yml is still refused on nightly-status.
Re-run steps 2-8, then hand off on handoff/r10-fly-packet-red-paths with its body ref. This is the top-priority throughput fix: main's red Nightly refuses every new PR until it lands.
No Claude footers.
