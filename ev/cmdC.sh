#!/bin/bash
exec env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'import heatpump_optimizer.optimizer as _grad_optmod' '_gate = _grad_optmod._bounds_supported_by_batch' 'R.section("The batched objective prices the cost half per batch (#948)")'
