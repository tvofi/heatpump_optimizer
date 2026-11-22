#!/bin/bash
# run FLOWCAP block in cwd tree
PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("~/hpo-seats/r10s6/rev-3866-local/fl_prelude.py").read())' "# R11-OWNER-FLOWCAP (tvofi, 2026-11-22" "_pa_bl_fb, _ = _pa_boost_level" 2>&1
