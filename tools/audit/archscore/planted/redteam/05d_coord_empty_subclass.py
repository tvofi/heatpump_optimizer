"""Minimal form of 05c: rename the coordinator class to _CoordinatorBody and append
``class HeatPumpOptimizerCoordinator(_CoordinatorBody)`` with only a docstring. Not one line of
logic moves; every name, import and isinstance check still resolves to the same runtime class
(with one extra, empty level in the MRO)."""
import ast, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
lines = src.splitlines(keepends=True)
lines[cls.lineno - 1] = lines[cls.lineno - 1].replace("class HeatPumpOptimizerCoordinator(", "class _CoordinatorBody(", 1)
lines.insert(cls.end_lineno, '\n\nclass HeatPumpOptimizerCoordinator(_CoordinatorBody):\n'
             '    """Coordinator for Heat Pump Cost Optimizer."""\n')
p.write_text("".join(lines))
