CLOUD FIXER seat for PR #2745 of tvofi/heatpump_optimizer, at head 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e for the base you were given.
Output: push the code to refs/heads/handoff/r10-sav-comfort-r4, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-sav-comfort-r4 <body.md>`, which pushes refs/heads/handoff-body/r10-sav-comfort-r4; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
This is a REPAIR of open pull request #2745 (R10-SAV-COMFORT, fix/r10-sav-comfort), round 4. Fetch origin fix/r10-sav-comfort, cut your worktree from its head 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e. Follow the fixer contract (dev/governance/roles/fixer.md) from step 2 on. Push refs only: handoff/r10-sav-comfort plus handoff-body/r10-sav-comfort (the topic is r10-sav-comfort even though this dispatch ref carries a -r4 suffix).

1. tests / fast (3.14) is red on stress.py's unchanged-plan check: winter/1z/space/pin-off 84263 production calls vs the baseline's 78480 = 1.074x, on work the counts vouch at 1.001x, over the 1.05x cap. A mandate approval does not turn a required check green, so the head must pass it. Find the growth. Is it a real per-scenario extra call the change needs, or a hot-path call that can move out of the loop? Pay it by improving the code; that is the default.
2. If and only if no payment exists (tools/audit/archscore/ run before and after, each attempt recorded), implement a scenario-scoped, justified allowance in stress.py. Write a `## Raise justification` section with every payment tried and the `Architecture score: dS` line. budget-raise-gate applies (mandate 6329234399, scope all).
3. Add a `## Red checks` entry for tests / fast (3.14) that names the failure and answers it.

No host or home paths in anything you push. Do not end the turn while a background job runs.
