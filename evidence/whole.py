import subprocess, sys, os, importlib.util
W="/tmp/tmp.fZlfDxzmcH"
spec=importlib.util.spec_from_file_location("m",W+"/mutants.py")
src=open(W+"/mutants.py").read(); Msrc=src[src.index("M = ["):src.index("pre = json")]
C="custom_components/heatpump_optimizer/"; ns={"C":C}; exec(Msrc,ns)
name=sys.argv[1]; WT=W+"/wt_"+name
subprocess.run(["git","worktree","add","-q","--detach",WT,"2d010b0913cabbbfc72ace3fc8d203bfb65744f7"],check=True)
_,f,old,new=[m for m in ns["M"] if m[0]==name][0]
p=os.path.join(WT,f); s=open(p).read(); assert s.count(old)==1; open(p,"w").write(s.replace(old,new))
script=sys.argv[2] if len(sys.argv)>2 else "tests/features.py"
r=subprocess.run([sys.executable,script],cwd=WT,env={**os.environ,"PYTHONPATH":"tests/hastub"},capture_output=True,text=True)
fails=[l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
tail=[l for l in r.stdout.splitlines() if "CHECKS" in l][-1:]
print(f"RESULT whole mutant={name} script={script} rc={r.returncode} {tail}")
for l in fails[:12]: print("   ",l[:200])
if r.returncode and not fails: print(r.stderr[-800:])
