# Monthly savings history Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Savings tab on the expanded card listing each booked month’s thermostat-baseline SEK, actual SEK, savings SEK, and savings %, with the open month calendar-pro-rata and labelled estimated.

**Architecture:** Book `savings_baseline` and `savings_actual` on the existing `MonthlyLedger` at interval settle. Derive savings; never book a third line. The last solve’s thermostat baseline (space + DHW) rides on `OptimizationResult.baseline_power_schedule` as a pickle-safe float list, is copied into `get_current_action()["baseline_kw"]` using that method’s existing step index, and is stored on `_pending_prediction` at interval start. Row building and pro-rata live in `ledger.py` so `coordinator.py` stays at most a few call sites. Publish `data["savings_months"]` to a new always-on `MonthlySavingsSensor`; the card reads `_monthly_savings`.

**Tech Stack:** Home Assistant custom component (coordinator / sensor / ledger), Lovelace card (`heatpump-optimizer-card.js`, no build step), `tests/features.py` + `tests/entities.py` + `tests/card.mjs` (`R.check` / `check`, not pytest).

**Spec:** `docs/superpowers/specs/2026-09-05-monthly-savings-history-design.md`

## Global Constraints

- `claims-for:` stays `6.3.14`. Do not re-record value-bearing goldens.
- Do not raise `SOLVE_BUDGET_RATIO` or `SCENARIO_BUDGET_FACTOR`.
- Structure ratchet only moves down. Never re-record `cross_seam_fraction`. Re-measure at **this PR’s merge-base**. After W3-G3, `coordinator_loc` is at ceiling: **pay** (helpers in `ledger.py`) or stop and ask. Do not raise `coordinator_loc`, `max_class_loc`, `coordinator_attrs`, or `coordinator_methods`.
- W3-G3 process route: worker instance attrs do not come back. Baseline series must be lists on `OptimizationResult`. Never put those fields in `data[]` or on a plan sensor.
- Energy-only table: no deferred, capacity, or grid fee. Spot is `_current_spot_price` already on pending. `dt` is settled elapsed hours.
- Savings is derived: `baseline.sek − actual.sek`. Skip **both** lines when `baseline_kw` is missing. Do not write zeros as a stand-in for “no plan”.
- `savings_pct` is omitted (`null`) when `baseline_sek <= 0.01`. Do not publish `0.0` as “no pct”. Clip otherwise matches `_savings_percentage` (`−100..100`).
- Never hand-edit `VERSION`, the manifest version, `RELEASE_NOTES.md` headings, or `CARD_VERSION` — `tools/release/stamp.py` only.
- One PR. `Closes #460` on its own line. Do not reuse #457. Do not `Closes #232` / `#234`.
- Gate lock `/tmp/hpo-gate.lock` if the select is `MODE: FULL` or names `tests/stress.py`. This plan’s default select is features / entities / card / structure — no lock.
- Three-dot diffs vs merge-base. `cp` backups for source mutation; restore and confirm md5.
- This repo’s tests are plain scripts, not pytest. Commands below are exact.

## Seat (do not skip)

