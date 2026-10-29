# `ledger.py`

- `ledger.py` — the obligations ledger (R10-ORCH-LEDGER; the machinery
  design's section 6.3): one table of kinds, two stores beside the relay's log
  (`dispositions.tsv`, written only by `dispose`; `events.tsv`, append-only
  `open`/`close`/`attempt`) and one fold. Derived kinds are recomputed each pass
  (`level` derives `handoff-no-pr` for the relay; the tick derives
  `design-build` and `review-owed`); event kinds are keyed on kind, subject and
  sha, an open at a new sha superseding the old, and close by the producer's
  `close`, a moved or closed pull request, or the tick's read-back of the
  approver's comment (`verdict-unposted` only on its own first line: a relayed
  POSTED closes nothing). `escalate` turns stranded handoffs into DISPATCH
  lines, oldest first, naming the roster group, and an OWNER FLAG past the
  second threshold, behind `HPO_LEDGER_AGING` (`<dispatch_h>,<owner_h>` or
  `off`; default the owner's 4 h and 12 h). `open_pr.sh` records each opener
  attempt on its handoff ref (`started`, then `opened,PR=<n>` or `unopened`).
  The first run imports `cloud-disposed` (last disposition per ref) and the
  log's still-open OWED lines; a reader folds that in memory and writes
  nothing. Refusals: a ref of no arm, a kind of no table, a derived kind
  opened. A missing store is first run; an unreadable one is UNREADABLE.
  `board` exits 0 none owed, 1 owed (with its summary line), 2 unreadable.
