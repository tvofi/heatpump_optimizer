# RCA-BULK-1: class RCAs for P4, P7, P8 and P10

This is a root-cause seat. It follows `tools/audit/briefs/root-cause.md` and `.claude/rules/defect-root-cause.md`, and it was written 2026-09-28 against `origin/main` `3490cb16`. The seat was read-only and posted nothing.

- `$E` = `SCR/phaseC/bulk1/`. Every script and output cited below is there. The mutants and prototypes ran on `git archive` copies of main, which have since been deleted. `escapes.sh` recomputes the release counts.
- Instance rows are from `phaseA/a1/register_rows.tsv`. The FLAG re-maps in `reclassifications.md` are **applied**: P8 loses R2 D2-02, R4 D2-04 and R5 D12-01. P10 loses R1 D7-03 and the four N-solve-recompute rows. P7 loses R3 D1-03 (N-future-instant).
- Spans run from **issue created to issue closed by its fix**, taken from GitHub timestamps. They are a lower bound on cost, because find/verify/judge seats are excluded. This is RCA-1736's method.

## 0. Shared common cause (cited, not re-derived)

RCA-1736 §2 applies to all four classes unchanged:

- **(c)**: the barrier trigger counts per round, so a class at 1–3 per round never fires.
- **(a)**: no step folds rounds into `bugclasses.json`. Round 8 was never classified, and the R9 judge re-minted or split classes.

Only the class-specific evidence is added here:

| | per-round max, after flags | ledger at main (`bugclasses.json`) | Root cause sections written |
|---|---|---|---|
| P4 | 3 (R2, R5, both before the 2026-09-25 rule) | rounds 1–7 only; R8 D0-s1-01 and R9 #1664 not folded | 0 |
| P7 | 2 (R3, before the flag) | complete (F1.1 folded R9) | 0 |
| P8 | 2 (R4) | rounds 1–7; #1513 (R8) and #1657 (R9) not folded | 0 |
| P10 | 1 (R1 max drops from 3 to 1 once the flags apply) | rounds 1–7; R9 re-minted as `N-loop-cpu` / #1658 "CPU-WORK-INLINE" | 0 |

Two further points apply to all four classes:

- **Trigger 1 still binds each instance.** Every dated instance below except #777 (baseline untagged, shipped population zero) reached a tagged release (§§1–4), so each owed a Root cause section independent of any round count, and none was written. The rule says this trigger has no enforcement moment. These four classes are the measured cost of that gap.
- **P10's name was too narrow.** Its register mechanism, *"A solve on a GIL-holding thread"*, excluded the loop-inline shape of R9, so the judge minted a new class (`N-loop-cpu`): RCA-1736's "no name yet" in another form.

---

## 1. P7: naive wall-clock datetime arithmetic across DST

