#!/usr/bin/env python3
"""ARCH2-s2 (round 10, D7 wave 2, seat 2): the architecture score's delta for one prototype patch.

Metric: delta_S = sum w*log2((base+1)/(proto+1)) over SCORE_METRICS (tools/audit/archscore/score.py),
        the baseline tree against the baseline tree with prototype patches applied; every counter
        on (ARCHSCORE_ABLATE must be unset), gate-only tripwires reported.
Count key: the static census of the PROTOTYPE TREE's code (no runtime value), so a fix review
        re-derives it by scoring its own head against the same baseline, not by re-applying a patch.
Instrumented symbols: archscore.vector:measure and archscore.score:delta over
        coordinator:HeatPumpOptimizerCoordinator and the collaborators each patch touches.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s2/arch2_delta.py PATCH... [--on-s1] [--revert]
          PATCH names files in this directory (several are applied in order: the union).
          --on-s1: the base is BASELINE plus wave-1 ARCH-s1's ALL_P1_P2_P3.patch (read from
          origin/handoff/audit-r10-arch-s1 at S1_SHA), and the prototype is that base plus PATCH.
Perturbation: --revert applies the patches and then reverses them (git apply -R, last first)
          before measuring: the tree is the base again and delta_S must be exactly 0.0000.
Root rule: ROOT is repo_root(__file__); both trees are read from git
          objects at BASELINE, never from the working tree.
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
S1_SHA = "dbabc395f951544bd36d7946cd359ee976b9be83"
S1_PATCH = "dev/audit/rounds/round10/D7/arch-s1/ALL_P1_P2_P3.patch"
#: the cells this seat's scope names (multi-assigned attrs, footprint, the tariff family's guard)
#: plus the two write censuses the MQTT/peak-guard and the price-learning writers sit in.
MY_CELLS = ("coordinator_multiassigned_attrs", "coord_footprint", "params_over_10",
            "hub_solve_writes", "shared_inplace_writes")
SCOPE_CELLS = ("coordinator_multiassigned_attrs", "coord_footprint", "params_over_10")


def resolve(ref: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", ref], capture_output=True,
                          text=True, check=True).stdout.strip()


def apply(root: Path, patch: Path, reverse: bool = False) -> None:
    cmd = ["git", "apply", "-C2", "--include=custom_components/*", "--whitespace=nowarn"]
    if reverse:
        cmd.append("-R")
    subprocess.run([*cmd, str(patch)], cwd=root, check=True)


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        print("ARCHSCORE_ABLATE is set: every counter must be on", file=sys.stderr)
        return 2
    patches = [(HERE / a).resolve() for a in argv[1:] if not a.startswith("--")]
    if not patches:
        print(__doc__)
        return 2
    revert = "--revert" in argv
    on_s1 = "--on-s1" in argv
    base_ref = resolve(BASELINE)
    t_cpu, t_thr = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch2s2-") as tmp:
        base_dir, proto_dir = Path(tmp) / "base", Path(tmp) / "proto"
        base_dir.mkdir()
        proto_dir.mkdir()
        score.tree_of(base_ref, base_dir)
        score.tree_of(base_ref, proto_dir)
        if on_s1:
            s1 = Path(tmp) / "s1.patch"
            s1.write_bytes(subprocess.run(["git", "-C", str(ROOT), "show", f"{S1_SHA}:{S1_PATCH}"],
                                          capture_output=True, check=True).stdout)
            apply(base_dir, s1)
            apply(proto_dir, s1)
        for p in patches:
            apply(proto_dir, p)
        if revert:
            for p in reversed(patches):
                apply(proto_dir, p, reverse=True)
        base = vector.measure(base_dir)
        proto = vector.measure(proto_dir)
    d = score.delta(base, proto)
    print(f"base={base_ref[:12]}{' + ARCH-s1 ALL' if on_s1 else ''} patches={[p.name for p in patches]}"
          f"{' (applied and reverted)' if revert else ''}")
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
    for name, cells in (("cells", MY_CELLS), ("scope_cells", SCOPE_CELLS)):
        share = 0.515 * sum(w[m] for m in cells)
        print(f"RESULT {name}_share={share:.4f} weighted-log2 (every cell cut by 30%, ARCH-s1's definition)")
        print(f"RESULT {name}_bar_150pct={1.5 * share:.4f} weighted-log2")
    print(f"RESULT cells_delta_S={sum(d['terms'].get(m, 0.0) for m in MY_CELLS):+.4f} weighted-log2")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (static count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
