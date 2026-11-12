CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-prepr-residue, at head 2ced371c1af5581c47dc6163b53c29ee15347a3d. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 2ced371c1af5581c47dc6163b53c29ee15347a3d for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-prepr-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-prepr-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-prepr-residue, even with no code. Then push the code to refs/heads/handoff/r10-prepr-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-prepr-residue <body.md>`, which pushes refs/heads/handoff-body/r10-prepr-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-prepr-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-prepr-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-prepr-residue and refs/heads/handoff-wip/r10-prepr-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND for R10-PREPR-RESIDUE (critical path), pull request 3479, PR head 336a6ca07744d5139914947f58d9f0c4f04bb45a; resume from handoff/r10-prepr-residue at bdc2e986fa5f8f72c7194c685b20b0c0041f66a2. Continue; do not re-cut.

ANSWER verdict/3479@de925f9c0b69a1b4a4083a020b7a894a407c31b8: carry 7 (PREPR-SLOT-LIVELOCK) was dismissed on a null control that cannot fail. Give carry 7 a null control that can fail, or build the fix. Then re-run the finder's harness at both ends, run mutant_run.py --diff, and name every carry as Carry N in the body.

----- REVIEW VERDICT (verbatim) -----
Fix review: blocked b6c080dbcc6cd2294e3ae0913a2c818670749566 harness-vacuous: carry 7 (PREPR-SLOT-LIVELOCK) dismissal rests on a null control that cannot fail

bus-nonce: cb2a5e8b41a5c01c8ec9bdd7842b8c54

Round 1. Head measured: b6c080dbcc6cd2294e3ae0913a2c818670749566 (ev/HEAD.txt). No pull request and no CI exist yet; no review packet.

## Block

Carry 7 is dismissed "not reproduced" from prepr_slot_nested.py, and that harness cannot reproduce or exclude the livelock:

1. The bare control is vacuous. My own bare run (ev/bare.py, pool 4/4 held, no HPO_SLOT_LABEL) printed 61 ordinary self-test rows in 40 s and zero "heavy slot" lines (ev/bare.out): it was not queueing, it was just slow. The labelled run needs 380 s, so `bare_finished=0` at a 40 s bound is the same outcome with or without a slot queue. The labelled and bare runs are indistinguishable by the harness's metrics.
2. `labelled_queued=0` is trivially 0: `queued` is true only when a slot line exists and lacks "joined"; `labelled_real_slot_lines=0`, so no slot line exists to grade. `prepr.sh --self-test` takes the self-test branch (prepr.sh:1876) and never reaches `take_slot`; the nested self-test touches no slot in either arm.
3. The harness injects `HPO_SLOT_LABEL=outer` itself, so it never exercises the thing the carry asks about: where an outer prepr's step 3h loses the label. Step 3h (prepr.sh:4366-4367) calls `take_slot` then `heavy_run ... --self-test`; the label is exported only on the successful-take path (:4184), and the WARN path (:4192) exports none. A real outer prepr holding a slot and running 3h, with the pool full, is untested.
4. The roster carry's own failing test (outer prepr holding a slot runs its nested --self-test with every slot taken and completes; null: bare nested run still takes a slot) was not built. Null control owed: a bare arm that demonstrably differs (a slot line or a queue entry in slot-status), and an arm driven through a real outer prepr step 3h.

Reruns at the head reproduce the body's figures (ev/harness.out: labelled_rc=0, labelled_real_slot_lines=0, labelled_queued=0 in 380 s, bare_finished=0, direct_take_finished=0), so the figures are true but do not support the dismissal.

## Evidence

- Carry 4 (roster index 5, .gitignore): mutation re-run: reverting `/config/` to `config/` fails tests/gitignore_config.py (rc 1, dev/audit/config/x and dev/governance/config/x ignored; ev/gitignore_mutant.txt); head passes rc 0 (ev/gitignore_head.txt). Null control (root config/x still ignored) is in the test and passes. Both nested config dirs are tracked.
- Carry bookkeeping against wave-r10-groups.json at origin/handoff/audit-r10-roster: R10-PREPR-RESIDUE carry list has the .gitignore text at 0-based index 4 (1-based 5, landed) and PREPR-SLOT-LIVELOCK at 0-based 6 (1-based 7, dismissed); the body's numbering is consistent.
- VERSION and RELEASE_NOTES.md untouched (three-dot diff empty).
- Merge: `git merge-tree --write-tree origin/main b6c080dbcc6cd2294e3ae0913a2c818670749566` exit 0, tests/closures.json resolved by the ledger driver (LEDGER-MERGE: resolved); no conflict.
- tests/closures.json additions are the two new files' entries only; not re-derived by me (the closure recorder was not re-run).
- Red checks: none exist for this unopened head; body says none. owed-reds not consulted because no check ran.
- Not re-derived: the body's "PRE-PR rc=0" run (heavy, not re-run).

## Findings

- Follow-up: carry 7's harness needs a discriminating bare arm and a real outer-prepr step 3h arm; until then PREPR-SLOT-LIVELOCK is undismissed and stays open. Carry: R10-PREPR-RESIDUE
