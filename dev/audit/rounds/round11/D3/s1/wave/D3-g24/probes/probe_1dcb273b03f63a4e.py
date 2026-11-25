#!/usr/bin/env python3
# Metric: (1) replay_moved = number of replayed HeatPumpOptimizer._solve_space calls (each call a real DHW
#   solve made, re-run on the same optimizer and arguments with its captured warm start and with crafted ones:
#   init_base x2-0.5, warm = init_base x1.5, init_base + p_max, init_base - p_max/2, all -1 kW) whose returned
#   (power vector, status, score) differs at all under the mutant; (2) whole_moved = scenarios whose full
#   optimize() plan or status differs; (3) guess_outside_bounds_{baseline,mutant} = calls whose seeded guess
#   (as handed to _seed_pinned_guess, the line after the mutant) lies outside the solve's own bounds -- the
#   proof the crafted inputs reach the mutated line with a value it changes. Count key: _solve_space's return.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_1dcb273b03f63a4e.py
# Expected: see EXPECTED below (exact counts, tolerance 0).
# EXPECTED RESULT null_replay_moved=0 count
# EXPECTED RESULT null_replay_tried=18 count
# EXPECTED RESULT null_guess_outside_bounds_baseline=0 count
# EXPECTED RESULT null_guess_outside_bounds_mutant=0 count
# EXPECTED RESULT null_whole_moved=0 count
# EXPECTED RESULT null_whole_tried=3 count
# EXPECTED RESULT null_captured_warm_calls=0 count
# EXPECTED RESULT mutant_replay_moved=0 count
# EXPECTED RESULT mutant_replay_tried=18 count
# EXPECTED RESULT mutant_guess_outside_bounds_baseline=0 count
# EXPECTED RESULT mutant_guess_outside_bounds_mutant=6 count
# EXPECTED RESULT mutant_whole_moved=0 count
# EXPECTED RESULT mutant_whole_tried=3 count
# EXPECTED RESULT mutant_captured_warm_calls=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g24 (4 vCPU Intel Xeon @ 2.10GHz, Linux,
#   CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._solve_space
#   (optimizer.py:4943, CLAMP_DROP), scenarios dhw_enabled with power_caps_extra 3/2/1 kW (_space_core.SCEN).
# Perturbation: mutant 1dcb273b03f63a4e, optimizer.py:4943
#   'guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)' -> 'guess = np.minimum((guess), headroom)',
#   applied in memory (_mutlib.mutated; mock.patch.object on the class for the whole-solve arm); direction:
#   replay_moved / whole_moved 0 -> >0.
# Null control: the baseline method against itself (null_* moved counts must be 0, null out-of-bounds 0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.simplefilter("ignore", RuntimeWarning)
import _mutlib  # noqa: E402
import _space_core  # noqa: E402

OLD = '        guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)'
NEW = '        guess = np.minimum((guess), headroom)'
_space_core.run(OLD, OLD, "null")
_space_core.run(OLD, NEW, "mutant")
_mutlib.footer()
