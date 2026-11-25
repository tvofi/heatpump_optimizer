#!/usr/bin/env python3
# Metric: max |baseline - mutant| over the step state vector (K or kW) across the scenario battery of _blib.py
#   (ThermalModel.simulate_step over 108 configs x inputs); scenarios moved = how many of the battery's scenarios differ at all.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_97bd985754f1099b.py
# Expected: see the RESULT lines; a nonzero baseline_vs_mutant_max_abs_diff makes the key a candidate, zero = equivalent-candidate.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g43 (4 vCPU Xeon @ 2.10GHz), counts exact, PROVISIONAL timings none.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.simulate_step, line 4140.
# Perturbation: the one-line mutant `if n_sub == 1:` -> `if False:` at thermal_model.py:4140, applied to a scratch copy of the baseline
#   package (nothing in the gate's tree changes). Direction: see RESULT.
# Null control: the same battery, baseline against an unedited scratch copy (identical, diff 0), and batch_vs_scalar_parity_baseline.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blib as B
LINE, OLD, NEW = 4140, 'if n_sub == 1:', 'if False:'
if __name__ == "__main__":
    B.run_step_probe("step", LINE, OLD, NEW)
