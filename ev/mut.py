import subprocess, sys, os
os.chdir(os.path.expanduser("~/wt-mut"))
O="custom_components/heatpump_optimizer/optimizer.py"; T="custom_components/heatpump_optimizer/thermal_model.py"
M=[
("M1 deferred return linear", O, "return float(_bought_back(p, electrical, len(prices), self.config.dt_hours) * refill_price)", "return float(electrical * refill_price)"),
("M2 terminal law None", O, "_refill_law(params, len(prices), self.config.dt_hours),\n        )", "None,\n        )"),
("M3 refill_law guard always None", O, "    if not params.cop_partload_derate:\n        return None\n    hours", "    if True:\n        return None\n    hours"),
("M4 refill_power_kwh identity", T, "    if not params.cop_partload_derate or hours <= 0.0:\n        return heat_per_cop_kwh", "    if True:\n        return heat_per_cop_kwh"),
("M5 quantile 0.25->0.5", O, "_REFILL_PRICE_QUANTILE = 0.25", "_REFILL_PRICE_QUANTILE = 0.5"),
("M6 copysign dropped", T, "    return math.copysign(\n        power_for_heat_per_cop_kw(params, abs(heat_per_cop_kwh), hours=hours),\n        heat_per_cop_kwh,\n    )", "    return power_for_heat_per_cop_kw(params, abs(heat_per_cop_kwh), hours=hours)"),
("M7 buffer-branch law guard off", O, "            if refill is not None:\n                return refill_price * refill(", "            if False:\n                return refill_price * refill("),
("M8 single-sum law guard off", O, "        if refill is not None:\n            return refill_price * refill(deficit / max(cop_end, 1e-6))", "        if False:\n            return refill_price * refill(deficit / max(cop_end, 1e-6))"),
("M9 refill hours doubled", O, "    hours = _REFILL_PRICE_QUANTILE * n_steps * dt_hours", "    hours = 2 * _REFILL_PRICE_QUANTILE * n_steps * dt_hours"),
("M10 hours<=0 guard dropped", T, "    if not params.cop_partload_derate or hours <= 0.0:", "    if not params.cop_partload_derate:"),
("NULL docstring edit", O, "The price stored heat is bought back at", "The price stored heat is bought back at (null)"),
]
for name, f, a, b in M:
    src=open(f).read(); assert src.count(a)==1, (name, src.count(a))
    open(f,"w").write(src.replace(a,b))
    r=subprocess.run([sys.executable, os.path.expanduser("~/svr_check.py")], env={**os.environ,"PYTHONPATH":"tests/hastub:custom_components:tests"}, capture_output=True, text=True)
    subprocess.run(["git","checkout","-q","--",f])
    print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {r.stdout.splitlines()[0] if r.stdout else r.stderr.strip().splitlines()[-1][:150]}")
print("tree clean:", subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout.strip()=="" )
