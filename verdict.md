Fix review: blocked 7fe24f9f61f1935fab269f006e126fc6f84184b3 merge-conflict: head does not merge with origin/main (thermal_model.py and others conflict) and the gate check is red

bus-nonce: 591afeba57b931282315828c5a814a15

## Block
- `git merge-tree --write-tree origin/main 7fe24f9f61f1935fab269f006e126fc6f84184b3` reports content conflicts, among them custom_components/heatpump_optimizer/thermal_model.py, dev/audit/rounds/round3/D5/option_doc_coverage.py and dev/audit/rounds/round4/D6/claims.json (full list in ev/merge-tree.txt). The branch must be rebased and steps 2-8 of fixer.md re-executed.
- `merge_train.py classify` printed `RED 7fe24f9f61f1935fab269f006e126fc6f84184b3 pending: none red: gate`. The `tests / fast (3.14)` check is red and not named in the body's `## Red checks` (review_packet: red-unanswered).
- review_packet also refused on `structure`, because the head merged with main does not merge cleanly.

I did not run mutation proofs or re-check the body's figures, since the head cannot land as is.

## Evidence
- ev/HEAD.txt: head reviewed.
- ev/merge-tree.txt: merge-tree output.
- ev/classify.txt: CI classification.
- ev/review-packet.md: rendered packet.
