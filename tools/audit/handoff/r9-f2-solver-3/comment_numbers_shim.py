"""Companion to D5-s2's comment_numbers.py for a tree that retired
const.DHW_COLD_WATER_TEMP (R9-F2.3). The harness reads that constant by
name, so at the head it exits on AttributeError before printing its other
rows. This re-creates the name in memory as DEFAULT_DHW_INLET_TEMP (the value
the retired constant held), then runs the harness unchanged, so its rows
for the OTHER claims (D5-s2-02's) are measured at the head. Its
draw_cold_end row reads the shim, not a claim: at the head no comment or
constant makes that claim (git grep DHW_COLD_WATER_TEMP custom_components
prints nothing).
usage: comment_numbers_shim.py <path to comment_numbers.py> [args]"""
import runpy, sys
sys.path.insert(0, "custom_components")
from heatpump_optimizer import const
if not hasattr(const, "DHW_COLD_WATER_TEMP"):
    const.DHW_COLD_WATER_TEMP = const.DEFAULT_DHW_INLET_TEMP
path = sys.argv[1]; sys.argv = [path] + sys.argv[2:]
runpy.run_path(path, run_name="__main__")
