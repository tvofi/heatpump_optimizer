CLOUD FIXER seat for PR #2758 of tvofi/heatpump_optimizer, at head 7f91e684293abb4ba0276d8b16eb7010448d9fff. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 7f91e684293abb4ba0276d8b16eb7010448d9fff for the base you were given.
Output: push the code to refs/heads/handoff/triage-s6-batch15-r2, then write the PR body and run `bash tools/audit/seat/body_push.sh triage-s6-batch15-r2 <body.md>`, which pushes refs/heads/handoff-body/triage-s6-batch15-r2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):

Push your return refs (code first, then the handoff-body push as the return signal) as soon as prepr passes; a result left only in your session is lost work. Handoff topic and branch names exactly as stated in this brief and in Output above (if they differ for -r2, push BOTH names).
no host or home paths in anything you push
