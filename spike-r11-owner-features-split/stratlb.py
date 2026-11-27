"""Spike: the measured lower bound of the re-key's expected CPU-s, from a stratified sample stopped early.

    python3 stratlb.py STRATA.json FORK.jsonl MOD.jsonl INFLIGHT.txt

A finished row counts its child plus solve-worker CPU; a row in flight at the stop counts the CPU of
its process group so far (INFLIGHT: `<pgid> group: <ps time>...`, mapped to strata by the caller's
--inflight STRATUM=pgid,... list); a row never started counts 0. Each stratum's mean is therefore a
lower bound, and N_h * mean_h * phases (2 for function-body rows: phase F and phase C; 1 for
module-level rows) a lower bound of that stratum's expected cost. Servers are left out.
"""
import json
import sys

strata = json.load(open(sys.argv[1]))
done = {}
for path in sys.argv[2:4]:
    for l in open(path):
        d = json.loads(l)
        if d.get("verdict") in ("killed", "survived") and not d.get("null"):
            done[d["anchor"]] = d["cpu_s"] + d.get("worker_cpu_s", 0.0)
infl = {}
for l in open(sys.argv[4]):
    g, _, times = l.partition(" group: ")
    tot = 0.0
    for t in times.split():
        s = 0.0
        for p in t.split(":"):
            s = s * 60 + float(p)
        tot += s
    infl[g.strip()] = tot
assign = dict(x.split("=") for x in sys.argv[5:])  # STRATUM=pgid,pgid
total = 0.0
for k, s in strata.items():
    xs = [done[r] for r in s["rows"] if r in done]
    xs += [infl[g] for g in assign.get(k, "").split(",") if g]
    lb = sum(xs) / len(s["rows"])
    mult = 1 if k == "MOD" else 2
    print(f"{k}: N {s['N']}, sampled {len(s['rows'])}, finished {sum(r in done for r in s['rows'])}, "
          f"in flight {len([g for g in assign.get(k, '').split(',') if g])}; mean >= {lb:.1f}; "
          f"phase F >= {s['N'] * lb:.0f}; x{mult} phases >= {s['N'] * lb * mult:.0f}")
    total += s["N"] * lb * mult
print(f"expected total >= {total:.0f} CPU-s (servers excluded); cap 150000")