**3L-G7.** One PR, after **3L-G6 (#457)**, before Wave 4. If #457 is still blocked, sit after **3L-G5 (#408)** so Wave 4 does not wait.

Do not start production code while W3-G3 holds `coordinator.py`, or while #408 holds coordinator/config.

Implement in a **fresh** worktree from `origin/main` **after** those seats, e.g. `~/wt/3l-g7-monthly-savings`. Do not implement in `~/wt/docs-monthly-savings` (docs-only) or in a dirty W3-G3 checkout.

Model: Grok 4.6 extra high.

## File map

| File | Responsibility |
|---|---|
| `custom_components/heatpump_optimizer/ledger.py` | `pro_rata_factor`, `savings_pct`, `MonthlyLedger.add_savings_settlement`, `MonthlyLedger.savings_months` |
| `custom_components/heatpump_optimizer/optimizer.py` | `OptimizationResult.baseline_power_schedule`; `_build_result` writes it; both solve paths pass space+DHW kW; `get_current_action` copies current step to `baseline_kw` |
| `custom_components/heatpump_optimizer/coordinator.py` | `pending["baseline_kw"]` from `_current_action`; one settle call; `data["savings_months"]` in `_build_data_dict` |
| `custom_components/heatpump_optimizer/sensor.py` | Register `MonthlySavingsSensor` (`_monthly_savings`) |
| `custom_components/heatpump_optimizer/{strings.json,translations/en.json,translations/sv.json,icons.json}` | Sensor name + icon |
| `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` | Third tab, table, i18n |
| `tests/features.py` | Ledger + settlement + action + publish |
| `tests/entities.py` | Sensor, holes pin, object-id / suffix pin |
| `tests/card.mjs` | Tab, empty copy, estimated row |
| `tests/structure_budgets.json` | Re-measure only; record **improvements** only |

Do not add a Store, a plan-sensor attribute, or a `ContractComparisonSensor` attribute.

---

### Task 1: Ledger pro-rata and percent

**Files:**
- Modify: `custom_components/heatpump_optimizer/ledger.py`
- Test: `tests/features.py` (new section immediately before `sys.exit(R.close("FEATURE CHECKS"))`)

**Interfaces:**
- Consumes: `datetime`, `calendar.monthrange`
- Produces: `pro_rata_factor(now: datetime) -> float`, `savings_pct(baseline_sek: float, savings_sek: float) -> float | None`

- [ ] **Step 1: Write the failing checks**

Append before `sys.exit(R.close("FEATURE CHECKS"))` in `tests/features.py`:

```python
R.section("3L-G7 — monthly savings history")

from datetime import datetime as _SavDT
from heatpump_optimizer.ledger import (
    MonthlyLedger as _SavLedger,
    month_key as _sav_month_key,
    pro_rata_factor as _sav_factor,
    savings_pct as _sav_pct,
)

_feb10 = _SavDT(2026, 2, 10, 15, 0)
_feb1 = _SavDT(2026, 2, 1, 8, 0)
_jan31 = _SavDT(2026, 1, 31, 12, 0)
R.check(
    "February 10 uses 28 / 10",
    abs(_sav_factor(_feb10) - 2.8) < 1e-12,
    repr(_sav_factor(_feb10)),
)
R.check(
    "day 1 uses divisor 1 (February 1 is 28 / 1)",
    abs(_sav_factor(_feb1) - 28.0) < 1e-12,
    repr(_sav_factor(_feb1)),
)
R.check(
    "January 31 uses 31 / 31",
    abs(_sav_factor(_jan31) - 1.0) < 1e-12,
    repr(_sav_factor(_jan31)),
)
R.check(
    "pct is baseline-relative and clipped",
    abs(_sav_pct(100.0, 60.0) - 60.0) < 1e-12
    and abs(_sav_pct(100.0, 200.0) - 100.0) < 1e-12
    and abs(_sav_pct(100.0, -200.0) - (-100.0)) < 1e-12,
)
R.check(
    "pct is omitted when baseline_sek <= 0.01, not published as 0.0",
    _sav_pct(0.01, 0.0) is None and _sav_pct(0.0, 1.0) is None,
    repr(_sav_pct(0.01, 0.0)),
)
```

- [ ] **Step 2: Run the script and confirm the new checks fail**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: import error `cannot import name 'pro_rata_factor'` (or the first `R.check` never runs). Do not treat a full-file green as success.

- [ ] **Step 3: Implement the two helpers**

Add to `ledger.py` (stdlib `calendar` import at top). Keep this module free of Home Assistant imports.

```python
import calendar


def pro_rata_factor(now: datetime) -> float:
    """Calendar days in this month over max(1, day-of-month)."""
    days = calendar.monthrange(now.year, now.month)[1]
    return days / max(1, now.day)


def savings_pct(baseline_sek: float, savings_sek: float) -> float | None:
    """Same clip as optimizer._savings_percentage, but None when the baseline is ~0.

    The optimizer helper returns 0.0 in that case; the published row must omit
    the percentage instead of claiming 0 %.
    """
    if baseline_sek <= 0.01:
        return None
    return float(np.clip(savings_sek / baseline_sek * 100.0, -100.0, 100.0))
```

- [ ] **Step 4: Re-run**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: `ALL <n> FEATURE CHECKS PASSED` and the five new `ok` lines.

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/ledger.py tests/features.py
git commit -m "feat: monthly-savings pro-rata and percent helpers"
```

---

### Task 2: Ledger settlement writer and row builder

**Files:**
- Modify: `custom_components/heatpump_optimizer/ledger.py`
- Test: `tests/features.py` (same section)

**Interfaces:**
- Consumes: `pro_rata_factor`, `savings_pct`, `MonthlyLedger.add`, `MonthlyLedger.line`, `month_key`
- Produces:
  - `MonthlyLedger.add_savings_settlement(when, *, baseline_kw: float | None, actual_kwh: float, spot: float, dt: float) -> None`
  - `MonthlyLedger.savings_months(now: datetime) -> list[dict]` with keys `month`, `baseline_sek`, `actual_sek`, `savings_sek`, `savings_pct`, `estimated`

- [ ] **Step 1: Write the failing checks**

Append in the same section:

```python
_led = _SavLedger()
_led.add_savings_settlement(
    _feb10, baseline_kw=2.0, actual_kwh=0.5, spot=2.0, dt=0.5
)
_k = _sav_month_key(_feb10)
_base = _led.line(_k, "savings_baseline")
_act = _led.line(_k, "savings_actual")
R.check(
    "settlement books baseline kW×dt and actual kWh at spot",
    abs(_base["kwh"] - 1.0) < 1e-12
    and abs(_base["sek"] - 2.0) < 1e-12
    and abs(_act["kwh"] - 0.5) < 1e-12
    and abs(_act["sek"] - 1.0) < 1e-12,
    f"base {_base} actual {_act}",
)
_led_skip = _SavLedger()
_led_skip.add_savings_settlement(
    _feb10, baseline_kw=None, actual_kwh=0.5, spot=2.0, dt=0.5
)
R.check(
    "missing baseline_kw writes neither line",
    "savings_baseline" not in _led_skip.months.get(_k, {}).get("lines", {})
    and "savings_actual" not in _led_skip.months.get(_k, {}).get("lines", {}),
)
_led.add(_feb10, "spot", kwh=1.0, sek=2.0)
_led.add(_SavDT(2026, 1, 15), "spot", kwh=10.0, sek=20.0)
_rows = _led.savings_months(_feb10)
R.check(
    "a month without savings_baseline is omitted, even if spot was booked",
    [r["month"] for r in _rows] == ["2026-02"],
    repr([r["month"] for r in _rows]),
)
R.check(
    "open month scales all three SEK columns and leaves pct unchanged",
    _rows[0]["estimated"] is True
    and abs(_rows[0]["baseline_sek"] - 5.6) < 1e-9
    and abs(_rows[0]["actual_sek"] - 2.8) < 1e-9
    and abs(_rows[0]["savings_sek"] - 2.8) < 1e-9
    and abs(_rows[0]["savings_pct"] - 50.0) < 1e-9,
    repr(_rows[0]),
)
_led.add_savings_settlement(
    _SavDT(2026, 1, 20), baseline_kw=1.0, actual_kwh=1.0, spot=1.0, dt=1.0
)
_ordered = [r["month"] for r in _led.savings_months(_feb10)]
R.check(
    "rows are oldest first, newest last",
    _ordered == ["2026-01", "2026-02"],
    repr(_ordered),
)
_closed = [r for r in _led.savings_months(_feb10) if r["month"] == "2026-01"][0]
R.check(
    "a closed month is unscaled",
    _closed["estimated"] is False
    and abs(_closed["baseline_sek"] - 1.0) < 1e-9
    and abs(_closed["actual_sek"] - 1.0) < 1e-9,
    repr(_closed),
)
```

Numbers: 2.0 kW × 0.5 h = 1.0 kWh × 2.0 SEK/kWh = 2.0 SEK baseline; actual 0.5 kWh × 2.0 = 1.0 SEK; savings 1.0; raw % = 50. Open-month factor 2.8 → 5.6 / 2.8 / 2.8.

- [ ] **Step 2: Run and confirm fail**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: `AttributeError: 'MonthlyLedger' object has no attribute 'add_savings_settlement'`

- [ ] **Step 3: Implement**

On `MonthlyLedger` in `ledger.py`:

```python
    def add_savings_settlement(
        self,
        when: datetime,
        *,
        baseline_kw: float | None,
        actual_kwh: float,
        spot: float,
        dt: float,
    ) -> None:
        """Book the two savings lines, or neither.

        ``baseline_kw is None`` means no plan covered the interval — skip.
        A finite 0.0 kW is a real thermostat-off step and must book.
        ``actual_kwh`` is already energy (spot + immersion), not kW.
        """
        if baseline_kw is None:
            return
        if not (
            np.isfinite(baseline_kw)
            and np.isfinite(actual_kwh)
            and np.isfinite(spot)
            and np.isfinite(dt)
        ):
            return
        base_kwh = float(baseline_kw) * float(dt)
        self.add(
            when, "savings_baseline", kwh=base_kwh, sek=base_kwh * float(spot)
        )
        self.add(
            when,
            "savings_actual",
            kwh=float(actual_kwh),
            sek=float(actual_kwh) * float(spot),
        )

    def savings_months(self, now: datetime) -> list[dict]:
        """Published rows: months that booked savings_baseline, oldest first."""
        open_key = month_key(now)
        factor = pro_rata_factor(now)
        rows: list[dict] = []
        for key in sorted(self.months):
            lines = self.months[key].get("lines") or {}
            if "savings_baseline" not in lines:
                continue
            baseline_sek = float(self.line(key, "savings_baseline")["sek"])
            actual_sek = float(self.line(key, "savings_actual")["sek"])
            estimated = key == open_key
            if estimated:
                baseline_sek *= factor
                actual_sek *= factor
            savings_sek = baseline_sek - actual_sek
            rows.append(
                {
                    "month": key,
                    "baseline_sek": round(baseline_sek, 2),
                    "actual_sek": round(actual_sek, 2),
                    "savings_sek": round(savings_sek, 2),
                    "savings_pct": savings_pct(baseline_sek, savings_sek),
                    "estimated": estimated,
                }
            )
        return rows
```

- [ ] **Step 4: Re-run**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: all new checks `ok`.

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/ledger.py tests/features.py
git commit -m "feat: ledger savings settlement and month rows"
```

---

### Task 3: Baseline series on OptimizationResult

**Files:**
- Modify: `custom_components/heatpump_optimizer/optimizer.py` (`OptimizationResult` ~762, `_build_result` ~1563, space `_build_result` call ~3059, DHW `_build_result` call ~5134, `get_current_action` ~5864)
- Test: `tests/features.py` (same section)

**Interfaces:**
- Consumes: existing `baseline_power` / `baseline_dhw` arrays already computed on both solve paths
- Produces: `OptimizationResult.baseline_power_schedule: list[float]` (space + DHW electrical kW per step); `get_current_action(...)["baseline_kw"]` for the current step

- [ ] **Step 1: Write the failing checks**

`_bl_opt` (already a `HeatPumpOptimizer` in this file) is the action host. Append:

```python
import inspect as _sav_inspect
import pickle as _sav_pickle
from pathlib import Path as _SavPath
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer as _SavOpt,
    OptimizationResult as _SavOR,
)

_ts_sav = [_SavDT(2026, 2, 10, 12, 0) + timedelta(minutes=15 * i) for i in range(4)]
_res_sav = _SavOR(
    power_schedule=[1.0] * 4,
    room_temp_trajectory=[21.0] * 5,
    slab_temp_trajectory=[22.0] * 5,
    timestamps=_ts_sav,
    prices=[1.0] * 4,
    predicted_cost=1.0,
    baseline_cost=2.0,
    predicted_savings=1.0,
    savings_percentage=50.0,
    optimal_setpoints=[21.0] * 4,
    status="optimal",
    baseline_power_schedule=[3.5, 4.0, 0.0, 1.25],
)
R.check(
    "baseline_power_schedule pickles as a plain float list",
    _sav_pickle.dumps(_res_sav.baseline_power_schedule) and True,
)
_act_sav = _bl_opt.get_current_action(_res_sav, _ts_sav[1])
R.check(
    "get_current_action copies the current step's baseline kW",
    abs(_act_sav["baseline_kw"] - 4.0) < 1e-12,
    repr(_act_sav.get("baseline_kw")),
)
_act_zero = _bl_opt.get_current_action(_res_sav, _ts_sav[2])
R.check(
    "a 0.0 baseline step is copied, not treated as missing",
    "baseline_kw" in _act_zero and _act_zero["baseline_kw"] == 0.0,
    repr(_act_zero.get("baseline_kw")),
)
_src_br = _sav_inspect.getsource(_SavOpt._build_result)
R.check(
    "_build_result writes baseline_power_schedule",
    "baseline_power_schedule=" in _src_br,
)
_src_opt = _SavPath("custom_components/heatpump_optimizer/optimizer.py").read_text()
R.check(
    "both solve paths pass the baseline array into _build_result",
    "baseline_power=baseline_power," in _src_opt
    and "baseline_power=baseline_power + baseline_dhw," in _src_opt,
)
```

- [ ] **Step 2: Run and confirm fail**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: `TypeError: unexpected keyword argument 'baseline_power_schedule'` (or `baseline_kw` missing).

- [ ] **Step 3: Implement**

On `OptimizationResult` (after `dhw_power_schedule` is fine):

```python
    # Thermostat-baseline electrical kW per step (space + DHW). Settlement
    # reads the current step; must be a pickle-safe list for the process route.
    baseline_power_schedule: list[float] = field(default_factory=list)
```

`_build_result` — add kw-only `baseline_power: np.ndarray | None = None` and pass:

```python
            baseline_power_schedule=(
                [float(v) for v in np.asarray(baseline_power, dtype=float)]
                if baseline_power is not None
                else []
            ),
```

Space-only `_build_result(...)` call (~3059): add `baseline_power=baseline_power,`.

DHW `_build_result(...)` call (~5134): add `baseline_power=baseline_power + baseline_dhw,`.

In `get_current_action`, next to the DHW block that uses index `i`:

```python
        if result.baseline_power_schedule and i < len(result.baseline_power_schedule):
            action["baseline_kw"] = float(result.baseline_power_schedule[i])
```

A list of `[0.0, ...]` is truthy; a missing/empty list omits the key. A single-step `[0.0]` is truthy, so 0.0 still copies.

- [ ] **Step 4: Re-run**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: all new checks `ok`.

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/optimizer.py tests/features.py
git commit -m "feat: carry thermostat baseline kW on the solve result"
```

---

### Task 4: Coordinator pending, settle, publish

**Files:**
- Modify: `custom_components/heatpump_optimizer/coordinator.py`
  - `_pending_prediction` dict ~9592
  - `_accumulate_energy` ~9766 (book **before** the `energy <= 0` return)
  - `_build_data_dict` ~7194 (always set `savings_months`, including when `result` is None)
- Test: `tests/features.py` (same section)

**Interfaces:**
- Consumes: `self._current_action.get("baseline_kw")`, `MonthlyLedger.add_savings_settlement`, `MonthlyLedger.savings_months`
- Produces: `pending["baseline_kw"]`; ledger lines on settle; `data["savings_months"]`
- Does **not** produce: a new coordinator method or attr; `data["baseline_power_schedule"]`

Do not add `self._baseline_power_schedule`. Read the current step from the action. That keeps `coordinator_attrs` / `coordinator_methods` flat.

- [ ] **Step 1: Write the failing checks**

```python
_sv = _t2_coord()
_sv_pending = {
    "price": 2.5,
    "spot_price": 2.0,
    "grid_fee": 0.5,
    "space_power": 1.0,
    "dhw_power": 1.0,
    "when": NOW,
    "baseline_kw": 4.0,
}
_sv_sample = AccuracySample(when=NOW, actual_power_kw=2.0)
_sv._accumulate_energy(_sv_sample, 0.5, _sv_pending)
_sv_m = NOW.strftime("%Y-%m")
_sv_b = _sv._ledger.line(_sv_m, "savings_baseline")
_sv_a = _sv._ledger.line(_sv_m, "savings_actual")
R.check(
    "with a pending baseline both savings lines move",
    abs(_sv_b["kwh"] - 2.0) < 1e-12
    and abs(_sv_b["sek"] - 4.0) < 1e-12
    and abs(_sv_a["kwh"] - 1.0) < 1e-12
    and abs(_sv_a["sek"] - 2.0) < 1e-12,
    f"base {_sv_b} actual {_sv_a}",
)
_sv0 = _t2_coord()
_sv0._accumulate_energy(_sv_sample, 0.5, {**_sv_pending, "baseline_kw": None})
# also the omitted-key case
_sv_omit = dict(_sv_pending)
del _sv_omit["baseline_kw"]
_sv1 = _t2_coord()
_sv1._accumulate_energy(_sv_sample, 0.5, _sv_omit)
R.check(
    "without a pending baseline neither savings line is written",
    _sv0._ledger.line(_sv_m, "savings_baseline")["kwh"] == 0.0
    and "savings_baseline" not in _sv0._ledger.months.get(_sv_m, {}).get("lines", {})
    and "savings_baseline" not in _sv1._ledger.months.get(_sv_m, {}).get("lines", {}),
)
_sv_idle = _t2_coord()
_sv_idle._accumulate_energy(
    AccuracySample(when=NOW, actual_power_kw=0.0),
    0.5,
    {**_sv_pending, "space_power": 0.0, "dhw_power": 0.0},
)
R.check(
    "zero metered energy still books savings when a baseline exists",
    abs(_sv_idle._ledger.line(_sv_m, "savings_baseline")["kwh"] - 2.0) < 1e-12
    and abs(_sv_idle._ledger.line(_sv_m, "savings_actual")["kwh"] - 0.0) < 1e-12,
)
_sv_imm = _t2_coord()
_sv_imm._immersion_active = True
_sv_imm._accumulate_energy(
    AccuracySample(when=NOW, actual_power_kw=6.9),
    0.5,
    {**_sv_pending, "space_power": 1.0, "dhw_power": 1.0},
)
# 6.9 kW × 0.5 h = 3.45 kWh actual (spot+immersion), same as contract comparison
R.check(
    "savings_actual is spot+immersion metered kWh, not the carved spot line",
    abs(_sv_imm._ledger.line(_sv_m, "savings_actual")["kwh"] - 3.45) < 1e-9,
    repr(_sv_imm._ledger.line(_sv_m, "savings_actual")),
)
import homeassistant.util.dt as _dt_sav
_real_now_sav = _dt_sav.now
try:
    _dt_sav.now = lambda: NOW
    _pub = _sv._build_data_dict()
finally:
    _dt_sav.now = _real_now_sav
R.check(
    "coordinator publishes savings_months and never the baseline series",
    isinstance(_pub.get("savings_months"), list)
    and len(_pub["savings_months"]) >= 1
    and "baseline_power_schedule" not in _pub
    and "baseline_kw" not in _pub,
    repr({k: _pub.get(k) for k in ("savings_months", "baseline_power_schedule")}),
)
_sv._current_action = {"power": 1.0, "dhw_power": 0.5, "baseline_kw": 3.25}
# Drive the pending builder by reading the assignment target after a call
# is not possible without the interval loop; pin the source instead:
_pend_src = Path(
    "custom_components/heatpump_optimizer/coordinator.py"
).read_text()
R.check(
    "interval-start pending copies baseline_kw from the current action",
    '"baseline_kw": self._current_action.get("baseline_kw")' in _pend_src,
)
```

Actual kWh for 2.0 kW × 0.5 h = 1.0 kWh. Baseline 4.0 kW × 0.5 h = 2.0 kWh × 2.0 spot = 4.0 SEK.

- [ ] **Step 2: Run and confirm fail**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: first settlement check fails (lines still 0).

- [ ] **Step 3: Implement**

In the `_pending_prediction = { ... }` literal (~9592), add:

```python
            "baseline_kw": self._current_action.get("baseline_kw"),
```

In `_accumulate_energy`, after `energy = max(0.0, actual * elapsed_hours)` and `_fold_score_sample(...)`, **before** `if energy <= 0:`:

```python
        self._ledger.add_savings_settlement(
            when,
            baseline_kw=pending.get("baseline_kw"),
            actual_kwh=energy,
            spot=spot,
            dt=elapsed_hours,
        )
```

In `_build_data_dict`, on the initial `data` dict (or just after it, **outside** `if result:`):

```python
        data["savings_months"] = self._ledger.savings_months(dt_util.now())
```

Do not add the list onto plan views or `ContractComparisonSensor` payloads.

- [ ] **Step 4: Re-run**

Run: `PYTHONPATH=tests/hastub python3 tests/features.py`

Expected: all new checks `ok`.

- [ ] **Step 5: Mutation — delete the book, confirm the “lines move” check fails, restore**

```bash
cp custom_components/heatpump_optimizer/coordinator.py /tmp/hpo-coord-savings.bak
```

Comment out or delete the `add_savings_settlement` call. Re-run `PYTHONPATH=tests/hastub python3 tests/features.py`. Expected: `with a pending baseline both savings lines move` **FAIL**. Then:

```bash
cp /tmp/hpo-coord-savings.bak custom_components/heatpump_optimizer/coordinator.py
test "$(md5 -q custom_components/heatpump_optimizer/coordinator.py)" = "$(md5 -q /tmp/hpo-coord-savings.bak)"
PYTHONPATH=tests/hastub python3 tests/features.py
```

Expected: md5 match; features green again.

- [ ] **Step 6: Commit**

```bash
git add custom_components/heatpump_optimizer/coordinator.py tests/features.py
git commit -m "feat: settle and publish monthly savings rows"
```

---

### Task 5: MonthlySavingsSensor

**Files:**
- Modify: `custom_components/heatpump_optimizer/sensor.py` (`async_setup_entry` ~166; new class next to `PredictedSavingsSensor` ~427)
- Modify: `custom_components/heatpump_optimizer/strings.json`, `translations/en.json`, `translations/sv.json` (insert after `monthly_peak_power`)
- Modify: `custom_components/heatpump_optimizer/icons.json` (same key)
- Test: `tests/entities.py`

**Interfaces:**
- Consumes: `coordinator.data["savings_months"]`
- Produces: entity id `sensor.heat_pump_optimizer_monthly_savings`; state = open-month estimated `savings_sek` or `None`; attrs `{savings_months}` and `waiting_for: "settled_savings_month"` only while the list is empty

- [ ] **Step 1: Write the failing entity checks**

In `tests/entities.py`:

1. Add to `DATA` (empty list so the empty branch is real):

```python
    "savings_months": [],
```

2. Add to `_ATTR_RICH` a populated list so the holes table sees the ready branch:

```python
    "savings_months": [
        {
            "month": "2026-01",
            "baseline_sek": 1200.0,
            "actual_sek": 900.0,
            "savings_sek": 300.0,
            "savings_pct": 25.0,
            "estimated": False,
        },
        {
            "month": "2026-02",
            "baseline_sek": 800.0,
            "actual_sek": 700.0,
            "savings_sek": 100.0,
            "savings_pct": 12.5,
            "estimated": True,
        },
    ],
```

3. Pin published keys in `_PUBLISHED_ATTRS` (alphabetical, after `MeasuredPowerSensor` / before `OptimizationModeSensor` as the file’s order requires):

```python
    "MonthlySavingsSensor": frozenset({"savings_months", "waiting_for"}),
```

4. Add object-id pin next to Predicted Savings (~5065):

```python
    ("Monthly Savings", "sensor.heat_pump_optimizer_monthly_savings"),
```

5. Add `_monthly_savings` to the suffix-derivation tuple (~5088).

6. Add a waiting/ready pair in the “Waiting for evidence” section (~1788), **or** a dedicated section if that loop’s `_key`/`_missing` shape does not fit. Dedicated is clearer:

```python
_empty_sav = sensor.MonthlySavingsSensor(
    FakeCoordinator({**DATA, "savings_months": []}), ENTRY
)
R.check(
    "MonthlySavingsSensor is unavailable before any booked month",
    not _empty_sav.available,
)
R.check(
    "MonthlySavingsSensor names settled_savings_month while empty",
    _empty_sav.extra_state_attributes.get("waiting_for") == "settled_savings_month"
    and _empty_sav.native_value is None
    and _empty_sav.extra_state_attributes.get("savings_months") == [],
    repr(_empty_sav.extra_state_attributes),
)
_ready_sav = sensor.MonthlySavingsSensor(
    FakeCoordinator(_ATTR_RICH), ENTRY
)
R.check(
    "MonthlySavingsSensor state is the open month's estimated savings_sek",
    _ready_sav.available
    and _ready_sav.native_value == 100.0
    and _ready_sav.extra_state_attributes.get("waiting_for") is None
    and _ready_sav.extra_state_attributes.get("savings_months")
    == _ATTR_RICH["savings_months"],
    repr(_ready_sav.native_value),
)
```

Place the dedicated checks **after** `_ATTR_RICH` is defined (~4489), not at line 1788.

If `MonthlySavingsSensor` does not exist yet, Step 2 fails on `AttributeError` — that is the red bar.

- [ ] **Step 2: Run and confirm fail**

Run: `PYTHONPATH=tests/hastub python3 tests/entities.py`

Expected: `AttributeError: module 'heatpump_optimizer.sensor' has no attribute 'MonthlySavingsSensor'` and/or holes mismatch.

- [ ] **Step 3: Implement the sensor**

Register in `async_setup_entry` immediately after `PredictedSavingsSensor`:

```python
        MonthlySavingsSensor(coordinator, entry),
```

Class (MEASUREMENT, not MONETARY+TOTAL — same trap as `PredictedSavingsSensor`):

```python
class MonthlySavingsSensor(_WaitsForEvidenceMixin, HeatPumpOptimizerSensorBase):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "monthly_savings", "monthly_savings")
        self._attr_native_unit_of_measurement = coordinator.currency

    def _rows(self) -> list:
        rows = (self.coordinator.data or {}).get("savings_months")
        return rows if isinstance(rows, list) else []

    @property
    def _waiting_for(self) -> str | None:
        return None if self._rows() else "settled_savings_month"

    @property
    def native_value(self) -> float | None:
        for row in self._rows():
            if isinstance(row, dict) and row.get("estimated"):
                val = row.get("savings_sek")
                return round(val, 2) if isinstance(val, (int, float)) else None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {"savings_months": self._rows()}
        waiting = self._waiting_for
        if waiting is not None:
            attrs["waiting_for"] = waiting
        return attrs
