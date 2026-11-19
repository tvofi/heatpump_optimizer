#!/usr/bin/env python3
"""D6-s1 round 11: executed behavioural checks for the prose claims the ledger cannot key mechanically.

Metric: per claim, whether the production behaviour the sentence states holds (1) or not (0); the
headline RESULT false_claims counts sentences whose stated behaviour the driven code contradicts.
Key: the value the production seam delivers (a menu's page tuple, an override's clamped expiry, a
ring's kept length, a guard's suppressing flag, an arbiter's dropped write record, a learner's
heat-loss scale, an option row's default), never the document's own text.

RUN (export root, no cd):
    PYTHONUTF8=1 PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s1/claims.py [--skip-rolling]
        [--perturb-grace SECONDS] [--perturb-legionella DAYS] [--rolling-plant-error X]
Writes dev/audit/rounds/round11/D6/s1/behaviour_rows.tsv (unit id -> command, result, verdict),
which ledger.py folds into the ledger.
Expected (baseline export 92d38ecb, box B1): false_claims=5 exact (echo-grace sentence, legionella
  interval in README + configuration.md x2 rows are counted by ledger.py, here README's sentence;
  see RESULT lines); rolling numbers +-0.02 (solver/BLAS-dependent).
Perturbations:
  --perturb-grace 60   one-line edit of pump_arbiter.hold in memory (`if observed is None:` ->
                       `if observed is None or utc_elapsed_seconds(now, at) < 60:`):
                       echo_grace_contradictions goes 6 -> 0 (down).
  --perturb-grace 20   the same edit at pump_arbiter.ECHO_GRACE_S: 6 -> 3.
  --perturb-legionella 7  swaps const/ThermalParameters default to 7: legionella_default_days 10 -> 7,
                       legionella contradictions 1 -> 0 (down).
  --rolling-plant-error 1.25  the "correct model" arm on a 25 % wrong model: drift_from_1 goes up.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, asyncio, inspect, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(".").resolve()
sys.path[:0] = [str(ROOT / "custom_components"), str(ROOT / "tests"), str(ROOT / "tools/audit")]
HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--skip-rolling", action="store_true")
ap.add_argument("--perturb-grace", type=float)
ap.add_argument("--perturb-legionella", type=float)
ap.add_argument("--rolling-plant-error", type=float, default=1.0)
ap.add_argument("--out", default=str(HERE / "behaviour_rows.tsv"))
a = ap.parse_args()
t_cpu0, t_thr0 = time.process_time(), time.thread_time()

import text_ledger  # noqa: E402
FILES = ["README.md", "docs/configuration.md", "docs/dashboard-card.md", "docs/how-it-works.md", "docs/index.html"]
UNITS = text_ledger.enumerate_units(".", FILES, "D6")


def uids(path, needle):
    hits = [u[0] for u in UNITS if u[0].startswith(path + "#") and needle in " ".join(u[3].split())]
    assert hits, (path, needle)
    return hits


ROWS = []
FALSE = []
CMD = "PYTHONUTF8=1 PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s1/claims.py"


def row(name, ok, result, targets):
    print(f"CLAIM {name}: {'true' if ok else 'FALSE'} :: {result}")
    if not ok:
        FALSE.append(name)
    for path, needle in targets:
        for u in uids(path, needle):
            ROWS.append((u, CMD, f"{name}: {result}", "true" if ok else "false"))


from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import config_flow as cf, const, manual_plan, snapshots, power_guard, pump_arbiter  # noqa: E402
from heatpump_optimizer import thermal_model  # noqa: E402

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

# 1. options pages (C1: "23 options pages")
O = cf.HeatPumpOptimizerOptionsFlow
pages = list(O._TOP_MENU) + list(O._ADVANCED_MENU)
read_only = [p for p in pages if p == "setup_overview"]
ok = len(pages) == 24 and len(pages) - len(read_only) == 23
row("options_pages", ok, f"menus list {len(pages)} pages ({len(O._TOP_MENU)} top + {len(O._ADVANCED_MENU)} advanced), {len(read_only)} read-only",
    [("README.md", "menu of 24 pages")])
print(f"RESULT options_pages={len(pages)} count")

# 2. manual-plan window (C1: "up to 20 manual-plan hours")
far = manual_plan.build_override(dhw_slots=None, space_slots=None, expires_at=NOW + timedelta(hours=30), now=NOW)
clamp_h = (far.expires_at - NOW).total_seconds() / 3600.0
refused = False
try:
    manual_plan.build_override(dhw_slots=None,
                               space_slots=[{"start": (NOW + timedelta(hours=20, minutes=15)).isoformat(),
                                             "end": (NOW + timedelta(hours=21)).isoformat()}],
                               expires_at=NOW + timedelta(hours=19), now=NOW)
except manual_plan.ManualPlanError:
    refused = True
ok = abs(clamp_h - 20.0) < 1e-9 and refused
row("manual_plan_window", ok, f"expiry 30 h clamps to {clamp_h:g} h; a slot starting at +20.25 h refused={refused}",
    [("README.md", "pins exact run slots for up to 20 hours"), ("README.md", "Pin exact run slots for up to 20 hours"),
     ("docs/index.html", "of run slots you can pin yourself"), ("docs/configuration.md", "defaults to 20 hours")])
print(f"RESULT manual_plan_window_h={clamp_h:g} h")

# 3. weekly snapshot ring of 8 (C1: "8 weekly snapshots")
ring = snapshots.SnapshotRing()
taken = 0
t = NOW
for day in range(0, 7 * 12 + 1):
    t = NOW + timedelta(days=day)
    if ring.due(t):
        ring.take(t, {"x": {"v": day}}, {}, True)
        taken += 1
gaps = {(datetime.fromisoformat(b["taken_at"]) - datetime.fromisoformat(a_["taken_at"])).days
        for a_, b in zip(ring.snapshots, ring.snapshots[1:])}
ok = len(ring.snapshots) == 8 and gaps == {7}
row("snapshot_ring", ok, f"{taken} taken over 12 weeks of daily ticks, {len(ring.snapshots)} kept, gaps {sorted(gaps)} days",
    [("README.md", "Every learner is snapshotted weekly"), ("docs/how-it-works.md", "A ring of weekly snapshots")])
print(f"RESULT snapshots_kept={len(ring.snapshots)} count")

# 4. peak guard hysteresis: "two agreeing samples to engage and two to clear"
g = power_guard.GuardState()
seq = []
for i, proj in enumerate([5.0, 5.0, 1.0, 1.0]):
    g.update(NOW + timedelta(seconds=20 * i), "w", proj, 4.0, 0.0, floor_hold=False)
    seq.append(g.suppressing)
ok = seq == [False, True, True, False]
row("peak_guard_two_samples", ok, f"suppressing after over,over,clear,clear = {seq}",
    [("README.md", "The peak guard needs two agreeing samples"), ("docs/how-it-works.md", "Two agreeing readings engage it")])

# 5. legionella default: "on by default at 60 °C every 7 days"
if a.perturb_legionella is not None:
    const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS = a.perturb_legionella
    thermal_model.ThermalParameters.__dataclass_fields__["dhw_legionella_interval_days"].default = a.perturb_legionella
    thermal_model.ThermalParameters.__init__.__defaults__  # dataclass default lives in __init__
    import dataclasses
    _fields = {f.name: f for f in dataclasses.fields(thermal_model.ThermalParameters)}
    _defaults = list(thermal_model.ThermalParameters.__init__.__defaults__ or ())
    _names = [p for p in inspect.signature(thermal_model.ThermalParameters.__init__).parameters][1:]
    _off = len(_names) - len(_defaults)
    _i = _names.index("dhw_legionella_interval_days") - _off
    _defaults[_i] = a.perturb_legionella
    thermal_model.ThermalParameters.__init__.__defaults__ = tuple(_defaults)
p = thermal_model.ThermalParameters()
days, temp, enabled = float(p.dhw_legionella_interval_days), float(p.dhw_legionella_temp), bool(p.dhw_legionella_enabled)
ok = days == 7.0 and temp == 60.0 and enabled
row("legionella_default", ok, f"ThermalParameters() default: enabled={enabled}, {temp:g} °C every {days:g} days",
    [("README.md", "Anti-legionella is on by default at 60 °C every 7 days")])
print(f"RESULT legionella_default_days={days:g} days")
print(f"RESULT legionella_contradictions={0 if days == 7.0 else 1} count")

# 6. comfort_weight default 5 on the Savings vs comfort page
cw = [r for r in cf._OPTION_FIELDS if r.key == const.CONF_COMFORT_WEIGHT]
ok = bool(cw) and all(float(r.default) == 5.0 and r.step == "tuning" for r in cw)
row("comfort_weight_default", ok, f"option rows {[(r.step, r.default) for r in cw]}",
    [("README.md", "default 5) on the **Savings vs comfort** page")])

# 7. echo grace: "Readings in the first 60 seconds after a write are not counted"
if a.perturb_grace is not None:
    src = inspect.getsource(pump_arbiter.hold)
    edited = src.replace("        if observed is None:\n",
                         f"        if observed is None or utc_elapsed_seconds(now, at) < {a.perturb_grace!r}:\n", 1)
    assert edited != src, "hold() no longer has the line the perturbation edits"
    exec(compile(edited, pump_arbiter.__file__, "exec"), pump_arbiter.__dict__)


class _Coord:
    def __init__(self, hass, config):
        self.hass, self._config = hass, config

    def arbiter_inputs(self):
        return type("Inp", (), {"hass": self.hass, "config": self._config})()


from harness import FakeHass, FakeState  # noqa: E402

counted = {}
for dt_s in (5, 10, 19, 21, 30, 59, 61, 90):
    hass = FakeHass({"number.dhw": FakeState("50", unit="°C")})
    coord = _Coord(hass, {const.CONF_DHW_SETPOINT_ENTITY: "number.dhw"})
    held = pump_arbiter.state_for(coord)
    held.written["dhw_setpoint"] = (55.0, NOW)
    pump_arbiter.hold(coord, NOW + timedelta(seconds=dt_s))
    counted[dt_s] = "dhw_setpoint" not in held.written  # the record dropped = the reading counted as a miss
contra = [s for s, c in counted.items() if (s < 60) == c]
ok = not contra
row("echo_grace_60s", ok, f"reading counted (write record dropped) at +s: {counted}; contradicting the 60 s sentence at {contra}",
    [("docs/configuration.md", "Readings in the first 60 seconds after a write are not counted")])
print(f"RESULT echo_grace_contradictions={len(contra)} count")
print(f"RESULT echo_grace_const_s={pump_arbiter.ECHO_GRACE_S:g} s")

# 8. closed-loop learner (C1: "within ±12 %", "35 % more heat ... three simulated days")
if not a.skip_rolling:
    src = (ROOT / "tests/rolling.py").read_text().splitlines()
    end = next(i for i, l in enumerate(src) if l.startswith("R.section("))
    ns = {"__name__": "rolling_defs"}
    exec(compile("\n".join(src[:end]), "tests/rolling.py", "exec"), ns)
    import numpy as np
    correct = ns["run_rolling"](days=2, dhw=False, plant_error=a.rolling_plant_error, learn=True)
    drift = float(correct["history"]["heat_loss_scale"][-1])
    ok = abs(drift - 1.0) < 0.12
    row("learner_left_alone_12pct", ok, f"2-day closed loop, plant_error={a.rolling_plant_error}: scale {drift:.3f} (|{drift - 1:.3f}| vs 0.12)",
        [("README.md", "A model that is already correct is left alone")])
    print(f"RESULT drift_from_1={abs(drift - 1.0):.4f} ratio")
    bound_pump = {"heat_pump_max_power": 4.25}
    learned = ns["run_rolling"](days=3, dhw=False, plant_error=1.35, learn=True, config=bound_pump)
    plain = ns["run_rolling"](days=3, dhw=False, plant_error=1.35, config=bound_pump)
    sc = learned["history"]["heat_loss_scale"]
    spread = float(np.std(sc[-len(sc) // 4:]))
    steps = learned["total_steps"]
    bound = ns["floor_for"](learned["config"], steps)
    bl = float(np.sum(np.maximum(0.0, bound - learned["history"]["room"])) * ns["DT"])
    bp = float(np.sum(np.maximum(0.0, bound - plain["history"]["room"])) * ns["DT"])
    ok = sc[-1] > sc[0] + 0.05 and sc[-1] <= 1.35 + 0.15 and spread < 0.05 and bl < bp
    row("learner_converges_35pct", ok,
        f"3 days at 1.35: scale {sc[0]:.3f}->{sc[-1]:.3f}, last-quarter std {spread:.4f}, breach {bp:.2f}->{bl:.2f} K·h",
        [("README.md", "loses 35 % more heat than configured")])
    print(f"RESULT learned_scale_end={sc[-1]:.3f} ratio")

with open(a.out, "w") as fh:
    fh.write("# unit\tcommand\tresult\tverdict  (written by claims.py)\n")
    for r in ROWS:
        fh.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in r) + "\n")
print(f"RESULT claims_checked={len({r[0] for r in ROWS})} count")
print(f"RESULT false_claims={len(FALSE)} count  {FALSE}")
cpu, thr = time.process_time() - t_cpu0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "0"
print(f"RESULT swapins={sw}")
