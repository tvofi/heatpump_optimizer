#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, D7-arch3-01 / D7-s3-51 and D7-arch3-02 / D7-s3-52):
the untyped_payload_keys census measured from a different side than the finder's harnesses.

Metric:
  fixture_blind   -- keys of the COMMITTED golden coordinator fixtures' ``data`` (tests/golden/
                     coord_*.json, recorded, not re-run) that the census of _async_update_data does
                     not produce (finder used a live re-capture instead).
  one_away_key    -- headline untyped_payload_keys with ONE AwayView key re-declared Any
                     (finder untyped all ten); control one_energy_key: one EnergyTotals key Any -> 1.
  spelling_<S>    -- headline with EnergyTotals' 6 keys declared in spellings the finder did not
                     try: Union[Any, None], typing.Any, Annotated[Any, ...], Required[Any],
                     "Optional[Any]", Any | int; control Any -> 6, float -> 0.
Count key: payload keys.
Instrumented symbols: tools/audit/archscore/metrics/untyped_payload_keys.py:Flow.returned_keys, is_any, measure.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_payload_census.py
          run from the root of the tree under test (tools/audit is read from it, so the D7-arch3-01/02
          patched census is measured by running it from a tree with those patches applied).
Null control: one_energy_key must read 1 and spelling_Any 6 on every tree, else the arm is dead.
Expected (d749c986d): fixture_blind 10 (the away_* keys), one_away_key 0, spellings other than
          Any/float: 0 except where C1 already parses them; with patches 01+02: fixture_blind 0,
          one_away_key 1, every untyped spelling 6.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "tools" / "audit")]
from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import untyped_payload_keys as U  # noqa: E402

PRODUCER = f"{C.COORD_MODULE}:{C.COORD_CLASS}._async_update_data"
PKG = Path("custom_components") / "heatpump_optimizer"
IMPORTS = ("import typing\nfrom typing import TYPE_CHECKING, Annotated, Any, Optional, Required, "
           "TypedDict, Union\n")
SPELLINGS = {
    "float": "float", "Any": "Any", "Union_Any_None": "Union[Any, None]", "typing_Any": "typing.Any",
    "Annotated_Any": 'Annotated[Any, "free"]', "Required_Any": "Required[Any]",
    "str_Optional_Any": '"Optional[Any]"', "Any_or_int": "Any | int",
}


def tree(tmp: Path, name: str, cls: str, spelling: str, first_only: bool) -> Path:
    t = tmp / name
    shutil.copytree(ROOT / PKG, t / PKG)
    p = t / PKG / "payload.py"
    src = p.read_text()
    m = re.search(rf"class {cls}\(TypedDict, total=False\):\n((?:    .*\n|\n)+?)\n\nclass", src)
    body = m.group(1)
    new = re.sub(r"^(    \w+): .*$", rf"\1: {spelling}", body, count=1 if first_only else 0, flags=re.M)
    src = src.replace(body, new).replace("from typing import TYPE_CHECKING, TypedDict\n", IMPORTS)
    p.write_text(src)
    C.reset_caches()
    return t


def main() -> None:
    t_cpu, th = time.process_time(), time.thread_time()
    C.reset_caches()
    pkg = C.load(str(ROOT))
    keys, _ = U.Flow(pkg, C.engine(pkg)).returned_keys(PRODUCER)
    fixture: set = set()
    for f in sorted((ROOT / "tests" / "golden").glob("coord_*.json")):
        fixture |= set(json.loads(f.read_text())["data"])
    blind = sorted(fixture - set(keys))
    print("fixture_not_census:", blind)
    print(f"RESULT fixture_keys={len(fixture)} count")
    print(f"RESULT fixture_blind={len(blind)} count")
    with tempfile.TemporaryDirectory(prefix="archa-payload-") as tmp:
        tmp = Path(tmp)
        print(f"RESULT one_away_key={U.measure(tree(tmp, 'away1', 'AwayView', 'Any', True))['value']} count")
        print(f"RESULT one_energy_key={U.measure(tree(tmp, 'en1', 'EnergyTotals', 'Any', True))['value']} count")
        for name, sp in SPELLINGS.items():
            v = U.measure(tree(tmp, f"sp_{name}", "EnergyTotals", sp, False))["value"]
            print(f"RESULT spelling_{name}={v} count")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
