#!/bin/bash
exec env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")'
