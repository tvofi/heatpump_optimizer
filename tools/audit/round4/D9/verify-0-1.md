# D9 verify-0-1 — round 4, panel D9-0, seat 1 of 3

- **Worktree**: `/Users/timmalmstrom/.zcode/workspace/default/audit-r4-verify-D9-1`
  (detached at `ae2a60b58e22ae06d14554fa131612f726ef53b7`, branch
  `claude/13-dimension-audit-920935`; production code byte-identical to the
  finder's baseline `7dd68dd` for everything measured here).
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from this worktree's root, five
  BLAS variables pinned `1` before numpy per the contract.
- **Lock**: `tests/gate_lock.py take --label d9-verify-1` at the start
  (previous lease from the dead run had expired; the tool took it cleanly),
  renewed between every command, released at the end. Every run's
  exclusivity was confirmed by process (`ps aux | grep -E
  "[s]tress\.py|[t]ests/run\.sh"` printed beside the RESULTs;
  `concurrent_gate_procs=0` on every timing run except my own deliberately
  concurrent full-gate run, where the 1 was my own gate).
- **Box conditions**: load1 quoted, not gated, per `tools/audit/README.md`.
  Other verifier panels were running: load1 spanned 2.5–19.1 across this
  session. Every number below is either a count (exact), a rational of
  committed constants (exact), or a ratio measured inside one process;
  absolute seconds are marked PROVISIONAL and nothing rests on them.
- **Stance**: refute-first. Attacks run per finding are listed with their
  outcomes.

## Votes

| id | vote | severity |
|---|---|---|
| D9-05 | **verify** | medium |
| D9-06 | **verify** | medium |
| D9-INST | **verify** | low (instrument) |

## D9-05 — verify, medium

**Structure, by source.** `optimizer.py:objective_batch` exists twice, at
`:3432` (space-only) and `:5528` (with-DHW); each calls
`ThermalModel.simulate_trajectory_batch` once and then loops
`for b in range(...)` at `:3454` / `:5552`, calling `_comfort_terms`
(`:1560`), `energy_cost_of`, `cycling`, `capacity` and `terminal_cost` once
per row. The claim's code shape is exact.

**Finder's harness re-run** (`h9_batch_cost_loop.py`, per its header,
lock held, `concurrent_gate_procs=0`, `thread_factor=0.999998`,
load1 13.5–14.5): `comfort_terms_calls_per_solve=29591` (exact),
`comfort_terms_calls_per_gradient=97.0197` (exact), `batch_rows_per_gradient=96`
(exact), `comfort_terms_cpu_share_pct=32.2979` (finder 33.331, quiet
32.690; inside the ±5 pp band), `simulate_batch_cpu_share_pct=38.3714`,
`comfort_over_simulate_batch=0.841718`, flat-price null delta `+0.8278 pp`.
Perturbation `H9_HORIZON=12`: `49.0299` calls/grad, `48` rows/grad, share
`32.6381` — count halves, share invariant; direction down; matches the
finder's `h9_h12.out` line for line.

**My own harness** (`d9_own_d9_05.py`, written for this seat): a different
instrument (accumulated `time.process_time` — CPU — inside the hook,
divided by whole-solve CPU, where h9 used wall `perf_counter`/wall) and an
independent solve builder (inputs built directly from `tests/profiles.py`,
no `d9common`). Results (`load1` 16.5–19.1, counts unaffected):
`own_comfort_calls_per_solve=29591` (exact), `own_comfort_calls_per_gradient=97.0197`
(exact), `own_comfort_cpu_share_pct=33.5109`, `own_batch_cpu_share_pct=37.9051`,
`own_comfort_over_batch_cpu=0.884074`, flat null delta `+1.00119 pp`; at
`OWN_HORIZON=12`: `49.0299` / `48` rows / share `31.0173`. The CPU-ratio
instrument lands within 0.2–0.8 pp of the finder's wall-ratio figure, so
the wall/CPU distinction is immaterial here (single-threaded solve,
`thread_factor≈1.0`). `own_comfort_calls_minus_rows=311` against `njev=305`:
the loop count is the batch width plus the one scalar trajectory scipy
evaluates per gradient — the count is the batch's, not a constant.

**Attacks.**
1. *Contention* — counts bit-identical at load1 up to 19; shares are
   same-process ratios; my CPU-share instrument is immune to inter-process
   load by construction. Survived.
2. *Null control* — flat prices move the share by ≤1.0 pp against a 33 %
   effect: the cost is the batch shape, not the price structure. Holds.
3. *Perturbation* — horizon halving halves the count both in the finder's
   and my harness. Direction down. Holds.
4. *Aggregate artefact* — none: one default scenario, plus the null arm,
   plus the perturbation arm; no grid to drop cells from.
5. *Severity* — bounded, silent CPU cost (a third of an out-of-process
   solve), no wrong number, no user-visible defect. Medium is earned;
   high would not be.

## D9-06 — verify, medium

