import sys
sys.path[:0] = ["tests", "custom_components"]
import numpy as np
from heatpump_optimizer import optimizer as M
def obj(x, *_a):
    d = np.asarray(x, dtype=float) - np.linspace(-1.0, 1.5, np.size(x))
    return float(np.sum(d * d * (1.0 + 0.3 * np.abs(d))))
def batch(mat, *_a): return np.array([obj(np.array(r)) for r in mat])
def solve():
    n=[0]
    def counted(x,*a): n[0]+=1; return obj(x,*a)
    M._multi_start_minimize(counted, [np.zeros(12), np.full(12, 0.7)], [(-2.0, 2.0)] * 12, maxiter=40, batch_objective=batch, fd_eps=1e-4)
    return n[0]
print("prod", solve())
orig = M._fused_value_and_gradient
M._fused_value_and_gradient = lambda b, bo, e, on_value=None: orig(b, bo, e, None)
print("no memo feed", solve())
