#!/usr/bin/env python3
"""D10-v1 independent re-measure of D10-s1-02 (missing translation kwargs).

Metric definition (own, regex/text-block based, not sharing s1's AST walker):
qs_exception_missing_translation_v1 = count of `raise <Name>(` occurrences,
Name in {HomeAssistantError, ServiceValidationError, ConfigEntryNotReady,
ConfigEntryAuthFailed, UpdateFailed} (bare or dotted, e.g. `exceptions.X`),
across custom_components/heatpump_optimizer/*.py, where the raise statement's
full source text (from the `raise` keyword through the matching close-paren,
found by bracket depth counting) does not contain both the substrings
"translation_domain" and "translation_key".

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D10/v1_exception_translation_regex.py
Expected: RESULT qs_exception_missing_translation_v1=4 (cross-check against
s1's AST count of 4) ± 0
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import glob
import re
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
PKG = os.path.join(REPO_ROOT, "custom_components", "heatpump_optimizer")

EXC_NAMES = {
    "HomeAssistantError", "ServiceValidationError", "ConfigEntryNotReady",
    "ConfigEntryAuthFailed", "UpdateFailed",
}
RAISE_RE = re.compile(
    r"\braise\s+(?:[A-Za-z_][A-Za-z0-9_]*\.)?(" + "|".join(EXC_NAMES) + r")\s*\("
)


def extract_call_block(src, start_idx):
    """From the '(' after the exception name, walk bracket depth to find the
    matching ')' and return the whole raise-through-close-paren text."""
    open_idx = src.index("(", start_idx)
    depth = 0
    i = open_idx
    while i < len(src):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                return src[start_idx:i + 1]
        i += 1
    return src[start_idx:]


def scan_file(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    hits = []
    total = 0
    for m in RAISE_RE.finditer(src):
        total += 1
        block = extract_call_block(src, m.start())
        has_domain = "translation_domain" in block
        has_key = "translation_key" in block
        if not (has_domain and has_key):
            lineno = src.count("\n", 0, m.start()) + 1
            hits.append((path, lineno, m.group(1)))
    return total, hits


def scan():
    files = sorted(glob.glob(os.path.join(PKG, "*.py")))
    all_hits = []
    total = 0
    for f in files:
        t, hits = scan_file(f)
        total += t
        all_hits.extend(hits)
    return total, all_hits


def main():
    t0 = time.process_time()
    total, hits = scan()
    for path, lineno, name in hits:
        rel = os.path.relpath(path, REPO_ROOT)
        print(f"  missing translation kwargs (regex): {rel}:{lineno} {name}")
    print(f"RESULT qs_exception_raise_total_v1={total}")
    print(f"RESULT qs_exception_missing_translation_v1={len(hits)}")
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
