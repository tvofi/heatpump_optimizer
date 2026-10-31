"""ARCH-s2 harness: the architecture-score delta one prototype patch buys, and its perturbation.

Metric: delta_S = S(prototype) - S(baseline), S = sum w * log2((ref+1)/(cur+1)) over
tools/audit/archscore/vector.py's SCORE_METRICS, every counter on (ARCHSCORE_ABLATE must be
unset; the harness refuses to run otherwise). Per-metric deltas are printed for every metric
that moved, gate-only tripwires included.

Perturbation: the same patch applied in reverse onto the prototype tree must give a vector equal
to the baseline's, so delta_S(perturbed) = 0 exactly. That proves the patch file is the whole
delta and the score responds to it.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/harness.py \
        --base 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef \
        dev/audit/rounds/round10/D7/arch-s2/patches/<NN>_*.patch [more patches, applied in order]

Expected: the delta_S each finding in REPORT.md states, tolerance 0 (every metric is a
deterministic static count). Baseline: origin/main 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef,
2026-10-14. Machine: the seat's macOS box (counts only, contention-immune).
Writes only under a tempfile.mkdtemp root.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

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


REPO = repo_root(__file__)
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore import score, vector  # noqa: E402


def apply(tree: Path, patch: Path, reverse: bool = False) -> None:
    cmd = ["patch", "-p1", "-s", "-f", "--no-backup-if-mismatch", "-d", str(tree), "-i", str(patch.resolve())]
    if reverse:
        cmd.insert(1, "-R")
    subprocess.run(cmd, check=True)


def main() -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        print("REFUSED: ARCHSCORE_ABLATE is set; every counter must be on")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("patches", nargs="+", type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    root = Path(tempfile.mkdtemp(prefix="arch-s2-"))
    try:
        base_dir = score.tree_of(a.base, root / "base")
        proto_dir = root / "proto"
        shutil.copytree(base_dir, proto_dir)
        for p in a.patches:
            apply(proto_dir, p)
        base_v = vector.measure(base_dir)
        proto_v = vector.measure(proto_dir)
        d = score.delta(base_v, proto_v)
        print(score.report(base_v, proto_v))
        print(f"RESULT delta_S={d['dS']:+.4f} weighted_log2")
        print(f"RESULT admissible={int(d['admissible'])} bool")
        for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY):
            b, c = base_v.get(m), proto_v.get(m)
            if b != c:
                print(f"RESULT {m}={b}->{c} count")
        for m, t in d["terms"].items():
            print(f"RESULT term_{m}={t:+.4f} weighted_log2")
        # perturbation: the patches reversed, newest first
        for p in reversed(a.patches):
            apply(proto_dir, p, reverse=True)
        pert_v = vector.measure(proto_dir)
        pd = score.delta(base_v, pert_v)
        same = all(base_v.get(m) == pert_v.get(m) for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY))
        print(f"RESULT perturbed_delta_S={pd['dS']:+.4f} weighted_log2")
        print(f"RESULT perturbed_vector_equals_baseline={int(same)} bool")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = "unmeasured"
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        swap = next(ln.split(":")[1].strip(" .") for ln in out.splitlines() if ln.startswith("Swapins"))
    except Exception:
        pass
    print(f"RESULT swapins={swap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