**Finder's harness re-run** (`h7_memory_gate.py`, per its header, lock
held): every FINAL number exact — `scenarios_recorded=51`,
`memory_top_n=6`, `scenarios_never_memory_probed=45`,
`min/max_rss_multiple_required_to_fail=2.52905/2.64294`,
`scenarios_where_2x_rss_passes=51`, `min_traced_multiple=2.07637`,
`scenarios_where_2x_traced_passes=51`, `rss_fail_threshold_mb=248.1`,
`inject2x_rss_rule_fires=False` (executed), `inject2x_traced_rule_fires=True`.
Perturbation `H7_PERTURB=nofloor`: `memory_budget_factor=1.05` leaves
`min_rss_multiple_required_to_fail` at `2.52905` (the floor dominates; the
factor cannot move the threshold), `nofloor_min=1.05` exactly. Both
reproduce.

**My own arithmetic** (inside `d9_own_d9_06.py`): the constants re-derived
by regex from the *source text* of `tests/stress.py` (not by importing it)
and the table read directly — identical numbers (2.52905 / 2.64294 / 51 /
51 / 45 / 2.07637). Recorded RSS range 91.3–98.1 MiB; 0.5 × 98.1 = 49.1 <
150, so the additive floor dominates every scenario.

**My own executed injection, through the gate's own entry point.**
`tests/stress.py` was edited in this worktree (restored byte-identical
afterwards, sha256 `7a017970…` verified): `build_case` gains a block,
inert unless `D9V1_INJECT=1` and the spec is exactly winter/pv
(`two_zone, dhw, pv, no tariff, cycling 0.0, no building, 24 h`), that
holds RSS to ~2.1× the 98.1 MiB record via a fully page-written anonymous
mmap (resident, invisible to `tracemalloc` — the numpy-internal blind spot
`stress.py:1512` documents) and traced to exactly 2 × 3.46 = 6.92 MiB via
a `bytearray`. Controls through the real `--memory-probe` subprocess:

| arm | probe RSS | probe traced |
|---|---|---|
| clean winter/pv | 80.3 MiB | 3.46 MiB |
| injected winter/pv (repeat runs) | 185.8–223.8 MiB (memory-pressure scatter; ≥1.92× record) | **6.92 MiB every run (exactly 2.00×)** |
| injected env, off-target scenario (winter/cycle) | 84.1 MiB | 3.48 MiB — edit inert |

**The confirming full-gate run** (lock held, `python3 tests/stress.py`,
`D9V1_INJECT=1`, exit 0):

```
-- Memory (D9-04)
  winter/pv   RSS peak  216.8 MiB, traced 6.9 MiB (recorded 98 / 3.5)
  ok  the memory pass probes the recorded peak on each axis
  ok  the probed scenarios' memory peaks stay within their recorded budgets
  ok  every memory-pass scenario has recorded peaks
  ok  the memory pass retains less than 512 MiB of RSS in the parent
...
  ok  the budgets are tight enough to see a 2x regression, uniform or confined to one scenario
ALL 62 STRESS CHECKS PASSED
```

216.8 / 98.1 = **2.21× RSS** and 6.9 / 3.5 = **2.00× traced** — a stronger
injection than the claim requires — and the gate stays green in full,
with the self-congratulating detection line `ok` a few lines below (the
finder said "three lines"; in this run's layout it is five — the wording
is loose, the substance holds: same run, same output, adjacent).

**The detection check is CPU-only, by source.** `_blind` in
`tests/stress.py:2622-2711` is assembled exclusively from
`SOLVE_BUDGET_RATIO`, `SWEEP_BUDGET_RATIO`, `SCENARIO_BUDGET_FLOOR_RATIO`,
`SCENARIO_BUDGET_FACTOR`, `SCENARIO_WORK_FACTOR` — all solver-CPU budgets.
`MEMORY_BUDGET_FACTOR` never enters it. `DETECTION_TARGET=2.0` is enforced
for the CPU rules and for nothing on the memory side.

**The "45 of 51" half, by source.** `_memory_probe_labels()`
(`tests/stress.py:2393-2413`) takes half of `MEMORY_TOP_N` from the
recorded traced leaders and half from the RSS leaders of the *committed*
table — 6 scenarios — in check mode; the other 45 recorded memory budgets
are never compared. Confirmed in the gate output: exactly six probes.

**The `:1512` "cancels" comment is wrong, arithmetically.** The rule is
`probe > recorded + max(150, recorded·(MBF−1))` — additive with an
absolute floor. The ~80–90 MiB interpreter+numpy baseline sits inside both
sides and would cancel under a ratio rule; under this additive rule it
inflates the threshold's denominator-independent slack, which is exactly
why a 2× regression lands at 196–217 MiB against a 248.1 MiB bar.

**Attacks.**
1. *Is 2× the wrong target?* `DETECTION_TARGET=2.0` is `stress.py`'s own
   stated target (`:261`); the CPU rules are sized against it. The memory
   rules are not. No strawman.
2. *Does CI tighten STRESS_MEMORY_FACTOR?* No —
   `.github/workflows/tests.yml:285-295` sets only `GOLDEN_MODE` and
   thread pins; the comment records no STRESS_* knob is set. The defaults
   measured here are what runs.
