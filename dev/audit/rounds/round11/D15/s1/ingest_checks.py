#!/usr/bin/env python3
"""D15-s1 M3: tools/replay/debug_ingest.py's checks, each beside the size of the section it reads.

Metric (one line): per ingest check, ok (1/0) and the item count of the bundle section the
check reads (0 = the pass is vacuous); per bundle, checks passing and checks passing vacuously.
Counts and check names only: no bundle value is printed. Never commit a bundle.
Count key: debug_ingest.Results.fails as ingest() returns it, and len() of the section read.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/ingest_checks.py \
        --bundle B [--synthetic S] [--corrupt accuracy] [--empty SECTION]
Expected at the baseline: synthetic and real checks_ok=11/11 while the tool's own verdict line
    reads tool_stages_ok=12/12 (checks_run=11), vacuous_passes=0; --corrupt accuracy:
    11/12 (bias-rederived fails, corruption-refused ok); --empty replay: replay-clean stays ok
    while its section reads 0 (vacuous_passes rises to 1) -- the perturbation.
Perturbation: --empty replay (the replay half emptied, as a download whose recorder was not set
    up carries it) -> vacuous_passes 0 -> 1 (up); --corrupt accuracy -> checks_ok 12 -> 11 (down).
Null control: the synthetic bundle (dbg_bundle_gen.py), where every section is filled.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: tools/replay/debug_ingest.py:ingest, store:quarantines, store:store_name,
    accuracy:AccuracyTracker.from_dict.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import copy
import io
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402

CHECKS = ("schema", "manifest-cycles", "manifest-version", "rows-match", "replay-clean",
          "planted-leak-caught", "stores-present", "stores-declared", "stores-sanitize-idempotent",
          "accuracy-loaded", "corruption-refused", "bias-rederived")


def section_size(bundle: dict, check: str) -> int:
    replay = bundle.get("replay") or {}
    stores = bundle.get("stores") or {}
    acc = [v for k, v in stores.items() if k.endswith("_accuracy")]
    samples = ((acc[0].get("accuracy", acc[0]) if acc else {}) or {}).get("samples")
    return {
        "schema": int(bool(bundle.get("schema"))),
        "manifest-cycles": int(bool(bundle.get("manifest"))),
        "manifest-version": int(bool((bundle.get("manifest") or {}).get("integration_version"))),
        "rows-match": len(bundle.get("cycle_rows") or []),
        "replay-clean": sum(len(r or []) for r in (replay.get("states") or {}).values()),
        "planted-leak-caught": 1,
        "stores-present": len(stores),
        "stores-declared": len(stores),
        "stores-sanitize-idempotent": len(stores),
        "accuracy-loaded": len(samples) if isinstance(samples, list) else 0,
        "corruption-refused": len(acc),
        "bias-rederived": sum(1 for r in bundle.get("cycle_rows") or [] if r.get("accuracy_sample")),
    }[check]


def run(tag: str, bundle: dict, corrupt: str) -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        res = debug_ingest.ingest(bundle, corrupt=corrupt)
    ran = [c for c in CHECKS if f": {c}" in buf.getvalue()]
    ok = [c for c in ran if c not in res.fails]
    vacuous = [c for c in ok if section_size(bundle, c) == 0]
    for c in ran:
        print(f"RESULT {tag}_check[{c}]={int(c in ok)} section_items={section_size(bundle, c)} unit=bool")
    print(f"RESULT {tag}_checks_ok={len(ok)}/{len(ran)} unit=count")
    # What the tool's own verdict line (debug_ingest.main: 12 - fails over a constant 12) states.
    print(f"RESULT {tag}_tool_stages_ok={12 - len(res.fails)}/12 checks_run={len(ran)} unit=count")
    print(f"RESULT {tag}_vacuous_passes={len(vacuous)} unit=count")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--synthetic", type=Path)
    ap.add_argument("--corrupt", choices=("", "accuracy"), default="")
    ap.add_argument("--empty", choices=("", "replay", "cycle_rows", "stores"), default="")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    synth = a.synthetic
    if synth is None:
        out = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, str(ROOT / "tools/replay/dbg_bundle_gen.py"), "--days", "7", "--out", str(out)],
                       check=True, capture_output=True, env=dict(os.environ, PYTHONPATH="tests/hastub:tests"))
        synth = out / "bundle.json"
    for tag, path in (("synthetic", synth), ("real", a.bundle)):
        if path is None:
            continue
        bundle = copy.deepcopy(debug_ingest.load_bundle(path))
        if a.empty:
            bundle[a.empty] = {} if a.empty != "cycle_rows" else []
        run(tag, bundle, a.corrupt)
    tc = time.thread_time() - t0
    print(f"RESULT thread_factor={((time.process_time() - c0) / tc) if tc > 0 else 1.0:.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        sw = int(next(l for l in out.splitlines() if l.startswith("Swapins")).split(":")[1].strip(" ."))
    except Exception:  # noqa: BLE001
        sw = -1
    print(f"RESULT swapins={sw} unit=count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
