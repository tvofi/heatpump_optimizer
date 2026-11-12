CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-openpr-host-refusal, at head 402b0e76364e5befd6480946add4930cb410928e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 402b0e76364e5befd6480946add4930cb410928e for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-openpr-host-refusal, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal, even with no code. Then push the code to refs/heads/handoff/r10-hotfix-openpr-host-refusal, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-openpr-host-refusal <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-openpr-host-refusal; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal and refs/heads/handoff-wip/r10-hotfix-openpr-host-refusal-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
REPAIR of the handoff r10-hotfix-openpr-host-refusal, blocked a second time at 19c3f4f85cad138f99c63309ac1717ae8d601439 class-open by the fix review (probe/revt-r10-hotfix-openpr-host-refusal-23a4ce0c). Pull request #3515 exists; its head descends the reviewed tip. resume=handoff/r10-hotfix-openpr-host-refusal@19c3f4f85cad138f99c63309ac1717ae8d601439 : merge origin/main if it moved, repair on top; do not re-cut.

Second block of the same class: close the class. No scratch tree shared between overlapping measurements (each measurement owns a private tree no other run can touch, and a cache entry is written only from a complete, undisturbed run); pin the surviving prepr.sh line in pr_step_sig with a row that fails when it is deleted; then run a full mutant pass over the delta and kill or disposition every survivor, not only the one named.

BLOCKED VERDICT, verbatim:

Fix review: blocked 19c3f4f85cad138f99c63309ac1717ae8d601439 class-open: pr_host_refusal measures every topic in one shared scratch tree, so two refusals measured at once call a head's own break the host's, close a true host refusal, and leave a wrong answer cached for main

bus-nonce: 23a4ce0c97187d9a619ca95ac73e344f

Round 2 of this hotfix (round 1 blocked `4b91c2f9f705b76db9e041e1c88ad12bb79147f8`, class-open). Scope: the delta, `tools/audit/seat/open_pr.sh`, `pr_args.sh` and `instruments/open_pr.sh.md`; no production (`custom_components/`) delta is the branch's own, so nothing widened. Reviewed from a detached worktree at the head.

## Block

1. **The predicate's unguarded domain: overlapping measurements.** `pr_step_sig` builds its worktree at `<cache>/tree`, and `op_host_refusal` passes one cache for every topic (`$(dirname -- "$D")/selftest-main`, i.e. `$HPO_STATE_DIR/pr/selftest-main`). The only lock held is the per-branch one, and the body says the run is outside prepr's heavy slot, so two topics refused during the same host fault (the case the hotfix exists for; one measurement is ~6 to 11 minutes by the body's figures) remove and replace each other's tree mid-run. Measured with `ev/race-probe.sh` (the reviewer's probe, a stand-in self-test in the fixture shape of the suite's own; `ev/race-probe.log`, three trials each, all alike):
   - cold cache, a clean head and a head-broken head overlapping: the head-broken head reads **0, the host's**. This is round 1's class (a head's own break called the host's), reached by timing instead of by path.
   - warm cache, overlapping: a true host refusal reads 1, the head's, so its PR closes: #3508's defect.
   - after a cold overlap the cached `<main sha>.sig` holds the corrupted run's rows; alone and unraced, both clean heads then read 1 until main moves or the file is removed.
   - control, sequential: clean heads 0, broken head 1.
   With the real self-test two corrupted runs are less likely to agree row for row than with a stand-in, so the first bullet is shown on the stand-in only; the second and third need only one run to be disturbed. Owed: a scratch tree no other run can touch (one per invocation, or the cache under a lock), main's answer written only from an undisturbed run, and an arm that overlaps two measurements and fails on today's code.
2. **Surviving reviewer mutant, same repair.** Deleting `[ ! -f "$w/tools/audit/prepr.sh" ] || st=tools/audit/prepr.sh` in `pr_step_sig` leaves the suite at 235 checks, 0 failed (`ev/selftest-m8.log`). No tree at this head holds `tools/audit/prepr.sh`, so the branch is unexercised: pin it with an arm or drop it.

## Findings

none beyond the block.

## Evidence

- No review packet and no CI exist before the pull request opens; nothing was waited on, and step 11 has no check run to read. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`. Body `## Red checks`: none.
- Head: body `## Head` names `19c3f4f85cad138f99c63309ac1717ae8d601439`; `refs/heads/handoff/r10-hotfix-openpr-host-refusal` still pointed at it when this verdict was written. Role contract diff merge-base...origin/main under `dev/governance/roles/`: empty.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 (origin/main `43e95474559ca8e2188830f8775c1ddf52df964a`, merge base `005eed2573da9e946fa4838de147401d0ff36cc1`).
- RESULT mutation proof, in-suite: `bash tools/audit/seat/pr_args.sh --self-test` at the head, 235 checks, 0 failed, rc 0 (`ev/selftest-head.log`); every `mut:host*` and `ret:*` arm the body names prints ok.
- RESULT null control: `open_pr.sh` from `4b91c2f9` with `pr_step_sig` and `pr_host_refusal` removed, under the head's arms: 235 checks, 19 failed, among them "a self-test refusal the head's own commit causes still closes the PR, under the host fault" (`ev/selftest-null.log`). The body's figure holds.
- RESULT reviewer mutants (diffs in `ev/mutants-diff.log`, failing rows in `ev/mutant-fails.txt`): m1 compare exit status only, killed, 2 failed, the inputs arm reads 0 of 60; m2 FAIL rows dropped from the signature, killed, 2 failed, 0 of 60; m3 `rm -f "$c"/*.sig` removed, killed, 1 failed; m6 `OP_REFUSED=1` removed, killed, 3 failed; m8 survives (Block 2).
- RESULT round 1's class, by path: `selftest_inputs` evaluated from prepr's text at the head returns 60 entries (`ev/selftest_inputs.txt`); the arm reads 60 of 60 as the head's. The comparison is of two trees, not of names, so no entry is left to a list. Closed for sequential runs; open under overlap (Block 1).
- Seam rule, close sites: `git grep -n -E "gh pr close" -- tools .github .claude` returns the two lines the body states; `pr_host_refusal` has one caller, `op_host_refusal` (`ev/cheap-checks.log`).
- Scoped gate: `closure.py select` prints `MODE: SCOPED -- 1 script(s) run`, `tests/doc_claims.py`, which passes (343 checks); `tests/structure.py` passes. `VERSION`, notes heading, `custom_components/` and goldens: no change in merge-base...head; no claim file touched, so `env_drift.py --all` was not run.
- Log shape read against the tree, not the stub: prepr's `say` prints `  REFUSE   self-test ...` and app_push's `die` prints `app_push: REFUSE: the body did not pass tools/pr/prepr.sh...`, both matching the classifier's patterns.
- Not re-derived: the body's real-tree measurements (664 s for the two signatures, 346 s and 542 passed for prepr's self-test on main) were not re-run; they are the fixer's.
- The finding still has no committed finder's harness; the probe above is the reviewer's, disclosed as such.


Re-run steps 2-8 of dev/governance/roles/fixer.md after any merge. Do not alter VERSION, the manifest or RELEASE_NOTES.md. If it cannot be done in scope, stop with BLOCKED.md.

A BASH_ENV in the cloud environment runs the profile ahead of every nested bash: run tests/entities.py and any closures recording with `env -u BASH_ENV`.
