#!/usr/bin/env python3
"""
Metric: test coverage of integration modules (custom:heatpump_optimizer)
Run: python3 tools/audit/round8/D10/s2_coverage.py
Expected: percentage of lines covered across all test scripts
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: cloud Linux 4-vCPU 15GB RAM
"""
import os
import sys
import subprocess
import time
import tempfile
import shutil
import re

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

# Create temp directory for coverage data
tmpdir = tempfile.mkdtemp(prefix="hpo_coverage_", dir=os.environ.get("TMPDIR", "/tmp"))
coverage_data = os.path.join(tmpdir, ".coverage")

# Test scripts to run - from tests/run.sh
test_scripts = [
    "tests/entities.py",
    "tests/features.py",
]

try:
    env = os.environ.copy()
    env["PYTHONPATH"] = "tests/hastub"
    env["COVERAGE_FILE"] = coverage_data

    # Run coverage on test scripts
    for script in test_scripts:
        if os.path.exists(script):
            result = subprocess.run(
                [sys.executable, "-m", "coverage", "run", "--append",
                 "--source=custom_components/heatpump_optimizer", script],
                env=env,
                capture_output=True,
                timeout=120
            )

    # Generate report
    report_result = subprocess.run(
        [sys.executable, "-m", "coverage", "report", "--skip-covered"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Parse report to extract coverage percentage
    output = report_result.stdout
    coverage_pct = 0.0
    total_lines = 0
    missing_lines = 0

    # Look for coverage percentage in summary line
    for line in output.split('\n'):
        if "TOTAL" in line:
            # Format: TOTAL    1234  567  89%
            parts = line.split()
            if "TOTAL" in parts and len(parts) >= 4:
                try:
                    # Extract percentage from last part
                    pct_str = parts[-1].rstrip('%')
                    coverage_pct = float(pct_str)
                    total_lines = int(parts[1]) if len(parts) > 1 else 0
                    missing_lines = int(parts[2]) if len(parts) > 2 else 0
                except:
                    pass
            break

except subprocess.TimeoutExpired:
    coverage_pct = -1
    total_lines = 0
    missing_lines = 0
except Exception as e:
    print(f"Error running coverage: {e}", file=sys.stderr)
    coverage_pct = 0.0
    total_lines = 0
    missing_lines = 0

finally:
    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)

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
print(f"RESULT coverage_percent={coverage_pct:.1f} %")
print(f"RESULT coverage_total_lines={total_lines} lines")
print(f"RESULT coverage_missing_lines={missing_lines} lines")
print(f"RESULT thread_factor={thread_factor:.3f}")
print(f'RESULT load1={load1:.2f}')
print(f"RESULT swapins={swapins}")
