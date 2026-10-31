# RCA — avoidable interpreter-bound recomputation in the solve (round 9, N=5)

Seat: round-9 RCA, performance classes. Baseline `1936d5ca` (v6.7.1); prototype cut
from `origin/main` `db878b29`. Box: shared 4-vCPU Linux container, Python
3.14.0rc2, BLAS pinned to 1 thread, load average 10-17 from other sessions
throughout — every count below is exact, every CPU figure is provisional.
Harnesses and their outputs are beside this file (`demo_calls.py`,
`evidence/`); the measurements they print are the only source of the figures.

## Root cause

### 1. Cause (reproduced at 1936d5ca)

**The batched objective's cost terms are per-row Python loops by design, and the
fix that created them was accepted on the finding's proxy count, not on its
cost.** R4-D9-05 found `_comfort_terms` re-entered 97 times per gradient (33 % of
the solve). #985 (`ba811ce5`, v6.4.4) replaced the re-entry with batch "twins"
whose rows "run the scalar body verbatim on its own freshly allocated per-row
arrays" — a `for b in range(n_rows)` loop — because an axis-1 reduction
re-planned 19 of 51 stress scenarios on CI's x86_64 (bitwise parity). Its commit
message records what was re-measured: *"The win the finding counted -- no
per-row helper re-entry -- is unchanged: 97.02 -> 1.02 comfort-terms entries per
gradient."* The CPU was not re-measured; `RELEASE_NOTES.md` calls the result
"vectorized". `tools/audit/briefs/fixer.md` step 15 then made the shape the
rule: *"Where the contract is bitwise, run the SCALAR EXPRESSION per row"*.
Nothing downstream measures interpreter work outside the named seams below a
3.0x per-scenario CPU factor (see the cpu-gate-blind RCA), so the loops stayed.

Which side moved (`git log -S`): the four per-row twins —
`HeatPumpOptimizer._comfort_terms_batch`, `cycling_penalty_batch`,
`_terminal_cost_batch.<locals>.cost_batch` and `tariff.peak_cost_batch` — were
all born in `ba811ce5`; none predates it.

Reproduction (`evidence/share.txt`, wrapper timing with `time.process_time`,
perturbation `--double NAME` runs the wrapped function twice):

| seam | scenario | share of solve CPU | perturbation |
|---|---|---|---|
| `tariff.peak_cost_batch` (per-row loop) | winter 2z DHW capacity tariff (= sweep `winter/tariff`) | **0.624** | doubled: share 0.764, solve 1.61x (predicted 0.768 / 1.62x) |
| same | `shoulder/tariff+pv+cycle` (the gate's dearest scenario) | **0.473** | — |
| `_comfort_terms_batch` (D9-s1-01) | `winter/tariff` / `shoulder/1z/dhw` | 0.115 / 0.271 | row-vectorised twin (below) |
| `cycling_penalty_batch` (RC-sw1) | `shoulder/tariff+pv+cycle` | 0.043 | — |
| `_terminal_cost_batch.<locals>.cost_batch` | `winter/2z/dhw` / `shoulder/1z/dhw` | 0.022 / 0.031 | doubled: 0.037 |

The row-vectorised comfort twin (a one-hunk demo commit `45492d88`, axis-1
reductions) is **bit-identical on this box**: objective, evaluations and
simulate counts equal on **51 of 51** sweep scenarios (`evidence/rows_defect.txt`
against `evidence/rows_fixed.txt`), and the per-row loop it removes is
2.2-12.6 % of each scenario's production calls (9,741-517,779 calls on the five
demo scenarios, `evidence/demo_defect.txt`); under the meter the full sweep
costs 341.6 s CPU with the loop and 281.3 s without. That parity is per-box
(`fixer.md` step 15 and the verifier carry-in on Fortran-order batches both
stand); it is shown here only to size the recomputation.

### 2. Class search — what else the same cause reaches

Instrument: `sys.monitoring` counting every `PY_START` and `CALL` executed by
production bytecode, per function (`evidence/callmap_base_2zdhw.txt`,
`winter/tariff`, 6.77 M calls when counted by code object).

