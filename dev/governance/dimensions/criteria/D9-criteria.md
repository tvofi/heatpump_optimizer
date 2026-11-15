# D9 acceptance criteria: the Pi-class budget per cost centre

> CPU and memory resource efficiency — target hardware is
> Raspberry-Pi-class running all of Home Assistant. Measure, don't assert
> [...] and whether the stress budget should become a real gate

— the owner, `D9.md`. Each cost centre is a metric `D9.md` defines, measured
by its harness there.

Drafted by a fixer seat under mandate 6893738184 (scope all);
binding as the owner's words until the owner rewrites them.
A finding names the statement it fails.

`tests/stress_budgets.json` records the code's own peaks per scenario so
that `tests/stress.py` can see a regression against them; it is no budget.
A cost under its recorded row and over a budget here fails; a cost over its
row and inside every budget here is a regression, not a D9 finding.

## The Pi extrapolation

CPU is measured on the seat's host, pinned to one core with BLAS threads at
one (`D9.md`, Traps), and multiplied by **F**, the time of
`tests/stress.py`'s `reference_solve` on one Raspberry Pi 4 core over its
time on the host. Until a seat measures F on Pi-class hardware, F = 5,
an assumption (Cortex-A72 at 1.5 GHz against a current desktop core) the
finding states as one. Bytes are not scaled.

## Budgets (CPU figures are Pi seconds, after F)

- **B1 solver CPU per cycle**: the sum over a cycle's full solves of their
  process CPU, at most 60 s: a tenth of one core over the shortest
  optimisation interval the options flow accepts (10 min). Fail: above.
- **B2 longest GIL hold** on the event loop thread: at most 100 ms, the
  interval asyncio reports as a slow callback. Fail: above.
- **B3 loop-thread work per cycle**: at most 0.5 s. Fail: above.
- **B4 retained growth**: the retained-bytes slope after 200 warm-up cycles,
  times the 52,560 cycles of a year at the shortest interval, at most 10 MiB
  (199 bytes per cycle). Fail: above.
- **B5 memory peak**: per solve, `rss_attrib_mb` as `tests/stress.py`
  measures it at most 32 MB and the solving process's `rss_peak_mb` at most
  128 MB. Fail: either above.
- **B6 payload**: each entity's recorded attributes at most 16,384 bytes of
  JSON (the recorder's own limit), and all recorded attribute bytes at most
  5 MB per day at the shortest interval. Fail: either above.
- **B7 gradient cost**: simulate-step-equivalents per gradient evaluation
  at most the horizon's step count per simulated trajectory (the owner's
  "96 ... not ~9,300" at the default horizon). Fail: above.

Full solves per cycle carry no budget of their own: B1 prices them.
