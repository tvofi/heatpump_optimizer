"""Fix reviewer's (round 5, #2873) mutants -- reviewer-built. Driver: tests/plan_view.py+tests/card.mjs and tests/debug_collect.py over a git-archive copy of the head.
usage: kmutants_r5.py <archive-dir> <outdir> <name>"""
import os, shutil, subprocess, sys
SRC, OUT, name = sys.argv[1:4]
IN = "custom_components/heatpump_optimizer/inputs.py"; CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M = {"NULL": [],
 "K1_implausible_unworded": [(IN, '    "implausible": "outside its plausible range",\n', '')],
 "K2_sv_p_implausible_deleted": [(CARD, '    "health.p_implausible": "Utanför rimligt intervall",\n', '')],
 "K3_en_p_implausible_deleted": [(CARD, '    "health.p_implausible": "Out of range",\n', '')],
 "K4_stale_unworded": [(IN, '    "stale": "stale",\n', '')],
 # reviewer's own attacks
 "K5_sv_health_stale_deleted": [(CARD, '    "health.stale": "Inaktuell",\n', '')],
 "K6_table_names_unpublished_class": [(IN, '    "stale": "stale",\n', '    "stale": "stale",\n    "bogus": "bogus",\n')],
 "K7_sv_p_implausible_blank": [(CARD, '"health.p_implausible": "Utanför rimligt intervall"', '"health.p_implausible": "  "')],
}
d = os.path.join(OUT, name); shutil.rmtree(d, ignore_errors=True); shutil.copytree(SRC, d)
for f, old, new in M[name]:
    p = os.path.join(d, f); s = open(p).read(); assert s.count(old) == 1, (name, f, s.count(old)); open(p, "w").write(s.replace(old, new))
env = dict(os.environ, PYTHONPATH="tests/hastub", NODE_OPTIONS="--max-old-space-size=8192")
ARMS = (("debug_collect", [sys.executable, "tests/debug_collect.py"]), ("card", ["sh", "-c", "python3 tests/plan_view.py >/dev/null 2>&1 && node tests/card.mjs"]))
for label, cmd in [a for a in ARMS if a[0] in os.environ.get("ARMS", "debug_collect,card").split(",")]:
    r = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr; open(os.path.join(OUT, f"{name}.{label}.log"), "w").write(out)
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL") and "a16:" not in l]
    last = out.strip().splitlines()[-1][:140] if out.strip() else ""
    print(f"RESULT {name} {label}: rc={r.returncode} FAIL(non-a16)={len(fails)} | {last}", flush=True)
    for l in fails[:4]: print("   ", l[:240], flush=True)
shutil.rmtree(d)
