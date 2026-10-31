# `owed_unactioned.py`

- `owed_unactioned.py` — says which tick owed lines have outlived a sweep with
  no live acknowledgement (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). It reads
  the board's whole owed family (`-> OWED…`, `REVIEW OWED:`, `DISPATCH:`,
  `OWNER FLAG:`, `DESIGN-BUILD:`, `MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:` (queue the PR for the train,
  which posts the approval), `UNLEVELLED:` (read the state by hand), `REVIEW STALLED:` (re-fire the reviewer)), keys
  each line on its topic or `#<pr>` (a verdict level's head8 is its id, so a
  new head re-raises), and
  counts in `--state` the boards each key has stood on. A key standing
  `--after` (2) sweeps is UNACTIONED unless an `--acks` file holds a live
  `OWED-ACK <UTC> <key> <id> [ttl=<h>] <reason>` whose id prefixes a sha the
  key carries now (7+ characters, or the whole of a non-sha ledger id; the
  tool's own indented `ack:` echo and a `<placeholder>` reason are refused);
  an acknowledgement lapses after its ttl (default 1 h, at
  most 12), so a handled line comes back for its handling to be checked, and
  free queue text covers nothing. When: every sweep, step (5) of
  `sweep_template.md`. Exit 0 none unactioned, 1 the UNACTIONED block (each
  with a ready ack line), 2 UNREADABLE: no provenance line, a board older than
  `--max-board-min`, an owed line it cannot key, an unreadable state.
  `--self-test` drives it offline.
