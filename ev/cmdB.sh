#!/bin/bash
exec env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS' '# R11-OUTSIDE-HONEST-STARTS-RUNS (pull request 3529, Bankaifan)'
