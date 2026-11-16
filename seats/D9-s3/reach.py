#!/usr/bin/env python3
"""D9-s3 M2: which production files can the stress gate's cost channels see?

Metric (one line): per D9 universe file, the functions (code objects, module
bodies excluded) that START at least once while `tests/stress.py:build_case`
runs every sweep scenario (`stress.sweep_combinations()`) under the gate's own
meter `stress.SolverWork` -- the only code whose cost any stress channel
(work counts, kernel CPU, whole-solve CPU median, memory probe) can read. A
file with 0 executed functions is BLIND: a 2x regression of any metric in it
leaves every stress reading bit-identical. Count key: `sys.monitoring`
PY_START events on code objects whose `co_filename` is the production file.
The www card (.js) is never loaded by a Python gate and is reported blind.

Perturbation: `--only <label,...>` restricts the sweep (e.g. to
`winter/1z/space`): RESULT files_reached falls (the DHW and two-zone modules
drop out), proving the count reads executed code, not imports.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D9/s3/reach.py [--only label,label]
Expected at 92d38ecb (default): universe=96 files, files_reached=16 (exact),
  files_blind=80 (exact), coordinator.py executed=0 of 835. --only
  winter/1z/space: files_reached=13.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box B3,
  Linux x86_64, Python 3.14 (counts are final; no timing is reported).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import glob  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--only", default="")
args = ap.parse_args()

_argv = sys.argv
sys.argv = [_argv[0]]
sys.path.insert(0, "tests")
import stress  # noqa: E402

sys.argv = _argv

PKG = os.path.abspath("custom_components/heatpump_optimizer")


def code_objects(path: str) -> set[tuple[str, int]]:
    """Every function code object a file defines, by (qualname, firstlineno)."""
    top = compile(open(path).read(), path, "exec")
    out: set[tuple[str, int]] = set()
    stack = [top]
    while stack:
        co = stack.pop()
        for c in co.co_consts:
            if isinstance(c, types.CodeType):
                out.add((c.co_qualname, c.co_firstlineno))
                stack.append(c)
    return out


def main() -> int:
    t0, tt0 = time.process_time(), time.thread_time()
    universe = sorted(glob.glob(os.path.join(PKG, "*.py")))
    universe += sorted(glob.glob(os.path.join(PKG, "www", "*.js")))
    hit: dict[str, set[tuple[str, int]]] = {}
    mon = sys.monitoring
    tool = mon.PROFILER_ID if mon.get_tool(mon.PROFILER_ID) is None else 5
    mon.use_tool_id(tool, "d9s3-reach")

    def on_start(code, _offset):
        fn = code.co_filename
        if fn.startswith(PKG):
            hit.setdefault(os.path.abspath(fn), set()).add(
                (code.co_qualname, code.co_firstlineno))
        return mon.DISABLE

    mon.register_callback(tool, mon.events.PY_START, on_start)
    combos = stress.sweep_combinations()
    if args.only:
        keep = set(args.only.split(","))
        combos = [c for c in combos if c["label"] in keep]
    mon.set_events(tool, mon.events.PY_START)
    try:
        for c in combos:
            spec = {k: v for k, v in c.items() if k != "label"}
            stress.build_case(**spec)
    finally:
        mon.set_events(tool, 0)
        mon.free_tool_id(tool)

    reached = blind = 0
    for path in universe:
        rel = os.path.relpath(path)
        if path.endswith(".js"):
            print(f"FILE {rel} executed=0 defined=n/a blind=1")
            blind += 1
            continue
        defined = code_objects(path)
        got = hit.get(path, set()) & defined
        is_blind = not got
        reached += not is_blind
        blind += is_blind
        print(f"FILE {rel} executed={len(got)} defined={len(defined)} blind={int(is_blind)}")
    print(f"RESULT scenarios={len(combos)} scenarios")
    print(f"RESULT universe={len(universe)} files")
    print(f"RESULT files_reached={reached} files")
    print(f"RESULT files_blind={blind} files")
    coord = os.path.join(PKG, "coordinator.py")
    print(f"RESULT coordinator_executed={len(hit.get(coord, set()))} functions")
    print(f"RESULT coordinator_defined={len(code_objects(coord))} functions")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