```

Translations — same three files, after `monthly_peak_power`:

```json
      "monthly_savings": {
        "name": "Monthly Savings"
      },
```

`translations/sv.json`:

```json
      "monthly_savings": {
        "name": "Månatligt sparande"
      },
```

`icons.json`:

```json
      "monthly_savings": {
        "default": "mdi:calendar-month"
      },
```

- [ ] **Step 4: Re-run**

Run: `PYTHONPATH=tests/hastub python3 tests/entities.py`

Expected: `ALL <n> ENTITY CHECKS PASSED`. If holes fail, the printed missing/extra keys are the edit.

- [ ] **Step 5: Commit**

```bash
git add custom_components/heatpump_optimizer/sensor.py \
  custom_components/heatpump_optimizer/strings.json \
  custom_components/heatpump_optimizer/translations/en.json \
  custom_components/heatpump_optimizer/translations/sv.json \
  custom_components/heatpump_optimizer/icons.json \
  tests/entities.py
git commit -m "feat: MonthlySavingsSensor for the savings table"
```

---

### Task 6: Card tab and table

**Files:**
- Modify: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
  - `STRINGS.en` / `STRINGS.sv` (~43 / ~448)
  - `ExpandedDialog.activePage` ~5283
  - `ExpandedDialog.html` tabs ~5322
  - host render ~9021
  - `cardStyleBlock()` for `.savings-table`
- Test: `tests/card.mjs` (Task 7 writes the checks; this task only needs the existing tab check to keep passing)

**Interfaces:**
- Consumes: `plan.statEntity("_monthly_savings")`, `plan.currency()`
- Produces: `activePage()` is `"plan" | "setup" | "savings"`; default page unchanged; legend plan-only

- [ ] **Step 1: Extend i18n**

English, under the header keys:

```javascript
    "header.tab_savings": "Savings",
    "savings.col_month": "Month",
    "savings.col_baseline": "Baseline",
    "savings.col_actual": "Actual",
    "savings.col_savings": "Savings",
    "savings.col_pct": "%",
    "savings.estimated": "estimated",
    "savings.empty": "No settled savings months yet.",
