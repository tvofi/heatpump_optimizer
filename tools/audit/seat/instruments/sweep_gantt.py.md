# `sweep_gantt.py`

- `sweep_gantt.py` — compares the live state against the plan's Gantt and
  prints one `GANTT-SLIP <KEY> <detail>` line per unacknowledged slip: `IDLE`
  (the plan starts the group by now and nothing works on it), `LATE` (a
  group's finish moved over 6 h past the baseline) and `CLOSURE` (over 2 h).
  Owner ruling (tvofi 2026-11-01): compare the real state against the gantt
  each time the plan html is updated, mechanically, and surface slips to act
  on, defer or accept. Handoffs count as live only when the tip was committed
  within 12 h, and fire lines are filtered to 12 h (ruling 2026-11-06); the
  `--handoff-rows` and `--fired-ledger` forms apply both filters here. Acks
  are `<ISO> <KEY> act|defer|accept` lines; `accept` also re-baselines. When:
  every second pass of `sweep_runner.sh`, or by hand after a plan update.
  Refusal: a missing baseline is seeded from `--plan`, never an error.
  `--self-test` drives each slip kind, the 12 h filters and the ack forms
  beside their null controls.
