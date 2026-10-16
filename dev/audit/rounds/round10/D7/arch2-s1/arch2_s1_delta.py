#!/usr/bin/env python3
"""ARCH2-s1 (round 10, D7): the architecture score's delta for the thermal-parameters single owner.

Metric: delta_S = sum w*log2((base+1)/(proto+1)) over SCORE_METRICS (tools/audit/archscore/score.py),
        every counter on (ARCHSCORE_ABLATE must be unset), gate-only tripwires reported.
Count key: the static census of the prototype tree (no runtime value); a fix review re-derives it by
        scoring its own head against the same base.
Instrumented symbols: archscore.vector:measure, archscore.score:delta over
        coordinator:HeatPumpOptimizerCoordinator, dhw_learning:DhwProfileLearner,
        legionella:LegionellaGuard.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s1/arch2_s1_delta.py \
              --on main|main+arch-s1 [--revert]
          main          base = BASELINE, proto = base + P1_thermal_params_single_owner.patch
          main+arch-s1  base = BASELINE + ARCH-s1's ALL_P1_P2_P3.patch (read from the git object of
                        ARCH_S1_COMMIT), proto = that base + this seat's patch
Perturbation: --revert applies this seat's patch and then reverses it (git apply -R) before
          measuring; the tree is the base again and delta_S must be exactly 0.0000.
Expected (baseline 9061fbd3d710, darwin): main +3.8448 (hub_solve_writes 38->23),
          main+arch-s1 +16.8373 (hub_solve_writes 16->1); --revert 0.0000 on both.
Root rule: ROOT is resolved from this file (five parents up); every tree is read from git objects,
          never from the working tree, so the result does not depend on the checkout.
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

BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
ARCH_S1_COMMIT = "dbabc395f951544bd36d7946cd359ee976b9be83"
ARCH_S1_PATCH = "dev/audit/rounds/round10/D7/arch-s1/ALL_P1_P2_P3.patch"
PATCH = HERE / "P1_thermal_params_single_owner.patch"
#: The cells this seat was given, then every counter the change moves.
CELLS = ("hub_solve_writes", "shared_inplace_writes")
MOVED = ("coord_footprint", "coordinator_multiassigned_attrs")


def apply(root: Path, patch: Path, reverse: bool = False) -> None:
    cmd = ["git", "apply", "--include=custom_components/*", "--whitespace=nowarn"]
    if reverse:
        cmd.append("-R")
    subprocess.run([*cmd, str(patch)], cwd=root, check=True)


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        print("ARCHSCORE_ABLATE is set: every counter must be on", file=sys.stderr)
        return 2
    if "--on" not in argv or argv[argv.index("--on") + 1] not in ("main", "main+arch-s1"):
        print(__doc__)
        return 2
    on = argv[argv.index("--on") + 1]
    revert = "--revert" in argv
    t_cpu, t_thr = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch2s1-") as tmp:
        base_dir, proto_dir = Path(tmp) / "base", Path(tmp) / "proto"
        for d in (base_dir, proto_dir):
            d.mkdir()
            score.tree_of(BASELINE, d)
        if on == "main+arch-s1":
            s1 = Path(tmp) / "arch-s1.patch"
            s1.write_bytes(subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{ARCH_S1_COMMIT}:{ARCH_S1_PATCH}"],
                capture_output=True, check=True).stdout)
            apply(base_dir, s1)
            apply(proto_dir, s1)
        apply(proto_dir, PATCH)
        if revert:
            apply(proto_dir, PATCH, reverse=True)
        base = vector.measure(base_dir)
        proto = vector.measure(proto_dir)
    d = score.delta(base, proto)
    print(score.report(base, proto))
    print(f"RESULT on={on} revert={revert}")
    print(f"RESULT delta_S={d['dS']:+.4f} weighted-log2")
    print(f"RESULT verdict={d['verdict']}")
    print(f"RESULT admissible={d['admissible']}")
    moved = 0
    for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY):
        b, c = base.get(m), proto.get(m)
        if b is None or c is None:
            print(f"RESULT {m}=unmeasured")
            continue
        moved += b != c
        tag = ("cell" if m in CELLS else "moved" if m in MOVED
               else "tripwire" if m in vector.GATE_ONLY else "other")
        print(f"RESULT {m}_base={b} count")
        print(f"RESULT {m}_proto={c} count")
        print(f"RESULT {m}_term={d['terms'].get(m, 0.0):+.4f} weighted-log2 ({tag})")
    print(f"RESULT metrics_moved={moved} count")
    w = score.weights()
    for label, ms in (("cells", CELLS), ("cells_and_moved", CELLS + MOVED)):
        sw = sum(w[m] for m in ms)
        print(f"RESULT {label}_sum_w={sw:.4f}")
        print(f"RESULT {label}_bar_150pct={1.5 * sw:.4f} weighted-log2 (1.5 x the gain of halving each)")
        print(f"RESULT {label}_delta_S={sum(d['terms'].get(m, 0.0) for m in ms):+.4f} weighted-log2")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (static count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
