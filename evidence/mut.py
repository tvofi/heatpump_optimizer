import sys, subprocess, shutil, os
W, S = sys.argv[1], sys.argv[2]
HC="custom_components/heatpump_optimizer/heat_curve.py"
M=[
 ("M21 adoption bound removed", 'baseline = _within_range(reading.value - (state["written"] - baseline), reading)', 'baseline = reading.value - (state["written"] - baseline)'),
 ("M22 helper ceiling side deleted", "    if reading.hi is not None:\n        value = min(reading.hi, value)\n", ""),
 ("M23 helper floor side deleted", "    if reading.lo is not None:\n        value = max(reading.lo, value)\n", ""),
 ("M24 adoption bounds floor only", 'baseline = _within_range(reading.value - (state["written"] - baseline), reading)', 'baseline = max(reading.lo, reading.value - (state["written"] - baseline))'),
 ("M25 plan target unbounded", "    target = _within_range(banded, reading)\n", "    target = banded\n"),
 ("M26 reserve +2 -> +1 (budget 1 writes)", "writes_today(state, now) + 2 > budget", "writes_today(state, now) + 1 > budget"),
 ("M27 adoption clamps to the old baseline's band instead", 'baseline = _within_range(reading.value - (state["written"] - baseline), reading)', 'baseline = _within_range(reading.value - (state["written"] - baseline), reading._replace(lo=None, hi=None)) if hasattr(reading, "_replace") else reading.value - (state["written"] - baseline)'),
]
for name, old, new in M:
    d=os.path.join(S,"mt"); shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(W, d, ignore=shutil.ignore_patterns(".git"))
    p=os.path.join(d,HC); src=open(p).read(); n=src.count(old)
    if n!=1: print(f"{name}: APPLY-FAIL count={n}", flush=True); continue
    open(p,"w").write(src.replace(old,new))
    r=subprocess.run(["bash",os.path.join(S,"mcmd.sh"),d],capture_output=True,text=True,timeout=900)
    out=r.stdout+r.stderr
    fails=[l.strip()[:140] for l in out.splitlines() if l.lstrip().startswith("FAIL")]
    last=out.strip().splitlines()[-1][:120] if out.strip() else ""
    print(f"{name}: rc={r.returncode} {last} | " + " || ".join(fails[:4]), flush=True)
