#!/usr/bin/env python3
"""ARCH3-s6 (round 10, D7): the architecture score's delta for this seat's prototype patches.

Metric:   delta_S = sum w*log2((base+1)/(proto+1)) over SCORE_METRICS (tools/audit/archscore/score.py),
          the baseline tree against the baseline tree with the named patches applied in order;
          every counter on (ARCHSCORE_ABLATE must be unset); gate-only tripwires reported.
          Reported, not chased: this seat's case rests on the objective metrics of
          private_reach.py, setpoint_unit.py, store_report_equiv.py and runtime_closure.py.
Command:  python3 dev/audit/rounds/round10/D7/arch3-s6/score_delta.py PATCH... [--revert] [--on ABS_PATCH]
          PATCH: patches/P1_issue_writer_leaf.patch ... P4_reason_vocabulary.patch (applied in order);
          --on applies a patch to BOTH trees first (main plus an overlapping prototype).
Perturbation: --revert applies the patches and then reverses them, last first: delta_S must read
          0.0000 with no metric moved.
Expected (baseline d749c986d, Apple M1, darwin): see REPORT table; exact (static counts).
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

BASELINE = "d749c986d238d87fd6aa3c7550cee25be3bf9ca1"


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
    with tempfile.TemporaryDirectory(prefix="arch3s6-") as tmp:
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
    print(f"RESULT delta_S={d['dS']:+.4f} weighted-log2")
    print(f"RESULT verdict={d['verdict']}")
    print(f"RESULT admissible={d['admissible']}")
    for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY):
        b, c = base.get(m), proto.get(m)
        if b is None or c is None:
            print(f"RESULT {m}=unmeasured")
            continue
        tag = "tripwire" if m in vector.GATE_ONLY else "score"
        if b != c or tag == "tripwire":
            print(f"RESULT {m}={b}->{c} count ({tag}) term={d['terms'].get(m, 0.0):+.4f}")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
