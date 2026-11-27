"""Spike: the re-key's expected and upper CPU-s from the per-stratum seeded sample, driven to completion.

    python3 stratcost.py STRATA.json FORK.jsonl MOD.jsonl [--shards N] [--line-record S]

Per row the cost is the drive's child CPU plus its solve workers' CPU (forkdrive.py, moddrive.py).
Stratum h of N_h rows, sample of n_h rows driven to kill or end: expected N_h * mean_h; upper
N_h * (mean_h + t_{0.95, n_h - 1} * sd_h / sqrt(n_h)), never below N_h * max_h. Phase C (the C1
re-drive on the written parts) is priced at phase F's figure: a part's drive runs a subset of the
spans phase F ran between the same fork point and the same kill span, so it costs at most phase F's
for a row killed in that span (a miss in the phase-F part is counted by the drive's ledger, not here).
Module-level rows have no phase F: their file-edit drive is the C1 drive and is counted once.
Servers: phase F one swap-run pass and phase C one pass of every part, per shard, each priced at the
measured server CPU; plus one LINE record of the parts (--line-record, measured on the monolith).
"""
import json
import math
import sys

T95 = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833}

a = sys.argv[1:]
strata = json.load(open(a[0]))
res = {}
server = []
for path in a[1:3]:
    for l in open(path):
        d = json.loads(l)
        if d.get("server"):
            server.append(d["cpu_s"])
        elif "anchor" in d and not d.get("null") and d.get("verdict") in ("killed", "survived"):
            res[d["anchor"]] = d
shards = int(a[a.index("--shards") + 1]) if "--shards" in a else 1
line_rec = float(a[a.index("--line-record") + 1]) if "--line-record" in a else 0.0
exp_tot = up_tot = 0.0
for k, s in strata.items():
    xs = [res[r]["cpu_s"] + res[r].get("worker_cpu_s", 0.0) for r in s["rows"] if r in res]
    n, N = len(xs), s["N"]
    if n < len(s["rows"]):
        print(f"{k}: {len(s['rows']) - n} of {len(s['rows'])} sampled rows not finished; figures refused")
        sys.exit(1)
    mean = sum(xs) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    up = max(mean + T95.get(n - 1, 1.833) * sd / math.sqrt(n), max(xs))
    mult = 1 if k == "MOD" else 2  # phase F + phase C
    killed = sum(res[r]["verdict"] == "killed" for r in s["rows"])
    print(f"{k}: N {N}, n {n}, killed {killed}, per row mean {mean:.1f} sd {sd:.1f} max {max(xs):.1f} upper {up:.1f}; "
          f"x{mult} phases: expected {N * mean * mult:.0f}, upper {N * up * mult:.0f}")
    exp_tot += N * mean * mult
    up_tot += N * up * mult
srv = max(server) if server else 0.0
over = shards * 2 * srv + line_rec
print(f"servers: {shards} shard(s) x 2 passes x {srv:.0f} + LINE record {line_rec:.0f} = {over:.0f}")
print(f"TOTAL expected {exp_tot + over:.0f}  upper {up_tot + over:.0f}  cap 150000")
