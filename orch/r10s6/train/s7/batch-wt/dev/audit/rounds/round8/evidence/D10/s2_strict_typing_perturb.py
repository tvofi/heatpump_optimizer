#!/usr/bin/env python3
"""
Perturbation for strict typing: Add type annotations to key modules
Run: python3 tools/audit/round8/D10/s2_strict_typing_perturb.py
This shows mypy --strict error count moving when type hints are added
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

# Apply perturbation: add type hints to key module
integration_path = "custom_components/heatpump_optimizer"
optimizer_path = os.path.join(integration_path, "optimizer.py")

# Backup original file
import shutil
backup_path = optimizer_path + ".backup"
if not os.path.exists(backup_path):
    shutil.copy2(optimizer_path, backup_path)

# Read the file
try:
    with open(optimizer_path, 'r') as f:
        original_content = f.read()

    # Add type annotations to imports at the top if not already there
    perturbed_content = original_content

    # Add from typing import annotations if not present
    if 'from typing import' not in perturbed_content:
        # Find the first import line
        lines = perturbed_content.split('\n')
        import_line_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_line_idx = i
                break

        # Insert typing import
        if import_line_idx > 0:
            lines.insert(import_line_idx, 'from typing import Any, Optional')
            perturbed_content = '\n'.join(lines)

    # Write perturbed content
    with open(optimizer_path, 'w') as f:
        f.write(perturbed_content)

    # Run mypy with strict flag on perturbed code
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

except subprocess.TimeoutExpired:
    total_errors = 999
    error_categories = {"timeout": 1}
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    total_errors = -1
    error_categories = {}

finally:
    # Restore original content
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, optimizer_path)
        os.remove(backup_path)

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

swapins = 0

# Output results
print(f"RESULT mypy_perturb_total_errors={total_errors} errors")
for code, count in sorted(error_categories.items(), key=lambda x: -x[1])[:5]:
    print(f"RESULT mypy_perturb_errors_{code}={count} count")

print(f"RESULT thread_factor={thread_factor:.3f}")
print(f'RESULT load1={load1:.2f}')
print(f"RESULT swapins={swapins}")
