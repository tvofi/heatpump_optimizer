# Judge — round 3, third tranche: D3 (test-suite gaps), findings D3-01 … D3-05

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, in the detached judge
worktree `.../audit-r3/judge3`. Machine: 8-core Apple M1, macOS Darwin 25.6.0,
python3 3.11.5, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS. The five BLAS thread
variables are pinned to `"1"` in every process I started, `GATE_JOBS=1`,
`PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift`. Measured pin:
`RESULT thread_factor=1.000 ratio`. The box was shared throughout; `load1`
moved between **6.4 and 37.9** and is quoted beside every run.

`tests/stress.py` was never run, the gate lock was never taken, no branch was
created and nothing was pushed. Two mutants were committed inside this detached
worktree (D3-04 needs `recorded_at` to resolve); the tree was
`git reset --hard`ed to the baseline after every mutant and **is at the
baseline now** (`RESULT tree_restored_to=ae36eff19d8e…`).

**What I executed: 27 script-runs** — `entities.py` 6, `features.py` 7,
`structure.py` 4 (including `--record`), `optimality.py` 3, `validate.py` 3,
`solar_alignment.py` / `typing_ruler.py` / `deployment_shape.py` /
`plan_view.py` 1 each — plus 25 interpreter spawns and 75 reap trials for the
`#525` race. Harnesses, each with the header `tools/audit/README.md` requires,
under `tools/audit/round3/D3/judge/`:

| harness | what it produces |
|---|---|
| `rerun.py` | runs named scripts against named mutants in this real checkout, reading the reporter's summary out of the WHOLE output; `entities.json`, `features.json`, `arith.json` |
| `rescore.py` | the corrected aggregates and leave-one-out, from the finder's own record plus my corrections |
| `d304.py` | the whole D3-04 sequence: mutate, commit, ratchet, `--record`, re-run the closure; `d304.json` |
| `g525_race.py` | the `#525` null control's race against the production reap sequence; `g525_race.json` |

---

## 0. The instrument, re-measured — and it is worse than the report of it

Both verifiers reached the same defect by different routes. I did not take
either. I read the two lines and then measured the blast radius out of the
finder's own stored record.

`tools/audit/round3/D3/prescreen.py:157` records
`"tail": out[-1200:]`, and `verdicts.py:strict_kill` reads **all three** of its
kill arms — moved exit code, the literal `Traceback (most recent call last)`,
and the reporter's `N of M … FAILED` count — out of that tail.

```
RESULT recorded_script_runs=317 runs
RESULT tails_truncated_to_exactly_1200_chars=223 of 317 runs
RESULT tests/entities.py: 34 runs, 0 carry a summary line, baseline_rc={1}, rc never moved
RESULT tests/features.py: 19 runs, 0 carry a summary line, baseline_rc={1}, rc never moved
RESULT every_other_script: baseline_rc={0}  (rc was a working detector)
```

So the defect is **exactly two scripts wide and 53 runs deep**, and for those
53 runs two of the three arms were dark: the count arm never once saw a
summary line, and the exit code could not move because the worker slots were a
`git init` with no commit, which leaves `entities.py` and `features.py` already
red. The only live arm was "a traceback appears", and it misfired once, by
twenty characters — M24's recorded tail begins

```
't recent call last):\n  File ".../external_heat.py", line 461, in _decay\n …
TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'NoneType'
```

— the window sliced `Traceback (most recen` off the front of a production
crash. That reconciles verifier 1's `blind_runs=50`: 53 runs minus the three
where a full traceback happened to survive the slice.

Two consequences I want stated precisely, because they cut in opposite
directions:

* **`entities.py` and `features.py` hold 3,430 of the suite's assertions**
  (1,294 and 2,136), and every one of the 22 recorded survivors has at least
  one blind run in it. The finding that rests on them is inflated.
* **Nothing else is affected.** Every other script was green on the slot, so
  its exit code separated the arms. In particular the `validate.py`,
  `optimality.py`, `deployment_shape.py`, `typing_ruler.py`, `plan_view.py`
  and `manual_plan.py` zeroes that D3-05 rests on are **real**, and the
  differential gate ran for **all 22** survivors (only M22 and M34 lack it,
  and both were killed by another script).

