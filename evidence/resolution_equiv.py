"""b29e4ee4's hand resolution: raw mapping reads (main 6b91e238) vs parsed fields (head), on the arbiter helpers."""
import sys, itertools
from datetime import datetime, timedelta, timezone
sys.path.insert(0, sys.argv[1] + "/custom_components")
from heatpump_optimizer import pump_arbiter as pa, quiet_windows as qw
from heatpump_optimizer.entry_config import EntryConfig, _spec, _entity
specs = [None, "", "  ", "06:00-08:00", "22:00-06:00", "mon 06:00-08:00", "garbage", "06:00-08:00,20:00-21:00"]
ents = [None, "", "switch.pump_night_mode", "binary_sensor.x", "sensor.y", "nodot"]
nows = [datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=15 * k) for k in range(0, 7 * 96, 7)]
mism = 0; n = 0
for e in ents:
    n += 1
    if qw.silent_control_usable(e) != qw.silent_control_usable(_entity(e, None)):
        mism += 1; print("ENT MISMATCH", e)
for s in specs:
    n += 1
    if pa._silent_rows(s) != pa._silent_rows(_spec(s, "")):
        mism += 1; print("ROWS MISMATCH", s)
for s, o in itertools.product([x for x in specs if pa._silent_rows(x)], specs):
    for now in nows:
        n += 1
        a = pa._inside_silent(s, o, now); b = pa._inside_silent(s, _spec(o, ""), now)
        if a != b:
            mism += 1; print("INSIDE MISMATCH", s, o, now, a, b)
# the config path end to end: from_mapping fields vs raw
for s, o, e in itertools.product(specs, specs, ents):
    cfg = EntryConfig.from_mapping({"quiet_silent_windows": s, "quiet_off_windows": o, "heat_pump_capacity_limited_entity": e})
    n += 1
    if (cfg.quiet_silent_windows, cfg.quiet_off_windows, cfg.heat_pump_capacity_limited_entity) != (_spec(s, ""), _spec(o, ""), _entity(e, None)):
        mism += 1; print("FIELD MISMATCH", s, o, e)
print(f"RESULT resolution_equiv comparisons={n} mismatches={mism}")
