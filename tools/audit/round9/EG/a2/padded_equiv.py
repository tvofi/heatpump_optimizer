"""PYTHONPATH=tests/hastub python3 tools/audit/round9/EG/a2/padded_equiv.py [tree] (R9-EG-A2, #1874): optimizer._padded_nonneg against its CMP_BOUND mutant (`<` -> `<=`) on every size
0..n+3 for n in 1..96 and three value draws, counting the ties (size == n_steps, the only inputs the arms
differ on) and the differing outputs; then a tie-only control (pads one extra zero at a tie) that must differ
on every tie."""
import sys, numpy as np
from pathlib import Path
root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[5])
sys.path[:0] = [root + "/custom_components", root + "/tests/hastub"]
from heatpump_optimizer.optimizer import _padded_nonneg as head
def mutant(values, n):
    series = np.clip(np.asarray(values, dtype=float), 0.0, None)
    if series.size <= n:
        series = np.concatenate([series, np.zeros(n - series.size)])
    return series[:n]
def control(values, n):
    series = np.clip(np.asarray(values, dtype=float), 0.0, None)
    if series.size == n:
        return np.concatenate([series[:-1], series[-1:] + 1.0])
    return head(values, n)
rng = np.random.default_rng(5); cases = ties = diff = cdiff = 0
for n in range(1, 97):
    for size in range(0, n + 4):
        for _ in range(3):
            v = rng.normal(0, 2, size)
            a, b, c = head(v, n), mutant(v, n), control(v, n)
            cases += 1; tie = size == n; ties += tie
            diff += not (a.dtype == b.dtype and a.shape == b.shape and np.array_equal(a, b))
            cdiff += tie and not np.array_equal(a, c)
print(f"cases {cases} ties {ties} head-vs-mutant differing {diff} tie-only control differing on ties {cdiff}")
