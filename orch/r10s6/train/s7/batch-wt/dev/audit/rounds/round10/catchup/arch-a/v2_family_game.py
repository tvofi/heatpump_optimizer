#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, D7-arch3-03 / D7-s3-53): the invented-family evasion of
counter C6 on pairs the finder did not choose.

For each of up to N victims (entities whose key-prefix family has >= 3 members, so renaming one
cannot empty it), plant a split by renaming the victim to sort right after an unrelated entity (the first row of a
different family of >= 2 members) in both languages (its en/sv name + " Zeta"), then game it by
homing the victim and that partner into an invented family "qqpair" via ENTITY_FAMILY_OVERRIDES.

Metric: per victim, (plant family_splits, game family_splits, game family_orphan_overrides);
        evaded = plant > 0 and game splits < plant and game C6 == 0.
Count key: victims.
Instrumented symbols: tools/audit/archscore/metrics/family_splits.py:measure,
        tools/audit/archscore/counters.py:family_orphan_overrides.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_family_game.py [N]
          from the root of the tree under test (tools/audit read from it: run it from a tree with
          D7-arch3-03 applied for the perturbation arm).
Null control: the unplanted tree reads family_splits 0 and C6 0 (honest arm).
Expected (d749c986d): evaded == victims tried; with D7-arch3-03: evaded 0.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "tools" / "audit")]
from archscore import counters as K  # noqa: E402
from archscore.metrics import family_splits as F  # noqa: E402

PKG = Path("custom_components") / "heatpump_optimizer"
ANCHOR = "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n"


def build(tmp: Path, name: str, victim: tuple | None, partner: str | None,
          labels: tuple[str, str] = ("Zeta reading", "Zeta avl\u00e4sning")) -> Path:
    t = tmp / name
    shutil.copytree(ROOT / PKG, t / PKG)
    if victim:
        plat, key = victim
        for lang, label in zip(("en", "sv"), labels):
            p = t / PKG / "translations" / f"{lang}.json"
            d = json.loads(p.read_text())
            d["entity"][plat][key]["name"] = label
            p.write_text(json.dumps(d, ensure_ascii=False))
    if partner:
        p = t / PKG / "const.py"
        src = p.read_text()
        assert src.count(ANCHOR) == 1
        src = src.replace(ANCHOR, ANCHOR + f'    "{victim[1]}": "qqpair",\n    "{partner}": "qqpair",\n')
        p.write_text(src)
    return t


def main(argv: list[str]) -> int:
    n = int(argv[1]) if len(argv) > 1 else 4
    t_cpu, th = time.process_time(), time.thread_time()
    rows = F.load_rows(ROOT)
    ov = F.overrides(ROOT)
    fam = {k: ov.get(k, k.split("_")[0]) for _p, k, *_ in rows}
    sizes: dict[str, int] = {}
    for f in fam.values():
        sizes[f] = sizes.get(f, 0) + 1
    victims = [(p, k) for p, k, *_ in rows if sizes[fam[k]] >= 3 and k not in ov][: n * 3 : 3][:n]
    evaded = tried = 0
    with tempfile.TemporaryDirectory(prefix="archa-fam-") as tmp:
        tmp = Path(tmp)
        h = build(tmp, "honest", None, None)
        print(f"RESULT honest family_splits={F.measure(h)['value']} C6={K.family_orphan_overrides(h)} count")
        for i, (plat, key) in enumerate(victims):
            # the partner: an unrelated entity; the victim is renamed to sort right after it in
            # both languages (its name + " Zeta"), which is what makes the pair adjacent
            _pp, partner, pen, psv = next(r for r in rows if fam[r[1]] != fam[key] and r[1] not in ov
                                          and sizes[fam[r[1]]] >= 2)
            labels = (pen + " Zeta", psv + " Zeta")
            plant = build(tmp, f"plant{i}", (plat, key), None, labels)
            game = build(tmp, f"game{i}", (plat, key), partner, labels)
            ps, gs, gc = F.measure(plant)["value"], F.measure(game)["value"], K.family_orphan_overrides(game)
            ev = ps > 0 and gs < ps and gc == 0
            tried += 1
            evaded += ev
            print(f"RESULT victim={plat}.{key} partner={partner} plant_splits={ps} game_splits={gs} "
                  f"game_C6={gc} evaded={ev}")
    print(f"RESULT evaded={evaded} count (of {tried})")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
