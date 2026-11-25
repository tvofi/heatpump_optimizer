"""N-log-flood barrier reach (D14-s2, round 11): which per-cycle log shapes the class barrier counts.

Metric: tests/entities.py's own ``_r10_unlatched_logs`` (extracted by AST and
exec'd, never copied) run over the package as it is, then over the package
with one planted unlatched per-cycle site of each shape appended to
coordinator.py: ``_LOGGER.warning`` (control: must be counted),
``_LOGGER.exception``, ``_LOGGER.critical``, ``_LOGGER.log(logging.WARNING, ...)``
and an alias ``log = _LOGGER; log.warning``. RESULT per shape: 1 when the
barrier's count rose, 0 when it is blind. Plus the package's live sites of the
blind shapes (``SITE`` lines), each needing a disposition.
Key: the barrier function's own Counter total.

Perturbation (``--widen``): the barrier's one attribute test widened in memory to
("warning", "error", "exception", "critical") -> counted_exception and
counted_critical 0 -> 1 (and barrier_sites_baseline +1: the sysid _finish site).
Control: the ``_LOGGER.warning`` plant must read 1; ``--no-control`` drops it.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/logflood_shape.py
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT counted_warning=1,
counted_exception=0, counted_critical=0, counted_log_level=0, counted_alias=0,
RESULT live_blind_sites=1 (sysid.py _finish, once per experiment). Exact.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import ast
import re
import sys
import time
from collections import Counter
from pathlib import Path

SHAPES = {
    "warning": "_LOGGER.warning('x')",
    "exception": "_LOGGER.exception('x')",
    "critical": "_LOGGER.critical('x')",
    "log_level": "_LOGGER.log(logging.WARNING, 'x')",
    "alias": "log = _LOGGER\n    log.warning('x')",
}


def _barrier(widen=False):
    src = Path("tests/entities.py").read_text()
    if widen:
        # the one-line barrier repair: count every level a flood can log at
        old = 'child.func.attr in ("warning", "error")'
        assert src.count(old) == 1, "barrier line moved"
        src = src.replace(old, 'child.func.attr in ("warning", "error", "exception", "critical")')
    tree = ast.parse(src)
    keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name == "_r10_unlatched_logs")
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_R10_LATCH_WORD" for t in n.targets))]
    assert len(keep) == 2, "barrier not found"
    ns = {"ast": ast, "Counter": Counter, "re": re}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "tests/entities.py", "exec"), ns)
    return ns["_r10_unlatched_logs"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-control", action="store_true")
    ap.add_argument("--widen", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    fn = _barrier(a.widen)
    pkg = Path("custom_components/heatpump_optimizer")
    sources = {p.name: p.read_text() for p in sorted(pkg.glob("*.py"))}
    base = sum(fn(sources).values())
    print(f"RESULT barrier_sites_baseline={base} sites")
    for name, body in SHAPES.items():
        if a.no_control and name == "warning":
            continue
        planted = dict(sources)
        planted["coordinator.py"] = sources["coordinator.py"] + f"\n\ndef _planted_cycle_step():\n    {body}\n"
        print(f"RESULT counted_{name}={sum(fn(planted).values()) - base}")
    live = 0
    for name, src in sources.items():
        for node in ast.walk(ast.parse(src)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("exception", "critical", "log")
                    and "LOGGER" in ast.unparse(node.func.value)):
                live += 1
                print(f"SITE {name}:{node.lineno} {ast.unparse(node.func)}")
    print(f"RESULT live_blind_sites={live} sites")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
