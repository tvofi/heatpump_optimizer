#!/usr/bin/env python3
"""D3-s1 M5(d)/(e): can a production (cell-file) edit ever move tests/card_drift.mjs?

Metric (one line): states tests/card_drift.mjs reports as moved (`N state(s)
moved` / `identical in all N states`, plus its exit status), on a payload
tests/plan_view.py writes from a worktree of HEAD, per arm: `base` (no edit),
`prod_small`/`prod_large` (one cell-file line edited so the payload's sha256
differs from base's), `card` (one token of the bundled card's CSS edited).
card_drift renders the working tree's card and HEAD^1's card against ONE shared
payload (tests/card_drift.mjs header), so a production edit, which reaches the
card only through that payload, moves both sides alike.

Instrumented symbol: tests/card_drift.mjs's verdict over tests/plan_view.py's
payload (production `thermal_model.py` line PROD_LINE executed through
plan_view's solve); tests/closures.json's card_drift.mjs closure
(closure.py `_widen` PRODUCERS union) for the edge count.
Perturbation: the `card` arm (one CSS token in
custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js) -> moved
states UP from 0; the `prod_*` arms change the payload sha256 and leave moved
at 0 (the claim). Also prints card.mjs's verdict per arm: a payload reader
that is not differential does see payload changes.

Run (repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_card_drift_payload.py [--select-only]
Writes only under $TMPDIR (own worktree, private HPO_PLANDATA).
Expected: base moved=0, prod_small moved=0 payload_changed=1, prod_large
moved=0 payload_changed=1, card moved>0. Exact counts; seconds provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-m5 (Linux
x86_64, nproc 4, Intel Xeon @ 2.10GHz), alone on the box.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time as _t
_P0, _T0 = _t.process_time(), _t.thread_time()
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
PROD_FILE = PKG + "thermal_model.py"
PROD_OLD = "        new_room = state.room_temperature + dT_room * dt_hours"
CARD_FILE = PKG + "www/heatpump-optimizer-card.js"
CARD_OLD = "      ha-card { padding: 12px 12px 8px 12px; }"
CARD_NEW = "      ha-card { padding: 13px 12px 8px 12px; }"
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]


def edit(path: Path, old: str, new: str) -> str:
    src = path.read_text()
    assert src.count(old + "\n") == 1, (path, old)
    path.write_text(src.replace(old + "\n", new + "\n"))
    return src


def arm(tree: Path, root: Path, name: str) -> dict:
    plan = root / f"plan-{name}.json"
    env = {**os.environ, "PYTHONPATH": "tests/hastub", "HPO_PLANDATA": str(plan)}
    t0 = time.monotonic()
    pv = subprocess.run([sys.executable, "tests/plan_view.py"], cwd=tree, env=env,
                        capture_output=True, text=True, timeout=1200)
    # stdout to a FILE: node's process.exit(1) truncates a piped stdout
    # (measured here: a pipe kept 1 of 44 DRIFT lines, a file all 44).
    with open(root / f"cd-{name}.txt", "w") as fo:
        rc = subprocess.run(["node", "tests/card_drift.mjs", "HEAD^1"], cwd=tree,
                            env=env, stdout=fo, stderr=subprocess.STDOUT,
                            timeout=1200).returncode
    cd = subprocess.CompletedProcess([], rc, (root / f"cd-{name}.txt").read_text(), "")
    cm = subprocess.run(["node", "tests/card.mjs"], cwd=tree, env=env,
                        capture_output=True, text=True, timeout=1200)
    out = cd.stdout
    # card_drift prints `  DRIFT      <state> (unclaimed)` or `  CLAIMED    <state>`
    # per moved state and `  identical  <state>` per unmoved one.
    moved_states = re.findall(r"^  (?:DRIFT|CLAIMED)\s+(\S+)", out, re.M)
    moved = len(moved_states)
    ident = len(re.findall(r"^\s*identical\s", out, re.M))
    cmf = re.search(r"(\d+) CARD CHECK\(S\) FAILED", cm.stdout)
    sha = hashlib.sha256(plan.read_bytes()).hexdigest() if plan.exists() else "none"
    return {"arm": name, "plan_view_rc": pv.returncode, "payload_sha256": sha,
            "card_drift_rc": cd.returncode, "moved": moved, "identical": ident,
            "card_mjs_rc": cm.returncode, "moved_states": moved_states[:6],
            "card_drift_head": out[:400],
            "card_mjs_failed": int(cmf.group(1)) if cmf else 0,
            "wall_s": round(time.monotonic() - t0, 1),
            "card_drift_tail": out[-300:]}


def main() -> int:
    if "--select-only" in sys.argv:
        rows = []
        return report(rows)
    root = Path(tempfile.mkdtemp(prefix="d3s1-carddrift-"))
    tree = root / "tree"
    subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(tree),
                    "HEAD"], cwd=mt.ROOT, check=True)
    rows = []
    try:
        rows.append(arm(tree, root, "base"))
        for name, new in (("prod_small", PROD_OLD + " * 1.0001"),
                          ("prod_large", PROD_OLD + " * 1.5")):
            orig = edit(tree / PROD_FILE, PROD_OLD, new)
            try:
                rows.append(arm(tree, root, name))
            finally:
                (tree / PROD_FILE).write_text(orig)
        orig = edit(tree / CARD_FILE, CARD_OLD, CARD_NEW)
        try:
            rows.append(arm(tree, root, "card"))
        finally:
            (tree / CARD_FILE).write_text(orig)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                       cwd=mt.ROOT, capture_output=True)
        shutil.rmtree(root, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=mt.ROOT, capture_output=True)
    return report(rows)


def report(rows: list) -> int:
    base_sha = rows[0]["payload_sha256"] if rows else ""
    for r in rows:
        r["payload_changed"] = int(r["payload_sha256"] != base_sha)
        print(json.dumps({k: v for k, v in r.items() if k != "card_drift_tail"}))
        print(f"RESULT {r['arm']}_moved={r['moved']}")
        print(f"RESULT {r['arm']}_payload_changed={r['payload_changed']}")
        print(f"RESULT {r['arm']}_card_drift_rc={r['card_drift_rc']}")
        print(f"RESULT {r['arm']}_card_mjs_failed={r['card_mjs_failed']}")
    clos = mt.load_closures().get("tests/card_drift.mjs", [])
    edges = sum(1 for c in CELLS if PKG + c + ".py" in clos)
    print(f"RESULT card_drift_cell_closure_edges={edges}")
    # tests/closure.py:select, the scoped gate's own decision, per one-file
    # cell diff: how many single-cell-file diffs schedule card_drift.mjs.
    import closure  # noqa: E402
    sel = sum(1 for c in CELLS if "tests/card_drift.mjs"
              in closure.select([PKG + c + ".py"])["run"])
    print(f"RESULT cell_diffs_selecting_card_drift={sel}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(_t.process_time() - _P0) / max(_t.thread_time() - _T0, 1e-9):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
