# RCA — CPU gate blind to a regression outside its sampled work (round 9, N=3)

Seat: round-9 RCA, performance classes. Baseline `1936d5ca` (v6.7.1); prototype
cut from `origin/main` `db878b29`. Box: shared 4-vCPU Linux container, Python
3.14.0rc2, BLAS pinned to 1 thread, load average 10-17 from other sessions —
counts exact, CPU provisional. Harnesses and outputs beside this file.
Companion: `../avoidable-interpreter-bound-recomputation/RCA.md`, whose barrier
is this class's third part.

## Root cause

### 1. Cause (reproduced at 1936d5ca)

**Every channel the CPU gates judge is either an aggregate CPU ratio or a count
at a hand-named seam over a hand-listed population, and the one self-check that
sizes them (`DETECTION_TARGET`) proves each figure can see a 2x of itself, never
a 2x of a component it dilutes.** A component with share *s* of its aggregate
moves the aggregate by 1+*s* when it doubles; the aggregates' factors are 3.0x
(per-scenario CPU), a sqrt(2) band on a mean over 51 (sweep), and a sqrt(2) band
on the whole cycle (replay). So a 2x anywhere outside a named seam or a listed
scenario is invisible until *s* approaches 1. The three instances are the three
ways work can sit outside:

| instance | outside what | reproduced here | shipped verdict |
|---|---|---|---|
| D9-s2-03 | the named simulate seams | `peak_cost_batch` run twice on `winter/tariff`: solve CPU **1.61x** (`../avoidable-…/evidence/share.txt`); evaluations 764/764 and simulate 1.0000x (`demo_tariff2x.txt`) | per-scenario 1.61 < 3.0; both counts 1.000x; sweep, derived from the recorded table times the measured shares (8 tariff scenarios, 4,018 of 6,631 recorded ratio units, share 0.47-0.62): **1.29-1.38x < 1.414** — derived, not run |
| D9-s2-02 | the solve (the loop thread) | loop thread doubled exactly (`evidence/demo_loop.out`): whole-cycle `cpu_ratio` 2.85 against clean 2.18-2.39 | **0 offenders** against the shipped `COST_BUDGETS` (3.576) |
| D9-s2-71 | the listed scenarios | `evidence/demo_axes.out`, shipped sweep | **6 production axis values unsampled**: layouts `single_tank_valve`, `two_tank_4way`, `valve_upper_direct_slab`; valve modes `manual`, `smart_read`, `smart_write` — 0 of 51 built plants throttle |

Valve solves cost 1.5x-3.2x the same-season two-zone DHW control on this box
(10.86 / 8.98 / 18.65 s against 5.89 s, `evidence/valve_cost.txt`).

