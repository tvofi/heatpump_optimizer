import subprocess, sys, os, pathlib
wt = pathlib.Path(os.environ["HOME"]) / "wt"; S = sys.argv[1]
F = wt / "custom_components/heatpump_optimizer/wood_fuel.py"
OLD = "    if result is not None and det.suppressing:\n"
muts = [("baseline", OLD), ("GUARD_OFF if True", "    if True:\n"),
        ("BOOLOP or", "    if result is not None or det.suppressing:\n")]
env = dict(os.environ, PYTHONPATH=f"tests/hastub:{S}/jj")
src = F.read_text(); assert src.count(OLD) == 1
for name, new in muts:
    F.write_text(src.replace(OLD, new))
    try:
        for t in ["tests/features.py", "tests/guard_pins.py", "tests/wood_advisor.py"]:
            r = subprocess.run([sys.executable, t], cwd=wt, env=env, capture_output=True, text=True, timeout=1500)
            lines = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
            fails = [l.strip()[:160] for l in lines if l.strip().startswith("FAIL")]
            print(f"{name} | {t}: rc={r.returncode} {lines[-1:]} {fails[:3]}", flush=True)
    finally:
        F.write_text(src)
st = subprocess.run(["git","status","--porcelain"], cwd=wt, capture_output=True, text=True).stdout
print("RESTORED clean" if not st.strip() else "DIRTY:\n"+st)
