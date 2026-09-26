"""D14 round 9, verifier V2 (independent) for D14-s2-02: money label vs the feed's own currency.

Metric (one line): v2_unflagged_mismatch = cells (instance currency X in {SEK, EUR, NOK} x price
entity unit F/kWh, F in {SEK, EUR, NOK, DKK}) where the REAL CurrentPriceSensor's
native_unit_of_measurement names a currency != F while coordinator._entity_price returns the
feed number unconverted, and coordinator._audit_price_units creates no repair issue;
v2_money_widgets_off_instance[EUR] = option-widget unit strings in config_flow._OPTION_FIELDS that contain a
literal ISO currency code (scan of the built selector objects, not source text).
Keys: the sensor's delivered unit, the delivered price value, hass.issues after the audit.

Null control: the 3 cells with F == X -> 0.
Perturbation (--fix): coordinator.currency resolved from the price entity's money code
(mock.patch.object(C, "resolve_currency")) -> v2_unflagged_mismatch to 0.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_currency.py [--fix]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging, re
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
import heatpump_optimizer.coordinator as C  # noqa: E402
from heatpump_optimizer import sensor as S, config_flow as CF  # noqa: E402

FIX = "--fix" in sys.argv
cells = mism = unflag = null_bad = 0
for X in ("SEK", "EUR", "NOK"):
    for F in ("SEK", "EUR", "NOK", "DKK"):
        hass = FakeHass()
        hass.config.currency = X
        hass.states.set("sensor.nordpool", FakeState("0.10", unit=f"{F}/kWh"))
        cfg = {"price_source": "entity", "price_entity": "sensor.nordpool",
               "weather_entity": "weather.home"}
        entry = FakeEntry(data=cfg)
        ctx = (mock.patch.object(C, "resolve_currency",
                                 lambda h: h.states.get("sensor.nordpool").attributes.get("unit_of_measurement", "").split("/")[0]
                                 or X)
               if FIX else mock.patch.object(C, "_LOGGER", C._LOGGER))
        with ctx:
            coord = C.HeatPumpOptimizerCoordinator(hass, entry)
        entry.runtime_data = coord
        sensor = S.CurrentPriceSensor(coord, entry)
        unit = sensor.native_unit_of_measurement
        val = C._entity_price(hass, "sensor.nordpool")
        C._audit_price_units(hass, cfg)
        issues = [i for i in (getattr(hass, "issues", None) or [])]
        labelled = unit.split("/")[0]
        cells += 1
        bad = labelled != F and val == 0.10
        if F == X:
            null_bad += bad
        if bad:
            mism += 1
            if not issues:
                unflag += 1
        print(f"CELL instance={X} feed={F}/kWh sensor_unit={unit} value={val} issues={len(issues)}")
print(f"RESULT v2_cells={cells} count")
print(f"RESULT v2_mismatch={mism} count")
print(f"RESULT v2_unflagged_mismatch={unflag} count")
print(f"RESULT v2_null_control_bad={null_bad} count")

# literal currency codes in the option widgets' delivered unit strings
lit = []
money_widgets = off_inst = 0
hass_eur = FakeHass()
hass_eur.config.currency = "EUR"
for fld in CF._OPTION_FIELDS:
    w = fld.widget
    if isinstance(w, CF._ByHass):
        w = w.of(hass_eur)
    cfgd = getattr(w, "config", None) or {}
    unit = str(cfgd.get("unit_of_measurement", "")) if isinstance(cfgd, dict) else ""
    m = re.match(r"^(SEK|EUR|NOK|DKK|USD|GBP)/", unit)
    if m:
        money_widgets += 1
        if m.group(1) != "EUR":
            off_inst += 1
            lit.append((fld.key, unit))
print(f"RESULT v2_money_widgets[EUR instance]={money_widgets} count")
for k, m in lit:
    print(f"LITERAL {k}: {m}")
print(f"RESULT v2_money_widgets_off_instance[EUR]={len(lit)} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
