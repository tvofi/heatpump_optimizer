CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-review-dispatch-residue, at head e59e21fee4629623f2f88ea83be76d527b7d0805. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch e59e21fee4629623f2f88ea83be76d527b7d0805 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-review-dispatch-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-review-dispatch-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-review-dispatch-residue, even with no code. Then push the code to refs/heads/handoff/r10-review-dispatch-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-review-dispatch-residue <body.md>`, which pushes refs/heads/handoff-body/r10-review-dispatch-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-review-dispatch-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-review-dispatch-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-review-dispatch-residue and refs/heads/handoff-wip/r10-review-dispatch-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR for fixer r10-review-dispatch-residue (part p3, handoff/r10-review-dispatch-residue-p3 tip d95a3490ef0a1ae41a1bd20095f665a44e40d40a).
Resume from handoff/r10-review-dispatch-residue-p3@d95a3490ef0a1ae41a1bd20095f665a44e40d40a.
The verdict on that head, quoted verbatim (probe/revt-r10-review-dispatch-residue-p3-077d2518 verdict.md):
----- VERDICT BEGIN -----
Fix review: blocked d95a3490ef0a1ae41a1bd20095f665a44e40d40a mutation-vacuous: fixer-guard-off readback-nonce legacy-refusal-swallow

bus-nonce: 077d25185454a0512b76a38f9ec359cb

Round 3 of review (the body's "Round 3 (this repair)"); measured at d95a3490ef0a1ae41a1bd20095f665a44e40d40a, reviewed from detached worktrees at that head.

## Block

Three mutants of production lines this diff adds to `tools/audit/seat/cloud_dispatch.py` survive `cloud_dispatch.py --self-test` (167 checks, 0 failed under each), recorded in `ev/own-mutants.log`:

- `fixer-guard-off`: `if role == "fixer" and (part or len(...) > PART_CARRIES)` with the `role == "fixer" and` conjunct deleted. Not equivalent: with it gone, every non-fixer seat of a group holding over five pending carries (reviewer, design, probe) is refused with the fixer's split, which would refuse the reviewer dispatch of this very group. Demonstrated with a probe check (`ev/probe-cloud_dispatch.py`, `ev/fixer-guard-probe.log`): `not why_any("R10-SPLIT", "probe")` passes on the unmutated file (168 checks, 0 failed) and fails under the mutant (168 checks, 1 failed). The body pins the other half, `--part` for another role refusing, but not that a non-fixer seat of an over-five group dispatches unrefused.
- `readback-nonce`: the read-back ref `{nonce.strip()[:8]}` changed to `{nonce.strip()}`. It survives because the self-test's nonce `abc123` is shorter than eight characters; with a real 32-hex nonce, the mutant tells the seat to `ls-remote` a ref it never pushed, so the read-back always misses.
- `legacy-refusal-swallow`: `raise Refusal(str(e))` in the `RosterNotFound` arm changed to `pass`. No fixture raises `RosterNotFound` on this path, so the mutant's NameError, which replaces the refusal, is never reached.

Each mutant was applied alone and the file restored afterwards (`git status` was clean after each run). To repair this: pin a non-fixer dispatch of an over-five group as unrefused, use a nonce of at least nine characters in the stop-path arm, and add one fixture with a missing roster on the part path.

## Findings

- The head was already merged to main through #3450 (merge a7887485de, `ev/merged-on-main.txt`) before this review at the handoff returned. So this block cannot hold the merge, and the three pins above are owed on main by a later part of this group. Carry: R10-REVIEW-DISPATCH-RESIDUE

## Evidence

- No pull request existed when this was dispatched, so there was no review packet and no CI to wait on (handoff review). `merge_train.py owed-reds` was not consulted because the head had no PR checks to read.
- RESULT harness=r10_flow_dispatch_mutants.py head=d95a3490ef0a1ae41a1bd20095f665a44e40d40a mutants=63 survived=0 rc=0 (`ev/mutants.log`): 58 killed, 5 CRASHED (parent-drop, topic-to-id, head-ignored, roster-repo-ignored, pointer-off), M0 null-ok. These match the body's Figures line for line. This part's 35 named mutants each read verdict=killed.
- RESULT selftest head=d95a3490ef0a1ae41a1bd20095f665a44e40d40a checks=167 failed=0 (`ev/selftest-head.log`).
- RESULT own-mutants (`ev/own-mutants.log`): killed topic-part-gt2, fold-lt, part-index-off, small-lt, selfskip-off, seat-refused-head, ci-wait-head; survived fixer-guard-off, readback-nonce, legacy-refusal-swallow. My first ci-wait-head spelling matched two sites and was not applied, so it was re-aimed at the unique f-string and then killed.
- Body's Unpinned sites: the prefilter `>` vs `>=` is equivalent on output as argued, because five raw carries hold at most five pending. `carry_only` is a pre-existing default. Neither of these is the block.
- Merge: `git merge-tree --write-tree origin/main d95a3490ef0a1ae41a1bd20095f665a44e40d40a` exits 0 (tree 619ee4c132), trivially, since the head is an ancestor of origin/main 8c10361eb1.
- `tests/closure.py select --diff cbd23f1c8b` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (`ev/closure.log`). `tests/structure.py`: STRUCTURE RATCHET PASSED (`ev/structure.log`).
- The diff touches none of VERSION, the manifest, RELEASE_NOTES.md, tests/golden or the claim files, so there is no drift to claim.
- The body's head and merge base (cbd23f1c8b) match the fetched handoff tip. The body records "Forward-carry: none" and "Red checks: none"; with no CI, the latter could not be checked against live runs.
- `dev/governance/roles/` differs between the merge base and origin/main only in design-review.md and others outside fix-review.md's steps, which this review applied as rendered at the current checkout through role_pack.py.
----- VERDICT END -----
Repair the three surviving mutants named above with pins, re-run fixer steps 2-8, push handoff and handoff-body with Code: <tip>.
