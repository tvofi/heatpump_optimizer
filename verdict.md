Fix review: blocked 49658957ac52c32e3fae3e30dc2b584946641d22 merge-conflict: tests/deployment_shape.py conflicts with origin/main dbdc520e

bus-nonce: a4cb488b71e5c18f189e48a835055852

## Block

- `git merge-tree --write-tree origin/main 49658957ac52c32e3fae3e30dc2b584946641d22` at origin/main dbdc520e86e4453755f553ab21a39de205a70b34 exits 1 with `CONFLICT (content): Merge conflict in tests/deployment_shape.py` (ev/merge-tree.txt). The conflict is the #1218 closure note's pair counts: main's side records 182 of the 561 script pairs at >= 0.80 (and 182 among the 435 comparable pairs), this head's side 186 (ev/deployment_shape-conflict.txt). It is not a claim file, so no `MERGE-CLAIM` driver settles it; it is the fixer's to resolve (fix-review.md step 13). GitHub reports `mergeable_state: dirty` too, but the block rests on the merge-tree exit, not that field.
- The repair re-derives the note from what `tests/entities.py` prints on the merged tree, and re-records `tests/structure_budgets.json` against main dbdc520e's table. The ledger merge of that file resolves only by summing deltas and prints nonsense for one row (`unloaded_package_imports: 14 + both deltas = -6`; main has meanwhile lowered max_class_loc to 7822 and class_excess_loc to 17241), so the raise this PR records against 7aa6020f's table must be re-measured on the merged tree with `tests/structure.py`, and the body's `## Raise justification` figures re-stated against the new main.

## Findings

none

## Evidence

- Review scope: full (packet `## Review scope` line: no verdict names the reviewed head). Only the merge measurement and the budget raise were checked to completion; the conflict blocks, and the code review owed at the repaired head is full again since the diff will move.
- Budget raise at this head: `tests/structure.py` at 49658957ac52c32e3fae3e30dc2b584946641d22 measures max_class_loc=7833, module_excess_loc=21773, class_excess_loc=17278, unloaded_package_imports=3, each `ok` at exactly the recorded budget (ev/structure-at-head.txt, ev/budgets-diff.txt). So the raise equals the measured value at this head: max_class_loc 7832 -> 7833 and module_excess_loc 21763 -> 21773 against the base d9100de7's table. The body records class_excess_loc 17288 -> 17285; the head's file and measurement read 17278, which is lower and harmless but differs from the body's figure.
- `## Raise justification` carries a `Payments tried:` line, lists four payments, each with an `Architecture score: dS` line or a reason it was not built (1: dS -2.5873, rejected for an import cycle; 2: dS -0.0011, kept as 00be81ff; 3 and 4: no payment exists), plus the head-level line `Architecture score: dS -0.0011 WORSENS (coord_footprint 2531 -> 2533)`. That satisfies CLAUDE.md rule 2's mandate-exception shape. I did not re-run score.py: the figures are against main 7aa6020f, and the merge repair moves them.
- review_packet: `REFUSE structure: ... head does not merge cleanly with origin/main` on tests/deployment_shape.py, which agrees with the merge-tree measurement.
- CI: `merge_train.py classify 49658957ac52c32e3fae3e30dc2b584946641d22 --pr 3882` printed `WAIT 49658957ac52c32e3fae3e30dc2b584946641d22 pending: gate red: none` (ev/classify.txt). Not waited out, because the merge conflict blocks whatever CI concludes at this head.
- `owed-reds` (full set in ev/owed-reds.txt): none of them is red at this head, so no `## Red checks` answer is owed.
- seat_comms: initialised (`resumed 6faa8f40733b`), heartbeat running, no CMD received.
- Earlier fire: probe/rev-3882-a4cb488b already held f5c4ebb8 (2026-11-26 01:01 UTC), `Fix review: merge 49658957` with `pending-ci: gate`, written when this head still merged with the main of that time. origin/main has since moved to dbdc520e, and the head no longer merges with it. This commit is a fast-forward child of f5c4ebb8, so that record is kept rather than force-pushed away. This verdict supersedes it.
