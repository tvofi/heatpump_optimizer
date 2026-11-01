# Null control for the typing repair: undone_settings at fa2d2d91 vs the head, over well-formed undo records.
import importlib.util, sys, json, random, itertools
sys.path.insert(0, "custom_components")
import heatpump_optimizer.entry_config as head
spec = importlib.util.spec_from_file_location("heatpump_optimizer.entry_config_old", "/tmp/claude-0/nc/old/entry_config.py",
                                              submodule_search_locations=None)
old = importlib.util.module_from_spec(spec); old.__package__ = "heatpump_optimizer"; sys.modules[spec.name] = old; spec.loader.exec_module(old)
rng = random.Random(7)
keys = ["name", "two_zone_mode", "dhw_enabled", "wood_furnace_enabled", "comfort_weight", "target_temperature",
        "indoor_temp_entity", "price_weight", "main_fuse_amperes", "dhw_setpoint"]
vals = [None, True, False, "auto", "on", "off", 3.0, 22, "sensor.x"]
n = same = 0
for _ in range(3000):
    d = {k: rng.choice(vals) for k in keys if rng.random() < .5}
    o = {k: rng.choice(vals) for k in keys if rng.random() < .5}
    for scope in ("settings", "learners", "both"):
        rec = json.loads(json.dumps(head.undo_point(scope, d, o)))
        rd, ro = head.factory_settings(d, o, two_zone=rng.random() < .5, dhw=rng.random() < .5, wood=rng.random() < .5)
        a, b = old.undone_settings(rd, ro, rec), head.undone_settings(rd, ro, rec)
        n += 1; same += a == b
        assert old.undo_point(scope, d, o) == head.undo_point(scope, d, o)
print(f"RESULT typing_null_control well_formed_records={n} identical={same}")
for name, rec in {"settings None": {"scope": "both", "settings": None, "pinned": [{}, {}]},
                  "pinned 3 sides": {"scope": "both", "settings": [{}, {}], "pinned": [{}, {}, {}]}}.items():
    try: a = old.undone_settings({}, {}, rec)
    except Exception as e: a = type(e).__name__
    print(f"  malformed {name}: old {a!r} head {head.undone_settings({}, {}, rec)!r}")
