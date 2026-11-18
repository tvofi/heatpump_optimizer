import json
out={}
for z in ("off","on"):
    for m in ("none","manual","smart_read","smart_write"):
        for seed in (None, -50.0, 3.0):
            c=_fl_coord(two_zone_mode=z, mixing_valve_mode=m)
            if seed is not None: c._flow_bias.observe(_fl_expected_curve+seed, _fl_expected_curve)
            _fold_flow_lift(c,_T6); _fold_flow_lift(c,_T6)
            out[f"{z}/{m}/{seed}"]=repr(c._flow_bias.as_dict())
print("BITWISE", json.dumps(out, sort_keys=True))
