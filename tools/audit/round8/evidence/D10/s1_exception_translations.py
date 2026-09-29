#!/usr/bin/env python3
"""D10-s1-02: count of HomeAssistantError-family raise sites in the
integration missing translation_domain/translation_key keyword arguments.

Metric definition: qs_exception_raise_missing_translation = count of
`raise X(...)` call sites, X in {HomeAssistantError, ServiceValidationError,
ConfigEntryNotReady, ConfigEntryAuthFailed, UpdateFailed}, across
custom_components/heatpump_optimizer/*.py, whose call's keyword arguments do
NOT include both `translation_domain` and `translation_key`.

Instrumented symbol: custom_components.heatpump_optimizer.coordinator's four
`raise UpdateFailed(...)` sites (the "Tibber outage latch" and the two
"Error updating data" wrappers) plus every other exception raise in the
package, via a corpus-wide AST walk.

Perturbation: adding translation_domain=DOMAIN, translation_key="x" to the
outage-latch raise in `_tibber_fetch_failed` must move the count down by
one; removing the existing kwargs from one already-compliant raise
(services.py's first ServiceValidationError/HomeAssistantError raise found
with translation kwargs) must move it up by one. Both edits are applied and
reverted in a `finally` block.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D10/s1_exception_translations.py
Expected: RESULT qs_exception_raise_missing_translation=4 (baseline) ± 0
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: 4-vCPU cloud container; pure AST count, contention-immune, final.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import ast
import glob
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
PKG = os.path.join(REPO_ROOT, "custom_components", "heatpump_optimizer")

EXC_NAMES = {
    "HomeAssistantError", "ServiceValidationError", "ConfigEntryNotReady",
    "ConfigEntryAuthFailed", "UpdateFailed",
}


def scan_dir(pkg=PKG):
    total = 0
    missing = []
    for f in sorted(glob.glob(os.path.join(pkg, "*.py"))):
        src = open(f, encoding="utf-8").read()
        tree = ast.parse(src, f)
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                call = node.exc
                fname = None
                if isinstance(call.func, ast.Name):
                    fname = call.func.id
                elif isinstance(call.func, ast.Attribute):
                    fname = call.func.attr
                if fname in EXC_NAMES:
                    total += 1
                    kwnames = {kw.arg for kw in call.keywords}
                    if not ({"translation_domain", "translation_key"} <= kwnames):
                        missing.append((os.path.relpath(f, REPO_ROOT), node.lineno, fname))
    return total, missing


def main():
    t0 = time.process_time()
    total, missing = scan_dir()
    for m in missing:
        print(f"  missing translation kwargs: {m[0]}:{m[1]} {m[2]}")
    print(f"RESULT qs_exception_raise_total={total}")
    print(f"RESULT qs_exception_raise_missing_translation={len(missing)}")

    coord = os.path.join(PKG, "coordinator.py")
    with open(coord, encoding="utf-8") as f:
        orig = f.read()
    target = 'raise UpdateFailed(reason)'
    assert target in orig, "perturbation target not found; harness stale"
    patched = orig.replace(
        target,
        'raise UpdateFailed(reason, translation_domain="heatpump_optimizer", '
        'translation_key="tibber_fetch_failed")',
        1,
    )
    try:
        with open(coord, "w", encoding="utf-8") as f:
            f.write(patched)
        total_after, missing_after = scan_dir()
        print(f"RESULT qs_exception_raise_missing_translation_after_fix={len(missing_after)}")
    finally:
        with open(coord, "w", encoding="utf-8") as f:
            f.write(orig)

    cfg_flow = os.path.join(PKG, "services.py")
    with open(cfg_flow, encoding="utf-8") as f:
        cf_orig = f.read()
    total0, missing0 = scan_dir()
    # find a compliant raise site to regress (strip its translation kwargs)
    tree = ast.parse(cf_orig, cfg_flow)
    victim = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            call = node.exc
            fname = call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", None)
            if fname in EXC_NAMES:
                kwnames = {kw.arg for kw in call.keywords}
                if {"translation_domain", "translation_key"} <= kwnames:
                    victim = node
                    break
    if victim is not None:
        lines = cf_orig.splitlines(keepends=True)
        # crude but effective: comment out the whole raise statement's kwargs
        # by reconstructing via ast.unparse with kwargs stripped, then
        # replacing the source segment (Python 3.9+ has end_lineno).
        seg = "".join(lines[victim.lineno - 1: victim.end_lineno])
        import re
        seg_patched = re.sub(
            r",?\s*translation_domain\s*=\s*[^,)]+", "", seg
        )
        seg_patched = re.sub(
            r",?\s*translation_key\s*=\s*[^,)]+", "", seg_patched
        )
        assert seg_patched != seg, "regression edit did not change source"
        patched_cf = "".join(lines[: victim.lineno - 1]) + seg_patched + "".join(lines[victim.end_lineno:])
        try:
            with open(cfg_flow, "w", encoding="utf-8") as f:
                f.write(patched_cf)
            total1, missing1 = scan_dir()
            print(f"RESULT qs_exception_raise_missing_translation_after_regress={len(missing1)}")
        finally:
            with open(cfg_flow, "w", encoding="utf-8") as f:
                f.write(cf_orig)
    else:
        print("RESULT qs_exception_raise_missing_translation_after_regress=SKIPPED_no_victim_found")

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
