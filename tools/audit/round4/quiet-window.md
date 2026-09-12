# Round 4 — the quiet window

Every number behind a `provisional` round-4 finding, re-executed on an idle box
with the gate lock held, exactly as each harness's own header says to run it.

- **Baseline**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- **Box**: 8-core Apple M1, 8 GB, macOS 25.6, python 3.11.5
  (`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`),
  numpy 2.4.6 / scipy 1.17.1. Always `PYTHONPATH=tests/hastub`, always from
  each tree's own root, always with the five BLAS variables pinned to `1`.
- **Lock**: `python3 tests/gate_lock.py take --label quiet-r4`, renewed between
  commands, released at the end.
- **Exclusivity, by process and not by ownership**: `ps aux | grep -E
  "[s]tress\.py|[t]ests/run\.sh"` before every timing run. `concurrent_gate_procs`
  is printed beside every RESULT below and was **0** throughout. One caveat a
  reader needs: that grep also matches the *wrapper shell* of the command being
  launched, because the shell's own command line contains the script's path, so
  a naive count reads 2–3 when the true count is 0. The figures below are the
  harnesses' own `concurrent_gate_procs`, which counts processes and not
  wrappers.
- **`load1` is quoted, not gated.** `tools/audit/README.md` measured this box's
  ambient floor at 1.86 with zero audit workload and its best over ten 60-second
  retries at 1.55, so a `load1 <= 1.5` bar is a stall. Observed range in this
  window: **2.95 – 6.60**, the upper end being the measurement's own load.
- **`swapins`** was `42003807` at the first RESULT and `42065178` at the last:
  61 371 over the whole window, none of it attributable to a single harness.
- **One small correction to the README's own load figure, offered as an
  observation and not as a rule change.** `tools/audit/README.md` records this
  box's ambient floor at 1.86 and its best over ten 60-second retries at 1.55.
  Immediately after the last run here, with every audit process stopped, `load1`
  read **1.43**. That does not make a `load1 <= 1.5` bar workable — nothing in
  this window could have been measured at 1.43, because measuring raises it —
  but the floor is lower than 1.86 when the box is genuinely idle, and the
  README's two numbers were taken while round 2 was running.

## 1. The re-taken numbers

`original` is the value the finder's report carries. A verdict of *not
reproduced* is a result, not a failure: it blocks the round from being called
dry on that number until it is re-measured or refuted.

