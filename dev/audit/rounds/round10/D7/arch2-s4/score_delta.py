#!/usr/bin/env python3
"""ARCH2-s4 (round 10, D7): the architecture score's delta for prototype patches against the baseline.

Metric:   delta_S = sum w*log2((base+1)/(proto+1)) over SCORE_METRICS (tools/audit/archscore/score.py),
          the baseline tree against the baseline tree with the named patches applied in order;
          every counter on (ARCHSCORE_ABLATE must be unset); gate-only tripwires reported.
Count key: the static census of the PROTOTYPE TREE's code, so a fix review re-derives it by scoring
          its own head against the same baseline, not by re-applying these patches.
Cells:    this seat's: import_cycle_modules, dead_members, public_unused, coordinator_private_reach
          (module boundaries) and duplication_copies (learner and persistence clone classes).
          bar = 1.5 x 0.515 x sum(w) -- 150 % of wave 1's "every cell cut by 30 %" share.
Instrumented symbols: archscore.vector:measure and archscore.score:delta over the package.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s4/score_delta.py PATCH... [--revert]
          PATCH: P1_one_utc_clock_owner.patch, P2_store_owns_load_prelude.patch,
          P3_one_fabric_interval.patch in this directory; several = their union.
          --on BASEPATCH (absolute path, repeatable) applies a patch to BOTH trees first: the delta
          of these patches on main plus an overlapping wave-1 patch (the brief's second measurement).
Perturbation: --revert applies the patches and then reverses them (git apply -R, last first):
          the tree is the baseline again and delta_S must read 0.0000 with no metric moved.
Expected (baseline 9061fbd3d710, Apple M1, darwin): see REPORT.md's table; exact (static counts).
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
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from archscore import score, vector  # noqa: E402

BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
MY_CELLS = ("import_cycle_modules", "dead_members", "public_unused", "coordinator_private_reach",
            "duplication_copies")


def apply(root: Path, patch: Path, reverse: bool = False) -> None:
    cmd = ["git", "apply", "--include=custom_components/*", "--whitespace=nowarn"]
    if reverse:
        cmd.append("-R")
    subprocess.run([*cmd, str(patch)], cwd=root, check=True)


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        print("ARCHSCORE_ABLATE is set: every counter must be on", file=sys.stderr)
        return 2
    on = [Path(argv[i + 1]) for i, a in enumerate(argv) if a == "--on"]
    names = [a for i, a in enumerate(argv[1:], 1) if not a.startswith("--") and argv[i - 1] != "--on"]
    if not names:
        print(__doc__)
        return 2
    patches = [(HERE / n).resolve() for n in names]
    revert = "--revert" in argv
    t_cpu, t_thr = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch2s4-") as tmp:
        base_dir, proto_dir = Path(tmp) / "base", Path(tmp) / "proto"
        base_dir.mkdir()
        proto_dir.mkdir()
        score.tree_of(BASELINE, base_dir)
        score.tree_of(BASELINE, proto_dir)
        for b in on:
            apply(base_dir, b)
            apply(proto_dir, b)
        for p in patches:
            apply(proto_dir, p)
        if revert:
            for p in reversed(patches):
                apply(proto_dir, p, reverse=True)
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
        print(f"RESULT {m}={b}->{c} count ({tag}) term={d['terms'].get(m, 0.0):+.4f}")
    w = score.weights()
    cells = sum(w[m] for m in MY_CELLS)
    print(f"RESULT cells_sum_w={cells:.4f}")
    print(f"RESULT cells_share_30pct={0.515 * cells:.4f} weighted-log2")
    print(f"RESULT bar_150pct={1.5 * 0.515 * cells:.4f} weighted-log2")
    print(f"RESULT cells_delta_S={sum(d['terms'].get(m, 0.0) for m in MY_CELLS):+.4f} weighted-log2")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (static count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
