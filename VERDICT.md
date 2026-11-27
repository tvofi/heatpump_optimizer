Fix review: merge 88da7f9bc11961a25be34db44d990efa7383ce9c
bus-nonce: 02dbcc149a5062483eb300d7aaac2711

Round 2, delta scope (owner ruling: later rounds review the delta only). Prior verdict: blocked at 21b920ba64892ade1446b8c7e804461cfb12b41b, mutation-vacuous, two survivors. Delta 21b920ba64..88da7f9bc11961a25be34db44d990efa7383ce9c is tools/ci/sweep_selftest.py, +11 lines (two rows); no production change (evidence/delta.txt).
RESULT sweep self-test at head: 147 checks, 0 failed (null control: both new rows pass on unmutated code).
RESULT prior survivor tools/ci/sweep.py:400 (judge's deferred_ids guard): re-applied, now killed by row "W1: a deferred run left while its sources are busy is not re-judged by its gate alone from a green sweep" (evidence/mutants.txt). Resolved.
RESULT prior survivor tools/ci/sweep.py:463 (completion's v status clause): re-applied, now killed by row "W2 completion arm null: a run still in progress is no completion; settle re-runs the red that judged early". Resolved.
RESULT finder's harness: none named in the packet; the delta is test-only, so a reading of dev/audit/harnesses/ci3885_queue.py cannot move against round 1's. Carry: dismissed: evidence, not a finding
RESULT merge-tree origin/main HEAD: rc 0. Live checks: every required check passes; tests / nightly-status red and not required. Carry: dismissed: evidence, not a finding
