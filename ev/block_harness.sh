#!/bin/sh
# runs the Tibber failure-semantics section of tests/features.py alone
exec env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py \
 --prelude 'from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass' \
 --prelude 'import asyncio as _asyncio' \
 --prelude "exec(open('/tmp/W/lc.py').read())" \
 'R.section("Unload lifecycle and Tibber failure semantics' '# #216 (round-2 D10-B)'
