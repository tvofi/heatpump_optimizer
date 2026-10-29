CLOUD FIXER seat for PR #2872 of tvofi/heatpump_optimizer, at head 8ecde5f26aaf89d95da32c64e6ca736846479ab8. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 8ecde5f26aaf89d95da32c64e6ca736846479ab8 for the base you were given.
Output: push the code to refs/heads/handoff/r10-fix-2872-r2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fix-2872-r2 <body.md>`, which pushes refs/heads/handoff-body/r10-fix-2872-r2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Fixer seat, PR #2872 (tvofi/heatpump_optimizer), under dev/governance/roles/fixer.md, at PR head 8ecde5f26.

The previous cloud fixer stalled on a ref_privacy false positive (HOME=/root matching root-cause.md). That false positive is fixed on main by #2949 (merged at 3042dcd4). The PR is DIRTY against main and its body was being re-cut.

Do: merge origin/main into the PR head (resolve any conflict as a union, reading the merged artifact back per orchestrator.md section 6; a semantic conflict you resolve is described in the body), finish and push the re-cut body so it describes the new head, answer every red check in `## Red checks` (tests / nightly-status and governance / delivery-status grade main: answer each with one line saying this diff touches none of what it reads, unless it does). Run prepr.sh before handoff. Push via the handoff refs (bus.sh / body_push.sh) and stop at handoff; the orchestrator updates the PR.