- **New, and the largest member: `tariff.peak_cost_batch`.** 62.4 % of a
  capacity-tariff solve, 47.3 % of the gate's dearest scenario. Its row loop
  calls `metering_windows` 37,070 times, `_day_peaks` 37,064,
  `_plateau_aware_day_max` 37,063 and `_smooth_topk_sum` 18,063 (2.52 M calls,
  37 % of all production calls). No round-9 finding, sweep, issue or fix brief
  names it (`grep -r peak_cost_batch` over `judge/ sweep/ issues/ fix/` is
  empty): the S5 enumerator scanned `optimizer.py` and `ThermalParameters` only,
  and no D9 harness solved a tariff scenario.
- **Mis-disposed by S5: `_terminal_cost_batch.<locals>.cost_batch`**
  (`optimizer.py:2164` at baseline). S5 keyed the loop to the outer builder
  (called once) and wrote *not applicable*; the loop is in the returned closure,
  entered 382 times per solve, 2.2-3.1 % of the solve. The enumerator's
  qualname keying cannot see a loop inside a closure — every per-row twin #985
  built as a closure has this blind spot.
- **Excluded, measured:** the per-step helpers with the highest entry counts are
  not material. Isolated CPU of each at its per-solve count against the same
  solve (`evidence/micro.txt`): `ThermalModel.effective_heat_loss_coefficient`
  (298,272 entries) 0.34 %, `ThermalModel._stability_substeps` (74,496) 0.62 %,
  `mixing_valve.is_throttling` (112,711) 0.08 %,
  `ThermalParameters.lower_floor_heat_loss_learned` (149,090) 0.07 %.
  D9-s1-71's DHW helpers stand on the finder's own measurement; the widened
  ThermalParameters properties S5 folded into it are, on this measurement,
  under 1 % each.

### 3. Process state: **(c)** — followed, and did not produce the intended result

Three processes touched this class; each was obeyed.

