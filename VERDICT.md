Fix review: merge 66c8fa12c1b16193470181ab747d641656d84a62

bus-nonce: 76c4b2f7e1b8cbf45544116bf80b0722

Round 1 of a record PR (triage s8 batch 82, P319). Head measured: 66c8fa12c1b16193470181ab747d641656d84a62; diff is two new files under dev/programme (delivery row, triage note), no production code.

## Evidence
- RESULT code facts at origin/main: `load_dests` is at carry_audit.py:342; the explicit-ref path is lines 347-352 and sets no `round_roster`; the `round_ref` read and `round_roster = (rref, ...)` sit at 372-374 under `else:` (the body's "370-374" covers the comment through the assignment). `queue_pre_flight.py:197` calls `ca.load_dests(self.checkout, "origin/main", ...)`. The premise holds (ev/load_dests-main.txt).
- RESULT roster instance: R10-FLY-CANCEL-SWEEP is absent from main's wave-r10-groups.json (0 hits) and present on origin/handoff/audit-r10-roster (3 hits), as the body says for #3004 b42363f1. R10-FLY-RELAY-REVIEW-FF, the carry's destination, is on the round roster branch.
- Not re-derived: the two train-log waivers (#3004 b42363f1, #2925 162aa32f) and the held op b82-P319.txt live on the orchestrator's machine. The #3004 instance is consistent with the roster facts above; the #2925 one is taken from the body.
- Null controls: carried in the carry text (neither-roster group still BAD-DEST; round-branch-done group still refused), as the contract needs. They are not run, since no code is in this PR.
- Merge: `git merge-tree --write-tree origin/main 66c8fa12c1b16193470181ab747d641656d84a62` exits 0, no conflict. VERSION, manifest and notes untouched; claim files untouched; no budget or closure file moved.
- CI: merge_train.py classify exits 0, GREEN, nothing pending or red. The packet's gate digest is green with no refusals and carry_audit reports 0 findings, 0 bad destinations.
- Commit message of the head carries no footer or trailer.