**In-class members:** R2 D2-03 (#243), R3 D2-02 (#777), R5 D1-08 (#1299) and R9 D14-s4-01 (#1665, 9 seams). There is also a pre-audit fix, v4.0.4 `366387ad` (#61, *"DST-proof learning"*).

### Cause

Home Assistant hands every aware stamp **one shared `ZoneInfo`**, and CPython does arithmetic on two stamps sharing a tzinfo **as wall clock**. So `a - b` and `a + timedelta` are silently wrong across a transition, at any site.

Correctness therefore depends on each call site knowing to go through UTC. Before F1.1 nothing forced that. After F1.1 there are helpers (`accuracy.utc_elapsed_seconds`, `utc_shift`, `coordinator._utc_age_seconds`), but they are opt-in.

**The class search finds 13 raw zoned `-`/`+ timedelta` sites still at main** (`$E/p7_raw_sites.txt`). Among them:

- `services.py:873` and `manual_plan.py:288`: `now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS)`. A manual override applied the evening before the autumn fold lasts 21 true hours, not 20. This is arithmetic, not a runtime observation.
- `coordinator.py:6397, 7894, 8122, 10382, 10731`
- `power_guard.py:84`
- `open_meteo.py:327`
- `pump_arbiter.py:497`

This is the class's current blast radius: mostly ±1 h spacing or expiry skew twice a year.

### Process state

**(c) for landing.** `tests/dst_checks.py` has existed since v4.0.4 (2026-08-26) as a set of per-seam pins, and it was obeyed:

- Round 1 recorded *"DST explicitly confirmed NOT a gap (dedicated 314-line suite)"* (`docs/audit-2026-09.md:213`). Round 2 then found the plan grid (#243).
- #777's own commit (`c7e2f817`) says *"the existing case started at 13:30, ten hours after the 03:00 fold, which is why this survived"*.
- Each fix added pins keyed on its own seam, so the next seam landed unpinned.

**(c) again for the barrier.** F1.1 (#1722) landed a runtime tracer that is narrower than its own finder's harness:

- The sweep's `p7_dst_seams.py` had `--arm tariff`, a capacity tariff with an off-peak mask, which reached `window_factors` pre-#777 (sweep S7, `SWEEP.md`).
- The landed tracer replays only `synthetic-dhw-only.json`, whose options are `{"optimization_interval": 30}`.

### Does F1.1's barrier cover R2/R3/R5? Measured, not reasoned

I re-introduced each historical member's pre-fix shape into main and ran main's `tests/dst_checks.py` (`p7_mutants.py`, `dst_*.out`):

| member | mutant | instance pins | **the tracer check** ("no production seam does wall-clock arithmetic") |
|---|---|---|---|
| — | none (main) | 66/66 pass | ok |
| R2 D2-03 #243 | `_utc_step_starts` walks wall time | 4 FAIL | **FAIL**: `('coordinator.py','<listcomp>')` |
| R3 D2-02 #777 | `window_factors` walks from `slot0` in wall time | 2 FAIL (#777's own pins) | **ok, blind**: the capacity-tariff path is never configured |
| R5 D1-08 #1299 | `_plan_age_minutes` subtracts raw | 3 FAIL (#1299's own pins) | **ok, blind** |
| R5, the shared helper | `_utc_age_seconds` subtracts raw | 9 FAIL | **FAIL**: `_utc_age_seconds` |

**Why R5 is blind.** A probe (`dst_R5-D1-08.out` plus the probe run) found `_plan_age_minutes` executed **144 times** in the tracer window. **Every true age was 0 s.** The plan age is only ever read in the same cycle that stamps it, so its operands never straddle the transition.

**Verdict on F1.1's barrier.** It covers 1 of the 3 in-class historical members (R2). The other two are held only by their per-instance pins.

The register's barrier text claims *"Reaches every seam a replayed cycle executes"*. That is false in two measured ways:

- **Config-gated seams**, for example the capacity tariff.
- **Executed seams whose operands never straddle the transition**, for example ages read in their own cycle.

The text names neither; it names only "a seam no replayed cycle drives" and "stored text". A minor point: on Python 3.11 the key is `<listcomp>`, not the function name, because comprehensions have their own frame before PEP 709.

### Cost test

| instance | span | releases carrying it (≥, from the baseline) |
|---|---|---|
| #243 | 57.6 h | 18 (v6.2.15→v6.3.14) |
| #777 | 3.9 h | 0 (shipped population zero per its commit) |
| #1299 | 18.2 h | 1 |
| #1665 | 19.1 h | 7 (v6.7.1→v6.7.8) |

- Mean span 24.7 h (n=4).
- Rate: 5 in 31 days (08-26→09-26), about **4.8 per month**, or roughly 119 h of span per month.
- The countermeasure is two more replay arms. Measured basis: one 6-cycle replay takes 3.1 s wall (`p10` timing, same harness). Estimate: ≤20 s per `dst_checks.py` run. At the ~380 PR runs per month in the cpu-gate-blind RCA, that is about 2 h per month, far less than about 119 h per month. **Passes.**

### Countermeasure: build (the barrier is incomplete; P7 is `barriered`, so every new instance owes it)

Add two arms to the tracer in `tests/dst_checks.py`:

1. **Config arm.** Replay the same three days with a capacity tariff and off-peak mask at 15 and 60 minutes. This is the finder's `--arm tariff`. Add a manual plan applied before the fold.
2. **Straddle arm.** Replay the same days with the solve failing for 2 h across the transition. For example, `_await_process` raises for cycles 3–6, the shape `p10_loop_kernels.py`'s fallback arm uses. Stamps written before the fold are then read after it.

**Demonstration owed.**

- Must now FAIL: the `R3-D2-02` and `R5-D1-08` mutants in `p7_mutants.py`. Today the tracer check passes on both.
- Must stay green: main.
- Must stay 0: the plain-day null.
- Expected to fire, as the at-main bound: `services.py:873` and `manual_plan.py:288`. They need a fix or a named exemption.

Also amend the P7 `barrier` text to list what it does not reach. Tests only, no production lines.

---

## 2. P10: CPU work holds the Home Assistant event loop

**In-class members:** R1 D9-02 (#199), R2 D9-05 (#290), R3 D9-03 (#783), R5 D9-06 (#1337), R6 D9-01 (#1399), R9 D9-s1-03 and D9-s2-01 (#1658). There is also a pre-audit issue, #98 (08-28).

### Cause

Home Assistant runs `_async_update_data` and **every entity property read** on the event loop, and it gives CPU work no boundary by default.

The integration built exactly one off-interpreter route, `_await_process` / `process_worker` (#199/#290, `8542e51c`, 2026-09-05). It carries only `optimize` and one what-if (`coordinator.py:1283, 10152`). Any other CPU consumer lands wherever it is written, and nothing measures where:

- **The #511 fallback** re-runs the solve in-process on an executor thread. This is an accepted trade, capped at 3 cycles (`coordinator.py:716, 1294`).
- **The sysid fit** runs inline in `async_run_optimization` (`coordinator.py:5194→10610`).
- **The sensor advisor** simulates on every entity write (`sensor.py:111` → `topology.py:_advisor_replay`).

### Process state

**(a) for landing.** No rule, brief line or check states where CPU work may run. `tests/entities.py` has an executor hand-off table (#1529), but it checks *what state* a job reads, not *what work* runs on the loop. No test reads loop-thread work at all; a grep of `tests/` finds no heartbeat or loop figure.

**(c) plus a naming failure for recognition.** The register statement excluded the loop-inline shape, so R9 re-minted the class; five non-starvation rows sat in it (flags). #1337 was closed `not_planned` as *"deferred pending the quiet-window re-take; re-open to run it"*. No re-take was scheduled anywhere, and R6 re-found the same defect as #1399. That is state (a) for deferred re-takes.

### Blast radius at main, measured

`p10_loop_kernels.py` counts every `ThermalModel.simulate_*` call during a replayed day. Each call is attributed to one of three routes: worker, executor thread, or loop.

| arm | worker | executor | **loop** | site |
|---|---|---|---|---|
| base (main) | 8177 | 0 | **2304** | `topology.py:_advisor_replay` (384 per cycle, #1658 D9-s2-01, **live**) |
| fixed (advisor attribute returns `{}`) | 8177 | 0 | **0** | — |
| fallback (`_await_process` raises) | 0 | **3926** | 2304 | 12 optimizer sites: the #511/#783/#1337/#1399 route |

The sysid fit (D9-s1-03) is **not reached**. The replay never arms an experiment, and the fit's kernel is `np.linalg`, not `ThermalModel`. Its seam is live at main by reading (`coordinator.py:10610`).

### Cost test

| instance | span |
|---|---|
| #199 | 93.8 h |
| #290 | 70.8 h |
| #783 | 18.4 h |
| #1399 | 2.3 h |
| #1337 | closed deferred after 26.9 h |
| #1658 | open since 09-26 |

- Mean span 46.3 h (n=4 fixed).
- Escapes (≥ releases): #199 **34**, #290 19, #783 2, #1399 1, #1658 **10 and counting** (v6.7.1–v6.7.10).
- Rate: 8 in 29 days, about **8.3 per month**.
- Detector standing cost: **3.1 s wall** per 6-cycle replay, measured on a 4-vCPU box at load 1.1. It is about 0 marginal if it rides the existing replay lane. **Passes by orders of magnitude.**

### Countermeasure: build a count-based detector, and make it the class barrier

The rule: *kernel calls in the Home Assistant interpreter outside `process_worker.run_worker` = 0 on a replayed day.* This is `p10_loop_kernels.py`'s base arm as a check.

- The fallback arm is the positive control, and it fires.
- The fixed arm is the pass case.
- It counts calls, not time, so it does not depend on BLAS or load. That is the property the cpu-gate-blind RCA's `loop_cpu_ratio` lacks: that one is a ratio budget, which cannot see an instance already present when the budget is recorded, as #1658 is.
- `loop_cpu_ratio` remains the complement for loop CPU spent outside the model kernels.

Two parts are owed:

1. Extend the kernel list to the sysid fit entry points.
2. Add an arm with sysid armed.

**Demonstration owed at landing:**

- R1 D9-02, the solve on a `ThreadPoolExecutor`: the same shape as the fallback arm, so it would have fired, as measured above.
- #1658 D9-s2-01: fires at main (base arm) and passes once fixed.
- D9-s1-03: owed.

---

## 3. P8: a currency or unit resolved differently per surface

**In-class members:** R1 D4-04 (#168), R4 D6-02 (#940), R4 D12-01 (#961), R7 D4-03 (#1456), R8 D2-s2-02 (#1513) and R9 D12-s3-81 plus D14-s2-02 (#1657). There is also an unregistered sibling, #1228 (D8-03, 09-19).

### Cause

The register's detector idea, *"every currency/unit read site must resolve through one shared function"*, **already exists and predates every instance**. `currency.py` was added in v4.1.0 (`9a0d4c5e`, 2026-08-27). Its docstring says *"The one place the display currency is decided"*. But it decides the wrong fact:

- `resolve_currency(hass)` returns the **instance's label currency** (`currency.py:17`).
- The numbers are denominated by the **price feed**.
- The ingest seam parses the feed's unit and **drops the money code**: *"The currency itself is never converted"* (`inputs.py:350`; sweep: `coordinator.py:1326, 1344`, `price_model.py:700`).
- Every surface then applies its own precedence: nine sensors read `coordinator.currency` (`sensor.py:437…2750`), the card has its `currency()`/`savingsUnit()` chain, and the config-flow bounds are SEK-sized numbers under a currency label (`config_flow.py:1731, 1734`, `grid_fee.py`).

The two **dimension-unit** instances, °C (#961) and öre or MWh (#1513), were closed for good by one converter each at the input seam. The **currency** half is the part never carried.

### Process state

**(c).** The canonical-function process existed, was followed, and did not produce the intended result, because it canonicalises the label and not the denomination.

It is about to recur at the barrier level. #1657's sweep marks every `resolve_currency` site *"guarded — the canonical resolution"* and proposes a `structure.py` metric forcing all money through it. **That would ratify the defect.** It must not be built as proposed.

### Blast radius at main, measured

`p8_denomination.py` replays one hour with the price entity in EUR/kWh on the harness's SEK instance:

- **11 of 11** published money units read `SEK`. The mismatched units include `plan_predicted_savings`, `cost_total_heating` and `cost_current_electricity_price=SEK/kWh`.
- Null arm, SEK feed: **0 of 11**.

The class is live at main.

### Cost test

| instance | span | releases carrying it (≥) |
|---|---|---|
| #168 | 2.9 h | 17 |
| #940 | 1.8 h | 1 |
| #961 | 12.1 h | 1 |
| #1456 | 1.9 h | 1 |
| #1513 | 14.5 h | 1 |
| #1657 | open | 10 |

- Mean span 6.6 h (n=5).
- Rate: 8 in 25 days, about **9.6 per month**, or about 63 h per month.
- Detector: two 1-hour replays, about 3 s (measured basis as in §2). **Passes.**

### Countermeasure: build (production change, owner-gated as a product rule)

1. **One denomination fact.** Carry the feed's money code from the ingest seam with the series. The money unit is the feed's code, with `resolve_currency` only as the fallback when the feed has none. Plausibility bounds become multiples of the feed's own price level, not SEK constants.
2. **Detector:** `p8_denomination.py` as a check, `money_units_mismatched == 0` on the EUR-feed arm.
   - Demonstrated: 11 → must reach 0 at the fix. The null arm is 0.
   - Past instances it catches: D14-s2-02 and the sensor surface of R4 D6-02. It does not reach the card (R7 D4-03) or config-flow labels (R1 D4-04, D12-s3-81). Those need the R9 sweep's `p8_currency.py --seams` re-keyed so that `resolve_currency` is **a seam, not a guard**.

Whether the display currency should follow the feed is a product rule for tvofi. It is F1.8's owner question, stated rather than assumed.

---

## 4. P4: the seed set or stop tolerance misses the optimum

**Members:** 16 instances, R1–R9. Filed issues include #185, #186, #233, #826, #921, #1293–#1295, #1377/#1378, #1447 and #1664.

### Cause

The solver is a local method (L-BFGS-B, multi-start) over a non-convex objective. Its seeds are energy anchors (0.20, 0.35 and 1.0× the baseline, bang-bang starts and a warm start), and it stops at `ftol=1e-6` (`optimizer.py:564, 709, 4113`). Both were calibrated on the cells that existed when they were set.

Features that reshape the objective moved the optimum outside those brackets:

- the capacity-tariff plateau (R2);
- zero-range bounds (R2 D9-01);
- the two-zone winter optimum at 0.20× (R7, #1447);
- shoulder prices (R9, #1664).

The D0 brief's method (steps 2 and 4: strictly-superset challengers, including a global outer bound, over the 8×5 grid) **finds a gap by construction** against any finite seed set. The measured gaps are 0.04–1.2 % of the objective.

### Process state

- **(d) for landing.** The seeds and tolerance were sound for their calibration cells, and each feature changed the precondition. The certificate (#1409) is the *notice-the-change* countermeasure. It exists in `tests/optimality.py:543` ff, but its population is a fixed 5-cell grid.
- **(c) for recurrence.** The brief is obeyed and manufactures instances.
- **(a) at the ledger.** `bugclasses.json` still reads `detector: null` although the certificate exists.

### Cost test

| instance | span | releases carrying it (≥) |
|---|---|---|
| #185 | 11.7 h | 20 |
| #186 | 11.7 h | — |
| #826 | 10.6 h | 2 |
| #1447 | 12.4 h | 1 |
| #1664 | open | 10 |

- Fixed instances: mean span 11.6 h (n=4). Refused or not planned: #233 at 22.3 h and #1293 at 27.0 h.
- The money involved:
  - #1293's MPC shoulder cell realised 0.75 SEK/day (1.28 % of the bill) at the tighter stop rule.
  - #233 measured up to 2.16 SEK/day, masked by re-planning.
  - **The tightening that closes the objective gap lost 6.4 % money on the backtest shoulder cell** (`dfc0d2ed`; owner comment on #1293), and cost 2.4× thread CPU.
- A **class-eliminating** barrier means a search that brackets every basin: a global method, or #1294's ladder at "a quarter of the sweep's solver CPU". That cost is paid on **every solve** on a Pi-class target, 48 per day. It is not money-monotone, and it is outside the bound (*"may not degrade … functionality or quality"*).

### Verdict: refuse the barrier. Recorded, with the owner asked per the rule

The class reached 3 per round twice (R2, R5), so the rule's "a seat finding none within the bound asks the owner" applies. The owner has already refused its two eliminating forms on numbers (#1293, #1294). This seat recommends recording that refusal as the class disposition, plus three changes:

1. **Ledger.** Set the detector to the certificate (`tests/optimality.py`, "solve certificate over the energy-diverse cell grid (#1409)"). Set the status to `detector`, and add the refusals #1293 and #1294 to the entry.
2. **D0 brief (policy, owner approval).**
   - A gap closable only by a refused knob is a duplicate of that refusal; R8 D0-s1-01 was already handled this way, informally.
   - A finding must show **money** (the `tests/backtest.py` shape), not objective alone, since #1293 proved the two diverge.
   - A new cell that shows a gap joins `_CERT_CELLS` with a claim. This is the certificate's own stated growth rule.
3. **#1664** is handled in F2.4 as an ordinary fix or claim. It needs no barrier.

---

## 5. Summary

| class | cause (1 line) | process state | cost numbers | verdict | placement | register change |
|---|---|---|---|---|---|---|
| **P7** | Home Assistant's shared `ZoneInfo` makes any zoned `-`/`+timedelta` wall-clock; UTC helpers are opt-in; 13 raw sites left (`services.py:873` manual plan lasts 21 h across the fold) | (c) landing: per-seam `dst_checks` pins since v4.0.4; (c) barrier: F1.1's tracer dropped the finder's tariff arm and never straddles same-cycle stamps | 4.8/mo; 24.7 h mean span (n=4); ≥18/0/1/7 releases; +≤20 s per run | **Build**: tracer config arm and straddle arm. Measured: the tracer catches R2 only; R3 (#777) and R5 (#1299) mutants pass it | new tests-only group **F1.1b** (`tests/dst_checks.py`), after F10.1b | Keep `barriered`, but **amend `barrier` text** to name both measured non-reach modes (status stays `barriered`, so new instances keep owing the arms) |
| **P10** | Home Assistant runs update and entity reads on the loop; one process route carries only `optimize`; no rule on where other CPU work runs | (a) landing; (c)/naming for recognition (mechanism excluded loop-inline, re-minted R9); (a) deferred re-take (#1337) | 8.3/mo; 46.3 h mean span (n=4); ≥34/19/2/1/10 releases; detector 3.1 s | **Build**: kernel-route count = 0 outside the worker. At main: loop=2304 (`topology._advisor_replay`, live); fixed 0; fallback fires 3926 | **F1.7** (fixes #1658; its fix is the pass arm), with F10.2's `loop_cpu_ratio` as the complement | Mechanism → "CPU work outside the process worker (loop-inline or GIL thread)"; fold `N-loop-cpu`/#1658; `detector` = `p10_loop_kernels.py`; status `detector`, then `barriered` at F1.7 |
| **P8** | `currency.py` is the one resolver but returns the instance label; ingest drops the feed's money code; each surface applies its own precedence | (c): the canonical-function process was followed and canonicalised the wrong fact; #1657's barrier proposal would ratify it | 9.6/mo; 6.6 h mean span (n=5); ≥17/1/1/1/1/10 releases; detector ~3 s | **Build**: carry the denomination from ingest; detector: EUR feed on SEK instance gives 11/11 mismatched at main, 0/11 null. **Refuse** #1657's proposed `resolve_currency` metric | **F1.8** (owner product rule on display currency); card/config surfaces via the re-keyed sweep enumerator | `detector_idea` → "the money unit is the feed's denomination; `resolve_currency` is a seam, not the guard"; fold #1513, #1657, #1228 |
| **P4** | Local multi-start with finite, calibrated seeds and `ftol=1e-6`; new features move optima outside the brackets; the D0 method finds a superset gap by construction | (d) landing; (c) recurrence (the brief manufactures instances); (a) ledger (`detector: null` despite #1409) | 16 instances over 25 days; 11.6 h mean span (n=4); ≥20/2/1/10 releases; gaps 0.04–1.2 %; the eliminating fix lost 6.4 % money and costs 2.4× CPU | **Refuse** the eliminating barrier (outside the bound; owner asked; #1293/#1294 already refused); keep the certificate; D0 brief amendments to the owner | **F2.4** (#1664 as fix or claim); brief change as a policy PR | status `open` → `detector` (`tests/optimality.py` certificate); cite the #1293/#1294 refusals; fold R8 and R9 |

## 6. Not measured

- **P7:** the two new arms are specified, not built. The 13 residual sites are a grep, not a runtime result; only the manual-plan skew is arithmetic-certain.
- **P10:** the sysid seam and its kernel extension are not run.
- **P8:** the card and config-flow surfaces are not run.
- **P4:** no solver race was re-run. Gap figures are the judges' own.
- **Spans** exclude audit-seat cost. Release counts are lower bounds measured from each round's baseline.
