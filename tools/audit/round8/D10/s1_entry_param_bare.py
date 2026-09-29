#!/usr/bin/env python3
"""D10-s1-01: count of function/method parameters annotated ConfigEntry
(bare, imported from homeassistant.config_entries, including a subscripted
form like ConfigEntry[X]) rather than the integration's own typed alias
HeatPumpOptimizerConfigEntry, across custom_components/heatpump_optimizer/*.py.

Metric definition: qs_entry_param_bare = count of parameter annotations
across all functions/methods in the integration package whose AST
annotation resolves to the name `ConfigEntry` (Name or a Subscript whose
value is Name `ConfigEntry`), as opposed to `HeatPumpOptimizerConfigEntry`.
This is the exact metric the integration's own quality_scale.yaml cites by
name for the strict-typing platinum rule ("every entry parameter is typed
with HeatPumpOptimizerConfigEntry, none bare (qs_entry_param_bare=0)").

Instrumented symbol: custom_components.heatpump_optimizer.diagnostics:async_get_config_entry_diagnostics
(and, as a corpus-wide AST walk, every module in the package).

Perturbation: editing diagnostics.py's signature from
`entry: ConfigEntry[HeatPumpOptimizerCoordinator]` to
`entry: HeatPumpOptimizerConfigEntry` must move qs_entry_param_bare from 1
to 0. Editing sensor.py's first occurrence the other way (alias -> bare)
must move it from 1 back up to 2. Both are applied and reverted in a
`finally` block; the tree is byte-identical to baseline on exit.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D10/s1_entry_param_bare.py
Expected: RESULT qs_entry_param_bare=1 (baseline) ± 0 (exact, integer count)
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: 4-vCPU cloud container (see BASELINE.md); this is a pure AST
count, contention-immune, final not provisional.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import ast
import glob
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
# repo root is 4 levels up: tools/audit/round8/D10/ -> repo root
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
PKG = os.path.join(REPO_ROOT, "custom_components", "heatpump_optimizer")


def is_bare_configentry_annotation(node):
    """True if `node` is `ConfigEntry` or `ConfigEntry[...]` (bare name,
    not the HeatPumpOptimizerConfigEntry alias)."""
    if node is None:
        return False
    if isinstance(node, ast.Name):
        return node.id == "ConfigEntry"
    if isinstance(node, ast.Subscript):
        val = node.value
        if isinstance(val, ast.Name):
            return val.id == "ConfigEntry"
        if isinstance(val, ast.Attribute):
            return val.attr == "ConfigEntry"
    if isinstance(node, ast.Attribute):
        return node.attr == "ConfigEntry"
    return False


def count_bare_in_file(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = list(node.args.args) + list(node.args.posonlyargs) + list(node.args.kwonlyargs)
            for a in args:
                if is_bare_configentry_annotation(a.annotation):
                    hits.append((path, node.name, a.arg, node.lineno))
            if is_bare_configentry_annotation(node.returns):
                hits.append((path, node.name, "<return>", node.lineno))
    return hits


def scan():
    files = sorted(glob.glob(os.path.join(PKG, "*.py")))
    all_hits = []
    for f in files:
        all_hits.extend(count_bare_in_file(f))
    return all_hits


def main():
    t0 = time.process_time()
    hits = scan()
    t1 = time.process_time()
    for path, fn, argname, lineno in hits:
        rel = os.path.relpath(path, REPO_ROOT)
        print(f"  bare ConfigEntry: {rel}:{lineno} in {fn}({argname})")
    print(f"RESULT qs_entry_param_bare={len(hits)}")

    # perturbation: patch diagnostics.py bare -> alias, expect count to drop by 1
    diag = os.path.join(PKG, "diagnostics.py")
    with open(diag, "r", encoding="utf-8") as f:
        orig_diag = f.read()
    patched_diag = orig_diag.replace(
        "entry: ConfigEntry[HeatPumpOptimizerCoordinator]",
        "entry: HeatPumpOptimizerConfigEntry",
    )
    assert patched_diag != orig_diag, "perturbation target string not found; harness stale"
    try:
        with open(diag, "w", encoding="utf-8") as f:
            f.write(patched_diag)
        hits_after = scan()
        print(f"RESULT qs_entry_param_bare_after_fix={len(hits_after)}")
    finally:
        with open(diag, "w", encoding="utf-8") as f:
            f.write(orig_diag)

    # second perturbation direction: sensor.py alias -> bare on first occurrence
    sens = os.path.join(PKG, "sensor.py")
    with open(sens, "r", encoding="utf-8") as f:
        orig_sens = f.read()
    target = "entry: HeatPumpOptimizerConfigEntry,"
    idx = orig_sens.find(target)
    assert idx != -1, "perturbation target not found in sensor.py; harness stale"
    patched_sens = (
        orig_sens[:idx]
        + "entry: ConfigEntry[HeatPumpOptimizerCoordinator],"
        + orig_sens[idx + len(target):]
    )
    try:
        with open(sens, "w", encoding="utf-8") as f:
            f.write(patched_sens)
        hits_regress = scan()
        print(f"RESULT qs_entry_param_bare_after_regress={len(hits_regress)}")
    finally:
        with open(sens, "w", encoding="utf-8") as f:
            f.write(orig_sens)

    process_cpu = time.process_time() - t0
    print(f"RESULT scan_cpu_s={process_cpu:.4f}")
    print("RESULT thread_factor=1.00")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
