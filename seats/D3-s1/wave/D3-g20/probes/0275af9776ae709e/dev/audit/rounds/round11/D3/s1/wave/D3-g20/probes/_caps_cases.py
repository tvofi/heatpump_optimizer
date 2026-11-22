"""_build_space_power_caps inputs: extra caps shorter, equal, longer, empty, 0-d, non-finite; blocked on/off; off steps."""
import numpy as np

N = 96


def cases():
    out = []
    for n in (1, 4, N):
        for blocked in (False, True):
            for off in (None, np.arange(n) % 2 == 0):
                out.append((f"n={n} extra=None blocked={blocked} off={off is not None}", (n, None, blocked, off)))
                for size in sorted({0, 1, n - 1, n, n + 1, 2 * n} - {-1}):
                    for fill in (0.0, 2.5, 99.0, np.nan):
                        out.append((f"n={n} extra.size={size} fill={fill} blocked={blocked} off={off is not None}",
                                    (n, np.full(size, fill), blocked, off)))
                out.append((f"n={n} extra=0-d 2.5 blocked={blocked}", (n, np.float64(2.5), blocked, off)))
    return out


NULL = ("n=96 extra=None blocked=False off=None", (N, None, False, None))
