Fix review: merge 851237fcb9d3bb41b67e94a460323fd6d1f1e4f1

PR #1837, R9-F10.9d, round 2. Round 1 blocked 39fda423 on mutation (C1, C3 and C4 survived); that verdict is in F10.9d-review-39fda423.

## What I measured at 851237fc
I measured 851237fc, which is also the PR head and the head named in body 6e0004bf. Main is unchanged at 3bd6f122. The delta from 39fda423 is one entities check plus the PR's own delivery row (e77b1f99). I ran everything on Python 3.13 with requirements-ci and tests/hastub; the script and log are mutc2.py and mutc2.log here.
- RESULT, unmutated: entities.py prints ALL 2055 ENTITY CHECKS PASSED, and structure.py prints STRUCTURE RATCHET PASSED.
- RESULT, mutants:
  - C1 sets _exec_record's audit-hook inert_reads to []. entities rc 1: KILLED.
  - C2 drops the _union_strace union. entities rc 1: KILLED.
  - C3 makes _fold_inert_reads iterate nothing. entities rc 1: KILLED.
  - C4 turns check()'s `if missed:` into `if False:`. entities rc 1: KILLED.
  - C6 drops the --partial merge's fold call. entities rc 1: KILLED.
  - C5 drops the full merge's fold call. It SURVIVES; the body discloses it and gives the reason, since a full merge needs every script's recording. It is backstopped: a full re-derivation without the fold writes an empty inert_reads, and the now-pinned check() refuses that table in the closures job.
- The predicate side is unchanged since round 1, and round 1's findings stand. All six predicate mutants were caught except `f in reads[0]`, which is equivalent and cannot be caught. Re-recording harness_headers.py gives the same five INERT reads. The census re-derives exactly: 0 of 120 ELIGIBLE, and unrecorded falls from 50 to 30 of 50.
- The body's corrected seam account matches what I measured.

## Checks
- Briefs are current against main. merge-tree with origin/main is clean.
- VERSION, the manifest version and the release-notes heading are untouched.
- No claim files changed, and no budget was raised.
- Forward-carry: the HANDOVER "Owed from R9-F10.9d" entry is in the diff.
- Red checks: the body names stress.py (Python 3.11 has no sys.monitoring) and answers it.
- CI at 851237fc when I wrote this: every completed check passed. The Tests workflow (fast, closures, coverage) was not yet listed for this head. Per step 11 I cite CI rather than re-running the gate, so the merge seat merges on that run going green.
