# `policy_reread_check.py`

- `policy_reread_check.py` — says whether a session owes a policy re-read:
  OK when `--stamp`'s instant is later than the newest compaction in
  `--transcript` (a JSON line whose `subtype` is `compact_boundary`), else
  OWED; `--write-stamp` records a finished re-read in the format the check
  reads. When: the sweep's step 0 (`sweep_template.md`), after every
  compaction. Refusal: it fails closed -- no stamp, an unparseable one, one
  ahead of the clock, an unreadable transcript, or a line naming the marker
  that is not JSON each print OWED, never OK. `--self-test` drives both arms.
