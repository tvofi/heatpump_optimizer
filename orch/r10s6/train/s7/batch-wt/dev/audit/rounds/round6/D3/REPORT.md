# D3 — test-suite gaps, audit round 6

Baseline **`e336cc2c530882a142ef298de6420706d96a6300`** (v6.6.9), audited in the
isolated worktree `~/audit-r6-D3`. Interpreter
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` (numpy 2.4.6,
scipy 1.17.1, orjson 3.12.0); everything run from the worktree root with
`PYTHONPATH=tests/hastub`, `GATE_JOBS=1`, one `env_drift.py` at a time, no
`stress.py` during the fan-out, and the comparison ref always the baseline SHA.

**This report is a PRE-SCREENED LIST, not a list of findings.** A survivor below
is a *candidate*: the quiet window runs the full `GATE_SCOPE=full
GOLDEN_MODE=drift` gate for the top six and only those become findings.

## Method — delete the decision, re-run the closure, see whether the suite notices

1. `candidates.py` walks the AST of every `custom_components/heatpump_optimizer/*.py`
   (64 modules, 49 797 lines, 2 315 `if` statements, 143 `try`) and enumerates four
   deletion shapes — `NOGUARD` (`if C:` → `if False:`), `ALWAYS` (`if C:` →
   `if True:`), `FLIPCMP` (`a >= b` → `a > b`), `NOCLAMP` (`min(a, b)` → `(a)`) —
   **6 046 sites**, weighted **3** (money/comfort/safety: optimizer, thermal model,
   price, tariff, grid fee, battery, DHW schedule, coordinator, legionella, defrost,
   power guard, …), **2** (a user-visible entity, service or config decision), **1**
   (support code).
2. `candidates.py --seed 20260922 --n 36 --cap 4` draws **36 mutants, at most four
   per module**. Seed, weights, pool size per class and per module, and the draw
   are all in `sample.json`.
3. `mutate.py --index N --apply` writes the patch into one production file and
   prints the unified diff; `--revert` restores with `git reset --hard <baseline>`.
4. `prescreen.py` measures each mutant's **closure** with
   `tests/closure.py select --files`, then runs it in ascending cost, fail-fast:
   tier 1 every cheap script, tier 2 `features.py` / `entities.py` /
   `optimality.py`, tier 3 `env_drift.py --all <baseline>`.

`tests/golden.py` is **not** run. Under `GOLDEN_MODE=drift` — the mode the gate
runs — `run.sh`'s `lane_golden` *skips* `golden.py` and runs `env_drift.py --all`
in its place, and `golden.py` run on its own does the same thing itself
(`tests/golden.py:166` hands the whole comparison to `env_drift.py --all`). Running
both would capture the same 56 scenarios twice.

### Two things the pre-screen cannot work without, that the brief does not name

**`env_drift.py` refuses a ref that resolves to HEAD**, and this worktree's HEAD
*is* the baseline SHA, so the unmutated tree cannot be compared at all:

```
$ python3 tests/env_drift.py --all e336cc2c5308…
SELF-COMPARISON: 'e336cc2c530882a142ef298de6420706d96a6300' resolves to
e336cc2c5308, which is HEAD. …
```

The comparison ref must be the baseline SHA and never HEAD, so each mutant is
**committed** before its run — detached HEAD in an isolated worktree, no branch
moves — and reverted with `git reset --hard <baseline>` after. That is also what
makes `card_drift.mjs` runnable: `tests/run.sh:462` skips it when `GOLDEN_REF`
*is* HEAD, so under an unmutated tree its only honest exit code here is the
refusal.

**A script already red on the unmutated tree is not evidence of a kill.** It
reports every mutant as killed. `prescreen.py --clean` takes a control that moves
HEAD off the baseline with an *empty* commit — the same guard conditions, an
unchanged tree — and `baseline_rc.json` records the result; a script whose control
rc is non-zero is excluded from kill attribution and appears in each record's
`red_at_baseline`. The control found exactly one:

| script | control rc | why |
|---|---|---|
| `tests/entities.py` | **1** | 3 of 1678 checks fail on the pristine baseline tree — finding D3-01 |
| every other closure script | 0 | measured; the `env_drift.py --all` control ran 358.6 s and printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked` |

Without that exclusion all 36 mutants would read as `KILLED tests/entities.py`.

## Finding

### D3-01 — three `entities.py` checks are red or green according to whether an unpinned optional package is installed

*Severity: medium. Stop-rule class: bug (instrument).*

`tests/entities.py` is in the measured production closure of **all 64** modules,
so it runs for every production change. On the pristine baseline tree of this
worktree it exits **1**, reporting `3 of 1678 ENTITY CHECKS FAILED`:

```
a3:orjson serialises through Home Assistant's json_bytes
  [ha=accepted json_bytes_ha=accepted; host pin must execute helpers.json.json_bytes, not a local dumps]
a3:orjson fails a payload orjson rejects, and passes a finite one
  [bad=[True, '0 failed HA json_bytes'] ok=[True, '0 failed HA json_bytes']]
json_bytes_ha returning b"{}" leaves a3:orjson green on an orjson-illegal payload
  [a no-op json_bytes_ha must not satisfy A3(b); the default serializer must still be json_bytes_ha …]
```

**Mechanism.** `tests/hastub/homeassistant/helpers/__init__.py:_json_bytes` takes
an `orjson` fast path first:

```python
try:
    import orjson
    return orjson.dumps(obj)
except ImportError:
    pass
# …only here does the hand-written walk() refuse non-finite floats
```

`orjson.dumps` does **not** refuse non-finite floats, so on any box where
`orjson` is importable the stub returns `b'{"k":null}'` for `{"k": inf}` and the
`walk()` below — the code the docstring calls "orjson's refusals" — is dead.
`entities.py` asserts that `json_bytes({"k": inf})` raises, so it fails.
`tests/requirements-ci.txt` does not pin `orjson`; it is present or absent with
whatever else the runner happens to have.

**Causal chain, executed both ways** (harness `json_bytes_probe.py`):

| arm | `json_bytes({"k": inf})` | `tests/entities.py` |
|---|---|---|
| as found | **accepted** | `3 of 1678 … FAILED`, exit 1 |
| perturbation: `sys.modules["orjson"] = None` | **refused** (`ValueError`) | `ALL 1678 ENTITY CHECKS PASSED`, exit 0 |

**Instrumented symbol:** `homeassistant.helpers.json.json_bytes`, the alias the
stub installs at `tests/hastub/homeassistant/helpers/__init__.py:44-46`.
**Perturbation:** make `import orjson` fail; the failure count must move 3 → 0 and
it does. **Metric definition:** the number of `R.check` failures `entities.py`
prints in its own closing line, for the pristine baseline tree.
**Proposed fix scope:** one file, `tests/hastub/homeassistant/helpers/__init__.py`
— run the non-finite walk before the `orjson` fast path, or give the fast path the
same refusals. No production code.

## The pre-screened list (all 36 mutants)

`w` is the consequence weight; *killed by* names the first script in the pre-screen
order that exited non-zero, and `tiers` which tiers it reached. `PARTIAL` means the
differential gate (tier 3) was **not** run — it is not a survivor.

| # | site | shape | w | verdict | killed by | tiers |
|---|---|---|---|---|---|---|
| 0 | `wear.py:106` | NOCLAMP | 2 | **KILLED** | tests/features.py | 1+2 |
| 1 | `thermal_model.py:1511` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 2 | `wood_fuel.py:352` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 3 | `frontend.py:147` | FLIPCMP | 2 | **KILLED** | tests/frontend.py | 1 |
| 4 | `coordinator.py:990` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 5 | `optimizer.py:3249` | FLIPCMP | 3 | **KILLED** | tests/features.py | 1+2 |
| 6 | `accuracy.py:381` | ALWAYS | 2 | **KILLED** | tests/features.py | 1+2 |
| 7 | `optimizer.py:4652` | NOCLAMP | 3 | **SURVIVOR** | — | 1+2+3 |
| 8 | `config_flow.py:445` | NOGUARD | 2 | **KILLED** | tests/config_flow_steps.py | 1 |
| 9 | `price_model.py:697` | NOGUARD | 3 | **KILLED** | tests/manual_plan.py | 1 |
| 10 | `tariff.py:61` | FLIPCMP | 3 | **KILLED** | tests/features.py | 1+2 |
| 11 | `wood_fuel.py:373` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 12 | `optimizer.py:5178` | NOCLAMP | 3 | **KILLED** | tests/manual_plan.py | 1 |
| 13 | `comfort_band.py:113` | FLIPCMP | 3 | **KILLED** | tests/config_flow_steps.py | 1 |
| 14 | `config_flow.py:2483` | ALWAYS | 2 | **KILLED** | tests/config_flow_steps.py | 1 |
| 15 | `wood_fuel.py:176` | FLIPCMP | 3 | **KILLED** | tests/features.py | 1+2 |
| 16 | `thermal_model.py:2064` | NOCLAMP | 3 | **KILLED** | tests/features.py | 1+2 |
| 17 | `silent_mode.py:79` | NOGUARD | 2 | **PARTIAL** | — | 1+2 |
| 18 | `optimizer.py:3546` | ALWAYS | 3 | **PARTIAL** | — | 1+2 |
| 19 | `thermal_model.py:1445` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 20 | `name_match.py:415` | ALWAYS | 2 | **KILLED** | tests/config_flow_steps.py | 1 |
| 21 | `thermal_model.py:2277` | ALWAYS | 3 | **KILLED** | tests/features.py | 1+2 |
| 22 | `config_flow.py:1860` | NOGUARD | 2 | **KILLED** | tests/config_flow_steps.py | 1 |
| 23 | `services.py:593` | NOGUARD | 2 | **KILLED** | tests/features.py | 1+2 |
| 24 | `coordinator.py:9878` | NOGUARD | 3 | **KILLED** | tests/manual_plan.py | 1 |
| 25 | `coordinator.py:5587` | ALWAYS | 3 | **PARTIAL** | — | 1+2 |
| 26 | `presets.py:153` | ALWAYS | 2 | **PARTIAL** | — | 1+2 |
| 27 | `coordinator.py:527` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 28 | `price_model.py:754` | FLIPCMP | 3 | **KILLED** | tests/manual_plan.py | 1 |
| 29 | `inputs.py:684` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 30 | `defrost.py:599` | ALWAYS | 3 | **PARTIAL** | — | 1+2 |
| 31 | `dhw_schedule.py:273` | ALWAYS | 3 | **KILLED** | tests/guard_pins.py | 1 |
| 32 | `legionella.py:157` | ALWAYS | 3 | **KILLED** | tests/features.py | 1+2 |
| 33 | `sysid.py:743` | FLIPCMP | 3 | **KILLED** | tests/features.py | 1+2 |
| 34 | `grid_fee.py:273` | NOGUARD | 3 | **KILLED** | tests/features.py | 1+2 |
| 35 | `config_flow.py:2273` | ALWAYS | 2 | **KILLED** | tests/config_flow_steps.py | 1 |

**Tally: 30 KILLED, 1 SURVIVOR, 5 PARTIAL, 0 unapplicable.** 12 of the 30 were
killed inside tier 1 (the cheap scripts), 18 by tier 2; the whole tier-1 sweep
costs ~60 s per mutant.

### Kill attribution

| script | mutants killed |
|---|---|
| `tests/features.py` | 18 |
| `tests/config_flow_steps.py` | 6 |
| `tests/manual_plan.py` | 4 |
| `tests/frontend.py` | 1 (`frontend.py:147`) |
| `tests/guard_pins.py` | 1 (`dhw_schedule.py:273`) |

`tests/features.py` carried 60 % of the kills, and it is the single most expensive
script in the cheap-plus-behavioural set (median 157.8 s measured). Four kills came
from scripts that cost under 10 s (`manual_plan.py`, `frontend.py`,
`guard_pins.py`), which is what makes the fail-fast ordering worth its complexity.

### The one survivor, and why it is not a gap

**index 7 — `custom_components/heatpump_optimizer/optimizer.py:4652`,
`p_dhw_run = max(0.1, min(p_max * 0.8, p_max))`**, shape `NOCLAMP`, reached tier 3
and survived `env_drift.py --all` (301.5 s, rc 0), `features.py` (159.7 s),
`optimality.py` (85.5 s) and every cheap script.

It is an **equivalent mutant**: for every real `p_max` the two forms are the same
number, because `max(0.1, ·)` already floors the negative branch and
`min(0.8x, x) == 0.8x` for `x >= 0`:

```
$ python3 -c "…"   # 15 points: -1e6, -1, -1e-9, 0, 1e-9, 0.1, 0.15, 1, 2.5, 6, 11, 16, 22, 1e6, inf
disagreements over 15 points: []
```

So the suite does not fail on it because there is nothing to fail on: the inner
`min(…)` is **dead code in the clamp**. That is a hygiene observation about
`optimizer.py:4652`, not a test-suite gap — the verifier's question ("which single
production line, in which file, and which check *should* have failed") has the
answer *none can*, and the honest reading is that the mutant is void.

### The five PARTIALs — the quiet window's real queue

These five passed every cheap script **and** `features.py`, and never saw the
differential gate; each is the answer to *"which single production line, and which
check should have failed"* if the quiet window kills it:

| # | line | file | shape | check that should have failed | why it plausibly survives tiers 1–2 |
|---|---|---|---|---|---|
| 17 | `silent_mode.py:79` | `if not windows and weekly is None: return None` → `if False` | NOGUARD | `tests/features.py` silent-mode ceiling cases, or `env_drift.py` on any scenario with a silent-mode window | the guard only skips the *no-window* case; if every fixture that reaches this function has a window, the branch is never taken |
| 18 | `optimizer.py:3546` | `if changed: … re-solve` → `if True` | ALWAYS | `tests/features.py` buffer-cap-repair cases, or `env_drift.py`'s `fuse_guard` / `cap` scenarios | an extra re-solve changes cost but not the plan when the repair already converged |
| 25 | `coordinator.py:5587` | `if entry is None or not hasattr(entry, "async_start_reauth"): return` → `if True` | ALWAYS | `tests/features.py` Tibber-reauth cases (the fixture must build an entry with `async_start_reauth`) | `FakeEntry` may lack the attribute, so the guard is already unconditionally true under the harness |
| 26 | `presets.py:153` | `if self.upper_emitter not in EMITTERS: self.upper_emitter = EMITTER_RADIATORS` → `if True` | ALWAYS | `tests/entities.py` preset-default cases, or `tests/config_flow_steps.py` | overwrites a *valid* emitter with radiators; caught only if a fixture sets a valid non-radiator upper emitter |
| 30 | `defrost.py:599` | `if delta is not None and delta > 0: self._seconds_on += delta` → `if True` | ALWAYS | `tests/features.py` defrost accrual, or `env_drift.py` on a defrost scenario | `delta` is normally a real positive number, so `True` and the guard agree on every clean fixture |

**Top six for the quiet window** (the five PARTIALs plus the one survivor, which
the quiet window should re-run to confirm the equivalence argument holds at the
full gate): **7, 17, 18, 25, 26, 30**.

## Resource use of the suite

Harness `resources.py` (counts and ratios only, contention-immune).

### The forced set

Six scripts sit in the measured production closure of **all 64** modules, so *any*
production edit forces them:

| script | recorded s | measured s on this box | what the recorded number really times |
|---|---|---|---|
| `tests/typing_ruler.py` | 0.1 | 0.6 median | — |
| `tests/structure.py` | 1.6 | 1.6 | — |
| `tests/deployment_shape.py` | 1.5 | 2.0 | — |
| `tests/entities.py` | 51.1 | 68.5 | — |
| `tests/golden.py` | 0.4 | not run (skipped in drift) | `golden.py --only __no_such_scenario__` |
| `tests/env_drift.py` | 0.4 | **301.5–358.6** | `env_drift.py --cache-key <ref> --all` |

`RESULT forced_suite_s=55.1 s` is what `closures.json` says the forced set costs.
Its two differential guards are recorded at the deliberately-cheap stub invocation
(`closures.json`'s own `_comment`, #934), so the honest forced-set figure is
**55.1 − 0.8 + 358.6 ≈ 412.9 s**, of which `env_drift.py` is **87 %**. The scoped
gate's premise is that a change buys back only what it cannot reach; for production
code it reaches everything.

### Measurement table: recorded vs measured

`wall_ratio_<script>` = median measured wall ÷ recorded seconds. Measured on a
shared box (load1 5.5–12.3), so **every wall number here is provisional** and the
quiet window re-takes it.

| script | runs | wall median | cpu median | recorded | ratio |
|---|---|---|---|---|---|
| `tests/env_drift.py` | 1 | 301.5 s | 297.8 s | 0.4 | **753.8×** |
| `tests/optimality.py` | 2 | 85.8 s | 85.2 s | 42.0 | **2.04×** |
| `tests/card.mjs` | 23 | 9.1 s | 12.3 s | 4.8 | 1.92× |
| `tests/guard_pins.py` | 15 | 0.7 s | 0.7 s | 0.4 | 1.75× |
| `tests/solar_alignment.py` | 27 | 0.8 s | 0.7 s | 0.5 | 1.60× |
| `tests/manual_plan.py` | 28 | 6.3 s | 5.6 s | 4.5 | 1.40× |
| `tests/entities.py` | 1 | 68.5 s | — | 51.1 | 1.34× |
| `tests/deployment_shape.py` | 34 | 2.0 s | 1.9 s | 1.5 | 1.33× |
| `tests/plan_view.py` | 27 | 1.0 s | 0.9 s | 0.8 | 1.25× |
| `tests/card_drift.mjs` | 27 | 4.0 s | 5.9 s | 2.9 | 1.38× |
| `tests/features.py` | 24 | 157.8 s | 146.4 s | 136.1 | 1.15× |
| `tests/validate.py` | 11 | 33.6 s | 32.8 s | 18.8 | 1.79× |
| `tests/typing_ruler.py` | 35 | 0.6 s | 0.2 s | 0.1 | 6.50× |
| `tests/config_flow_steps.py` | 30 | 13.6 s | 13.6 s | 16.8 | 0.81× |
| `tests/frontend.py` | 1 | 0.1 s | 0.1 s | 0.0 | n/a |
| `tests/structure.py` | 34 | 1.6 s | 1.6 s | 1.6 | 1.31× |

Every row above 1.15× says the recorded table sizes the gate low, and the 753.8× on
`env_drift.py` is not load: it is #934's deliberate stub record. `optimality.py`
(2.04×), `validate.py` (1.79×) and `card.mjs` (1.92×) are the next largest and are
load-plus-real-cost.

### Duplicated coverage

`closed_prod_<script>` = production modules inside that script's measured closure;
Jaccard over the production closures:

```
structure.py 64 == typing_ruler.py 64          Jaccard 1.000
golden.py 64 == env_drift.py 64 == entities.py 64 == structure.py 64 == typing_ruler.py 64
plan_view.py 45 == solar_alignment.py 45       Jaccard 1.000
optimality.py 11 == validate.py 11 == edge.py 11 == backtest.py 11   Jaccard 1.000
```

Twelve of the top twelve pairs are Jaccard **1.000** — over-approximation is not
the problem, *co-extensive closures* are. Five scripts claim the identical 64-module
set and only one of them (`env_drift.py --all`) is the differential check the drift
gate reads; `golden.py` is skipped in that mode entirely, so one of the five is a
closure entry that can never decide anything in CI. `structure.py` and
`typing_ruler.py` (1.6 s + 0.6 s) say nothing about behaviour yet are forced by
every production edit.

### Scripts that solve more than they assert

`checks_per_solve` = `R.check(` call sites ÷ solve call sites in the source:

| script | checks | solve sites | ratio |
|---|---|---|---|
| `tests/entities.py` | 1 256 | 2 | **628.0** |
| `tests/features.py` | 2 770 | 28 | 98.9 |
| `tests/stress.py` | 78 | 22 | 3.6 |
| `tests/env_drift.py` | **0** | 4 | 0.0 (by design — its instrument is a byte comparison) |
| `tests/golden.py` | **0** | 3 | 0.0 (same) |
| `tests/plan_view.py`, `tests/validate.py`, `tests/structure.py` | 0 | 0 | — |

## Non-findings

Everything checked that held, with the command or number that showed it.

- **`tests/entities.py`'s three reds are not a production defect** — the chain is
  entirely inside `tests/hastub`; production publishes nothing non-finite on these
  paths. Ledgered as the instrument finding D3-01.
- **`card_drift.mjs` works in this worktree** — control rc 0, 4.0 s median, under
  an empty commit that moves HEAD off the baseline. It refuses (rc 1) when HEAD
  *is* the ref, which is what `run.sh:462` does deliberately.
- **`env_drift.py --all` is green on the pristine tree**: exit 0,
  `NO UNCLAIMED DRIFT: 56 scenario(s) checked against e336cc2c5308…`,
  `NO STALE FIXTURE: 56 committed fixture(s) still match`, 358.6 s wall /
  311.95 s user with the warm baseline cache.
- **`optimizer.py:4652`'s `min(p_max * 0.8, p_max)` is an equivalent mutant** — 15
  probe points, zero disagreements. Not a suite gap; dead code in the clamp.
- **`coordinator.py:990`'s `tests_dir.is_dir()` guard is test scaffolding** — it
  puts `tests/hastub` on `PYTHONPATH` for a *test* run. Its kill by
  `tests/features.py` measures the harness, not the integration.
- **`wear.py:106`'s `max(0, …)` lifetime floor is caught**, by
  `tests/features.py`, 198.5 s.
- **The cheap tier is a real instrument, not a formality**: 12 of 30 kills
  (40 %) came from tier 1, four of those from scripts costing under 10 s.

## Harnesses

| path | what it is |
|---|---|
| `tools/audit/round6/D3/candidates.py` | enumerates the 6 046 candidate sites, draws the 36-mutant sample |
| `tools/audit/round6/D3/mutate.py` | applies/reverts one mutant from `sample.json`, prints the diff |
| `tools/audit/round6/D3/prescreen.py` | the tiered fail-fast closure pre-screen, with `--clean` control |
| `tools/audit/round6/D3/resources.py` | forced set, closure overlap, checks-per-solve, wall ratios |
| `tools/audit/round6/D3/json_bytes_probe.py` | both arms of the D3-01 chain, as `RESULT` lines |
| `tools/audit/round6/D3/sample.json` | seed, weights, pool, the draw |
| `tools/audit/round6/D3/baseline_rc.json` | the clean-control exit code per script |
| `tools/audit/round6/D3/results_A.json`, `results_B.json` | per-mutant records |

## Exposure

None. No `docs/audit-*.md`, no earlier round's register, no GitHub; `git log` and
`gh` were not run. The only repository text read outside the code under audit was
the two briefs, `tools/audit/README.md`, `tests/README.md` and source comments.

## What I could not finish

The fan-out budget (~2 h) does not cover `env_drift.py --all` at 301–359 s for every
mutant that survives tiers 1–2. Tier 3 is deadline-capped and the second half of the
sample (indices 18–35, run in a second worktree so two pre-screens could not fight
over one working tree) never reaches it. Five mutants are `PARTIAL` for that reason.
A `PARTIAL` record is **not** a survivor: the quiet window must run the full
`GATE_SCOPE=full GOLDEN_MODE=drift` gate on indices 7, 17, 18, 25, 26 and 30 before
any of them is called a finding.
