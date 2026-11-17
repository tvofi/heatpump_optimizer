#!/usr/bin/env python3
"""D9-s3 M2: for each production file the stress gate reaches, would a 2x CPU
regression confined to that file trip the gate's whole-solve CPU channel?

Metric (one line): per reached file F and sweep scenario, F's share s of
`stress.build_case`'s profiled solve CPU (cProfile tottime of F's functions /
the scenario's total); a per-call 2x confined to F moves that scenario's
`stress.solve_cpu_median` ratio to 1+s, so the whole-solve channel
(`stress.solve_cpu_over_verdict`, factor sqrt(2)) sees it iff
median_over_scenarios(1+s) > SWEEP_SOLVE_CPU_FACTOR. Shares inside the three
metered kernels (`ThermalModel.simulate_step`, `simulate_trajectory_batch`,
`simulate_dhw_step`) are seen per call by `kernel_cost_over_verdict` and are
reported apart. The verdict is the gate's own function applied to the median.
Count key: cProfile tottime per co_filename (provisional: profiler overhead
inflates Python-call-heavy code; ratios within one run).

Perturbation: `--double MODULE:QUALNAME` makes that pure production function
run twice per call: its file's median share must rise (and 1+s with it),
proving the share reads executed CPU.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D9/s3/cpu_share.py [--double optimizer:_fd_rows]
Expected at 92d38ecb: no single non-kernel file reaches a median share of
  0.414; the largest is optimizer.py. Provisional (CPU shares under load).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box B3.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import cProfile  # noqa: E402
import importlib  # noqa: E402
import pstats  # noqa: E402
import resource  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--double", default="")
ap.add_argument("--only", default="")
args = ap.parse_args()

_argv = sys.argv
sys.argv = [_argv[0]]
sys.path.insert(0, "tests")
import stress  # noqa: E402

sys.argv = _argv
PKG = os.path.abspath("custom_components/heatpump_optimizer")


def main() -> int:
    t0, tt0 = time.process_time(), time.thread_time()
    if args.double:
        mod, qual = args.double.split(":")
        m = importlib.import_module(f"heatpump_optimizer.{mod}")
        owner, name = m, qual
        if "." in qual:
            cls, name = qual.split(".", 1)
            owner = getattr(m, cls)
        orig = getattr(owner, name)

        def twice(*a, **k):
            # A repeat of the call: its CPU lands in its own file, where a
            # cpu_scaler burn would land in stress.py's wrapper instead.
            orig(*a, **k)
            return orig(*a, **k)
        setattr(owner, name, twice)
    combos = stress.sweep_combinations()
    if args.only:
        combos = [c for c in combos if c["label"] in set(args.only.split(","))]
    shares: dict[str, list[float]] = {}
    kernel_shares: list[float] = []
    # Kernel time is the kernel channel's: profiling is switched off inside
    # the three metered seams (wrapped at SolverWork's class attributes, the
    # same place stress.per_call_cost_rounds injects), and the kernel share
    # comes from build_case's own solver_kernel_ms / solve_cpu_ms on an
    # unprofiled solve of the same scenario.
    current = {"prof": None}

    def unprofiled(seam):
        def _call(*a, **k):
            p = current["prof"]
            if p is not None:
                p.disable()
            try:
                return seam(*a, **k)
            finally:
                if p is not None:
                    p.enable()
        return _call

    SW = stress.SolverWork
    saved = (SW._step_wrapped, SW._batch_wrapped, SW._dhw_step_wrapped)
    for c in combos:
        spec = {k: v for k, v in c.items() if k != "label"}
        plain = stress.build_case(**spec)
        ks = float(plain["solver_kernel_ms"]) / max(float(plain["solve_cpu_ms"]), 1e-9)
        kernel_shares.append(ks)
        SW._step_wrapped, SW._batch_wrapped, SW._dhw_step_wrapped = (
            unprofiled(f) for f in saved)
        prof = cProfile.Profile()
        current["prof"] = prof
        try:
            prof.enable()
            stress.build_case(**spec)
            prof.disable()
        finally:
            current["prof"] = None
            SW._step_wrapped, SW._batch_wrapped, SW._dhw_step_wrapped = saved
            from heatpump_optimizer.thermal_model import ThermalModel as _TM
            _TM.simulate_step, _TM.simulate_trajectory_batch, _TM.simulate_dhw_step = saved
        st = pstats.Stats(prof).stats
        total = sum(v[2] for v in st.values()) or 1e-9
        per_file: dict[str, float] = {}
        for (fn, _line, func), v in st.items():
            if not os.path.abspath(fn).startswith(PKG):
                continue
            rel = os.path.relpath(os.path.abspath(fn))
            per_file[rel] = per_file.get(rel, 0.0) + v[2]
        for rel, t in per_file.items():
            # share of the whole solve outside the kernels, scaled to the solve
            shares.setdefault(rel, []).append(t / total * (1.0 - ks))
    n = len(combos)
    seen_any = 0
    for rel in sorted(shares):
        vals = shares[rel] + [0.0] * (n - len(shares[rel]))
        med = statistics.median(vals)
        seen = stress.solve_cpu_over_verdict(1.0 + med)
        seen_any += seen
        print(f"FILE {rel} median_share={med:.4f} max_share={max(vals):.4f} "
              f"in_scenarios={len(shares[rel])}/{n} whole_solve_sees_2x={int(seen)}")
    print(f"RESULT scenarios={n} scenarios")
    print(f"RESULT files_profiled={len(shares)} files")
    print(f"RESULT files_whose_2x_trips_whole_solve={seen_any} files")
    print(f"RESULT kernel_median_share={statistics.median(kernel_shares):.4f} ratio provisional")
    top = max(shares, key=lambda r: statistics.median(shares[r] + [0.0] * (n - len(shares[r]))))
    print(f"RESULT top_file={top}")
    print(f"RESULT top_file_median_share={statistics.median(shares[top] + [0.0] * (n - len(shares[top]))):.4f} ratio provisional")
    print(f"RESULT whole_solve_factor={stress.SWEEP_SOLVE_CPU_FACTOR:.4f} ratio")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
