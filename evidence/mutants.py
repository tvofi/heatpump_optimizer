import subprocess,sys
S="tools/audit/seat/sweep_render.py"; P="tools/audit/seat/policy_reread_check.py"
M=[
("M1",S,'raise Refused(f"host-path','pass  # (f"host-path'),
("M2",S,"a <= m.start() and m.end() <= b","a <= m.end() and m.start() <= b"),
("M3",S,"    if bad:\n","    if False:\n"),
("M4",S,"    if unknown:\n","    if False:\n"),
("M5",S,"    if unused:\n","    if False:\n"),
("M6",S,"    if missing:\n","    if False:\n"),
("M7",S,"if isinstance(v, bool) or not","if not"),
("M8",P,"if read_at > now:","if False:"),
("M9",P,"if read_at > last:","if read_at >= last.replace(microsecond=0):"),
("M10",P,"if newest is None or at > newest:","if newest is None:"),
("M11",P,' or obj.get("subtype") != MARKER',''),
("M12",P,'            return None, f"transcript line {n} names {MARKER} and is not JSON"','            continue'),
# reviewer's own extra mutants
("X1",S,"if \"\\n\" in s or \"{{\" in s:","if False:"),
("X2",S,"m.group(1) for m in CITED.finditer(text) if not","m.group(1) for m in CITED.finditer(text) if False and not"),
("X3",P,"if at is None:\n            return None","if False:\n            return None"),
("X4",P,"    if read_at is None:\n        return False","    if False:\n        return False"),
]
for name,f,a,b in M:
    src=open(f).read()
    n=src.count(a)
    if n!=1: print(name,"ANCHOR COUNT",n); continue
    open(f,"w").write(src.replace(a,b))
    r=subprocess.run([sys.executable,"-I",f,"--self-test"],capture_output=True,text=True)
    fails=[l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(name, "rc=%d"%r.returncode, "KILLED" if r.returncode else "SURVIVED", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])
    for l in fails: print("   ",l)
    subprocess.run(["git","checkout","--",f]); 
    assert subprocess.run(["git","diff","--quiet"]).returncode==0
