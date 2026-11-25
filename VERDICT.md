Fix review: merge 2ac9d407611e19e4a3101c2aca71cd0ff31626d8

bus-nonce: cf0ff600bdcc95a0c05e22f33f5164a3

## Summary

Round 3, a delta round over the reviewed head 0812e8b2e4dfad56459eb2b11eca80de9f98c673. I measured head 2ac9d407611e19e4a3101c2aca71cd0ff31626d8, which is the head the body names. The delta `git diff 0812e8b2e4 2ac9d40761` touches only `tools/audit/seat/corpus_mirror.py` (15 lines added, 3 removed). It has no `custom_components/` line, so nothing widens the scope (fix-review.md step 12).

Both survivors from the previous verdict are now killed:
- The keep side of `s3`'s stale-file removal is pinned by a new case on the pause-then-resume run: `partition keep: ...`. The case checks that the 3 files held at the pause are byte-identical after the resume and that the directory's stems equal the cursor's batch keys.
- `observe`'s first cost no longer has a default to mutate: `max(seen["max"], cost) if "max" in seen else cost`. It is pinned by observing `92, 30`, so the first answer is the largest.

Python parses the rewritten tuple assignment as `cost, (max(...) if ... else cost)`, the intended reading. It behaves the same as before for every non-negative cost.

## Findings

- Follow-up: none. Both findings of the previous verdict are resolved at this head (see Evidence), and the delta raises nothing new. Carry: dismissed: no finding outside those this PR settles

## Evidence

- Setup: `cloud-setup.sh --check` printed OK. I read the role pack from main. The review packet rendered with no refusals and no advisories, and its carry_audit printed `1 routed, 0 unrouted`.
- Merge: `git merge-tree --write-tree origin/main 2ac9d40761` exited rc 0 with no conflict (ev/merge-tree.txt).
- Self-test at the head (ev/selftest-head.txt): `corpus_mirror self-test: ok (with mutants)`, rc 0. It printed 138 `ok` lines, 74 of them `ok   mutant killed`, and no FAIL. This matches the body's 138/74. The new in-tree mutants `partition keeps current` and `first cost is a max` are each killed, and the re-anchored `largest cost kept` is also killed.
- My own mutants, run with `--self-test --no-mutants` on a copy at the head (driver ev/reviewer-mutant-driver.py, output ev/reviewer-mutants.txt):
  - The previous round's `if stale.stem not in batches:` -> `if True:` is KILLED by `partition keep`.
  - The inverted predicate `if stale.stem in batches:` is KILLED by both `partition keep` and `partition files`.
  - `max(seen["max"], cost)` -> `seen["max"]` (the new cost ignored) is KILLED by `graphql cost`.
- Figures re-derived at the head (ev/figures.txt):
  - The formula costs print `[(1, 3), (30, 92), (32, 99), (33, 102), (50, 154)]`.
  - The ITEM_FIELDS diff count is 0.
  - The scoped gate prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
  - `structure.py` prints `STRUCTURE RATCHET PASSED`.
  - Not re-derived: the issue/PR search counts (1082 and 2785), the wall-time arithmetic built on them, and the body's scratch-driver outputs, which are not in the tree. My driver above covers the same mutants.
- Untouched: the PR diff names only `tools/audit/seat/corpus_mirror.py`, its instruments guide and `dev/programme/delivery/3868.md`. It leaves `VERSION`, the manifest version, `RELEASE_NOTES.md`, `tests/golden/` and both claim files alone.
- CI: `merge_train.py classify 2ac9d40761 --pr 3868` printed `GREEN 2ac9d407611e19e4a3101c2aca71cd0ff31626d8 pending: none red: none`, rc 0 (ev/classify.log). No required check is red, so no `## Red checks` answer is owed (ev/owed-reds.txt).
- Finder's harness: none is named. The harness is the self-test's stubbed GitHub, as in round 2. The class is one seam, so no enumeration rule is owed.
- Forward-carry: the body states none, and the delta changes no later stage's brief.
