#!/usr/bin/env python3
"""D15-s2 harness, D15.M5 (timeline replay): in which clock zone does
``tools/replay/debug_replay.py`` replay a bundle?

``tests/replay.py`` replays each fixture in a child whose ``HASTUB_TZ`` is the
fixture's ``time_zone`` (``child_env``); ``debug_replay.py`` calls
``run_fixture`` in its own process and sets no zone, so the stub's clock
stays UTC whatever zone the install ran in.

Metric (one line): ``differing_cycles`` = replay cycles whose published
records (``tests/replay.py:sweep``'s, every entity's state and attributes,
each ISO instant normalised to UTC so a mere offset spelling never counts;
attributes ending ``_ms``, the run's own wall time, dropped: the --null arm
shows they differ between identical runs)
differ between ``debug_replay.run_seeded`` as shipped (no zone) and the same
call in the lane's environment (``replay.child_env(time_zone)``), over the
window's first ``--hours`` hours. ``published_fields_differing`` counts the
(entity.field) labels behind it.
Count key: the records the production entities publish through ``sweep``;
nothing is read off the bundle.

Run (from the export root):
    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m5_zone.py --bundle B [--hours 4]
    ... --perturb fixed   # perturbation: the shipped arm given HASTUB_TZ=time_zone
                          # (debug_replay's one-line fix) -> differing_cycles 0
    ... --null            # null control: the shipped arm twice -> 0 (replay determinism)
Expected at 92d38ecb: the synthetic bundle (its fixture's time_zone is
Europe/Stockholm too) --hours 4: differing_cycles 8 of 8, --null 0,
--perturb fixed 0. The owner's download is taken at --hours 1 (4 cycles; a
real-bundle cycle costs minutes of CPU on the shared box): differing_cycles > 0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
Privacy: prints counts and entity-field labels of this integration's own
published entities only (the replay half's masked ids), never a value.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
HERE = Path(__file__).resolve()
#: Attributes that measure the run itself (wall time), not the plan: they differ
#: between two identical runs (the --null arm shows it), so they are dropped.
VOLATILE_SUFFIX = "_ms"


def _norm(node):
    if isinstance(node, dict):
        return {str(k): _norm(v) for k, v in node.items()}
    if isinstance(node, (list, tuple)):
        return [_norm(v) for v in node]
    if isinstance(node, float):
        return round(node, 6)
    if isinstance(node, datetime):
        return node.astimezone(timezone.utc).isoformat() if node.tzinfo else node.isoformat()
    if isinstance(node, str) and len(node) >= 19 and node[4:5] == "-" and "T" in node:
        try:
            when = datetime.fromisoformat(node)
        except ValueError:
            return node
        if when.tzinfo is not None:
            return when.astimezone(timezone.utc).isoformat()
    if isinstance(node, (str, int, bool)) or node is None:
        return node
    return str(node)


def child(bundle: Path, hours: float, out: Path) -> int:
    """One arm, in this process: the shipped ``run_seeded`` over the window."""
    for p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
              ROOT / "tools" / "replay"):
        sys.path.insert(0, str(p))
    import debug_ingest
    import debug_replay
    import replay as replay_mod

    b = debug_ingest.load_bundle(bundle)
    doc = b.get("replay") or {}
    start = datetime.fromisoformat(doc["window"]["start"])
    window = debug_replay.trim_replay(doc, start, start + timedelta(hours=hours))
    cycles: list = []
    real_sweep = replay_mod.sweep

    def recording_sweep(entities, action, errors, t):
        records = real_sweep(entities, action, errors, t)
        cycles.append({"t": t.astimezone(timezone.utc).isoformat(),
                       "records": {r["entity_id"]: _norm({"s": r["state"], "a": {
                           k: v for k, v in (r["attributes"] or {}).items()
                           if not str(k).endswith(VOLATILE_SUFFIX)}, "av": r["available"]})
                                   for r in records}})
        return records

    replay_mod.sweep = recording_sweep
    verdict = debug_replay.run_seeded(window, b.get("stores") or None, None)
    out.write_text(json.dumps({"cycles": cycles, "counts": verdict.get("counts")}))
    return 0


def arm(bundle: Path, hours: float, tz: str | None, tmp: Path, name: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k != "HASTUB_TZ"}
    if tz:
        env["HASTUB_TZ"] = tz
    out = tmp / f"{name}.json"
    subprocess.run([sys.executable, str(HERE), "--bundle", str(bundle), "--hours", str(hours),
                    "--child", str(out)], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.loads(out.read_text())


def diff(a: dict, b: dict) -> tuple[int, set[str], int]:
    n = 0
    labels: set[str] = set()
    for ca, cb in zip(a["cycles"], b["cycles"]):
        differs = False
        for ent in set(ca["records"]) | set(cb["records"]):
            ra, rb = ca["records"].get(ent), cb["records"].get(ent)
            if ra == rb:
                continue
            differs = True
            if ra is None or rb is None:
                labels.add(f"{ent}")
                continue
            if ra.get("s") != rb.get("s"):
                labels.add(f"{ent}.state")
            for k in set(ra.get("a") or {}) | set(rb.get("a") or {}):
                if (ra.get("a") or {}).get(k) != (rb.get("a") or {}).get(k):
                    labels.add(f"{ent}.{k}")
        n += differs
    return n, labels, min(len(a["cycles"]), len(b["cycles"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--hours", type=float, default=4.0)
    ap.add_argument("--perturb", default="")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--child", type=Path)
    ap.add_argument("--labels", type=int, default=12)
    a = ap.parse_args(argv)
    if a.child:
        return child(a.bundle, a.hours, a.child)
    began = time.monotonic()
    sys.path.insert(0, str(ROOT / "tools" / "replay"))
    sys.path.insert(0, str(ROOT / "tests" / "hastub"))
    import debug_ingest
    tz = (debug_ingest.load_bundle(a.bundle).get("replay") or {}).get("time_zone") or "UTC"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        shipped = arm(a.bundle, a.hours, tz if a.perturb == "fixed" else None, tmpd, "shipped")
        other = (arm(a.bundle, a.hours, None, tmpd, "again") if a.null
                 else arm(a.bundle, a.hours, tz, tmpd, "lane"))
    n, labels, cycles = diff(shipped, other)
    print(f"RESULT replay_time_zone_is_utc={int(tz == 'UTC')} unit=flag")
    print(f"RESULT compared_cycles={cycles} unit=count")
    print(f"RESULT differing_cycles={n} unit=count")
    print(f"RESULT published_fields_differing={len(labels)} unit=count")
    for label in sorted(labels)[:a.labels]:
        print(f"RESULT field={label}")
    print(f"RESULT shipped_counts={shipped.get('counts')}")
    print(f"RESULT other_counts={other.get('counts')}")
    print(f"RESULT wall_s={time.monotonic() - began:.0f} unit=s provisional=true")
    print("RESULT thread_factor=1.000 unit=ratio (arms run in children; counts only)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
