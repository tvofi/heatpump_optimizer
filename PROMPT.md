CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-tick-residue, at head 779c94324f7f15a17938526cc6e2c875170fabc0. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 779c94324f7f15a17938526cc6e2c875170fabc0 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-tick-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-tick-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-tick-residue, even with no code. Then push the code to refs/heads/handoff/r10-tick-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-tick-residue <body.md>`, which pushes refs/heads/handoff-body/r10-tick-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-tick-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-tick-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-tick-residue and refs/heads/handoff-wip/r10-tick-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND for R10-TICK-RESIDUE, pull request 3425, head 779c94324f7f15a17938526cc6e2c875170fabc0 (branch fix/r10-tick-residue; handoff/r10-tick-residue 88a5ebe1415d4c420ccca7d649d432692fc28709; the PR head is that handoff plus a main merge). Continue from the PR head; do not re-cut.

SCOPE. Carries 1-21 of the group (Carry 1 .. Carry 21, including the dismissed duplicates 18 and 19 kept bare) are this PR's scope and are built or answered in the existing body; keep every one named as `Carry N` in the body. Carries 22-29 are marked PART 2 ITEM (among them 27 and 28): they are OUT of this part, are not to be built here, and the body says so in one line naming each of Carry 22 .. Carry 29 as part 2.

OWED, and nothing else: for every surviving mutant the blocked verdict lists below (M3 and M4, and any other survivor it names), pin it with a check that fails under that mutant. Quote the failing run (the mutant applied) and the passing run (restored) in the body. Where a survivor is truly equivalent, record a survivor_triage entry for it instead, with the reason. The verdict's suggested checks: one `one_pr` case with `required` set, a `gate` failure and `classify_at` stubbed to `wait`, asserting no RED-UNOWNED line and no `_red[n]` entry, with the `red` stub as null control; a second case raising `mt.Stop` from `classify_at`, asserting the red stands. Then re-run fixer.md steps 2-8 and hand off via body_push.sh. Merge origin/main only if `git merge-tree --write-tree origin/main HEAD` conflicts.
RED-CHECK RULING (owner, 2026-11-09): no merge may be blocked on a non-required red. Only the reds that `merge_train.py owed-reds` lists for this PR and head are owed a `## Red checks` answer.

THE BLOCKED VERDICT, verbatim (ref verdict/3425, VERDICT.md):

Fix review: blocked 779c94324f7f15a17938526cc6e2c875170fabc0 mutation-vacuous: orchestrator_tick one_pr _classify_red call-site deleted; _classify_red except-branch flipped to fail open

bus-nonce: 1201d1a9e984cc9e4ead1050694a1e72

## Block

Round 1 (first review). Carry 9's production change is two parts: the helper `Tick._classify_red` and its use in `Tick.one_pr` (`tools/audit/seat/orchestrator_tick.py:1220-1221`, the lines that clear `self._red[n]` when classify does not read RED). The self-test exercises only the helper, called directly at `:4156`/`:4158` with `mt.Train.classify_at` monkeypatched. Two mutants survive `python3 tools/audit/seat/orchestrator_tick.py --self-test` at this head (305 checks, 0 failed under each; ev/mutants-head.txt):

- M3: delete the two `one_pr` lines `if red and required is not None and not self._classify_red(head, runs, required):` / `self._red[n] = []`. With this the tick reads the gate conclusion alone again, which is the merge-base behaviour the body's Null control describes. No check fails. The behaviour carry 9 claims, "the red-unowned level reads merge_train's classify, not the gate conclusion", is not pinned at the level that prints it.
- M4: flip `_classify_red`'s `except (mt.Stop, OSError, ValueError): return True` to `return False`. That makes it fail open, against its docstring's "fail closed ... an unread classify is RED". No check fails.

The body's named carry-9 mutant (`_classify_red` returning True unconditionally) is killed: 1 failed, "carry 9: a deferral red classify reads WAIT is not red-unowned". But it mutates only the helper's return value, not the wiring. What would fix it: one `one_pr` case with `required` set, a `gate` failure, and `classify_at` stubbed to `wait`. It asserts that no RED-UNOWNED line or `_red[n]` entry results, with the `red` stub as null control. A second case raises `mt.Stop` from `classify_at` and asserts that the red stands.

## Evidence

- Head reviewed: 779c94324f7f15a17938526cc6e2c875170fabc0 (ev/HEAD.txt). The body's figures were taken at 88a5ebe1415d4c420ccca7d649d432692fc28709. `review_carry.py 88a5ebe1 779c9432` prints CARRY: the range is a main merge (91811f03dd) plus the delivery row. The body names 779c9432 as head.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merges with main: `git merge-tree --write-tree origin/main 779c9432` exit 0, tree 81efd52575f6d0ac7d89e72060b6452de44fc10e.
- Self-tests at head (ev/selftests-head.txt, ev/orch-head.txt), re-run by me:
  - beat_jobs: 195 checks, 0 failed, with PYTHONPATH=tests/hastub.
  - owed_unactioned: 59, 0 failed.
  - remerge_main_selftest: 2, 0 failed.
  - orchestrator_tick: 305, 0 failed.
  - The four figures in the body re-derive as 0 failed.
- Mutants killed:
  - carry 13: plan_cap_unread, killed by "plan-beat: the overlay's plan_coordinator_cap is handed to replan as --coordinator-cap". The null-control check "no plan_coordinator_cap leaves replan its own default" passes. replan.py defines `--coordinator-cap` at tools/plan/replan.py:3171 (type=int, default 2), so the pass-through hits a real flag.
  - carry 15: `remerge_main_selftest.py --mutant` gives 1 failed (the detached-worktree check). The attached null control stays ok.
  - carry 10: with the CAP_NOTICE skip disabled, owed_unactioned --self-test exits 1 with `Unreadable: an owed line names no topic ... capped at 8 of 11`. That is killed, though by a crash rather than a named FAIL line.
  - carry 9 helper: `_classify_red`→True gives 1 failed.
- VERSION, the manifest version, RELEASE_NOTES heading and both claim files are absent from the three-dot diff (ev/changed-files.txt). No golden fixture moved, so step 4 has nothing to compare.
- The new file tools/audit/seat/remerge_main_selftest.py is classified: it was added to tests/closures.json.
- Finder's harness: none. This group is roster carries, and each self-test is the fixer's own instrument.
- CI: `merge_train.py classify 779c9432 --pr 3425` printed `WAIT ... pending: gate red: none` on every poll (ev/classify.log). The digest's earlier `gate failure` (id 130265454654) is superseded by a pending run. No concluded red at this head is owed a `## Red checks` answer yet. This verdict's block is independent of CI.
- review_packet refusal `hot-file: #3384 ... shares tools/audit/seat/orchestrator_tick.py` is the train's sequencing concern. It does not bear on this patch.

## Findings

none
