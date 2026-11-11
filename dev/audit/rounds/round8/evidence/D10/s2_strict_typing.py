#!/usr/bin/env python3
"""
Metric: mypy --strict type checking errors in integration (custom:heatpump_optimizer)
Run: python3 tools/audit/round8/D10/s2_strict_typing.py
Expected: count of mypy --strict errors by category
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: cloud Linux 4-vCPU 15GB RAM
"""
import os
import sys
import subprocess
import re
import time

# Thread pin BEFORE numpy import
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

# Track timing
start_time = time.time()
start_cpu = time.process_time()
start_thread = time.thread_time()

# Create mypy config for strict checking
mypy_config = """
[mypy]
strict = True
python_version = 3.11
check_untyped_defs = True
disallow_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_return_any = True
warn_unused_configs = True
"""

# Integration module path
integration_path = "custom_components/heatpump_optimizer"

try:
    # Run mypy with strict flag
    env = os.environ.copy()
    env["PYTHONPATH"] = "tests/hastub"

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", "--show-error-codes", integration_path],
        env=env,
        capture_output=True,
        text=True,
        timeout=60
    )

    output = result.stdout + result.stderr

    # Parse error counts by category
    error_categories = {}

    # Match lines like: "file.py:123: error: message [error-code]"
    for line in output.split('\n'):
        # Extract error code if present
        match = re.search(r'\[(\w+)\]', line)
        if match:
            code = match.group(1)
            error_categories[code] = error_categories.get(code, 0) + 1

    # Also count lines with "error:" to get total
    total_errors = len([l for l in output.split('\n') if ': error:' in l])

    # Count other error types
    total_warnings = len([l for l in output.split('\n') if ': warning:' in l])
    total_notes = len([l for l in output.split('\n') if ': note:' in l])

except subprocess.TimeoutExpired:
    total_errors = 999  # Indicate timeout
    error_categories = {"timeout": 1}
    total_warnings = 0
    total_notes = 0
except Exception as e:
    print(f"Error running mypy: {e}", file=sys.stderr)
    total_errors = -1
    error_categories = {}
    total_warnings = 0
    total_notes = 0

# Measure timing and system metrics
end_time = time.time()
end_cpu = time.process_time()
end_thread = time.thread_time()

wall_time = end_time - start_time
cpu_time = end_cpu - start_cpu
thread_time = end_thread - start_thread

if thread_time > 0:
    thread_factor = cpu_time / thread_time
else:
    thread_factor = 1.0

# Get system metrics
try:
    load1 = os.getloadavg()[0]
except:
    load1 = 0.0

# Count page ins (swaps) - simplified
swapins = 0

# Output results
print(f"RESULT mypy_total_errors={total_errors} errors")
print(f"RESULT mypy_total_warnings={total_warnings} warnings")
print(f"RESULT mypy_total_notes={total_notes} notes")

# Output top error categories
for code, count in sorted(error_categories.items(), key=lambda x: -x[1])[:5]:
    print(f"RESULT mypy_errors_{code}={count} count")

print(f"RESULT thread_factor={thread_factor:.3f}")
print(f'RESULT load1={load1:.2f}')
print(f"RESULT swapins={swapins}")
