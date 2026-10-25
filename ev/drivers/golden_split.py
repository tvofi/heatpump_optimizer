"""Reviewer probe: in the committed golden plans (solver output), count running
steps where channel_heating_steps says a channel heats but pump_arbiter.step_duty's
per-circuit rule (own draw > MIN_RUNNING_DRAW_KW) does not serve it."""
import json, glob, types, sys
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import optimizer as O, pump_arbiter as A
t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
tot = 0; files = 0; total_steps = 0
for f in sorted(glob.glob("tests/golden/*.json")):
    d = json.load(open(f))
    if not isinstance(d, dict) or "power_schedule" not in d or not d.get("dhw_power_schedule"):
        continue
    sp, dh = d["power_schedule"], d["dhw_power_schedule"]
    sh = O.channel_heating_steps(sp, dh); dhh = O.channel_heating_steps(dh, sp)
    n = 0
    for i in range(min(len(sp), len(dh))):
        r = types.SimpleNamespace(timestamps=[t0], power_schedule=[sp[i]], dhw_power_schedule=[dh[i]], duty_floor_kw=None)
        duty = A.step_duty(r, t0)
        if (sh[i] and duty not in ("both", "space")) or (dhh[i] and duty not in ("both", "dhw")):
            n += 1
    total_steps += len(sp); files += 1; tot += n
    if n: print(f"{f.split('/')[-1]}: {n}")
print(f"RESULT golden_steps_channel_heating_but_duty_unserved={tot} files={files} steps={total_steps}")
