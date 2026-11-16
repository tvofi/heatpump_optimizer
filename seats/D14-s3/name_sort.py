#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): N-name-sort over the PUBLISHED roster.

``tests/entities.py``'s #1760 check sorts the translation-file roster. This
detector sorts what a replayed install actually registers: the entities the
six platforms publish on the replay fixtures (``tests/replay.py:sweep``),
under each shipped language's displayed name (the translation the entity's
``translation_key`` resolves to) and under the entity id, and counts the
declared families (``const.ENTITY_FAMILY_OVERRIDES``, else the key's lead
token -- the same declaration the barrier reads) that sort as more than one
contiguous run.

Metric: split families per (fixture, order), order in {en, sv, de, entity_id};
count key: the published entity's own ``entity_id`` and ``translation_key``.
Perturbation (``--perturb``): the English name of ``learning_observed_cop``
becomes "Observed COP" (the barrier's own null-control rename) -> en splits up.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/name_sort.py
Expected at 92d38ecb6: en/sv/de 0 (exact); entity_id: printed, see REPORT.md.
Machine: box B7, 4 vCPU.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replaykit  # noqa: E402

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

FIXTURES = {"synthetic-dhw-only.json": 1.0, "owner-2026-10-30-away.json": 0.5}
SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})
COLLATE = {"en": lambda n: n.casefold(),
           "sv": lambda n: n.casefold().translate(SV_TAIL),
           "de": lambda n: n.casefold().translate(str.maketrans("äöü", "aou")),
           "entity_id": lambda n: n}


def child(tree: Path, fixture: str) -> dict:
    doc = json.loads((tree / "tests" / "replay" / fixture).read_text())
    start = datetime.fromisoformat(doc["window"]["start"])
    doc["window"]["end"] = (start + timedelta(hours=FIXTURES[fixture])).isoformat()
    out = replaykit.run(tree, doc, 30)
    first = out["records"][0]
    return {"fixture": fixture,
            "roster": sorted({(r["entity_id"], r["key"]) for r in first if r["key"]})}


def runs(order, members):
    pos = [i for i, x in enumerate(order) if x in members]
    return 0 if len(pos) < 2 else 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=replaykit.ROOT)
    ap.add_argument("--fixture")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    tree = a.tree.resolve()
    if a.child:
        replaykit.emit(child(tree, a.fixture))
        return 0
    t0 = time.monotonic()
    replaykit.tree_paths(tree)
    from heatpump_optimizer import const
    pkg = tree / "custom_components" / "heatpump_optimizer"
    tr = {lang: json.loads((pkg / "translations" / f"{lang}.json").read_text())["entity"]
          for lang in ("en", "sv", "de")}
    overrides = getattr(const, "ENTITY_FAMILY_OVERRIDES", {})
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(2) as ex:
        res = list(ex.map(lambda f: replaykit.child(Path(__file__).resolve(), tree,
                                                    ["--fixture", f]), FIXTURES))
    total = 0
    for d in res:
        if d is None:
            print("RESULT ran=0 count")
            continue
        roster = [tuple(x) for x in d["roster"]]
        fam = {}
        for eid, key in roster:
            fam.setdefault(overrides.get(key, key.split("_")[0]), set()).add((eid, key))
        fams = {t: m for t, m in fam.items() if len(m) >= 2}
        print(f"fixture {d['fixture']}: {len(roster)} published keyed entities, "
              f"{len(fams)} families of 2+")
        for order_name, coll in COLLATE.items():
            def name(item):
                eid, key = item
                if order_name == "entity_id":
                    return eid
                plat = eid.split(".")[0]
                n = tr[order_name].get(plat, {}).get(key, {}).get("name") \
                    or tr["en"].get(plat, {}).get(key, {}).get("name") or key
                if a.perturb and order_name == "en" and n == "Learning Observed COP":
                    n = "Observed COP"
                return n
            order = sorted(roster, key=lambda it: coll(name(it)))
            split = {t: runs(order, m) for t, m in fams.items() if runs(order, m) > 1}
            for t, n in sorted(split.items()):
                print(f"  {order_name}: family {t!r} in {n} runs: "
                      f"{sorted(name(x) for x in fams[t])}")
            tag = d["fixture"].split("-")[0]
            print(f"RESULT {tag}_{order_name}_split_families={len(split)} count")
            if order_name != "entity_id":
                total += len(split)
    print(f"RESULT name_split_families_total={total} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    replaykit.tail_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())
