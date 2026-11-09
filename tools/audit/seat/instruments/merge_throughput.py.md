# `merge_throughput.py`

- `merge_throughput.py` — measures whether merges land inside the previous
  merge's gate window often enough to justify a merge queue. When: someone
  proposes a queue; the numbers decide before the mechanism is built. Its
  `flow` subcommand is the flow board (Lean study K1): throughput against
  the owner's demand of one roster group merged per hour, read from git
  alone — the first-parent log, the review/verdict bus refs through
  `review_strength`'s grammar and the roster through `roster_lib`. It prints
  per rolling hour and per 24 h: groups closed against takt 1.0, fly-ins
  closed, main moves split into group-carrying/record/roster-edit/fly-in,
  WIP by flow lane (A/B/C/F), first-pass review yield with its blocked-class
  mix, and lead time per size, and prints UNAVAILABLE rather than a zero
  when a source cannot be read. When: any flow change that claims to move
  throughput. Refusal: `--self-test` — its fixture's exact counts, the
  unchanged-fixture null control, and a named arm per classification
  predicate; `governance.yml`'s self-test step runs it. For the plan page's
  Flow section and the bottleneck alert (tvofi 2026-11-07, proposal 2) it
  adds `flow_merge_wait` (per PR merged in a window, the hours from its latest
  `merge` verdict on the bus at or before the merge, whether that verdict named
  the merged head, and a count of merges with no verdict, never a zero wait),
  `train_batches` (each `BATCH` banner of `merge_train.py`'s `train.log`, its
  queue, its `SKIP` lines with a reason class, and `done` once its `SKIP
  REPORT` line closes it; the self-test pins each writer literal in
  `merge_train.py`) and `bottleneck_metrics`, which composes them with
  `flow_closed`, `flow_verdicts`, `flow_lead` and `pr_cap.wip_groups`. The
  live train log is `$HOME/.local/state/hpo/merge_train/train.log`.
