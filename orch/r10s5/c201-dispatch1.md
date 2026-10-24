Session s5 dispatch, 2026-10-23T16:30Z, local seats only (no cloud runner this session). WIP 8/6 by pr_cap.py dispatch-gate; the one new group start is R10-LIVESTATE, over the cap as critical path (orchestrator.md section 5).

- Standing seats: tick (window 1, reads tick_loop.sh's board), merge (queue file, train.sh under mandate 6329234399), proposal-triage (re-rules s4's scratch proposals P-D..P-Q and the assessor's c2569 item into dev/programme/triage/s5-batch1.md). Roster seat starts with triage's first ACCEPT.
- R10-LIVESTATE: designer (XL, decision 0014), note to design/r10-livestate; fixer only after Design review: approve.
- R10-CI-LAYOUT-P2: replacement P2b coordinator. The s4 coordinator and its probe-runner both stopped at 13:48-13:51Z on a usage limit; their unpushed ruleset-window commits (to 27e2aca0c) are held by wip-sync/ext-p2b-coord-780164c2 and adopted in place. The P2b re-cut (#2662) waits for #2665 to merge. The ruleset 23698884 PUT stays the orchestrator's.
- Reviewers: #2665 (head 29b08d042), #2666 (0dda6260a), #2667 (5d874ec63), dispatched through bus.sh.
- Returned to their fixers: #2664 (blocked root-cause-detectable, instrument-self-tests and pr-contract red), #2668 (instrument-self-tests and pr-contract red), #2669 (pr-contract red).

Leaves #201 open.
