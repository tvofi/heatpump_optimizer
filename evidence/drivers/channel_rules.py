"""Reviewer probe (#2819 round 2): does any production reader answer
'does this channel heat at this step' by a rule other than
optimizer.channel_heating_steps?  Readers: pump_arbiter.step_duty (the duty the
arbiter serves) and the action's dhw_heating_active rule (optimizer.py
get_current_action: dhw_power > 0.1), on steps straddling 0.05 and 0.1 kW."""
import sys, types
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import optimizer as O, pump_arbiter as A
steps = [(0.30, 0.08), (0.08, 0.50), (0.08, 0.08), (0.30, 0.00), (0.00, 0.30), (0.04, 0.04)]
t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
dis = 0
for sp, dh in steps:
    space_h = O.channel_heating_steps([sp], [dh])[0]
    dhw_h = O.channel_heating_steps([dh], [sp])[0]
    r = types.SimpleNamespace(timestamps=[t0], power_schedule=[sp], dhw_power_schedule=[dh], duty_floor_kw=None)
    duty = A.step_duty(r, t0 + timedelta(minutes=1))
    duty_space = duty in ("both", "space"); duty_dhw = duty in ("both", "dhw")
    dhw_active = dh > 0.1  # optimizer.py get_current_action, verbatim predicate
    d = (space_h != duty_space) + (dhw_h != duty_dhw) + (dhw_h != dhw_active)
    dis += bool(d)
    print(f"space={sp} dhw={dh} channel_heating(space,dhw)=({space_h},{dhw_h}) step_duty={duty} dhw_heating_active={dhw_active} disagree={d}")
print(f"RESULT steps_where_readers_disagree={dis} of {len(steps)}")