| finding / lead | harness | metric | original | quiet | load1 | thread_factor | procs | verdict |
|---|---|---|---|---|---|---|---|---|
| non-finding 1 | `D9/h1_grad_cost.py` | `two_zone_dhw.equiv_per_grad` | 194.83 | **194.833** | 2.96 | 1.0105 | 0 | reproduced within tolerance |
| non-finding 1 | `D9/h1_grad_cost.py` | `two_zone_dhw.wall_s_PROVISIONAL` | 1.78324 s | **1.63268 s** | 2.96 | 1.0105 | 0 | reproduced within tolerance (−8.4 %) |
| non-finding 1 | `D9/h1_grad_cost.py` | `two_zone_dhw.cpu_ratio_vs_reference` | 0.0788188 | **0.0773479** | 2.96 | 1.0105 | 0 | reproduced within tolerance (−1.9 %) |
| non-finding 1 | `D9/h1_grad_cost.py` | `reference_solve_wall_s` | 22.6019 s | **21.1724 s** | 2.96 | 1.0000 | 0 | reproduced within tolerance |
| non-finding 2 | `D9/h1_grad_cost.py` | `zero_range_fuse_cap.equiv_per_grad` | 195.021 | **195.021** | 2.96 | 1.0000 | 0 | reproduced (exact) |
| non-finding 3 | `D9/h2_cycle.py` | `msm_entries_per_cycle` | 0 | **0** | 3.16 | 1.2900 | 0 | reproduced (exact); RESULT rejected, see §2 |
| non-finding 5 | `D9/h2_cycle.py` | `loop_thread_cpu_ms` (cycle 0) | 3.87 ms | **3.86988 ms** | 3.16 | 1.2900 | 0 | reproduced; RESULT rejected, see §2 |
| non-finding 5 | `D9/h2_cycle.py` | `executor_cpu_ms_per_cycle` | 0.28 ms | **0.263 / 0.222 / 0.290 ms** | 3.16–3.42 | 1.2900–1.2994 | 0 | reproduced; RESULT rejected, see §2 |
| non-finding 5 | `D9/h2_cycle.py` | `wall_s` (cycle 0) | 1.28 s | **1.24862 s** | 3.16 | 1.2900 | 0 | reproduced; RESULT rejected, see §2 |
| non-finding 6 | `D9/h4_retained.py` | `coord_deep_bytes_final` | 43 269 B | **43 269 B** | 3.23 | not printed | 0 | reproduced (exact) |
| non-finding 6 | `D9/h4_retained.py` | `coord_deep_bytes_slope_per_cycle` | −5.26 B/cyc | **−5.25714 B/cyc** | 3.23 | not printed | 0 | reproduced (exact) |
| non-finding 9 | `D9/h4_retained.py` | `job_pickle_bytes_per_solve` | 12 081 B | **12 081 B** | 3.23 | not printed | 0 | reproduced (exact) |
| non-finding 9 | `D9/h4_retained.py` | `reply_pickle_bytes_per_solve` | 18 183 B | **18 183 B** | 3.23 | not printed | 0 | reproduced (exact) |
| non-finding 3 | `D9/h4_retained.py` | `solves_through_process_worker` | 8 | **8** | 3.23 | not printed | 0 | reproduced (exact) |
| non-finding 7 | `D9/h4_retained.py` | `traced_bytes_slope_per_cycle` | ~5 000 B/cyc | **5 308.43 B/cyc** | 3.23 | not printed | 0 | reproduced within tolerance |
| (header band) | `D9/h4_retained.py` | `worker_rss_slope_mb_per_solve` | header: < 1.0 MiB | **1.232 MiB/solve** | 3.23 | not printed | 0 | **not reproduced (got 1.232)** — over its own header band; the report carries no figure to compare |
| non-finding 9 | `D9/h5_worker_footprint.py` | `worker_modules` | 725 | **725** | 3.41 | not printed | 0 | reproduced (exact) |
| non-finding 9 | `D9/h5_worker_footprint.py` | `module_overhead` | 36 | **36** | 3.41 | not printed | 0 | reproduced (exact) |
| non-finding 9 | `D9/h5_worker_footprint.py` | `control_rss_mb` | 69.2 MiB | **68.48 / 66.95 / 69.41 MiB** | 3.07–4.18 | not printed | 0 | reproduced within tolerance |
| non-finding 9 | `D9/h5_worker_footprint.py` | `worker_rss_mb_after_10_solves` | 57.2 MiB | **88.97 / 82.41 / 59.08 MiB** | 3.07–4.18 | not printed | 0 | **not reproduced (got 88.97, 82.41, 59.08)** |
| non-finding 9 | `D9/h5_worker_footprint.py` | `footprint_overhead_mb` (derived) | −12.0 MiB | **+20.48 / +11.22 / −10.34 MiB** | 3.07–4.18 | not printed | 0 | **not reproduced (got +20.48, +11.22, −10.34)** — the sign flips across three consecutive runs |
| **D9-06** | `D9/h7_memory_gate.py` | `min_rss_multiple_required_to_fail` | 2.52905 | **2.52905** | 4.95 | not printed | 0 | reproduced (exact) |
| **D9-06** | `D9/h7_memory_gate.py` | `max_rss_multiple_required_to_fail` | 2.64294 | **2.64294** | 4.95 | not printed | 0 | reproduced (exact) |
| **D9-06** | `D9/h7_memory_gate.py` | `scenarios_where_2x_rss_passes` | 51 | **51** | 4.95 | not printed | 0 | reproduced (exact) |
| **D9-06** | `D9/h7_memory_gate.py` | `scenarios_never_memory_probed` | 45 | **45** | 4.95 | not printed | 0 | reproduced (exact) |
| **D9-06** | `D9/h7_memory_gate.py` | `rss_fail_threshold_mb` | 248.1 MiB | **248.1 MiB** | 4.95 | not printed | 0 | reproduced (exact) |
| **D9-06** | `D9/h7_memory_gate.py` | `clean_probe_rss_mb` | 82.0 MiB | **79.5 MiB** | 4.95 | not printed | 0 | reproduced within tolerance |
| **D9-06** | `D9/h7_memory_gate.py` | `inject2x_probe_rss_mb` | 131.6 MiB | **132.0 MiB** | 4.95 | not printed | 0 | reproduced within tolerance |
| **D9-06** | `D9/h7_memory_gate.py` | `inject2x_rss_rule_fires` | False | **False** | 4.95 | not printed | 0 | reproduced (exact) |
| non-finding 7 | `D9/h8_leak_attrib.py` | `total_growth_bytes` | 50 910 B | **55 025 B** | 4.68 | not printed | 0 | reproduced within tolerance (+8.1 %, band ±40 %) |
| non-finding 7 | `D9/h8_leak_attrib.py` | `production_growth_bytes` | 30 117 B | **32 590 B** | 4.68 | not printed | 0 | reproduced within tolerance (+8.2 %) |
| non-finding 7 | `D9/h8_leak_attrib.py` | top production line | `coordinator.py:877/879` | **`coordinator.py:5931` (7 830 B)** | 4.68 | not printed | 0 | reproduced within tolerance; the *leader* changed — `:5931` is new at the top, `:877`, `:879` and `accuracy.py:184` still in the top four |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `comfort_terms_calls_per_solve` | 29 591 | **29 591** | 4.31 | 1.0000 | 0 | reproduced (exact) |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `comfort_terms_calls_per_gradient` | 97.0197 | **97.0197** | 4.31 | 1.0000 | 0 | reproduced (exact) |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `comfort_terms_cpu_share_pct` | 33.331 | **32.6895** | 4.31 | 1.0000 | 0 | reproduced within tolerance (−0.64 pp, band ±5 pp) |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `simulate_batch_cpu_share_pct` | 38.7611 | **37.9522** | 4.31 | 1.0000 | 0 | reproduced within tolerance |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `comfort_over_simulate_batch` | 0.8599 | **0.861333** | 4.31 | 1.0000 | 0 | reproduced within tolerance |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `solve_wall_s_PROVISIONAL` | 1.9733 s | **1.95275 s** | 4.31 | 1.0000 | 0 | reproduced within tolerance |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `cpu_ratio_vs_reference` | 0.078388 | **0.0857176** | 4.31 | 1.0000 | 0 | reproduced within tolerance (+9.3 %) |
| **D9-05** null control | `D9/h9_batch_cost_loop.py` | flat-price `comfort_share` delta | +0.82 pp | **+1.32 pp** | 4.31 | 1.0000 | 0 | reproduced — the control still holds (the share does not move with prices) |
| **D9-05** | `D9/h9_batch_cost_loop.py` | `row_loop_share_pct` | header band 25–55 | **never printed** | — | — | — | **not reproduced (no such RESULT)** — §3 |
| non-finding 4 | `harnesses/j5_gil.py` `production` | `two_zone_dhw.starvation_share` | 0.0247027 | **0.0** | 3.85 | not printed | 0 | **not reproduced (got 0.0)** — the claim strengthens; see below |
| non-finding 4 | `harnesses/j5_gil.py` `production` | `idle.starvation_share` (null) | 0.0354081 | **0.0** | 3.85 | not printed | 0 | **not reproduced (got 0.0)** |
| non-finding 4 | `harnesses/j5_gil.py` `production` | `two_zone_dhw.longest_gil_hold_ms` | 21.9796 ms | **2.55921 ms** | 3.85 | not printed | 0 | **not reproduced (got 2.559)** |
| non-finding 4 | `harnesses/j5_gil.py` `thread` | `two_zone_dhw.starvation_share` | 0.975227 | **0.964496** | 3.64 | not printed | 0 | reproduced within tolerance |
| non-finding 4 | `harnesses/j5_gil.py` `thread` | `two_zone_dhw.gap_p50_ms` | 21.0374 ms | **22.1011 ms** | 3.64 | not printed | 0 | reproduced within tolerance |
| non-finding 4 | `harnesses/j5_gil.py` `thread` | `two_zone_dhw.longest_gil_hold_ms` | 65.4776 ms | **129.857 ms** | 3.64 | not printed | 0 | **not reproduced (got 129.9)** |
| non-finding 4 | `harnesses/j5_gil.py` `thread` | `switchinterval_0.5ms.starvation_share` | 0.532198 | **0.0239051** | 3.64 | not printed | 0 | **not reproduced (got 0.0239)** |
| non-finding 4 | `harnesses/j5_gil.py` `thread` | `idle.longest_gil_hold_ms` | 7.65721 ms | **33.6958 ms** | 3.64 | not printed | 0 | **not reproduced (got 33.70)** |

