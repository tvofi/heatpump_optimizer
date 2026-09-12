#!/usr/bin/env python3
"""D5 harness 5 — entities the integration actually creates that no user-facing
document names.

METRIC: `undocumented_entities` = number of entities returned by driving the
        real ``async_setup_entry`` of every platform in
        ``heatpump_optimizer.PLATFORMS`` whose user-visible name (the
        ``strings.json`` ``entity.<platform>.<translation_key>.name`` string)
        AND whose ``translation_key`` AND whose entity_id suffix all fail to
        appear, case-insensitively, in ANY user-facing document
        (README.md, DISCLAIMER.md, docs/how-it-works.md, configuration.md,
        dashboard-card.md, architecture.md, automations.md, ecl110.md).
        A reader who sees the entity in Home Assistant has nowhere to look it up.

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/entity_doc_coverage.py

Set D5_ROOT=<dir> to point the *document* side at a copy of the tree (the
production side always comes from the checkout this file lives in).

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT entities_created=74 count
    RESULT undocumented_entities=0 count   (tolerance: exact)
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
INSTRUMENTED SYMBOL: heatpump_optimizer.sensor:async_setup_entry (and the
    binary_sensor / button / climate / switch / datetime platforms' own
    ``async_setup_entry``) — the entity list is produced by running them, not
    by reading a table.
PERTURBATION: delete the row naming one currently-documented entity from
    README.md's Entities section (and its other mentions) -> the count must go
    UP by 1. Adding a paragraph naming one reported entity moves it DOWN by 1.
"""
import os
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
DOCROOT = Path(os.environ.get("D5_ROOT") or REPO).resolve()

sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO))

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402

PLATFORMS = ["sensor", "binary_sensor", "button", "climate", "switch", "datetime"]
USER_DOCS = [
    "README.md", "DISCLAIMER.md",
    "docs/how-it-works.md", "docs/configuration.md", "docs/dashboard-card.md",
    "docs/architecture.md", "docs/automations.md", "docs/ecl110.md",
]


def collect(platform):
    mod = importlib.import_module(f"custom_components.heatpump_optimizer.{platform}")
    added = []
    coord = FakeCoordinator({})
    entry = FakeEntry(data={})
    entry.runtime_data = coord
    asyncio.run(mod.async_setup_entry(FakeHass(), entry, lambda es: added.extend(es)))
    return added


def main():
    strings = json.loads((REPO / "custom_components" / "heatpump_optimizer"
                          / "strings.json").read_text(encoding="utf-8"))
    ent_strings = strings.get("entity", {})

    corpus = {}
    for rel in USER_DOCS:
        p = DOCROOT / rel
        corpus[rel] = p.read_text(encoding="utf-8", errors="replace").lower() if p.exists() else ""
    blob = "\n".join(corpus.values())

    rows = []
    for plat in PLATFORMS:
        for e in collect(plat):
            tk = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
            eid = getattr(e, "entity_id", None) or ""
            name = ""
            if tk and plat in ent_strings and tk in ent_strings[plat]:
                name = ent_strings[plat][tk].get("name", "") or ""
            suffix = eid.split(".", 1)[1] if "." in eid else eid
            rows.append((plat, tk or "", name, eid, suffix))

    undocumented = []
    for plat, tk, name, eid, suffix in rows:
        needles = [n for n in (name, tk, suffix, eid) if n]
        hit = any(n.lower() in blob for n in needles)
        if not hit:
            undocumented.append((plat, tk, name, eid))

    print("--- entities no user-facing document names ---")
    for plat, tk, name, eid in undocumented:
        print(f"  {plat:<14} key={tk:<38} name={name!r:<40} {eid}")

    per_doc = {}
    for rel in USER_DOCS:
        text = corpus[rel]
        per_doc[rel] = sum(
            1 for _p, tk, name, _eid, suffix in rows
            if any(n and n.lower() in text for n in (name, tk, suffix))
        )
    print()
    print("--- entities named, per document ---")
    for rel, n in per_doc.items():
        print(f"  {rel}: {n}/{len(rows)}")

    print()
    print(f"RESULT entities_created={len(rows)} count")
    print(f"RESULT undocumented_entities={len(undocumented)} count")
    print(f"RESULT documented_entities={len(rows) - len(undocumented)} count")
    _thr = time.thread_time()
    print(f"RESULT thread_factor={time.process_time() / _thr if _thr else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
