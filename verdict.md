Fix review: merge 36c7b25f9b5fab1e9496dee7814160de37bf8461

bus-nonce: 0cb4ed3697f16a310029ee65d282a8f3

Round: resolution-delta review (scope per owner ruling 2026-11-09), head 36c7b25f9b5fab1e9496dee7814160de37bf8461, delta from c671154342fbb2949fd670d30065a7228e172466.

## Evidence
- Head measured: 36c7b25f9b5fab1e9496dee7814160de37bf8461 (ev/HEAD.txt). review_carry.py prints FRESH-REVIEW (two main merges), so this is a resolution-delta review.
- finding.schema.json union: the class_guess enum at the head holds both main's R10-TOPIC-FAMILY and this PR's N-stamp-claim-conflict, and no id twice (54 entries, 54 distinct). `node tools/policy/check-wave-script.mjs`: 226 passed, 0 failed, so the enum equals bugclasses.json plus new (ev/check-wave-script.txt).
- audit-find.js: `fold_ledger.py sync` at the head prints "already carries dev/audit/config/finding.schema.json" and leaves the tree clean, so the file is byte-identical to the committed one (ev/sync.txt).
- Head merge 36c7b25f9 (parents 3e8998600, b8f67a775) hand-resolved one file, dev/audit/config/bugclasses.json: both R10-RCA-SWEEP-SETTLE-LOOP (main) and R10-RCA-STAMP-CLAIM-CONFLICT (this PR) are kept, separated by a comma, JSON valid (ev/head-merge-cc.txt).
- custom_components/ differs between c671154 and the head only through main's own merged changes: the PR adds none against its merge base (three-dot diff origin/main...head over custom_components/ is empty, checked). No wider review.
- Merges with origin/main: git merge-tree --write-tree exits 0 (ev/merge-tree.txt).
- CI at this head: `merge_train.py classify` prints "GREEN 36c7b25f9b5fab1e9496dee7814160de37bf8461 pending: none red: none" (ev/classify.txt).
- Not re-derived: the previous verdict at c671154342fbb2949fd670d30065a7228e172466 is not on verdict/3351 or any probe/rev-3351 ref I could fetch (only 0149fd19 and a36d0a6e), so I could not list its findings. I judged only the two resolution points and the live checks; main's own changes stand on that verdict.
- carry_audit: no findings recorded.
