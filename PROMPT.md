CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-owner-auto-carry, at head ef797d794017c98f7fb2d8a168d7de63d435ef3b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-owner-auto-carry
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ef797d794017c98f7fb2d8a168d7de63d435ef3b for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-owner-auto-carry before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-owner-auto-carry, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-owner-auto-carry, even with no code. Then push the code to refs/heads/handoff/r11-owner-auto-carry, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-owner-auto-carry <body.md>`, which pushes refs/heads/handoff-body/r11-owner-auto-carry; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-owner-auto-carry`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-owner-auto-carry and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-owner-auto-carry and refs/heads/handoff-wip/r11-owner-auto-carry-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# R11-OWNER-AUTO-CARRY: carry review verdicts automatically when a PR's own diff is unchanged

This is an owner order (tvofi, 2026-11-27: "Start working on 1-3 immediately"), so it is exempt from the instrument freeze. Role: dev/governance/roles/fixer.md. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

## The finding

The finding comes from the round-11 study: verdicts invalidated by main merges cost 50-150 hours of review wait.

fix-review.md already says a verdict carries while the PR's own diff is unchanged, and two instruments already decide a carry:
- tools/audit/seat/review_carry.py, which prints CARRY or FRESH-REVIEW;
- tools/pr/app_approve.sh --carry.

But nothing applies the carry without the orchestrator. When the head moves by a main merge or a CI bot commit (`ci: pin killed mutants`, `ci: re-record closures`, `ci: merge main`), the PR loses its holder. Then:
- `bus.sh confirm` refuses on C8 (a concluded red at the verdict head);
- `merge_train.py add` refuses because the newest posted verdict is not the ref's tip.

Observed today: #3925, with verdict 946e6ceb at 129cc121 and head d50ab75e, a single `ci: pin killed mutants` commit.

## What to do

Make the carry automatic and safe, in the tracked instruments:
- When review_carry prints CARRY for the move from verdict head to new head, the merge path accepts the verdict at the new head. Use one instrument, merge_train.py add or bus.sh confirm, whichever owns it.
- Grade C8 at the new head, not at the verdict head. The rule keeps its strength: a head still red takes no merge verdict. It also stops refusing a red that the carried commit cured.
- FRESH-REVIEW keeps today's behaviour: dispatch a delta reviewer.
- Record each automatic carry in a line the beat or board reads, so a holder is visible.

Read first:
- tools/audit/seat/instruments/review_carry.py.md
- tools/audit/seat/instruments/merge_train.py.md
- tools/audit/seat/instruments/bus.sh.md
- dev/governance/roles/fix-review.md
- orchestrator.md section 7

If the change alters what a policy file says a seat must do, it is policy. Then put it in its own PR for owner approval, and keep the instrument change separate.

## Tests

Self-tests come first. Each needs a fixture where the carry must fire (a mutation-pin commit only) and a null control where it must not:
- a commit touching the PR's own files;
- a merge with a conflict resolution in reviewed code.

Mutation proof on the decision.

Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1. CI is the authority.

## Handoff

Push the code to handoff/r11-owner-auto-carry and the body to handoff-body/r11-owner-auto-carry. Seats never open a PR. If blocked, write BLOCKED.md with the exact refusal and a Question line.
