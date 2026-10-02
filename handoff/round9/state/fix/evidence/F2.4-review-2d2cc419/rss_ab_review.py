"""Reviewer's interleaved A/B of stress.py's own memory entry points
(--memory-baseline, --memory-probe) for one scenario, base vs head.
Each draw: a fresh empty-probe baseline then the scenario probe, in the
tree's own stress.py, exactly as the memory pass computes attributable."""
import json, os, subprocess, sys, statistics
S = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
SPEC = {"season": "winter", "two_zone": True, "dhw": True, "tariff": False,
        "pv": False, "cycling": 1.0}
def probe(tree, args):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([f"{tree}/tests/hastub", f"{tree}/custom_components"])
    p = subprocess.run([PY, f"{tree}/tests/stress.py"] + args, cwd=tree,
                       capture_output=True, text=True, env=env)
    return json.loads(p.stdout.strip().splitlines()[-1])
res = {"base": [], "head": []}
for i in range(N):
    for arm in (("base", "head") if i % 2 == 0 else ("head", "base")):
        tree = f"{S}/{arm}"
        b = float(probe(tree, ["--memory-baseline"])["rss_mb"])
        p = probe(tree, ["--memory-probe", json.dumps(SPEC)])
        att = max(0.0, float(p["rss_mb"]) - b)
        res[arm].append((b, float(p["rss_mb"]), att, float(p["traced_mb"])))
        print(f"draw {i} {arm}: baseline {b:.1f} probe {p['rss_mb']:.1f} attributable {att:.1f} traced {p['traced_mb']:.2f}", flush=True)
for arm, rows in res.items():
    a = [r[2] for r in rows]; t = [r[3] for r in rows]; pk = [r[1] for r in rows]
    print(f"RESULT {arm} n={len(a)} attrib min/median/max {min(a):.1f}/{statistics.median(a):.1f}/{max(a):.1f} "
          f"probe_rss median {statistics.median(pk):.1f} traced min/max {min(t):.2f}/{max(t):.2f} "
          f"over_14.1={sum(1 for x in a if x > 9.4*1.5)}")
