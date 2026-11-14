Fix review: merge 336a6ca07744d5139914947f58d9f0c4f04bb45a

bus-nonce: b8bdfe461b0b059dfeeb9cb1796c3b6b
pending-ci: gate

Round 2 (later round over b6c080dbcc6cd2294e3ae0913a2c818670749566; scope: delta). Head measured: 336a6ca07744d5139914947f58d9f0c4f04bb45a (ev/HEAD.txt). review_carry b6c080db -> 336a6ca0 prints FRESH-REVIEW, so this is a delta review. The PR's own three-dot patch is now .gitignore, dev/audit/harnesses/prepr_slot_nested.py, dev/programme/delivery/3479.md, tests/closures.json (+1 entry, the harness) and tests/layout.py. The rest of the b6c080db..head diff is main merges. No custom_components/ line is in the PR's own patch, so nothing widens the scope.

## Evidence

- Previous block (harness-vacuous, carry PREPR-SLOT-LIVELOCK) resolved. At the head, `python3 dev/audit/harnesses/prepr_slot_nested.py` gives rc 0 and verdict=ok (ev/harness_head.out). The bare arm now differs by evidence. slot-status lists its ticket (`queue=prepr-1075`, bare_queued=1) while the labelled nested arm prints `heavy slot joined prepr-1067`, finishes in 0.1 s and leaves `queue=-`. Points 1 and 2 of the old block are cured. Point 3 is cured too: the harness no longer injects HPO_SLOT_LABEL. The outer shell runs prepr's real `take_slot` text against the real tests/gate_lock.py with 3/4 slots held, and outer_exported_label=1 comes from the real take path. The WARN path (unusable lock dir) exports no label and only warns (warn_no_label=1, warn_finished=1).
- Mutation re-run, harness: `--mutant` (deletes `export HPO_SLOT_LABEL` from the cut function) gives rc 1. outer_exported_label, nested_finished, nested_queue_empty and nested_joined all flip to 0 (ev/harness_mutant.out).
- My own planted mutant on the static arm: I inserted `  take_slot` into prepr.sh's `--self-test` branch (after :1907). selftest_branch_takes_slot=1 and the harness gave rc 1 (ev/harness_static_plant.out). The static arm can fail. I restored the file afterwards.
- Old block point 4, the arm through a live outer prepr step 3h, is met by composition rather than by a live run. It combines the real `take_slot` text (take, join and WARN arms) with the static proof that the nested `--self-test` branch makes no real take_slot call. I judge that sufficient, since step 3h is exactly `take_slot` followed by a nested `--self-test`.
- Carry 4 (.gitignore `/config/`): `python3 tests/layout.py` at the head gives rc 0. It prints `layout: GITIGNORE: 0 finding(s)`, both gitignore self-test rows are ok, and `layout self-test: ok` (ev/layout_head.out). Mutant: reverting `.gitignore` to `config/` gives rc 1, `GITIGNORE: 2 finding(s)` naming dev/audit/config/x and dev/governance/config/x (ev/layout_gitignore_mutant.out). The null control (root config/x still ignored) is inside gitignore_config().
- Repair of the 433536b6 reds:
  - (a) arch-instrument UNWIRED. tests/gitignore_config.py no longer exists, nothing in the tree names it outside tests/layout.py's own function, and tests/layout.py is `run_always` in tests/run.sh:604.
  - (b) closures stale/UNDER-SCOPED. The PR's closures.json delta is now the single harness entry, and `git merge-tree` resolves tests/closures.json via the ledger driver.
  - (c) fast (3.14) entities.py/harness_headers.py. The new script is gone and the harness carries the inlined repo_root walk.
  - Locally `tests/harness_headers.py` fails 56/112 identically at the head and at origin/main ef579d9b (ev/harness_headers.out, ev/harness_headers_main.out). That is an environment difference in this container, not the PR. The body's 112/112 and entities.py 2707/2707 were not re-derived by me; CI's fast lane at this head is the evidence (see CI state).
- Budget: the three-dot diff touches no *_budgets.json, tests/ci_budgets.json or tests/deployment_shape.py. The 54->56 raise in 37d7082ae is net-reverted, so nothing is raised.
- Red checks (owed set: ev/owed_reds.txt). At 433536b65f2507d47eaeeadebc8b9461bac19013 these went red: gate, tests / arch-instrument, tests / closures, tests / closures-autofix, tests / fast (3.14) and tests / nightly-status. bdc2e986 and the head show no failure. The body's `## Red checks` answers arch-instrument, closures (UNDER-SCOPED named) and fast (3.14), each with a cheaper detector. closures-autofix and nightly-status are outside the owed set. `gate` is in the owed set and is the aggregate of the others. The body does not name it separately, so pr-contract's run at this head is the evidence that the body clears the check (step 11: it is not re-derived).
- Merge: `git merge-tree --write-tree origin/main 336a6ca0` gives exit 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.out). No conflict.
- VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff empty).
- Body figures: the harness RESULT set reproduces exactly at the head. The queue ticket numbers are pids and differ per run. The body cites prepr.sh:4184 and :4192 for the export and WARN paths; at this head they sit at :4265 and in the WARN branch below it (line drift from main merges). Citation only, the behaviour is the same.
- Forward-carry: the body has one item, PREPR-SLOT-LIVELOCK `dismissed:` with harness@79c063dc. carry_audit at the head routes it (1 routed, 0 unrouted). The dismissal is now supported by a discriminating control.
- Finder's harness: none named in the packet. The carry's harness was built by the fixer, and I disclose it as the builder's. It is committed in the tree (dev/audit/harnesses/prepr_slot_nested.py).
- CI state: `merge_train.py classify` printed `WAIT 336a6ca07744d5139914947f58d9f0c4f04bb45a pending: gate red: none` every minute from 03:43 to 04:13 UTC (ev/classify.log). No red at this head, and the gate is still pending, hence the pending-ci line.

## Findings

none
