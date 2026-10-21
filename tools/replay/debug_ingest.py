#!/usr/bin/env python3
"""Ingest and validate an ``hpo-debug/1`` debugger bundle.

Generalises the R9-DBG-0 smoke (``dbg_ingest_smoke.py`` at ``eae236d66``):
schema and manifest, ``export.violations`` over the replay half with a
planted-credential null control, every store document through
``store._sanitize`` and ``AccuracyTracker.from_dict``, and the accuracy
monitor re-derived from the store window vs the bundle's own cycle rows.

    PYTHONPATH=tests/hastub:tests python3 tools/replay/debug_ingest.py --bundle B.json
    PYTHONPATH=tests/hastub:tests python3 tools/replay/debug_ingest.py --bundle B.json --corrupt accuracy
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", HERE):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

SCHEMA = "hpo-debug/1"
PLANTED_SECRET = "sk-ant-api03-abcdefghijklmnop1234567890"


def load_export():
    spec = importlib.util.spec_from_file_location(
        "hpo_replay_export", HERE / "export.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_bundle(path: Path) -> dict:
    raw = path.read_bytes()
    if path.suffix == ".gz" or raw[:2] == b"\x1f\x8b":
        import gzip
        raw = gzip.decompress(raw)
    return json.loads(raw)


def domain_suffix(key: str, domains) -> str | None:
    """Longest ``DOMAINS`` suffix of a store key (entry ids carry underscores)."""
    hits = [s for s in domains if key.endswith("_" + s)]
    return max(hits, key=len) if hits else None


class Results:
    def __init__(self) -> None:
        self.fails: list[str] = []

    def check(self, name: str, ok: bool, note: str = "") -> None:
        mark = "ok" if ok else "FAIL"
        print(f"  {mark}: {name}" + (f" -- {note}" if note else ""))
        if not ok:
            self.fails.append(name)


def ingest(bundle: dict, *, corrupt: str = "") -> Results:
    results = Results()
    print("stage 1: schema and manifest")
    results.check("schema", bundle.get("schema") == SCHEMA,
                  f"schema={bundle.get('schema')!r}")
    manifest = bundle.get("manifest") or {}
    results.check("manifest-cycles", isinstance(manifest.get("cycles"), int)
                  and manifest["cycles"] > 0)
    results.check("manifest-version", bool(manifest.get("integration_version")))
    results.check("rows-match", len(bundle.get("cycle_rows") or [])
                  == manifest.get("cycles"))

    print("stage 2: privacy gate over the replay half (export.violations)")
    export = load_export()
    replay_doc = bundle.get("replay") or {}
    found = export.violations(replay_doc)
    results.check("replay-clean", not found, "; ".join(found[:3]))

    print("stage 2b: null control -- a planted credential must be caught")
    planted = copy.deepcopy(replay_doc)
    planted.setdefault("states", {})["sensor.secret_leak"] = [
        ["2026-01-15T00:00:00+00:00", PLANTED_SECRET, {}, None]]
    caught = export.violations(planted)
    print(f"RESULT planted_leak_caused_violations={len(caught)} unit=count")
    results.check("planted-leak-caught", bool(caught), "; ".join(caught[:2]))

    print("stage 3: store documents through the real loaders")
    from heatpump_optimizer import store as store_mod
    from heatpump_optimizer.accuracy import AccuracyTracker
    stores = copy.deepcopy(bundle.get("stores") or {})
    results.check("stores-present", bool(stores), f"{len(stores)} stores")
    undeclared = [k for k in stores if domain_suffix(k, store_mod.DOMAINS) is None]
    results.check("stores-declared", not undeclared, ",".join(undeclared[:3]))
    dirty = [k for k, document in stores.items()
             if store_mod._sanitize(document) != document]
    results.check("stores-sanitize-idempotent", not dirty, ",".join(dirty[:3]))

    accuracy_docs = [k for k in stores if k.endswith("_accuracy")]
    if corrupt == "accuracy" and accuracy_docs:
        document = stores[accuracy_docs[0]]
        if "accuracy" in document:
            document["accuracy"] = {"samples": "poisoned"}
        else:
            document["samples"] = "poisoned"
    tracker = None
    if accuracy_docs:
        document = stores[accuracy_docs[0]]
        payload = document.get("accuracy", document)
        tracker = AccuracyTracker.from_dict(payload)
        loaded = len(tracker.samples)
        print(f"RESULT accuracy_samples_loaded={loaded} unit=count")
        if corrupt == "accuracy":
            results.check("corruption-refused", loaded == 0)
        else:
            results.check("accuracy-loaded", loaded > 0)

    print("stage 4: monitor re-derivation (store window vs bundle rows)")
    if tracker is not None and tracker.samples:
        from datetime import datetime as _dtm
        from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker as _AT
        recomputed = tracker.temperature_bias()
        row_pairs = [(r["t"], r["accuracy_sample"]) for r in bundle.get("cycle_rows", ())
                     if r.get("accuracy_sample")]
        tail = row_pairs[-len(tracker.samples):]
        row_tracker = _AT()
        for when, sample in tail:
            row_tracker.samples.append(AccuracySample(
                when=_dtm.fromisoformat(when),
                predicted_temp=sample.get("predicted_temp"),
                actual_temp=sample.get("actual_temp"),
                predicted_power_kw=sample.get("predicted_power_kw"),
                actual_power_kw=sample.get("actual_power_kw"),
                outdoor_temp=sample.get("outdoor_temp"),
            ))
        row_bias = row_tracker.temperature_bias()
        published = ((bundle.get("diagnostics") or {}).get("accuracy")
                     or {}).get("temperature_bias")
        delta = (abs(recomputed - row_bias)
                 if recomputed is not None and row_bias is not None else None)
        print(f"RESULT store_window_bias={recomputed} unit=celsius")
        print(f"RESULT rows_window_bias={row_bias} unit=celsius")
        print(f"RESULT live_deque_bias={published} unit=celsius")
        print(f"RESULT accuracy_bias_delta={delta} unit=celsius")
        results.check("bias-rederived",
                      delta is not None and delta < 0.05,
                      f"store={recomputed} rows={row_bias} live-deque={published}")
    else:
        results.check("bias-rederived", False, "no accuracy samples to re-derive")
    return results


def _mini_bundle() -> dict:
    """A cheap bundle the gate can ingest: committed replay fixture plus one sample."""
    replay = json.loads((ROOT / "tests" / "replay" / "synthetic-dhw-only.json").read_text())
    sample = {
        "t": "2026-01-15T12:00:00+00:00",
        "predicted_temp": 20.0, "actual_temp": 20.1,
        "predicted_power_kw": 1.0, "actual_power_kw": 1.0,
        "outdoor_temp": -5.0,
    }
    return {
        "schema": SCHEMA,
        "manifest": {"cycles": 1, "integration_version": "gate", "days": 1},
        "replay": replay,
        "cycle_rows": [{"t": sample["t"], "accuracy_sample": {
            k: sample[k] for k in sample if k != "t"}}],
        "payload_snapshots": [],
        "stores": {"heatpump_optimizer_foreign_accuracy": {"accuracy": {
            "samples": [sample]}}},
        "store_save_counts": {},
        "diagnostics": {"accuracy": {"temperature_bias": -0.1}},
    }


def gate_checks() -> list[tuple[str, bool, str]]:
    """Cheap ingest arms for ``tests/entities.py``; no coordinator tick."""
    import io
    from contextlib import redirect_stdout
    bundle = _mini_bundle()
    buf = io.StringIO()
    with redirect_stdout(buf):
        clean = ingest(bundle)
        poisoned = ingest(copy.deepcopy(bundle), corrupt="accuracy")
    leaked = "planted-leak-caught" not in clean.fails
    return [
        ("debug ingest: schema, stores, accuracy, bias, planted leak",
         not clean.fails, ",".join(clean.fails)),
        ("debug ingest: --corrupt accuracy is refused by the loader",
         "corruption-refused" not in poisoned.fails
         and "accuracy-loaded" not in poisoned.fails,
         ",".join(poisoned.fails)),
        ("debug ingest: planted credential is the null control",
         leaked, buf.getvalue()[-200:]),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--corrupt", choices=["", "accuracy"], default="")
    args = parser.parse_args(argv)
    results = ingest(load_bundle(args.bundle), corrupt=args.corrupt)
    ok = not results.fails
    print(f"RESULT stages_ok={12 - len(results.fails)}/12 unit=count")
    print(f"RESULT smoke_verdict={'pass' if ok else 'fail'} unit=verdict")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
