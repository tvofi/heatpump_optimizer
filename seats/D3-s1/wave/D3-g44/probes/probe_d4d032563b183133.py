#!/usr/bin/env python3
# Metric: max |baseline - mutant| over room/slab/buffer/wood/refused arrays of ThermalModel.simulate_trajectory_batch across a 32-scenario grid
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_d4d032563b183133.py
# EXPECTED: scenarios_moved=0 (equivalent) ; null_max_abs_diff=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see MACHINE.txt).
# Instrumented symbol: thermal_model:ThermalModel.simulate_trajectory_batch line 4752 `dT_buf > dT_cap` -> `dT_buf >= dT_cap` (in memory).
# Perturbation: key d4d032563b183133, CMP_BOUND; direction: none expected (scale=delivered/drawn=1.0 at tie).
# Null control: the same recompile with old==new.
import sys; sys.path.insert(0, __import__("os").path.dirname(__file__))
import batchscen
batchscen.main("d4d032563b183133", 4752, 'dT_buf > dT_cap', 'dT_buf >= dT_cap', "")
