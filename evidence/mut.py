import sys, subprocess, pathlib
f = pathlib.Path("tools/audit/seat/ci_critpath.py"); orig = f.read_text()
M = [
 ("c10-q-empty", 'q = "".join(f"&{k}={v}" for k, v in (("event", event), ("branch", branch)) if v)', 'q = ""'),
 ("c10b-branch-dropped", '(("event", event), ("branch", branch))', '(("event", event),)'),
 ("c10c-event-dropped", '(("event", event), ("branch", branch))', '(("branch", branch),)'),
 ("c10d-keys-swapped", '(("event", event), ("branch", branch))', '(("branch", event), ("event", branch))'),
 ("c10e-q-not-appended", 'page={page}{q}"', 'page={page}"'),
 ("c9-git-first", "p.stdout if p.returncode == 0\n", "p.stdout if False\n"),
 ("c9b-rc-inverted", "p.stdout if p.returncode == 0\n", "p.stdout if p.returncode != 0\n"),
 ("c7-cycle-guard", "        if n in path:\n", "        if False:\n"),
]
for mid, a, b in M:
    n = orig.count(a)
    if n != 1:
        print(f"{mid}: NOT APPLIED count={n}"); continue
    f.write_text(orig.replace(a, b))
    try:
        p = subprocess.run([sys.executable, "-I", str(f), "--self-test"], capture_output=True, text=True, timeout=600)
        out = (p.stdout + p.stderr).strip().splitlines()
        fails = [l for l in out if l.startswith("FAIL")]
        print(f"{mid}: {'KILLED' if p.returncode else 'SURVIVED'} rc={p.returncode} | {out[-1] if out else ''}")
        for l in fails: print("   ", l)
    finally:
        f.write_text(orig)
print("restored clean:", subprocess.run(["git","status","--short"],capture_output=True,text=True).stdout == "")
