# Proposal triage, session s14, batch 188 (P610)

The bar and the denominators are batch 141's.

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- `handoff/audit-r10-roster`, first-parent history 2026-11-04 to 2026-11-11T11:25Z (1,394 commits).
- The drain's retained per-op reports: `roster-report.txt` (to 2026-10-26) and
  `s7/roster-s8-report.txt` (to 2026-10-31), under the r10s6 state directory.
- The live drain state: `digest/state/roster-done.json` and the roster queue `s7/roster-queue-s7.txt`, read at 11:25Z.

## P610: ROSTER-WRITER-CONCURRENCY

Verdict: REJECT. No mechanism is built to cut or serialise writers on the roster branch. The
contention is real but measured well under the bar. What makes a carry wait is the serial cost
of each op, and the queue depth in front of it.

Source: queue line 289, 2026-11-11, orchestrator s14: "the roster branch handoff/audit-r10-roster
has too many concurrent writers".

Measurements:
- **Who writes.** First-parent commits since 2026-11-04 come from three writers:
  - 1,181 `roster_edit` commits, all from the one beatd `roster-drain` job. It holds a lock and
    runs one op at a time (`beat_jobs.py` `roster_drain`, `ROSTER_PASS_BUDGET_S = 450` at `:137`).
    The seat-queued carries go through it too. The `roster-fix-1` edit seen live at 11:24Z was
    the drain's own child, applying queue line 4436.
  - 213 foreign commits. These are the triage record commits (`triage: s14 batch N`) and the
    `roster_sync` derives from `postmerge.py`. That is 1.23 an hour over 173.6 h.
  - If the claim were true in its strong form, there would be several independent `roster_edit`
    writers. There is one.
- **What a race costs a drain op.** Method: take each pair of consecutive drain commits less than
  300 s apart, which is one op's wall time, and split the pairs by whether a foreign commit
  landed between them.
  - 7 days: 940 clean pairs, median 48 s; 33 pairs with a foreign commit between, median 167 s.
    The pairs with a foreign commit are 3.4% of all pairs. Even with every extra second blamed
    on the race, the cost is 6.3% of drain time.
  - Null control: a long gap is more likely to contain a foreign commit, whatever the cost. The
    length-biased null mean of all the gaps is 118.4 s (since 2026-11-10T08:00Z). The observed
    mean of the pairs with a foreign commit is 169 s, over 26 pairs. The excess over the null is
    6.8% of drain time. With no length-bias correction at all, the upper bound in the same
    window is 16.9%.
  - From a foreign commit to the next drain commit: median 53 s. That is one op re-run, which
    matches the retry path: `roster_queue.py:393` makes 4 attempts, and `roster_edit.py`
    `PUSH_ATTEMPTS = 3` at `:210`.
  - If the claim cleared the bar, the null-corrected excess would be over 20%.
- **Refusals from races.** The retained reports hold 943 ops: 804 pushed and 139 refused.
  - None of the refusals is a lost push race. The refusals are input errors: a missing
    `@file`, the triage gate, a duplicate entry, a byte-identical no-op.
  - 3 were `cannot lock ref` fetch races, on a local ref shared between seats. All 3 predate
    `b7ac768450` (2026-10-31), which made `fetch_origin` retry that race (`FETCH_ATTEMPTS = 4`,
    `:998`).
  - If races cost work, refusals of the form "the push lost the race on every attempt" would
    appear here. There are none.
- **What actually delays a carry.** At 11:25Z the drain had 27 pending lines, queue lines 4437
  to 4463. P607 at line 4458 was 22nd.
  - At a clean median of 43 to 48 s an op, plus a 450 s pass budget that splits the queue across
    passes, that is about 20 to 35 min.
  - 18 of those 27 lines are one closeout burst: `mark-carry R10-TRAIN-RESIDUE`, queued together.
  - Removing every foreign writer would save at most the 6.8%.

Disposition:
- No group and no carry.
- The latency lever is already in the tree, and it needs no ruling. A seat that queues a burst of
  ops onto one group can use `roster_queue.py run --batch`, which makes one worktree and one
  push.
- Re-open trigger: this returns as a queue line if the null-corrected race excess, measured the
  same way, passes 20% of drain time over a 24 h window, or if any drain op is refused for
  losing a push race on every attempt.
