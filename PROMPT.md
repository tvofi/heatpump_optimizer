CLOUD FIXER seat for PR #2872 of tvofi/heatpump_optimizer, at head 27bb23875cf0248028d243b4643523e6f4c7f04e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 27bb23875cf0248028d243b4643523e6f4c7f04e for the base you were given.
Output: push the code to refs/heads/handoff/r10-cop-partload-red, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-cop-partload-red <body.md>`, which pushes refs/heads/handoff-body/r10-cop-partload-red; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (body-only), PR #2872 (R10-COP-PARTLOAD); your contract is dev/governance/roles/fixer.md.
Your merge handoff, handoff/r10-cop-partload at 7d9ac8b81d4caf13da90796c3d5d699750b7e721, is good, but update_pr.sh refused its body (scratch upd/b2872.md, which is handoff-body/r10-2872-claims). The red checks are unanswered in ## Red checks: budget-raise-gate / budget-raise-gate, governance / delivery-status, tests / fast (3.14), tests / mutation, tests / mutation-autofix, tests / nightly-status and tests / typing.
Do this:
1. Run tools/audit/seat/failure_logs.sh 2872 for each red check.
2. Answer each in ## Red checks per defect-root-cause.md: the cheaper detector and its standing cost, or that none exists. nightly-status and delivery-status grade main unless this diff touches what they read.
3. Answer budget-raise-gate from ## Raise justification as CLAUDE.md rule 2 requires.
4. Make ## Head describe 7d9ac8b8.
5. Push BODY.md to handoff-body/r10-cop-partload (that topic, not r10-2872-claims) with tools/audit/seat/body_push.sh, and confirm tools/pr/prepr.sh passes on the body at that head.
6. Change no code.
