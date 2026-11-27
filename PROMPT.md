CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-repair-3930-3883, at head d380053b0187f26669983531553b08e69254ac43. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=fixer dimension=- model=claude-opus-5-5 seat=fixer-r11-repair-3930-3883
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch d380053b0187f26669983531553b08e69254ac43 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-repair-3930-3883 before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-repair-3930-3883, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-repair-3930-3883, even with no code. Then push the code to refs/heads/handoff/r11-repair-3930-3883, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-repair-3930-3883 <body.md>`, which pushes refs/heads/handoff-body/r11-repair-3930-3883; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-repair-3930-3883`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-repair-3930-3883 and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-repair-3930-3883 and refs/heads/handoff-wip/r11-repair-3930-3883-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Repair: #3930 (budget raise refused under the mandate) and #3883 (self-test red)

Role: dev/governance/roles/fixer.md, as a repair of open PRs, one at a time. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

## #3930 (R11-SEAM-inputs-freshness), head 2a2ca2c9

Its body's `## Raise justification` re-records four `tests/structure.py` rows:
- `class_excess_loc`
- `max_class_loc`
- `module_excess_loc`
- `seam_cut_total`

It reports `Architecture score: dS +1.2196 WORSENS`. CLAUDE.md rule 2 lets a mandate approve a raise only once no payment that improves the architecture exists, and only with a score that does not read as worse. So the raise is refused as it stands.

Pay for it:
- move, share or refactor code so that each row stays within its budget, or rises less;
- re-run `tools/audit/archscore/` before and after, and get a dS that is not worse;
- keep only the raise that no sound payment removes, with each payment you tried listed in `## Raise justification`;
- never delete working functionality to fit.

`tests / mutation` is red too: follow ci-autofix.md, and run `--pin-killed` if no bot commit comes. Triage survivors by hand.

If no payment exists and the score still worsens, stop. Write BLOCKED.md with the measured numbers and the Question "raise needs the owner". Do not push a raise.

## #3883 (R11-OWNER-STEP-KICK), head 13aff813

`gate` and `governance / instrument-self-tests` are red. Read each red with tools/audit/seat/failure_logs.sh. An instrument-self-tests step that the diff's scope selects is this PR's finding (defect-root-cause.md): repair it. A step outside that scope is unowed: record it.

## Both

- Answer each red in the body's `## Red checks`.
- Prepr is scoped: export PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 in the calling shell. CI is the authority.
- Push the code to handoff/r11-repair-<N> and the body to handoff-body/r11-repair-<N>, N the PR number.
- Seats push refs and never open a PR.
- If you are blocked, write BLOCKED.md with the exact refusal line and a Question line.
