from datetime import datetime, timedelta, timezone  # noqa: E402
import numpy as np  # noqa: E402

NAME = "_update_snow_memory"
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def drive(mutated, accum, gap_h, rate):
    """One _update_snow_memory call: (accumulator cm, solar damped?)."""
    c = make_coord({"snow_roof_factor_enabled": True})
    c._snow_accum_cm, c._snow_accum_last, c._last_heavy_snow = accum, NOW - timedelta(hours=gap_h), None
    with arm(NAME, OLD, NEW, mutated):
        damped = c._update_snow_memory(NOW, np.array([rate] * 48, dtype=float))
    return round(c._snow_accum_cm, 6), bool(damped)


for label, args in CASES.items():
    b, m = drive(False, *args), drive(True, *args)
    print(f"RESULT {label}_baseline=(accum_cm,damped){b}")
    print(f"RESULT {label}_mutant=(accum_cm,damped){m}")
moved = sum(int(drive(False, *a) != drive(True, *a)) for a in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} null inputs (accum, gap_h, rate) {NULLS}")
print(f"RESULT inputs_tried={len(CASES) + len(NULLS)} count")
tail()