### What the re-takes mean, lead by lead

**D9-05 survives the quiet window intact.** Every count is bit-identical and the
wall share moved 0.64 pp inside a ±5 pp band. The null control still holds: the
flat-price arm's share differs by 1.32 pp, an order below the effect. Nothing in
the finding rested on a contaminated absolute.

**D9-06 survives exactly, and §5 settles it by execution.** Every FINAL number
is a rational of committed constants and reproduces to the digit.

**Non-finding 9 does not survive.** "The solve worker is not a memory tax beyond
numpy and scipy" rests on the worker's RSS after ten solves being *below* a
numpy+scipy control — 57.2 against 69.2 MiB. Three consecutive quiet runs give
88.97, 82.41 and 59.08 MiB against a control stable at 66.95–69.41, so the
derived `footprint_overhead_mb` reads **+20.48, +11.22, −10.34 MiB**. The metric
does not converge and its *sign* is not stable, so it cannot carry a claim in
either direction. The module counts it also rests on (725 / 689 / 36) are exact
and unaffected, and `worker_rss_mb_after_first_solve` is the stable half
(84.27 / 87.11 / 83.84). Whoever re-measures this should budget the
scenario-attributable component rather than the watermark — the same correction
D9-06 asks of `stress.py`.

**Non-finding 4 changes shape but not direction.** On the shipped process route
the quiet box gives **exactly zero** starvation on all three arms, against 0.025
reported; the idle null control is also zero, against 0.035. The pre-fix
`thread` route still starves at **0.964** (reported 0.975). So the contrast that
carries the non-finding — process route at the idle floor, thread route
saturated — is sharper in the quiet window than it was under load, and the two
reported values were load artefacts. The *longest-hold* figures and the
`switchinterval` perturbation do not reproduce at all (129.9 ms against 65.5;
0.024 against 0.532); they are single-sample extremes and should not be quoted.

