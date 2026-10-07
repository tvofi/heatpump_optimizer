Fix review: merge b956925c59005584c8543db2bee5974e5b385c59

bus-nonce: ac6545a1da0c94a74a8a35fcaf5fb508

Reviewer seat r9c-rev-2018, round 3, judging only the delta since 223f88c2. The measured head, b956925c59005584c8543db2bee5974e5b385c59, was still the live head when I posted.

1. **The code delta is only an automatic main merge.**
   - b956925c merges main 17f30f9c into 223f88c2.
   - `git merge-tree --write-tree 223f88c2 17f30f9c` gives tree 0103e142, the head's own tree, so nothing was resolved by hand.
   - The PR's three-dot patch is byte-identical at both heads: `cmp` of `git diff <mb>...<head>` reports PATCH IDENTICAL, with merge bases 38c03d94 and 17f30f9c.
   - The only files the merge adds are main's `tools/pr/prepr.sh` and `dev/programme/delivery/2021.md`.
   - `merge-tree` against current origin/main 45142cc3 exits 0.
2. **`## Red checks` now names both reds.** It lists `closures` (112810272267) and `closures-autofix` (112820973686, `skip-manual-repair-owed`) as inherited from main, citing main's run 112789710707 at 38c03d94 and naming eg_b7_seam_hubs.py.
   - The citations are the round-2 head's jobs, which is correct for when the body was written.
   - At this head the same failure recurs in new jobs: `closures` 112845374722 fails on the identical `INERT READS UNDER-APPROXIMATED: tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py`, and `closures-autofix` 112857546455 reports `AUTOFIX: skip-manual-repair-owed`.
   - The body's statement that #2017 added the file is right: #2017's merge, b281a4c3, brought in 286733c7.
3. **Nothing else regressed.** The commit check-runs endpoint returned HTTP 500 on all 4 pages tried (failure count 4), so I read the Actions jobs API for the head's runs instead.
   - Tests 37636857833: `fast (3.14)` 112845243316 succeeded. stress.py's two pins passed (#1987 and #2018), and the run ended `ALL 106 STRESS CHECKS PASSED`.
   - The only reds are `closures` and `closures-autofix`, both inherited, and `delivery-status` and `nightly-status`, both grading main and both already answered in the body.
   - Every other job succeeded or was skipped.
   - The other workflows succeeded: PR contract (twice), Hassfest, Validate, CodeQL, and Budget raise gate 37636859471. Its cancelled twin, 37636857865, is superseded by that success.
   - The `closures` log at this head shows `done tests/stress.py (exit 0)`.

`closures` stays red until the main repair, #2022, lands; it is not this PR's. The code-owner approval from @tvofi is still owed, as `## Approval` states.
