Fix review: merge b4ce6ef0fe45b6c9635ed5d22e0d71afb176371a

bus-nonce: 7da687fdf1528f382fa90e944e51a711

Round 1. A triage record only: one markdown file under dev/programme/triage/ and one delivery row; no production code, VERSION, manifest, notes or claim file touched.

## Evidence
- Head measured: b4ce6ef0fe45b6c9635ed5d22e0d71afb176371a (ev/HEAD.txt). Re-read live: the PR head is unchanged.
- `git merge-tree --write-tree origin/main <head>` rc=0, tree 204b750b92; no conflict.
- `merge_train.py classify <head> --pr 3391` rc=0: GREEN, pending none, red none. No red check, so the body's "Red checks: none" is right and owes no root-cause answer.
- Review packet: refusals none, advisories none, carry_audit 0 finding items, figure_lint 1 unverified (a `git diff --stat` command, not a figure).
- Three-dot diff: 2 files, +489 lines, matching the body's "one file" plus the delivery row.
- Cited code at 6457496aba re-read: cloud_dispatch.py:474 (upper-case design-verdict ref), :231 (unbounded WAIT), orchestrator_tick.py:214 (UNBLOCKABLE_STAGES) and :2344 (OWED cap line), merge_train.py:817 (HOLD_REF) and :1275 (undraft), gh_calls.py:161, tests/gate_lock.py:112 (SLOT_LABEL_ENV), prepr.sh:3578-3579, owed_unactioned.py:111, carry_audit.py:32, cloud_relay.sh:692-693 all say what the entries state.
- Every destination group the rulings name (14 distinct ids) exists in the roster branch's rosters at its tip (ff9cf74ad, ahead of the body's 9a4a04d55).
- Not re-derived: the body's mutation proof and null control (roster_edit.py op_append_carry / brief_lint on a simulated roster); the session-local logs behind figures (13 of 160, 1089 re-attempts, 281 recarries). They are cited to out-of-tree logs and are not re-derivable here.
- The body's Head section names two SHAs: b4ce6ef0 is the head, 4cd0a64e6d the earlier code head; the PR's own patch is the same two files.
