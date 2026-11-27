CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-repair-3882b, at head b4ebe3dcf3c9ca70854267f23c1e4c1c81c4b2e6. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-repair-3882b
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch b4ebe3dcf3c9ca70854267f23c1e4c1c81c4b2e6 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-repair-3882b before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-repair-3882b, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-repair-3882b, even with no code. Then push the code to refs/heads/handoff/r11-repair-3882b, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-repair-3882b <body.md>`, which pushes refs/heads/handoff-body/r11-repair-3882b; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-repair-3882b`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-repair-3882b and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-repair-3882b and refs/heads/handoff-wip/r11-repair-3882b-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair: #3882, head 2dcff40e

Role: dev/governance/roles/fixer.md, as a repair of an open PR. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

The bus refuses review at 2dcff40e for two required reds.

1. `governance / instrument-self-tests` went red on steps this diff reaches (INTRODUCED). The steps include "Show a planted owner-only canary reaching no public path of the audit pipeline" and a self-tests-outside-tools/audit/seat step.
   - Read each with tools/audit/seat/failure_logs.sh.
   - These are this PR's findings (defect-root-cause.md): repair them test-first. Never weaken a self-test.
   - If a step proves an owner-only path became publicly reachable, fix the leak. Write the details only to BLOCKED.md on your wip ref, marked owner-only, never into the PR body or a comment.
2. `budget-raise-gate`: CLAUDE.md rule 2 applies.
   - Pay for the raise by moving, sharing or refactoring code. Run tools/audit/archscore before and after.
   - Keep only the raise that no payment removes, with `## Raise justification` and the `Architecture score: dS` line.
   - If no payment exists and the score worsens, write BLOCKED.md with the Question "raise needs the owner".

Note: the previous review flagged REKEY KEPT at duty_ledger.py:49. Check it is resolved.

Answer every red in `## Red checks`. The nightly-ha and nightly-status reds are not required.

Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1. CI is the authority.

Push the code to handoff/r11-repair-3882b and the body to handoff-body/r11-repair-3882b. Seats push refs and never open a PR. If you are blocked, write BLOCKED.md with the exact refusal line and a Question line.
