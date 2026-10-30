CLOUD FIXER seat for PR #2978 of tvofi/heatpump_optimizer, at head 882da1e01b3d209cf7f8b6c02427166e7c0c7655. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 882da1e01b3d209cf7f8b6c02427166e7c0c7655 for the base you were given.
Output: push the code to refs/heads/handoff/r10-train-overlap-grade-body2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-train-overlap-grade-body2 <body.md>`, which pushes refs/heads/handoff-body/r10-train-overlap-grade-body2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (body-only), PR #2978 (R10-TRAIN-OVERLAP-GRADE part 2, critical path), at head 882da1e01b3d209cf7f8b6c02427166e7c0c7655; your contract is dev/governance/roles/fixer.md.
The previous body fixer (cse_01MwNjECgDJtwWxQFPtDZbYi) measured at 882da1e0: merge_train self-test 355 checks, 0 failed; MUTANTS 20 run, 0 not as required (M0 passes, M1-M19 killed); prepr.sh rc=0.
It stopped only because body_push.sh needs handoff/r10-train-overlap-grade at the checkout head, and its brief forbade moving that ref. The orchestrator has now fast-forwarded handoff/r10-train-overlap-grade to 882da1e0.
Do this:
1. Check out 882da1e0 on a local branch named handoff/r10-train-overlap-grade.
2. Rebuild the body from handoff-body/r10-train-overlap-grade (ce6db9de) with four sections re-taken at this head: ## Head (names 882da1e0, no byte-identity claim against 72cfd904, says what 5cd2f86eb changed), ## Figures, ## Mutation proof (M1-M19 with their red arms) and ## Red checks (tests / nightly-status is main's red; this diff touches nothing it reads).
3. Re-run the self-test and mutants yourself; do not carry the numbers above.
4. Confirm `bash tools/pr/prepr.sh --body-check BODY.md` passes, then publish with tools/audit/seat/body_push.sh.
5. Push no code.
