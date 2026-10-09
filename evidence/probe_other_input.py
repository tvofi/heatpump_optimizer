#!/usr/bin/env python3
"""Reviewer-built. Floor-return live, ANOTHER configured input dead: does the
floor-return repair stay down?   python probe_other_input.py <tree>"""
import asyncio, os, sys
from datetime import timedelta
tree = os.path.abspath(sys.argv[1]); os.chdir(tree)
sys.path[:0] = [os.path.join(tree, p) for p in ("tests/hastub", "custom_components", "tests")]
path = os.path.join(tree, "tests/features.py"); src = open(path, encoding="utf-8").read()
ns = {"__file__": path, "__name__": "probe"}
exec(compile(src[: src.index('R = Results("Feature modules")')], path, "exec"), ns)
from homeassistant.util import dt as dtu
from heatpump_optimizer import const, notifier
from harness import FakeEntry
FakeState, FakeHass, Coord = ns["FakeState"], ns["FakeHass"], ns["Coord"]
now = dtu.utcnow()
states = {"sensor.indoor": FakeState("unavailable", unit="°C"),
          "sensor.outdoor": FakeState("-5.0", unit="°C"),
          "sensor.floor_return_synthetic": FakeState("31.5", unit="°C")}
cfg = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       const.CONF_FLOOR_RETURN_TEMP_ENTITY: "sensor.floor_return_synthetic"}
c = Coord(FakeHass(states), FakeEntry(data=cfg)); asyncio.run(c._update_current_state())
p = {"input_problems": c._input_health_view()["input_problems"]}
hass = FakeHass(); w = notifier.FloorReturnWatch(hass); lim = notifier.FLOOR_RETURN_SILENT_MINUTES
for m in (0, lim, lim * 10): w.handle(p, now + timedelta(minutes=m))
raised = [i for i in getattr(hass, "issues", []) if i[1] == notifier.ISSUE_FLOOR_RETURN_SILENT]
print(f"RESULT other-input-dead: problems={[(q['input'], q['problem']) for q in p['input_problems']]} "
      f"floor_return_temp={c._floor_return_temp} floor_return_silent_raised={len(raised)} "
      f"named={[i[2].get('translation_placeholders', {}).get('entity_id') for i in raised]}")
