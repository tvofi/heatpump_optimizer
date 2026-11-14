import json, subprocess, sys
T, H, R, RB = sys.argv[1:5]
def load(rev, p):
    return json.loads(subprocess.check_output(["git","show",f"{rev}:{p}"]))
def flat(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items(): out.update(flat(v, pre + "/" + k))
    else: out[pre] = d
    return out
files = ["custom_components/heatpump_optimizer/strings.json"] + [f"custom_components/heatpump_optimizer/translations/{l}.json" for l in ("de","en","sv")]
bad = 0
for p in files:
    t, h, r, rb = (flat(load(x, p)) for x in (T, H, R, RB))
    owned = {k for k in set(r) | set(rb) if r.get(k, None) != rb.get(k, None)}
    keys = set(t) | set(h) | set(r)
    n_owned = n_train = 0
    for k in sorted(keys):
        exp = r.get(k) if k in owned else t.get(k)
        if (k in owned and (k in r) != (k in h)) or (k not in owned and (k in t) != (k in h)) or h.get(k) != exp:
            bad += 1; print("MISMATCH", p, k)
        if k in owned: n_owned += 1
        else: n_train += 1
    print(f"{p}: keys={len(h)} owned-by-3561={sorted(owned)} train-keys-equal={n_train} owned-equal={n_owned}")
print("RESULT key-union:", "PASS" if bad == 0 else f"FAIL {bad}")
sys.exit(1 if bad else 0)
