import asyncio, sys
sys.path.insert(0, sys.argv[1])
from custom_components.heatpump_optimizer import async_migrate_entry
from custom_components.heatpump_optimizer import const
class E:
    def __init__(s, data, options):
        s.data, s.options, s.version, s.minor_version = dict(data), dict(options), 1, 1
class CE:
    def async_update_entry(s, e, data=None, options=None, version=None, minor_version=None):
        e.data, e.options, e.version, e.minor_version = data, options, version, minor_version
class H: config_entries = CE()
bad = E({"min_temperature": "abc", "dhw_tank_volume": 200.0}, {"silent_mode_power_fraction": "abc"})
ok = asyncio.run(async_migrate_entry(H(), bad))
print("bad:", ok, bad.data, bad.options)
txt = E({"min_temperature": "19.5"}, {})
asyncio.run(async_migrate_entry(H(), txt)); print("text:", txt.data, txt.options)
good = E({"min_temperature": 19.0, "dhw_tank_volume": 200.0}, {})
asyncio.run(async_migrate_entry(H(), good)); print("good:", good.data, good.options)
