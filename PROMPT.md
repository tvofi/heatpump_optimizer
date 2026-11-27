CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-owner-hotfile-counts, at head ef797d794017c98f7fb2d8a168d7de63d435ef3b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-owner-hotfile-counts
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ef797d794017c98f7fb2d8a168d7de63d435ef3b for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-owner-hotfile-counts before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-owner-hotfile-counts, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-owner-hotfile-counts, even with no code. Then push the code to refs/heads/handoff/r11-owner-hotfile-counts, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-owner-hotfile-counts <body.md>`, which pushes refs/heads/handoff-body/r11-owner-hotfile-counts; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-owner-hotfile-counts`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-owner-hotfile-counts and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-owner-hotfile-counts and refs/heads/handoff-wip/r11-owner-hotfile-counts-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# R11-OWNER-HOTFILE-COUNTS: take derived counts out of the hot files

This is an owner order (tvofi, 2026-11-27: "Start working on 1-3 immediately"), so it is exempt from the instrument freeze. Role: dev/governance/roles/fixer.md. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

## The finding

The finding comes from the orchestrator's round-11 study, which is not in the tree. In round 11, about 50% of the merge conflicts between open PRs and main came from derived counts and lists that every PR rewrites in the same lines:
- tests/deployment_shape.py;
- docs/architecture.md;
- dev/audit/rounds/round4/D6/claims.json, claims.md and claims.py.

Re-measure this yourself at your merge base:
- `git log --merges` on origin/main over the last 10 days;
- for each "Merge origin/main" commit on PR branches, the conflicted files (use `git merge-tree --write-tree` replay).

Report the count per file before and after the fix.

## What to do

For each hot file, stop storing a value that is derived from the tree. Instead, either:
- compute it at check time; or
- move it to a generated artifact that a merge driver regenerates, like the existing claimnotes and closures drivers.

Rules:
- Preserve every check's strength. Each check must still fail on its original defect: a demonstrated failing run before and a passing run after (defect-root-cause.md, "A detector must be shown to detect").
- Do not weaken a test or remove a pin.
- Where a file is user-facing documentation (docs/architecture.md), keep the text correct for a reader. Generate the number from a marker, or drop a figure that only restates the tree.
- Structure budgets may only move down. A raise follows CLAUDE.md rule 2.

## Measuring the effect

The null control: replay the last 10 days of PR-vs-main merges against the new tree. Show the conflict count in these files falling, and show that the conflicts in other files are unchanged.

Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1. CI is the authority.

## Handoff

Push the code to handoff/r11-owner-hotfile-counts and the body to handoff-body/r11-owner-hotfile-counts. Seats push refs and never open a PR. If blocked, write BLOCKED.md with the exact refusal and a Question line.
