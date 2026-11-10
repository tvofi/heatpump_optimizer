# `bottleneck_check.py`

- `bottleneck_check.py` — the bottleneck alert (tvofi 2026-11-07, proposal
  2): one `BOTTLENECK: <metric> <value> vs <threshold> -- <suggested action>`
  line per flow metric past its threshold, and nothing at all when none is. A
  source it cannot read prints `BOTTLENECK-UNREADABLE: <metric> -- <why>`. A
  line suggests and takes no action; the orchestrator decides. The metrics are
  `merge_throughput.bottleneck_metrics`, imported. The thresholds and minimum
  samples are `THRESHOLDS` (the owner's): first-pass yield under 0.6 over
  24 h (5 first passes), train skip-share over 30 % in the last 2 completed
  batches (3 entries), median merge-wait over 2 h over 24 h (3 PRs),
  throughput under 0.7 x takt over 6 h, in-progress WIP at or over the cap,
  and one blocked class over 30 % of blocks over 24 h (5 blocks). Throughput
  counts roster groups whose stage entered done in the window
  (`flow_closed`, the roster write, not the merge), so a hand record batch
  reads as a burst and record lag as a trough. When: the beat's `bottleneck`
  row runs it every 30 minutes with `--train-log` (the overlay's
  `train_log`), `--wip-cap` (`plan_slots`) and `--memory`, which re-prints a
  held breach's first line verbatim so the digest's wake fires once per trip
  and again only after a recovery. `--self-test`: a null control, one planted
  case per rule, each rule's boundary and minimum sample, a running batch not
  read, the UNREADABLE arm per rule, the trip memory, and one mutant per rule
  predicate; the beat row's arms are mutated in
  `dev/audit/harnesses/r10_outside_intake_p2_mutants.py`.
