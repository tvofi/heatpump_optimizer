# `survivor_list.py`

- `survivor_list.py` — `check VERDICT.md EVIDENCE_DIR`: for a first line
  `Fix review: blocked <sha> mutation-vacuous:`, reads every file under the
  evidence directory for the survivor lines `mutant_run.py` (`--diff`,
  `--spec`) and `tests/mutation_table.py` (`LIVES`, `--pin-killed`'s
  `UNPINNED ... -- lives`) print, less a site marked `[triaged equivalent]`,
  and prints one `UNLISTED <file>:<line>` (or spec name) per survivor the
  verdict does not name, rc 1. Any other verdict class passes unread. Owner
  ruling (tvofi 2026-11-07, card 2, NARROW): one block lists every survivor
  the review found at that head (`fix-review.md` step 1). When: `bus.sh
  push-verdict` runs it on every verdict, local or relayed by
  `cloud_relay.sh`. `--self-test` drives each driver format, the
  other-class null control, and pins the producers' own print statements.
