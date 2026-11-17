#!/usr/bin/env python3
"""D15-s1 M4: each store document of a bundle through its loader and the store boundary.

Metric (one line): per store (by its store.DOMAINS name), the stored version against the
version the release constructs it with (refused = differ), whether store._sanitize would
scrub a leaf (quarantines), off_domain's field count, whether its loader ran, and WARNING+
records the load logged. Counts and DOMAINS names only: no entry id, key or value of the
bundle is printed. Never commit a bundle.
Count key: the version QuarantiningStore.__init__ receives from the production constructor;
store.off_domain / store.quarantines over the stored document; loader exceptions caught here.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/store_replay.py --bundle B
        [--synthetic S] [--code-version thermal_learning|ledger]
Expected at the baseline, real bundle (owner's 2026-11-16 download): stores=16,
    loaders_ran=16, refused_versions=0, quarantined=0, off_domain_fields=103 (thermal_learning 1,
    off_restore 1, snapshots 101); synthetic: stores=6, off_domain_fields=192 (accuracy).
Perturbation: --code-version NAME raises, in memory, the production constant the release
    constructs store NAME with (coordinator.THERMAL_LEARNING_STORE_VERSION or
    coordinator.LEDGER_STORE_VERSION) by one -> real_refused_versions 0 -> 1 (up).
Null control: the synthetic bundle (tools/replay/dbg_bundle_gen.py), written by this tree.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: store:QuarantiningStore, store:off_domain, store:quarantines,
    coordinator:HeatPumpOptimizerCoordinator (its store loads), off_restore:_armed_record,
    pump_arbiter:_load, duty_switch:_load, notifier:Notifier.async_load.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import copy
import json
import logging
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
import debug_replay  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import store as S  # noqa: E402


class _Records(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def replay(tag: str, path: Path, bump: str) -> None:
    raw = json.loads(path.read_text())
    data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
    config = dict(data.get("config") or {})
    bundle = copy.deepcopy(debug_ingest.load_bundle(path))
    stored_versions = {S.store_name(k): v for k, v in ((bundle.get("manifest") or {}).get("store_versions") or {}).items()}
    stores = {S.store_name(k): (k, v) for k, v in (bundle.get("stores") or {}).items() if S.store_name(k)}
    from heatpump_optimizer import coordinator as coord_mod
    consts = {"thermal_learning": "THERMAL_LEARNING_STORE_VERSION", "ledger": "LEDGER_STORE_VERSION"}
    saved_const = None
    if bump in consts:
        saved_const = getattr(coord_mod, consts[bump])
        setattr(coord_mod, consts[bump], saved_const + 1)

    # The stub disk holds the version each document was saved at; seed it so.
    from homeassistant.helpers import storage as stub
    made: dict[str, int] = {}
    orig_init = S.QuarantiningStore.__init__

    def init(self, hass, version, key, *a, **k):  # noqa: ANN001
        made.setdefault(S.store_name(key) or key, version)
        return orig_init(self, hass, version, key, *a, **k)

    S.QuarantiningStore.__init__ = init
    stub._DISK.clear()
    debug_replay.seed_stores({k: v for k, v in (bundle.get("stores") or {}).items()})
    handler = _Records()
    pkg = logging.getLogger("heatpump_optimizer")
    pkg.addHandler(handler)
    pkg.setLevel(logging.DEBUG)
    ran: dict[str, bool] = {}
    loaded: dict[str, int] = {}
    try:
        original = debug_replay.enable_store_loads()
        try:
            from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
            coord = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=config))
        finally:
            debug_replay.restore_store_loads(original)
        for name in made:
            ran[name] = True
        loaded["thermal_learning.capacity_envelope"] = len(coord._capacity_envelope)
        loaded["accuracy.samples"] = len(coord.accuracy.samples)

        async def lazy() -> None:
            from heatpump_optimizer import duty_switch, notifier, off_restore, pump_arbiter
            for name, fn in (
                ("off_restore", lambda: off_restore._armed_record(coord.hass, coord.entry)),
                ("pump_duty", lambda: pump_arbiter._load(coord)),
                ("duty_switch", lambda: duty_switch._load(duty_switch.record_for(coord))),
                ("notifier", lambda: notifier.Notifier(coord.hass, coord.entry.entry_id, lambda c: None).async_load()),
            ):
                try:
                    out = await fn()
                    ran[name] = True
                    if name == "off_restore":
                        stored = ((stores.get("off_restore") or (None, {}))[1] or {}).get("armed") or {}
                        loaded["off_restore.armed"] = sum(1 for k, v in stored.items() if out.armed.get(k) == v)
                except Exception as err:  # noqa: BLE001
                    ran[name] = False
                    print(f"RESULT {tag}_loader_error[{name}]={type(err).__name__} unit=class")

        asyncio.run(lazy())
    finally:
        S.QuarantiningStore.__init__ = orig_init
        pkg.removeHandler(handler)
        if saved_const is not None:
            setattr(coord_mod, consts[bump], saved_const)

    warn = [r for r in handler.records if r.levelno >= logging.WARNING]
    totals = {"refused": 0, "quarantined": 0, "off": 0}
    for name in sorted(stores):
        key, doc = stores[name]
        code_v = made.get(name)
        sv = stored_versions.get(name)
        refused = int(code_v is not None and sv is not None and int(sv) != int(code_v))
        q = int(S.quarantines(doc))
        off = len(S.off_domain(key, doc))
        totals["refused"] += refused
        totals["quarantined"] += q
        totals["off"] += off
        print(f"RESULT {tag}_store[{name}] stored_v={sv} code_v={code_v} refused={refused} quarantines={q} "
              f"off_domain={off} loader_ran={int(ran.get(name, False))} unit=row")
    stored_env = len(((stores.get("thermal_learning") or (None, {}))[1] or {}).get("capacity_envelope") or {})
    acc_doc = (stores.get("accuracy") or (None, {}))[1] or {}
    stored_acc = len(((acc_doc.get("accuracy") or {}).get("samples")) or [])
    armed_doc = (stores.get("off_restore") or (None, {}))[1] or {}
    print(f"RESULT {tag}_stores={len(stores)} unit=count")
    print(f"RESULT {tag}_loaders_ran={sum(1 for n in stores if ran.get(n))} unit=count")
    print(f"RESULT {tag}_refused_versions={totals['refused']} unit=count")
    print(f"RESULT {tag}_quarantined={totals['quarantined']} unit=count")
    print(f"RESULT {tag}_off_domain_fields={totals['off']} unit=count")
    print(f"RESULT {tag}_load_warnings={len(warn)} unit=count")
    print(f"RESULT {tag}_capacity_envelope_stored={stored_env} loaded={loaded.get('thermal_learning.capacity_envelope')} unit=buckets")
    print(f"RESULT {tag}_accuracy_samples_stored={stored_acc} loaded={loaded.get('accuracy.samples')} unit=count")
    if "off_restore" in stores:
        print(f"RESULT {tag}_off_restore_armed_stored={len(armed_doc.get('armed') or {})} "
              f"loaded={loaded.get('off_restore.armed')} unit=count")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--synthetic", type=Path)
    ap.add_argument("--code-version", default="", choices=("", "thermal_learning", "ledger"))
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    synth = a.synthetic
    if synth is None:
        out = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, str(ROOT / "tools/replay/dbg_bundle_gen.py"), "--days", "7", "--out", str(out)],
                       check=True, capture_output=True, env=dict(os.environ, PYTHONPATH="tests/hastub:tests"))
        synth = out / "bundle.json"
    replay("synthetic", synth, a.code_version)
    if a.bundle:
        replay("real", a.bundle, a.code_version)
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
