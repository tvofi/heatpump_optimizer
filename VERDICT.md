Fix review: merge 3235ba4fd02cdce9560ea321751c59eae6a7eed4
bus-nonce: b18c31981de59c52f52919f6d0d2f561

# Fix review -- PR #2876, R10-HOUSE-GRADE, merge-delta review (round 5)

Reviewed head: `3235ba4fd02cdce9560ea321751c59eae6a7eed4` (GitHub's `headRefOid`
matched it when the review began and again before publishing). Worktree: a
detached worktree at that head under `~/hpo-seats/r10s6/rev-prod-s8/2876/`. I
did not push the branch, edit the fixer's worktree or the main checkout.

This is the fifth review of this pull request. The fourth (`verdict/2876`,
`Fix review: merge 9513b571420de2740607e12847adcf047ec94b1b`, nonce `dff02402`)
judged the fix. Per `fix-review.md` step 12 a main merge after a `merge`
verdict returns as its resolution delta, which alone this review judges.

## What moved since 9513b571

`git log --first-parent 9513b571..3235ba4fd`: three merge commits and nothing
authored.

- `179572ef5` = `9513b571` + main `e8cb7e683` (the v7.0.5 stamp). With the
  `claimnotes` driver installed, `git merge-tree --write-tree 9513b571 e8cb7e683`
  prints `MERGE-CLAIM: refused` for **both** claim files (the stamp emptied
  main's lists; the branch's list carried them) and `LEDGER-MERGE: resolved
  tests/closures.json`. The committed tree differs from the driver's output in
  `tests/golden/claimed_drift.txt` alone: the hand resolution deletes the
  conflict markers and main's stamped-out `config_flow` line (a line of the
  old merge base, not of this branch) and keeps the branch's R10-HOUSE-GRADE
  block. `card_claimed_drift.txt` equals the driver's output.
- `d857e54a7` = `9513b571` + `179572ef5`: tree identical to `179572ef5`.
- `3235ba4fd` = `d857e54a7` + main `07295d4ea` (`ci: record nightly kills`):
  tree identical to the driver merge.
- `git merge-tree --write-tree origin/main 3235ba4fd`: rc 0, no conflict.

## Merge-delta checks (RESULT lines)

- RESULT three-dot content: the added/removed lines of `git diff
  $(git merge-base 9513b571 origin/main) 9513b571` and of `git diff
  origin/main...3235ba4fd` are identical (0 differing lines; 26 files, 550
  insertions, 169 deletions on both). Only hunk offsets and context moved, so
  the reviewed fix is byte-identical on the new base.
- RESULT claim files = main + this branch's block: the merge base is
  `origin/main` itself (`07295d4ea`), and the three-dot diff of each claim file
  is a pure append. `claimed_drift.txt` adds the R10-HOUSE-GRADE note and five
  bare claims: `coord_all_features`, `coord_dhw`, `coord_grid_fee`,
  `coord_minimal`, `coord_two_zone`. `card_claimed_drift.txt` adds the note and
  `score_open`. Nothing else is touched.
- RESULT claims-for: `VERSION` 7.0.5; `# claims-for: 7.0.5` in both files.
  `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- RESULT `python3 tests/env_drift.py --claims-only 07295d4ea`: `claims
  hygiene: ... ok`.
- RESULT `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 07295d4ea`
  (6 min here): rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE:
  56 committed fixture(s)`. Each of the five coord fixtures reads `CLAIMED ... 2
  leaves moved`, the two `envelope_drivers` leaves, each "present on one side
  only". Every claim moved, and every moved fixture is claimed.
- RESULT review packet (`review_packet.py render` at this head): Refusals
  none, Advisories none, `CARRY-AUDIT: 1 finding item(s): 1 routed`,
  `FIGURES: 9 resolved, 4 not verified, 0 refused`. The mutation-ledger diff is
  the branch's own pins (envelope_score/presets), unchanged by the merges.
- RESULT CI watch item: `tests/mutation_ledger/killed_by/coordinator.py/@module.CONST.6b93afbe.json`
  came in with main's `07295d4ea`. Its `old` line `BUFFER_AMBIENT_TEMP = 20.0`
  is at `coordinator.py:1413` at this head, and the branch's coordinator diff
  writes no module constant, so the merge leaves the anchor live.
- RESULT live checks at this head: every check concluded success or skipped except `prelude` (in progress); `tests / mutation` job 122582935144 ends `MUTATION TABLE PASSED`, `tests / fast (3.14)`, `tests / closures` and `pr-contract` success (`ev/checks-at-3235ba4fd02cdce9560ea321751c59eae6a7eed4.txt`), re-read
  just before publishing.

## Findings

- None blocking. The hand resolution of the stamp merge's refused claim files
  is correct: it keeps exactly the branch's own block and main's emptied list,
  and env_drift reads every claim moved and every move claimed. Carry: dismissed: merge-delta verified clean, nothing changes a later stage

Evidence: `ev/` (each file names the head `3235ba4fd02cdce9560ea321751c59eae6a7eed4`).
