#!/usr/bin/env python3
# Metric: ThermalParameters.buffer_is_store (bool) for a throttling-valve buffer of exactly BUFFER_STORE_MIN_VOLUME litres
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_cde383447b865539.py
# EXPECTED: baseline True, mutant False at the tie; null equal
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see ../MACHINE.txt; 4 vCPU, load provisional).
# Instrumented symbol: thermal_model:ThermalParameters.buffer_is_store line 303: volume >= MIN -> > (in memory, recompiled from the file).
# Perturbation: key cde383447b865539; direction: True -> False at volume == BUFFER_STORE_MIN_VOLUME
# Null control: the same recompile with old==new.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from mutlib import tm, mutant, LINES
from custom_components.heatpump_optimizer import const, mixing_valve as mv
import sys as _s
src_line = LINES[302]
print("RESULT site=%r" % src_line.strip())
old = ">= BUFFER_STORE_MIN_VOLUME"; new = "> BUFFER_STORE_MIN_VOLUME"
mut = mutant("ThermalParameters", "buffer_is_store", 303, old, new); nul = mutant("ThermalParameters", "buffer_is_store", 303, old, old)
moved = nm = tried = 0
for vol in (const.BUFFER_STORE_MIN_VOLUME, const.BUFFER_STORE_MIN_VOLUME - 1e-9, const.BUFFER_STORE_MIN_VOLUME + 1e-9, 5.0, 750.0):
    p = tm.ThermalParameters(buffer_tank_volume=vol, mixing_valve_mode=mv.MODE_MANUAL)
    b, m, n = p.buffer_is_store, mut(p), nul(p); tried += 1; moved += b != m; nm += b != n
    print(f"RESULT vol_{vol!r}: baseline={b} mutant={m}")
print(f"RESULT inputs_tried={tried} count"); print(f"RESULT inputs_moved={moved} count"); print(f"RESULT null_moved={nm} count")
