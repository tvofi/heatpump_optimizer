Fix review: merge 6948302a4eaf992e221be3786fc2d74d864f7eeb

bus-nonce: 5f7c8d6cb404cc64dad3f3d6740ff28d

Round: resolution-delta review (later round) of the merge of origin/main (1cabb845) into the branch; delta from 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b.

## Evidence
- RESULT de.json at head == origin/main de.json: byte-identical (git diff --quiet, rc 0).
- RESULT delta 3377b5f0..head touches 3 files: de.json, www/heatpump-optimizer-card.js, dev/programme/delivery/3378.md. Each is byte-identical to origin/main, and each is a file main's #3378 changed. No file differs from both the reviewed head and main.
- RESULT automatic merge of 3377b5f0 and 1cabb845 conflicts only in de.json; head differs from the automatic tree only there (11 conflict-marker lines resolved to main's side). review_carry prints FRESH-REVIEW because the head is a hand-resolved merge, as expected.
- No production code differs from main beyond de.json and the card file, both main's own; no wider review warranted.
- git merge-tree --write-tree origin/main head: clean.
- CI: merge_train.py classify exit 0: GREEN 6948302a4eaf992e221be3786fc2d74d864f7eeb pending: none red: none. The review packet's early "gate failure" digest was stale. owed-reds set in ev/owed-reds.txt; none red.
- carry_audit at head: 2 routed, 0 unrouted, 0 bad destinations.
- Not re-derived: the previous verdict's findings at 3377b5f0 were not available to this seat; the delta touches nothing of the PR's own work, so none is reopened by it.
