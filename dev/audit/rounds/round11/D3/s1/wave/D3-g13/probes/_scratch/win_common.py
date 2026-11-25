from datetime import datetime, timedelta, timezone  # noqa: E402
from custom_components.heatpump_optimizer import defrost  # noqa: E402

W = defrost.DefrostWindow
T0 = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
N0 = datetime(2026, 1, 15, 6, 0)


def s(sec, base=T0):
    return base + timedelta(seconds=sec)


# (name, [(op, seconds, flag)], peek/close at seconds); op "o" observe, "c" close
SEQS = {
    "on_then_peek": ([("o", 0, True)], 600),
    "off_on_peek": ([("o", 0, False), ("o", 300, True)], 900),
    "on_off_peek": ([("o", 0, True), ("o", 300, False)], 900),
    "repeat_same_stamp": ([("o", 0, True), ("o", 0, True), ("o", 300, True), ("o", 300, True)], 300),
    "zero_length": ([("o", 0, True)], 0),
    "backwards_clock": ([("o", 600, True), ("o", 300, True)], 200),
    "dark_then_on": ([("o", 0, None), ("o", 120, True)], 600),
    "carried_level_after_close": ([("o", 0, True), ("c", 1800, None)], 2400),
    "carried_level_reobserved": ([("o", 0, True), ("c", 1800, None), ("o", 1800, True)], 2400),
    "none_observed": ([], 600),
}


def drive(seq, peek_at, peek_fn=None, cls=W):
    w = cls()
    for op, sec, flag in seq:
        if op == "o":
            w.observe(s(sec), flag)
        else:
            w.close(s(sec))
    ob = (peek_fn or cls.peek)(w, s(peek_at))
    return (round(ob.duty, 12), ob.events, ob.observed, ob.seconds)
