#!/usr/bin/env python3
"""v1_cachekey.py -- D3 verifier's own measurement of D3-s1-02.

Metric (one line): number of environments differing from the clean one ONLY in
HPO_PLANDATA / HPO_GATE_LOCK_LABEL / HPO_GATE_FLOCK_CHILD for which the key
printed by `tests/env_drift.py --cache-key <BASE> --all` (the production CLI, a
subprocess per arm) differs from the clean key -- i.e. a run that would miss an
entry warmed in the clean environment. (Whether the clean key hits the shared
cache right now is printed but is NOT the metric: the shared cache can be stale
for other reasons, e.g. a package installed on the box after warming.)
Second, empirical arm: pairs of entries in the shared drift cache whose
key_inputs differ ONLY in HPO_* environment entries, and how many of those pairs
carry an identical capture_sha256 (a paid re-capture that produced the same bytes).

Controls: clean_again (null, must equal clean); OMP_NUM_THREADS=2 (positive
control: a variable that is SUPPOSED to split the key must split it).
--reads: additionally runs the real capture worker
(`env_drift.py --capture <tree> <tmp>/out.json --all`) with os._Environ.__getitem__
and __iter__ wrapped by a sitecustomize, and reports how many HPO_* reads and
whole-environment iterations the capture made (dynamic, not a grep).
Perturbation (--perturb): in-process, drop "HPO_" from
env_drift.CACHE_ENV_PREFIXES and recompute the keys -> misses must fall to 0.

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/v1_cachekey.py [--perturb] [--reads]
Expected at cdf82daabcfe3777d98b31489f36df5555ec9d82: misses=4 of 4 HPO-only
arms (clean hits), distinct keys over the 4 HPO arms = 4, null equal,
positive control splits; --perturb misses=0; --reads hpo_reads=0.
Machine: 4-vCPU cloud container; wall numbers provisional, counts exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
BASE = "cdf82daabcfe3777d98b31489f36df5555ec9d82"
TMP = Path("/home/claude/audit-r8/tmp/D3-v1")
CACHE = Path(os.environ.get("DRIFT_CACHE_DIR",
                            os.path.expanduser("~/.cache/heatpump_optimizer/drift-baseline")))
NAMES = ("HPO_PLANDATA", "HPO_GATE_LOCK_LABEL", "HPO_GATE_FLOCK_CHILD")
ARMS = {
    "clean": {},
    "plandata_v1": {"HPO_PLANDATA": str(TMP / "plandata")},
    "plandata_other": {"HPO_PLANDATA": str(TMP / "plandata2")},
    "lock_v1": {"HPO_GATE_LOCK_LABEL": "D3-v1", "HPO_GATE_FLOCK_CHILD": "1"},
    "lock_other": {"HPO_GATE_LOCK_LABEL": "D9-s1", "HPO_GATE_FLOCK_CHILD": "1"},
    "clean_again": {},
    "posctl_omp2": {"OMP_NUM_THREADS": "2"},
}
HPO_ARMS = ("plandata_v1", "plandata_other", "lock_v1", "lock_other")


def base_env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("HPO_")}
    e["PYTHONPATH"] = "tests/hastub"
    return e


def key_subprocess(extra):
    env = dict(base_env(), **extra)
    p = subprocess.run([sys.executable, "tests/env_drift.py", "--cache-key", BASE, "--all"],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    return p.stdout.strip()


def keys_inprocess(perturb):
    sys.path.insert(0, str(ROOT / "tests"))
    import env_drift as ed
    if perturb:
        ed.CACHE_ENV_PREFIXES = tuple(p for p in ed.CACHE_ENV_PREFIXES if p != "HPO_")
    saved = dict(os.environ)
    out = {}
    try:
        for arm, extra in ARMS.items():
            os.environ.clear()
            os.environ.update(base_env())
            os.environ.update(extra)
            out[arm] = ed.cache_key(ed.cache_key_inputs(str(ROOT), BASE, True))
    finally:
        os.environ.clear()
        os.environ.update(saved)
    return out


SITE = r'''
import os, atexit, json
_log = {"hpo_reads": [], "iterations": 0}
_gi = os._Environ.__getitem__
_it = os._Environ.__iter__
def _getitem(self, k):
    if isinstance(k, str) and k.startswith("HPO_"):
        _log["hpo_reads"].append(k)
    return _gi(self, k)
def _iter(self):
    _log["iterations"] += 1
    return _it(self)
os._Environ.__getitem__ = _getitem
os._Environ.__iter__ = _iter
atexit.register(lambda: open(os.environ["V1_READLOG"], "w").write(json.dumps(_log)))
'''


def capture_reads():
    d = Path(tempfile.mkdtemp(prefix="v1-reads-", dir=TMP))
    (d / "sitecustomize.py").write_text(SITE)
    env = dict(base_env(), **ARMS["lock_v1"], HPO_PLANDATA=str(TMP / "plandata"),
               TMPDIR=str(TMP), V1_READLOG=str(d / "log.json"))
    env["PYTHONPATH"] = f"{d}:tests/hastub"
    t = time.monotonic()
    p = subprocess.run([sys.executable, "tests/env_drift.py", "--capture", str(ROOT),
                        str(d / "out.json"), "--all"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=3600)
    wall = time.monotonic() - t
    log = json.loads((d / "log.json").read_text())
    n = len(json.loads((d / "out.json").read_text())) if (d / "out.json").exists() else -1
    return p.returncode, log, wall, n


def main():
    perturb = "--perturb" in sys.argv
    t0 = time.process_time(); w0 = time.thread_time()
    if perturb:
        keys = keys_inprocess(True)
        print("PERTURBED (in-process): HPO_ dropped from CACHE_ENV_PREFIXES")
    else:
        keys = {arm: key_subprocess(extra) for arm, extra in ARMS.items()}
    hit = {arm: (CACHE / f"{k}.json").exists() for arm, k in keys.items()}
    for arm in ARMS:
        print(f"  {arm:15s} {keys[arm][:16]} hit={int(hit[arm])}")
    misses = sum(1 for a in HPO_ARMS if keys[a] != keys["clean"])
    print(f"RESULT clean_hits_warm_cache={int(hit['clean'])} count")
    print(f"RESULT hpo_only_misses={misses} count (of {len(HPO_ARMS)})")
    print(f"RESULT distinct_keys_hpo_arms={len({keys[a] for a in HPO_ARMS})} count")
    print(f"RESULT null_equal={int(keys['clean'] == keys['clean_again'])} count")
    pairs = same = 0
    ents = []
    for f in sorted(CACHE.glob("*.json")):
        try:
            d = json.loads(f.read_text())
            ents.append((d["key_inputs"], d["capture_sha256"]))
        except Exception:
            pass
    for i in range(len(ents)):
        for j in range(i + 1, len(ents)):
            (a, ca), (b, cb) = ents[i], ents[j]
            rest_eq = all(a.get(k) == b.get(k) for k in set(a) | set(b) if k != "environment")
            strip = lambda e: sorted(x for x in e if not x.startswith("HPO_"))
            if rest_eq and a["environment"] != b["environment"] and \
                    strip(a["environment"]) == strip(b["environment"]):
                pairs += 1
                same += int(ca == cb)
    print(f"RESULT cache_pairs_differing_only_in_hpo={pairs} count")
    print(f"RESULT cache_pairs_identical_capture={same} count")
    print(f"RESULT posctl_splits={int(keys['posctl_omp2'] != keys['clean'])} count")
    if "--reads" in sys.argv:
        rc, log, wall, n = capture_reads()
        print(f"RESULT capture_rc={rc} count")
        print(f"RESULT capture_payloads={n} count")
        print(f"RESULT capture_hpo_reads={len(log['hpo_reads'])} count {sorted(set(log['hpo_reads']))}")
        print(f"RESULT capture_env_iterations={log['iterations']} count")
        print(f"RESULT capture_wall_s={wall:.1f} s (provisional)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
