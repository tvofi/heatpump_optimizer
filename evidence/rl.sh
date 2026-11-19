#!/bin/bash
cd "$1" || exit 2
E="env PYTHONPATH=tests/hastub:custom_components:tests"
S='from heatpump_optimizer.thermal_model import ThermalState as _rl_State'
$E python3 tools/audit/seat/features_block.py --emit-prelude ../rl-prelude-$2.py "$S" > ../ev2/rl-emit-$2.txt 2>&1
echo "emit rc=$?" >> ../ev2/rl-emit-$2.txt
$E python3 tools/audit/seat/features_block.py --prelude "exec(open('../rl-prelude-$2.py').read())" "$S" > ../ev2/rl-$2.txt 2>&1
echo "rc=$?" >> ../ev2/rl-$2.txt
