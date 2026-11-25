#!/usr/bin/env python3
"""D15-s1 M2: the privacy gate of D15.md step 2, over a synthetic and a real bundle.

Metric (one line): ``replay_doc.violations`` count (via ``tools/replay/export.py``'s
``violations``) over the scope ``--scope`` names, per bundle; plus the LEAK_PROBES
controls green and the planted-credential arms caught. Counts only: no string, key
or value of a bundle is printed. A bundle is a user's private data; never commit one.
Count key: the number of strings ``export.violations`` returns for the scope given.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/privacy_gate.py \
        [--bundle REAL] [--synthetic SYNTH] [--scope whole|debug|replay]
``--synthetic`` omitted: tools/replay/dbg_bundle_gen.py --days 7 is run into a temp dir.
Expected at the baseline (--scope whole, the scope D15.md step 2 names):
    leak_probe_controls_green=46/46, synthetic_violations=72 (+-5, prose varies with
    the fixture), synthetic_replay_violations=0, synthetic_private_hits=0, planted arms 5/5.
    Real bundle (owner's 2026-11-16 download): real_violations=1102 (+-10), real_replay_violations=0,
    real_private_hits=0.
Perturbation: --scope replay (what tools/replay/debug_ingest.py's stage 2 gates) ->
    synthetic_violations and real_violations go to 0 (to_zero), while the planted arms stay caught.
Null control: the synthetic bundle carries no private datum by construction, so every
    violation it raises is a false refusal; private_hits (a credential-named key holding a value
    other than the redaction marker, or a coordinate past the decimal cap) is the true-positive count.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: replay_doc:violations, replay_doc:text_ok (through tools/replay/export.py),
    tests/replay.py:leak_probes.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import copy
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import export  # noqa: E402  tools/replay/export.py
from export import _doc  # noqa: E402  the loaded replay_doc module

PLANT = "sk-ant-api03-abcdefghijklmnop1234567890"
REDACTED = "**REDACTED**"


def load(path: Path) -> tuple[dict, dict]:
    """(whole download, debug bundle)."""
    doc = json.loads(path.read_text())
    data = doc.get("data") if isinstance(doc.get("data"), dict) else doc
    bundle = data.get("debug") if isinstance(data.get("debug"), dict) else data
    return doc, bundle


def scoped(doc: dict, bundle: dict, scope: str) -> object:
    if scope == "replay":
        return bundle.get("replay") or {}
    return bundle if scope == "debug" else doc


def private_hits(node: object, under_secret: bool = False) -> int:
    """True positives: a credential-named key carrying anything but the redaction marker,
    or a coordinate key past the decimal cap."""
    n = 0
    if isinstance(node, dict):
        for k, v in node.items():
            secret = bool(_doc.SECRET_KEY.search(str(k)))
            if secret and not _doc._no_credential(v) and v != REDACTED:
                n += 1
            if _doc._is_coordinate(k):
                places = _doc.json_decimal_places(v)
                if places is not None and places > _doc.MAX_COORDINATE_DECIMALS:
                    n += 1
            n += private_hits(v)
    elif isinstance(node, list):
        n += sum(private_hits(v) for v in node)
    return n


def plant_arms(bundle: dict) -> tuple[int, int]:
    """A credential planted in each section of the bundle: how many the gate catches."""
    arms = 0
    caught = 0
    for section in ("replay", "stores", "payload_snapshots", "cycle_rows", "manifest"):
        if section not in bundle:
            continue
        arms += 1
        b = copy.deepcopy(bundle)
        if section == "replay":
            b["replay"].setdefault("states", {})["sensor.secret_leak"] = [
                ["2026-01-15T00:00:00+00:00", PLANT, {}, None]]
            target = b["replay"]
            base = export.violations(bundle["replay"])
        else:
            node = b[section]
            if isinstance(node, list):
                node.append({"api_key": PLANT})
            else:
                node["zz_planted"] = {"api_key": PLANT}
            target = b
            base = export.violations(bundle)
        caught += int(len(export.violations(target)) > len(base))
    return arms, caught


def leak_controls() -> tuple[int, int]:
    spec = importlib.util.spec_from_file_location("hpo_replay_tests", ROOT / "tests" / "replay.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        res = mod.leak_probes()
    return sum(1 for _n, ok, _d in res if ok), len(res)


def synth_bundle() -> Path:
    out = Path(tempfile.mkdtemp())
    subprocess.run([sys.executable, str(ROOT / "tools/replay/dbg_bundle_gen.py"), "--days", "7", "--out", str(out)],
                   check=True, capture_output=True, env=dict(os.environ, PYTHONPATH="tests/hastub:tests"))
    return out / "bundle.json"


def measure(tag: str, path: Path, scope: str) -> None:
    doc, bundle = load(path)
    conf = export.entry_keys(*export.default_const_paths())
    v = export.violations(scoped(doc, bundle, scope))
    print(f"RESULT {tag}_violations={len(v)} unit=count scope={scope}")
    print(f"RESULT {tag}_replay_violations={len(export.violations(bundle.get('replay') or {}, conf))} unit=count")
    print(f"RESULT {tag}_replay_rows={sum(len(r) for r in (bundle.get('replay') or {}).get('states', {}).values())} unit=count")
    print(f"RESULT {tag}_private_hits={private_hits(scoped(doc, bundle, scope))} unit=count")
    print(f"RESULT {tag}_redaction_markers_refused={_marker_refusals(scoped(doc, bundle, scope))} unit=count")
    arms, caught = plant_arms(bundle)
    print(f"RESULT {tag}_planted_arms_caught={caught}/{arms} unit=count")


def _marker_refusals(node: object) -> int:
    """Leaves equal to Home Assistant's redaction marker that text_ok refuses."""
    if isinstance(node, dict):
        return sum(_marker_refusals(v) for v in node.values())
    if isinstance(node, list):
        return sum(_marker_refusals(v) for v in node)
    return int(node == REDACTED and not _doc.text_ok(node))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--synthetic", type=Path)
    ap.add_argument("--scope", choices=("whole", "debug", "replay"), default="whole")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    green, total = leak_controls()
    print(f"RESULT leak_probe_controls_green={green}/{total} unit=count")
    measure("synthetic", a.synthetic or synth_bundle(), a.scope)
    if a.bundle:
        measure("real", a.bundle, a.scope)
    tc = time.thread_time() - t0
    print(f"RESULT thread_factor={((time.process_time() - c0) / tc) if tc > 0 else 1.0:.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print(f"RESULT swapins={_swapins()} unit=count")
    return 0


def _swapins() -> int:
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        return int(next(l for l in out.splitlines() if l.startswith("Swapins")).split(":")[1].strip(" ."))
    except Exception:  # noqa: BLE001 - Linux has no vm_stat
        try:
            return int(next(l for l in open("/proc/vmstat") if l.startswith("pswpin")).split()[1])
        except Exception:  # noqa: BLE001
            return -1


if __name__ == "__main__":
    sys.exit(main())