**Non-finding 7's attribution reproduces; its leader does not.** The totals land
+8 % inside a ±40 % band, but the largest single production line in the quiet
run is `coordinator.py:5931` at 7 830 B, which the report does not name. Its
three named lines are all still in the top four. The report's own stated
limitation stands untouched: eight cycles cannot separate a bounded history
filling from an unbounded one, and the 200-cycle settling run was not done here
either.

## 2. `h2_cycle.py`'s RESULTs are rejected by the contract, and re-taking does not fix it

`tools/audit/README.md`: *"A timing or memory RESULT whose `thread_factor`
exceeds 1.05 is rejected and re-taken."* `h2_cycle.py` reports **1.29034,
1.29935 and 1.29** across three consecutive re-takes at load1 3.16–3.42 with
zero concurrent gate processes. It does not clear, and it is not going to.

The cause is not BLAS. `h2` computes the contract's ratio literally —
`time.process_time() / time.thread_time()` over the whole run — and `h2` is the
one D9 harness that, by design, pushes the solve through a **real
`ThreadPoolExecutor`** rather than `FakeHass`'s inline executor (the trap
`tools/audit/README.md` records). A second thread doing real work makes process
CPU exceed main-thread CPU by construction, so the ratio is structurally ≈1.29
no matter how quiet the box is.

Both things are true and both belong in the record: **the numbers reproduce**
(loop CPU 2.87–3.02 ms/cycle steady, 3.87 ms on cycle 0; executor 0.22–0.29 ms;
`msm_entries_per_cycle` 0 exactly), and **the contract's acceptance rule cannot
be satisfied by this harness as written**. The rule assumes `thread_factor` is a
BLAS-threading signal; in a harness that deliberately uses a second thread it
measures something else under the same name. That is a defect in the harness
contract's wording or in `h2`'s telemetry, not in the box — and per
`tools/audit/README.md`, *"a defect in an instrument is a finding"* of the
dimension that met it. Recorded here, not filed.

## 3. Three harness-contract gaps found while re-executing

None was reported by its finder, and each is small.

1. **`h9_batch_cost_loop.py` names a RESULT it never prints.** Its header lists
   `row_loop_share_pct` among the metrics *and* gives it an expected band
   (`25 - 55 (+/- 8 pp)`). `grep row_loop_share_pct` over the file returns only
   those two header lines: the harness emits no such RESULT. D9-05's prose does
   not lean on it — the claim rests on `comfort_terms_cpu_share_pct`, which is
   printed and reproduces — but a header that states a tolerance for a number
   the script cannot produce will send a judge looking for it.
