Fix review: merge 47d48472d4e348c5076831984691e3a122944e5e

bus-nonce: 9dde167206ded66bf29a8f6a758b32b4
This is round 2. I measured 47d48472d4e348c5076831984691e3a122944e5e, the head after code head 85d8301e plus two main merges, and re-read the live head before posting; it has not moved. Evidence: /Users/timmalmstrom/hpo-seats/review-2057/ev2

## The round-1 block is resolved
- **Refusal probe** (refusal_probe.txt, my own probe, run through the real check()):
  - canonical text (null control): rc=0
  - unsorted inert list: rc=1
  - {seconds, rc} entry: rc=1
  - top-level keys unsorted: rc=1
  - indent=2: rc=1
- **Mutation:** with the byte comparison replaced by `if False:`, exactly the three new pins FAIL (3 of 56; mutant_textcheck.txt). Unmutated: ALL 56 PASSED, and ledger_merge --self-test prints all passed.
- **The old writer after this lands** (oldwriter_probe_r2.txt): I ran the merge-base closure.py, which closures-autofix pins through base.sha, on the head's table.
  - It writes {seconds, rc}.
  - The head check refuses it: rc=1, `under_scoped_in_output=False`, and the output names `closure.py canonical`. Because the refusal is not UNDER-SCOPED, the autofix does not re-trigger on it.
  - `canonical` repairs it with content_equal=True.
- **Main protection:** `closures` is a required context on main (ruleset 23698884, 17 contexts; rules_main.json). A branch carrying that text cannot merge green, and a push to main forces FULL. So main cannot be left red for good: a one-commit repair exists. Ruleset 22628467 now holds only deletion and non_fast_forward.

## Merges
f4db93853 and 47d48472d are each tree-identical to the automatic `git merge-tree` result, run with the claimnotes and ledgermerge drivers configured (merges_by_hand.txt). Nothing was resolved by hand.

## Body figures, re-derived
- My replay at 816547ef (replay.py, carried from round 1) printed RESULT pairs=420 T0=70 NOSEC=14 PR=16 seconds_rewrites_as_written=72 under_band=12. That matches the body's 16/420 and 12 of 72, and the code comment's "60 of 72" agrees.
- The harness at today's main printed 506/87/17, matching the body.
- Transition: the four PRs conflict once against main+2057 under git's default merge, and `--resolve` returns rc=0 with no entry lost (transition_resolve.txt). This matches the body.
- The 2x band: the body and code comment now name sweep order, budget_seconds and driver_timeout (TIMEOUT_SCALE 3). That is correct.

## CI at 47d48472d4e348c5076831984691e3a122944e5e
40 runs: 24 success, 14 skipped, 2 failure (checkruns_47d48472.tsv). `closures`, `closure-scope` and `mutation` succeeded, and closures-autofix was skipped. The two reds are delivery-status (113339431081) and nightly-status (113339428674). Both grade main, the diff does not reach what they read, and the body names and answers both. The body's job ids are from af9936d8; the cause is unchanged.

## Notes (not blocking)
- The body says the 16/420 command is in study/. synth.py there has no PR-writer arm and no new file was added, so that command is not reproducible from the cited path. The figure itself is verified independently by my replay.py.
- In the selftest, the {seconds, rc} variant also lacks the trailing newline, so it differs from canonical on two axes. The same pin carries a no-op `.replace('"_comment"', '"_comment"')`.
