CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-hotfix-mutation-driver-cap, at head ac9045c223721608e684c8a2213831aa34c1fa4f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-hotfix-mutation-driver-cap
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ac9045c223721608e684c8a2213831aa34c1fa4f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-hotfix-mutation-driver-cap, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap, even with no code. Then push the code to refs/heads/handoff/r11-hotfix-mutation-driver-cap, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-hotfix-mutation-driver-cap <body.md>`, which pushes refs/heads/handoff-body/r11-hotfix-mutation-driver-cap; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap and refs/heads/handoff-wip/r11-hotfix-mutation-driver-cap-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
Group R11-HOTFIX-MUTATION-DRIVER-CAP. The owner ruled on 11-28 to build it mid-round, as an exception to the tooling freeze.

Problem, measured on #3897 (blocked report on the ref handoff-wip/r11-seam-actuation-writes-mutpin, eea6fbe0, BLOCKED.md):
- tests/mutation_table.py's sampled drive (--scope changed --max 10 --jobs 3) drew 10 sites, and 9 of them are killed only by tests/features.py, at about 1617 s per run.
- With the lazy baseline and the null control that makes 11 features.py runs on 3 workers. The `tests / mutation` job hits its 160-minute limit.
- This happened 5 times on 11-28: #3869 twice, #3897, #3845 and #3883.
- Pinning cannot shrink the job, because sampled_pool draws pinned sites too.

Goal: the mutation job at a head like #3897's fits well inside its timeout, with no loss of kill evidence. Candidate shapes, chosen by measurement:
- a per-driver cost cap in sampled_pool, or cost-weighted sampling, so at most K sites whose only killer is a driver over T seconds are drawn;
- running a pinned killer's block (tools/audit/seat/features_block.py, the pinned site's section) instead of the whole features.py.

Requirements:
- The failing test comes first.
- Mutation proof, and the null control: a head whose sites are cheap must draw exactly as before.
- Measure the job's wall-clock estimate on #3897's head ebd70acc before and after the change.
- Do not weaken the ratchet. An unpinned added site must still refuse.

Hand off on handoff/r11-hotfix-mutation-driver-cap.
