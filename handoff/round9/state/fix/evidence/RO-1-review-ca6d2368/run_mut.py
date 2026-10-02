import subprocess, sys, shutil, os
SRC="/home/claude/wt-head/tests/layout.py"
orig=open(SRC).read()
M=[
 ("A ** stops crossing dirs", 'out += ".*"\n            i += 2', 'out += "[^/]*"\n            i += 2'),
 ("B brace keeps first alt only", 'glob[i + 1:j].split(",")', 'glob[i + 1:j].split(",")[:1]'),
 ("C dir ref drops trailing-dot form", r'(?=/|\.(?!\w)|[^\w./-]|\Z)', r'(?=/|[^\w./-]|\Z)'),
 ("D under(): dir entry matches exact only", 'return path.startswith(entry) if entry.endswith("/") else path == entry', 'return path == entry'),
 ("E target(): dir rename drops tail", 'return r["new"] + path[len(r["old"]):] if r["old"].endswith("/") else r["new"]', 'return r["new"]'),
 ("F manifest not skipped", 'skip = [MANIFEST, *hist,', 'skip = [*hist,'),
 ("G enforce never fails", 'if a.enforce and any(found.values()):', 'if False:'),
 ("H grep error ignored", 'if proc.returncode not in (0, 1):', 'if False:'),
 ("I file ref head boundary dropped", r'head = r"(?<![\w.-])"', r'head = r""'),
 ("J enumerate guard dropped (main)", 'if n != count:', 'if False:'),
 ("K self-test vacuity guard n>=len(files) dropped", 'n == count and n >= len(files)', 'n == count'),
 ("L ? matches slash", 'out += "[^/]"', 'out += "."'),
 ("M * crosses dirs", 'out += "[^/]*"\n            i += 1', 'out += ".*"\n            i += 1'),
 ("N retired arm skips since!=null entries", 'if not under(p, r["old"]):', 'if not under(p, r["old"]) or r.get("since"):'),
 ("O dead arm: news ignored", 'if not olds and not news:', 'if not olds:'),
]
res=[]
for name,a,b in M:
    assert orig.count(a)==1,(name,orig.count(a))
    open(SRC,"w").write(orig.replace(a,b))
    try:
        st=subprocess.run([sys.executable,"tests/layout.py","--self-test"],cwd="/home/claude/wt-head",capture_output=True,text=True)
        rp=subprocess.run([sys.executable,"tests/layout.py","--report"],cwd="/home/claude/wt-head",capture_output=True,text=True)
        en=subprocess.run([sys.executable,"tests/layout.py","--enforce"],cwd="/home/claude/wt-head",capture_output=True,text=True)
    finally:
        open(SRC,"w").write(orig)
    counts=[l.strip() for l in rp.stdout.splitlines() if "finding(s)" in l]
    fails=[l.split("self-test: ")[1].split(":")[0] for l in st.stdout.splitlines() if "FAIL" in l]
    res.append((name, st.returncode, rp.returncode, en.returncode, counts, fails))
    print(f"{name}: selftest rc={st.returncode} report rc={rp.returncode} enforce rc={en.returncode} {counts} FAILS={fails}", flush=True)
subprocess.run(["git","diff","--exit-code","tests/layout.py"],cwd="/home/claude/wt-head")
