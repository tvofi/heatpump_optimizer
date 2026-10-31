import subprocess, sys, os, pathlib
wt = pathlib.Path(os.environ["HOME"]) / "wt"
S = sys.argv[1]
BP = "blueprints/automation/notify_wood_cheaper_window.yaml"
TA = "tests/wood_advisor.py"
NEWCOND = """          - >-
            {% set prev = trigger.from_state if trigger.from_state is defined
            else none %}{{ prev is not none and prev.state not in
            ['unavailable', 'unknown'] }}
"""
muts = [
 ("null: comment line", BP, "condition:\n", "# null\ncondition:\n"),
 ("delete prev-state condition", BP, NEWCOND, ""),
 ("drop `prev is not none and`", BP, "prev is not none and prev.state", "prev.state"),
 ("drop 'unavailable' from list", BP, "['unavailable', 'unknown']", "['unknown']"),
 ("drop 'unknown' from list", BP, "['unavailable', 'unknown']", "['unavailable']"),
 ("prev condition -> true", BP, "{{ prev is not none and prev.state not in\n            ['unavailable', 'unknown'] }}", "{{ true }}"),
 ("delete daily branch", BP, "      - \"{{ trigger.id == 'daily' }}\"\n", ""),
 ("daily branch -> false", BP, "\"{{ trigger.id == 'daily' }}\"", "\"{{ false }}\""),
 ("overlap end side <=", BP, "ws <\n            as_timestamp(o.end)", "ws <=\n            as_timestamp(o.end)"),
 ("overlap start side <=", BP, "as_timestamp(o.start) < we", "as_timestamp(o.start) <= we"),
 ("harness eager or/and", TA, "parts = (cond(x) for x in c[\"conditions\"])", "parts = [cond(x) for x in c[\"conditions\"]]"),
]
env = dict(os.environ, PYTHONPATH=f"tests/hastub:{S}/jj")
for name, f, old, new in muts:
    p = wt / f; src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"MUTANT {name}: anchor count {n} -- NOT APPLIED"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, TA], cwd=wt, env=env, capture_output=True, text=True, timeout=200)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.strip().startswith("FAIL")]
        tail = [l for l in out.splitlines() if l.strip()][-1:]
        print(f"MUTANT {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} {tail}")
        for l in fails: print("   ", l.strip()[:200])
        if r.returncode and not fails: print("   ", out[-600:])
    finally:
        p.write_text(src)
st = subprocess.run(["git","status","--porcelain"], cwd=wt, capture_output=True, text=True).stdout
print("RESTORED clean" if not st.strip() else "DIRTY:\n"+st)
