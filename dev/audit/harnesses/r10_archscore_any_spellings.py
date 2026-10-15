#!/usr/bin/env python3
"""Which spellings of "no type" the payload census reads as untyped (R10-ARCHSCORE-COVERAGE, D7-s3-52).

Written by the R10-ARCHSCORE-COVERAGE fixer. The finder's ``payload_any_spellings.py`` (round 10, ARCH-s3)
drives four of the eight spellings the catch-up judge listed; this drives all eight, plus the controls
that DO state a type, the same way: for each spelling S, ``untyped_payload_keys.measure(tree)["value"]``
on a temp copy of the working tree where every field of payload.py's ``EnergyTotals`` (six keys the
census sees) is declared ``S``. A spelling that states no type reads 6; one that states a type reads 0.
The null control switches counter C1b off (``ANY_SPELLINGS = False``, ``ARCHSCORE_ABLATE=C1b``'s
switch): the eight spellings must then read 0 again, and bare ``Any`` still 6.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_archscore_any_spellings.py

Root: the working directory; the tree is copied to a private temp dir, never edited in place.
Instrumented: ``tools/audit/archscore/metrics/untyped_payload_keys.py`` (``is_any``, ``any_aliases``).
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tools" / "audit")]
from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import untyped_payload_keys as U  # noqa: E402

UNTYPED = {  # the catch-up judge's eight (CATCHUP-JUDGE.json, D7-arch3-02), and a TypeAlias of one
    "any_or_none": "Any | None", "optional_any": "Optional[Any]", "string_any": '"Any"',
    "alias_any": "_Untyped", "union_any_none": "Union[Any, None]", "annotated_any": 'Annotated[Any, "k"]',
    "string_optional_any": '"Optional[Any]"', "any_or_int": "Any | int", "typealias_any": "_UntypedAlias",
}
TYPED = {"float": "float", "float_or_none": "float | None", "optional_float": "Optional[float]",
         "string_float": '"float"', "annotated_float": 'Annotated[float, "k"]', "dict_of_any": "dict[str, Any]"}
IMPORTS = ("from typing import TYPE_CHECKING, Annotated, Any, Optional, TypeAlias, TypedDict, Union\n"
           "_Untyped = Any\n_UntypedAlias: TypeAlias = Optional[_Untyped]\n")


def headline(tmp: Path, name: str, spelling: str) -> int:
    dst = tmp / name / C.PKG_REL
    shutil.copytree(ROOT / C.PKG_REL, dst, ignore=shutil.ignore_patterns("__pycache__"))
    p = dst / "payload.py"
    src = p.read_text()
    m = re.search(r"class EnergyTotals\(TypedDict, total=False\):\n((?:    .*\n)+)", src)
    anchor = "from typing import TYPE_CHECKING, TypedDict\n"
    if m is None or src.count(anchor) != 1:
        raise SystemExit("payload.py moved: EnergyTotals or its typing import is not where this harness reads it")
    src = src.replace(m.group(1), re.sub(r"^(    \w+): .*$", rf"\1: {spelling}", m.group(1), flags=re.M))
    p.write_text(src.replace(anchor, IMPORTS))
    C.reset_caches()
    return U.measure(tmp / name)["value"]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="r10-any-") as tmp:
        tmp = Path(tmp)
        C.reset_caches()
        print(f"RESULT baseline_headline={U.measure(ROOT)['value']} count")
        print(f"RESULT untyped_with_bare_any={headline(tmp, 'bare', 'Any')} count")
        for name, s in {**UNTYPED, **TYPED}.items():
            print(f"RESULT untyped_with_{name}={headline(tmp, name, s)} count")
        U.ANY_SPELLINGS = False
        try:
            print(f"RESULT null_c1b_off_bare_any={headline(tmp, 'off_bare', 'Any')} count")
            for name, s in UNTYPED.items():
                print(f"RESULT null_c1b_off_{name}={headline(tmp, 'off_' + name, s)} count")
        finally:
            U.ANY_SPELLINGS = True


if __name__ == "__main__":
    main()
