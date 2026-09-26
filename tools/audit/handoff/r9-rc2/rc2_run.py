"""Run features.py's RC2 block alone, from a tree root (the block text is
extracted from that tree's tests/features.py, not copied)."""
import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass, Results
import asyncio as _asyncio
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer import away as away_mode
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
src = open(sys.argv[1] if len(sys.argv) > 1 else "tests/features.py").read()
start = src.index("# RC2 (round 9):")
end = src.index("# -- the accuracy store: a corrupt read", start)
R = Results("rc2 block")
_T1_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
exec(compile(src[start:end], "features.py:rc2", "exec"), globals())
sys.exit(R.close("RC2 BLOCK"))
