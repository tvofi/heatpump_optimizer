## Forward-carry

- The round-1 verdict's finding on `roster_lib.is_open` (`roster_lib.py:205-206`): it tests only `DONE_STAGES` (`("done", "rca-done")`, line 33), so `carry_audit.py`'s destination check (lines 330-334) passes an `absorbed` group; it sits beside P124, whose write-time arm already refuses `absorbed`. Carry: R10-ORCH-ROSTER-SCHEMA
