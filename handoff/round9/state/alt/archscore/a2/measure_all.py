#!/usr/bin/env python3
"""Reproduce corpus.tsv: every labelled commit measured at its first parent and at itself.

    python3 measure_all.py [--repo /home/user/heatpump_optimizer] [--force]

Reads labels.tsv (hand-labelled from metric-independent sources, quoted there). For each
row: checks the commit is an ancestor of origin/main, finds the first-parent main commit
that carried it, checks out <sha>^1 into wt-before and <sha> into wt-after (two detached
worktrees owned by this directory, created if missing), runs measure_one.py (the CURRENT
tests/structure.py at 7952d8f9 + the m1/m2/m3 enumerators) on each, caches the JSON in
results/<sha>.json, and writes corpus.tsv with after - before deltas. Worktrees are
removed at the end unless --keep.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

STRUCT = [
    "classes_over_300", "attrbag_classes_over_30", "methods_over_200", "methods_over_150",
    "max_class_loc", "max_method_loc", "max_cc", "coordinator_loc", "coordinator_methods",
    "coordinator_attrs", "coordinator_multiassigned_attrs", "duplication_blocks",
    "functions_cc_over_25", "functions_cc_over_15", "const_modules_over_50", "local_imports",
    "dead_top_level_symbols", "dead_methods", "internal_call_edges", "cross_seam_edges",
    "cut_dhw", "cut_learning", "cut_fetch", "cut_grid", "cut_views",
]
ENUM = ["m1_solve_sites", "m1_solve_fields", "m1_coord_sites", "m1_coord_fields", "m1_pkg_sites",
        "m2_keys_read", "m2_read_sites", "m2_unproduced",
        "m3_reaches", "m3_members", "m3_files", "m3_writes"]
NULL = ["null_pkg_loc"]
ALL = STRUCT + ENUM + NULL


def git(repo, *args, cwd=None):
    return subprocess.run(["git", "-C", str(cwd or repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def ensure_wt(repo: str, path: Path, sha: str) -> None:
    if not path.exists():
        git(repo, "worktree", "add", "--detach", str(path), sha)
    else:
        git(repo, "checkout", "-q", "--detach", "--force", sha, cwd=path)
        git(repo, "clean", "-qfdx", cwd=path)


def measure(tree: Path) -> dict:
    out = subprocess.run([sys.executable, str(HERE / "measure_one.py"), str(tree)],
                         capture_output=True, text=True)
    if out.returncode:
        return {"_measure_one_error": out.stderr[-500:]}
    return json.loads(out.stdout)


def carried_by(repo: str, sha: str) -> str:
    """The oldest first-parent main commit that contains ``sha``."""
    full = git(repo, "rev-parse", sha)
    fp = git(repo, "rev-list", "--first-parent", "--reverse", "origin/main").split()
    if full in fp:
        return full[:8]
    # binary search: containment is monotone along the first-parent chain
    lo, hi = 0, len(fp) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", full, fp[mid]]).returncode == 0:
            hi = mid
        else:
            lo = mid + 1
    return fp[lo][:8]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/home/user/heatpump_optimizer")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    rows = list(csv.DictReader(open(HERE / "labels.tsv"), delimiter="\t"))
    wb, wa = HERE / "wt-before", HERE / "wt-after"
    out_rows = []
    for r in rows:
        sha = git(a.repo, "rev-parse", r["sha"])
        if subprocess.run(["git", "-C", a.repo, "merge-base", "--is-ancestor", sha, "origin/main"]).returncode:
            print(f"SKIP {r['sha']}: not on origin/main", file=sys.stderr)
            continue
        parent = git(a.repo, "rev-parse", f"{sha}^1")
        cache = RESULTS / f"{sha[:12]}.json"
        if cache.exists() and not a.force:
            res = json.loads(cache.read_text())
        else:
            ensure_wt(a.repo, wb, parent)
            ensure_wt(a.repo, wa, sha)
            res = {"before": measure(wb), "after": measure(wa)}
            cache.write_text(json.dumps(res, indent=1, sort_keys=True))
        b, af = res["before"], res["after"]
        date = git(a.repo, "log", "-1", "--format=%ad", "--date=short", sha)
        row = {
            "sha": sha[:8], "parent": parent[:8], "carried_by": carried_by(a.repo, sha), "date": date,
            "pr": r["pr"], "label": r["label"], "circ": r["circ"], "class": r["class"],
            "description": r["description"], "label_source": r["label_source"],
        }
        errs = []
        for side, d in (("before", b), ("after", af)):
            for k, v in d.items():
                if k.endswith("_error"):
                    errs.append(f"{side}:{k}={v}")
        row["measure_errors"] = " | ".join(errs)
        row["seam_fallback_b/a"] = f"{b.get('_seam_fallback')}/{af.get('_seam_fallback')}"
        for k in ALL:
            vb, va = b.get(k), af.get(k)
            row[f"d_{k}"] = "NA" if vb is None or va is None else round(va - vb, 4)
        for k in ("coordinator_loc", "null_pkg_loc", "m1_solve_sites", "m3_reaches"):
            row[f"abs_{k}_b/a"] = f"{b.get(k)}/{af.get(k)}"
        out_rows.append(row)
        print(f"{row['label']:7s} {row['sha']} {row['date']} errs={bool(errs)}", file=sys.stderr)
    with open(HERE / "corpus.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(out_rows)
    if not a.keep:
        for p in (wb, wa):
            if p.exists():
                git(a.repo, "worktree", "remove", "--force", str(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
