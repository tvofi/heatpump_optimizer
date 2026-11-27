Fix review: merge e368e32982dc0f1a0873571682bd77dad241d9ab

bus-nonce: 6231d591686eb2180d8adb520ec713a0

## Scope

- Delta review against the blocked verdict at a36a6a7337 (verdict/3897 e7b4ce97cb). a36a6a73 is an ancestor of the head. The branch-own production patch, three-dot against main before (91f6e91bea) and after (aee9548a47), differs only in coordinator.py and legionella.py (`ev/interdiff_*.txt`); the other six production files' own patches are identical.

## Prior block: resolved

- legionella.py adds `FollowerCycle`: `async_observe` records the reading and clears `followed`; the step tail runs `async_follow`; `_async_update_data`'s `finally` runs `async_follow_missed` under `tail_lock`, which follows only when nothing has followed since the observe. So a cycle that raises before its tail still enforces the boost bound and the disabled-disinfection switch-off, and a cycle that reaches its tail follows once.
- tests/features.py adds four checks that drive `_async_update_data` with `_fetch_tibber_prices` raising: past the bound, disabled, a null control inside the bound, and once per cycle.
- Perturbation (`ev/mutant.diff`, the finally guard set to `if False:`), run with `features_block.py --through` at each tree: head 3 of 4140 failed, mutant 6 of 4140 failed. The three extra failures are the bound, disabled and once-per-cycle checks; the null control passes in both trees (`ev/head_through.txt`, `ev/mut_through.txt`). The three failures common to both trees come from the block runner (pickle, subprocess, sys.path), not from this PR.

## Findings

- Merge f6072bab resolves tests/features.py as the union of both sides' appended blocks, with nothing lost (`ev/f6072bab_remerge.txt`). Carry: dismissed: verified here
- origin/main moved to 43ec8e3273 during this review, and `git merge-tree` now conflicts in pump_arbiter.py against f99ae8a4ef (D7-s3-05/D7-s1-03 store deletions) (`ev/merge_tree.txt`). Against aee9548a47 the merge was clean. Any resolution changes the PR's diff, so this verdict does not carry over it, and the resolution needs a delta review. Carry: dismissed: the train's re-merge, then a delta review
- The body's D16-s1-05 departure is still with the orchestrator for a ruling, as at the prior round. Carry: dismissed: routed by the body to the orchestrator's ruling

## Evidence

- CI: `merge_train.py classify` GREEN, nothing pending, nothing red (`ev/classify.txt`). nightly-status is red but is not owed.
- VERSION, manifest, RELEASE_NOTES.md and tests/golden are untouched three-dot (`ev/version_claims_untouched.txt`).
