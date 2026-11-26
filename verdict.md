Fix review: blocked eead33b0ac600ce4f6ef250ba47166fefe8e0402 ci-red: required gate RED at this head; tests / closures still stale (tools/ci/shards.py), repaired only by the bot re-record at 98c1e9df

bus-nonce: 43f89420d4af0a17bbf0b1607e270e7c

## Block

Round 4, a delta round over fe2b516c..eead33b0ac600ce4f6ef250ba47166fefe8e0402. It is the fixer's commit fa4ea28e plus a merge commit with no other change; eead33b0's tree diff from fe2b516c is fa4ea28e's 4 files. The previous block (fe2b516c) was ci-red: tests / closures UNDER-SCOPED, because tests/entities.py reads tools/ci/shards.py and its closure did not list it. The delta does not touch tests/closures.json. At this head `merge_train.py classify eead33b0... --pr 3902` reads `RED eead33b0ac600ce4f6ef250ba47166fefe8e0402 pending: none red: gate` (rc 1). tests / closures (job 139896056658) ends `1 closure(s) are stale` with exit 1. The prior block therefore stands at this head. A red never carries (fix-review.md step 12).

The repair exists: closures-autofix pushed 98c1e9dff262a71ce3c5285c790b4b6173dd16a9 ("ci: re-record closures", github-actions[bot], parent eead33b0). It adds tools/ci/shards.py to tests/entities.py's closure, adds services.yaml to one closure, and updates three `recorded` timings. `review_carry.py eead33b0 98c1e9df` prints CARRY (rc 0), and the bot commit is the repair ci-autofix.md provides. The remaining review owed at 98c1e9df is a green classify there: the fixer's code delta below found nothing to block.

## Red checks

- gate / tests / closures: caused by this PR, an under-scoped closure for tests/entities.py over the new tools/ci/shards.py, repaired by the autofix at 98c1e9df; this is the block. The body names it under its Red checks as left to closures-autofix, which ci-autofix.md sanctions. Cheaper detector: `./tests/derive_closures.sh --single tests/entities.py` on Linux, or `ci_predict.py`'s closures arm, before the handoff; the body does not say why ci_predict did not predict it.
- tests / nightly-status: red, not in the owed-reds set (ev/owed-reds.txt); not answered, no block.
- The previous round's unattributed `tests / fast (3.14)` red is green at this head (job 139896056569, success).

## Findings

- Note: root-cause-unanswered: the body says closures-autofix should record tools/ci/shards.py, but it does not answer why `ci_predict.py` (which it reports predicting no closures red at 4c267409) missed an UNDER-SCOPED read of a new file that tests/entities.py reads. Carry: #3885

## Evidence

- Delta (fa4ea28e, 4 files): tests.yml fast job name made a literal `fast (` ... `)`; prelude.outputs always prints `fast_shards`/`fast_plan` (empty when there is no planner); entities.py `_PCR_READ` reads a chained `ROOT / "a" / "b"` as one path; pr-contract restores tests/run.sh.
- Mutant, prelude: replacing `out.update({"fast_shards": "", "fast_plan": ""})` with `pass` makes `prelude.py --self-test` print `FAIL P2: with no planner both outputs are still printed, empty ... got {'fast_shards': None, 'fast_plan': None}` and `154 checks, 1 failed` (rc 1, ev/mutant-prelude.txt). Head: `154 checks, 0 failed` (rc 0, ev/prelude-selftest-head.txt). KILLED.
- Mutant, entities `_PCR_READ`: tests/entities.py cannot import on this host (no homeassistant in any local interpreter; ev/entities-head.txt), so I re-ran its `_pcr_closure` logic standalone over the head tree (ev/pcr-reader-probe.txt). The old reader puts the directory `tests` in the closure; the new one puts `tests/run.sh`, which shards.py reads as `RUN_SH = ROOT / "tests" / "run.sh"`. pr-contract restores `'tests/run.sh'`. This is my own probe, not the fixer's harness. The entities.py check itself ran green in CI's `tests / fast (3.14)` at this head.
- tests.yml name: the literal form renders `fast (3.14)` when shard is empty and `fast (3.14, K/N)` otherwise, matching the body's naming. Not executed locally (GitHub expression).
- `python3 tools/ci/selftest_scope.py static` at the head: `129 gated step(s), 0 problem(s)`, rc 0 (ev/static-head.txt).
- `git merge-tree --write-tree origin/main eead33b0`: rc 0, tree 19a12ac9; tests/closures.json resolved by the ledger merge driver (ev/merge-tree.txt). The head is behind main and merges cleanly.
- Head move during review: 98c1e9df, one bot commit, review_carry CARRY (ev/head-moved.txt, ev/autofix-closures.diff).
- classify poll log: ev/classify-log.txt. The closures log tail and classify line: ev/ci-red-closures.txt. Packet: ev/review-packet.md.
