Fix review: blocked e1c061cfb1807d8f9891136a3d323bee52f8f2e9 ci-deferral-red: classify reads RED on gate; both reds are deferrals whose decider is green, so a rerun settles it, not a fixer

bus-nonce: aec2410831b5df8390a0fac3a59c552e

Round 1. Head measured: e1c061cfb1807d8f9891136a3d323bee52f8f2e9 (PR head unchanged at read). Docs-only: one RCA file under dev/audit/ (INERT prefix, tests/closure.py:330) plus a delivery row.

## Block
- `merge_train.py classify e1c061cfb1807d8f9891136a3d323bee52f8f2e9 --pr 3362` prints `RED ... pending: none red: gate` (see ev/classify.txt). The two red `gate` jobs (128932207779 in run 42540768170, 128922256394 in run 42540768226) both log only `FAIL run(s) [...] at this head are still being judged; their gate decides`, a deferral. The deciding run 42546086673 has `gate` success (129030033063, 07:21Z) and 42561892061 also `gate` success. Nothing re-runs the old suites' deferrals (the PR's own case (d): Gate sweep disabled), so the train's worst-latest-per-suite rule keeps reading RED. No code defect; rerun the two old gate jobs (or push-free re-judgement by the orchestrator) and this is mergeable on substance.

## Evidence
- Merges with main: `git merge-tree --write-tree origin/main e1c061cfb1807d8f9891136a3d323bee52f8f2e9` rc 0 (tree 738d32cd...), no conflict.
- Diff vs merge base: 2 files, +325, no VERSION/manifest/RELEASE_NOTES/golden/claim/budget/closures file touched (VERSION 7.1.8 untouched).
- Mutation proof and null control: n/a, no code lands; body states so.
- Cited code re-read at origin/main: CAP_MERGES=10, CAP_ORPHANS=20, SEAT_WINDOW_MIN=120, `type:comment` query (orchestrator_tick.py:2050), gate.py:33 gate-sweep.yml docstring, orchestrator.md:261 session-local copy rule: all as the document says. R10-TICK-LEVELS, R10-BODY-CONTRACT, R10-FLY-STANDING-CONTRACTS exist in wave-r10-groups.json; R10-FLY-TICK-BLIND absent, as the body says.
- Red-check answer: body's `## Red checks` names gate and answers it (deferral; no cheaper detector); carry_audit at the head: 9 routed, 0 unrouted.
- Not re-derived by me: the 17/20/244 board counts, 5/2/1/3/6 split, 33.0 h/20.8 h figures, Gate sweep disabled timestamp and the 0-vs-2/7 search counts (board file, scratch ev and live reads from 11-08 are not available to this seat).
