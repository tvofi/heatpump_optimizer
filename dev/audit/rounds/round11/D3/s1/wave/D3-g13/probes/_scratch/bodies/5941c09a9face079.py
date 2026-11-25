OLD = "if isinstance(raw, (int, float)) and not isinstance(raw, bool):"
NEW = "if isinstance(raw, (int, float)) or not isinstance(raw, bool):"
MUT = staticmethod(mutated(defrost, W._elapsed, OLD, NEW))


class WM(W):
    pass


WM._elapsed = MUT
from decimal import Decimal  # noqa: E402


def _eq(a, b):
    return a == b or (a != a and b != b)


moved = []
# 1) every production-shaped stamp: aware UTC, aware non-UTC, naive, mixed, DST edge, None
tz2 = timezone(timedelta(hours=2))
pairs = {
    "aware_utc": (s(600), s(0)), "aware_tz2": (s(600).astimezone(tz2), s(0)), "naive": (s(600, N0), s(0, N0)),
    "mixed": (s(600), s(0, N0)), "equal": (s(0), s(0)), "negative": (s(0), s(600)), "none_then": (s(0), None),
    "none_now": (None, s(0)), "micro": (s(0.000001), s(0)),
}
for name, (a, b_) in pairs.items():
    rb, rm = W._elapsed(a, b_), WM._elapsed(a, b_)
    print(f"RESULT stamp_{name}: baseline={rb!r} mutant={rm!r}")
    if not _eq(rb, rm):
        moved.append(name)
# 2) the full window sequences through the mutated helper
for name, (seq, at) in SEQS.items():
    if drive(seq, at) != drive(seq, at, cls=WM):
        moved.append(name)
print(f"RESULT production_shaped_moved={len(moved)} of {len(pairs) + len(SEQS)} ({','.join(moved)})")


# 3) fabricated stamps: objects whose difference's total_seconds() is not a float (no production caller passes one)
class _Delta:
    def __init__(self, v):
        self.v = v

    def total_seconds(self):
        return self.v


class _Stamp:
    tzinfo = timezone.utc

    def __init__(self, v):
        self.v = v

    def __sub__(self, other):
        return _Delta(self.v)


fab = {"bool_True": True, "decimal_5": Decimal("5"), "str_5": "5"}
fab_moved = []
for name, v in fab.items():
    rb = W._elapsed(_Stamp(v), _Stamp(0))
    try:
        rm = WM._elapsed(_Stamp(v), _Stamp(0))
    except Exception as exc:  # noqa: BLE001
        rm = f"raises {type(exc).__name__}"
    print(f"RESULT fabricated_{name}: baseline={rb!r} mutant={rm!r}")
    if not _eq(rb, rm):
        fab_moved.append(name)
print(f"RESULT fabricated_moved={len(fab_moved)} of {len(fab)} ({','.join(fab_moved)})")
footer()
