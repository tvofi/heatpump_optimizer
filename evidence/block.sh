#!/bin/bash
# runs the R10-WHY-NOW-WIDGET features block in the cwd (the fixer's MUTANT_CMD, quoted from the body)
env PYTHONPATH=tests/hastub:tests python3 tools/audit/seat/features_block.py --prelude 'from types import SimpleNamespace' --prelude 'from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState' '# --- R10-WHY-NOW-WIDGET: per-slot drivers' '# R10-CLONE-2238 (#2238'
