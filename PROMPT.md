CLOUD FIXER seat for PR #2973 of tvofi/heatpump_optimizer, at head 18c9d3193e4aafd3a7997e125fc6e164ef8343d6. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 18c9d3193e4aafd3a7997e125fc6e164ef8343d6 for the base you were given.
Output: push the code to refs/heads/handoff/r10-marketplace-red, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-marketplace-red <body.md>`, which pushes refs/heads/handoff-body/r10-marketplace-red; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (body-only), PR #2973 (R10-MARKETPLACE), branch fix/r10-marketplace, at head 18c9d3193e4aafd3a7997e125fc6e164ef8343d6; your contract is dev/governance/roles/fixer.md.
review_packet refuses the reviewer dispatch: "concluded red check `tests / nightly-status` is not named in ## Red checks".
Do this:
1. Run tools/audit/seat/failure_logs.sh 2973 and list every red check at the head.
2. Name each one in ## Red checks with its answer (defect-root-cause.md). nightly-status grades main, so answer it as main's red unless this diff touches what it reads.
3. Change no code; the head stays 18c9d319.
4. Publish BODY.md on handoff-body/r10-marketplace with tools/audit/seat/body_push.sh, and confirm tools/audit/seat/review_packet.py passes on it.
