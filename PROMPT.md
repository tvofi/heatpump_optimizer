CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-entities-redaction-flake, at head 50373173d486faf394b24637c177ab38b691b394. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 50373173d486faf394b24637c177ab38b691b394 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-entities-redaction-flake, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake, even with no code. Then push the code to refs/heads/handoff/r10-hotfix-entities-redaction-flake, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-entities-redaction-flake <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-entities-redaction-flake; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake and refs/heads/handoff-wip/r10-hotfix-entities-redaction-flake-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Hotfix: entities.py redaction check matches clock readings by chance

Topic r10-hotfix-entities-redaction-flake. Main is red.

## Defect

`tests / fast (3.14)` went red on main at 50373173d486 with
`FAIL the location is redacted whole, from data and from options, not coarsened ['**REDACTED**']`:
1 of 2711 entity checks. Both redaction reads were `**REDACTED**`, so the failing arm is the
rounded-coordinate search `str(round(_c, 1)) in _blob` at tests/entities.py lines 25817-25822
(origin/main, verified). It looks for "59.3", "18.1", "59.4", "18.2" anywhere in the whole
diagnostics output. That output carries `"exported_at": now.isoformat()` (diagnostics.py line 401)
and a `dt_util.utcnow().timestamp()` value (line 378), so a clock reading such as `...:18.1xxxxx`
matches by chance.

Not proven: which timestamp matched. Not reproduced locally. Do not claim the mechanism as
measured; demonstrate it as below.

## Fix shape

- The check searches for the rounded coordinates in the payload with the clock-bearing fields
  removed (or with the clock pinned), never in the raw blob.
- On failure it prints which string matched and where.
- Production code does not change unless you prove the coordinates really leak.
- Failing test first is replaced by a deterministic demonstration: pin the clock to a value
  containing one of the rounded strings; show the old check fails and the new one passes. Null
  control: a genuinely coarsened coordinate in the payload still fails the new check.
- Mutation proof for the changed check.
- Body `## Red checks` names `tests / fast (3.14)` at main 50373173 and answers the root-cause
  question: whether a cheaper detector existed, or none.

## Handoff mechanics

Push a wip ref first (handoff-wip/r10-hotfix-entities-redaction-flake), then the handoff
(handoff/r10-hotfix-entities-redaction-flake), update the body with body_push.sh. Hotfix-scoped
prepr (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`). Open no pull request; the orchestrator does.
