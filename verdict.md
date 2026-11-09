Fix review: blocked e1c061cfb1807d8f9891136a3d323bee52f8f2e9 ci-unsettled: merge_train.py classify still exits 3 (WAIT) after about 35 min; no defect found in the diff

bus-nonce: 4e16f54e60e437dab3e2c8e2187f499c

Round 1 of this PR's review. This is a hand-back unverdicted, not a finding against the fix: the diff passed every check I could run, and the only block is that CI on this head has not settled.

## Block

- `python3 tools/audit/seat/merge_train.py classify e1c061cfb1807d8f9891136a3d323bee52f8f2e9 --pr 3362` printed `WAIT ... pending: gate red: none` (rc 3) on every run from about 04:30Z to 04:55Z. The cause is run 42561892061, started 04:27Z after the push-time runs; its `prelude` (job 128979910443) and `refresh` (128979910441) were still `queued`. Every other check run on the head is success or skipped, except the two deferral-only `gate` reds named in the body (runs 42540768170 and 42540768226), which later gate run 42546086673 (job 128932665609) superseded with success. Re-dispatch the review once classify exits 0. Nothing in the diff needs changing.

## Evidence

- Head measured: e1c061cfb1807d8f9891136a3d323bee52f8f2e9, equal to `refs/pull/3362/head` at 04:55Z (ev/HEAD.txt).
- Diff is two new files, `dev/audit/rca/R10-RCA-TICK-BLIND.md` and `dev/programme/delivery/3362.md` (ev/diffstat.txt). `dev/audit/` is on `tests/closure.py`'s INERT list (line 330). No `VERSION`, manifest, `RELEASE_NOTES.md`, golden, claim or budget file moved (ev/touched-protected.txt is empty), so steps 4, 5 and 14 have nothing to move. No production code lands, so the mutation proof (step 1) and the finder's harness (steps 2, 3) are n/a, as the body says.
- `git merge-tree --write-tree origin/main e1c061cfb1807d8f9891136a3d323bee52f8f2e9` exits 0 (ev/merge-tree.txt). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Carries (step 10): R10-TICK-LEVELS, R10-BODY-CONTRACT and R10-FLY-STANDING-CONTRACTS each exist in `dev/programme/rosters/wave-r10-groups.json` on origin/main and on `handoff/audit-r10-roster` (git grep). The packet's carry_audit reports 9 finding items, 9 routed, 0 unrouted, 0 bad destinations. The body's R10-FLY-TICK-BLIND note matches the section 4 text.
- Red-check answer (step 11): the body's `## Red checks` names `gate` and answers it. It cites a deferral-only red (runs 42540768170 and 42540768226) and gives the cheaper detector, the disabled sweep, with a Carry. I read the check runs at this head and they match. `tools/ci/gate.py:33` does say gate-sweep.yml re-runs a deferral.
- Code citations re-read at the head: `SEAT_WINDOW_MIN = 120` at `orchestrator_tick.py:128`, `CAP_MERGES = 10` at line 157, `CAP_ORPHANS = 20` at line 181, the `type:comment` query at line 2050, `OPENER = re.compile(...)` at `beat_jobs.py:134`, and `one_pr` / "NOT REVIEWABLE" at `orchestrator_tick.py:1120` and 1173. The file is 4937 lines, as the document says (ev/tick-query.txt).
- Not re-derived: the time and count figures (33.0 h, 20.8 h, 17 NOT REVIEWABLE, 244 flagged lines, the 5/2/1/3/6 split, driver4 output, the seven refused verdicts). They rest on the session state directory, the stored 19:11Z board and logs I do not have, and the document's section 5 itself lists the ones it could not establish. The null control for (e) did not reproduce either: from this seat `gh api --method GET search/issues -f q=<sha> repo:tvofi/heatpump_optimizer [type:comment|in:comments|none]` returned HTTP 422 "Query must include 'is:issue' or 'is:pull-request'" for all three forms (ev/search-counts.txt). The 0-against-2-and-7 table is therefore unverified here. Once an arm for (e) is fixed, its fixer should pin the exact query that GitHub accepts.
- I built no instrument of my own.
