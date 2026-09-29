"""xmodule_duplication: duplicated normalised function bodies ACROSS modules.

``tests/structure.py``'s ``duplication_blocks`` finds maximal runs of >= 10
consecutive normalised lines shared by two functions -- but it hashes
windows per module, so a copy placed in ANOTHER module is invisible (#1738
arm a; m5_dup_control: a 32-line copy into sysid.py left the metric at 14,
the same copy into tariff.py moved it to 16).

Definition. Same normalisation as structure.py (``normalized_function_lines``:
each function's lines stripped, blank and comment-only lines dropped, nested
def/class spans cut out and never bridged), same window (DUP_BLOCK_LINES =
10), same maximal-run merge (``duplicate_runs``) -- with the window digest
table built over the WHOLE package, and a window counted only when the
functions sharing it live in at least two different modules. Headline: the
number of (function, maximal run) rows so produced -- the structure.py row
shape, so a copy of one function into another module adds 2 (the original's
row and the copy's).

Details: the same-module count computed by the identical code path (the
structure.py calibration anchor), the module pairs, and the rows.
"""
from __future__ import annotations

import ast
import hashlib
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

DUP_BLOCK_LINES = 10


def nested_spans(fn) -> list[tuple[int, int]]:
    spans = []
    for child in C.walk(fn):
        if child is fn:
            continue
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            starts = [d.lineno for d in getattr(child, "decorator_list", [])]
            spans.append((min(starts + [child.lineno]), child.end_lineno))
    return spans


def normalized_function_lines(fn, src_lines: list[str]) -> list[tuple[int, str]]:
    excluded = nested_spans(fn)
    out: list[tuple[int, str]] = []
    segment = 0
    for lineno in range(fn.lineno, fn.end_lineno + 1):
        if any(a <= lineno <= b for a, b in excluded):
            segment += 1
            continue
        stripped = src_lines[lineno - 1].strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append((segment, stripped))
    return out


def runs(normalized: dict[tuple, list[tuple[int, str]]], window: int, cross: bool) -> list[tuple]:
    windows: dict[str, list[tuple[tuple, int]]] = defaultdict(list)
    for fid, lines in normalized.items():
        for i in range(len(lines) - window + 1):
            if lines[i][0] != lines[i + window - 1][0]:
                continue
            digest = hashlib.sha1("\n".join(x for _, x in lines[i:i + window]).encode()).hexdigest()
            windows[digest].append((fid, i))
    covered: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
    partners: dict[tuple, set] = defaultdict(set)
    for sites in windows.values():
        owners = {fid for fid, _ in sites}
        if len(owners) < 2:
            continue
        mods = {fid[0] for fid in owners}
        for fid, start in sites:
            others = {o[0] for o in owners if o[0] != fid[0]}
            same = [o for o in owners if o != fid and o[0] == fid[0]]
            if cross and not others:
                continue
            if not cross and not same:
                continue
            covered[fid].append((start, start + window))
            if cross:
                partners[fid] |= others
        del mods
    rows = []
    for fid, spans in covered.items():
        spans.sort()
        merged = []
        a0, b0 = spans[0]
        for a, b in spans[1:]:
            if a <= b0:
                b0 = max(b0, b)
            else:
                merged.append((a0, b0))
                a0, b0 = a, b
        merged.append((a0, b0))
        for a, b in merged:
            rows.append((fid[0], fid[1], fid[2], b - a, tuple(sorted(partners.get(fid, ())))))
    return sorted(rows)


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    normalized = {}
    for m in pkg.mods.values():
        for fn in C.walk(m.tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                normalized[(m.rel.rsplit("/", 1)[-1], fn.name, fn.lineno)] = normalized_function_lines(fn, m.lines)
    cross = runs(normalized, DUP_BLOCK_LINES, cross=True)
    # calibration anchor: structure.py's per-module table
    per_mod: dict[str, dict] = defaultdict(dict)
    for fid, lines in normalized.items():
        per_mod[fid[0]][fid] = lines
    same = sum(len(runs(d, DUP_BLOCK_LINES, cross=False)) for d in per_mod.values())
    pairs: dict[str, int] = defaultdict(int)
    for f, _n, _l, _len, partners in cross:
        for p in partners:
            pairs[" <-> ".join(sorted((f, p)))] += 1
    return {
        "metric": "xmodule_duplication",
        "value": len(cross),
        "details": {
            "window": DUP_BLOCK_LINES,
            "same_module_rows_structure_py_shape": same,
            "module_pairs": dict(sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0]))),
            "rows": [f"{f}:{ln} {n} ({length} lines) ~ {','.join(p)}" for f, n, ln, length, p in cross],
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
