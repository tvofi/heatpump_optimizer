Fix review: blocked e1c061cfb1807d8f9891136a3d323bee52f8f2e9 root-cause-unanswered: gate

bus-nonce: fe0aae455ae0ba3126a1737824c0284e

Round 1.

## Block

Body says `## Red checks` is `none`, but the head's `gate` check concluded failure twice (jobs 128922256394 at 01:03Z, run 42540768226; 128932207779 at 01:37Z, run 42546086673 decider named in the log), and `merge_train.py classify` exits 1 RED on it. I can tell what these are: both FAIL lines read "FAIL run(s) [...] at this head are still being judged; their gate decides", and the deciding gate (job 128932665609, run 42546086673) concluded success at 01:38:38Z. So they are deferral-only reds kept alive by `latest_runs`' worst-per-suite rule while Gate sweep is disabled_manually (re-read at this review: disabled_manually, updated 2026-11-08T11:54:00Z), which is this PR's own case (d). The body must name `gate` under `## Red checks` and answer it (the cheaper detector, or the finding; section 1(d) of the document already holds the answer, so one line suffices), and a `pr-contract` run must start after the last red concluded (01:37:01Z; the last pr-contract/pr-contract success started 01:35:08Z). I read the head as otherwise merge-ready; re-dispatch after the body edit.

## Evidence

- Head reviewed: e1c061cfb1807d8f9891136a3d323bee52f8f2e9 (ev/HEAD.txt). Merge with origin/main: `git merge-tree --write-tree` rc 0, tree 2a2682f9. Diff: 2 added files (dev/audit/rca/R10-RCA-TICK-BLIND.md, dev/programme/delivery/3362.md); VERSION, manifest and notes untouched; no production code, so no mutation proof or null control owed beyond the document's own.
- CI at this head: every required check green except `gate` as above; tests/closures, fast, mutation, arch-score, budget-raise-gate, pr-contract/pr-contract all success. mutation: no production line in the diff, no mutant drawn.
- carry_audit at head: 9 items, 9 routed, 0 unrouted (packet). Destinations R10-TICK-LEVELS, R10-FLY-STANDING-CONTRACTS, R10-BODY-CONTRACT accepted.
- Re-derived: CAP_MERGES=10, CAP_ORPHANS=20, SEAT_WINDOW_MIN=120; the type:comment query at orchestrator_tick.py:2050; gate.py's "gate-sweep.yml re-runs it" docstring; OPENER regex in beat_jobs.py; HANDOVER.md line 61 "updated-for: stays manual"; state_docs.py excludes HANDOVER.md; orchestrator.md line 261 "session-local copy is a defect"; the file's 4937 lines at 17e621f08c; Gate sweep state and time.
- Not re-derived: the 0/2 and 0/7 search counts. At this review the GitHub search API answers HTTP 422 "Query must include 'is:issue' or 'is:pull-request'" for both the type:comment and bare forms, so neither the 0 nor the non-zero figure can be reproduced now; the claim that type:comment returns 0 rests on the author's earlier read. The 17/20/244 board counts, the 5/2/1/3/6 class split, ref ages and the roster history rest on session-local scratch I have no access to; not verified.
- Round 1 of this review.

## Findings

- Follow-up: the (e) figure "0 against 2 and 0 against 7" is unreproducible today (the search API now rejects the query shape); the owning fixer must pin the replacement query against a fixture, not a count, and check the API's current requirement of is:issue/is:pull-request. Carry: R10-TICK-LEVELS
