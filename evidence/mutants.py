import subprocess, sys, os
S="/Users/timmalmstrom/hpo-seats/r10s3/review-n-log-flood"; W=S+"/wt"
PY="/Users/timmalmstrom/heatpump_optimizer/tools/audit/seat/shims/seat-python"
F=W+"/custom_components/heatpump_optimizer/log_latch.py"
M=[("70f837e7","    if not active:","    if False:","tests/solar_alignment.py"),
   ("80a0007e","    return True","    pass","tests/solar_alignment.py"),
   ("96c9f042","        return False","        pass","tests/solar_alignment.py"),
   ("83745963","        if held.pop(key, None) is not None:","        if False:","tests/features.py"),
   ("da0bf41e","    if held.get(key) == text:","    if False:","tests/features.py")]
orig=open(F).read()
env=dict(os.environ, PYTHONPATH="tests/hastub")
try:
    for h,old,new,script in M:
        lines=orig.split("\n"); idx=[i for i,l in enumerate(lines) if l==old]
        assert len(idx)==1,(h,idx); lines[idx[0]]=new
        open(F,"w").write("\n".join(lines))
        r=subprocess.run([PY,script],cwd=W,env=env,capture_output=True,text=True)
        out=r.stdout+r.stderr
        open(f"{S}/evidence/mutant.{h}.txt","w").write(out)
        fails=[l for l in out.splitlines() if "FAIL" in l][:3]
        print(f"RESULT mutant_{h} script={script} rc={r.returncode} killed={r.returncode!=0}", fails, flush=True)
finally:
    open(F,"w").write(orig)
print("restored", subprocess.run(["git","-C",W,"status","--porcelain","--","custom_components"],capture_output=True,text=True).stdout or "clean")
