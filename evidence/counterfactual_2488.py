#!/usr/bin/env python3
"""Rebuild the PR body's counterfactual in a TEMP INDEX (never the worktree)
and print the guard's own counts. Variants:
  A: head index, ref_namespaces dropped, the 4 live files restored to base
  B: A + the two record files restored to base and removed from `historical`
  C: B + the `handoff/round9/` entry dropped (map without the move)
"""
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "hpo-seats/r10s3/rev-2488"
BASE = "76bb45628745ff8843f61c1708641f271643a224"
LIVE = ["custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
        "tests/features.py", "tools/audit/seat/handover_prompt.py", "tools/audit/seat/roster_lib.py"]
RECORDS = ["dev/audit/config/bugclasses.json", "dev/programme/plan-2026-09-open-issues.md"]
sys.path.insert(0, str(ROOT / "tests"))
import layout  # noqa: E402


def git(*a, **kw):
    return subprocess.run(["git", *a], cwd=ROOT, check=True, capture_output=True, **kw)


def index_manifest(idx):
    return json.loads(subprocess.run(["git", "show", ":tests/layout.json"], cwd=ROOT,
                                     env={**os.environ, "GIT_INDEX_FILE": str(idx)}, check=True,
                                     capture_output=True).stdout)


def write_manifest(idx, m):
    data = json.dumps(m, indent=1).encode()
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=ROOT, input=data,
                          check=True, capture_output=True).stdout.decode().strip()
    subprocess.run(["git", "update-index", "--cacheinfo", f"100644,{blob},tests/layout.json"],
                   cwd=ROOT, env={**os.environ, "GIT_INDEX_FILE": str(idx)}, check=True)


def build(variant):
    fd, name = tempfile.mkstemp(prefix="hpo-idx-")
    os.close(fd)
    idx = Path(name)
    env = {**os.environ, "GIT_INDEX_FILE": str(idx)}
    subprocess.run(["git", "read-tree", "HEAD"], cwd=ROOT, env=env, check=True)
    m = index_manifest(idx)
    m.pop("ref_namespaces", None)
    if variant in "BC":
        subprocess.run(["git", "restore", "--source=" + BASE, "--staged", "--", *LIVE], cwd=ROOT, env=env, check=True)
    if variant in "BC":
        subprocess.run(["git", "restore", "--source=" + BASE, "--staged", "--", *RECORDS], cwd=ROOT, env=env, check=True)
        m["historical"] = [h for h in m["historical"] if h not in RECORDS]
    if variant == "C":
        m["retired"] = [r for r in m["retired"] if r["old"] != "handoff/round9/"]
    write_manifest(idx, m)
    return idx, m


for variant in "ABC":
    idx, m = build(variant)
    try:
        os.environ["GIT_INDEX_FILE"] = str(idx)
        found = layout.guard(ROOT, m, BASE)
        c = Counter()
        for f in found:
            if "cites handoff/, " in f:
                c["handoff/"] += 1
            elif "cites handoff/round9/, " in f:
                c["handoff/round9/"] += 1
            else:
                c["other"] += 1
        files = {f.split(":")[1] for f in found if "unswept:" in f}
        print(f"RESULT variant {variant}: total={len(found)} {dict(c)} unswept_files={len(files)}")
        for f in found[:4] + found[-2:]:
            print("   ", f[:150])
        landed = layout.landed(layout.tracked(ROOT), m["retired"], m.get("ref_namespaces", ()))
        print("    landed has handoff/:", any(e["old"] == "handoff/" for e in landed),
              "| handoff/round9/:", any(e["old"] == "handoff/round9/" for e in landed))
    finally:
        del os.environ["GIT_INDEX_FILE"]
        idx.unlink(missing_ok=True)