**Class search.** The same shape one level up: `tests/replay.py`'s coverage
check is `COST_FILES`, a hand list of five files (#1544); and S5's own
recompute enumerator keyed loops to named qualnames and missed the terminal
closure (companion RCA). Both are populations written down rather than derived.
The one place the gate already derives its population from production —
`metered_seam_cut`, the simulate surface read from `ThermalModel`'s source
(cf499947, round-6 D9-02) — is the pattern this barrier generalises; it was
applied to one axis only.

### 2. Process state: **(c)** — followed, and did not produce the intended result

The process is "fix the finding by adding the channel the finding measured, and
let `DETECTION_TARGET` prove the channel can see a 2x". It was followed every
time, and every round found the next unnamed place (`git log -S` on
`tests/stress.py` / `tests/replay.py`, register rows in `docs/audit-2026-09.md`,
`tools/audit/round8/D9/report-s2.json`):

| round | blind spot found | channel added |
|---|---|---|
| R1 | D9-03 one ratio over a 1913x spread; D9-04 no memory line | #145 per-scenario budgets, memory (2026-09-02) |
| R2 | D9-02 2x invisible; pin/cap paths *"UNSAMPLED"* | #378 evaluation count (#346); three hand-picked zero-range scenarios |
| R4 | D9-06 2x memory invisible | #949 |
| R5 | D9-01 kernel run twice; D9-07 per-call kernel cost | #1229 simulate count (09-19); `634a9424` kernel cost (09-21) |
| R6 | D9-02 DHW kernel unmetered | `cf499947` DHW seam + `metered_seam_cut` (09-22) |
| R7 | D9-03 simulate channel blind to batch-vs-scalar | — |
| R8 | D9-s2-01 no budget reaches the coordinator cycle | `COST_BUDGETS` whole-cycle ratio in replay |
| R9 | D9-s2-02 (R8's fix is blind to the loop share), -03, -71 | — |

The R8 -> R9 pair is the proof of state (c): R8's fix added exactly what R8
measured (a whole-cycle ratio), and R9 measured that ratio at 1.126x under a
doubled loop thread. The `DETECTION_TARGET` docstring states the obeyed rule and
its limit in one sentence: *"this pins every observed figure into (budget /
DETECTION_TARGET, budget]"* — every figure, never the components under it.
Not (d): the valve topologies (v3.7.0, 2026-08-23) predate the per-scenario
budgets (#145, 2026-09-02) and the sweep's scenario list.

### 3. Cost test

Unit: wall-clock seconds per audit round (9 rounds in 26 days, 2.9 days each).
Stress runs per round: 329 merged PRs in 26 days = 36.6 per round, times at
least a PR run and a main push = **>= 73**. Replay is nightly: 2.9 runs per
round.

**P(recurrence)** — measured: a CPU-gate blind spot was found in **8 of 9
rounds** (R3 is the exception), table above. What is *not* measured is the rate
at which a real regression lands in a blind spot; no shipped escape in the
record is attributed to one.

**cost(defect)** per occurrence, user side, for the regressions the demos
inject (x7 Pi factor is the register's stated assumption; 48 solves/day):
a doubled `peak_cost_batch` adds 7.1 s per capacity-tariff solve here
(18.81 - 11.66 s), x7 x 48 x 2.9 = **~6,900 s per round per tariff
installation**.

**cost(countermeasure, recurring)**, per part:

| part | standing cost, measured | per round |
|---|---|---|
| plant-axis coverage check | 0.09-0.13 s per stress run (51 plants read, nothing solved) | ~9 s |
| the scenarios it forces (three valve plants, winter members) | 38.5 s solve CPU per tree, x2 trees per stress run | ~5,600 s |
| loop-thread figure, nightly | one more replay of the fixture per night: 20.5-22.4 s (the whole lane, four replays, 125.6 s wall) | ~65 s |
| production-call channel (D9-s2-03) | carried and costed in the companion RCA: 78 s per run (15-scenario subset) | ~5,700 s |

**Verdict.** The coverage check and the loop figure pass at any non-trivial
probability (~75 s per round against one tariff installation-round of 6,900 s).
The production-call channel passes as the companion RCA states. The three
valve scenarios are the one part whose cost is a sampled path's full price
(~5,600 s per round); cheaper members (summer, one zone where the topology
allows) are the file's own precedent for the zero-range trio and were not
measured here. Whether a throttling-valve path is worth sampling at that price
is **tvofi's call**, and so is each new `stress_budgets.json` entry.

### 4. The class-eliminating barrier: derive the sampled population from production

Three parts, one principle — the gate's population is read from production,
not written down — and each closes one way work sits outside the sample:

1. **Work outside the named seams (D9-s2-03)** — the production-call channel
   (companion RCA): every call production bytecode executes, per file, both
   trees side by side, judged at 5 % of vouched growth. `tariff2x` arm:
   **fires** (`winter/tariff` 1.482x) where every shipped channel is silent;
   null arm: **identical** counts, no fire.
2. **Paths outside the listed scenarios (D9-s2-71)** —
   `plant_axes`/`unsampled_plant_axes` in `tests/stress.py`: every selectable
   `topology.LAYOUTS` key and every `mixing_valve.MODES` value must be reached
   by some scenario's *built* plant (sentinel `optimize`, nothing solved).
   - fail: shipped sweep, **6 unsampled**;
   - pass: plus three valve plants from `tests/golden.py`'s own configs (one
     re-moded to `smart_read` — the check caught the first attempt missing it),
     **0 unsampled**;
   - null: the valve plants alone, **2 unsampled** (`layout:no_valve`,
     `valve_mode:none`) — not vacuous; a combo that never reaches `optimize`
     raises rather than shrinking the population.
3. **Work outside the solve (D9-s2-02)** — `loop_cpu_ratio` in
   `tests/replay.py`: the cycle's thread CPU less its executor jobs (the test
   double runs jobs inline), plus the entity reads, over the same reference,
   banded exactly as `cpu_ratio` and perturbed nightly by a `loop` arm.
   - fail at shipped: loop doubled -> **0** shipped offenders;
   - fires with the figure: **1** (`loop_cpu_ratio 0.784 over its budget
     0.5214`); whole cycle doubled -> 2; clean x3 -> **0** (0.321-0.369);
   - in-memory mutant dropping the figure turns `control:cycle_cost:loop_thread`
     False; with the budget at its placeholder 0 the lane refuses ("no recorded
     budget") rather than passing. The real lane, both ways: with
     `REPLAY_LOOP_RATIO=0.5214` **77 of 77 checks pass**, including the new
     `cycle_cost sees a doubled cycle loop` (0.7404 against clean 0.4006);
     unset, `cycle_cost` **FAILs** with three "no recorded budget" offenders
     (`evidence/replay_lane_recorded.txt`, `evidence/replay_lane_unrecorded.txt`).

**One barrier or two?** One *principle*, one shared part. The production-call
channel is the whole barrier for the recompute class and the D9-s2-03 third of
this one: a CPU gate that sees the solve's interpreter work does catch
recomputation — `defect` arm 4 of 5 scenarios — and does so at 5 %, far under
any CPU factor this file can hold. It cannot cover this class's other two
thirds: a count cannot see a plant no scenario builds (D9-s2-71), and the stress
sweep never runs the coordinator (D9-s2-02; S5 measured
`stress_cycle_functions=0`). So F10.2 carries three parts, of which one is
shared, and both classes' barriers are complete only together.

**Residual, stated:** a per-call slowdown outside the kernels that adds no call
(the channel counts, the kernel-cost channel times only the seams); replay's
`COST_FILES` stays a hand list; the loop figure is sampled on one fixture.

**Ratchet.** Test files only; no production line, no structure metric, no new
tracked file. Two budget decisions are needed and **not taken here**: the
`loop_cpu_ratio` entry in `COST_BUDGETS` (prototype placeholder `0`; this box's
record is 0.5214, not a canonical-runner value) and the valve scenarios'
`stress_budgets.json` entries.

## Plan fold

- **Lands in F10.2, as planned**, with the companion barrier. Branch
  `handoff/r9-rca-cpu-gate-blind` = the production-call channel commit (same
  code as the companion branch) plus this class's two parts.
  Files: `tests/stress.py` (**code-owned**), `tests/replay.py` (not
  code-owned), and — for the fixer, not the prototype — `tests/stress_budgets.json`
  (new entries through `budget-raise-gate`). None is policy.
- **Lines:** 0 production. Test: +364 in `tests/stress.py` (287 shared + 77),
  +72/-10 in `tests/replay.py`, as prototyped; the fixer should land ~260
  after trimming comments, plus 3 scenario specs and their budget rows.
- **Needs tvofi (already an F10.2 gate):** the `loop_cpu_ratio` budget value,
  recorded on the canonical runner; whether to sample throttling-valve plants at
  ~5,600 s per round or pick cheaper members; the production-call channel's
  subset-vs-full choice (companion RCA).
- **No change to the plan's PR set for this class**; the companion RCA adds
  F2.5 and the edge F2.5 -> F10.2.

## Figures

Enumerators (prototype worktree root, `PYTHONPATH=tests/hastub`):

- `python3 demo_axes.py` -> `demo_axes.out` (`RESULT arm=… unsampled=`).
- `python3 demo_loop.py` -> `demo_loop.out` (`RESULT arm=… shipped_over= prototype_over=`).
- `tests/replay.py` with and without `REPLAY_LOOP_RATIO` -> `evidence/replay_lane_*.txt`.
- D9-s2-03 arm: `../avoidable-interpreter-bound-recomputation/demo_calls.py tariff2x …`.
