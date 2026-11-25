"""_build_comfort_bounds inputs: mold-floor arrays shorter, equal, longer, empty, 0-d, non-finite."""
import numpy as np

N = 96
HOURS = (np.arange(N) * 0.25) % 24.0


def cases():
    out = []
    for n in (1, 4, N):
        hours = HOURS[:n]
        for size in sorted({0, 1, n - 1, n, n + 1, 2 * n} - {-1}):
            for fill in (18.0, 25.0, np.nan, -np.inf):
                out.append((f"n={n} floors.size={size} fill={fill}", (hours, n, None, np.full(size, fill))))
        out.append((f"n={n} floors=0-d 18.0", (hours, n, None, np.float64(18.0))))
        out.append((f"n={n} floors=list[18.0]*{max(n - 1, 0)} margins=0.5", (hours, n, np.full(n, 0.5), [18.0] * max(n - 1, 0))))
    return out


NULL = ("n=96 floors=None margins=None", (HOURS, N, None, None))