**The arithmetic is not the problem.** I re-ran `verdicts.py` over
`prescreened_merged.json`: `PRESCREENED.md` regenerates **byte-identically**
(`diff` empty), and `analyse.py` prints `survival_rate=0.647`. The rows are
wrong, not the aggregation. The finder's record is honest enough to convict
itself, which is why three seats could.

**A method note for the record.** `tools/audit/briefs/D3.md` item 3 says in as
many words: *"Report candidates, not findings … The quiet window runs the full
`GATE_SCOPE=full GOLDEN_MODE=drift` gate for the top six survivors; **only
those become findings**."* Five findings were filed off the candidate list.
Marking them `provisional` mitigates that; it does not undo it. The
instrument defect would have been caught by the step the brief prescribed and
the finder skipped.

---

## 1. My own baselines — the null control every number below rests on

In a real checkout at the baseline, unmutated:

```
RESULT BASELINE.tests/entities.py.rc=0    (37.9s, load1 22.31)  ALL 1294 ENTITY CHECKS PASSED
RESULT BASELINE.tests/features.py.rc=0    (158.9s, load1 37.94) ALL 2136 FEATURE CHECKS PASSED
RESULT BASELINE.tests/structure.py.rc=0   (2.7s)                STRUCTURE RATCHET PASSED
RESULT BASELINE.tests/optimality.py.rc=0  (74.4s, load1 17.88)  ALL 14 OPTIMALITY CHECKS PASSED
RESULT BASELINE.tests/validate.py.rc=0    (34.0s, load1 15.49)
```

Both of the scripts the pre-screen could not read are **green here**, at
`load1` 22 and 38. That is the null control for every kill below: a moved
verdict is the mutant's doing, not the harness's.

---

## 2. D3-01 — the number

**Verdict: `weakened`, severity `medium`, value 0.441 (consequential 0.345),
stop-rule class `hygiene`.** Votes: v1 `weaken`/medium, v2 `weaken`/medium —
**comparable**: both wrote the finder's own metric definition, over the whole
output instead of a tail. The finder's 0.647 is wrong **by the finder's own
rule**, not by a rival one.

**All seven claimed kills, re-executed by me, in a real checkout:**

```
RESULT M07.tests/entities.py.rc=1  (35.4s)  1 of 1294 FAILED
       new=['the state summarises the same signals, and says so when there are none (#246)']
RESULT M27.tests/entities.py.rc=1  (32.8s)  1 of 1294 FAILED
       new=['the learned comfort weight is visible']
RESULT M19.tests/features.py.rc=1  (122.3s) 1 of 2136 FAILED
       new=['a corrupt store loads what survives and never bricks the score loop']
RESULT M24.tests/features.py.rc=1  (0.8s)   production TypeError, external_heat.py:461
RESULT M30.tests/features.py.rc=1  (96.5s)  3 of 2136 FAILED
       new=['a configured entity that does not exist is missing_entity',
            'a missing entity is reported as such',
            'and the freeze reason names both the condition and the key (missing_entity)']
RESULT M32.tests/features.py.rc=1  (102.4s) 2 of 2136 FAILED
       new=['and in the weekly grammar when the configuration names days',
            'and renders back to the string the user typed']
RESULT M33.tests/features.py.rc=1  (115.6s) 1 of 2136 FAILED
       new=['a recent run blocks another']
RESULT mis_scored_kills=7 of 7 reproduced
```

Every one is `rc 0 -> 1`: merge-blocking. Every new check name is the semantic
twin of its own mutation. Three **negative controls** in the same pass — M12,
M16 (`entities.py`) and M14 (`features.py`) — stay green, so the re-run is not
a script that simply fails under load. My M30 shows **three** new names where
verifier 2 recorded four; the fourth was the `#525` wall-clock check (§7),
which did not fire in my run. That isolates the mutation's own three and is a
small correction in the finding's disfavour, so I take it.

**Five equivalent mutants, each settled by a production line I read myself at
the baseline blob, not by an opinion:**

