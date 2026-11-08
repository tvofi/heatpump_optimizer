import subprocess,sys,pathlib
f=pathlib.Path(sys.argv[1])/'tools/plan/replan.py'; orig=f.read_text()
M=[
("then-le","    then = min(int(rec[\"open\"]), sum(1 for i in pending if i < cut))\n","    then = min(int(rec[\"open\"]), sum(1 for i in pending if i <= cut))\n"),
("then-max","    then = min(int(rec[\"open\"]), sum(1 for i in pending if i < cut))\n","    then = max(int(rec[\"open\"]), sum(1 for i in pending if i < cut))\n"),
("then-plus-added-dropped","    return then + added, (","    return then, ("),
]
for name,a,b in M:
    if orig.count(a)!=1: print(name,'ANCHOR',orig.count(a)); continue
    f.write_text(orig.replace(a,b))
    try:
        r=subprocess.run([sys.executable,'-I','tools/plan/replan.py','--self-test'],cwd=sys.argv[1],capture_output=True,text=True,timeout=900,env={'PATH':'/opt/hpo/venv-ci/bin:/usr/bin:/bin','REPLAN_MUTATION_CHILD':'1','HOME':'/root'})
        fails=[l for l in r.stdout.splitlines() if l.startswith('FAIL')]
        print(name,'rc=',r.returncode,'KILLED' if r.returncode else 'SURVIVED',fails[:1],flush=True)
    finally: f.write_text(orig)
