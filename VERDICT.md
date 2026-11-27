Fix review: merge 86811c25dd0e87528a8e9aaac0d7dda40df70037
bus-nonce: 8865437414d172e09cab9983126fe468

Scope: full (packet names no prior reviewed head). Worktree detached at the head; roles diff against origin/main empty.

Mutation proof (evidence/mutation_86811c25.txt), block `# R11-SEAM-store-p2 (round-11 sweep P1`: unmutated 4/4 pass; boundary call deleted 2/4 fail; `_KINDS["choice"]` reverted to `v in d.choices` 1/4 fail; `_declares_number` choice arm -> False 2/4 fail; `_unflag_numbers` identity 2/4 fail; list walk off 2/4 fail; dict walk off 2/4 fail. No survivor.

Null / base end (evidence/base_store_head_block.txt): the head's block against the merge base's store.py reads 2/4 failed, every loader reading the stored true as 1.0 (`lead_pending: [1.0, 3.0]`).

Finder's harness (evidence/finder_p1_probes_head.txt): `p1_probes.py` reads `store_bool_admitted_as_number=6 of 7` at the head, as the body states. Its arm calls loaders on stub stores past `QuarantiningStore.async_load`. I traced every caller of the six loaders: each is fed by a QuarantiningStore load, the learner snapshot restore included (the `snapshots/#/learners/*` aliases). The finder's payloads, driven through the real load, move from 1.0 to absent (base block above). The harness does not move because the fix sits at the load boundary, which the stubs bypass; that is not a defect in the fix.

Writer side: tests/finite_boundary.py at head, ALL 122 PASSED (evidence/finite_boundary_head.txt): the round-trip of every saver through every loader is unchanged.

Note: red-checks: `gate` 140382618077 is red in duplicate CI run 45959507078 ("run(s) [45959506547] at this head are still being judged; their gate decides"), and that run's `gate` 140409068529 is green. This diff does not cause it, so it is not owed here. Carry: dismissed: duplicate-run deferral by design; the sibling gate at this head is green
Note: red-checks: `tests / nightly-status` is red because main's scheduled nightly 45919083139 failed. The check is not required, and the PR body's `## Red checks: none` does not record it. Carry: dismissed: main's nightly, not this diff; non-required
Note: code: `debugger.accuracy_report` reads the accuracy document raw from disk (`_read_stores`), so the self-test would still show a stored true lead as 1.0 where the live load reads it as absent. Carry: dismissed: the self-test reports the disk document as stored; it writes nothing and feeds no plan
