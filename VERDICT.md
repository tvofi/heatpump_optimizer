Fix review: blocked 345daba44851215b9510f27826957e1bd5fc0a30 carry-missing: not carried to R10-REVIEW-CARRY (P200) or R10-FLOW-TOOLKIT-MODEL (P203)
bus-nonce: faf124fbdcbf9c22a6d446ba8e6aa13f

# Fix review -- PR #2899, roster: round-10 batch (R10-RCA-FRICTION-RESIDUE fixes wires, immersion-latch re-pin)

Round 1. Reviewed head: 345daba44851215b9510f27826957e1bd5fc0a30, in a detached worktree at that
head, against origin/main 07295d4ea. `dev/governance/roles/` has no diff between the merge base
and origin/main.

## Results

- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head:
  `TOTAL: 0 error(s) across 1 file(s)`, rc 0 (`ev/brief_lint.txt`).
- `R10-RCA-FRICTION-RESIDUE` `fixes` at the head: `[2410, 2593, 2597, 2660, 2784]`
  (`ev/groups.txt`).
- Groups, origin/main against the head: `212 212 0 0 17`. Seventeen groups differ, which matches
  the body.
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree `967e42c22`)
  (`ev/merge-tree.txt`). The three-dot diff touches only the roster JSON and
  `dev/programme/delivery/2899.md`.
- Live check-runs at the head (`ev/check-runs.txt`): 55 runs, 36 success, 19 skipped,
  0 failure, 0 pending. There is no red to answer.
- The routing in the body is correct: each named group is live and owns the file its carry
  touches. `R10-REVIEW-CARRY` is at `fixing` and lists `dev/governance/roles/fix-review.md`.
  `R10-FLOW-TOOLKIT-MODEL` is at `not-started` and lists `tools/audit/seat/roster_lib.py` and
  `roster_edit.py`. `R10-FLOW-WIP` is at `not-started` and lists
  `tools/audit/seat/orchestrator_tick.py`.

## Findings

- F1 (blocking, carry-missing): the body's `## Forward-carry` says P200 (the four unstated
  verdict-relay checks in `fix-review.md`) "belongs to" `R10-REVIEW-CARRY`. It says P203
  (`roster_lib.gate_kind`) belongs to `R10-FLOW-TOOLKIT-MODEL`. Neither write is in the tree.
  At this head, and at the roster tip `origin/handoff/audit-r10-roster` = `de410e4c9`,
  `R10-REVIEW-CARRY` keeps the same 3 carries as origin/main and none names P200.
  `R10-FLOW-TOOLKIT-MODEL` goes from 10 to 12 carries, and the two additions are the
  `LIVE_STAGES` and XS-size notes, not P203. The only carries citing `s6-batch35.md#P200` and
  `#P203` are still on `R10-ORCH-REVIEW-PACKET` and `R10-ORCH-ROSTER-SCHEMA`. This PR sets both
  of those groups to `done`, so after it merges no fixer reads P200 or P203. That is the exact
  failure the body describes. `finding-propagation.md` requires the carry to be in the tree
  before the producing PR merges (`ev/carry-routing.txt`). Repair: run `roster_edit.py
  append-carry` for each, through the standing roster seat's queue, on
  `handoff/audit-r10-roster`. Each carry must state its control as a precondition. Then
  re-take the head. Carry: R10-REVIEW-CARRY
- F2 (the same defect, second destination): P203's text must land on `R10-FLOW-TOOLKIT-MODEL`
  in the same roster batch. Carry: R10-FLOW-TOOLKIT-MODEL
- F3 (verified, non-blocking): the P199 line is true. `R10-FLOW-WIP` already holds the carry
  citing `dev/programme/triage/s6-batch35.md#P199`. Carry: dismissed: verified in the tree at this head
- F4 (non-blocking): `## Head` describes three different heads: the row commit `345daba44`,
  the merge `cfd7ccf5f`, and "the head is `de410e4c9`". Its figures were measured at
  `de410e4c9`, before main `07295d4ea` was merged in. The lint and the `fixes` figure
  reproduce at `345daba44`. Carry: dismissed: figures re-derived at the reviewed head
