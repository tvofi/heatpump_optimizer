#!/usr/bin/env python3
"""D15-s1's enumerator: the universe of each step it owns (D15.md M1-M4), one item per line.

Metric (one line): the items a step ranges over; `wc -l` is the step's universe.
Lines name bundles by date and round, checks and probes by the tree's own names, and stores by
their store.DOMAINS name: no entry id, entity id or value of a bundle is printed.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/enum_s1.py --step M1|M2|M3|M4 \
        --bundle REAL --synthetic SYNTH [--repo FULL_CHECKOUT]
M1: `tools/audit/enumerate.py d15-installs` (run against --repo, default the cwd) plus this
    round's bundle; M2: LEAK_PROBES x {export_drops, check_refuses}, the gate scopes and the
    planted-credential sections per bundle; M3: tools/replay/debug_ingest.py's checks per bundle;
    M4: the store documents per bundle.
Expected at the baseline with the owner's 2026-11-16 download: M1=2 (--repo a full checkout;
    in a walled export enumerate.py refuses, finding D15-s1-01), M2=62, M3=24, M4=22.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

CHECKS = ("schema", "manifest-cycles", "manifest-version", "rows-match", "replay-clean",
          "planted-leak-caught", "stores-present", "stores-declared", "stores-sanitize-idempotent",
          "accuracy-loaded", "corruption-refused", "bias-rederived")
SECTIONS = ("replay", "stores", "payload_snapshots", "cycle_rows", "manifest")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=("M1", "M2", "M3", "M4"))
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--synthetic", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=ROOT)
    a = ap.parse_args()
    import debug_ingest
    from heatpump_optimizer import store as S
    real = debug_ingest.load_bundle(a.bundle)
    gen = str((real.get("manifest") or {}).get("generated_at", ""))[:10]
    lines: list[str] = []
    if a.step == "M1":
        proc = subprocess.run([sys.executable, "-I", str(ROOT / "tools/audit/enumerate.py"), "d15-installs",
                               "--repo", str(a.repo)], capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stderr.strip(), file=sys.stderr)
            return 2
        lines = proc.stdout.splitlines() + [f"bundle {gen} round=11 steps=M1,M2,M3,M4 (this round's, the task's path)"]
    elif a.step == "M2":
        spec = importlib.util.spec_from_file_location("hpo_replay_tests", ROOT / "tests" / "replay.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in mod.LEAK_PROBES:
            lines += [f"leak_probe:{name}:export_drops", f"leak_probe:{name}:check_refuses"]
        for tag in ("synthetic", "real"):
            lines += [f"gate {tag} scope={s}" for s in ("whole", "debug", "replay")]
            lines += [f"plant {tag} {s}" for s in SECTIONS]
    elif a.step == "M3":
        lines = [f"check {tag} {c}" for tag in ("synthetic", "real") for c in CHECKS]
    else:
        for tag, path in (("synthetic", a.synthetic), ("real", a.bundle)):
            b = debug_ingest.load_bundle(path)
            lines += sorted(f"store {tag} {S.store_name(k) or 'undeclared'}" for k in (b.get("stores") or {}))
    print("\n".join(sorted(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
