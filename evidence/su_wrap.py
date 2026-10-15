"""Reviewer's wrapper (mine, not the finder's): runs surface_units.py unmodified at the
PR head, where setpoint_check._read_setpoint moved to inputs.read_setpoint and
pump_arbiter no longer imports state_unit. Aliases only; neither is on the write path."""
import runpy, sys
sys.path[:0] = ["tests/hastub", "tests", "."]
from custom_components.heatpump_optimizer import inputs, pump_arbiter, setpoint_check
setpoint_check._read_setpoint = inputs.read_setpoint
pump_arbiter.state_unit = inputs.state_unit
sys.argv = [sys.argv[1]] + sys.argv[2:]
runpy.run_path(sys.argv[0], run_name="__main__")