2. **Four of the seven re-executed D9 harnesses print no `thread_factor`.**
   `h4`, `h5`, `h7` and `h8` call `d9common.telemetry()` with no argument, so
   the RESULT block carries `load1`, `swapins` and `concurrent_gate_procs` but
   not the factor the contract requires beside "a timing or memory RESULT".
   Every one of those four reports a PROVISIONAL RSS or byte figure. `h1` and
   `h9` print per-arm factors and are fine; `h2` prints one and is §2.
3. **`harnesses/j5_gil.py` prints `load1` only** — no `thread_factor`, no
   `swapins`, no `concurrent_gate_procs`. It predates the round-4 contract. For
   the runs above all three were measured from `d9common` immediately before and
   after each route: `load1` 3.85 / 3.64, `swapins` 42 065 178 unchanged across
   both routes, `concurrent_gate_procs` 0.

## 4. What was not in scope here

`tools/audit/round4/RESUME.md` names "D9's whole timing set and D11-06/D11-07"
as the provisional set. This session's brief enumerated D9's seven harnesses
plus `j5_gil.py` on both routes, and that is what was executed. **D11-06 and
D11-07 were not re-run**: neither is a timing number — D11-06 rests on a
`search/issues` count and on `policy_lint --stats`, D11-07 on DORA figures from
the API — so the quiet box is not what they were waiting for. They still owe a
re-execution by a seat with `gh`.

## 5. D9-06's confirming run, executed

D9's report names one run it could not do:

> The confirming run is: inject a 2x allocation into one scenario, run the full
> gate, watch the memory section stay green.

**Done. The memory section stays green.**

### Method

`winter/pv` was chosen because it is the recorded RSS leader (98.1 MiB) *and*
one of the six labels `MEMORY_TOP_N` actually probes in check mode — a scenario
outside that set would have proved only the 45-of-51 half. `tests/stress.py`'s
`build_case` was wrapped in the `audit-r4-D9` worktree so that this one
scenario, identified by its full spec
(`season=winter, two_zone, dhw, pv, cycling=0.0`), retains memory until it
reports **2x its recorded peak on both axes**:

- RSS to 2 × 98.1 = 196.2 MiB via an anonymous `mmap`, page-touched. An `mmap`
  is resident but outside `PyMem`, so `tracemalloc` does not see it — that is
  the numpy-internal growth `stress.py:1512` documents as the traced arm's blind
  spot, and modelling it honestly is the whole point.
- traced to 2 × 3.46 = 6.92 MiB via a `bytearray`, sized from *current* traced
  bytes so the probe's reported **peak** lands on target.

Three controls were executed before the gate run:

| arm | probe RSS | probe traced |
|---|---|---|
| `D9_INJECT_2X` unset — the null control for the edit itself | 84.3 MiB | 3.47 MiB |
| `uniform2x`, the target scenario | **202.7 MiB** | **6.92 MiB** |
| `uniform2x`, a *different* scenario (`winter/cycle`) | 83.5 MiB | 3.48 MiB |

The edit is inert unless switched on, and when switched on it touches exactly
one scenario. The unset arm matches the clean gate's own probe of `winter/pv`
(83.9 MiB / 3.5 MiB) to a tenth.

### The two full gate runs

Both `python3 tests/stress.py` from the `audit-r4-D9` root, BLAS pinned,
`concurrent_gate_procs=0`, gate lock held.

**Control (clean tree)** — 8 m 17 s wall, 465.85 s user, `load1` 2.75 at start:

```
-- Memory (D9-04)
  winter/pv                          RSS peak    83.9 MiB, traced   3.5 MiB (recorded 98 / 3.5)
  ok   the memory pass probes the recorded peak on each axis
  ok   the probed scenarios' memory peaks stay within their recorded budgets
  ok   every memory-pass scenario has recorded peaks
  ok   the memory pass retains less than 512 MiB of RSS in the parent
1 of 62 STRESS CHECKS FAILED
```

The one failure is **not** in the memory section and is not the injection's:

