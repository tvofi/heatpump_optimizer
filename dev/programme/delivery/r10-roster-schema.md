# R10-ORCH-ROSTER-SCHEMA — where its delivery row is

The row the ledger reads is `dev/programme/delivery/<N>.md`, committed and
pushed by `tools/audit/seat/open_pr.sh` when this pull request opens, in the
open-row shape `- [#N](...) — **open**, ...` and updated to `**merged**` at its
merge.

This file is a pointer, not a row. `tests/delivery_status.py`'s `read_texts`
keeps only digit-named stems, so a row named by topic is read by no check --
which is why the wave brief's name for the row appears as friction in the pull
request body rather than as a row the ledger would never open.
