"""Prototype P3 arm B: the comfort floor price per zone-K is the same in every topology and twin.

The marginal price of undershooting the floor by u -> 0+ in ONE zone must equal the single-zone
room's, in the scalar _comfort_terms and in _comfort_terms_batch alike."""
import sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
import golden

t0 = time.time()
n, u = 8, 1e-4
def slope(opt, zone, batch):
    floor = np.full(n, 20.0); top = np.full(n, 24.0); tgt = np.full(n, 21.0); band = np.full(n, 1.0)
    def pen(d):
        room = np.full(n + 1, 21.0); up = room.copy(); lo = room.copy()
        tgt_arr = {"room": room, "upper": up, "lower": lo}[zone]
        tgt_arr[1:] = 20.0 - d
        if zone == "room":
            up[1:] = lo[1:] = 20.0 - d
        args = (room, up, lo, tgt, floor, top, band)
        if batch:
            return float(opt._comfort_terms_batch(*(a[None, :] if a.shape == (n + 1,) else a for a in args))[0][0])
        return float(opt._comfort_terms(*args)[0])
    return (pen(u) - pen(0.0)) / (u * n)

one = golden.make(two_zone=False, dhw=False)["optimizer"]
two = golden.make(two_zone=True, dhw=False)["optimizer"]
ref = slope(one, "room", False)
bad = 0
for batch in (False, True):
    r1 = slope(one, "room", batch)
    for zone in ("upper", "lower"):
        r2 = slope(two, zone, batch)
        ok = abs(r2 / ref - 1.0) < 1e-3 and abs(r1 / ref - 1.0) < 1e-3
        bad += not ok
        print(f"ARM batch={int(batch)} zone={zone} single={r1:.5f} two_zone={r2:.5f} ratio={r2 / ref:.4f} ok={int(ok)}")
print(f"RESULT p3_zone_price_mismatch={bad} of 4 wall_s={time.time() - t0:.2f}")
