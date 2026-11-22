Fix review: merge 507e2f8740268f926bb755459f7c300b8db7512d

bus-nonce: 777f005e6551ea7597c9245675c3de96
pending-ci: gate

## Scope

Round: first review at this head. The packet reads `Review scope: full` (the earlier reviewed head 70c8c8c5 is not an ancestor of this head, so no delta round applies). The diff is record-class: 24 files, all `dev/programme/delivery/<N>.md` one-line row files; no production, test, instrument or policy path changes.

## Evidence

- RESULT paths: `git diff --name-only e3cb5c0...507e2f87` names only `dev/programme/delivery/*.md` (24 files, +24 -20); `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched (step 5).
- RESULT rows: every one of the 23 `merged` rows names a SHA that is a first-parent merge commit of that same PR on origin/main and an ancestor of it (ev/rows.txt); the 24th row is #3844's own `open` row.
- RESULT figure: `python3 tests/delivery_status.py` at the head prints `DELIVERY STATUS OK — 24 rowed, 0 pending, 0 overdue`, rc 0 (ev/delivery_status.txt); it matches the body's one figure, which names its instrument rather than a number.
- RESULT head: the body's `## Head` is 507e2f8740268f926bb755459f7c300b8db7512d, the head reviewed (step 7).
- RESULT merge: `git merge-tree --write-tree origin/main 507e2f87…` exits 0 with no conflict (ev/merge-tree.txt); merge base is origin/main e3cb5c0.
- Mutation proof (step 1): n/a, as the body states; the diff writes no production, test or check code line, so there is nothing to mutate. Steps 2, 3, 4, 6, 9, 14, 15, 16 have no object here: there is no finder's harness, no quantified production claim, no claim-file or golden change, no budget or instrument figure moved, and no actuator path.
- Policy currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- CI: `merge_train.py classify 507e2f8740268f926bb755459f7c300b8db7512d --pr 3844` read `WAIT ... pending: gate red: none` (rc 3) on every run from 20:45:16 to 21:16:29 UTC (ev/classify-poll.txt), so the verdict carries `pending-ci: gate`. The live check-runs listing shows a `gate` run that concluded failure at 20:23:54, before `tests / lane-proofs` (still queued) had finished; classify reads it as pending, not red. Every other completed check at this head is success or skipped. No owed red is answered here because classify reports none (`red: none`).
