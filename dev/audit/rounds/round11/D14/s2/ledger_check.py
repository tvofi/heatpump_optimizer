"""D14.M1 ledger check (D14-s2, round 11): is each class's status what its own fields say?

Metric, per class of dev/audit/config/bugclasses.json (status open,
prototype-only, detector or barriered -- the M1/M5 cell's axis):
  * status_vocab   the status is one of the brief's three (open / detector /
                   barriered) -- D14.md M1 defines no other
  * detector_cmd   'detector' status carries a non-empty detector; 'barriered'
                   carries a non-empty barrier and a runnable command (detector
                   or barrier text naming an in-tree script)
  * paths_exist    every repository path the detector/barrier text names
                   (tests/, tools/, dev/, custom_components/, .github/) exists
                   at the export root
  * counts         total == len(instances) == sum(per_round.values()), and
                   max_per_round == max(per_round.values())
One CLASS line per class with each verdict; RESULT counts per check.
Key: the ledger's own fields and the tree's files, nothing hand-carried.

Perturbation (``--plant``): one class's total incremented in memory -> the
counts failure count rises by 1.

Run: python3 dev/audit/rounds/round11/D14/s2/ledger_check.py [--plant]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: the RESULT lines it prints are exact
(no timing); recorded in REPORT.md.
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
import json
import re
import sys
import time

PATH = re.compile(r"(?<![\w/.-])((?:tests|tools|dev|custom_components|\.github)/[\w./-]+\.(?:json|mjs|py|js|sh|md|yml)\b)")
VOCAB = {"open", "detector", "barriered"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    with open("dev/audit/config/bugclasses.json", encoding="utf-8") as f:
        ledger = json.load(f)
    classes = {k: v for k, v in ledger.items() if not k.startswith("_")}
    if a.plant:
        k0 = sorted(classes)[0]
        classes[k0] = dict(classes[k0], total=(classes[k0].get("total") or 0) + 1)
    fails = {"status_vocab": [], "detector_cmd": [], "paths_exist": [], "counts": []}
    for k in sorted(classes):
        v = classes[k]
        st = v.get("status")
        det = (v.get("detector") or "").strip()
        bar = (v.get("barrier") or "").strip()
        verdicts = {}
        verdicts["status_vocab"] = st in VOCAB
        names = PATH.findall(det + " " + bar)
        if st == "detector":
            verdicts["detector_cmd"] = bool(det)
        elif st == "barriered":
            verdicts["detector_cmd"] = bool(bar) and (bool(det) or bool(names))
        else:
            verdicts["detector_cmd"] = True
        missing = sorted({p.rstrip(".") for p in names if not os.path.exists(p.rstrip("."))})
        verdicts["paths_exist"] = not missing
        inst = v.get("instances") or []
        pr = v.get("per_round") or {}
        tot = v.get("total")
        mx = v.get("max_per_round")
        verdicts["counts"] = (
            tot == len(inst) == sum(pr.values())
            and mx == (max(pr.values()) if pr else 0)
        )
        for c, ok in verdicts.items():
            if not ok:
                fails[c].append(k)
        detail = ""
        if missing:
            detail += f" missing={missing}"
        if not verdicts["counts"]:
            detail += f" total={tot} instances={len(inst)} per_round_sum={sum(pr.values())} max={mx}"
        print(f"CLASS {k} status={st} det={'y' if det else 'n'} bar={'y' if bar else 'n'} "
              + " ".join(f"{c}={'ok' if ok else 'FAIL'}" for c, ok in verdicts.items()) + detail)
    print(f"RESULT classes={len(classes)}")
    for c, ks in fails.items():
        print(f"RESULT {c}_fail={len(ks)} {','.join(ks)}")
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
