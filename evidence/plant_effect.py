"""Does a plant the guard passes change the replay's outputs? (stub solver)"""
import sys
P = sys.argv[1]; sys.argv = ["x", "stub"]
import fork_equiv as fe
from heatpump_optimizer.optimizer import HeatPumpOptimizer
HeatPumpOptimizer.optimize = fe.stub_optimize
sys.argv = ["x", P]
import guard_plants  # noqa: installs the planted cycle and runs check_fork
b = fe.head
arms = {"channel_boost": "channel", "mode_boost": "mode"}
sh = b.replay(arms); un = b.replay(arms, fork=0)
for a in arms:
    d = fe.diff_fields(sh[a], un[a])
    print("RESULT effect", P, a, "EQUAL" if not d else "DIFFERENT " + ",".join(d))
