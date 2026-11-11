Fix review: merge a32f2e0bf405e4245c1864c294599c976f90a1cf

bus-nonce: 1a2b691d5b3038f25adea793ebdc82b2
pending-ci: gate

Round: a continuation of the delta round whose merge verdict (commit 4b602a697c1f on probe/rev-3464-b241498e, nonce b241498e) named f0f6b47f2c8f402e6d35b461c06760318576b01a. That verdict stands and none of it is redone. It never posted, so no verdict on verdict/3464 names f0f6b47f and the packet's scope line reads `full`; the scope taken here is fix-review.md step 12's carry instead, because `review_carry.py f0f6b47f2c8f402e6d35b461c06760318576b01a a32f2e0bf405e4245c1864c294599c976f90a1cf` prints `review_carry: CARRY` (`ev/review_carry.txt`).

## Findings

(none. The verdict at f0f6b47f left no open finding, and the merge adds no change of the branch's own.)

## Evidence

- Separation: `git log f0f6b47f..a32f2e0b --not origin/main` returns one commit, a32f2e0bf405 itself, with parents f0f6b47f2c8f and main 046736a49f8c (`ev/review_carry.txt`).
- Automatic merge: `git merge-tree --write-tree f0f6b47f 046736a4` with the tree's ledger driver prints `LEDGER-MERGE: resolved tests/closures.json`, exits 0 and writes tree f3a042e125b8, which is the head's own tree (0 diff lines, `ev/auto_merge.txt`). The head holds no hand resolution.
- Main's own changes: `git diff --stat f0f6b47f a32f2e0b` and `git diff --stat 61afd4f2 046736a4` (merge base to main) list the same 12 files with the same totals (`ev/auto_merge.txt`).
- tests/closures.json is the driver's union (`ev/closures_union.txt`, a reviewer-built set comparison): three list leaves differ, and each at the head equals the set union of the reviewed head's and main's, sorted, with no duplicate. `closures.tests/entities.py` holds 565 entries, the branch's one and main's one over the base. No scalar leaf differs.
- Files both sides touched, `dev/governance/roles/fixer.md` and `tests/entities.py`: the changed lines of the branch's delta are identical before and after the merge, and so are main's (`ev/semantic_merge.txt`, four comparisons, each IDENTICAL).
- `node tools/policy/policy_lint.mjs --budgets` exits 0 at the head in a detached worktree (`ev/semantic_merge.txt`); main's fixer.md edit and the branch's fit the per-file cap together.
- `tests/entities.py` was not run by this seat: the seat's python3 has no `homeassistant` module and the script stops at import (`ev/semantic_merge.txt`). The standing-terms check at this head is CI's `gate` to show, which is the pending context.
- Production code: `git diff --name-only origin/main...a32f2e0b` lists nothing under `custom_components/`, and VERSION, RELEASE_NOTES.md and tests/golden are untouched. Nothing widens the scope.
- Merge with main: `git merge-tree --write-tree origin/main a32f2e0b` at origin/main 046736a49f8c exits 0 (`ev/merge_tree.txt`).
- PR body: its `## Head` section names a32f2e0bf405e4245c1864c294599c976f90a1cf. Its Red checks section answers `budget-raise-gate / budget-raise-gate`, the one failed check run at this head (check run 130863752546, read from the PR's check runs); classify does not count it red.
- Roles: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- CI at this head: `WAIT a32f2e0bf405e4245c1864c294599c976f90a1cf pending: gate red: none` at 2026-11-11T23:45Z and again at publish (`ev/classify.txt`). The runs began at 23:37Z. This seat did not poll for 30 minutes: the continuation brief asks for the pending-ci line when CI is not done, and the relay holds the verdict until `gate` is green.
- Head re-read at publish: origin/fix/r10-standing-contracts-p2 and refs/pull/3464/head are both a32f2e0bf405e4245c1864c294599c976f90a1cf.
