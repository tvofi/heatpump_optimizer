Fix review: merge 93f6ce5c391c49e0853dde6cf96430fe265f798f

bus-nonce: 7166a6d725268ec89bb69ad3e0a24f0f

Delta review of record PR 3210 (ruling text only), 1570415e to the head. Round 1 blocked on citation-wrong; that is now repaired.

## Evidence
- Roster read: origin/handoff/audit-r10-roster at ed1e31e1a0c78ab449ea8373bc81ec8f5febf865, dev/programme/rosters/wave-r10-groups.json; R10-HANDOFF-PATH holds 16 carries.
- Carry 9 is the P22 text: key (topic, handoff sha, body sha), "Only content refusals (prepr REFUSE) stay recorded failed", "28 permanent ... unrecoverable for all 28". The head cites carry 9 at lines 84, 102, 123, 143 and 144, all right.
- Carry 6 is the driver4.py / seen2.txt text. The head cites carry 6 at line 133, right. Carry 8 is pr_tools_fresh and carry 5 is the structure.py/#3052 text, so the old numbers were wrong. Carry 11 is stem(), unrelated to the driver, and is not cited.
- The delta (ev/delta-1570415e-to-head.diff) changes only these citations plus the narrowing sentence. Nothing else in the file moved.
- Paste block (lines 140 to 150 of the head file) uses carry 9 throughout and carries no stray number. The roster's own carry 13 already holds the same text with carry 9.
- Narrowing sentence present at head lines 144 to 146: it narrows carry 9's "Only content refusals (prepr REFUSE) stay recorded failed" by splitting body-content refusals from retryable steps, and says it adds no second rule. It does not contradict carry 9: carry 9's content refusals stay recorded until the body ref moves, and only the non-content refusals gain a retry.
- Other figures and ids (P384/P385 numbering, 94 failed rows, 22 of 45, R10-TRIAGE-S6 delivery row) are untouched by the delta and still resolve; carry_audit at the head: 0 findings. figure_lint: 1 resolved, 1 not verified (a generic git diff --stat line), 0 refused.
- Merge with origin/main (785c2b604b...): git merge-tree --write-tree rc 0, clean (ev/merge-tree.txt).
- CI, all check-run pages: merge_train.py classify exits 0, "GREEN 93f6ce5c391c49e0853dde6cf96430fe265f798f pending: none red: none".
- Two concluded-red checks I read: governance / delivery-status (job log: "DELIVERY STATUS OVERDUE - 10 rowed, 12 pending, 21 overdue", listing other PRs #3220, #3229, #3227 and others as pending rows) and tests / nightly-status (log: slow lane failed on the 2026-11-05 scheduled run 41943946464, head 499162c, and says it is not a required context). Neither concerns this PR's files and neither is required, so classify does not count them.
- This merge verdict approves ruling text only.
