from datetime import datetime, timezone  # noqa: E402

NAME = "_track_curve_comfort"
OLD = "if margin <= 0.0 and self._curve_learner.bias < 0.0:"
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def drive(mutated, margin, bias):
    """One _track_curve_comfort call on a live coordinator; the zone margin is fixed via worst_zone_margin_k."""
    c = make_coord({"curve_learning_enabled": True})
    lr = c._curve_learner
    lr.bias, lr.comfortable_days, lr.resets = bias, 5, 0
    with arm(NAME, OLD, NEW, mutated), \
            mock.patch.object(co, "worst_zone_margin_k", lambda temps, floor: margin), \
            mock.patch.object(CLS, "_learning_frozen", lambda self, *a, **k: None), \
            mock.patch.object(co, "learner_room_unread", lambda cfg: None):
        c._curve_day = NOW.date().isoformat()
        c._track_curve_comfort(NOW)
    return (round(lr.bias, 6), lr.comfortable_days, lr.resets)


for label, (margin, bias) in CASES.items():
    b, m = drive(False, margin, bias), drive(True, margin, bias)
    print(f"RESULT {label}_baseline=(bias,comfortable_days,resets){b}")
    print(f"RESULT {label}_mutant=(bias,comfortable_days,resets){m}")
moved = sum(int(drive(False, mg, bs) != drive(True, mg, bs)) for mg, bs in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} null inputs {NULLS}")
tail()
