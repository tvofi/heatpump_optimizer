# reviewer's twin of the body's no_rule3.py: rule three forced off, then the harness
import runpy, sys
import heatpump_optimizer.supply_hold as sh
sh._ends_soon = lambda *_a: False
sys.argv = ["early_cutoff_closed_loop.py"] + sys.argv[1:]
runpy.run_path("dev/audit/harnesses/early_cutoff_closed_loop.py", run_name="__main__")
