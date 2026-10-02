Fix review: blocked b74fc1aa21e443fef353a5bb49ea630397bf2913 root-cause-unanswered: nightly-status went red, unanswered (the body's `## Red checks` no longer names it, pr-contract 111063804675 refuses, and the dispatch the earlier answer cited, 37050037132, concluded failure)

bus-nonce: 08d7a18b43dc11832275448a0b9a699e

Round 4, the hand-resolution delta. PR #1851 (R9-EG-A1), head b74fc1aa21e443fef353a5bb49ea630397bf2913 = merge(25f434a6, origin/main 03ba7f70f). Evidence: evidence/ (HEAD.txt names the head). The resolution is correct. The block is the body alone.

## The resolution: correct

Recomputing the merge gives a conflict only in tests/deployment_shape.py. The claimnotes/ledger driver resolved tests/closures.json (`LEDGER-MERGE: resolved`). The head differs from the automatic merge tree e66bbf20 in exactly two files (resolution-diff.txt):

1. tests/deployment_shape.py, the conflict. The resolution keeps main's history clause ("86 until ... payload.py, 85 until ... dhw_planner.py", 87 files) together with the PR's arch_score_head.py exception. The pair figures read 90 of 435 and 325. No conflict marker remains.
   - RESULT the #1218 probe (d308_probe.py, mine) at head: both checks ok. With a third full-coverage closure injected: FAIL, so a third is still refused.
   - RESULT the full `tests/entities.py` at head under the seat venv: ALL 2081 ENTITY CHECKS PASSED, rc=0.
2. tests/closures.json, beyond the driver's merge. The resolution adds dhw_planner.py and payload.py to arch_score_head.py's closure, and its seconds go 10.0 to 33.6.
   - RESULT the closure has 107 files and covers all 87 tracked production files.
   - RESULT CI `closures` succeeds (111049946493), so Linux agrees with the --single re-record. `closure-scope` also succeeds.

Item 3: RESULT tools/audit/round4/D6/claims.json and claims.md at head are byte-identical to origin/main (03ba7f70f). They are not in the PR's diff any more.

Item 4, arch_score.py not re-run. The argument holds:
- RESULT `closure.py select --diff 25f434a6`: "SKIP tests/arch_score.py (closure: 89 files, no changed file is in its measured closure)". "RUN tests/arch_score_head.py (its closures.json entry changed)".
- RESULT none of the 73 files changed by the merge is in arch_score.py's closure. That closure includes tests/structure.py since round 2.
- CI's fast (3.14) at head is a success (111049854683).

Item 5: RESULT the PR's own diff (merge-base..head, per-file patch-id) is unchanged from 25f434a6 except tests/closures.json and tests/deployment_shape.py, both above. There are 94 files at both heads. VERSION, the manifest and the notes are untouched by the PR (v6.7.14 is main's stamp). merge-tree against origin/main exits 0.

## Blocking: nightly-status is red, and the body does not answer it

RESULT check-runs at b74fc1aa: everything is success, skipped or neutral except:
- nightly-status: failure (111049854457). It is no longer NIGHTLY ABSENT. It now reads: "NIGHTLY FAILED: mutation-ledger-push, mutation-nightly failed in the last verification dispatch", run 37050037132 (main aa7a811), conclusion 'failure'.
- pr-contract: failure (111063804675, 22:59Z). "check `nightly-status` is red and `## Red checks` does not name it ... this diff touches what it reads (docs/plan-2026-09-open-issues.md)".

The body re-pushed at 22:08:58Z has only the fast (3.14) entry under `## Red checks`. The nightly-status paragraph accepted at 25f434a6 is gone. That paragraph would also be stale now: the dispatch it cited as the proof concluded in failure.

Owed, as a body edit only: name nightly-status and answer it against the new failure. That means the cause and owner of the mutation-ledger-push / mutation-nightly failures in 37050037132, a concluded green dispatch on main, or the finding that the cause is outside this PR. Separately, `## Head` reads "merges the authored code head b74fc1aa... and then merges origin/main", which names the head as its own parent; the authored head is 25f434a6. If the code head stays b74fc1aa, every RESULT above carries.
