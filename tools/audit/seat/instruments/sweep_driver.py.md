# `sweep_driver.py`

- `sweep_driver.py` — the probe PR's sweep, where `workflow_run` never fires
  (`gate-sweep.yml` runs only from the default branch): every poll (60 s floor,
  tvofi 2026-10-19) it lists the PR's `ci.yml` runs at the live head, reads each
  run attempt not yet swept (N5-1) and starts `python3 -I <tree>/tools/ci/gate.py
  --sweep --run <id>` as a concurrent child for it: attempt 1 only under
  `--nochain`, every attempt under `--chain`. It logs one line per sweep,
  `superseded=1` for an attempt first seen already replaced, reads `/rate_limit`
  before each poll and backs off below 20 % remaining or on a 403 (A1 item 5),
  and exits after 900 s with every run completed and nothing new. When: a seat
  drives a probe PR through the sweep (M-6, M-2, the combined control). It only
  reads (`gh api` GET); the child's re-runs are the only writes. Refusal: a
  `--poll` under 60. `--self-test` runs it over a fake `gh` and clock.