```
FAIL every scenario's solve costs what it should, in CPU, for this machine
     [shoulder/tariff+pv+cycle used 19792 ms of CPU = 972x the 20.4 ms
      reference measured beside it (budget 860x)]
```

— a per-scenario CPU check against budgets recorded on another machine. It did
**not** recur in the injected run, so it is flaky on this box at this load, and
it is named here so nobody attributes it to the injection.

**Injected (`D9_INJECT_2X=uniform2x`)** — 8 m 58 s wall, 518.57 s user,
`load1` 6.60:

```
-- Memory (D9-04)
  winter/cycle                       RSS peak    84.0 MiB, traced   3.5 MiB (recorded 96 / 3.5)
  winter/pv+cycle                    RSS peak    84.6 MiB, traced   3.5 MiB (recorded 96 / 3.5)
  heavy_old/shoulder                 RSS peak    83.4 MiB, traced   3.5 MiB (recorded 96 / 3.5)
  winter/pv                          RSS peak   198.9 MiB, traced   6.9 MiB (recorded 98 / 3.5)
  winter/2z/dhw                      RSS peak    88.0 MiB, traced   3.5 MiB (recorded 98 / 3.5)
  typical_slab/winter                RSS peak    89.6 MiB, traced   3.4 MiB (recorded 98 / 3.4)
  ok   the memory pass probes the recorded peak on each axis
  ok   the probed scenarios' memory peaks stay within their recorded budgets
  ok   every memory-pass scenario has recorded peaks
  ok   the memory pass retains less than 512 MiB of RSS in the parent
ALL 62 STRESS CHECKS PASSED
```

### Verdict

**D9-06 is confirmed by execution, not by arithmetic.** A regression that
doubles one scenario's memory on both recorded axes — `198.9 / 98 = 2.03x` RSS,
`6.9 / 3.5 = 2.00x` traced — passes the gate in full. The gate did not merely
stay green in the memory section; it went **greener than the clean control**,
because the control's one flaky CPU red did not recur.

Two details sharpen it beyond what the finder claimed:

1. **The gate says the opposite about itself, a few lines later, in the same
   run.** Three lines below the four silent memory checks it prints
   `ok   the budgets are tight enough to see a 2x regression, uniform or
   confined to one scenario`. That check is real, and it is about CPU only —
   `DETECTION_TARGET` is enforced for the CPU rules and for nothing else. A
   reader of the output has no way to know the assurance does not cover the
   section immediately above it.
2. **`stress.py` states the principle it breaks, in its own comments.** At
   `:466` `SCENARIO_BUDGET_FLOOR_RATIO` is documented as defaulting to zero
   because *"the detection check refuses a floor that would blind a scenario to
   a DETECTION_TARGET-fold regression."* The RSS rule carries exactly such a
   floor — the `max(150.0, ...)` term — with no detection check over it. The
   file argues the case against its own memory rule.

The tree was restored: `git checkout -- tests/stress.py`, verified
byte-identical to the pre-injection copy.

`h7_memory_gate.py`'s own numpy-shaped arm (a `tracemalloc`-visible allocation,
which fires the traced rule) was re-executed as part of §1 and reproduced —
`inject2x_rss_rule_fires=False`, `inject2x_traced_rule_fires=True`. It was
**not** re-run through the full gate, because the `uniform2x` arm is the
stronger statement: it is a true 2x on both axes and both rules stay silent,
where the numpy arm is a 38x traced regression that trips the traced rule for
the wrong reason.

## 6. D3's mutation survivors through the full gate

D3's report hands the quiet window its own next step: *"the quiet window runs the
full `GATE_SCOPE=full GOLDEN_MODE=drift` gate for the top six, and only those
become findings."* Six were run, most consequential first.

### The command, and the baseline-ref check the brief requires

```
GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=7dd68dd327fe3dbfb09f3bd0fe38910c58877697 \
  GATE_JOBS=1 HPO_GATE_LOCK_LABEL=quiet-r4 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 ./tests/run.sh
```

`env_drift.py` refuses a ref that resolves to `HEAD`, so the worktree's HEAD was
checked before the first run: **`bc8c394`**, which is not the baseline. No mutant
needed committing. Two things about that HEAD are worth recording:

