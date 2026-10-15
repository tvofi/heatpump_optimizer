#!/usr/bin/env python3
"""Which spellings of "no type" the payload census reads as untyped (R10-ARCHSCORE-COVERAGE, D7-s3-52).

Written by the R10-ARCHSCORE-COVERAGE fixer. The finder's ``payload_any_spellings.py`` (round 10, ARCH-s3)
drives four of the eight spellings the catch-up judge listed; this drives all eight, plus the controls
that DO state a type, the same way: for each spelling S, ``untyped_payload_keys.measure(tree)["value"]``
on a temp copy of the working tree where every field of payload.py's ``EnergyTotals`` (six keys the
census sees) is declared ``S``. A spelling that states no type reads 6; one that states a type reads 0.
The null control switches counter C1b off (``ANY_SPELLINGS = False``, ``ARCHSCORE_ABLATE=C1b``'s
switch): the eight spellings must then read 0 again, and bare ``Any`` still 6.

The second half reads the same spelling rule from the other side (C14, #2293's round-1 review): for each
spelling of ``_fold_away``'s parameter type (``away_mode.AwayState``, with ``None``, in a union of either
order, ``Optional``, ``Annotated``, as a string), how many of the keys ``AwayState.as_dict`` publishes the
payload census sees. Every spelling must read all of them; ``AwayState | int`` (not one class) reads 0, and
with C14 off (``FOLLOW_ANNOTATED = False``) every spelling reads 0.

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


PARAM = {  # the spellings C14 reads as one class, and one it must not
    "plain": "away_mode.AwayState", "or_none": "away_mode.AwayState | None", "none_or": "None | away_mode.AwayState",
    "optional": "Optional[away_mode.AwayState]", "union_none": "Union[away_mode.AwayState, None]",
    "union_none_first": "Union[None, away_mode.AwayState]", "annotated": 'Annotated[away_mode.AwayState, "x"]',
    "string_or_none": '"away_mode.AwayState | None"', "optional_string": 'Optional["away_mode.AwayState"]',
    "control_or_int": "away_mode.AwayState | int",
}
PARAM_AT = "def _fold_away(state: away_mode.AwayState, "


def away_seen(tmp: Path, name: str, spelling: str) -> int:
    dst = tmp / ("p_" + name) / C.PKG_REL
    shutil.copytree(ROOT / C.PKG_REL, dst, ignore=shutil.ignore_patterns("__pycache__"))
    p = dst / "coordinator.py"
    src = p.read_text()
    if src.count(PARAM_AT) != 1:
        raise SystemExit("coordinator.py moved: _fold_away's parameter is not where this harness reads it")
    p.write_text(src.replace(PARAM_AT, f"def _fold_away(state: {spelling}, ")
                 + "\nfrom typing import Annotated, Optional, Union  # noqa: E402,F401\n")
    C.reset_caches()
    pkg = C.load(str(tmp / ("p_" + name)))
    flow = U.Flow(pkg, C.engine(pkg))
    produced = flow.returned_keys(f"{C.COORD_MODULE}:{C.COORD_CLASS}._async_update_data")[0]
    return len(set(flow.returned_keys("away:AwayState.as_dict")[0]) & set(produced))


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
        for name, s in PARAM.items():
            print(f"RESULT away_keys_seen_param_{name}={away_seen(tmp, name, s)} count")
        U.FOLLOW_ANNOTATED = False
        try:
            for name, s in PARAM.items():
                print(f"RESULT null_c14_off_away_keys_seen_param_{name}={away_seen(tmp, 'off_' + name, s)} count")
        finally:
            U.FOLLOW_ANNOTATED = True


if __name__ == "__main__":
    main()
