import numpy as np
def f(x: list[float]) -> list[float]:
    _l = lambda x: np.asarray(x, dtype=float).tolist()  # noqa: E731
    a = _l(x)
    b = _l(x)
    return a + b
