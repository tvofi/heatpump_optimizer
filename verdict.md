Fix review: merge 079fb16467219f6a46a8981ecf28c477c6d52ba3

bus-nonce: cfee3acf23a1ccd0bc7443568e9b5aa2

Round 2 of PR #3011 (R10-ARCH-DOCS-WIRING). Measured head 079fb16467219f6a46a8981ecf28c477c6d52ba3 (code head fc907699e, previous reviewed head 75b30a4e2). Scope: the delta 75b30a4e..079fb164 and round 1's open point (gate-red on tests / briefs).

## Findings

- carry-1645.json's control paragraph still cites `tests/doc_claims.py:487`, `:605-619` and `:612`, which the two added imports shifted too (the code now sits near 622). Nothing reads them: brief_lint passes, and the paragraph's own `remeasure` text says not to trust its line numbers. Carry: dismissed: prose in a field that tells the reader to re-locate by symbol, not enforced by brief_lint, and the two enforced anchors in `brief` are fixed.
- The body records the cheaper detector (prepr step 3f running brief_lint when the diff touches any file a carry or roster `path:line` cites) as not built here, for orchestrator triage. Carry: dismissed: one occurrence so far, outside this group's seam, and the body records the decision as defect-root-cause.md allows.

## Evidence

- RESULT brief anchors: tests/doc_claims.py:479 is `def check_initial_setup_menu`, :570 is `def check_simulate_plan_fields` at this head (ev/anchors.txt). carry-1645.json's `brief` field cites exactly those two lines.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs` exits 0 here, and `carry-1645.json: 0 error(s), 0 warning(s)` (ev/brief_lint.txt). CI `tests / briefs` is success at this head. The output's remaining ERROR lines are the deliberate fixture/wave errors the lint's own tail says it pins (CARRY ok); I did not separately re-derive the body's "ten" count.
- RESULT other citations: a grep of dev/ and tests/ finds no other `doc_claims.py:<line>` in a carry or roster file beyond carry-1645.json. I did not read the roster branch (`handoff/audit-r10-roster`) itself; the body states it has none.
- RESULT red check answered: the body's `## Red checks` names `tests / briefs`, the cause, the process state (prepr 3f skipped because doc_claims.py is not pinned), the cheaper detector (local brief_lint, ~2.5 min, or a 3f extension) with its standing cost, and a recorded countermeasure decision. The detector is real: it is the lint CI ran and the one I ran.
- RESULT mergeability: `git merge-tree --write-tree origin/main 079fb16467219f6a46a8981ecf28c477c6d52ba3` exits 0, no conflict (ev/merge-tree.txt).
- RESULT version: no change to VERSION, RELEASE_NOTES.md or a manifest version against the merge base.
- RESULT CI: `merge_train.py classify 079fb16467219f6a46a8981ecf28c477c6d52ba3` exits 0 (GREEN, pending none, red none), after the head's later runs concluded.
- Delta beyond the re-anchor is two automatic merges of origin/main (#2989 open_pr.sh/pr_args.sh, delivery rows); none touches this PR's files. Round 1's mutation proof, forward-carry and figures were not re-litigated; the earlier mutants' lines in tests/doc_claims.py are untouched by the delta (only the carry JSON changed in the fixer's commit fc907699e).
- review_carry.py prints FRESH-REVIEW against 75b30a4e (round 1 was blocked), so this verdict is a fresh one at the head above.
