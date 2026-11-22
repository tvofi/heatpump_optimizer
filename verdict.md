Fix review: merge c0c6a9b7c231a95c00ca67062aed0b1da6f20233

bus-nonce: a37b886b456704e614c58bec3b84275f

## Summary
Round 1, full scope. PR #3851 is a Dependabot dependency bump: playwright and playwright-core 1.65.0 -> 1.65.1 (semver patch) in tests/pwlane/package.json and package-lock.json. It writes no production line and no fixture, budget or claim file.
Note: already-merged: origin/main already holds this head, merged as eaaaf24e5becdf9682e961cc3ca33f25df920438 (Merge pull request #3851) before this review ran; the verdict attaches to the reviewed head for the record.

## Evidence
- CI: `merge_train.py classify c0c6a9b7c231a95c00ca67062aed0b1da6f20233 --pr 3851` exit 0: `GREEN c0c6a9b7c231a95c00ca67062aed0b1da6f20233 pending: none red: none` (ev/classify.txt). tests / browser, the lane that installs this package, is success in the packet digest.
- Merge: `git merge-tree --write-tree origin/main c0c6a9b7c231a95c00ca67062aed0b1da6f20233` exit 0, no conflict (ev/merge-tree.txt).
- Diff: two files, 9 insertions and 9 deletions; the lockfile moves version, resolved URL and sha512 integrity together for playwright and playwright-core, consistent with npm ci's integrity check (ev/diff.txt).
- Step 1 (mutation): there is no production line to delete. A change to dependency metadata alone generates no mutant, so the mutation check does not apply here.
- Steps 2-3, 6, 8-9: no finding, harness, null control or quantified claim is made.
- Step 4: no golden or claim file in the diff.
- Step 5: VERSION, the manifest and RELEASE_NOTES.md untouched (empty diff).
- Steps 11 and 14: no red; no budget, closures.json or INERT entry moved. Both pwlane files were already classified: package.json in tests/closure.py, package-lock.json in tests/closures.json.
- Role contract current: the three-dot diff of dev/governance/roles/ against origin/main is empty.
- Comms: the stored prompt named COMMS.md at 6c17b87e; that commit holds ADDENDUM.md and seat_comms.sh, and this seat followed ADDENDUM.md.
