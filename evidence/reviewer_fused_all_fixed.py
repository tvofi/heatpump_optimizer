"""Reviewer's probe (not the finder's): the fused value-and-gradient with every variable fixed."""
import sys
import numpy as np
import heatpump_optimizer.optimizer as om

x0 = np.array([1.0, 2.0, 0.5])
bounds = [(float(v), float(v)) for v in x0]
seen = []


def batch(mat, *_a):
    m = np.atleast_2d(np.asarray(mat, dtype=float))
    seen.append(m.shape[0])
    return np.sum((m - 3.0) ** 2, axis=1)


fun = om._fused_value_and_gradient(batch, bounds, 1e-4)
try:
    value, grad = fun(x0)
except Exception as exc:  # noqa: BLE001
    print(f"RESULT fused all-fixed: raised {type(exc).__name__}: {exc}; batch heights {seen}")
    sys.exit(1)
print(f"RESULT fused all-fixed: value {value}, gradient {grad.tolist()}, batch heights {seen}")
