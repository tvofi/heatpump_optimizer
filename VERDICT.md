Fix review: merge e8e8615d8a3f1d5d829b2d290f33c61539d887a7

VERDICT: MERGE. Round 1.

Head measured: e8e8615d8a3f1d5d829b2d290f33c61539d887a7 (authored code head
fdb05e622648e0d0ade13bd7521934b67b3813cf plus the PR's own delivery row).
`git ls-remote origin refs/heads/fix/r9-closures-inert-prestudy` at publish
time is still e8e8615d8a3f1d5d829b2d290f33c61539d887a7.

RESULT diff-exactly-one-line: PASS — three-dot diff
$(git merge-base origin/main HEAD)...HEAD is 2 files, 2 insertions:
dev/programme/delivery/2125.md (the PR's own delivery row, new file) and
one line in tests/closures.json, inserted in inert_reads'
tests/harness_headers.py entry between "round9/fixplan/gen.py" and
"round9/rca/1747/b8_replan_blocked.py" — fixplan/ < prestudy/ < rca/, the
entry's existing ASCII sort order. No other entry touched.

RESULT line-is-CI's-named-path-and-file-parses: PASS — the added line is
character-for-character "dev/audit/rounds/round9/prestudy/boost_drift_refit.py",
the path CI's defect line named. python3 -I json.load() parses;
inert_reads['tests/harness_headers.py'] holds 541 paths, added path present,
list still fully sorted (ir == sorted(ir)).

RESULT ci-closures-at-head: PASS — the `closures` check-run at
e8e8615d8a3f1d5d829b2d290f33c61539d887a7 concluded SUCCESS (completed
2026-10-10T18:27:39Z; job 114276979238 in run 38073939251: "Re-record the
closures" then "Fail if tests/closures.json under-approximates" both passed).
That is the verification: CI's own Linux strace re-derive. No local re-derive
attempted (forbidden off Linux). Every other check at this head is green,
skipped or neutral; nothing red.

RESULT body-names-red-and-answers: PASS — the body quotes CI's
`INERT READS UNDER-APPROXIMATED` output verbatim including the named pair
`tests/harness_headers.py:
dev/audit/rounds/round9/prestudy/boost_drift_refit.py`, and `## Red checks`
answers it by CI's re-run at this head. Truthful against the check-runs API:
the only red in play is main's closures at 969c3a5c8; no gate check at this
PR's heads went red unanswered.

Other contract checks, briefly:
- No mutation proof owed: no production line added or deleted; the row's
  absence is precisely main's current red state (contract 1's null-mutant
  is already demonstrated by main).
- VERSION, manifest version, RELEASE_NOTES.md heading untouched (contract 5).
- Contract 14 (numbers earned, not gamed): the moved number is the inert_reads
  entry; CI's under-approximation failure at main and success here is the
  mechanism named, run in both directions — the movement is earned.

bus-nonce: 0a44033b89ec1db49543750ec0a05861