1. **The fix process for R4-D9-05** was followed: failing test, parity pins,
   review PASS (`#985`, `docs/plan-2026-09-open-issues.md` row: *"Fix review
   round 1 PASS … at frozen head db19d29"*). Its acceptance metric was the
   finding's counted proxy (helper entries per gradient), which a per-row loop
   satisfies while the work stays; `peak_cost_batch`'s docstring says so in so
   many words: *"the per-row re-entry -- not the arithmetic -- is the
   recomputation round 4 (D9-05) counted, and this twin is what the
   recomputation-count pin reads"*.
2. **`fixer.md` step 15** was followed, and it prescribes the per-row shape.
3. **The stress gate** was followed and cannot see it (the cpu-gate-blind RCA:
   named-seam counts plus a 3.0x per-scenario CPU factor).

Not (a): a process existed. Not (b): nobody skipped a step. Not (d): the bitwise
contract and the gate predate #985. A firmer instruction ("vectorise properly")
would be the (b) countermeasure, and step 15 shows why it fails — the bitwise
contract is real, so an instruction alone re-produces the loop.

### 4. Cost test

Unit: wall-clock seconds per audit round (9 rounds in 26 days,
2026-09-01..26: 2.9 days per round).

**P(recurrence)** — measured class frequency, rounds with at least one judged
avoidable-recomputation-in-the-solve finding: R1 (D9-01), R2 (D9-01, D9-03,
D9-04), R4 (D9-05), R8 (D9-s1-01), R9 (five) = **5 of 9 rounds, 0.56**
(`docs/audit-2026-09.md` registers, `tools/audit/round8/D9/report-s1.json`;
R3 D9-01 refuted, R7 D9-02 excluded as an owner-mandated design cost).

**cost(defect)** per occurrence, user side only (the audit seats each instance
consumed are real but unmeasured, so the verdict does not rest on them). Solve
cadence 48/day (`DEFAULT_OPTIMIZATION_INTERVAL` 30 min). Pi factor x7 is the
register's stated assumption (R2 D9), not a measurement:

- a `peak_cost_batch`-sized instance: 0.624 x 11.66 s = 7.3 s per solve here,
  x7 x 48 x 2.9 = **~7,100 s per round per capacity-tariff installation**;
- a `_comfort_terms_batch`-sized instance: 0.271 x 1.886 s = 0.51 s per solve,
  x7 x 48 x 2.9 = **~500 s per round per installation**.

**cost(countermeasure, recurring)** — the production-call channel's two
captures, run side by side, per stress run: a metered full sweep costs
**342 s CPU per tree** on today's tree and 281 s once the comfort loop is gone
(`evidence/rows_defect.txt`, `rows_fixed.txt`, 51 scenarios); the 15-scenario
one-per-family subset (cheapest member of each `(two_zone, dhw, tariff, pv,
cycling, pin, cap, building)` family) costs **90 s / 78 s**.
Stress runs per round: 329 merged PRs in 26 days = 36.6 per round, times at
least one PR run and one main push = **>= 73 runs**. Standing:
73 x 78 = **5,700 s per round** (subset) or 73 x 281 = 20,500 s (full sweep),
after F2.2.

**Verdict.** Subset form: 5,700 < 7,100 x 0.56 x N_tariff, i.e. it pays at
**2 capacity-tariff installations** (or 21 non-tariff ones) before a single
audit seat is counted. The full-sweep form needs 6 tariff installations. The
installation count is not in the tree; the subset form is recommended, and the
full form is tvofi's call if the stress lane's wall matters less than coverage.

### 5. The class-eliminating barrier: a production-call channel in the stress gate

**Form.** A third count channel beside evaluations and simulate steps: every
call production bytecode executes, per production file, per scenario, on the
branch and the merge base, captured side by side in fresh interpreters by one
driver text (`CALLS_PROBE_DRIVER` embeds `production_calls`' own source).
Judged on unchanged plans against the growth the evaluation and simulate counts
vouch for (#1208's restarts pass), at a **5 % allowance**. It names no seam:
the package's files are the population, which is what makes it class-shaped
rather than one more named channel. It keeps the timed sweep unmetered, so no
CPU budget moves. Refuses a scenario the meter did not count, a missing
baseline row, and coverage under the existing 40-scenario floor.

**Why the allowance can be 5 % when the CPU factors cannot go under 1.8x:** the
count is exact. Two captures of one tree in separate interpreters are
call-for-call identical (`evidence/demo_null2.txt`: `identical_calls=True` on
5 of 5). Legitimate movement, measured on every first-parent merge that touched
a solver file from #1091 to #1605, merge against first parent, three winter
scenarios each (22 merges, 62 judged scenario-pairs, `evidence/history.txt`):
at 5 % it fires on **2 of 22 merges**, 3 scenario-pairs; at 10 %, the same 2
merges; at 2 %, 3 merges. Every other merge moved unvouched calls by 2.2 % or
less, most by under 1 %.
- **#1370** (`9ca86655`): +12.7 % on `winter/2z/space`, +7.1 % tariff, +3.5 %
  dhw. It added a per-step `is_throttling` and buffer-UA derivation inside
  `_stability_substeps` — this class's own shape, at about 1 % CPU. A true
  positive of low severity: the fixer hoists it or vouches for it.
- **#1282** (`e7139a7f`, polish every candidate, owner override): +11.4 %
  unvouched on `winter/tariff` beyond the 1.43x its extra evaluations vouch
  for — the per-candidate L-BFGS-B restart's own bookkeeping. A deliberate,
  sanctioned cost; under the barrier it merges with a stated re-record, which
  is the ratchet's existing discipline, not a new one.

So the price is about one acknowledged re-record per 11 solver merges. The
allowance has a ceiling as well as a floor: the defect arm's call growth
(5.7-12.6 % on the scenarios it fires) overlaps #1370's (3.5-12.7 %), so an
allowance at or above ~12 % would silence the defect this class is about. 5 %
sits between the 2.2 % legitimate noise and the defect's 5.7 % lowest fire.

**Fail / pass / null** (`demo_calls.py`, 5 scenarios each, verdicts from the
prototype's own `calls_drift`, beside the shipped `work_over_verdict`):

| arm | here vs base | `calls_over` | shipped count channels over |
|---|---|---|---|
| defect: #985's per-row comfort twin re-introduced after its fix | `1936d5ca` vs `45492d88` | **4 of 5** (1.057x-1.126x; `optimizer.py` +9,741 to +517,779); full sweep **42 of 51** over 1.05x, family subset **10 of 15** (`rows_*.txt`) | 0 |
| fixed | `45492d88` vs `1936d5ca` | **0** | 0 |
| null (healthy tree against itself) | `origin/main` vs `origin/main` | **0**, calls identical | 0 |
| D9-s2-03 shape: `peak_cost_batch` run twice | `939ea6f9` vs `1936d5ca` | **1** (`winter/tariff` 1.482x, `tariff.py` +3,921,969) | 0 |

The one scenario that did not fire on the defect arm is `winter/1z/dhw`
(1.0233x): the comfort loop is 2.3 % of its calls. Detection needs one covered
scenario per code path, which the sweep's two-zone members give.

Mutation (in-memory, no pool): the three proof checks in the prototype
(`calls_over_verdict` on an identical count, on #985's measured 4,641,468 vs
4,123,689, and on 1.80x vouched growth) are (True, True, True) healthy; a
mutant that stops dividing by the vouched ratio turns the third False; a mutant
that never reports over turns the second False.

**What it does not see (residual, stated):** an instance under 5 % of every
scenario's calls — the terminal twin alone (2-3 % CPU) and any single
`ThermalParameters` property; and a per-call slowdown outside the kernels that
adds no call (a costlier numpy op on the same call count). Both are the
kernel-channel shape one level out; neither is a round-9 instance.

**Ratchet.** `tests/stress.py` only: no production line, no
`tests/structure_budgets.json` metric moves (every metric there is production),
no new tracked file. It needs **no** `*_budgets.json` raise. The branch is
under the structural ratchet by construction.

## Plan fold

- **Barrier lands in F10.2, as planned**, and is the same code as the
  cpu-gate-blind RCA's third part (D9-s2-03): one channel, carried once.
  Prototype: `handoff/r9-rca-avoidable-interpreter-bound-recomputation`
  (`tests/stress.py`, +287 lines, of which roughly 60 % comment/docstring).
  Estimate for the fixer: **0 production lines, ~200 test lines** after
  trimming; `tests/stress.py` is **code-owned** (tvofi review, already on F10.2).
  Not policy. It adds no budget-table entry. The allowance constant is new: the
  fixer re-derives it at the F10.2 merge base with `evidence/hist_eval.py`.
- **Plan change — a new PR for the class's largest member.** `peak_cost_batch`
  (tariff.py, 47-62 % of a capacity-tariff solve) and the mis-disposed terminal
  closure (`optimizer.py`) are new sweep-type instances of this class. F2.2 is
  at its five-finding cap (four findings plus RC-sw1), and `tariff.py` is F3's.
  Proposed **F2.5**: both instances, `optimizer.py` plus `tariff.py` borrowed
  from F3; `after: F2.2, F3.3`. F10.2 gains `after: F2.5`, for the same reason
  it follows F2.2 (budgets recorded on the faster solve). Plan PR count 41 -> 42.
- **Carry into F2.2's brief (and F2.5's), owed before this RCA's barrier PR
  merges (`finding-propagation.md`)** — the orchestrator's to write, since this
  seat writes only here: *"A recomputation fix is accepted on the finding's cost
  metric re-measured on the fixed tree (share of solve, or the production-call
  count), not on the finding's proxy count. #985 met its proxy (97.02 -> 1.02
  entries per gradient) and left a per-row loop that is 62 % of a tariff solve.
  Control: the fix must move the production-call count of the scenario the
  finding measured; `demo_calls.py fixed` is the shape."*
- **Policy proposal for tvofi (state (c), not landed here):** `fixer.md` step 15
  prescribes the per-row loop wherever parity is bitwise. Proposed addition:
  *"A per-row twin removes re-entry, not work; when it is the fix for a
  recomputation finding, re-measure the finding's cost on the fixed tree and
  report it; if parity forbids vectorising, the fix is a recorded partial with
  its remaining share, not a close."* It changes what a fixer must do, so it is
  policy and needs tvofi's approving review.
- **For tvofi:** the installation count the cost test's break-even turns on
  (2 tariff or 21 non-tariff installations for the subset form).

## Figures

Enumerators (run from the prototype worktree root, `PYTHONPATH=tests/hastub`):

- `python3 demo_calls.py {null,defect,fixed,tariff2x} winter/2z/space winter/1z/dhw winter/tariff shoulder/1z/dhw summer/1z/space`
  -> `evidence/demo_*.txt` (`RESULT ... calls_over=` / `shipped_count_over=`).
- `python3 evidence/share.py '<spec>' [--double NAME]` -> shares above.
- `python3 evidence/hist_eval.py 0.02 0.05 0.10` over `evidence/hist/` -> the
  legitimate-movement table.
