CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-repair-3907, at head 190ffb10c230b6beaf77593b2926d55682e37f47. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-repair-3907
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 190ffb10c230b6beaf77593b2926d55682e37f47 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-repair-3907 before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-repair-3907, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-repair-3907, even with no code. Then push the code to refs/heads/handoff/r11-repair-3907, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-repair-3907 <body.md>`, which pushes refs/heads/handoff-body/r11-repair-3907; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-repair-3907`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-repair-3907 and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-repair-3907 and refs/heads/handoff-wip/r11-repair-3907-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair: #3907 (R11-OUTSIDE-START-APPROACH, critical path), head 46cdd1f9

Role: dev/governance/roles/fixer.md, as a repair of an open PR. Identity: tvofi <70032254+tvofi@users.noreply.github.com>. Your roster group is R11-OUTSIDE-START-APPROACH on handoff/audit-r11-roster: read its brief with jq.

The PR head is red on these required checks: `tests / fast (3.14)`, `tests / coverage-ratchet`, `tests / mutation` and `gate`. Also red: `tests / mutation-autofix` and `governance / instrument-self-tests`.

1. Read each red with tools/audit/seat/failure_logs.sh, and the required set with `merge_train.py owed-reds`.
2. For each required red, establish whether this PR's diff causes it (three-dot against the merge base).
   - The roster records that this group follows #3805 (R11-OUTSIDE-HONEST-DHW-RUNS). If a red comes only from main having moved, or from #3805 not having merged yet, say so with evidence and do not repair it.
3. Repair every red the diff owns, following fixer.md:
   - test first;
   - mutation proof;
   - an `instrument-self-tests` step its scope selects counts too;
   - a mutation-autofix red means run `--pin-killed` yourself (ci-autofix.md).
4. Merge origin/main in if `git merge-tree --write-tree origin/main HEAD` conflicts.
5. Answer each red in the body's `## Red checks`, with the cheaper detector or a recorded finding that none exists.

Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 in the calling shell. CI is the authority. Run `python3 tests/doc_claims.py` and `node tools/policy/brief_lint.mjs` before the handoff.

Push the code to handoff/r11-repair-3907 and the body to handoff-body/r11-repair-3907. Seats push refs and never open a PR. If you are blocked, write BLOCKED.md with the exact refusal line and a Question line.
