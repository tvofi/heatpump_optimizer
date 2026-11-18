#!/usr/bin/env python3
"""D3-s1 M5 (d)/(e): tests/card_drift.mjs cannot see a cell-file mutation, yet
its measured closure lists 11 of the 12 cell files.

tests/closure.py folds the PRODUCERS edge into the consumer's closure
(`closures[consumer] |= closures[prod]`, "anything that can change the payload
can change what they test"), so card_drift.mjs inherits plan_view.py's 106
files, the cell files among them. card_drift renders the working tree's card
and the ref's card "against the same plan payload" (its own header), so a
change that only moves the payload moves both sides identically.

Metric (one line): of K cell-file mutants that each CHANGE the payload
plan_view.py writes (sha256 of the payload differs from the unmutated tree's),
how many make card_drift.mjs report a moved state or exit non-zero
(`card_drift_red`). Expected 0 of K.
Instrumented symbols: tests/closure.py PRODUCERS fold (closures.json
`tests/card_drift.mjs`), tests/card_drift.mjs's verdict line, the payload
plan_view.py writes (HPO_PLANDATA).
Perturbation (positive control): a one-line edit of the card source itself
(custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js, the
rendered default title "Heat pump plan" -> "Heat-pump plan") must turn card_drift red (direction up: 0 -> 1); the
null control is the unmutated tree, which must stay identical.
Mutants: the tests/mutation_table.py inventory sites in the cell files whose
line plan_view.py's traced baseline executes (state/baselines.json), in file
order, until K payload-moving mutants are found (default K=8, scan cap 200).

Run (seat worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/r2/m5_card_drift_blind.py [--k 8]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64, shared.
Counts are exact; no timing claim.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "dev/audit/rounds/round11/D3/s1")
import mutation_table as mt  # noqa: E402
import prescreen as ps  # noqa: E402

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--cap", type=int, default=200)
    ap.add_argument("--tree", default=str(Path(tempfile.gettempdir()) / "d3s1-workers" / "w9"))
    a = ap.parse_args()
    t = Path(a.tree)
    if not (t / ".git").exists():
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(t), "HEAD"],
                       cwd=mt.ROOT, check=True)
    plan = Path(tempfile.mkdtemp(prefix="d3s1-plan-")) / "plandata.json"
    env = {**os.environ, "PYTHONPATH": "tests/hastub", "HPO_PLANDATA": str(plan)}
    node = shutil.which("node") or "node"

    def payload() -> str | None:
        plan.unlink(missing_ok=True)
        subprocess.run([sys.executable, "tests/plan_view.py"], cwd=t, env=env,
                       capture_output=True, timeout=900)
        return hashlib.sha256(plan.read_bytes()).hexdigest() if plan.exists() else None

    def drift() -> tuple[int, str]:
        p = subprocess.run([node, "tests/card_drift.mjs", "HEAD^1"], cwd=t, env=env,
                           capture_output=True, text=True, timeout=900)
        last = [ln for ln in p.stdout.splitlines() if ln.strip()][-1:] or [""]
        return p.returncode, last[0]

    h0 = payload()
    rc0, line0 = drift()
    print(f"null: payload={h0 and h0[:12]} card_drift rc={rc0} '{line0}'", flush=True)

    clos = mt.load_closures().get("tests/card_drift.mjs", ())
    cells_in = [r for r in ps.RELS if r in clos]
    base = json.loads((ps.STATE / "baselines.json").read_text())
    hits = base["tests/plan_view.py"]["reach"]["hits"]
    inv = mt.inventory(sorted(mt.ROOT / r for r in cells_in))
    cand = [m for m in inv if m["line"] in set(hits.get(m["file"], ()))]
    moved, red, scanned = 0, 0, 0
    rows = []
    for m in cand[: a.cap]:
        if moved >= a.k:
            break
        scanned += 1
        path = t / m["file"]
        orig = path.read_text()
        lines = orig.splitlines(True)
        if lines[m["line"] - 1].rstrip("\n") != m["old"]:
            continue
        lines[m["line"] - 1] = m["new"] + "\n"
        try:
            path.write_text("".join(lines))
            h = payload()
            if h is None or h == h0:
                continue
            moved += 1
            rc, line = drift()
            is_red = rc != 0
            red += is_red
            rows.append((m["anchor"], m["line"], rc, line))
            print(f"MOVED {m['anchor']} L{m['line']} payload={h[:12]} card_drift rc={rc} '{line}'", flush=True)
        finally:
            path.write_text(orig)

    # positive control: edit the card source's first string literal line
    cp = t / CARD
    orig = cp.read_text()
    lines = orig.splitlines(True)
    idx = next(i for i, ln in enumerate(lines) if '"header.default_title": "Heat pump plan"' in ln)
    lines[idx] = lines[idx].replace("Heat pump plan", "Heat-pump plan", 1)
    try:
        cp.write_text("".join(lines))
        payload()
        prc, pline = drift()
    finally:
        cp.write_text(orig)
    print(f"posctl: card source line {idx + 1} edited -> card_drift rc={prc} '{pline}'")
    print(f"RESULT cells_in_card_drift_closure={len(cells_in)}")
    print(f"RESULT scanned={scanned} payload_moving_mutants={moved}")
    print(f"RESULT card_drift_red={red}")
    print(f"RESULT null_card_drift_rc={rc0}")
    print(f"RESULT posctl_card_drift_rc={prc}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
