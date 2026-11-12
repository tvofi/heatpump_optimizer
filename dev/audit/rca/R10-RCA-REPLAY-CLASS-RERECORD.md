# R10-RCA-REPLAY-CLASS-RERECORD

**Defect.** The scheduled nightly at d08ed31049 (run 42934263129) read the
synthetic clean cpu_ratio 1.7266 at class ref40 under that class's budget
floor 1.9937. The budget rested on two draws that predate 17bb738485 (one BLAS
ThreadpoolController, #3349), which cut the cycle's CPU on CI's runners to
0.61-0.66x.

**Cause.** The cut is a level shift in every class's cpu_ratio. The re-record
procedure re-derives the classes a run has drawn since the change. Its unit,
the drawn class, is wrong: the runner classes that were not drawn since the
shift kept budgets centred on pre-shift readings, and so will fail the same way
when next drawn.

**Process state: (c)** the stated re-record procedure was obeyed and its unit
is wrong.

**Countermeasure.** `level_shift_offenders` (tests/replay.py), the
`cycle_cost:level_shift` control, orders each class's clean draws by created
time. A level shift at T is every draw at or after T under the floor
(budget/2) that the draws before T derive. Every other class must then hold a
draw at or after T, or a declared cut (`COST_CUTS`) must explain the shift;
otherwise it names "class X rests wholly on draws before the shift class Y
shows at T" and prints the classes examined. Registered in
tools/policy/field_coverage.mjs as the `replay_cuts` arm;
`replay_draws.py shift [--table T] [--no-cuts]` runs it over any table.

**Demonstration** (`replay_draws.py shift --no-cuts --table <tsv>`, tables from
`git show <sha>:tests/replay_cost_draws.tsv`):

| table | result |
|---|---|
| d08ed31049 | red, names ref23, ref28, ref31, ref38, ref40, ref53 |
| 6715d97332 | green, 7 classes examined |
| 078780e687 | green, 7 classes examined |
| fix head, `--no-cuts` | red (the cut declaration dropped) |
| fix head | green, 7 classes examined |

**Cost.** One pass over a 7-class TSV inside tests/replay.py; no extra CI job.
