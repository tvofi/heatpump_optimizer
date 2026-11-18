"""D9 round 4 / H9 companion -- #948's correctness-identical null control.

The fix for #948 (R4-D9-05) vectorizes the batched objective's cost terms.
Its performance claim is measured by ``h9_batch_cost_loop.py``; this harness
is the OTHER half a performance change owes: proof that the plans did not
move. The same three solves (two-zone DHW winter, single-zone space winter,
two-zone DHW at the flat null price profile) are run through the production
``HeatPumpOptimizer.optimize`` via ``d9common``, and every output array is
dumped for a bitwise base-vs-head comparison.

COMMAND (from the repository root), at the merge base and at the fix head:

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h9_null_plans.py /tmp/null948_<arm>.npz

then compare the two archives; at #948's head the comparison was made with
``a[k].tobytes() != b[k].tobytes()`` over every key and printed
``byte-differing arrays: NONE -- all identical`` (18 arrays).

EXPECTED: every array in the two archives byte-identical. Any difference is
a plan that moved and a fix that is a behaviour change, not a speedup.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import sys  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import numpy as np  # noqa: E402

import d9common as C  # noqa: E402

import hashlib  # noqa: E402

SCENARIOS = {
    "two_zone_dhw_winter": dict(two_zone=True, dhw=True),
    "single_zone_space_winter": dict(two_zone=False, dhw=False),
    "two_zone_dhw_flat": dict(two_zone=True, dhw=True, price_profile="flat"),
}


def main() -> None:
    t0 = C.span_start()
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    out: dict[str, np.ndarray] = {}
    for name, kw in SCENARIOS.items():
        packed = C.make_solve(horizon_hours=24, **kw)
        res = C.run_solve(packed)
        # Rule: the arrays a user or a downstream sensor reads -- the plan,
        # the trajectory it implies, and the reported money figures -- one
        # byte each, no tolerance.
        out[f"{name}__power"] = np.asarray(res.power_schedule, dtype=float)
        out[f"{name}__room"] = np.asarray(res.room_temp_trajectory, dtype=float)
        out[f"{name}__objective"] = np.float64(res.objective_value)
        out[f"{name}__predicted_cost"] = np.float64(res.predicted_cost)
        out[f"{name}__savings"] = np.float64(res.predicted_savings)
        out[f"{name}__status"] = np.frombuffer(
            str(res.status).encode(), dtype=np.uint8
        )
    np.savez(sys.argv[1], **out)
    print(f"saved {sys.argv[1]}")
    for key, value in out.items():
        # A digest, not Python's ``hash``: the builtin salts bytes hashes
        # per process (PYTHONHASHSEED), so it is not comparable across the
        # two invocations this harness exists to compare.
        digest = hashlib.sha256(value.tobytes()).hexdigest()[:16]
        C.result(f"{key}.sha256_16", digest)
    # #950 D9-INST: the whole-span factor beside the block -- this harness
    # landed with #985 after the round-4 panel sat, carrying the same gap
    # the issue names in its four siblings; the solves run on the calling
    # thread under the pinned BLAS, so the plain ratio is the signal.
    C.telemetry(C.span_factor(t0))


if __name__ == "__main__":
    main()
