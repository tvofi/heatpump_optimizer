Fix review: blocked aa1bb8d34c5700351a164e3aaf56be65165236d6 class-open: accuracy accuracy/lead_pending/#/1 (a choice declaration of numbers, LEAD_BUCKETS) admits a stored true as lead 1.0
bus-nonce: 1b9e4b741669372e02a8719fec4104db

Round 1 (full review, no --reviewed-head), measured at aa1bb8d34c5700351a164e3aaf56be65165236d6 from a detached worktree. Roles diff merge-base...origin/main is empty, so this contract is current.

RESULT features_block_head=4 of 4 passed (ev/head_block.txt)
RESULT mutation_delete_unflag=2 of 4 failed (ev/mutant_delete_unflag.txt), the census listing 202 numeric declarations kept true and 0 flags lost
RESULT stored_true_at_numeric_choice_admitted=1 of 1 at the head (ev/probe_choice_head.txt)
RESULT merge_tree_vs_origin_main=clean (rc 0)
RESULT version_manifest_notes_golden_touched=0

## Blocking

- class-open: the PR's enumeration rule (the census in tests/features.py) reads only declarations of kind `real`/`int`. `store.DOMAINS["accuracy"]["accuracy/lead_pending/#/1"]` is `Domain("choice", choices=LEAD_BUCKETS)`, a choice whose members are all numbers (1.0, 3.0, 6.0, 12.0, 24.0). A stored `true` there is still a flag where a number is declared. At the head, `QuarantiningStore.async_load` returns it unchanged. `in_domain` admits it because `True in (1.0, ...)` is true, which contradicts the docstring's statement that `in_domain` refuses one. `AccuracyTracker.from_dict` then loads it as `(when, 1.0, 2.0)`, so a 1-hour lead that nobody predicted joins `lead_pending`. This is a store loader of the P1 class, one of the six named stores (accuracy). None of the body's census residue categories (map key, alias, never-stored payload) holds it. The probe that reproduces this is ev/probe_choice.py. It is the only numeric choice declaration in DOMAINS: the kind census counts 18 choice declarations and 1 with numeric choices.
  Suggested fix: in `_unflag_numbers`, also treat a `choice` whose `choices` are all non-bool numbers as numeric (or make `_KINDS["choice"]` refuse a bool against non-bool choices). Then widen the census to drive that declaration and the docstring claim along with it.
  Carry: R11-SEAM-store-p2

## Verified

- Mutation proof: deleting `data = _unflag_numbers(data, node)` fails both P1 checks. The six-loader check reads 1.0 at every loader, and the census check lists every numeric declaration kept as true. Restored afterwards.
- Null control holds at the head: the numbers stored beside each true (4.0, 20.5, 2.0, 3.0) load as stored, and all 23 flag declarations load true.
- Other stores: every store in custom_components goes through QuarantiningStore (LedgerStore included). No plain `Store(` is constructed outside store.py, so no other store bypasses the boundary.
- Loader tolerance of None at a numeric leaf is the precedent `_sanitize` already set for poisoned leaves, so reading a flag as None adds no new loader state.
- Live checks at the head: every check except tests / nightly-status (not required) is success or skipped. The two earlier `gate` failures (runs 45937149839, 45934499708) are superseded by the success at 05:53Z (job 140334664392).
- VERSION, manifest, RELEASE_NOTES.md and tests/golden are untouched (three-dot).

## Not verified

- The $EXPORT companions (p1_e2e.py, p2_companion.py) and d3_fnstate.py are out-of-tree. I did not re-run them. I relied on the features block and the in-tree census for carry 0, and I did not re-measure carry 1's P2 evidence.
- Finder's harness: the packet names none. The in-tree p1_probes.py store arm, by the body's own account, calls loaders past the load boundary, so it cannot move under this fix. I did not run it.

Note: perf: `_tries()` (uncached) now runs on every load, including stores with `lead=None`. Each load builds the trie and walks the document one more time. This is acceptable at the load cadence, but caching `_tries()` would remove the rebuild.
