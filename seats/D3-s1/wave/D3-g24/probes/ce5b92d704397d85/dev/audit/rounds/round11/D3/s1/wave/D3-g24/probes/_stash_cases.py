# The input cases every _stash_price_horizon probe of box D3-g24 tries (shared so the five
# CMP/BOOLOP mutants of lines 4696-4720 are searched over one and the same input space).
import numpy as np
N = 4
P = [1.0, 2.0, 3.0, 4.0]
T = [True, True, False, False]
CASES = [
    # name, price_risk_lambda, n_steps, price_known, price_sigma, prices, pv_surplus
    ("pad_known_short(n-1)", 0.0, N, [True] * 3, None, P, [0.5] * 4),
    ("pad_known_exact(n)", 0.0, N, [True] * 4, None, P, [0.5] * 4),
    ("pad_known_long(n+1)", 0.0, N, [True] * 5, None, P, [0.5] * 4),
    ("pad_known_empty(0)", 0.0, N, [], None, P, [0.5] * 4),
    ("pad_pv_short(n-1)", 0.0, N, T, None, P, [0.5] * 3),
    ("pad_pv_exact(n)", 0.0, N, T, None, P, [0.5] * 4),
    ("pad_pv_long(n+1)", 0.0, N, T, None, P, [0.5] * 5),
    ("pad_pv_empty(0)", 0.0, N, T, None, P, []),
    ("pad_pv_int_exact", 0.0, N, T, None, P, [1, 2, 3, 4]),
    ("lam0_sigma_none", 0.0, N, T, None, P, [0.0] * 4),
    ("lam0_sigma_pos", 0.0, N, T, [0.5] * 4, P, [0.0] * 4),
    ("lam0_sigma_inf", 0.0, N, T, [np.inf] * 4, P, [0.0] * 4),
    ("lam0_sigma_nan", 0.0, N, T, [np.nan] * 4, P, [0.0] * 4),
    ("lam_neg_sigma_pos", -0.5, N, T, [0.5] * 4, P, [0.0] * 4),
    ("lam_pos_sigma_none", 0.5, N, T, None, P, [0.0] * 4),
    ("lam_pos_sigma_empty", 0.5, N, T, [], P, [0.0] * 4),
    ("lam_pos_sigma_pos", 0.5, N, T, [0.5] * 4, P, [0.0] * 4),
    ("lam_pos_sigma_pos_all_known", 0.5, N, [True] * 4, [0.5] * 4, P, [0.0] * 4),
    ("lam_pos_sigma_zero", 0.5, N, T, [0.0] * 4, P, [0.0] * 4),
    ("lam_pos_sigma_neg", 0.5, N, T, [-1.0] * 4, P, [0.0] * 4),
    ("lam_pos_sigma_nan_unknown", 0.5, N, T, [0.0, 0.0, np.nan, 0.0], P, [0.0] * 4),
    ("lam_pos_sigma_nan_known", 0.5, N, T, [np.nan, 0.0, 0.0, 0.0], P, [0.0] * 4),
    ("lam_pos_sigma_zero_int_prices", 0.5, N, T, [0.0] * 4, [1, 2, 3, 4], [0.0] * 4),
    ("lam_pos_sigma_zero_negzero_price", 0.5, N, T, [0.0] * 4, [-0.0] * 4, [0.0] * 4),
    ("lam_tiny_sigma_tiny", 5e-324, N, T, [5e-324] * 4, P, [0.0] * 4),
]