```

Swedish:

```javascript
    "header.tab_savings": "Sparande",
    "savings.col_month": "Månad",
    "savings.col_baseline": "Referens",
    "savings.col_actual": "Faktisk",
    "savings.col_savings": "Sparande",
    "savings.col_pct": "%",
    "savings.estimated": "uppskattat",
    "savings.empty": "Inga avräknade sparandemånader ännu.",
```

- [ ] **Step 2: Tabs and `activePage`**

Replace `activePage`:

```javascript
  activePage() {
    if (this.page === "setup") return "setup";
    if (this.page === "savings") return "savings";
    return "plan";
  }
```

In `html()`, add the third tab after setup:

```javascript
            ${tab("plan", esc(L("header.tab_plan")))}
            ${tab("setup", esc(L("header.tab_setup")))}
            ${tab("savings", esc(L("header.tab_savings")))}
```

Leave `pickDefaultPage` as-is (plan if `anyData`, else setup).

- [ ] **Step 3: Savings body**

Add a method on the card class (near `_setupPageHtml`):

```javascript
  _savingsPageHtml() {
    const st = this.plan.statEntity("_monthly_savings");
    const rows = st && st.attributes && Array.isArray(st.attributes.savings_months)
      ? st.attributes.savings_months
      : [];
    if (!rows.length) {
      return `<p class="savings-empty">${esc(L("savings.empty"))}</p>`;
    }
    const cur = this.plan.currency();
    const money = (n) =>
      typeof n === "number" && Number.isFinite(n)
        ? `${n.toFixed(2)} ${esc(cur)}`
        : "—";
    const pct = (n) =>
      typeof n === "number" && Number.isFinite(n) ? `${n.toFixed(0)}%` : "—";
    const tr = (row) => {
      const est = row.estimated
        ? ` <span class="savings-est">${esc(L("savings.estimated"))}</span>`
        : "";
      return `<tr class="${row.estimated ? "estimated" : ""}">
        <td>${esc(String(row.month || ""))}${est}</td>
        <td>${money(row.baseline_sek)}</td>
        <td>${money(row.actual_sek)}</td>
        <td>${money(row.savings_sek)}</td>
        <td>${pct(row.savings_pct)}</td>
      </tr>`;
    };
    return `<table class="savings-table">
      <thead><tr>
        <th>${esc(L("savings.col_month"))}</th>
        <th>${esc(L("savings.col_baseline"))}</th>
        <th>${esc(L("savings.col_actual"))}</th>
        <th>${esc(L("savings.col_savings"))}</th>
        <th>${esc(L("savings.col_pct"))}</th>
      </tr></thead>
      <tbody>${rows.map(tr).join("")}</tbody>
    </table>`;
  }
