#!/usr/bin/env python3
"""ARCH-s1 (round 10, D7): the architecture score's delta for one prototype patch.

Metric: delta_S = sum w*log2((base+1)/(proto+1)) over SCORE_METRICS (tools/audit/archscore/score.py),
        the baseline tree against the baseline tree with one committed prototype patch applied;
        every counter on (ARCHSCORE_ABLATE must be unset), gate-only tripwires reported.
Count key: the static census of the PROTOTYPE TREE's code (no runtime value), so a fix review
        re-derives it by scoring its own head against the same baseline, not by re-applying this patch.
Instrumented symbols: archscore.vector:measure and archscore.score:delta over
        coordinator:HeatPumpOptimizerCoordinator and the collaborators the patch touches.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s1/arch1_delta.py PATCH [--revert]
          PATCH is one of P1_live_state_published_whole.patch, P2_away_override_published_whole.patch,
          P3_collaborators_own_their_fields.patch, ALL_P1_P2_P3.patch in this directory.
Perturbation: --revert applies the patch and then reverses it (git apply -R) before measuring:
          the tree is the baseline again and delta_S must be exactly 0 with no metric moved.
Expected (baseline 554e2ecfa7ad, Apple M1, darwin): P1 +6.5186 (footprint +3, alone), P2 +2.3771, P3 +1.5020,
          ALL +11.0039; exact (static counts). --revert: 0.0000 for each.
Root rule: ROOT is resolved from this file (five parents up), and the baseline tree is read from
          git objects at BASELINE, never from the working tree, so the result does not depend on
          which branch is checked out.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from archscore import score, vector  # noqa: E402

BASELINE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
MY_CELLS = ("coord_footprint", "coordinator_multiassigned_attrs", "coordinator_private_reach",
            "hub_solve_writes", "shared_inplace_writes", "params_over_10")


def apply(root: Path, patch: Path, reverse: bool = False) -> None:
    cmd = ["git", "apply", "--include=custom_components/*", "--whitespace=nowarn"]
    if reverse:
        cmd.append("-R")
    subprocess.run([*cmd, str(patch)], cwd=root, check=True)


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        print("ARCHSCORE_ABLATE is set: every counter must be on", file=sys.stderr)
        return 2
    if len(argv) < 2:
        print(__doc__)
        return 2
    patch = (HERE / argv[1]).resolve()
    revert = "--revert" in argv[2:]
    t_cpu, t_thr = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch1-") as tmp:
        base_dir = Path(tmp) / "base"
        proto_dir = Path(tmp) / "proto"
        base_dir.mkdir()
        proto_dir.mkdir()
        score.tree_of(BASELINE, base_dir)
        score.tree_of(BASELINE, proto_dir)
        apply(proto_dir, patch)
        if revert:
            apply(proto_dir, patch, reverse=True)
        base = vector.measure(base_dir)
        proto = vector.measure(proto_dir)
    d = score.delta(base, proto)
    print(score.report(base, proto))
    print(f"RESULT delta_S={d['dS']:+.4f} weighted-log2")
    print(f"RESULT verdict={d['verdict']}")
    print(f"RESULT admissible={d['admissible']}")
    for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY):
        b, c = base.get(m), proto.get(m)
        if b is None or c is None:
            print(f"RESULT {m}=unmeasured")
            continue
        tag = "cell" if m in MY_CELLS else ("tripwire" if m in vector.GATE_ONLY else "other")
        print(f"RESULT {m}_base={b} count")
        print(f"RESULT {m}_proto={c} count")
        print(f"RESULT {m}_term={d['terms'].get(m, 0.0):+.4f} weighted-log2 ({tag})")
    w = score.weights()
    cells = sum(w[m] for m in MY_CELLS)
    mine = sum(d["terms"].get(m, 0.0) for m in MY_CELLS)
    print(f"RESULT cells_sum_w={cells:.4f}")
    print(f"RESULT cells_target_30pct={0.515 * cells:.4f} weighted-log2 (every cell cut by 30%)")
    print(f"RESULT cells_delta_S={mine:+.4f} weighted-log2")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (static count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
