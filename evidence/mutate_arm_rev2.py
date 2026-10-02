import re, subprocess, sys, os
WT = os.path.abspath(sys.argv[1])
base = subprocess.run(["git", "diff", "-U0", "03ba7f70f007147bda32ac0fc5dd83b11499bbaf", "HEAD", "--", "tests/doc_claims.py"], cwd=WT, capture_output=True, text=True).stdout
added = set()
cur = 0
for l in base.splitlines():
    m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", l)
    if m: cur = int(m.group(1)); continue
    if l.startswith("+") and not l.startswith("+++"): added.add(cur); cur += 1
src = open(os.path.join(WT, "tests/doc_claims.py")).read().split("\n")
sites = []
for i in sorted(added):
    l = src[i-1]; s = l.strip()
    if re.match(r"(errs|out)\.append\(", s) or re.match(r"(el)?if .*:$", s) or s.startswith("res[\"fails\"] = ["):
        sites.append(i-1)
print(len(sites), "mutable lines among", len(added), "added lines")
mut = os.path.join(WT, "tests/_mut_doc_claims.py")
py = os.path.expanduser("~/hpo-seats/R9-F11.4-venv/bin/python3")
surv = 0
for i in sites:
    m = list(src); l = m[i]; ind = l[:len(l)-len(l.lstrip())]; s = l.strip()
    if re.match(r"(el)?if .*:$", s): m[i] = ind + ("elif False:" if s.startswith("elif") else "if False:")
    elif s.startswith("res[\"fails\"] = ["): m[i] = ind + "res[\"fails\"] = []"
    else:
        # a multi-line append: blank only a one-line one; otherwise comment the call out by wrapping
        if s.count("(") == s.count(")"): m[i] = ind + "pass"
        else: continue
    open(mut, "w").write("\n".join(m))
    r = subprocess.run([py, os.path.join(os.path.dirname(WT), "scratch", "arm_driver.py"), WT, mut], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
    out = (r.stdout.strip().splitlines() or [r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "no output"])[-1]
    killed = (("in_tree_failures=" in out) and ("in_tree_failures=0" not in out)) or ("MISS" in out); crash = "in_tree_failures=" not in out; killed = killed and not crash; print("CRASH" if crash else "", end="")
    surv += not killed
    print(f"{'KILLED  ' if killed else 'SURVIVED'} L{i+1}: {s[:80]} -> {out[:70]}")
os.remove(mut)
print("SURVIVORS:", surv)
