Fix review: merge 4570f384056b4bcad75931a7f34f346ddd040f10
bus-nonce: 07af82919063e81965f879969dd57e2f

Delta review against reviewed-head c48d7a36c5 (later rounds review the delta only).

- The PR's own diff, three-dot against main af4d89f7, is the same file by file as at c48d7a36c5, with two exceptions: tests/closures.json (three lines added to cycle_lane.py) and the #1218 note in tests/deployment_shape.py. 28325cf6 has the same tree as 8c50adf2. 4570f384 is a clean merge.
- Recomputed from tests/closures.json at the head: 34 scripts, 561 pairs, 435 comparable, 182 at Jaccard >= 0.80; 120 tracked package files. These match the note.
- Hand closure lines: coordinator.py imports circulation and number_restore, and pump_arbiter.py imports duty_ledger. Both importers are already in cycle_lane.py's closure. Every closure that contains coordinator.py also has all three files.
- Local runs at the head: deployment_shape.py, structure.py and cycle_lane.py (25/25) pass. CI typing passes.

Notes:
- entities.py did not finish locally: it timed out at 900 s while retrying gh with HTTP 502. That is an environment failure, so the CI gate is the authority. Carry: dismissed: network flake outside the PR
- The --single derive of cycle_lane.py was cancelled while queued behind 4/4 heavy slots. The closure lines were checked statically instead (see above). Carry: dismissed: covered by the static import check and CI's closure check
- budget-raise-gate is red because of script_runs_per_push 54->56. That diff is unchanged since the reviewed head and needs the owner's or the mandate's review, not this one. Carry: dismissed: approval-gated, not a code defect
- The note's phrase "cycle_lane.py, whose closure opens the whole package" was already there at the reviewed head. The closure holds 82 of 120 package files. Carry: dismissed: wording that predates the delta, counts correct
