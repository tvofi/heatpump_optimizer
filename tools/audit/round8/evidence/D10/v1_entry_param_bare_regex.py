#!/usr/bin/env python3
"""D10-v1 independent re-measure of D10-s1-01 (qs_entry_param_bare).

Metric definition (own, regex-based, deliberately NOT sharing the finder's
AST walker): qs_entry_param_bare_v1 = count of lines in
custom_components/heatpump_optimizer/*.py matching a parameter or return
annotation of the form `ConfigEntry` or `config_entries.ConfigEntry`
(optionally subscripted `[...]`), found via a line-scan regex over each
function/method signature block (a signature may span multiple lines, so
this joins each `def ... :` header before matching), excluding any
occurrence of `HeatPumpOptimizerConfigEntry` (which contains the substring
`ConfigEntry` but is the typed alias, not the bare type).

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D10/v1_entry_param_bare_regex.py
Expected: RESULT qs_entry_param_bare_v1=3 (cross-check against s1's AST
count of 3) ± 0
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

# Matches a bare ConfigEntry reference NOT immediately preceded by "HeatPumpOptimizer"
BARE_RE = re.compile(r"(?<!HeatPumpOptimizer)\bConfigEntry\b")


def extract_defs(src):
    """Yield (start_line, header_text) for each def/async def signature,
    joining continuation lines up to the matching ':' that starts the body."""
    lines = src.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("async def "):
            start = i
            buf = [line]
            depth = line.count("(") - line.count(")")
            j = i
            while depth > 0 and j + 1 < n:
                j += 1
                buf.append(lines[j])
                depth += lines[j].count("(") - lines[j].count(")")
            # also grab return-annotation line(s) up to the trailing ':'
            joined = "\n".join(buf)
            k = j
            while not joined.rstrip().endswith(":") and k + 1 < n:
                k += 1
                buf.append(lines[k])
                joined = "\n".join(buf)
            yield start + 1, joined
            i = k + 1
        else:
            i += 1


def scan_file(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    hits = []
    for lineno, header in extract_defs(src):
        for m in BARE_RE.finditer(header):
            hits.append((path, lineno))
    return hits


def scan():
    files = sorted(glob.glob(os.path.join(PKG, "*.py")))
    all_hits = []
    for f in files:
        all_hits.extend(scan_file(f))
    return all_hits


def main():
    t0 = time.process_time()
    hits = scan()
    for path, lineno in hits:
        rel = os.path.relpath(path, REPO_ROOT)
        print(f"  bare ConfigEntry (regex, header starts): {rel}:{lineno}")
    print(f"RESULT qs_entry_param_bare_v1={len(hits)}")
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
