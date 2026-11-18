# `pr_cap.py`

- `pr_cap.py` — the soft cap, on dispatch since 2026-10-20: `dispatch-gate`
  counts the roster groups whose `resume.stage` is `in-progress` through
  `roster_lib` at the roster ref, prints their ids and refuses at or over
  `HPO_WIP_CAP` (default 6) unless `--over-cap "<reason>"` is given; `info`
  prints the open count for `open_pr.sh` and never refuses. A group that also
  has an open pull request is one group. Imported by `orchestrator_tick.py`
  for its `WIP` and coordinator level lines. A bot is a GitHub-flagged bot
  other than `app/hpo-author`, which authors every seat PR. When: before
  dispatching a new group, and `open_pr.sh` before it opens (information
  only); the tick every pass. Refusal: at or over the cap without
  `--over-cap <reason>`; an empty reason; an invalid `HPO_WIP_CAP`; a roster
  it cannot read (never a clean zero); an open list gh cannot read, that is
  not JSON, or that reaches gh's 200 limit (reported, not gated).
