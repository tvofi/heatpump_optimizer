Fix review: merge 7a85168ef3ce5112c145e3441567d5bf28c632d0

bus-nonce: a6a5a405a47bb4dc12e9e2a061fbf29e

## Summary

First-round adversarial fix review of PR 3324 (R10-CLOSEOUT-INSTRUMENTS), measured at head 7a85168ef3ce5112c145e3441567d5bf28c632d0 against merge base 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50, from detached worktrees at both ends. All three defects in the group brief are fixed at the source: closeout's roster refusal and step 4 now read one rule (`roster_lib.closeout_exempt`, with replan's post-closure rule moved into roster_lib and no longer duplicated). worktree_gc maps seat branches to `fix/<topic>`, runs the cwd gate on every arm, accepts a colon-separated seats root, and adds class E for plain copies. prune_refs archives a tip under a per-sha tag when the remote already holds the plain tag at another sha. 22 of 24 targeted mutants were killed. The 2 survivors are untested guards in class E: the code is correct, but no fixture covers them. Both are carried below.

## Findings

- Follow-up: surviving mutant M24: deleting class E's `--dry-run` guard (`if [ "$DRY" -eq 0 ]` before `rm -rf "$cp"`, tools/audit/worktree_gc.sh) leaves `worktree_gc.sh --self-test` green at 132/0. The `--dry-run` fixture (`mkcase dry; build dry`) plants no class-E seat, so a dry run that deletes plain copies would pass the suite. The code is correct at this head; only the control is missing. Owed: a class-E seat in the dry fixture, asserting the copies are still on disk after `--dry-run`. Carry: R10-CLOSEOUT-CLEANUP
- Follow-up: surviving mutant M21: deleting class E's `live_under "$seat_real"` keep (the `live-worktree` arm) also leaves the self-test green. No fixture puts a registered worktree under a class-E seat. Since `[ ! -e "$cp/.git" ]` checks only the copy's top level, this guard alone stops `rm -rf` of a copy that has a registered worktree nested inside it. Owed: a fixture seat with a live worktree under a `*mutant*` copy, kept as `live-worktree`. Carry: R10-CLOSEOUT-CLEANUP
- Follow-up: class E's predicate is a name test, not a repository-copy test. Any directory without a top-level `.git` whose name contains `mutant`, `null` or `head` (for example `null-control-ev/` holding RESULT logs) is removed from a merged-topic seat after the orphan age. Class C runs `preserve_evidence` before it deletes; class E does not. The brief asks for "plain repo copies (mutant, null and head trees with no .git)". The fixer's own note says topic-from-dir-name is a reading to confirm, and that reading fails safe (an unmatched topic keeps the copies). The name test does not fail safe. Found by reading the code; I ran no experiment beyond M23 (filter widened to `*`, killed). Before its final `--apply`, the closeout run should confirm the seat layout, or require a repository marker (for example `custom_components/` or `tests/`) in a copy. Carry: R10-CLOSEOUT-CLEANUP
- Follow-up: another instance of the edit/code gate deferral: edit run 42478295273's gate job 128724826666 failed at 12:03:28Z with `FAIL run(s) [42478295004] at this head are still being judged; their gate decides`. That run's suite never re-judged, so `merge_train.py classify` stays `RED ... red: gate` (A5 keeps an older suite's worst gate). This holds even though the run it deferred to went green (gate 128730527584, 12:27Z), and so did the newest suite (gate 128755340122, 14:10Z). The train needs that job re-run before it can merge this head. Carry: R10-RCA-GATE-BUSY-DEFER-2

## Evidence

- RESULT head-reviewed 7a85168ef3ce5112c145e3441567d5bf28c632d0; `git ls-remote` at 14:39Z shows fix/r10-closeout-instruments and refs/pull/3324/head both still at it. The head did not move during the review (ev/HEAD.txt).
- RESULT round 1 (first-round review).
- RESULT roles-current: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches only orchestrator.md and standing-dispatch.md. fix-review.md was read from origin/main.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 7a85168e` exits 0 (tree 84f0825265008430840e6f25148be5ff523b45e4; origin/main 8a4cf2618c53). No conflict and no claim file is involved (ev/merge-tree.txt).
- RESULT self-tests, head vs base (ev/selftest-*): worktree_gc 132 checks, 0 failed (105 at base); closeout 35/0 (28 at base); prune_refs PASS 77 (74 at base); roster_lib 67/0 at both ends; replan `self-test: 0 failed` at both ends. Every figure in the body's `## Figures` re-derives exactly.
- RESULT mutation (ev/mutation-summary.txt, driver ev/mut.py, one worktree per mutant at the head, harness = each instrument's own self-test). The PR has no separate finder's harness; the packet says `Finder's harness: none named`. Its controls are the group brief's fixture arms, which the self-tests implement, so I mutated against those. Killed:
  - M01: blocker exemption dropped.
  - M02: issue exemption dropped.
  - M03: ruled-group host condition dropped.
  - M04: `RULED_STAGES` emptied.
  - M05: transitive post-stamp growth disabled.
  - M06: wired issues dropped.
  - M07: per-sha aliasing off.
  - M08: delete check accepting only the plain tag (killed by an uncaught ApplyRefused, rc=1).
  - M09: alias always.
  - M10: class A cwd gate dropped.
  - M11: class B cwd gate dropped.
  - M12: class B cwd gate restored to the `onremote` condition (the brief's named mutant; it fails "carry 1 (a)").
  - M13: dirty-topic guard dropped.
  - M14: closed topic not mapped.
  - M15: topic mapping off.
  - M16: `closed` state unread.
  - M17: class E merged check off.
  - M18: class E age guard off.
  - M19: class E cwd off.
  - M20: `.git` guard off.
  - M22: first seats root only.
  - M23: name filter `*`.
  
  Survived: M21 and M24 (see Findings).
- RESULT null control: comment-only edits to worktree_gc.sh (N00) and prune_refs.py (N01) leave both self-tests green, so the kills are caused by the mutations.
- RESULT live roster (handoff/audit-r10-roster, ev/live-roster-exempt.txt): `closeout_exempt` exempts R10-CATALOG-PR (post-stamp owner step), the 5 `refused` groups, and issue 2965. `absorbed` is already closed by `CLOSED_STAGES`. Of the brief's disposition stages, `deferred` and `carries-open` deliberately stay blockers, as the comment says. 59 blockers remain on the live roster, as expected before the round ends.
- RESULT class rule: the body names the enumeration (`closeout_exempt` = post-closure groups plus their issues, plus ruled groups with no open host). The group brief's three seats (closeout roster/issue refusal, worktree_gc, prune_refs) are all in the diff. Nothing is class-open.
- RESULT moved rule: `post_closure_groups`, `CLOSE_STAMP_MARK` and `POST_CLOSE_STEP_RE` appear only in roster_lib at the head; replan calls `roster_lib.post_closure_groups`. No stale caller remains (grep).
- RESULT structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`. No `*_budgets.json`, `tests/closures.json`, claim file, VERSION, manifest or RELEASE_NOTES.md is in the three-dot diff.
- RESULT delivery row: dev/programme/delivery/3324.md is in the diff. No other new tracked file is added (9 files, 8 of them modified). `tests/closure.py select --diff <merge-base>` prints its scoped mode (ev/closure-select.txt).
- RESULT CI: `merge_train.py classify 7a85168e --pr 3324` was run 4 times from about 14:35Z to 14:39:38Z, about 60 s apart, and printed `RED 7a85168ef3ce5112c145e3441567d5bf28c632d0 pending: none red: gate` (rc=1) each time (ev/classify-*.txt). That sole red is gate job 128724826666 (edit run 42478295273): `FAIL run(s) [42478295004] at this head are still being judged; their gate decides`. Under the brief, a "still being judged" red gets a wait of up to 60 minutes. It has stood since 12:03Z, about 2.5 h, and the run it deferred to concluded green (gate 128730527584). The newest suite's gate 128755340122 (14:10Z) is also green, and every other check across all 68 runs is success or skipped. I judge the head GREEN in substance. The train's own RED still guards the merge until that job is re-run (see Findings).
- RESULT red-check answer: the only concluded red is the deferral gate above. pr-contract 128730374977 started at 12:26:11Z, after that red concluded (12:03:30Z), and is green, so it is the evidence that the body was checked. The body's `## Red checks` gives the local entities.py account and does not name gate 128724826666. It is a deferral rather than a defect, and it is carried to its RCA group.
- RESULT body accuracy: `## Head` names 7a85168e, the head I measured. It also carries a stray older SHA line, `fe7d2e21dcb5` (commit fe7d2e21d, an earlier tip). The intro's "Merge base is origin/main 73365699a135" is stale: the actual merge base is 4fe7d593, after merge commit 2b72e48fd. Neither changes the reviewed patch.
- RESULT figures I could not re-derive: the body's "Survivors: 0 reported, wall time not measured (step skipped)" refers to a prepr step that did not run. CI `tests / mutation` is green, but under #1120 that can mean nothing was evaluated, and I did not read that lane's log. My own 24 targeted mutants above replace it. The body's per-mutant failure counts ("4 failed", "7 failed") were taken with the fixer's exact edits, which I do not have. My mutants differ: for example, M01 printed 2+ FAIL lines rather than exactly 4.
- RESULT forward-carry: the body states `none`. The three class-E items above go to R10-CLOSEOUT-CLEANUP, which owns the same files and runs the final `--apply` after this group.

## Friction

none
