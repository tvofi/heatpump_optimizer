#!/usr/bin/env python3
"""Round 11 plan (P3): the roster's projection, its hot-file order and its file check, from the tree.

Metric (one line): tools/plan/replan.py's summary.wall_hours for the published roster draft
(.claude/workflows/wave-r11-groups.json) with tools/plan/durations.json. KEY: replan's own plan.json.

Three things, all re-derived on every run and none stored:

  files   every file a finding's `files` field names (../JUDGE-INPUT.json) is in its group's files, or
          in groups.json's `file_exclusions` with the reason it is named and not edited. Exit 1 on a miss.
  wall    replan.py at --coordinator-cap 3 and 2, on two rosters: the PUBLISHED one, and the same roster
          with each comment group's hot-file order written as `after` edges (ORDERED). The comment groups
          carry no edge (ADR-010): their order against the behaviour groups is a file order, which replan
          does not model, so the published figure is the lower bound and the ordered one the upper.
  order   the merge order on every file two or more groups name: the ORDERED cap-3 projection's finish
          order, then start, then roster position. The comment groups are last on every file of their
          glob and are left out of the rows.

Run (from the repository root; a few seconds):
    python3 dev/audit/rounds/round11/PLAN/projection.py            the summary lines
    python3 dev/audit/rounds/round11/PLAN/projection.py --order    and the hot-file order as a table
Writes only under a tempfile root.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
ROSTER = REPO / ".claude" / "workflows" / "wave-r11-groups.json"
PKG = "custom_components/heatpump_optimizer/"
START = "2026-11-18T12:00:00Z"
GLOBS = {"R11-SEAM-comments-production": (PKG + "*.py",), "R11-SEAM-comments-tests": ("tests/*.py",)}


def in_glob(path: str, glob: str) -> bool:
    head = glob[:-len("*.py")]
    return path.startswith(head) and path.endswith(".py") and "/" not in path[len(head):]


def names(group: dict, path: str) -> bool:
    return any(path in (f, f.rstrip("/")) or (f.endswith("/") and path.startswith(f))
               or (f.endswith("*.py") and in_glob(path, f)) for f in group["files"])


def check_files(groups: list[dict]) -> int:
    findings = {f["id"]: f for f in json.loads((HERE.parent / "JUDGE-INPUT.json").read_text())}
    excluded = json.loads((HERE / "groups.json").read_text())["file_exclusions"]
    missing = 0
    for g in groups:
        skip = {(f if f.startswith(("tests/", "tools/", "docs/", "dev/")) else PKG + f)
                for f in excluded.get(g["group"], {})}
        for fid in g["findings"] + list(g["merged"]):
            for path in findings[fid].get("files") or []:
                if path not in skip and not names(g, path):
                    print(f"MISSING {g['group']} {fid} {path}")
                    missing += 1
    print(f"files: {missing} file(s) a finding names that its group neither lists nor excludes")
    return missing


def ordered(roster: dict) -> dict:
    out = copy.deepcopy(roster)
    for g in out["groups"]:
        if g["group"] in GLOBS:
            mine = [f for f in g["files"] if not f.endswith("*.py")]
            g["after"] = sorted(o["group"] for o in roster["groups"] if o["group"] not in GLOBS and any(
                any(in_glob(f, glob) for glob in GLOBS[g["group"]]) or f in mine for f in o["files"]))
    return out


def replan(roster: dict, cap: int, tmp: Path, tag: str) -> dict:
    (tmp / tag).mkdir()
    src, out = tmp / tag / ROSTER.name, tmp / tag / "plan.json"  # replan reads the round from the roster's name
    src.write_text(json.dumps(roster))
    run = subprocess.run([sys.executable, str(REPO / "tools/plan/replan.py"), "--repo", str(REPO),
                          "--roster-file", str(src), "--coordinator-cap", str(cap), "--start", START,
                          "--out", str(out)], capture_output=True, text=True)
    if run.returncode:
        raise SystemExit(run.stdout + run.stderr)
    return json.loads(out.read_text())


def short(name: str) -> str:
    return name[len("R11-SEAM-"):] if name.startswith("R11-SEAM-") else name


def main(argv: list[str]) -> int:
    roster = json.loads(ROSTER.read_text())
    groups = roster["groups"]
    rc = 1 if check_files(groups) else 0
    position = {g["group"]: i for i, g in enumerate(groups)}
    with tempfile.TemporaryDirectory(prefix="r11-projection-") as tmp:
        plans = {}
        for tag, r in (("PUBLISHED", roster), ("ORDERED", ordered(roster))):
            for cap in (3, 2):
                p = plans[tag, cap] = replan(r, cap, Path(tmp), f"{tag}{cap}")
                at_once = sum(1 for g in p["groups"].values() if g["start"] == p["generated"]["start"])
                coord = sum(1 for g in p["groups"].values() if g["coordinator"])
                print(f"wall {tag} cap {cap}: {p['summary']['wall_hours']} h | groups {len(p['groups'])} | "
                      f"start at once {at_once} | coordinator groups {coord} | "
                      f"peak in flight {p['summary']['peak_in_flight']} | "
                      f"critical chain {' > '.join(short(n) for n in p['critical_path'])}")
    plan = plans["ORDERED", 3]["groups"]

    def key(n: str) -> tuple:
        return (plan[n]["finish"], plan[n]["start"], position[n])

    print("order coordinator.py: " + ", ".join(short(n) for n in sorted(
        (g["group"] for g in groups if g["group"] not in GLOBS and names(g, PKG + "coordinator.py")), key=key)))
    if "--order" in argv:
        shared: dict[str, list[str]] = {}
        for g in groups:
            if g["group"] not in GLOBS:
                for f in g["files"]:
                    shared.setdefault(f, []).append(g["group"])
        rows: dict[str, list[str]] = {}
        for f, gs in shared.items():
            if len(gs) > 1:
                rows.setdefault(", ".join(short(n) for n in sorted(gs, key=key)), []).append(
                    f[len(PKG):] if f.startswith(PKG) else f)
        print("| file | order |\n|---|---|")
        for order, files in sorted(rows.items(), key=lambda kv: (-len(kv[0].split(", ")), sorted(kv[1]))):
            print("| " + " ".join(f"`{f}`" for f in sorted(files)) + " | " + order + " |")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