3. *Is the injection realistic?* Both halves are: the mmap models
   numpy-internal growth that `tracemalloc` cannot see (`:1512`'s own
   documented blind spot), the bytearray models Python-object growth; the
   gate's own probe entry point executed them. The off-target control
   shows the edit itself changes nothing.
4. *Flaky-green?* The gate printed ALL 62 PASSED with zero failures; no
   CPU red occurred to hide behind (and a CPU red would not be the memory
   section anyway).
5. *Severity* — the gate is the defect, not the product; a memory
   regression blind spot on an instrument. Medium, as filed.

## D9-INST — verify, low (instrument finding)

**First half: h2's `thread_factor` is ~1.29 by construction.**
Re-ran `h2_cycle.py` per its header (lock held, `load1=2.50`,
`concurrent_gate_procs=0` — a quiet box, so this is not contention):
`RESULT thread_factor=1.29763`, alongside `msm_entries_per_cycle=0` and
loop/executor CPU consistent with the quiet window's re-takes. Then proved
the mechanism with my own construction harness `d9_own_d9_inst.py`, which
imports **no numpy at all** (nothing that could spin a BLAS pool is
loaded) and runs a pure-Python busy loop on the main thread plus ~30 % as
much on a real `ThreadPoolExecutor(max_workers=1)` thread:
`own_pure_python_thread_factor=1.29743` with
`own_expected_factor=1.29743` (predicted = measured to five digits:
second-thread CPU lands in `process_time` and not in `thread_time`),
idle control `0.999995`. The contract's `> 1.05` rejection rule
(`tools/audit/README.md:51-53`) assumes the ratio is a BLAS-threading
signal; in a harness that deliberately uses a second real thread — which
the README itself mandates for executor-boundary measurements — the rule
is unsatisfiable by construction. The finding's wording is confirmed.

**Second half: h4/h5/h7/h8 print no `thread_factor` beside PROVISIONAL
memory RESULTs.** Code-level: `h4_retained.py:272`,
`h5_worker_footprint.py:165`, `h7_memory_gate.py:186`, `h8_leak_attrib.py:108`
all call `C.telemetry()` with no argument; `d9common.telemetry()` prints
`load1`/`swapins`/`concurrent_gate_procs` only. Executed confirmation:
my `h7` re-run's RESULT block (above) carries no `thread_factor` while
printing `clean_probe_rss_mb_PROVISIONAL` — a memory RESULT the contract
says must be accompanied by one (and rejected if it exceeds 1.05). `h4`
and `h5` headers promise PROVISIONAL RSS RESULTs in the same shape; `h8`
prints byte figures. `h1`/`h9` print per-arm factors and `h6` prints one —
the gap is exactly the four named.

**Supporting, from the quiet window's §3 and re-checked here:**
`h9_batch_cost_loop.py`'s header names `row_loop_share_pct` among its
metrics with an expected band (25–55 ± 8 pp) and never prints it — `grep`
finds only the two header lines. A judge re-running per header would look
for a RESULT that cannot exist.

**Attacks.** Could h2 fix its telemetry by measuring the factor only over
the solve-span rather than the whole run? No — the executor thread is
active across the same span by design; any window that includes the
executor's work inherits the inflation, and a window that excludes it is
not the metric the contract defines. Could the contract's rule be applied
anyway ("rejected and re-taken")? Re-taking cannot lower a structural
number — the quiet window re-took it three times (1.29034/1.29935/1.29)
and I re-took it once more at load1 2.5 (1.29763). The defect is in the
contract's wording (or h2's telemetry naming), not the box, and per
`tools/audit/README.md` a defect in an instrument is a finding of this
dimension. Severity low: it mislabels a rejection condition; it does not
corrupt a number the finding rested on (h2's RESULTs reproduce).

## Harnesses written by this seat (all under `tools/audit/round4/D9/`)

| file | measures |
|---|---|
| `d9_own_d9_05.py` | D9-05 via CPU-time share, own builder, flat null, `OWN_HORIZON` perturbation |
| `d9_own_d9_06.py` | D9-06 thresholds from source text + JSON; `--memory-probe` controls incl. off-target; rule application |
| `d9_own_d9_inst.py` | D9-INST construction proof: numpy-free executor `thread_factor` ≈ 1.30, idle control ≈ 1.0 |

Captured outputs: `verify_h9_rerun.out`, `verify_h9_h12_rerun.out`,
`verify_own_d9_05.out`, `verify_own_d9_05_h12.out`, `verify_h7_rerun.out`,
`verify_h7_nofloor_rerun.out`, `verify_own_d9_06.out` (partial: the
in-probe arms moved to direct `--memory-probe` calls while the injection's
mmap sizing was being made robust — the arithmetic half of that file's
output is the completed part), `verify_own_d9_06_fullgate.out` (the full
injected gate), `verify_h2_rerun.out`, `verify_own_d9_inst.out`.

`tests/stress.py` was restored to its committed content (sha256 verified
identical to the pre-edit checksum); `git status` in the worktree is clean
except the files under `tools/audit/round4/D9/` written by this seat. The
lock `d9-verify-1` was released at the end.
