"""Verifier D1#1, V2 for D1-s2-05: exhaustive (not seeded) wrong-type numeric options, at the CURRENT version.

Metric: over every key of the healthy all-features entry whose value is a non-bool number,
substituted by "abc" and by None, the number of mutants whose coordinator constructor
raises or whose two cycles both raise, at entry.version = CONFIG_ENTRY_VERSION (7, no
migration runs) and at version 1. Also the share by op. Null: healthy entry -> 0.
Uses the finder rig's scenario() for setup/cycles only; the mutant set is mine.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_05_config_exhaustive.py [--limit N]
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "s2"))
import config_fuzz as F  # noqa: E402
from heatpump_optimizer.const import CONFIG_ENTRY_VERSION  # noqa: E402

limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10**9
keys = sorted(k for k, v in F.HEALTHY.items() if isinstance(v, (int, float)) and not isinstance(v, bool))[:limit]


def fails(out):
    if out["build"] != "ok":
        return "build"
    if out["c1"] != "ok" and out["c2"] != "ok":
        return "cycles"
    return None


ctrl = {v: fails(F.run(v, copy.deepcopy(F.HEALTHY))) for v in (1, CONFIG_ENTRY_VERSION)}
print(f"CTRL {ctrl}")
tot = {}
for version in (CONFIG_ENTRY_VERSION, 1):
    for op, val in (("abc", "abc"), ("none", None)):
        n = 0
        for k in keys:
            d = copy.deepcopy(F.HEALTHY)
            d[k] = val
            f = fails(F.run(version, d))
            if f:
                n += 1
                print(f"FAIL v{version} {op} {k} {f}")
        tot[(version, op)] = n
for (v, op), n in tot.items():
    print(f"RESULT v{v}_{op}_permanent_fail={n} of {len(keys)}")
print(f"RESULT null_ctrl_fail={sum(1 for x in ctrl.values() if x)} of 2")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
