# `roster_lib.py`

- `roster_lib.py` — shared roster parsing and wave logic (depth, critical
  path, open groups, the branch-to-group lookup), and the one owner of WHICH
  roster: `roster_path` picks the newest `dev/programme/rosters/wave-r<N>-groups.json`
  (at a ref or on the checkout) unless `--roster-path` names one; and of
  WHICH REF: `default_roster_ref` answers the round's roster branch
  `origin/handoff/audit-r<N>-roster` when the clone has it, else
  `origin/main`, with a note whenever that answer may be stale. Import it;
  `--self-test` is its only CLI. When: any tool that reads the roster — one
  schema reader, not several. Refusal: no roster where one was asked for
  raises `RosterNotFound`, never a fallback to another round's.
