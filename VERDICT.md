Fix review: merge 41d6cdb0d8d19e9d22ffc6171157f56220b159b5
bus-nonce: 0bd396c62b8fb1a1221d7b38d63b9027

Round 1 (first review, full scope), from a detached worktree at 41d6cdb0d8d19e9d22ffc6171157f56220b159b5; merge base 99436a082c.

RESULT diff_new_files=318 count (317 under dev/audit/ plus dev/programme/delivery/3810.md); modified: dev/governance/config/corpus_excluded.json (one entry), tests/closures.json (inert_reads only)
RESULT production_or_version_lines=0 lines (VERSION, manifest, RELEASE_NOTES.md, custom_components/, tests/golden)
RESULT depth_root_seams_head=0 count; at the copy commit 1fd7ed1c81: 3 (the three harnesses the body names); mutant (N-solve-recompute back to here.parents[6]): 1
RESULT sweep_controls=controls OK on N-solve-recompute and N-stale-step-actuation at the head
RESULT merge_tree_origin_main=0 exit (LEDGER-MERGE resolved tests/closures.json)

- Step 1 (mutation): n/a. This record PR has no production line. My mutant is the repo_root repair: undoing it on one harness brings back the depth-seam refusal at that exact site, so the repair is what the check reads.
- Step 2 (finder's harness): none named. The packet says the same. The PR lands evidence and fixes no finding.
- Steps 4-5: neither claim file changed. VERSION, the manifest and the notes heading are untouched.
- Step 11: the reds at c5c0a31a43 were tests / closures (INERT READS UNDER-APPROXIMATED, so UNDER-SCOPED-class, answered by closures-autofix 41d6cdb0d8), pr-contract (answered in the body) and gate (their aggregate). classify --pr reads GREEN at the head.
- Step 13: git merge-tree against origin/main exits 0.
- Step 8: I did not re-derive the body's unmeasuredNamedDocs() 0 vs 1. A local policy_lint.mjs timed out at 300 s on a loaded machine. CI's governance / policy-docs is success at this head.

Note: body: the "## Head" paragraph appears twice, word for word.
