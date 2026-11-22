"""Reviewer's driver (built by the fix reviewer, not the finder): every numeric
key of config_fuzz.HEALTHY x {str_word, none, list, dict}, at one version,
through config_fuzz.run -- the finder's own scenario."""
import sys, copy, os, time
sys.path.insert(0, os.environ["FUZZDIR"])
import config_fuzz as F
v = int(sys.argv[1]); only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
H = dict(F.HEALTHY)
for kv in os.environ.get("EXTRA","").split(","):
    if kv: k,_,val=kv.partition("="); H[k]=float(val) if "." in val else int(val)
keys = [k for k in sorted(H) if isinstance(H[k], (int, float)) and not isinstance(H[k], bool)]
if only: keys = [k for k in keys if k in only]
print("CTRL", F.run(v, copy.deepcopy(H)), flush=True)
print("numeric keys", len(keys), flush=True)
bad = 0
for k in keys:
    for op, val in (("str_word", "abc"), ("none", None), ("list", [H[k]]), ("dict", {"v": H[k]})):
        d = copy.deepcopy(H); d[k] = val
        r = F.run(v, d)
        fail = r["migrate"] != "ok" or r["build"] != "ok" or (r["c1"] != "ok" and r["c2"] != "ok")
        if fail:
            bad += 1; print(f"FAIL key={k} op={op} {str(r)[:160]}", flush=True)
print(f"RESULT census_fail={bad} of {len(keys)*4}", flush=True)
