CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-macos-selftest-lane, at head c987209cc7a891e0e4066d4ad8dc5cf55357c5ae. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c987209cc7a891e0e4066d4ad8dc5cf55357c5ae for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-macos-selftest-lane, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane, even with no code. Then push the code to refs/heads/handoff/r10-hotfix-macos-selftest-lane, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-macos-selftest-lane <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-macos-selftest-lane; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane and refs/heads/handoff-wip/r10-hotfix-macos-selftest-lane-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair brief: PR 3565 (R10-HOTFIX-MACOS-SELFTEST-LANE), mutation-vacuous

resume=handoff/r10-hotfix-macos-selftest-lane@2fb2c7f0eb7b550a1aa278d390e75088164ead2b

The round-3 fix review of head a55158085ed8cd6517113af8b77af07492a6634e blocked, first line verbatim:

verdict: #3565 Fix review: blocked a55158085ed8cd6517113af8b77af07492a6634e mutation-vacuous: red_carried_to_next_cycle, no_per_run_remember survive the self-test at this head

## What to do

Pin both surviving mutants in `tools/audit/seat/beat_jobs_selftest.py` (run as `beat_jobs.py --self-test`), one case each, with the production code otherwise unchanged:

1. `red_carried_to_next_cycle`: a new cycle starts with an empty red list after a completed cycle that had REDs. The case must fail when the red list is carried over into the next cycle.
2. `no_per_run_remember`: a pass killed partway keeps the runs it finished. The case must fail when the per-run remember is dropped.

For each, show the mutant failing the new case and the unmutated code passing it (a null control), as the fixer contract's mutation proof requires.

## Round

The next review of this PR is round 4. Per `dev/governance/roles/fixer.md`, the body owes a `## Re-cut` note per fixer, recording what this repair changed relative to the reviewed head.

Run prepr with PREPR_SKIP_CODE unset as usual. Main carries the weekend-clock fix at c987209c: merge origin/main in if your base predates it.
