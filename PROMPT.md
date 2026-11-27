CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-repair-red-batch, at head d380053b0187f26669983531553b08e69254ac43. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-repair-red-batch
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch d380053b0187f26669983531553b08e69254ac43 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-repair-red-batch before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-repair-red-batch, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-repair-red-batch, even with no code. Then push the code to refs/heads/handoff/r11-repair-red-batch, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-repair-red-batch <body.md>`, which pushes refs/heads/handoff-body/r11-repair-red-batch; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-repair-red-batch`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-repair-red-batch and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-repair-red-batch and refs/heads/handoff-wip/r11-repair-red-batch-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair: required reds on #3913, #3897 and #3869

Role: dev/governance/roles/fixer.md, as a repair of open PRs, one at a time. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

Heads and the reds to handle:
- #3913 (R11-LATE-P1-OPTIONS) at 95b952b9: `gate` and `tests / mutation`.
- #3897 (R11-SEAM-actuation-writes) at 98b4926e: `gate` and `tests / mutation`.
- #3869 (R11-OWNER-MODE-LEGS) at 441ed2ab: `gate` only. `tests / nightly-status` is exempt.

For each PR:
1. Read its reds with tools/audit/seat/failure_logs.sh and the required set with `merge_train.py owed-reds`.
2. A `tests / mutation` red:
   - follow ci-autofix.md;
   - if `tests / mutation-autofix` is red or no bot commit came, run `--pin-killed` yourself;
   - triage each survivor by hand under fixer.md: kill it with a test, or record it as equivalent with a reason;
   - never automate survivor triage.
3. A `gate` red with no other required red: read the gate log.
   - If it is a deferral (its log names another run still being judged), record that with the run id and repair nothing.
4. Answer each red in the body's `## Red checks`.

Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 in the calling shell. CI is the authority.

Push each repair to handoff/r11-repair-<N> and its body to handoff-body/r11-repair-<N>, N the PR number. Seats push refs and never open a PR. A PR that needs no repair gets one line in REPORT.md on handoff-wip/r11-repair-red-batch. If you are blocked, write BLOCKED.md with the exact refusal line and a Question line.
