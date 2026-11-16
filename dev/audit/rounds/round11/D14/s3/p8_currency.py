#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): P8 detector -- a published money
unit names the INSTANCE currency while the price feed declares another.

Metric: over a replayed day of ``tests/replay/synthetic-dhw-only.json`` whose
price sensor declares EUR (``unit_of_measurement`` ``EUR/kWh``, attribute
``currency: EUR``) on an instance configured for SEK, the number of distinct
published (entity, field) leaves -- an entity's unit, or any string in its
state or attributes, walked recursively -- that carry the token ``SEK``
(``sek_leaves``), beside those that carry ``EUR`` (``eur_leaves``). The count
key is the value the production entity delivers (its ``native_unit`` and its
published attribute strings, read through ``tests/replay.py:sweep``), never
the fixture's own label.

Arms (each in its own interpreter):
  eur_feed_sek_instance   the defect arm: SEK leaves must be 0 when fixed
  eur_feed_eur_instance   null control: no SEK anywhere to be had -> 0
  sek_feed_sek_instance   the fixture as committed: EUR leaves -> 0
Perturbation (``--perturb``): ``coordinator._feed_currency`` returns None, so
every surface falls back to the instance label -> sek_leaves goes up.
Pre-fix re-find (``--tree`` an export of 3490cb16): sek_leaves > 0.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/p8_currency.py
      ... --tree /tmp/x/3490cb16      ... --perturb
Expected at 92d38ecb6: see REPORT.md (exact counts). Machine: box B7, 4 vCPU.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replaykit  # noqa: E402  (pins BLAS threads first)

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

ARMS = ("eur_feed_sek_instance", "eur_feed_eur_instance", "sek_feed_sek_instance")
TOKEN = {c: re.compile(rf"\b{c}\b") for c in ("SEK", "EUR")}


def leaves(node, path, out):
    if isinstance(node, dict):
        for k, v in node.items():
            leaves(v, f"{path}.{k}", out)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node[:50]):
            leaves(v, f"{path}[]", out)
    elif isinstance(node, str):
        out.append((path, node))


def doc_for(tree: Path, arm: str, hours: float) -> dict:
    src = tree / "tests" / "replay" / "synthetic-dhw-only.json"
    doc = json.loads(src.read_text())
    start = datetime.fromisoformat(doc["window"]["start"])
    doc["window"]["end"] = (start + timedelta(hours=hours)).isoformat()
    if arm.startswith("eur_feed"):
        cfg = {**doc["entry"]["data"], **doc["entry"]["options"]}
        price = cfg.get("price_entity") or doc.get("price_series_entity")
        for row in doc["states"][price]:
            if row[2] is not None:
                row[2] = {**row[2], "unit_of_measurement": "EUR/kWh", "currency": "EUR"}
    return doc


def child(tree: Path, arm: str, perturb: bool, hours: float) -> dict:
    def setup(ctx):
        import harness
        harness.FakeConfig.currency = "EUR" if arm == "eur_feed_eur_instance" else "SEK"
        if perturb:
            from heatpump_optimizer import coordinator as cm
            cm._feed_currency = lambda hass, cfg: None
    out = replaykit.run(tree, doc_for(tree, arm, hours), 30, setup)
    hits = {c: {} for c in TOKEN}
    for recs in out["records"]:
        for r in recs:
            found = []
            if r.get("unit"):
                found.append(("unit", str(r["unit"])))
            leaves(r.get("state"), "state", found)
            leaves(r.get("attributes") or {}, "attr", found)
            for field, text in found:
                for c, rx in TOKEN.items():
                    if rx.search(text):
                        hits[c].setdefault(f"{r['entity_id']} {field}", text[:60])
    return {"arm": arm, "cycles": out["run"]["cycles"], "hits": hits,
            "cycle_offenders": out["run"]["counts"].get("cycle")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=replaykit.ROOT)
    ap.add_argument("--arm", choices=ARMS)
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--hours", type=float, default=3.0)
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    tree = a.tree.resolve()
    if a.child:
        replaykit.emit(child(tree, a.arm, a.perturb, a.hours))
        return 0
    t0 = time.monotonic()
    import concurrent.futures as cf
    arms = [a.arm] if a.arm else list(ARMS)
    extra = (["--perturb"] if a.perturb else []) + ["--hours", str(a.hours)]
    with cf.ThreadPoolExecutor(len(arms)) as ex:
        res = dict(zip(arms, ex.map(lambda arm: replaykit.child(
            Path(__file__).resolve(), tree, ["--arm", arm, *extra]), arms)))
    for arm, d in res.items():
        if d is None:
            print(f"RESULT {arm}_ran=0 count")
            continue
        print(f"arm {arm}: cycles={d['cycles']} cycle_offenders={d['cycle_offenders']}")
        for c in TOKEN:
            for leaf, text in sorted(d["hits"][c].items()):
                print(f"  {c} {leaf} = {text!r}")
            print(f"RESULT {arm}_{c.lower()}_leaves={len(d['hits'][c])} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    replaykit.tail_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())
