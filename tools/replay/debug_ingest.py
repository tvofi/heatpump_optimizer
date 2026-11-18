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


def read_download(path: Path) -> dict:
    """The file as handed, gunzipped and parsed, with any wrapper intact: the
    reader for a harness that measures the wrapper itself."""
    raw = path.read_bytes()
    if path.suffix == ".gz" or raw[:2] == b"\x1f\x8b":
        import gzip
        raw = gzip.decompress(raw)
    return json.loads(raw)


def load_bundle(path: Path) -> dict:
    return unwrap_download(read_download(path))


def unwrap_download(doc: dict) -> dict:
    """The bundle itself: Home Assistant's "Download diagnostics" file nests it
    under ``data.debug``; a bare bundle (it carries its own ``schema``) is
    returned as it is."""
    if isinstance(doc, dict) and "schema" not in doc:
        inner = (doc.get("data") or {}).get("debug") if isinstance(
            doc.get("data"), dict) else None
        if isinstance(inner, dict):
            return inner
    return doc


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
    undeclared = [k for k in stores if store_mod.store_name(k) is None]
    results.check("stores-declared", not undeclared, ",".join(undeclared[:3]))
    dirty = [k for k, document in stores.items()
             if store_mod.quarantines(document)]
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
        from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker as _AT
        # The store holds the tracker's window; the rows hold one sample per
        # cycle, and the tracker may sample less often than cycles run, so a
        # sample repeats across rows. Compare the samples both sides hold,
        # each counted once, keyed by the sample's own time.
        by_time = {}
        for row in bundle.get("cycle_rows", ()):
            sample = row.get("accuracy_sample")
            if sample:
                parsed = AccuracySample.from_dict(
                    {**sample, "t": sample.get("t") or row.get("t")})
                if parsed is not None:
                    by_time.setdefault(parsed.when, parsed)
        held = {s.when: s for s in tracker.samples}
        shared = sorted(set(held) & set(by_time))
        store_tracker, row_tracker = _AT(), _AT()
        store_tracker.samples.extend(held[w] for w in shared)
        row_tracker.samples.extend(by_time[w] for w in shared)
        print(f"RESULT store_window_samples={len(held)} unit=count")
        print(f"RESULT rows_distinct_samples={len(by_time)} unit=count")
        print(f"RESULT shared_samples={len(shared)} unit=count")
        recomputed = store_tracker.temperature_bias()
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
                      f"store={recomputed} rows={row_bias} live-deque={published} "
                      f"shared={len(shared)}/{len(held)}")
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


def _download(bundle: dict) -> dict:
    """The "Download diagnostics" file as Home Assistant writes it: the
    debugger bundle sits under ``data.debug`` beside the entry's own sections."""
    return {"home_assistant": {"version": "gate"}, "data": {"debug": bundle}}


def _tail_repeat_bundle(*, tamper: bool = False, disjoint: bool = False) -> dict:
    """Four store samples, rows covering the newest two and repeating the
    newest across the tail -- the shape a live bundle has when the tracker
    stops sampling while cycle rows continue."""
    base = _mini_bundle()
    stamps = [f"2026-01-15T1{n}:00:00+00:00" for n in range(4)]
    temps = [(20.0, 20.4), (20.0, 19.0), (20.0, 20.1), (20.0, 20.2)]
    samples = [{"t": t, "predicted_temp": p, "actual_temp": a,
                "predicted_power_kw": 1.0, "actual_power_kw": 1.0,
                "outdoor_temp": -5.0} for t, (p, a) in zip(stamps, temps)]
    seq = [samples[2], samples[3], samples[3], samples[3]]
    rows = [{"t": f"2026-01-15T2{n}:00:00+00:00",
             "accuracy_sample": copy.deepcopy(s)} for n, s in enumerate(seq)]
    if tamper:
        rows[1]["accuracy_sample"]["actual_temp"] = 25.0
        rows[2]["accuracy_sample"]["actual_temp"] = 25.0
    if disjoint:
        for row in rows:
            row["accuracy_sample"]["t"] = "2026-02-01T00:00:00+00:00"
    base["manifest"]["cycles"] = len(rows)
    base["cycle_rows"] = rows
    base["stores"] = {"heatpump_optimizer_foreign_accuracy": {"accuracy": {
        "samples": samples}}}
    base["diagnostics"] = {"accuracy": {"temperature_bias": 0.0}}
    return base


def _quiet_ingest(bundle: dict, **kw) -> Results:
    import io
    from contextlib import redirect_stdout
    with redirect_stdout(io.StringIO()):
        return ingest(bundle, **kw)


def _via_file(doc: dict, reader=None) -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "download.json"
        path.write_text(json.dumps(doc))
        return (reader or load_bundle)(path)


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
    download = _download(bundle)
    as_handed = _via_file(download, read_download)
    wrapped = _quiet_ingest(_via_file(download))
    repeat = _quiet_ingest(_tail_repeat_bundle())
    tampered = _quiet_ingest(_tail_repeat_bundle(tamper=True))
    disjoint = _quiet_ingest(_tail_repeat_bundle(disjoint=True))
    return [
        ("debug ingest: schema, stores, accuracy, bias, planted leak",
         not clean.fails, ",".join(clean.fails)),
        ("debug ingest: --corrupt accuracy is refused by the loader",
         "corruption-refused" not in poisoned.fails
         and "accuracy-loaded" not in poisoned.fails,
         ",".join(poisoned.fails)),
        ("debug ingest: planted credential is the null control",
         leaked, buf.getvalue()[-200:]),
        ("debug ingest: a download wrapped as HA writes it ingests like the bare bundle",
         not wrapped.fails, ",".join(wrapped.fails)),
        ("debug ingest: read_download keeps the wrapper the harnesses measure",
         as_handed == download, ",".join(sorted(as_handed))),
        ("debug ingest: rows repeating the newest sample and covering half the store re-derive the bias",
         not repeat.fails, ",".join(repeat.fails)),
        ("debug ingest: a shared sample whose row disagrees with the store still fails bias-rederived",
         "bias-rederived" in tampered.fails, ",".join(tampered.fails)),
        ("debug ingest: rows sharing no sample with the store fail bias-rederived (not vacuous)",
         "bias-rederived" in disjoint.fails, ",".join(disjoint.fails)),
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
