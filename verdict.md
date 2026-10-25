Fix review: merge 9442cb4ea930560bb6442d8f9f07ef80e1e7c4e8

bus-nonce: 413768281969f8f7a1e33e24dce99af7

Round 2 of the fix review of #2812 (round 1 was verdict/2812 72e78a51 at 09ed5f73f, blocked pin-wrong). Measured head `9442cb4ea930560bb6442d8f9f07ef80e1e7c4e8`. origin/main is `bc52ad2af1d0cfe95896119b649fa56e14c74b5b`, which is also the merge base. The role contract is current: `git diff bc52ad2af...origin/main -- dev/governance/roles/` is empty. Scope follows the brief: the round-1 content was checked only for being unchanged.

## Findings

- R10-HOUSE-GRADE's brief does not yet hold P122's design-point carry. P122 (dev/programme/triage/s6-batch24.md on #2813's branch, `ac6c53581`) says the roster entry "should hold" it "if its brief lacks it", and the brief lacks it: DESIGN NOTE FIRST, the five controls, and "do not tune the grade to hide" the learned scale of 2.09 (L1). The brief also still says a 100-year-old renovated house "should score at least 30-40". The owner's later clarification on #2816 (carried here as 09662b3f1) puts that same house, at about 1.5x typical pre-1960 loss, "below typical", meaning "low but clearly nonzero", with typical at mid-scale. These agree only if mid-scale sits above 40, and the fixer has to settle that in the design note. Nothing on #2812 depends on it, because the group is not-started and P122 is not on main yet. Once #2813 merges, the roster seat owes an append-carry of P122's text, plus a note that the owner's #2816 spec decides where 30-40 sits. Carry: R10-HOUSE-GRADE

## Evidence

- (1) Re-pins, checked against coordinator.py at the merge base bc52ad2af (`ev/coordinator-pins.txt`):
  - R10-LEARNER-DEFAULT cites `coordinator.py:6664-6673`. Those lines are inside `_learning_frozen` (def 6610): the `reading.entity_id` comment ("must NOT freeze learning") and the `reading.entity_id and not reading.ok` guard. The brief's only change against main is that token (6552-6559 -> 6664-6673). The stale 1113-1119 is gone.
  - R10-IMMERSION-LATCH cites `coordinator.py:10201-10214`. Those lines run from `immersion_excess = 0.0` through `metered = energy - immersion_excess`, inside `_accumulate_energy` (def 10105).
  - Its other pin, 8838-8895, is `_detect_immersion` (def 8838, last line 8895). `IMMERSION_FACTOR` is at const.py:1144.
  - Against main, the brief changes only those two range tokens.
- (2) Merge commit 20e9f0219 (parents 159d163e5 and bc52ad2af):
  - An automatic `git merge-tree` of those parents conflicts on the roster, so the conflict was resolved by hand.
  - I re-derived the three-way result group by group (`ev/merge-resolution.txt`). Only R10-UX-HEALTH.carry was changed on both sides. Main inserted the R10-LEARNER-ETA carry at index 9, ahead of demand-overbook. Head keeps main's 11 carries as an exact prefix, with LEARNER-ETA at 9 and demand-overbook at 10, then the branch's three new carries (#2809, #2815, owner's spec).
  - Across every group, each list field in main is a prefix of the head's. Group order is preserved, and no top-level key changed (`ev/figures.txt`, `ev/cmp.py`, which I wrote for this check).
  - `git diff bc52ad2af 9442cb4` touches only `dev/programme/delivery/2812.md` (+1) and `dev/programme/rosters/wave-r10-groups.json` (+91 -20). No content from main is reverted.
  - `git diff 20e9f0219 9442cb4` is the delivery row only.
- (3) Owner-spec carries:
  - R10-HOUSE-GRADE has two owner-spec carries plus one hover-explanation carry. The first two match the owner's two comments on #2816 (2026-10-25, the grade spec and the reason codes).
  - R10-COP-GATE's reason-code carry matches the second #2816 comment ("the heat-pump grade gets the same treatment, including reasons while it has no grade yet").
  - Not re-derived: I found no public source for the R10-UX-HEALTH "Owner's spec" carry or for the two "hover also explains the metric" carries. They are relayed by the coordinator, and I checked them only against the batch's own commits.
  - Destinations: R10-COP-GATE and R10-UX-HEALTH are not-started and not absorbed on origin/main. R10-HOUSE-GRADE does not exist on origin/main because this PR creates it (9d984a63b). At the head it is not-started, has issue #2816 wired, comes after R10-PARAMS-OWNER (not-started), and is confirmed by P122 on #2813.
- (4) Commits: `git log --no-merges --reverse origin/main..20e9f0219 -- dev/programme/rosters/` gives 27 commits. They match the body's Figures list line for line and in order (`ev/roster-commits.txt`). Including merges, `origin/main..9442cb4 -- wave-r10-groups.json` gives 28, which is the 27 plus 20e9f0219. The PR has 31 commits in all.
- Body figures re-derived: blob hashes match (main d3b890726e4c, head b7f33d15eed0). Groups go from 189 to 190, with R10-HOUSE-GRADE new and none removed. The 13 changed groups and the stage counts both match the body exactly (done 117->120, in-progress 10->7, not-started 47->48). The body names the head SHA 9442cb4 that I measured.
- Roster lint: `node tools/policy/brief_lint.mjs` at the head prints `TOTAL: 0 error(s) across 48 file(s)` and exits 0 (`ev/brief-lint.txt`). The `ok: N error(s)` lines come from its fixture self-tests, not from the roster. `.claude/workflows/brief_lint.mjs` is absent, so this is the script roster_edit.py's gate runs, at origin/main, which is the merge base.
- Merge: `git merge-tree --write-tree origin/main 9442cb4` exits 0 with tree caec96668 (`ev/merge-tree.txt`). It also merges cleanly onto #2813's head ac6c53581 (exit 0, tree 0d61d2d5, `ev/merge-tree-with-2813.txt`), because #2813 touches only its triage file and its delivery row. The body's merge order (after #2813) holds.
- CI on 9442cb4, read from check-runs: 43 runs and none red. Every concluded run succeeded or was skipped. `governance / instrument-self-tests` and one `prelude` were still in progress when read. Step 11 owes nothing.
- VERSION, the manifest and RELEASE_NOTES.md are untouched. Mutation proof and null control are n/a: the PR changes roster state only.
