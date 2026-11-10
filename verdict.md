Fix review: merge dd58cb82f7a65acb23e995d4c3ae69d5ccd39631

bus-nonce: 0f9883d09ac75f7ea5e97c516241f769

## Evidence
- Head measured: dd58cb82f7a65acb23e995d4c3ae69d5ccd39631 (docs-only: dev/programme/delivery/3382.md, dev/programme/triage/s6-batch129.md; no VERSION, manifest or notes touched, no claim file, budget or closure moved). Round 1.
- RESULT merge-tree: `git merge-tree --write-tree origin/main <head>` exit 0, no conflict.
- RESULT ci: `merge_train.py classify` rc 0, GREEN, pending none, red none.
- RESULT cited-lines at 355d9965a: mkdtemp lines 601, 1337, 1632 and rmtree-in-finally lines 623-624, 1359-1360, 1688-1689 match the note; file is 1693 lines; `git log --since=2026-10-24 --oneline 355d9965a -- tools/pr/ci_predict.py | wc -l` is 30. Raw output in ev/ci_predict_at_355d9965a.txt. At current main the lines have moved (601 -> 677) but the try/finally pattern still holds.
- RESULT no CODEOWNERS row and no structure_budgets.json row for ci_predict (grep empty), as claimed.
- Not re-derivable here: the host-local figures (tree size 603M, pids, df, the 0.55 GB leak). They are the seat's own readings on another machine; the verdict does not rest on them, since the REJECT turns on the verified existing finally blocks.
- Mutation proof, finder's harness, null control, claim drift: not applicable, no production code or fixture changes. carry_audit.py at head: 0 finding items. No red check, so no root-cause answer owed.
- The file name says s6 while its title says session s12, and batch128 follows the same naming. Carry: dismissed: evidence, not a finding
