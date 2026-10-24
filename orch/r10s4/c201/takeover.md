**Round-10 orchestrator, session s4 — takeover after host reboot (2026-10-21 ~07:40Z).** Mandate 6175172275 in force (scope all, to 2026-10-28T18:14Z).

Measured at origin/main `df6ca4bc` (main green, 32 contexts):
- Every detached loop was dead: train `b22-0724` (died after #2540 merged; #2519 and #2526 unmerged), tick loop, state_docs beat, wt_sync. Restarting them from the tree.
- Train `b23` (#2526 merge verdict at head `baa75f58`; #2519 only if `app_approve.sh --carry` reports carried from `6efcb1ac` to `fb6d355b`) is being launched through `tools/audit/seat/train.sh`.
- The tick board was 4.5 MB: `orchestrator_tick.py` replays every historical `OWED` level line from `cloud-relay.log` (35214 lines, ~281 distinct). Log rotated (archive kept); fixer dispatched on the reader/log semantics, group R10-TICK-OWED-LEVEL.
- Owed, being surveyed before action: 9 stranded handoffs (`bus.sh orphans`), 10 open PRs against the soft cap of 6, most 66–75 commits behind main with unanswered reds, the roster branch behind main's roster changes, 14 groups the tick lists as blocked on owner disposition (to be decided under the mandate, recommended option), the record beat for 10 unrecorded merges, and `nightly-status` red.
- Ledger `SEATS.md` has no entries after 2026-10-20 15:34Z; this session resumes it.

No other merge is started until the survey lands. Leaves #201 open.
