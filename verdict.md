Fix review: merge e1c061cfb1807d8f9891136a3d323bee52f8f2e9

bus-nonce: 216597941cdc49b87a05f8fb2220b5ce

Round 1. Head measured: e1c061cfb1807d8f9891136a3d323bee52f8f2e9 (the PR body's head).

## Evidence
- CI: `merge_train.py classify e1c061cfb1807d8f9891136a3d323bee52f8f2e9 --pr 3362` exits 0, GREEN, pending none, red none. The one red the body names (`gate`, a deferral line) is a deferral; the head's gate is now green.
- Merge: `git merge-tree --write-tree origin/main e1c061cfb1807d8f9891136a3d323bee52f8f2e9` rc 0, no conflict.
- Diff (three-dot): two new files, `dev/audit/rca/R10-RCA-TICK-BLIND.md` and `dev/programme/delivery/3362.md`. VERSION, the manifest and RELEASE_NOTES are untouched. No claim, golden, budget or closure file moves. `dev/audit/` is an INERT prefix (`tests/closure.py:330`).
- Mutation, finder's harness and null control: n/a, no production code lands. The body says so, and the packet names no finder's harness.
- Re-derived in the tree at origin/main: `SEAT_WINDOW_MIN = 120`, `CAP_MERGES = 10`, `CAP_ORPHANS = 20` (`orchestrator_tick.py`). The `type:comment` query is at `orchestrator_tick.py:2050`.
- Null control (e), re-run live: `search/issues` for cb5512741638 returns total_count 0 with `type:comment`, 1 without the qualifier and 1 with `in:comments` (`is:issue` now has to be added). The sign matches the body's 0 against 2/1. The absolute counts differ from the document's, because the search index moved, so those counts are not re-derived.
- Not re-derived: the 17/20/244 board counts and the 5/2/1/3/6 class split. They come from a 19:11Z board and a seat-scratch file that are not in the tree. The 8-of-17 and 6-real split rests on the author's job-log reads.
- Gate sweep now reads `active` (updated 2026-11-09T07:33Z), where the document records it `disabled_manually` at 2026-11-08T11:54Z. The document is dated to the 11-08 evidence, so this is a later re-enable and not a contradiction.
- Forward-carry: R10-TICK-LEVELS, R10-BODY-CONTRACT and R10-FLY-STANDING-CONTRACTS are all groups of `wave-r10-groups.json` on `handoff/audit-r10-roster`. The packet's carry_audit reports 9 routed, 0 unrouted, 0 bad destination.
- Red-check answer: the body names `gate` and answers it (a deferral, no cheaper detector). The head's gate is green.
- Delivery row `dev/programme/delivery/3362.md` is present.

## Findings
- Residual: the document's arm 1 and its disabled-sweep level line assume the sweep stays disabled, and it is now active. R10-TICK-LEVELS should re-measure the sweep state at its own merge base before keeping the "GATE SWEEP DISABLED" line, and keep the deferral-only classification regardless. Carry: R10-TICK-LEVELS