| id | line | why no input distinguishes it |
|---|---|---|
| M05 | `optimizer.py:4771` `max(c_dhw, 0.05)` dropped | `c_dhw` has exactly **one** assignment in the file, `optimizer.py:4000` `max(params.dhw_tank_thermal_mass, 0.05)`; every other appearance is a parameter or a `c_dhw=c_dhw` keyword, and `_repair_dhw_floor` has one caller (4335). The clamp re-clamps a clamped value. |
| M10 | `coordinator.py:2293` early return | every action in `_async_drive_pumps` sits inside `if vvc_entity:` (2298) or `if space_entity:` (2317); with both falsy the mutated body reaches neither. The docstring contract *"only entities the user explicitly configured are ever touched"* is enforced by those two guards, so the finder's bullet states the contract wrongly. |
| M17 | `thermal_model.py:2435` `solar_radiation is None` | `_Horizon.solar_radiation` is typed `np.ndarray` (`optimizer.py:1180`) and `optimize()` replaces `None` at 2243 **before** the horizon is built; both batch call sites (3341, 5433) pass that field. |
| M31 | `thermal_model.py:324` layout cache | the cached value is computed purely from `key` and is an immutable `str`; disabling the memo is a CPU change only. |
| M06 | `optimizer.py:1134` `values.size >= n_steps` | the only production producer is `coordinator.py:_baseline_house_load`, which returns `np.zeros(n_steps)` or `np.full(n_steps, …)`, so `size == n_steps` and the mutant's `concatenate([values, np.full(0, …)])` is the same array. **Weaker than the other four:** at `size > n_steps` the mutant would *raise* rather than truncate, so it is equivalent on production paths rather than absolutely. |

**The corrected aggregates, re-derived by me (`judge/rescore.py`):**

```
RESULT finder_survival=22 of 34 = 0.647   loo 0.600-0.710
RESULT corrected_survival=15 of 34 = 0.441   loo 0.367-0.484 (min: drop optimizer.py)
RESULT consequential_survival=10 of 29 = 0.345   loo 0.296-0.385 (min: drop optimizer.py)
```

**Which number is the number.** 0.441 is the one every cell of which was
decided by a run, and it is the honest correction of the claim as written.
0.345 is the better mutation score — equivalent mutants are not suite gaps —
but five of its twenty-nine cells are decided by static reading rather than
execution, and one of those five (M06) is equivalent only on production paths.
**I put the headline at 0.441 and carry 0.345 as the consequential figure**,
and neither is 0.647.

Leave-one-out behaves the way the finder's did — the aggregate is not one
module's doing — but it is carried *further* by `optimizer.py` after
correction than before (dropping it takes 0.441 to 0.367, against 0.647 to
0.600). The per-module story the report narrates was never established: at
n = 34 with cells of 1–4, verifier 2's permutation test gives p = 0.065 on the
finder's labels and p = 0.207 on the corrected ones. I did not re-run the
permutation test; I do not need it, because the finder's own leave-one-out is
the aggregate's defence and the module spread is not a claim I am upholding.

