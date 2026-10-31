"""N1b (NULL): reformat one function signature -- tariff.peak_cost_smooth's
eleven parameters, one per line, re-wrapped three or four per line (valid
PEP 8 hanging indent; the AST is identical).
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/tariff.py"
s = read(rel)
before = ast.dump(ast.parse(s))
s = replace_once(s, '''def peak_cost_smooth(
    total_power_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
    threshold_kw: float,
    price_per_kw: float,
    window_minutes: int,
    dt_hours: float,
    peaks_averaged: int = 3,
    offset_steps: int = 0,
    window_factors: np.ndarray | None = None,
    window_days: np.ndarray | None = None,
    distinct_days: bool = True,
) -> float:''', '''def peak_cost_smooth(
    total_power_kw: np.ndarray, baseline_load_kw: np.ndarray, threshold_kw: float,
    price_per_kw: float, window_minutes: int, dt_hours: float,
    peaks_averaged: int = 3, offset_steps: int = 0,
    window_factors: np.ndarray | None = None, window_days: np.ndarray | None = None,
    distinct_days: bool = True,
) -> float:''')
assert ast.dump(ast.parse(s)) == before
write(rel, s)
