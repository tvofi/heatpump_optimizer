Fix review: merge c3d899e911cec3c4054fcf057362b7e14bc05466

bus-nonce: fa8878c11b4105c38a3166e5a3417c59

Round 1. Record PR (record/autofix, author hpo-author[bot]).

## Head

Measured head c3d899e911cec3c4054fcf057362b7e14bc05466; PR head at post time is the same. Base 8cdb5dd.

## Findings

none

## Evidence

- RESULT files: three-dot diff touches exactly dev/programme/delivery/{3077,3078,3147,3149,3151,3153}.md plus the new 3162.md; no production code, no claim files, no VERSION/manifest/RELEASE_NOTES change.
- Each row is one line anchoring its own PR; state moved open -> merged.
- Merge SHAs verified as real merge commits on origin/main (git log): 3077=432e25c, 3078=8cdb5dd, 3147=3dd3697, 3149=4821660, 3151=94d8b47, 3153=35b7119. Subjects match each merged "Merge pull request #N" commit; main's existing rows for all six were still "open", so none already carried the merged state.
- Phrasing: 3147 and 3153 carry neutral titles without the group suffix; titles match the PRs (3147 title read from the PR).
- python3 tests/delivery_status.py at the head: runs without failure (ev/delivery_status.txt); only pending notices, which that check says block no merge.
- git merge-tree --write-tree origin/main head: exit 0, clean.
- Red checks: whole check-run set at the head has no concluded red check; the body names governance / record, tests / nightly-status and governance / delivery-status as possible reds and answers them.
- CI: merge_train classify -> GREEN c3d899e911cec3c4054fcf057362b7e14bc05466 pending: none red: none (rc 0).
- Mutation proof / null control: n/a, record-only diff.
