import subprocess
f=".github/workflows/tests.yml"; src=open(f).read()
for job in ("mutation-pins:\n    needs: [mutation]\n","mutation-autofix:\n    needs: [mutation, mutation-pins]\n"):
    i=src.index("  "+job); j=src.index("&& needs.mutation.result == 'failure'",i)
    k=j+len("&& needs.mutation.result == 'failure'")
    mut=src[:k]+"\n      && inputs.machinery != 'false'"+src[k:]
    open(f,"w").write(mut)
    p=subprocess.run(["python3","-I","dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py"],capture_output=True,text=True)
    open(f,"w").write(src)
    o=p.stdout.strip().splitlines()
    print(f"MUTANT tests.yml {job.split(':')[0]} if += '&& inputs.machinery != false': rc={p.returncode} :: "+" | ".join(l for l in o if 'pins jobs' in l or 'GATE' in l))
print("clean:",subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "yes")
