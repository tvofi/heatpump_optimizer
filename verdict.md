Fix review: merge c6c212f7524abfefa1c4590821bad7ea84cd2650

bus-nonce: c8f2af3eb02728deb8bc6fc2f1b02389

Round 1, measured at head c6c212f7524abfefa1c4590821bad7ea84cd2650 (the brief's b2499f12 is an earlier head; the diff is still only the batch file and its delivery row).

## Evidence
- RESULT: CI GREEN at this head (merge_train classify rc=0: pending none, red none).
- RESULT: git merge-tree --write-tree origin/main HEAD exits 0 (tree 81b76c7f), so no conflict.
- RESULT: the diff adds dev/programme/triage/s6-batch116.md and dev/programme/delivery/3203.md only; no production, claim, budget, VERSION or closure file moves, so there is no mutation, golden or budget check to run.
- RESULT: verdict grammar holds. The entry has Verdict: DEFER, Source:, Instances:, Cost: and Binding:, and it names the group that owns the item (R10-TICK-LEVELS) and what would change the answer, as proposal-triage.md requires.
- RESULT: the roster at a62d10eb0 and a PR-file query each match the entry's claims. R10-TICK-LEVELS is in-progress with pr 3200, R10-TICK-PR-BUCKETS is absorbed, and both carry the "Three owed classes", s6-batch115.md#P375 and "FIRED line prints nothing" texts. #3089, #3177, #3085 and #3174 touch 8, 3, 12 and 2 files with 0 under custom_components/. At d7e67e0d7, tools/audit/seat/orchestrator_tick.py has the FIRE-OWED payloads() arm at lines 947-948. b8e823699, efd37113a and a62d10eb0 are commits.
- Not re-derived: the ledger timestamps and line numbers (seat ledger, ledger-standin.txt, handoffs) are session-local files that are not in the tree. I could not verify them, and the entry cites them as the orchestrator's report.
- tests / nightly-status was red in the packet digest; the diff reaches nothing it reads, so it is not this PR's. The final classify counts no red.
- The ACCEPT-destination check does not apply, since the ruling is DEFER. The fix-review checks that need code (mutation, harness, claims, class rule, forward carry) do not apply to a record-only diff. The entry adds no carry, because the owning group already holds the text.
- Packet figure_lint: 0 refused, 1 unverified (a packet-internal diff command).

## Findings
- none
