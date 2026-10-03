"""PYTHONPATH=tests/hastub python3 tools/audit/round9/EG/a2/padded_equiv.py [tree] (R9-EG-A2, #1874):
optimizer._padded_nonneg against its CMP_BOUND mutant (`<` -> `<=`), the mutant built from the function's
own source with that one comparison flipped, on every size 0..n+3 for n in 1..96 and three value draws of
1-D input (every caller passes a per-step series), counting the ties (size == n_steps, the only inputs the
arms differ on) and the differing outputs; then a tie-only control (adds 1 to the last entry at a tie) that
must differ on every tie, and the 2-D case, where the mutant raises and is NOT equivalent."""
import inspect, sys, textwrap
from pathlib import Path
import numpy as np
root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[5])
sys.path[:0] = [root + "/custom_components", root + "/tests/hastub"]
from heatpump_optimizer import optimizer
head = optimizer._padded_nonneg
src = textwrap.dedent(inspect.getsource(head))
assert src.count("if series.size < n_steps:") == 1, "the site moved: re-key the triage and this probe"
ns = dict(vars(optimizer))
exec(compile(src.replace("if series.size < n_steps:", "if series.size <= n_steps:"), "<mutant>", "exec"), ns)
mutant = ns["_padded_nonneg"]
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
try:
    mutant(np.ones((2, 3)), 6); two_d = "same"
except ValueError:
    two_d = "mutant raises"
print(f"cases {cases} ties {ties} head-vs-mutant differing {diff} tie-only control differing on ties {cdiff}; "
      f"2-D input at a tie: {two_d}")