```

In the expanded-dialog body switch (~9025):

```javascript
      const body =
        page === "setup"
          ? this._setupPageHtml()
          : page === "savings"
            ? this._savingsPageHtml()
            : anyData
              ? `${this._chartBlock(built, true)}${this.whatIf.html()}`
              : this._noPlanHtml();
      dialog = this.dialog.html({
        title: this._title(),
        legend: page === "plan" && anyData ? this.legend.html(this._series) : "",
        body,
      });
```

- [ ] **Step 4: CSS**

Inside `cardStyleBlock()`, next to `.dlg-body` rules:

```css
      .savings-table { width: 100%; border-collapse: collapse; }
      .savings-table th, .savings-table td {
        text-align: left; padding: 0.35em 0.5em;
      }
      .savings-table th { font-weight: 600; }
      .savings-table tr.estimated td { font-style: italic; }
      .savings-est { font-weight: 400; opacity: 0.75; }
      .savings-empty { margin: 1em 0; }
```

- [ ] **Step 5: Existing card script still passes**

Run: `node tests/card.mjs`

Expected: existing `the dialog offers plan and setup tabs` still `ok` (it does not forbid a third tab). Fix any failure before committing.

- [ ] **Step 6: Commit**

```bash
git add custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
git commit -m "feat: Savings tab on the expanded card"
```

---

### Task 7: card.mjs coverage

**Files:**
- Test: `tests/card.mjs` (after the existing dialog-tab check ~1852)
- Modify: only if a test forces a card fix

**Interfaces:**
- Consumes: Task 6 markup and `_monthly_savings` discovery via `statEntity`

- [ ] **Step 1: Write the checks**

After the existing `the dialog offers plan and setup tabs` check (~1852):

```javascript
  check("the dialog offers a savings tab",
    /dlg-tab[^>]*data-page="savings"/.test(planPage));

  su.dialog.page = "savings";
  su._render();
  const savingsEmpty = collect(su.shadowRoot).join("\n");
  check("savings tab empty copy when the attribute is missing",
    /No settled savings months yet/.test(savingsEmpty));
  check("savings tab does not invent zero rows",
    !/0\.00/.test(savingsEmpty) && !/<tbody>\s*<tr/.test(savingsEmpty));
  check("legend stays off the savings page",
    !/Electricity price/.test(savingsEmpty));

  const savStates = mkStates(DEFAULT_SPACE, DEFAULT_DHW, true);
  savStates["sensor.heat_pump_optimizer_monthly_savings"] = {
    state: "100.00",
    attributes: {
      unit_of_measurement: "SEK",
      savings_months: [
        {
          month: "2026-02",
          baseline_sek: 800,
          actual_sek: 700,
          savings_sek: 100,
          savings_pct: 12,
          estimated: true,
        },
      ],
    },
  };
  const sav = build(savStates);
  sav._onCardClick({});
  sav.dialog.page = "savings";
  sav._render();
  const savingsFilled = collect(sav.shadowRoot).join("\n");
  check("savings tab draws the estimated current-month row",
    /2026-02/.test(savingsFilled) &&
    /800\.00/.test(savingsFilled) &&
    /700\.00/.test(savingsFilled) &&
    /100\.00/.test(savingsFilled) &&
    /12%/.test(savingsFilled) &&
    /estimated/.test(savingsFilled));
