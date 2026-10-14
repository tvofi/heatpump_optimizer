"""Reviewer probes at the head: private Tibber attributes, unavailable-only home, legacy registry rows."""
import sys, json, tempfile, contextlib, io, importlib.util
from datetime import timedelta
from pathlib import Path
wt = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(wt / "tests"), str(wt / "tests" / "hastub")]
spec = importlib.util.spec_from_file_location("replay_t", wt / "tests" / "replay.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sys.path.insert(0, str(wt / "tools" / "replay"))
import export, synthesize

def run(rows, states_for, entry=None):
    series, data = synthesize._series, synthesize.ENTRY_DATA
    synthesize.ENTRY_DATA = {**{k: v for k, v in data.items() if k != "price_entity"}, "price_source": "tibber", **(entry or {})}
    def patched(series=series):
        out = series()
        for eid, rowsfn in states_for.items():
            out[eid] = rowsfn()
        return out
    synthesize._series = patched
    err = io.StringIO()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            db = synthesize.write_install(Path(tmp))
            rp = Path(tmp) / ".storage" / "core.entity_registry"
            reg = json.loads(rp.read_text())
            reg["data"]["entities"] += rows
            rp.write_text(json.dumps(reg))
            with contextlib.redirect_stderr(err):
                p = export.build_export(Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(), None, [], None)
            return p, err.getvalue()
    except SystemExit as e:
        return f"refused: {e}", err.getvalue()
    finally:
        synthesize._series, synthesize.ENTRY_DATA = series, data

A, B = "96a14971-525a-4420-aae9-e5aedaa129ff", "4c1e6f3b-0d2a-4b7e-9a51-2f8c3d4e5a6b"
def row(eid, uid, tk="electricity_price", plat="tibber", dis=None):
    return {"entity_id": eid, "platform": plat, "unique_id": uid, "translation_key": tk, "config_entry_id": "01J", "disabled_by": dis}
PRIV = {"unit_of_measurement": "SEK/kWh", "state_class": "measurement", "friendly_name": "Electricity price Storgatan 17",
        "app_nickname": "Storgatan 17", "grid_company": "Ellevio AB", "estimated_annual_consumption": 18234, "max_price": 1.2}
num = lambda attrs: lambda: [(synthesize.DAY + timedelta(hours=h), f"{0.8+h/100:.3f}", attrs) for h in range(-1, 24)]
unav = lambda: [(synthesize.DAY + timedelta(hours=-2), "unavailable", {"restored": True})]

# P1 private attributes on the picked sensor do not reach the payload
p, e = run([row("sensor.electricity_price_storgatan_17", A)], {"sensor.electricity_price_storgatan_17": num(PRIV)})
blob = json.dumps(p) if isinstance(p, dict) else p
hits = [s for s in ("Storgatan", "Ellevio", "18234", "app_nickname", "grid_company") if s in blob]
print("RESULT P1_private_attrs", "ok" if isinstance(p, dict) and not hits else "FAIL", "picked=", p.get("price_series_entity") if isinstance(p, dict) else p, "hits=", hits, "| stderr:", e.strip()[-120:])
# P2 a second home with only 'unavailable' recorded (ended subscription) -> the active home is picked
p, e = run([row("sensor.electricity_price_a", A), row("sensor.electricity_price_b", B)],
           {"sensor.electricity_price_a": num(PRIV), "sensor.electricity_price_b": unav})
print("RESULT P2_unavailable_home", "ok" if isinstance(p, dict) and p["price_series_entity"] == "sensor.electricity_price_a" else "FAIL", p if not isinstance(p, dict) else p["price_series_entity"])
# P3 2023-era registry: price sensor translation_key None; RT sensor unique id '<home>_rt_Average power'; data sensor '<home>_month_cost'
p, e = run([row("sensor.electricity_price_a", A, None), row("sensor.power_a", f"{A}_rt_Average power", None), row("sensor.cost_a", f"{A}_month_cost", None)],
           {"sensor.electricity_price_a": num(PRIV), "sensor.power_a": num({}), "sensor.cost_a": num({})})
print("RESULT P3_2023_registry", "ok" if isinstance(p, dict) and p["price_series_entity"] == "sensor.electricity_price_a" else "FAIL", p if not isinstance(p, dict) else p["price_series_entity"])
# P4 pre-migration price sensor keyed on its consumption EAN (bare digits) is still the price sensor
p, e = run([row("sensor.electricity_price_a", "735999100000000001", None)], {"sensor.electricity_price_a": num(PRIV)})
print("RESULT P4_ean_unique_id", "ok" if isinstance(p, dict) and p["price_series_entity"] == "sensor.electricity_price_a" else "FAIL", p if not isinstance(p, dict) else p["price_series_entity"])
# P5 Data-API binary_sensor / sensor with device-id unique ids are not picked; another integration's bare-uuid price sensor (nordpool) is not picked
p, e = run([row("sensor.nordpool_kwh_se3", "nordpool_kwh_se3_sek_3_10_025", None, "nordpool"), row("sensor.grid_price", "0b6a7d2e-3f41-4c5a-9e8d-7c6b5a4f3e2d", None, "template"),
            row("sensor.pulse_ev_range", "dev123_range_remaining", "range_remaining")],
           {"sensor.nordpool_kwh_se3": num({}), "sensor.grid_price": num({}), "sensor.pulse_ev_range": num({})})
print("RESULT P5_foreign_bare_ids_refused", "ok" if isinstance(p, str) and "found 0 usable of 0" in p else "FAIL", p if isinstance(p, str) else p["price_series_entity"])