**Why `medium` and not `high`.** Ten single-line defects that merge green is a
real and useful finding, and the ones I would not want shipped are named:
`coordinator.py:3898` (learned heat loss never persisted — every restart
forgets it), `price_model.py:137` (§4), `sensor.py:1002` and `:885` (§3),
`dhw_learning.py:344` (the tank's cooling coefficient never learns). But the
headline as filed reads as an oracle indictment — *"survives the whole fast
gate, including the differential golden gate"* — of a gate whose value oracle
is byte-exact and which, on verifier 2's coverage measurement, **never
executes 14 of the 22 survivors' lines at all**. The deficit is inputs, not
assertions, and the remedy is fixtures. Two of the five bullets the finding
leads with (M05, M10) are equivalent mutants, which is a direct failure of
`D3.md` item 4 — *"for every survivor, which single production line … and
which check should have failed"*.

**Residual, and it is the round's, not mine.** `tests/stress.py` sits in the
closure of **7** corrected survivors (M04, M05, M06, M11, M17, M20, M31) and
was never run. After the equivalence correction only **three of the ten
consequential survivors** (M04, M11, M20) have it, so the unrun lane could
move the consequential number by at most 3 of 29 — 0.345 down to 0.241 in the
worst case, never up. `stop_rule_class` `hygiene`: no shipped line does
anything wrong; this measures how hard the suite is to fool.

---

## 3. D3-02 — "a published entity value is pinned by shape, never by value"

**Verdict: `weakened`, severity `medium`, value 2 of 4, stop-rule class
`hygiene`.** Votes: v1 `weaken`/medium, v2 `weaken`/medium.

The universal is **false**, and I refuted it twice.

*By reading.* In `tests/entities.py` at the baseline:

```
RESULT native_value_references=70 sites
RESULT published_accessor_comparison_lines=48 lines   (native_value |
       extra_state_attributes | current_temperature, compared with == != approx)
RESULT exact_literal_value_pins=32 lines
  entities.py:914  by_name["Measured Power"].native_value == 2.4
  entities.py:919  by_name["Observed COP"].native_value == 3.1
  entities.py:993  by_name["Monthly Peak Power"].native_value == 7.2
  entities.py:1060 by_name["Comfort Weight"].native_value == 6.4   …
```

*By execution.* Two of those pins kill two of the four `sensor.py` mutants,
`rc 0 -> 1` (§2). `entities.py` is in `sensor.py`'s six-script closure, so both
are merge-blocking on any pull request that touches `sensor.py`.

**Metric definitions: `not comparable` between the two verifiers.** v1's *"63
check sites"* counts sites over three accessors by its own net; v2's *"70"*
counts `native_value` textual references. They are different populations and
neither is wrong. My own measurement reproduces v2's 70 exactly as a reference
count and adds the number that actually settles the claim: **32 exact-literal
value pins**. The *kill* metric — 2 of 4 — is the same in both seats and in
mine, and it agrees.

**What survives, and it is the finding's own headline example.** M12
(`sensor.py:1002`, `UpperFloorTempSensor.native_value` returns `None` for every
state the integration can be in) and M16 (`sensor.py:885`,
`HeatPumpActionSensor.extra_state_attributes` returns `None` where Home
Assistant is owed a mapping) leave `entities.py` at `ALL 1294 … PASSED` in my
own run. `sensor.py`'s closure holds nothing else CI runs that could see them
— `golden.py` is skipped under `GOLDEN_MODE=drift`, the mode CI sets. **So
"a sensor that goes permanently blank merges green" is true for that sensor,
and the quantifier around it is false.**

The mechanism survives in a relocated form and that is worth keeping: verifier
2's coverage run shows **0 of 4** mutated `sensor.py` lines is executed while
all 55 golden fixtures are built, because the fixtures record
`coordinator.data` and never evaluate an entity property. The golden lane is
value-blind to entities; `entities.py` closes that by hand, name by name, for
the sensors somebody cared about. `medium`, because the residue is two
unpinned publishing surfaces with a user-visible consequence and a one-line
fix beside the thirty-two that already exist — not the whole published
surface.

---

## 4. D3-03 — the two non-finite guards

**Verdict: `weakened`, severity `medium`, value 1 of 2, stop-rule class
`hygiene`.** Votes: v1 `weaken`/low, v2 `weaken`/medium — same metric (1 of 2),
different severity call; I side with medium and say why.

*Half refuted, by my own run.* `accuracy.py:378` (`if not np.isfinite(parsed):
continue`, under the comment *"a poisoned sigma would reach the comfort bounds
as a NaN margin"*) **is pinned**: `tests/features.py` goes `rc 0 -> 1` on the
check *a corrupt store loads what survives and never bricks the score loop*.
`features.py` is in `accuracy.py`'s closure and runs on every pull request that
touches it. The finding's sentence *"the guard's own author wrote down the
consequence; nothing in the suite reproduces it"* is exactly backwards, and it
is the half the report argues hardest.

*The survivor stands and is worse than filed.* `price_model.py:137`
(`if not np.all(np.isfinite(values)): return False` in
`PriceShapeModel.observe_day`) survives `features.py` in my own run
(`ALL 2136 … PASSED`, 146.1 s, load1 26.17). I traced the consequence chain in
the baseline source rather than taking verifier 2's word:

* `mean = float(np.mean(values))` is `nan`; the guard below it, `mean <= 1e-6`,
  **cannot fire** — `nan <= 1e-6` is `False`.
* `normalised = np.clip(values / nan, SHAPE_MIN, SHAPE_MAX)` is all-`nan`;
  `updated / max(float(np.mean(updated)), 1e-6)` is `max(nan, 1e-6)` → `nan`.
* `self.shapes[idx]` becomes 24 `nan`s and `days[idx]` increments: **one bad
  hour poisons all 24 hours of that weekday profile, permanently**, and
  `as_dict()` persists it. That is R3-D1-01's mechanism arriving by a second
  route.

The learned shape is the relative cost of each hour — the thing the plan is
bought against. A test-suite gap on that guard is `medium`: nothing is wrong in
the shipped tree (the guard is there), but what it would let through is wrong
money, silently, and persisted.

---

## 5. D3-04 — caught only by a ratchet that calls it an improvement

**Verdict: `verified`, severity `medium`, value 1 of 12 scripts moves and it
reports `BETTER`, stop-rule class `hygiene`.** Votes: v1 `verify`/medium,
v2 `verify`/medium.

I ran the whole sequence myself rather than confirming two confirmations
(`judge/d304.py`, M09 = `coordinator.py:5433`, the Open-Meteo irradiance
fallback for a house with no pyranometer):

```
RESULT baseline_structure_rc=0 code (2.7s)  STRUCTURE RATCHET PASSED
RESULT mutant_committed=b5b07ded
RESULT structure_rc_before_record=1 code (3.2s)
   | RESULT cut_fetch=131 count
   | cut_fetch            132     131     -1  BETTER (lower is better)
   | 1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED
   | Nothing here is a violation. Run the command above, commit the …
RESULT structure_record_rc=0 code (3.0s)   tests/structure_budgets.json | 4 ++--
RESULT cut_fetch_after_record=131 count
RESULT structure_rc_after_record=0 code (2.8s)  STRUCTURE RATCHET PASSED
RESULT after_record.tests/entities.py.rc=0 code (39.5s)
RESULT after_record.tests/solar_alignment.py.rc=0 code (1.3s)
RESULT after_record.tests/deployment_shape.py.rc=0 code (2.9s)
RESULT after_record.tests/plan_view.py.rc=0 code (1.6s)
RESULT after_record.tests/typing_ruler.py.rc=0 code (0.2s)
RESULT closure_green_after_record=5 of 5 scripts (the Open-Meteo fallback still dead)
```

The perturbation is `--record` itself and the number moves in the stated
direction: rc `1 -> 0`. The null control is the unmutated ratchet at rc 0. The
distance between a dead irradiance input and a green gate is one documented
command and two lines of JSON.

Two corrections of emphasis I make in the finding's favour and one against:

* **In its favour.** My `entities.py` run is on the *mutant* and passes — the
  value oracle does not see it either, independently of the pre-screen's
  broken detector.
* **In its favour.** Verifier 1 drove the Node lane (`card.mjs`,
  `card_drift.mjs`), which the finder never did, and both pass.
* **Against it.** The report leans on *"`tests/solar_alignment.py` — the script
  whose one job is that irradiance lands on the right optimizer steps — runs
  and passes"*. That script's own docstring scopes it to `_forecast_arrays`,
  the coordinator-to-optimizer seam; the mutated line is in
  `_update_current_state`, which decides whether Open-Meteo is consulted at
  all. It passes because the defect is outside the seam it names, not because
  it is weak at its job.

**Why `medium` and not `high`.** What is really true here is that the mutant is
caught by **nothing**; `structure.py`'s red is an accounting artefact of a line
disappearing, and its remedy is documented, correct for its own purpose, and a
green light for this. That is nasty — a ratchet congratulating a deletion it
should be blind to is worse than silence — but it is a gate-design weakness
with a bounded cost and a human still reading the diff, not a user-visible
defect. `medium` as filed.

---

## 6. D3-05 — the two end-to-end solver scripts, and the restraint

**Verdict: `verified`, severity `low`, value 0 kills in 8 runs each (line
deletion) against `optimality.py` 2 of 2 (arithmetic), stop-rule class
`hygiene`.** Votes: v1 `verify`/low, v2 `verify`/low.

The zero is **not** an artefact of the truncation defect: `validate.py` and
`optimality.py` both had `baseline_rc=0` on every slot run, so the exit code
was a working detector for them throughout (§0). Their zero is real, and so is
the rest of the never-killed list.

The provisional gap is closed and empty — verifier 1 ran `edge.py` 12 times and
`backtest.py` 12 times (8 of the 12 mutants have both in their measured
closure) for **0 kills in 24 runs**, and the never-driven Node lane for **0 in
39**. I did not re-run those; they are negative results on scripts whose exit
code is a working detector, and re-taking 1,055 s of green on a shared box buys
nothing.

**What I did run is the perturbation, because it is what decides the
finding:** two *arithmetic* mutants — nothing deleted, no line count moved —
against both scripts.

```
RESULT BASELINE.tests/optimality.py.rc=0 (74.4s, load1 17.88) ALL 14 OPTIMALITY CHECKS PASSED
RESULT BASELINE.tests/validate.py.rc=0   (34.0s, load1 15.49)
RESULT A1.tests/optimality.py.rc=1 (64.5s)  1 of 14 FAILED   [optimizer.py:1960,
       np.sum(prices * p) -> np.sum(np.roll(prices,1) * p): every step priced at
       the previous step's price]
RESULT A1.tests/validate.py.rc=0   (32.5s)  killed=False
RESULT A4.tests/optimality.py.rc=1 (80.5s)  1 of 14 FAILED   [thermal_model.py:1464,
       wind_factor 1.0 + … -> 1.0 - …: wind now REDUCES modelled heat loss]
RESULT A4.tests/validate.py.rc=0   (31.8s)  killed=False
RESULT arithmetic_kills_optimality=2 of 2   RESULT arithmetic_kills_validate=0 of 2
```

So **the finder's restraint is right, and for the reason it did not have.**
Line deletion is the wrong operator for an end-to-end solver script:
`optimality.py` is not a dead script, it is a *quality floor* that notices a
mispriced objective and a sign-flipped wind term and does not notice a guard
whose body never runs. `validate.py`, at 22.8 assertions per solve against
`optimality.py`'s 2.8, kills neither — assertion density is not what catches
arithmetic. Proposing no deletion off eight line-deletion mutants was correct,
and a larger arithmetic sample is the measurement that would price these two
scripts honestly.

One honest discrepancy: my kills land on the check *"greedy same-energy
challenger does not rout the optimizer"*, verifier 2's on *"the forced-off pin
is honoured, or reported as safety-released"*. Both are `1 of 14`. The **kill**
reproduces; **which** of `optimality.py`'s arms trips first does not, so do not
build a claim on the arm name. The unmutated run is green at the same load, so
the kill is the mutant's doing.

I did **not** re-execute `solve_budget.py`'s 22.8-vs-2.8 assertions-per-solve
ratio (852.8 s under instrumentation in the finder's own record). Neither
verifier did either. That half of item 5 is unjudged and is not part of this
verdict.

---

## 7. The `#525` flake — a finding-shaped thing nobody filed

**Verdict: worth its own issue. `D3-FLAKE`, severity `medium`, stop-rule class
`bug` — the only `bug` in this tranche, because it is the only thing here that
is wrong in the shipped tree rather than absent from it.**

`tests/features.py:24114`'s null control asserts
`_g525_block_ticks <= 5 and _g525_block_s >= 1.5` — a **wall-clock lower
bound**. `_g525_measure` spawns a child running
`signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)`, plants it as
`coordinator._PROCESS_WORKER`, and reaps it after a single
`await asyncio.sleep(0.05)`. Production's `_shutdown_process_pool` stalls for
the full `worker.wait(timeout=2)` **only if the child survives `terminate()`**
— which requires the child's interpreter to have reached `signal.signal` inside
that 50 ms. If `SIGTERM` lands first the child dies on the default action,
`wait` returns at once, and `_g525_block_s` is `0.00`. That is the signature
the finder saw and could not explain.

Measured by me against the production reap sequence (close stdin, `terminate`,
`wait(timeout=2)`) and the test's own stubborn child, 25 trials per arm:

| arm | head start | `race_rate` (elapsed < 1.5 s) | elapsed min |
|---|---|---|---|
| **what `features.py` uses** | 0.05 s | **0.08 (2 of 25)** | 0.0017 s |
| null control | 1.00 s | **0.00 (0 of 25)** | 2.0014 s |
| perturbation | 0.02 s | **0.80 (20 of 25)** | 0.0015 s |

```
RESULT handler_delay_spawns=25 spawns
RESULT handler_delay_median=42.3 ms  p90=44.1 ms  max=70.5 ms
RESULT margin_at_50ms_min=-20.5 ms
RESULT load1=33.23 -> 18.48
```

The perturbation moves the metric in the stated direction, the null control
pins it at zero, and — this is where I go past both verifiers — **I observed
the failure at the head start `features.py` actually uses, 2 of 25**, and the
interpreter's worst handler-install time, **70.5 ms, is past the 50 ms budget
outright**. Verifier 1 measured 37.6 ms median / 47.6 ms worst at `load1` 7.9
and called it 2.4 ms of margin; at `load1` 18–33 the margin is **negative**.
The finder's 1-in-7 at `load1` 15–17 is what this distribution does.

It fires **twice per `features.py` run**: `_g525_free_ticks >= 50 and
_g525_free_s >= 1.5` is the sibling assertion and spawns its own child on the
same 50 ms budget, so at my measured rate roughly **15 % of `features.py` runs
carry a spurious red**, on a script that is in almost every module's closure.

Why an issue rather than a propagation: it is outside all five D3 findings, so
it cannot ride on one; it is not a third instance of a recurring error, so it
is not an RCA; and it has now been independently verified three times (finder
observed, verifier 1 quantified, judge re-measured with a harder number), which
is the condition `CLAUDE.md`'s fallback chain sets before filing. Severity
`medium` — no user consequence at all, but a nondeterministic merge-blocking
check has a real, recurring, bounded cost and trains a reviewer to re-run reds.
The fix is in the test, not in production: wait for a readiness byte from the
child before reaping, or assert on the child's *state* (that it outlived the
`terminate`) instead of on a wall-clock floor.

**What I am deliberately not endorsing.** Verifier 2 reports a second flaky
check, `a8:register_once`, firing on five mutually unrelated mutants with a
different random `extra=['…__dup']` set each time. I did not see it once in
**6 `entities.py` runs** in this serial, real checkout. It appeared only under
three concurrent worker slots, and the finder's own report already warns that
concurrent `prescreen.py` runs need distinct `--slot-prefix` values. It is
**unresolved, not established**, and it should not be filed on this evidence.

---

## 8. The register lines

| finding | verdict | severity | my number | votes as counted |
|---|---|---|---|---|
| D3-01 | `weakened` | medium | **15 of 34 = 0.441**; consequential 10 of 29 = 0.345; LOO 0.367–0.484 / 0.296–0.385 | v1 weaken/medium, v2 weaken/medium — comparable, both reproduce |
| D3-02 | `weakened` | medium | **2 of 4** `sensor.py` mutants survive; 32 exact-literal value pins in `entities.py` | v1 weaken/medium, v2 weaken/medium — kill metric comparable and identical; the 63-vs-70 site counts are **not comparable** |
| D3-03 | `weakened` | medium | **1 of 2** guards unpinned; the survivor turns 24 of 24 shape hours `nan` and persists them | v1 weaken/low, v2 weaken/medium |
| D3-04 | `verified` | medium | **1 of 12** scripts moves, reporting `BETTER`; `--record` → rc 0 with the fallback dead; 5 of 5 closure scripts I re-ran green | v1 verify/medium, v2 verify/medium |
| D3-05 | `verified` | low | **0 kills in 8 runs each** on line deletion; `optimality.py` **2 of 2** on arithmetic, `validate.py` **0 of 2** | v1 verify/low, v2 verify/low |
| D3-FLAKE | `verified` (new) | medium | `race_rate` **0.08** at the 50 ms head start the check uses, 0.00 at 1.0 s, 0.80 at 20 ms; handler delay max **70.5 ms** | not voted — raised by the finder as unreproduced, quantified by v1, re-measured here |

Nothing in this tranche is `unreproduced`. Nothing is `refuted` outright: each
of the three weakened findings keeps a narrower claim that I executed.

**What the round still owes on D3:** `tests/stress.py` against M04, M11 and M20
(the three consequential survivors whose closure names it); `solve_budget.py`'s
assertions-per-solve ratio, which no seat re-executed; and a larger *arithmetic*
sample, which is the operator class that would actually price `validate.py` and
`optimality.py`. The instrument defect belongs in the round record and in
whatever guidance `COMMON.md` carries about mutation work: **never read a kill
signal out of a truncated tail, and never screen in a slot whose baseline is
already red.**
