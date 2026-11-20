#!/usr/bin/env python3
"""Replay main's self-test drift step and split each refusal by whether it can
change `selftest_scope.select` (R11-RCA-SELFTEST-DOMINATED-DRIFT).

    python3 dev/audit/harnesses/r11_selftest_dominated_drift.py REV ARTIFACT [ARTIFACT...]
    python3 dev/audit/harnesses/r11_selftest_dominated_drift.py --self-test

REV's table and workflow against each `selftest-closures` artifact. `select`
consults an entry's `probes` and `dirs` only for an added or deleted path,
where `index` already selects the step, and every list for any change, where
`objects` already selects it. A miss in a list the entry's flags dominate
therefore leaves `select`'s output unchanged for every diff; the rest are the
refusals a selection instrument owes. Prints one line per refusal tagged
`owed` or `dominated`, then the counts.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/ci"))
import selftest_scope as s  # noqa: E402


def dominated_kinds(entry: dict) -> set[str]:
    if entry.get("objects"):
        return {"files", "probes", "dirs"}
    return {"probes", "dirs"} if entry.get("index") else set()


def split(table: dict, measured: dict, steps) -> tuple[list[str], list[str]]:
    refuse, _ = s.drift(table, measured, steps)
    owed, dom = [], []
    for line in refuse:
        parts = line.split()
        if parts[0] == "UNDER-SCOPED" and len(parts) > 4 and parts[3] in ("files", "probes", "dirs"):
            sid, kind = parts[2].rstrip(":"), parts[3]
            if kind in dominated_kinds(table["steps"].get(sid, {})):
                dom.append(line)
                continue
        owed.append(line)
    return owed, dom


def show(rev: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT, text=True)


def entry(files=(), probes=(), dirs=(), index=False, objects=False, sha="x"):
    return {"files": list(files), "probes": list(probes), "dirs": list(dirs),
            "index": index, "objects": objects, "run_sha": sha}


def self_test() -> int:
    """The split against planted tables: a dominated miss is excused, an
    undominated one is still owed, and `select` agrees for every change."""
    class St:
        def __init__(self, i): self.id, self.gated, self.run_sha = i, True, "x"
    steps = [St("walker"), St("lister"), St("indexer")]
    m = {"walker": entry(dirs=["d", "d/new"], objects=True),
         "lister": entry(dirs=["d", "d/new"]),
         "indexer": entry(probes=["d/new/.gitattributes"], files=["f"], index=True)}
    t = {"steps": {"walker": entry(dirs=["d"], objects=True), "lister": entry(dirs=["d"]),
                   "indexer": entry(index=True)}}
    owed, dom = split(t, m, steps)
    ok = True
    for name, cond in (
            ("an objects step's dirs miss is dominated", any("walker" in x for x in dom)),
            ("an unflagged step's dirs miss is owed (the defect still refused)", any("lister" in x for x in owed)),
            ("an index step's probes miss is dominated", any("indexer: probes" in x for x in dom)),
            ("an index step's files miss is owed", any("indexer: files" in x for x in owed))):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        ok &= cond
    fixed = {"steps": {k: {**v, **{kind: m[k][kind] for kind in dominated_kinds(v)}}
                       for k, v in t["steps"].items()}}
    for st in ("A", "D", "M"):
        for p in ("d/new/x.json", "d/new/.gitattributes", "f", "elsewhere/y"):
            sel_t = {i for i in ("walker", "indexer") if _picks(t["steps"][i], st, p)}
            sel_f = {i for i in ("walker", "indexer") if _picks(fixed["steps"][i], st, p)}
            if sel_t != sel_f:
                print(f"  FAIL dominated steps select differently for {st}:{p}")
                ok = False
    print(f"  {'ok  ' if ok else 'FAIL'} select over dominated steps is unchanged by the excused reads")
    return 0 if ok else 1


def _picks(e: dict, st: str, p: str) -> bool:
    """`selftest_scope.select`'s per-step test, verbatim in effect."""
    files, probes, dirs = set(e["files"]), set(e["probes"]), set(e["dirs"])
    if s.covers(files, p) or e.get("objects"):
        return True
    return st in ("A", "D") and (s.covers(probes, p) or bool(e.get("index"))
                                 or any(a in dirs for a in s._ancestors(p)))


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    rev, arts = argv[0], argv[1:]
    table = json.loads(show(rev, s.TABLE))
    steps = s.job_steps(show(rev, s.WORKFLOW))
    for a in arts:
        owed, dom = split(table, json.load(open(a))["steps"], steps)
        for x in owed:
            print(f"owed       {x[:200]}")
        for x in dom:
            print(f"dominated  {x[:200]}")
        print(f"{a}: {len(owed) + len(dom)} refusal(s), {len(owed)} owed, {len(dom)} dominated")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
