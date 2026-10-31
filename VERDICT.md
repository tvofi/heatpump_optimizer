Fix review: blocked 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa ci-pending: gate checks on this head still queued after ~12 min of polling, no GREEN/RED

bus-nonce: e4ef0669652a6f12489a3ab9f5ef6a65

## Block
`merge_train.py classify 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa` returned 3 (WAIT, "pending: gate red: none") on every poll from the start of the review; the packet shows `cancel-superseded`, `prelude` and `refresh` still queued. Content review found no defect. Re-dispatch this review, or publish a merge verdict, once classify exits 0. Nothing below argues against merge.

## Findings
- The destination group R10-FLY-TICK-APPROVAL-OWED is not in `dev/programme/rosters/wave-r10-groups.json` at origin/main (915406ce6) or at handoff/audit-r10-roster. The brief says it is live and `b85-P322.txt` agrees, but that held op lives on the orchestrator's machine, so I could not check the group's status or that the append-carry applies. The file list names `wave-r10-groups.json`; if the group is created only by the held op, the orchestrator must confirm the group exists before applying the carry. Carry: R10-FLY-TICK-APPROVAL-OWED | dismissed: the group comes from P294's fly-in (s6-batch64.md:90); applying the carry is the orchestrator's roster op and is not this PR's change.

## Evidence
- Head is 7ef58ef6e19bcac2722a6099dd0fde1e41d282fa; base and merge base are 915406ce6e01a5b6107e9141b70f1b76eabc60f1 (origin/main tip, #3028's merge). `git merge-tree --write-tree origin/main HEAD` exits 0 (clean), tree da3200b00.
- Diff is two added files, dev/programme/delivery/3031.md and dev/programme/triage/s6-batch85.md. No production code, VERSION, manifest or notes are touched.
- Cited symbols at the base: `ledger.py:618` is `def review_owed(prs, readback, dispatched, carries=None)`, with no headRefName test. `record_row.py:619` is `RECORD_BRANCH = "record/autofix"`. `orchestrator_tick.py:701` is the `lg.review_owed(...)` call site. `merge_train.py:1229` is `def sweep_bots`, and its lines 1261-1270 log `BOT #n pending`, `refused by the guard` and `not merged`. All hold.
- `git grep RECORD_BRANCH` over ledger.py and orchestrator_tick.py prints nothing at the base. standing-dispatch.md has no record/autofix sentence. R10-RECORD-HOLD-APPROVE and R10-ORCH-BEATD both have resume stage `done`. All as the record states.
- The P241 carry text is in wave-r10-groups.json on R10-RECORD-HOLD-APPROVE, as stated. Its `ledger.py review_owed (505-522)` anchor is stale, and the new carry cites 618 correctly.
- The 3 sweeps and the `AUTOMERGE OK #3028` print at 9e688830 are runtime observations, cited from the orchestrator. I could not re-derive them (figure_lint: 2 resolved, 3 not verified); #3028 is now merged.
- carry_audit at the head: 0 finding items, 0 unrouted. brief_lint and the triage gate are part of the queued CI and I did not run them. The packet has no refusals or advisories.
- No mutation proof applies: the PR writes no production line.
