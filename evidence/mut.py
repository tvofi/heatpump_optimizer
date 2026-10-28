import json, subprocess, sys, os, re
root = sys.argv[1]; out = sys.argv[2]; only = sys.argv[3:] 
T = "custom_components/heatpump_optimizer/thermal_model.py"
C = "custom_components/heatpump_optimizer/coordinator.py"
M = {
 "E": (T, "    if a and not scale_bounds[0] <= new_scale <= scale_bounds[1]:\n        again = reanchor_heat_loss(then, now, scale, ratio, (0.0, b), **bounds)\n        return again[0], again[1], True, again[3]\n", ""),
 "F": (T, "if a and not scale_bounds[0] <= new_scale", "if False and not scale_bounds[0] <= new_scale"),
 "G": (C, "        if scale_reset:\n", "        if False:\n"),
 "H": (T, "return again[0], again[1], True, again[3]", "return again[0], again[1], True, False"),
 "A": (C, "        self._apply_lower_floor_loss_ratio(new_ratio)\n        return True\n", "        return True\n"),
 "B": (C, "        if void:\n            self._house_heat_loss_samples = self._lower_floor_loss_samples = 0\n", "        if void:\n            pass\n"),
 "C1": (T, "    if b and not ratio_bounds[0] <= new_ratio <= ratio_bounds[1]:\n", "    if False:\n"),
 "C2": (T, "return (*reanchor_heat_loss(then, now, scale, ratio, (a, 0.0), **bounds)[:3], True)", "return new_scale, 1.0, False, True"),
 "D": (T, "        if void or abs(now[1] * then[0] / (now[0] * then[1]) - 1.0) > step:\n", "        if True:\n"),
 "bS_floor": (T, "not scale_bounds[0] <= new_scale", "not scale_bounds[0] < new_scale"),
 "bS_ceil": (T, "new_scale <= scale_bounds[1]", "new_scale < scale_bounds[1]"),
 "bR_floor": (T, "not ratio_bounds[0] <= new_ratio", "not ratio_bounds[0] < new_ratio"),
 "bR_ceil": (T, "new_ratio <= ratio_bounds[1]", "new_ratio < ratio_bounds[1]"),
 "b_split": (T, "- 1.0) > step:", "- 1.0) >= step:"),
 "b_total": (T, "abs(total_now / total_then - 1.0) <= step", "abs(total_now / total_then - 1.0) < step"),
 "b_lower": (T, "lower_then > 1e-9", "lower_then >= 1e-9"),
 "b_upper": (T, "min(upper) > 1e-9", "min(upper) >= 1e-9"),
 # reviewer's own
 "R1_recurse_zero_b": (T, "(0.0, b), **bounds)", "(0.0, 0.0), **bounds)"),
 "R2_ratio_reset_flag": (C, "        if ratio_reset:\n", "        if False:\n"),
 "R3_lnow_guard": (T, "    if l_now <= 0:\n        return new_scale, ratio, False, False\n", ""),
 "R4_root_form": (T, "if lin <= 0 else", "if lin < 0 else"),
 "R5_basis_voids_lt": (T, "bases.index(stored) < bases.index(basis)", "bases.index(stored) != bases.index(basis)"),
 "R6_scale_a_guard": (T, "if a and not scale_bounds[0]", "if not scale_bounds[0]"),
}
res = {}
for k, (f, old, new) in M.items():
    if only and k not in only: continue
    p = os.path.join(root, f); src = open(p).read()
    n = src.count(old)
    if n != 1: res[k] = {"error": f"site count {n}"}; print(k, "SITE", n, flush=True); continue
    open(p, "w").write(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tests/_rv_prefix.py"], cwd=root, capture_output=True, text=True,
                           env={**{x: y for x, y in os.environ.items() if x != "BASH_ENV"}, "PYTHONPATH": "tests/hastub"}, timeout=1200)
        fails = [l.strip() for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        res[k] = {"rc": r.returncode, "fails": fails, "tail": r.stdout.strip().splitlines()[-1:] + r.stderr.strip().splitlines()[-2:]}
    finally:
        open(p, "w").write(src)
    print(k, "rc", r.returncode, len(fails), flush=True)
json.dump(res, open(out, "w"), indent=1)
