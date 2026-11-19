#!/usr/bin/env python3
"""D15-s1 M1: intake and version seam of a diagnostics download.

Metric (one line): cycle rows with and without a ``version``; releases the rows name; each
release's first row dated after its tag (`git for-each-ref refs/tags`, a mismatch counted
when the first row precedes the tag); restart gaps by D15.md M1's rule
(dev/audit/harnesses/d15_restart_gaps.py's GAP_INTERVALS x optimization_interval); per gap,
accuracy-sample stamps (the rows' own accuracy_sample.t) strictly inside it, i.e. evidence the
integration ran during it. Counts only: no bundle value is printed. Never commit a bundle.
Count key: the bundle's cycle_rows as debug_ingest.load_bundle unwraps them.

Command (export or checkout root, with git tags):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/intake.py --bundle B [--strip-version]
Expected (owner's 2026-11-16 download): rows=662, rows_without_version=0, releases=9,
    release_before_tag=0, untagged_releases=0, restart_gaps=2, gaps_with_samples_inside=2,
    collection_final=1; synthetic (dbg_bundle_gen.py): rows=336, rows_without_version=336, gaps=0.
Perturbation: --strip-version drops every row's ``version`` -> rows_without_version 0 -> 662 (up),
    releases 9 -> 0: attribution falls back to the gap rule.
Null control: the synthetic bundle (no release field, no gap).
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: debugger:cycle_row (the writer of every row field read), const:DEFAULT_OPTIMIZATION_INTERVAL,
    tools/replay/debug_ingest.py:load_bundle.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

GAP_INTERVALS = 3  # dev/audit/harnesses/d15_restart_gaps.py


def tags() -> dict[str, datetime]:
    out = subprocess.run(["git", "for-each-ref", "--format=%(refname:short) %(creatordate:iso-strict)", "refs/tags/v*"],
                         capture_output=True, text=True).stdout
    found = {}
    for line in out.splitlines():
        name, _, when = line.partition(" ")
        try:
            found[name[1:]] = datetime.fromisoformat(when)
        except ValueError:
            continue
    return found


def measure(tag: str, path: Path, strip: bool) -> None:
    raw = json.loads(path.read_text())
    data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
    config = data.get("config") or {}
    bundle = debug_ingest.load_bundle(path)
    rows = [dict(r) for r in bundle.get("cycle_rows") or []]
    if strip:
        for r in rows:
            r.pop("version", None)
    print(f"RESULT {tag}_rows={len(rows)} unit=rows")
    print(f"RESULT {tag}_rows_without_version={sum(1 for r in rows if not r.get('version'))} unit=rows")
    first: dict[str, datetime] = {}
    for r in rows:
        if r.get("version"):
            first.setdefault(r["version"], datetime.fromisoformat(r["t"]))
    known = tags()
    print(f"RESULT {tag}_releases={len(first)} unit=count")
    print(f"RESULT {tag}_untagged_releases={sum(1 for v in first if v not in known)} unit=count")
    print(f"RESULT {tag}_release_before_tag={sum(1 for v, t in first.items() if v in known and t < known[v])} unit=count")
    switches = sum(1 for a, b in zip(rows, rows[1:]) if a.get("version") != b.get("version"))
    print(f"RESULT {tag}_release_switches={switches} unit=count")
    named = config.get(const.CONF_OPTIMIZATION_INTERVAL)
    interval_s = float(named if named is not None else const.DEFAULT_OPTIMIZATION_INTERVAL) * 60.0
    stamps = [datetime.fromisoformat(r["t"]) for r in rows]
    samples = sorted({datetime.fromisoformat(r["accuracy_sample"]["t"]) for r in rows
                      if isinstance(r.get("accuracy_sample"), dict) and r["accuracy_sample"].get("t")})
    gaps = [(a, b) for a, b in zip(stamps, stamps[1:]) if (b - a).total_seconds() >= GAP_INTERVALS * interval_s]
    inside = [sum(1 for s in samples if a < s < b) for a, b in gaps]
    print(f"RESULT {tag}_restart_gaps={len(gaps)} unit=count")
    print(f"RESULT {tag}_gaps_with_samples_inside={sum(1 for n in inside if n)} unit=count")
    print(f"RESULT {tag}_samples_inside_gaps={sum(inside)} unit=count")
    gaps_at_switch = sum(1 for (a, b) in gaps
                         for i in range(len(stamps) - 1) if stamps[i] == a and rows[i].get("version") != rows[i + 1].get("version"))
    print(f"RESULT {tag}_gaps_at_release_switch={gaps_at_switch} unit=count")
    m = bundle.get("manifest") or {}
    print(f"RESULT {tag}_collection_final={int(m.get('final') is True)} unit=bool")
    print(f"RESULT {tag}_manifest_cycles_match={int(m.get('cycles') == len(rows))} unit=bool")
    last = rows[-1].get("version") if rows else None
    print(f"RESULT {tag}_manifest_version_is_last_row_release={int(last == m.get('integration_version'))} unit=bool")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--synthetic", type=Path)
    ap.add_argument("--strip-version", action="store_true")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    if a.synthetic:
        measure("synthetic", a.synthetic, a.strip_version)
    measure("real", a.bundle, a.strip_version)
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
