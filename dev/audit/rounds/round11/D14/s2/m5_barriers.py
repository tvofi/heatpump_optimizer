"""D14.M5 barrier table (D14-s2, round 11): where each class's detector/barrier lives, and whether a CI entry point runs it.

Metric, per class of dev/audit/config/bugclasses.json whose status is open,
prototype-only, detector or barriered (the M1/M5 cell axis; `_rca` is not a
class): the in-tree scripts its `barrier` and `detector` text names, whether
each exists at the export root, and whether a CI entry point names it
(.github/workflows/*.yml, tests/run.sh, tools/ci/gate.py, or tests/entities.py /
tests/features.py, which run on the gate and spawn their children). A class is
`ci` when one named script is wired, `offline` when its scripts exist and none
is wired, `none` when its text names no in-tree script.
Key: the ledger's own text and the tree's files; nothing hand-carried.
Gate seconds per detector/barriered class are sweep.py's ROW lines (provisional).

Perturbation (``--plant``): one barriered class's barrier text pointed at a
script no CI entry point names (this harness itself) in memory ->
its row reads `offline` and RESULT barriered_offline rises by 1.

Run: python3 dev/audit/rounds/round11/D14/s2/m5_barriers.py [--plant]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT lines exact (no timing).
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import glob
import json
import re
import sys
import time
from collections import Counter

PATH = re.compile(r"(?<![\w/.-])((?:tests|tools|dev|custom_components|\.github)/[\w./-]+\.(?:mjs|py|js|sh))\b")
# A bare script name (`merge_train.py --self-test`) resolves to the unique in-tree
# file of that name under the code roots; an ambiguous or absent name stays unresolved.
BARE = re.compile(r"(?<![\w/.-])([\w-]+\.(?:mjs|py|sh))\b")
ROOTS = ("tests", "tools", ".github", "dev/audit/harnesses", "dev/audit/rca", "custom_components")


def _resolve(name, cache={}):
    if not cache:
        for r in ROOTS:
            for f in glob.glob(f"{r}/**/*", recursive=True):
                if "/rounds/" not in f and os.path.isfile(f):
                    cache.setdefault(os.path.basename(f), []).append(f)
    hits = cache.get(name, [])
    return hits[0] if len(hits) == 1 else None
AXIS = ("open", "prototype-only", "detector", "barriered")
CI = sorted(glob.glob(".github/workflows/*.yml")) + ["tests/run.sh", "tools/ci/gate.py",
                                                      "tests/entities.py", "tests/features.py"]


def _ci_text():
    out = {}
    for p in CI:
        try:
            with open(p, encoding="utf-8") as f:
                out[p] = f.read()
        except OSError:
            pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    with open("dev/audit/config/bugclasses.json", encoding="utf-8") as f:
        ledger = json.load(f)
    classes = {k: v for k, v in ledger.items() if isinstance(v, dict) and v.get("status") in AXIS}
    if a.plant:
        k0 = sorted(k for k, v in classes.items() if v["status"] == "barriered")[0]
        classes[k0] = dict(classes[k0], barrier="dev/audit/rounds/round11/D14/s2/m5_barriers.py", detector=None)
    ci = _ci_text()
    tally = Counter()
    for k in sorted(classes):
        v = classes[k]
        text = f"{v.get('barrier') or ''} {v.get('detector') or ''}"
        scripts = {p.rstrip(".") for p in PATH.findall(text)}
        names = {os.path.basename(x) for x in scripts}
        scripts |= {r for b in BARE.findall(text) if b not in names and (r := _resolve(b))}
        scripts = sorted(scripts)
        present = [s for s in scripts if os.path.exists(s)]
        wired = sorted({s for s in present for p, t in ci.items()
                        if p != s and os.path.basename(s) in t})
        state = "ci" if wired else ("offline" if present else "none")
        tally[(v["status"], state)] += 1
        print(f"CLASS {k} status={v['status']} state={state} named={len(scripts)} present={len(present)} "
              f"wired={','.join(wired) or '-'} unwired={','.join(s for s in present if s not in wired) or '-'}")
    print(f"RESULT classes={len(classes)}")
    for st in AXIS:
        for state in ("ci", "offline", "none"):
            print(f"RESULT {st.replace('-', '_')}_{state}={tally[(st, state)]}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
