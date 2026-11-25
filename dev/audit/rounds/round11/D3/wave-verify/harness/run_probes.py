#!/usr/bin/env python3
"""V1: re-run every candidate's probe exactly as its header says, in the baseline tree; keep stdout, stderr, rc."""
import json, os, subprocess, sys, time, pathlib
from concurrent.futures import ThreadPoolExecutor
D = pathlib.Path("<seat-dir>")
BASE = D / "base"
OUT = D / "v1"; OUT.mkdir(exist_ok=True)
cands = json.load(open(D / "candidates.json"))
only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
def run(c):
    if only and c["box"] not in only: return
    o = OUT / f"{c['key']}.json"
    if o.exists(): return
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    t = time.time()
    try:
        p = subprocess.run([sys.executable, c["probe_path"]], cwd=BASE, env=env, capture_output=True, text=True, timeout=900)
        r = {"rc": p.returncode, "stdout": p.stdout[-20000:], "stderr": p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        r = {"rc": "timeout", "stdout": "", "stderr": ""}
    r.update(key=c["key"], box=c["box"], wall_s=round(time.time() - t, 1), load1=os.getloadavg()[0])
    json.dump(r, open(o, "w"))
    print(c["box"], c["key"], r["rc"], r["wall_s"], flush=True)
with ThreadPoolExecutor(4) as ex:
    list(ex.map(run, cands))
print("V1-DONE", flush=True)
