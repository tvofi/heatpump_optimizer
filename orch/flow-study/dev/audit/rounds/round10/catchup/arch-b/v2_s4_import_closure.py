"""Catch-up verifier arch-b, V2 for D7-s4-81 (P1, one UTC clock owner): the RUNTIME import closure of the
persistence boundary, measured by importing it in a fresh interpreter (not an AST walk).

Metric: for M in {store, snapshots, setpoint_check, quiet_windows, silent_mode}: the number of
heatpump_optimizer.* entries in sys.modules after ``import heatpump_optimizer.M`` in a fresh child
interpreter, and whether heatpump_optimizer.optimizer and scipy.optimize were loaded.
Null control: ``const`` (a leaf) must load 1-2 package modules and no optimizer on every tree.
Perturbation: run with --root on a tree with P1 applied; store's count must fall and optimizer leave.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-b/v2_s4_import_closure.py [--root DIR]

Expected at baseline 9061fbd3d: store loads the optimizer (finder: AST closure 28 with optimizer IN).
Machine: seat macOS box; counts only. Writes nothing.
"""
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else Path.cwd()
CHILD = r"""
import sys, importlib
sys.path.insert(0, sys.argv[1])
importlib.import_module("heatpump_optimizer." + sys.argv[2])
mods = [m for m in sys.modules if m.startswith("heatpump_optimizer.")]
print(len(mods), int("heatpump_optimizer.optimizer" in sys.modules), int("scipy.optimize" in sys.modules))
"""
for m in ("const", "store", "snapshots", "setpoint_check", "quiet_windows", "silent_mode"):
    out = subprocess.run([sys.executable, "-c", CHILD, str(root / "custom_components"), m],
                         capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(root / "tests" / "hastub")})
    if out.returncode:
        print(f"RESULT runtime_closure_{m}=ERROR {out.stderr.strip().splitlines()[-1]}")
        continue
    n, opt, sp = out.stdout.split()
    print(f"RESULT runtime_closure_{m}={n} modules optimizer={opt} scipy_optimize={sp}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
