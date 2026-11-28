CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-outside-ci-3885-l3-timing, at head ac9045c223721608e684c8a2213831aa34c1fa4f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-outside-ci-3885-l3-timing
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ac9045c223721608e684c8a2213831aa34c1fa4f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-outside-ci-3885-l3-timing, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing, even with no code. Then push the code to refs/heads/handoff/r11-outside-ci-3885-l3-timing, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-outside-ci-3885-l3-timing <body.md>`, which pushes refs/heads/handoff-body/r11-outside-ci-3885-l3-timing; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing and refs/heads/handoff-wip/r11-outside-ci-3885-l3-timing-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Fixer: #3885 L3 rest — prelude reports API time and sleeping time separately

Outside group R11-OUTSIDE-CI-3885, critical path; land it as soon as possible. Read CLAUDE.md, dev/governance/roles/fixer.md and tools/audit/seat/instruments/*.md first.

Issue #3885 (outside contributor) asks the prelude (tools/ci/prelude.py, .github/workflows/ci.yml) to report API work and sleeping/waiting time separately, including which source runs delayed it. L3 W1 (defer at once) and W2 (completion re-run) are merged (#3935). What is left is the measurement.

Build:
- Per-step accounting in prelude: wall time in GitHub API calls vs time spent sleeping or deferring, plus the run ids that caused each wait.
- Emit it as a machine-readable summary line in the job log and in GITHUB_STEP_SUMMARY.

Keep everything as it is: same-head binding, rerun-attempt handling, fail-closed API and rate-limit behaviour, and the cycle-avoidance rules.

Process:
- Write the failing test first, with a mutation proof and a null control for every quantified claim.
- Make a structure-budget payment, never a raise.
- Push with tools/pr/app_push.sh or open_pr.sh only.
- The PR body says it is part of #3885 and closes nothing unless it is the last part.
