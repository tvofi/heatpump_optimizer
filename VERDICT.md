Fix review: merge c5a968de35f3e71e2e5b06e2174b7b54e6a7c306

bus-nonce: 607c141d921b6a6a806d4bf3605cc163

Round: second review of this group (round 2), after fixer round fix2591z on the blocked verdict at 400e15d277c7fb7c9e27aa1c203de282e0c51c4f. Group R10-FLY-BUDGET-LEAF. Reviewed from a detached worktree at c5a968de35f3e71e2e5b06e2174b7b54e6a7c306. At write time the PR head is still c5a968de35f3e71e2e5b06e2174b7b54e6a7c306 and origin/main is 3976515a08228598ea3863f4f36dc4c7c4846865.

## Prior blocks

- Block at 400e15d27 (mutant-survives: body_refusal's red-before-ERROR precedence was unpinned) is cleared. Commit cfdd9c26c adds two both-grounds rows, one at `reds_line` (7c) and one at `body_line` (7). Under the reviewer's mutant 2 (ERT) both rows go red at this head: 310 passed, 7 failed, against 312/5 unmutated (ev/selftest-m2.txt, ev/mutant-summary.txt). At 53ae6a8ca, the previous head plus a main merge, where prepr.sh is byte-identical to 400e15d27, the same swap (ETR measured, ev/selftest-p6.txt) still gives 308/5 and survives. That makes the new rows the killing ones.
- The prior second finding (the count suffix was unpinned, mutant 3) is cleared. With the suffix dropped, the result is 310/7, and both new rows go red (ev/selftest-m3.txt). Both rows assert `(2 error line(s) in all)`.

## Findings

none

## Evidence

- Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (ev/contract-currency.txt). The merge base equals origin/main 3976515a0.
- Diff, three-dot against the merge base: `tools/pr/prepr.sh` and `dev/programme/delivery/2591.md` only (ev/diff-names.txt). VERSION, the manifest version, the RELEASE_NOTES heading, claim files, goldens, budgets, closures and the ledger are untouched, so step 4 has nothing to compare and step 14 has nothing to earn. Between cfdd9c26c and the head, tools/pr/ does not change.
- RESULT selftest head (`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh --self-test`): 312 passed, 5 failed (ev/selftest-head.txt). The 5 failures are the four `6b` rows and `and makes no serial --single call beside it`, all of them "no interpreter that parses the tree was found (tried the seat venv ...)". They are the same 5 in every run here, so they are environmental (this container has no seat venv). CI's `instrument-self-tests` is green at this head.
- RESULT mutation proof, every non-identity order of body_refusal's three alternatives (R red sentence, E first ERROR, T tail) at this head (ev/mutant-*.diff, ev/mutant-summary.txt). The killing rows are those that pass unmutated and fail under the mutant:
  - ERT (m2): 310/7, killed by both new rows.
  - ETR (m6): 310/7, killed by both new rows.
  - RTE (m5): 310/7, killed by `and the refusal prints the error, not only its count` and `... ahead of the budget verdict`.
  - TRE (m7): 305/12, 7 rows.
  - TER (m4): 305/12, 7 rows. These include both new rows and the three red-gate rows.
  - SUFFIX dropped (m3): 310/7, killed by both new rows.
  - BASE `R || T` (the fix reverted, pb): 310/7, killed by the two Friction rows.
  Every swap of every pair of refusal conditions turns a row red.
- RESULT before the new rows at 53ae6a8ca: unmutated 308/5 (p0). ETR 308/5 survives (p6). RTE 306/7 (p5). TRE 303/10 (p7). Together with the head runs this re-derives every cell of the body's mutation table that I ran. The body's ERT and SUFFIX cells at 53ae6a8ca (308/5, survives) match the prior review's measurement at 400e15d27, whose prepr.sh is byte-identical. TER at 53ae6a8ca was not re-run by me; the body pairs it with TRE as 303/10.
- Class (step 6): the body names an enumeration rule. Every unordered pair of body_refusal's alternatives gets a body carrying both and asserting which wins, plus a sweep of all 3! - 1 = 5 order permutations. I checked each pair:
  - R/E: the new rows.
  - R/T: the red-gate rows `naming the check`, `naming budget-raise-gate` and `naming mutation`.
  - E/T: the two Friction rows.
  All five permutations are killed, as listed above. Sibling hunt (ev/class-enum.txt): every `body_check` caller outside the self-test is `body_line` (prepr.sh:728) or `reds_line` (prepr.sh:1036), and both go through `body_refusal`. Step 7's `step "pr-body" ... tail -1` (prepr.sh:2934) reads body_line's own one-line output, so it is that seam's consumer and not a sibling. The other `tail -1` reporters report other checks (predictor, copy-claimed, throwaway git). app_push.sh prints policy_lint's whole output. I found no open seam.
- Finder's harness at both ends. The roster brief names prepr's printed refusal line on a prose-Friction body, and no committed harness exists for it, so as in round 1 I replayed the merge base's expression (`grep -m1 'does not name it' || tail -1`) and the head's `body_refusal` over `policy_lint.mjs --pr-body` output (ev/both-ends.txt, ev/lint-*.txt). This instrument is mine, and I disclose it as mine.
  - bad-friction.md: base prints `PR-BODY: 1 error(s) in ...`; head prints the `## Friction` line does not parse error, `(1 error line(s) in all)`.
  - unnamed-red.md + prose Friction (`--red 'fast (3.14)'`): both print the red's sentence; head adds `(2 error line(s) in all)`.
  - unnamed-red.md: both print the red's sentence; head adds `(1 ...)`.
  - good.md, the null (rc 0): `PR-BODY: 0 error(s)`, with head adding `(0 ...)`.
  - red-answered.md with the red passed, a second null (rc 0): the same.
  This re-derives the body's both-ends table row for row.
- Null control: the single-error rows (unnamed-red alone, and the answered-red prose-Friction body) pass under ERT and ETR, so the new rows are not vacuous and the nulls hold. Re-derived.
- Body figures:
  - Self-test counts and killing rows: re-derived, as above.
  - Permutation count 5, all killed: re-derived.
  - `grep -n 'body_refusal'` giving one definition and two call sites: re-derived (prepr.sh:703, 730, 1042).
  - Three refusals #2545, #2558, #2582: not re-derivable. The body says so itself; those bodies have been rewritten, and the roster brief records them.
  - `MODE: SCOPED -- 0 script(s) run, 33 scoped out` and the run_always lines: not re-derived by me. CI's `closures`, `closure-scope` and `scope` are green at this head.
- Body `## Head` names c5a968de35f3e71e2e5b06e2174b7b54e6a7c306, the head I measured. Its commits above cfdd9c26c are main merges only (aef2c3e2e, c5a968de3), with no tools/pr change.
- Merge-tree: `git merge-tree --write-tree origin/main c5a968de35f3e71e2e5b06e2174b7b54e6a7c306` exits 0 with tree b7cffb621203a94b858f0d0856ee7d9b797dfecd and no MERGE-CLAIM line (ev/merge-tree.txt). It is clean, and the head already contains origin/main; no absorb is asked.
- carry_audit over the PR body: `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body ev/pr-body.md` gives `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (ev/carry-audit-body.txt). The body's Forward-carry is `none`, and nothing here changes a later stage (step 10). This verdict carries nothing. The group R10-FLY-BUDGET-LEAF is live on the roster (resume.stage `not-started`).
- mutation lane at this head (job 119602338064 log, ev/mutation-lane.txt): `MUTATION TABLE PASSED (empty scope)`, "no production code line added or modified against the base". It drew no mutant, so the targeted mutants above are the mutation evidence.
- Architecture (step 15): the added lines are two self-test rows and comments beside the existing rows, with no production change in this round. Nothing breaches.

## Red checks

The check-runs API per commit (ev/check-runs.txt, ev/check-runs-head-final.txt, the latter taken at 02:46Z after every run at the head had concluded):
- c5a968de3: every run is success, skipped or neutral except `nightly-status` (failure, 02:23:19–02:23:30Z). That includes instrument-self-tests, closures, Analyze (python), mutation and fast (3.14).
- aef2c3e2e, cfdd9c26c and 53ae6a8ca: no check runs.
- 400e15d27: `nightly-status` failure only.

`nightly-status` grades main's nightly run, and this diff touches nothing it reads. The body's `## Red checks` names it and answers why it is not this branch's. `pr-contract` ran green twice at this head, and the second run started at 02:23:47Z, after the last red concluded (02:23:30Z). So the red-check trigger is answered (step 11).
