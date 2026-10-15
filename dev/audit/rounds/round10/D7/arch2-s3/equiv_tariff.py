"""Bit-parity probe: the tariff twins' outputs on a seeded grid, base tree against head tree.

Metric: mismatches = probe outputs (float.hex) that differ between the two trees, over a seeded grid
of plans: plateaus (pure, mixed, k+1 tie), separated peaks, all-below-threshold, zero/one/odd widths,
offsets, window factors, distinct-days on/off, k in 1..5 and a fractional k, B in {1, 7, 97}.
Key: the value each production function returns (``tariff._smooth_topk_sum``,
``tariff.peak_cost``, ``tariff.peak_cost_smooth``, ``tariff.peak_cost_batch`` rows, and the scalar
vs batch row agreement inside each tree).

Perturbation: --perturb adds 1 ulp to the head tree's ``_PEAK_SMOOTH_TAU`` (via env HPO_PROBE_PERTURB,
read only by this probe's child) -- the mismatch count must rise above 0.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/equiv_tariff.py --base REF [--head DIR] [--perturb]

``--head`` defaults to the working tree. Counts only; contention-immune. Thread-pinned.
Writes only under a tempfile.mkdtemp root.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
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

CHILD = r'''
import json, os, sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from heatpump_optimizer import tariff as T
if os.environ.get("HPO_PROBE_PERTURB"):
    T._PEAK_SMOOTH_TAU = np.nextafter(T._PEAK_SMOOTH_TAU, 1.0)
# the scalar smooth top-k where the tree has one, else the batch on one row (the prototype's form)
smooth1 = getattr(T, "_smooth_topk_sum", None) or (
    lambda v, k, tau: float(T._smooth_topk_sum_batch(np.asarray(v, float).reshape(1, -1), k, tau)[0]))
rng = np.random.default_rng(20261015)
out = {}
h = lambda v: float(v).hex()
def plans(n):
    yield "flat", np.full(n, 4.0)
    yield "below", np.full(n, 0.5)
    yield "sep", np.where(np.arange(n) % 17 == 3, 7.0, 2.0)
    p = np.full(n, 3.0); p[n // 3: n // 3 + 9] = 6.0
    yield "plateau9", p
    q = p.copy(); q[min(n - 1, n // 3 + 2):][:1] -= 5e-4
    yield "mixed", q
    for i in range(4):
        yield f"rand{i}", rng.uniform(0, 7, n)
    yield "bang", np.where(rng.uniform(size=n) > 0.5, 6.0, 0.0)
for n in (0, 1, 7, 8, 9, 96, 192, 193):
    for name, plan in plans(n):
        for k in (0, 1, 2, 3, 5, 2.5):
            out[f"smooth/{n}/{name}/{k}"] = h(smooth1(plan, k, 0.05))
for n in (96, 192):
    for name, plan in plans(n):
        for k in (1, 3, 5):
            for wm in (15, 60):
                for off in (0, 3):
                    for dd in (False, True):
                        for fac in (None, "mask"):
                            wf = None
                            if fac:
                                nw = T.metering_windows(np.zeros(n), wm, 0.25, off).size
                                wf = np.where(np.arange(nw) % 24 < 12, 1.0, 0.5)
                            args = (plan, 1.5, 3.0, 20.0, wm, 0.25, k, off)
                            key = f"{n}/{name}/{k}/{wm}/{off}/{dd}/{fac}"
                            out["exact/" + key] = h(T.peak_cost(*args, window_factors=wf, distinct_days=dd))
                            sm = T.peak_cost_smooth(*args, window_factors=wf, distinct_days=dd)
                            out["smoothc/" + key] = h(sm)
                            for B in (1, 7, 97):
                                mat = np.vstack([plan] + [plan + rng.normal(0, 0.3, n) for _ in range(B - 1)])
                                if B == 97:
                                    mat = np.asfortranarray(mat)
                                bt = T.peak_cost_batch(mat, 1.5, 3.0, 20.0, wm, 0.25, k, off,
                                                       window_factors=wf, distinct_days=dd)
                                out[f"batch{B}/" + key] = [h(v) for v in bt]
                                rows = [h(T.peak_cost_smooth(mat[b], 1.5, 3.0, 20.0, wm, 0.25, k, off,
                                                             window_factors=wf, distinct_days=dd)) for b in range(B)]
                                out[f"rowparity{B}/" + key] = int(rows == out[f"batch{B}/" + key])
print(json.dumps(out))
'''


def run(tree: Path, perturb: bool) -> dict:
    env = dict(os.environ)
    env.pop("HPO_PROBE_PERTURB", None)
    env["PYTHONPATH"] = str(REPO / "tests" / "hastub")
    if perturb:
        env["HPO_PROBE_PERTURB"] = "1"
    r = subprocess.run([sys.executable, "-c", CHILD, str(tree / "custom_components")],
                       capture_output=True, text=True, env=env, cwd=tree)
    if r.returncode:
        sys.exit(f"child failed on {tree}:\n{r.stderr[-3000:]}")
    return json.loads(r.stdout)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default=str(REPO))
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    tmp = Path(tempfile.mkdtemp(prefix="arch2-s3-eqt-"))
    try:
        base = run(tree_of(a.base, tmp / "base"), False)
        head = run(Path(a.head), a.perturb)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    keys = sorted(set(base) | set(head))
    mism = [k for k in keys if base.get(k) != head.get(k)]
    parity_fail = [k for k in keys if k.startswith("rowparity") and head.get(k) != 1]
    print(f"RESULT probes={len(keys)} count")
    print(f"RESULT mismatches={len(mism)} count")
    print(f"RESULT head_scalar_batch_parity_failures={len(parity_fail)} count")
    for k in mism[:10]:
        print("  mismatch", k, base.get(k), head.get(k))
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
