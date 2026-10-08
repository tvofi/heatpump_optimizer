Fix review: merge 27fdda2a9445a850ccc988e2085cb1ea23dbcaee

bus-nonce: 775b07c5996eeb23b6d41553f304e761

PR #2049 (R9-CI-1), round 4. Head 27fdda2a9445a850ccc988e2085cb1ea23dbcaee, still the live head at posting (pulls API, after 06:29Z).
Evidence: /Users/timmalmstrom/hpo-seats/review-2049/ev4 (this round), plus ev2 and ev (rounds 1–3).

## The delta from 245468e2 is main alone (the resolution delta)

27fdda2a is a two-parent merge: 245468e2 (the round-2/3 head) and 6b91e238 (origin/main). Main's first-parent range e2a4f7c6..6b91e238 is #2007 (71abfe4f) and #2029 (6b91e238).
- `git merge-tree --write-tree 245468e2 6b91e238` exits 0 and yields tree 9aa1ce72. `git diff 9aa1ce72 27fdda2a` is empty, so there are no hand resolutions.
- The PR's own diff is unchanged: the +/- lines of `e2a4f7c6...245468e2` and `6b91e238...27fdda2a` are identical.
- Main touched three files this PR also touches: .github/workflows/tests.yml, tests/entities.py and tools/audit/seat/INSTRUMENTS.md. All three merged automatically, and CI at the head (below) runs the merged result green.

Every round-1–3 measurement therefore carries to this head:
- the M1–M8 RESULT lines, with M7 killed by the driven-child check and M2 surviving only on an unreachable mixed-head case;
- the closures.json semantic diff (one inert_reads entry, plus seconds and reordering);
- the R9-RO-9 carry at c3855292.

## The body names every red

`## Red checks` names `closures`, `closures-autofix`, `delivery-status`, `fast (3.14)` (the stamp.py --self-test cleanup race at 245468e2, check-run 113149021777, now carried to R9-RO-9 and with a root-cause seat on it) and `pr-contract`, each with its cause.

At this head the only red is `delivery-status` (check-run 113164512810), which is main's merge-subject attribution and is answered in the body. `fast (3.14)` did not go red again.

## CI at 27fdda2a (check-runs API, polled every 5 minutes, final read 06:29Z): 24 success, 14 skipped, 1 failure, 1 cancelled

- `fast (3.14)`: success (113164602334, 06:04Z)
- `closures`: success (113164683985, 06:01Z); `closures-autofix` skipped
- `coverage`: success (113164602322, 06:29Z); `coverage-ratchet` success
- `mutation`: success (113164601906); `mutation-pin-plan`, `mutation-pins` and `mutation-autofix` skipped because `mutation` passed
- `pr-contract`: success (113164512134, 113165345014)
- `policy-docs`: success
- `delivery-status`: failure, main's, answered
- one `budget-raise-gate` twin cancelled; the other check of that name is not red

The new sharded pin path has still not run on this PR's own diff (`mutation` stayed green). Its evidence is the proof runs: #2048 run 37711053129 (re-derived in round 1) and #2032/#2033's closures-autofix `changed`.

This PR edits code-owned .github/workflows/tests.yml and the policy rule ci-autofix.md, so it still needs tvofi's approving review at this head.
