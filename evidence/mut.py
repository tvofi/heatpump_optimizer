import os, subprocess, sys, pathlib
W = pathlib.Path("/tmp/hpo-rev-3930/wt")
CC = "custom_components/heatpump_optimizer/"
MUTS = {
 "M1_humidity_defaults": (CC+"coordinator.py", """        reading = entry_reader(
            self.hass, getattr(self, "_ctx", self)._config, now=dt_util.utcnow
        ).read(CONF_INDOOR_HUMIDITY_ENTITY, entity_id=entity_id)""", """        reading = InputReader(self.hass, {}).read(CONF_INDOOR_HUMIDITY_ENTITY, entity_id=entity_id)"""),
 "M2_pv_gate_off": (CC+"inputs.py", """        if not self.read(key, entity_id=entity_id).ok:
            return None
        return state_power_kw""", """        return state_power_kw"""),
 "M3_ended_reply_ok": (CC+"coordinator.py", """    if covering_forecast_row(rows, now) is None:
        return f"Forecast for {entity_id} ends before now"
""", ""),
 "M4_row0": (CC+"coordinator.py", """    row = covering_forecast_row(forecast, now)
    if row is None:
        return 0.0, 0.0""", """    row = forecast[0] if forecast else None
    if row is None:
        return 0.0, 0.0"""),
 "M5_quiet_off": (CC+"inputs.py", """            reading.quiet = reading.key in PUSHED_FLAG_KEYS and not source_polls(""", """            reading.quiet = False and not source_polls("""),
 "M6_live_off": (CC+"coordinator.py", """        outdoor = hold_current_hour(
            outdoor, step_starts, health.live(CONF_OUTDOOR_TEMP_ENTITY) if health else None
        )""", ""),
 "M7_bool_ok": (CC+"coordinator.py", """    elif type(data) in (int, float):  # a JSON bool is a flag (D1-s3-02)""", """    elif isinstance(data, (int, float)):"""),
 "M8_ha_clock": (CC+"inputs.py", """        return datetime.now(UTC)
""", """        from homeassistant.util import dt as dt_util
        return dt_util.utcnow()
"""),
 "M9_hour_bound_all": (CC+"plan_step.py", """starts[i].timestamp() < end else v""", """True else v"""),
}
CMD = ["python3", "tools/audit/seat/features_block.py", "# --- R11-SEAM-inputs-freshness: age and expiry of live inputs ---"]
env = dict(os.environ, PYTHONPATH="tests/hastub")
for name, (path, old, new) in MUTS.items():
    p = W / path
    src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(CMD, cwd=W, env=env, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip()[:160] for l in out.splitlines() if l.lstrip().startswith(("FAIL", "ERROR")) or "Error" in l]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
        for f in fails[:4]:
            print("   ", f)
    finally:
        p.write_text(src)
subprocess.run(["git", "status", "--short"], cwd=W)
