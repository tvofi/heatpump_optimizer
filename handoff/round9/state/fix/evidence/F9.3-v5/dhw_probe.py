import asyncio, json, sys
sys.path.insert(0, "tests")
import finite_boundary as fb
S = fb._storage
def rt(payload=None):
    S._DISK.clear()
    c = fb._build_coord()
    if payload is not None:
        S._DISK[fb.const.DOMAIN + "_" + fb.ENTRY_ID + "_dhw_profile"] = json.dumps(payload)
        asyncio.run(c._dhw_learner.async_load_profile())
    S._DISK.clear()
    asyncio.run(c._dhw_learner.async_save_profile())
    return json.loads(S._DISK[fb.const.DOMAIN + "_" + fb.ENTRY_ID + "_dhw_profile"])
fresh = rt()
again = rt(fresh)
cells = lambda p: p["hourly_profile"]
print("RESULT fresh_min=%.3g fresh_cells_below_0.2=%d" % (min(cells(fresh)), sum(v < 0.2 for v in cells(fresh))))
print("RESULT first_reload_changed_cells=%d of %d" % (sum(a != b for a, b in zip(cells(fresh), cells(again))), len(cells(fresh))))
ctrl = dict(again)
ctrl2 = rt(ctrl)
print("RESULT null_control_second_reload_changed_cells=%d" % sum(a != b for a, b in zip(cells(again), cells(ctrl2))))
prev = fresh
for i in range(1, 6):
    nxt = rt(prev)
    d = max(abs(a - b) for a, b in zip(cells(prev), cells(nxt)))
    print("RESULT reload_%d_max_abs_change=%.3g min=%.4g mean=%.6f" % (i, d, min(cells(nxt)), sum(cells(nxt)) / 24))
    prev = nxt
