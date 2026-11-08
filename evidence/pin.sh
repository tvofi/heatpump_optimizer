cd ${1:-/home/user/rev}
export PYTHONPATH=tests/hastub:custom_components:tests
python3 tests/wood_advisor.py 2>&1 | grep -E "FAIL|PASSED|Error" | head -8; a=${PIPESTATUS[0]}
python3 tools/audit/seat/features_block.py --prelude "from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator" --prelude "from harness import FakeEntry, FakeHass" --prelude "NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)" "from heatpump_optimizer.wood_fuel import (" "_wf_soc_kwargs = dict(" 2>&1 | grep -E "FAIL|PASSED|Error" | head -8; b=${PIPESTATUS[0]}
echo "wood_advisor rc=$a features rc=$b"
