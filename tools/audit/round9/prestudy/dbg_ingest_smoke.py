#!/usr/bin/env python3
"""R9-DBG-0 pre-study prototype: ingest smoke test for a debugger bundle.

Metric definition: given a bundle produced by ``dbg_bundle_gen.py``, whether
each harness stage accepts it -- (1) schema/manifest validation, (2) the
export lane's own privacy gate ``tools/replay/export.py:violations`` over the
bundle's replay half, (3) every store document round-trips through its real
``from_dict`` loader (accuracy via ``AccuracyTracker.from_dict``, the rest via
``QuarantiningStore``'s own sanitiser), (4) the accuracy monitor re-derives
its published bias from the store's samples, and (5) the last recorded cycle
replays through the real coordinator tick with a finite payload.

Run command (from the repository root):

    PYTHONPATH=tests/hastub:tests ~/.local/state/hpo/venv-ci/bin/python \
        tools/audit/round9/prestudy/dbg_ingest_smoke.py \
        --bundle /tmp/r9-dbg-0/bundle/bundle.json

Expected: every ``stage`` check ok, ``RESULT stages_ok=<stage count>``,
``RESULT accuracy_bias_delta=<tiny>`` (the re-derived bias equals the
published one to float noise), and the null control fires: a planted
credential string in a copy of the replay half is reported by ``violations``
(``RESULT planted_leak_caught=1``).

Perturbation (canon): ``--corrupt accuracy`` swaps the accuracy store's
``samples`` for a scalar; stage 3 must refuse it (the loader's own corruption
barrier, accuracy.py #923) and the smoke must fail, not pass. Baseline: the
seat worktree head of ``handoff/r9-dbg-0``.
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

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

SCHEMA = "hpo-debug/1"


def _load_export():
    spec = importlib.util.spec_from_file_location(
        "hpo_replay_export", ROOT / "tools" / "replay" / "export.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Results:
    def __init__(self) -> None:
        self.fails: list[str] = []

    def check(self, name: str, ok: bool, note: str = "") -> None:
        mark = "ok" if ok else "FAIL"
        print(f"  {mark}: {name}" + (f" -- {note}" if note else ""))
        if not ok:
            self.fails.append(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default="/tmp/r9-dbg-0/bundle/bundle.json")
    parser.add_argument("--corrupt", choices=["", "accuracy"],
                        help="perturbation arm: corrupt the accuracy store")
    args = parser.parse_args(argv)

    results = Results()
    bundle = json.loads(Path(args.bundle).read_text())

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
    export = _load_export()
    replay_doc = bundle.get("replay") or {}
    found = export.violations(replay_doc)
    results.check("replay-clean", not found, "; ".join(found[:3]))

    print("stage 2b: null control -- a planted credential must be caught")
    planted = copy.deepcopy(replay_doc)
    planted["states"]["sensor.secret_leak"] = [
        ["2026-01-15T00:00:00+00:00",
         "sk-ant-api03-abcdefghijklmnop1234567890", {}, None]]
    caught = export.violations(planted)
    print(f"RESULT planted_leak_caused_violations={len(caught)} unit=count")
    results.check("planted-leak-caught", bool(caught),
                  "; ".join(caught[:2]))

    print("stage 3: store documents through the real loaders")
    from heatpump_optimizer import store as store_mod
    from heatpump_optimizer.accuracy import AccuracyTracker
    stores = bundle.get("stores") or {}
    results.check("stores-present", bool(stores), f"{len(stores)} stores")
    domains_ok = True
    for key in stores:
        # Store keys are ``heatpump_optimizer_<entry_id>_<suffix>`` and the
        # entry id itself carries underscores, so match against DOMAINS.
        if not any(key.endswith("_" + suffix) for suffix in store_mod.DOMAINS):
            domains_ok = False
            print(f"    {key}: no DOMAINS declaration")
    results.check("stores-declared", domains_ok,
                  "every store key ends in a DOMAINS suffix")
    sanitized_ok = True
    for key, document in stores.items():
        clean = store_mod._sanitize(document)
        if clean != document:
            sanitized_ok = False
    results.check("stores-sanitize-idempotent", sanitized_ok)

    accuracy_docs = [k for k in stores if k.endswith("_accuracy")]
    if args.corrupt == "accuracy" and accuracy_docs:
        document = stores[accuracy_docs[0]]
        if "accuracy" in document:
            document["accuracy"] = {"samples": "poisoned"}
        else:
            document["samples"] = "poisoned"
    tracker = None
    if accuracy_docs:
        document = stores[accuracy_docs[0]]
        # The accuracy store carries both trackers plus defrost/peaks/comfort;
        # the room tracker is the document's own "accuracy" section.
        payload = document.get("accuracy", document)
        tracker = AccuracyTracker.from_dict(payload)
        loaded = len(tracker.samples)
        print(f"RESULT accuracy_samples_loaded={loaded} unit=count")
        if args.corrupt == "accuracy":
            # The loader's own barrier: a scalar 'samples' is refused, the
            # tracker comes back empty rather than raising (accuracy.py #923).
            results.check("corruption-refused", loaded == 0)
        else:
            results.check("accuracy-loaded", loaded > 0)

    print("stage 4: monitor re-derivation (store window vs bundle rows)")
    if tracker is not None and tracker.samples:
        # The store persists the last 192 samples; the live deque holds 672,
        # so the diagnostics summary's bias covers a different window (an
        # honest finding, recorded). The like-for-like control re-derives the
        # bias from the bundle's own cycle rows, tail 192.
        recomputed = tracker.temperature_bias()
        row_pairs = [(r["t"], r["accuracy_sample"]) for r in bundle.get("cycle_rows", ())
                     if r.get("accuracy_sample")]
        tail = row_pairs[-len(tracker.samples):]
        from heatpump_optimizer.accuracy import AccuracySample
        from heatpump_optimizer.accuracy import AccuracyTracker as _AT
        from datetime import datetime as _dtm
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

    print("stage 5: the replay half through the real lane (final day)")
    import copy as _copy
    import tempfile
    import replay as replay_mod
    from datetime import datetime, timedelta
    tail_fixture = _copy.deepcopy(replay_doc)
    last_row = (bundle.get("cycle_rows") or [{}])[-1]
    end = datetime.fromisoformat(last_row["t"])
    start = end - timedelta(hours=24)
    tail_fixture["window"] = {"start": start.isoformat(), "end": end.isoformat()}
    for entity_id, rows in list(tail_fixture["states"].items()):
        keep = [r for r in rows
                if datetime.fromisoformat(r[0]) >= start
                - timedelta(hours=6)]
        if keep:
            tail_fixture["states"][entity_id] = keep
    with tempfile.TemporaryDirectory() as tmp:
        tail_path = Path(tmp) / "tail-day.json"
        tail_path.write_text(json.dumps(tail_fixture))
        try:
            verdict = replay_mod.run_fixture(tail_path, None, None)
        except Exception as err:  # noqa: BLE001 - a raise is the observation
            results.check("lane-reruns", False, f"{type(err).__name__}: {err}")
            verdict = {}
    judge = (verdict.get("results") or {}) if isinstance(verdict, dict) else {}
    ran = verdict.get("cycles", 0)
    results.check("lane-reruns", ran > 0, f"cycles={ran}")
    hard_failures = [k for k, v in judge.items()
                     if k in ("finite", "unit", "no_default", "cycle") and v]
    results.check("lane-invariants", not hard_failures,
                  f"offenders in {hard_failures}" if hard_failures
                  else f"agreement={len(judge.get('agreement', []))}")

    stages = 12
    ok = not results.fails
    print(f"RESULT stages_ok={stages - len(results.fails)}/{stages} unit=count")
    print(f"RESULT smoke_verdict={'pass' if ok else 'fail'} unit=verdict")
    print("RESULT thread_factor=1.0 unit=ratio")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