```

- [ ] **Step 2: Run and confirm fail** (if Task 6 is incomplete) **or pass** (if Task 6 is done)

Run: `node tests/card.mjs`

Expected after Task 6: all new checks `ok`, `fails === 0`.

- [ ] **Step 3: Commit**

```bash
git add tests/card.mjs custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
git commit -m "test: card Savings tab empty and estimated row"
```

---

### Task 8: Structure ratchet and wrap-up

**Files:**
- Modify: `tests/structure_budgets.json` only if `python3 tests/structure.py` reports an **improvement** you must record
- Test: `tests/structure.py`, `tests/features.py`, `tests/entities.py`, `tests/card.mjs`

**Interfaces:**
- Consumes: the code from Tasks 1–7
- Produces: a merge-ready tree that does not raise any budget

- [ ] **Step 1: Re-measure**

Run: `python3 tests/structure.py`

If `coordinator_loc`, `max_class_loc`, `coordinator_attrs`, `coordinator_methods`, or `max_method_loc` **worsens** versus the merge-base file: do not `--record`. Move more lines into `ledger.py` (or inline less) and re-measure. If you cannot pay, stop and ask. Never raise a ceiling.

If metrics **improve**, run `python3 tests/structure.py --record` and include that file in the commit.

- [ ] **Step 2: Full targeted select**

```bash
PYTHONPATH=tests/hastub python3 tests/features.py
PYTHONPATH=tests/hastub python3 tests/entities.py
node tests/card.mjs
python3 tests/structure.py
```

Expected: all four green. Do not run `tests/stress.py` or `MODE: FULL` unless a later review asks; if you do, take `/tmp/hpo-gate.lock` first.

- [ ] **Step 3: PR hygiene**

- Branch off the post-W3-G3 (and post-#408 / post-#457 as seated) `origin/main`.
- Three-dot diff vs that merge-base must not include plan-sensor payload keys or golden files.
- Commit message / PR body: `Closes #<new-issue>` on its own line.
- Do not list #453 on any stamp.

