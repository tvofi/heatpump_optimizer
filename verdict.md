Fix review: merge 49c160536b7fbd72da50e8c544dbff0b483ca922

bus-nonce: 8253fe343a1ebb529bc08490f2f1a0cd

Round 1. Record PR (two files: dev/programme/triage/s6-batch90.md and delivery/3039.md); no production code, so no mutation proof, harness or claim drift applies. Head measured: 49c160536b7fbd72da50e8c544dbff0b483ca922 (still PR head per refs/pull/3039/head).

## Findings

None.

## Evidence

- (a) P327: s6-batch64.md#P294 has the APPROVAL-OWED arm (BLOCKED + REVIEW_REQUIRED + merge at head) and the UNLEVELLED catch-all (item 3); the six PRs are BLOCKED/REVIEW_REQUIRED merge-verdict instances and fall in the APPROVAL-OWED arm. At cabfaadc3, orchestrator_tick.py:689 requires ms in (CLEAN, UNSTABLE) for MERGE-READY and the --json list at :553-555 has mergeStateStatus and no reviewDecision. Confirmed. The instance times (05:09Z etc.) are the filing's; not re-derived.
- (b) Re-derived from 232 dispatch/reviewer-<N>-<sha8> refs, 231 with a later "Fix review:" commit on verdict/<N> (one has none): n=231. p50/p75/p90/p95 = 17.6/33.0/57.0/70.7 min (body 17/32/56/70, floor-truncated, within 1 min); max 959.6. Over 45/60/90/120 min: 34/21/6/4, exact. 34/231 = 14.7%, 6/231 = 2.6%. See ev/latency.txt.
- (c) P280 (s6-batch60.md) rejects exactly the RemoteTrigger run-log read, and cloud_dispatch.py reads no run. dispatch_ref gives dispatch/reviewer-rev-<N>, as the body says. The #3027 315-minute instance is the filing's; not re-derived.
- (d) roster_edit.py ruling_verdict reads P327 and P328 as ACCEPT; triage_refusal passes both carries; flipping either to REJECT refuses its carry. See ev/gate.txt.
- git merge-tree --write-tree origin/main at head: exit 0, clean. fix-review.md role-diff against origin/main: empty.
- merge_train.py classify at head: GREEN, pending none, red none. Packet gate digest green, refusals none, carry_audit 0 findings.
- Not re-derived: nothing beyond the two filing-sourced instance timings above.
