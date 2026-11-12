#!/bin/sh
cd "${1:-.}" 2>/dev/null
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/hastub exec python3 -B tools/audit/seat/features_block.py --prelude "exec(open('/tmp/tmp.1TFX19wr4j/prelude.py').read())" 'R.section("R10-GENERIC-HEAT-CURVE — the displace through a number entity' '# A crash: the write was armed'