- [ ] **Step 4: Commit remaining budget/record files if any**

```bash
git add tests/structure_budgets.json
git commit -m "chore: record structure improvements after monthly savings"
```

Only if Step 1 recorded an improvement.

---

## Self-review (plan vs spec)

| Spec requirement | Task |
|---|---|
| Lines `savings_baseline` / `savings_actual`; savings derived | 2, 4 |
| `baseline_kw` at interval start from last solve thermostat baseline | 3, 4 |
| Skip both lines when no baseline; no stand-in zeros | 2, 4 |
| Actual = spot + immersion metered kWh; SEK × pending spot | 4 |
| Month only if `savings_baseline` booked; oldest first | 2 |
| Open month: calendar pro-rata; `%` unchanged; `estimated: true` | 1, 2 |
| `savings_pct` null when baseline ≤ 0.01 | 1, 2 |
| `data["savings_months"]`; not on `ContractComparisonSensor` | 4 |
| `MonthlySavingsSensor` / `_monthly_savings`; MEASUREMENT; waiting_for | 5 |
| Holes-list pin | 5 |
| Third tab; default unchanged; legend plan-only | 6 |
| Empty state; estimated row; en+sv keys | 6, 7 |
| Baseline series not on plan sensor / `data[]`; process-route lists | 3, 4 |
| `coordinator_loc` pay-not-raise; no golden re-record; `claims-for: 6.3.14` | 8 |
| Mutation + `cp`/md5 | 4 |
| Seat 3L-G7 / issue filing | Seat + Task 8 |

No TBD. Types match across tasks: `baseline_kw` is `float | None`; rows use the six keys above; sensor suffix is `_monthly_savings`.