- It **moved during this window**, from `4cf4f2c` to `bc8c394` (a commit landing
  D3's own round-4 documents). `git diff --name-only 7dd68dd bc8c394` touches
  **zero** files under `custom_components/`, so every mutant below was applied to
  production that is byte-identical to the baseline. The move is noted because a
  quiet window is supposed to be exclusive and this one was not exclusive of
  *commits* — only of compute. No gate or stress process was ever concurrent:
  `concurrent=0` is recorded at the start of all seven runs.
- Each mutant was applied by exact-line replacement, refusing unless the line on
  disk matched `prescreen.json`'s recorded `old` byte for byte, and restored with
  `git checkout -- custom_components/` after its run. All six restore checks came
  back empty.

### The attribution control, which the verdicts below depend on

The same gate was run **once with no mutant at all** on the same tree, because
without it every mutant looks killed:

```
-- control gate start 16:25:11 concurrent=0 load1=2.45
CONTROL VERDICT: 1 TEST SCRIPT(S) FAILED
  control-red >>> FAILED: python3 tests/harness_headers.py
  (tests/stress.py in the same run: ALL 62 STRESS CHECKS PASSED)
```

`harness_headers.py` fails **13 of 25** on the clean tree, identically in all
seven runs, and it is a preparation artefact rather than a suite defect: the
finder tree has round 3's files stripped, so the still-tracked
`tools/audit/round3/D2/dst_window_factors.py` and `window_size_sweep.py` raise
`ModuleNotFoundError: No module named 'd2lib'` when `harness_headers.py` executes
them. It is subtracted from every mutant's failure set below. A reader checking
this: the count is `13 of 25` in the control and in every one of the six mutant
runs, so it moves with nothing.

### Results

| mutant | line | w | op | survived | killed by | run |
|---|---|---|---|---|---|---|
| **M31** | `thermal_model.py:2482` | 5 | `STMT_DEL` `C_w = p.wood_tank_thermal_mass` → `pass` | **no** | `tests/edge.py` (2 FAILURES) | 15:04:55–15:17:31 |
| **M06** | `grid_fee.py:106` | 5 | `GUARD_OFF` `if start <= end:` → `if False:` | **yes** | — | 15:17:32–15:29:31 |
| **M15** | `tariff.py:571` | 5 | `GUARD_OFF` `if price_per_kw <= 0 or not np.isfinite(threshold_kw):` → `if False:` | **no** | `tests/stress.py` (2 of 62) | 15:29:31–15:49:38 |
| **M01** | `legionella.py:521` | 4 | `GUARD_OFF` `if not params.dhw_legionella_enabled:` → `if False:` | **yes** | — | 15:49:38–16:01:32 |
| **M22** | `tariff.py:507` | 5 | `STMT_DEL` `k = max(1, min(int(k), x.size))` → `pass` | **yes** | — | 16:01:32–16:13:11 |
| **M32** | `optimizer.py:1549` | 5 | `CLAMP_DROP` `end = min(i + lookahead, n_steps)` → `end = (i + lookahead)` | **yes** | — | 16:13:11–16:24:50 |

**Four of six survive the full gate. Two do not — and both were killed by a
script D3's pre-screen deliberately excluded.**

### M31 — killed, and it is the most consequential of the six

`tests/edge.py`:

```
Space heating optimization (with DHW) failed: name 'C_w' is not defined
Space heating optimization (with DHW) failed: name 'C_w' is not defined
2 FAILURES
```

Exactly the predicted consequence: `C_w` is assigned only at `:2482`, inside
`if two_tank:`, and read at `:2483`, so deleting the assignment is a `NameError`
on every two-tank batch trajectory. D3's report does **not** narrate this mutant
— `prescreen.json` lists eleven survivors and the report writes up nine (S1–S9);
M31 and M32, both weight 5, are the two it omits. M31 is the one that mattered.

### M15 — killed, on cost rather than on correctness

`tests/stress.py`, 2 of 62:

```
FAIL no scenario exceeds its own recorded cost by the budget factor
     [winter/2z/dhw 283.4x vs budget 261.0x; winter_extreme/1z/space 19.3x vs 16.5x;
      summer/1z/space 9.8x vs 9.1x; heavy_old/winter 205.4x vs 133.6x]
FAIL the sweep as a whole costs what it has always cost, relative to this machine
     [150.7 s of solver CPU vs 1.1 s of reference = 134.62x, over the 134.32x budget]
```

Deleting `peak_cost`'s degenerate-input guard makes the capacity term do real
top-k arithmetic where it used to return `0.0` immediately, so the solve gets
measurably dearer. The kill is real and not the flakiness this box shows
elsewhere: `stress.py` returned **ALL 62 PASSED** in the control and in all four
surviving mutants' runs, and failed only under M15. Note what it means, though —
the suite catches this mutant by its **CPU cost**, not by a wrong number. No
assertion in the tree sees the value change; D3's S2 diagnosis stands.

### The four that survive

`M06`, `M01`, `M22` and `M32` each produced exactly the control's one red and
nothing else — `stress.py`, `edge.py`, `backtest.py` and `optimality.py` all
green under every one of them. So:

- **M06 (`grid_fee.py:106`, weight 5) is confirmed as a real gap**, and it is the
  one with money behind it: `parse_month_range("Mar-Sep")` returns all twelve
  months, so a seasonal grid fee is charged and optimised against year-round. The
  suite's only range assertion uses the wrapping case `Nov-Mar`, which takes the
  same branch with the guard gone. D3's S1 holds under the full gate.
- **M01 (`legionella.py:521`, weight 4) is confirmed**: a disabled legionella
  tracker with a recorded last cycle publishes a countdown instead of `None`,
  through `coordinator.py:6426` to `sensor.py:1183`/`:1230`. Both existing
  assertions run with the feature enabled. D3's S5 holds.
- **M22 (`tariff.py:507`, weight 5) survives, and D3's own honest bound is the
  reason** — `tariff.py:593` already clamps `k` before the only production call
  site, so the mutant is equivalent through that path. It is a test gap, not a
  product defect, and the full gate agreeing is the expected result rather than a
  disappointment.
- **M32 (`optimizer.py:1549`, weight 5) survives because it is an equivalent
  mutant, and nothing in the suite could have killed it.** Dropping the clamp
  leaves `end > n_steps`, and the only uses of `end` are `solar_gains[i:end]` and
  `heat_loss_factors[i:end]` — numpy slices silently clamp to the array's length,
  so the slice is identical and `if end <= i` is unaffected. This belongs beside
  D3's S9 as a second equivalent mutant, not on a survivor list as a gap.

### What this says about the pre-screen, and it is the part worth carrying

D3's method excludes `stress.py`, `edge.py` and `backtest.py` from the pre-screen
— per the brief, and defensibly, since they are the dear ones. The full gate run
here shows what that exclusion costs: **two of the six prescreened survivors are
not survivors**, and each was killed by one of the excluded three. The measured
false-survivor rate on this sample is therefore **2 of 6**, and both false
survivors are weight 5.

That is not an argument for pre-screening against the whole suite — it would cost
about twelve minutes per mutant, which is what these runs took. It is an argument
that **a prescreened survivor list is a candidate list and must be labelled one**,
and that the number D3 reports as a survivor count should carry the exclusion
beside it. `tests/mutation_budgets.json` sets `max_survivor_fraction` to `1.0` for
both scopes, so nothing downstream currently consumes the number — but the report
does, and so would a verifier.

One further measurement, since the runs were taken anyway: a full serial gate on
this box costs **11 m 38 s – 12 m 36 s** on a clean or equivalent tree and
**20 m 07 s** under M15, whose mutant makes the solves dearer. Seven runs,
`concurrent=0` at the start of each, `load1` 2.27–4.63.

## 7. What is still owed

- **`h5_worker_footprint.py`'s RSS half needs a metric that converges**, and
  until it does, D9's non-finding 9 has no number. Three quiet runs is the
  evidence; a fourth will not settle it.
- **The 200-cycle retention run** that would separate `accuracy.py:184` filling
  from leaking was not done here either. D9 names it; it is still open.
- **The BLAS-pin question (D9's non-finding 10) is unchanged** — it needs a
  Linux/OpenBLAS host, and this box is not one. No amount of quiet fixes it.
- **D11-06 and D11-07** were outside this session's brief (§4) and still owe a
  re-execution by a seat with `gh`.
- **The remaining five prescreened survivors** — `M08`, `M19`, `M20`, `M23`,
  `M25` — were not run; six was the cap. `M23` (`battery.py:134`, a
  `ZeroDivisionError` in a published property) is the one I would run seventh.
- **`h7_memory_gate.py`'s numpy-shaped arm was not re-run through the full
  gate**, only standalone (§5).
