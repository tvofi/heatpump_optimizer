Fix review: merge baaf0064355bdf4838021df66683584e3d8608c7

bus-nonce: ca0c724d6360d358463a69e02ccdce06

## Round

Fifth round, delta review: the orchestrator ruled past-three. The last blocked head is 0740542f38ffb23e273bf91fd128aa2469d9a120, and the round-4 block named one survivor, `note-replayed`, the class `mutation-vacuous`. The delta to this head is the merge 3b29e4e31 of origin/main ee64358be and the commit baaf00643. That commit adds 8 lines, one self-test arm in `tools/plan/size_durations.py`. `git show --remerge-diff 3b29e4e31` prints no hand resolution. The delta touches nothing under `custom_components/`, so it widens nothing. **The round-4 block is cured.**

## Evidence

- RESULT mutation-proof: the `note-replayed` mutant (`size_durations.run`, `input_note(via, since, len(prs), replayed)` changed to `..., False`) makes the self-test read `1 failed` at this head, on the new arm `run --prs-cache: sizes_provenance ends naming the replay, no read made`. Restored, it reads `0 failed`. The null is the same mutant on 0740542f's file, which reads `0 failed`, so the arm alone kills it. Source: ev/mutants.txt.
- RESULT arm-integrity: I wrote three mutants of my own on the arm. Flipping the expected flag to False: 1 failed. Passing `cache=None`: the raising `rest` read is reached (ZeroDivisionError). Deleting the cache write: ZeroDivisionError. The arm reads the replay path, not a default.
- RESULT diff-mode: `mutant_run.py --diff <merge-base>...HEAD --path tools/plan/size_durations.py --cmd "python3 tools/plan/size_durations.py --self-test"` printed 8 SURVIVED, lines 654, 684, 686, 689, 692, 695, 719 and 729. These match the body's count of 8 and each of its dispositions: the fixture, the `pages[4]` sentinel, four `check(...)` deletions, `gh_raised = True`, and `1 / 0` changed to `2 / 0`. The process was OOM-adjacent during the run, but the output is complete (rc line present). Source: ev/mutant_diff_size_durations.txt. I did not re-run the `replan.py` (11) and `plan_page.py` (3) counts. Neither file changed in the delta: `git diff --stat 0740542f baaf0064` lists only size_durations.py (+8). Those two figures carry from round 4 and were not re-derived here.
- RESULT merge: `git merge-tree --write-tree origin/main baaf0064` (origin/main ceb3070cc) gave rc=0 with no conflict. Source: ev/merge-tree.txt.
- RESULT protected: `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files, `*budgets.json` and `tests/closures.json` show an empty three-dot diff from the merge base.
- RESULT body: `policy_lint.mjs --pr-body` on BODY.md reported 0 errors. The body's `## Head` is baaf0064355bdf4838021df66683584e3d8608c7, the tip I measured.
- RESULT figures: the self-test's `0 failed`/`1 failed` was re-derived. `prepr.sh` (rc=0, `515 passed`) was not re-run, because the gate is CI's heavy run per step 11. It is not verified here, and the train re-proves it.
- CI: no pull request carries this head yet. PR #3428's head is still 0740542f, so this head has no check-runs and no review packet to read. The `owed-reds` set printed `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs`. The body answers `pr-contract` and `tests / fast (3.14)`, which is main's combi census red (#3466). `governance / instrument-self-tests` is main's (R10-HOTFIX-PUSHER-CENSUS) and is outside the owed set. The live checks must be read once #3428 takes this handoff.
- Roster carries and forward-carry: unchanged from round 4, where only `note-replayed` blocked. The body names `none` for forward-carry. The round-4 verdict text was not readable from this seat, so its single-class block is taken from the dispatch brief and the body's `## Re-cut`.
- Role currency: the role pack was rendered at origin/main ceb3070cc.

## Findings

- The handoff body's `## Mutation proof` ends on an unclosed backtick (`all dispositioned in \`## Unpinned sites`). The whole `## Unpinned sites` paragraph is therefore printed twice, once inside `## Mutation proof`. Nothing is lost and the lint passes, but the PR body should be cleaned when #3428 takes the handoff. Carry: dismissed: cosmetic body duplication, no content lost, fixed at the handoff body edit
