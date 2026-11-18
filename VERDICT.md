Fix review: merge bdc3a77df7fea249cecf09581813d3726ea3d070

bus-nonce: fd448d860136ed87902d9014d1adefff

Round 1, first-round full review of the three-dot diff at `bdc3a77df7fea249cecf09581813d3726ea3d070` (merge base `83b9012d61eb9dba11c265cf987dd1d5960c8c96`). The role contract is current (`git diff <mb>...origin/main -- dev/governance/roles/` is empty).

## Findings

- Note: body-claim: the body says `_settled_space` is "the name the merged code uses". No `custom_components/` file at this head, at origin/main or at #3709's head (`c5111367a9`) defines `_settled_space`, `_settled` or `_held_round`; only #3529's own head `1f9daef4d9` does (`optimizer.py:370`, `:1673`). The renamed design-note paragraph describes the combi hold and settle that the body assigns to group B, and #3709 builds neither name yet. Group B either lands those names or edits the note's Combi store paragraph and the Solve-time sentence to match what it builds (ev/checks.txt). This is a doc file outside `custom_components/`, so it does not block. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Evidence

- Diff: `dev/programme/delivery/3717.md` +1, and `docs/design/2026-11-12-honest-starts-and-runs/design.md` 2/2, one identifier changed twice. No `custom_components/`, test, budget, closure or claim-file line differs from the merge base.
- Mutation proof (step 1): not applicable. No production line differs, so there is no site to mutate. The CI `tests / mutation` check is success at the head.
- Finder's harness and null control (steps 2, 3, 9): none named. That fits a doc-only diff, because the unmodified tree is main.
- Claims (step 4): no golden fixture or claim file is in the diff, and no code changed, so nothing drifts.
- VERSION, manifest and notes heading (step 5): untouched, with 0 diff lines (ev/checks.txt).
- Body figure re-derived (step 8): `git diff --stat 7c2f4c30ca 345d32d62de2677080b66c8035540c09e5d7d3d9` prints 1 file changed, 2 insertions(+), 2 deletions(-), as stated.
- Head (steps 7, 12): the body names `bdc3a77df7fea249cecf09581813d3726ea3d070`, which is the PR head I measured.
- Merge with main (step 13): `git merge-tree --write-tree origin/main bdc3a77df7fea249cecf09581813d3726ea3d070` exits 0, tree `1c8491dd5b`, with no conflict.
- CI: `merge_train.py classify bdc3a77df7fea249cecf09581813d3726ea3d070 --pr 3717` prints `GREEN bdc3a77df7fea249cecf09581813d3726ea3d070 pending: none red: none` with exit 0 (ev/classify.txt).
- Red checks (step 11): `tests / nightly-status` is red at the head and is not in `merge_train.py owed-reds` (ev/owed-reds.txt), so no answer is owed. The body answers the reds from #3529's branch history anyway.
- Class (step 6), metrics (step 14), architecture (step 15), actuator refusal (step 16): not applicable, because the diff carries no code, budget or instrument movement.
