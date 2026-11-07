Fix review: merge 2fef6b26ac392e49366a8d4acb9b26f4a1162a7f

bus-nonce: cb8ecae6c132d58112ab90dce9976d72

Round: scoped body-only re-check of a head already verdicted (merge at 2fef6b26ac392e49366a8d4acb9b26f4a1162a7f, code 6a6b04ac6). Mutation proofs not redone: no figure I re-derived was off.

## Evidence
- Code identical: the +/- lines of the three-dot diff (merge base a37c58e5f) for nightly.yml, tests/mutation_table.py, tests/entities.py, tests/closures.json and both harnesses are byte-equal (md5 of changed lines) at 6a6b04ac6 and at 2fef6b26ac392e49366a8d4acb9b26f4a1162a7f. The PR touches no VERSION, manifest, RELEASE_NOTES.md, budgets file or claim file. The delivery row dev/programme/delivery/3269.md is in the diff. The two new harnesses are in tests/closures.json.
- Figures re-added from the body: shard draws 80+80+81+79=320; killed 14+35+21+20=90; lives 6+22+8+8=44; not run 60+23+51+51=185; 90+44+1+185=320; killed new 20 (22% of 90); 130 of 194 kills = 90+104; shared pairs 2234/6028=37%; charge 17.8/132.6 h=13%. All consistent. figure_lint: 9 resolved, 0 not verified. The shard logs and the 225-minute job time were not re-fetched.
- Merge: git merge-tree --write-tree origin/main (4b5d771bd) rc 0, LEDGER-MERGE resolved tests/closures.json (ev/merge-tree.err).
- Head section names 2fef6b26ac392e49366a8d4acb9b26f4a1162a7f, which is the live head.
- Red checks at the live head: pr-contract / pr-contract 42382938580 (push-time run, 15:35Z) is failure, refusing the old body. The re-taken body's pr-contract run 42392365518 (16:47Z) is success, and its gate (16:48Z) is success; gate in run 42382939427 is success. tests / nightly-status is failure: a check that grades main, not this diff, and the body names it with its cause (cancelled dispatch 42369836867). Every other concluded check is success or skipped. merge_train.py classify: GREEN, pending none, red none (rc 0).
- The check-run ids the body quotes (128444733261, 128434352318) differ from the ids this listing shows for the same runs (128465507613, 128465529651); the runs and conclusions match. Cosmetic.
- Survivor triage stays manual (body, ci-autofix.md); nothing in the diff touches it.

## Findings
- Owed after merge: the pins-per-night after-figure needs a workflow_dispatch nightly on main (mutation-ledger runs only on refs/heads/main), read with nightly_drain_breakdown.py over the four shard logs. Carry: R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT | dismissed: owed by the seat that lands this PR, not a defect in the diff
