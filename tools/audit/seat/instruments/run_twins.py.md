# `run_twins.py`

- `run_twins.py` — counts a workflow's cancelled `pull_request` runs that
  sat beside a same-SHA sibling (two events at one head, not a
  supersession), from cached `/actions/workflows/<file>/runs` pages or
  `--fetch`. When: judging a workflow's `concurrency:` block (R9-CI-2a).
  Refusal: none; it enumerates.
