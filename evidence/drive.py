import sys, collections, re, time
sys.path.insert(0, sys.argv[1]); import roster_edit as R
loc, n, dur = sys.argv[2], 0, float(sys.argv[3])
mode = sys.argv[4]
c = collections.Counter(); t0 = time.time()
while time.time() - t0 < dur:
    if mode == "once":
        rc, o, e = R._fetch_once(loc)
        if rc == 0: c["ok"] += 1
        elif R._is_lock_race(rc, o, e): c["race"] += 1
        else:
            c["other"] += 1; print("OTHER:", re.sub("[0-9a-f]{40}", "<sha>", e).strip()[:300])
    else:
        try: R.fetch_origin(loc); c["ok"] += 1
        except R.Refuse as x: c["refuse"] += 1; print("REFUSE:", str(x)[:200])
print("RESULT", mode, dict(c))
