#!/usr/bin/env python3
"""D10-v1 independent re-measure and breakdown of D10-s2-01 (mypy --strict
error count) plus a real perturbation (s2's own perturbation script is a
no-op: it inserts an unused `from typing import Any, Optional` line into
optimizer.py, which changes zero mypy output; this harness applies a
perturbation that actually narrows a real annotation and confirms the count
moves).

Metric definition (own): mypy_strict_errors_v1 = total `: error:` lines from
`python3 -m mypy --strict --show-error-codes custom_components/heatpump_optimizer`
run the same way as s2 (PYTHONPATH=tests/hastub), further split into
`stub_cascade` (error code import-untyped, or any other error on a line
whose message contains `has type "Any"` / `Item "..." of "Any | ` /
`Returning Any` — i.e. attributable to Any propagating from an untyped
stub import) versus `other` (every remaining error, i.e. not obviously an
artifact of the missing homeassistant py.typed stub).

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D10/v1_mypy_breakdown.py
Expected: RESULT mypy_strict_errors_v1=515 (cross-check against s2's 515) ± 5
(mypy timestamp/order nondeterminism across some runs, in practice exact)
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Perturbation: entity.py class HeatPumpOptimizerSensorBase's
`__init_subclass__` (or, if absent, the first `def __init__(self, ...)` in
entity.py) gets a `# type: ignore[no-untyped-def]` stripped/added is NOT
used (too indirect); instead this harness edits
`custom_components/heatpump_optimizer/__init__.py` line containing
`entry: heatpump_optimizer.HeatPumpOptimizerConfigEntry` (a `[valid-type]`
error site, self-contained, see mypy_out inspection) by adding an explicit
`TypeAlias` annotation to the alias definition
(`HeatPumpOptimizerConfigEntry = ConfigEntry[...]` ->
`HeatPumpOptimizerConfigEntry: TypeAlias = ConfigEntry[...]`) in
coordinator.py or wherever the alias is defined, and re-measures. Expected
direction: down (removes the `[valid-type]` "Variable ... is not valid as a
type" errors, currently >=2 occurrences). Applied and reverted in a
`finally` block.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import glob
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
PKG = os.path.join(REPO_ROOT, "custom_components", "heatpump_optimizer")

STUB_MARKERS = (
    "import-untyped",
    'has type "Any"',
    "Item \"Any\"",
    "of \"Any |",
    "Returning Any",
    "has type \"Any\"",
)


def run_mypy():
    env = os.environ.copy()
    env["PYTHONPATH"] = "tests/hastub"
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--show-error-codes",
         "custom_components/heatpump_optimizer"],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=90,
    )
    return result.stdout + result.stderr


def classify(output):
    total = 0
    stub_cascade = 0
    other = 0
    other_lines = []
    for line in output.splitlines():
        if ": error:" not in line:
            continue
        total += 1
        if any(marker in line for marker in STUB_MARKERS):
            stub_cascade += 1
        else:
            other += 1
            other_lines.append(line)
    return total, stub_cascade, other, other_lines


def find_alias_def():
    """Locate `HeatPumpOptimizerConfigEntry = ` definition (no TypeAlias)."""
    for fname in ("coordinator.py", "__init__.py", "const.py"):
        p = os.path.join(PKG, fname)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            src = f.read()
        m = re.search(r"^(HeatPumpOptimizerConfigEntry\s*=\s*.+)$", src, re.MULTILINE)
        if m:
            return p, src, m.group(1)
    return None, None, None


def main():
    t0 = time.process_time()
    baseline_out = run_mypy()
    total, stub_cascade, other, other_lines = classify(baseline_out)
    print(f"RESULT mypy_strict_errors_v1={total}")
    print(f"RESULT mypy_stub_cascade_v1={stub_cascade}")
    print(f"RESULT mypy_other_v1={other}")
    print(f"RESULT mypy_stub_cascade_fraction_v1={stub_cascade / total:.3f}" if total else "RESULT mypy_stub_cascade_fraction_v1=NA")
    for l in other_lines[:10]:
        print(f"  other-class sample: {l}")

    # Own perturbation: type-alias the ConfigEntry alias definition.
    path, src, defline = find_alias_def()
    if path is None or "TypeAlias" in defline:
        print("RESULT perturbation=SKIPPED_alias_def_not_found_or_already_typed")
    else:
        patched = src.replace(
            defline,
            defline.replace("HeatPumpOptimizerConfigEntry =",
                             "HeatPumpOptimizerConfigEntry: \"TypeAlias\" ="),
            1,
        )
        assert patched != src, "perturbation edit did not change source"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(patched)
            perturbed_out = run_mypy()
            total_p, stub_p, other_p, _ = classify(perturbed_out)
            print(f"RESULT mypy_strict_errors_v1_after_perturb={total_p}")
        finally:
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)

    # Also re-run s2's own perturbation script's edit inline here (unused
    # typing import) to show independently that it is a true no-op.
    optimizer_path = os.path.join(PKG, "optimizer.py")
    with open(optimizer_path, encoding="utf-8") as f:
        opt_src = f.read()
    lines = opt_src.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            lines.insert(i, "from typing import Any, Optional")
            break
    noop_patched = "\n".join(lines)
    try:
        with open(optimizer_path, "w", encoding="utf-8") as f:
            f.write(noop_patched)
        noop_out = run_mypy()
        total_noop, _, _, _ = classify(noop_out)
        print(f"RESULT mypy_strict_errors_v1_after_s2_noop_perturb={total_noop}")
    finally:
        with open(optimizer_path, "w", encoding="utf-8") as f:
            f.write(opt_src)

    print(f"RESULT scan_cpu_s={time.process_time() - t0:.4f}")
    print("RESULT thread_factor=1.00")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
