Fix review: merge 0149fd1932c4763d2723fb53023b849d0c7fe00e

bus-nonce: d298388eedd210d80c6b4e6087e99ce4

## Evidence
- Round: resolution-delta review against the merge verdict at a36d0a6e56cc5f5af6754a9dec2cd10e41be919d. review_carry.py prints FRESH-REVIEW (e5edce38e is not the automatic merge of its parents), so the delta is mine.
- Resolution delta: merge-tree of the parents 1e87d78d9 and 0a8033305 conflicts only in the generated schema blocks of .claude/workflows/audit-find.js and dev/audit/config/finding.schema.json (bugclasses.json auto-resolved by the ledger driver). The committed resolution differs from the automatic tree only in those two files (ev/resolution-delta.txt), and keeps both N-relay-handoff-starvation (from main) and N-stamp-claim-conflict (from this PR) in CLASS_GUESS and the class_guess enum.
- fold_ledger.py check at the head: 0 violations. agreement_py.py --run: divergent=0 unregistered=0 dead=0 refused=0, AGREEMENT ok.
- The head 0149fd193 differs from e5edce38e only by one line in dev/programme/delivery/3351.md.
- Three-dot diff against the merge base touches no VERSION, manifest, RELEASE_NOTES.md or golden/claim file.
- git merge-tree --write-tree origin/main 0149fd1932c4763d2723fb53023b849d0c7fe00e exits 0 (clean).
- CI: merge_train.py classify at the head exited 0: GREEN pending: none red: none (ev/classify.log, polled 08:43-09:06 UTC). The gate failure in the packet digest at render was a stale in-flight run; the final classification is GREEN, so no red check is owed an answer.
- Not re-run: gate and mutation (CI's heavy runs cited, per the role file). The PR's patch is unchanged from the previously reviewed one apart from the merge-resolved generated blocks.
- Round: first review of this resolution delta.

## Findings
None: the resolution delta settles everything it touches.
