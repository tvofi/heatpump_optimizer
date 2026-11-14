Fix review: merge f14a2fbcf5bb1d0f1e7debb586a840d829e2a83a

bus-nonce: 6b4dbee3a4293fb89869efe4fbbea114
pending-ci: gate

## Scope

Round 1, full review of this group's own commits, measured at head f14a2fbcf5bb1d0f1e7debb586a840d829e2a83a (merge base c987209cc7a891e0e4066d4ad8dc5cf55357c5ae).

The branch is STACKED: b6f3ab15b7 (first parent d712c2ba4a, PR #3481's head) merges PR #3574's old head 22e9330193. Commits reachable only through those two heads are those PRs' work and are reviewed there, not here. This PR lands only after #3574 and #3481 have merged; the body states the same condition and the re-merge enumerators (`git diff <stacked head> <merged head> --stat` for each).

This group's own commits: b6f3ab15b7 (the stacking merge; remerge-diff shows only the ledger driver's `class_excess_loc` resolution, 17503 + both deltas = 17454), f919d224ca (dev/README.md one cell: #201 -> #3394), 30314c72c5 (hand merge of origin/main c987209cc7), f14a2fbcf5 (the delivery row dev/programme/delivery/3582.md only). ev/own_commits.txt.

## Evidence

- (b) 30314c72c5's one hand resolution, tests/golden/claimed_drift.txt: blob e348abdc9e at 30314c72c5, at the head, and at handoff/r10-sav-valuation-residue 3b64f9397e: byte-identical, verified. Against parent 1 (f919d224ca, blob 62e9839bd4, identical to 22e9330193's) the result changes only claims-for 7.1.15 -> 7.1.16, the v7.1.16 note, and drops the config_flow R10-OUTSIDE-DHW-START-HYSTERESIS claim the stamp had emptied on main. Against parent 2 (c987209cc7, blob 8b6433462b) it adds only the eight valved baseline_cost claims, the six suspended may-drift entries and the R10-SAV-VALUATION-RESIDUE reason block, all #3574's. The driver printed `MERGE-CLAIM: refused` (different claims-for stamps), so the hand resolution was owed, not a bypass. ev/claim_file_and_merge.txt.
- (c) The body's `## Head` section says the evidence was measured at f919d22 and the merge adds only main's content. Verified: 30314c72c5's remerge-diff touches claimed_drift.txt alone.
- Step 13: `git merge-tree --write-tree origin/main f14a2fbcf5` rc=0, no conflict. origin/main = c987209cc7 = merge base, so the head is not behind main.
- Step 4: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all c987209cc7` exit 0: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`. 8 fixtures print `CLAIMED ... moved` and 8 are claimed, so every claim moved. card_claimed_drift.txt is unchanged on the three-dot diff (0 lines). `--claims-only c987209cc7`: `claims hygiene ... ok`. ev/env_drift_all.log.
- Step 5: the three-dot diff touches none of VERSION, the manifest or RELEASE_NOTES.md. VERSION 7.1.16 equals claims-for in both claim files.
- Step 1 mutation: n/a. The group's own diff writes no production line (one dev/README.md table cell plus a delivery row), so no mutant can be planted on it. The six unpinned sites the body lists (coordinator.py:10703, price_tiles.py:130/146/148x2, whatif.py:149) are stacked-head lines owned by #3481/#3574.
- Step 2: no finder's harness is named (packet: "none named"). For a docs-delta group the controls are the doc checks, re-run at this head: `python3 tests/doc_claims.py` prints ALL 348 checks PASSED, and `--markers` prints 0 of 0 marker(s) due. Both match the body. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints ALL 2711 ENTITY CHECKS PASSED, exit 0, which also matches the body. Its two printed `FAIL a12/a13` lines are its own negative-case output inside a passing run (ev/entities.txt).
- Step 8 figures: module count 92 (`ls custom_components/heatpump_optimizer/*.py | wc -l` at the head), re-derived. dev/governance/rules/writing-for-agents.md says "Volatile state goes on #3394", so the f919d224ca correction is right. The body's 54-path and 26-file delta counts were measured against 45d21a6a6d and were not re-derived here.
- Step 7: the body names f14a2fbcf5 as the head (row-only commit over authored head 30314c72c5); it matches.
- Step 10: the body's one forward-carry, Carry 5 (a live read of ruleset 23698884 confirming "requires only gate"), names its own group, R10-ARCH-DOCS-DELTA, pending "the owner's read". That waits on a pending owner read, which fixer.md allows for an own-group carry. carry_audit at the head (packet): 1 routed, 0 unrouted, 0 bad.
- Step 11 red checks: owed-reds at this head (ev/owed_reds.txt) includes arch-score, tests / briefs, tests / fast (3.14) and tests / mutation. The body answers all four under `## Red checks`, each with a cheaper detector, or the finding that none exists on this diff. CI at this head: `merge_train.py classify f14a2fbcf5 --pr 3582` printed WAIT (rc=3) from 03:26:47 to 03:56:09 UTC, last line `WAIT f14a2fbcf5bb1d0f1e7debb586a840d829e2a83a pending: gate red: none` (ev/classify.log). No required check was red at the head while I polled. The verdict therefore carries `pending-ci: gate`, and a red on that run is the relay's to refuse.
- Step 14: the only number this group's own commits move is the ledger driver's class_excess_loc resolution in b6f3ab15b7, the sum of the two stacked heads' own deltas. Neither stacked head's change is paid for here. No budget is raised.

## Findings

- Residual: two dated records still say #201 carries volatile state, dev/programme/plan-2026-09-open-issues.md:412 and dev/audit/rounds/round4/RESUME.md:6. Both are historical round and plan records, not governing documents, and neither is in this group's scope (docs/architecture.md, dev/README.md). Carry: dismissed: dated historical records describe the state when they were written; rewriting them would falsify the record.
- Residual: the body says `tests / briefs` "is not in merge_train.py owed-reds", but at this head it is in the set (ev/owed_reds.txt). The body still answers it under `## Red checks` with the cheaper detector (`node tools/policy/brief_lint.mjs`, about one second, already in prepr), so the trigger is met and only the side remark is wrong. Carry: dismissed: the trigger is answered; the wrong aside changes no obligation.
