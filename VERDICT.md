Fix review: blocked 467f58500d12be0b6907839a17be76432555851b introduced-red: tests / fast (3.14) fails tests/doc_claims.py because dev/README.md's machinery figure still cites the postmerge.py state_docs.py call that this diff deletes

bus-nonce: cfdd5337be09e2ec1773c5af44549e41

## Block

- **The red.** `merge_train.py classify 467f58500d12be0b6907839a17be76432555851b --pr 3451` ended `RED 467f58500d12be0b6907839a17be76432555851b pending: none red: gate` at 20:44:25Z (ev/classify.txt). Under the roll-up `gate`, the head's required runs read `tests / fast (3.14)` failure (job 132134194288) and `budget-raise-gate / budget-raise-gate` failure (job 132156990789). Both are in the set `merge_train.py owed-reds` prints (ev/owed_reds.txt). The budget-raise-gate red is the designed refusal that the body answers under `## Raise justification`. It is not the block.
- **The red is this diff's.** Job 132134194288's log ends `1 TEST SCRIPT(S) FAILED`, and the failing script is `>>> FAILED: python3 tests/doc_claims.py`, `2 of 348 checks FAILED`. I re-ran it locally:
  - At the head (worktree detached at 467f58500d): `python3 tests/doc_claims.py` prints `2 of 348 checks FAILED`, rc 1 (ev/doc_claims_head.log):
    - `FAIL every arrow is cited, every citation holds in the tree, and the figure has one entry  [postmerge.py -runs-> state_docs.py: tools/audit/seat/postmerge.py no longer holds '/state_docs.py", "--repo", repo, "--push"']`
    - `FAIL reversing any one arrow of the page's figure is a finding (anchor: the figure has arrows)  [45 of 45]`
  - At origin/main e23124ff6e, the head's merge base: `ALL 348 checks PASSED`, rc 0 (ev/doc_claims_main.log).
- **Cause.** This diff's `tools/audit/seat/postmerge.py` hunk deletes the `("docs", [*PY, f"{seat}/state_docs.py", "--repo", repo, "--push"], True)` step and adds the pin "postmerge runs no state_docs.py (the plan-beat owns the state docs)" (ev/postmerge_own.diff). `dev/README.md`, which this diff also edits (its step 6 "Record"), still draws the arrow `| postmerge.py | runs | state_docs.py | ... /state_docs.py", "--repo", repo, "--push" |` at line 402 (ev/readme_figure_rows.txt). R10-ARCH-DOCS (#2395, 62a7d7a57f) drew that figure, and doc_claims.py checks each of its arrows against the tree. The second FAIL is that check's anchor arm, which goes red with the first.
- **The body's answer does not cover it.** `## Red checks` answers `tests / fast (3.14)` as main's `FAIL combi_type_branch census` in `tests/features.py`. At this head features.py is not the failing script, and main passes doc_claims.py. pr-contract (job 132154826504, success) checked that the check is named, not what the answer says (step 11), so this verdict does not grade the answer. The block is the introduced red itself. It is reachable earlier and cheaper: `python3 tests/doc_claims.py` at the head takes about 12 s of CI wall time (job log, "wall clock"). Whether `prepr.sh`'s scoped run selects it for a postmerge.py change is not measured here.
- **Repair.** In the same diff, drop or redraw the `postmerge.py runs state_docs.py` arrow in `dev/README.md`'s machinery figure, and the line-281 `docs["state_docs.py"]` text if it describes postmerge, so that it matches the plan-beat ownership this diff states. Then re-run `python3 tests/doc_claims.py` to `ALL ... checks PASSED`. A policy-free docs fix inside the PR's own scope, so no new carry is needed.

## Evidence

- **Round.** This is a later round. The dispatch names the reviewed head 07941da7b5cbbf86cef28dd2632eb3bc0c870708. The packet's `## Review scope` reads `full`, because no verdict on verdict/3451 names 07941da7. The last merge verdict on the line is at dcf5e329dceabbf35716800fbacf4e2ff58741bd (verdict/3451 aafa0bd2), an ancestor of 07941da7. `review_carry.py` prints `FRESH-REVIEW` for both 07941da7 and dcf5e329 against the head. This is at least the fifth review round on #3451's line, so `fixer.md`'s re-cut rule applies from the fourth round. That is the orchestrator's call.
- **Own-diff interdiff against the last merge verdict.** I took the `+`/`-` line set of the PR's own three-dot diff at dcf5e329 (base a18e2e9d) and compared it with the one at the head (base e23124ff6e) (ev/own_delta_vs_dcf5e329.txt). It differs only in removed lines of text that main reworded under the PR:
  - `orchestrator.md`'s standing-set bullet and LOG sentence;
  - the deleted `proposal-triage.md` (main's a75d2565 rewording).

  Every added line is identical. The comparison against 07941da7 gives the same result. postmerge.py's own hunk is unchanged since dcf5e329, so the red arises from the interaction with main's figure, re-graded at this head.
- **Merge resolutions (body `## Head`, repair 8), re-checked at the head:**
  - **Main's LOG rule.** Main added "Blocking no production merge: LOG" to the deleted proposal-triage.md. It survives as `dev/audit/README.md:91` "is accepted only when its friction blocks a production merge, else ruled LOG." Body's null control reproduced: with that sentence removed, `policy_lint.mjs` still prints `TOTAL: 0 error(s) across 50 policy file(s)`. No lint arm covers it, as the body says.
  - **Main's "LOG, evidence" verdict line.** Its grammar went with the file. The `## P<n>` ruling format had already been deleted at the reviewed dcf5e329 (card C6), so this merge loses nothing new.
  - **The harness map.** It holds `roster_lib-1`/`-2` and `body_push-5`/`-6` (ev/checks.txt).
    - `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py body_push-5 body_push-6 roster_lib-1 roster_lib-2 S35 S36` prints `RESULT survivors=0`, rc 0 (ev/harness_mutants.log). This matches the body.
  - **The registrations.** `ci_predict.py` registers both `step_replay_self_test` and `roundref_self_test` (lines 1569-1570).
    - `ci_predict.py --self-test` prints 0 failed.
    - `handoff_push.sh --self-test` prints `6 checks, 0 failed`, rc 0.
- **Cheap checks at the head:**
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `--budgets`: rc 0 (ev/budgets.txt).
  - `rules_sync.mjs --check`: `RULES-SYNC ok`.
  - `brief_lint.mjs`: rc 0.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- **Merge with main.** `git merge-tree --write-tree origin/main 467f58500d` exits 0 (ev/merge_tree.txt). origin/main e23124ff6e is the head's merge base.
- **Versions.** The three-dot diff touches no `VERSION`, manifest, `RELEASE_NOTES.md`, claim file or `custom_components/` path. Its only `*_budgets.json` change is `dev/governance/config/policy_budgets.json`, which drops the two keys of the deleted file.
- **Head.** The body's `## Head` names 467f58500d12be0b6907839a17be76432555851b. `refs/pull/3451/head` read 467f58500d before this push (ev/HEAD.txt).
- **CI.** `instrument-self-tests` is a success at the head, so no INTRODUCED instrument red. The other required contexts are a success (ev/classify.txt, and the check-runs read at 20:44Z).
- **Mutation.** The diff writes no `custom_components/` line. The production mutation lane `tests / mutation` is a success. The resolution's load-bearing entries are graded by the harness run above.
