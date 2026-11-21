import subprocess, sys, json, os
R='/home/user/heatpump_optimizer'
M='R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'
E='R.section("Room history and the identifiability report")'
muts=json.load(open(sys.argv[1]))
for m in muts:
    p=os.path.join(R,m['file']); src=open(p).read()
    n=src.count(m['old'])
    if n!=1:
        print(f"MUT {m['id']}: SKIP old occurs {n} times"); continue
    open(p,'w').write(src.replace(m['old'],m['new']))
    try:
        cmd=['python3','tools/audit/seat/features_block.py','--prelude',f"exec(open('{os.environ['HOME']}/rev/prelude.py').read())",M]
        if m.get('scope')=='A': cmd.append(E)
        r=subprocess.run(cmd,cwd=R,capture_output=True,text=True,env={**os.environ,'PYTHONPATH':'tests/hastub'})
        out=r.stdout+r.stderr
        fails=[l for l in out.splitlines() if l.startswith('FAIL') or 'Error' in l][:4]
        summ=[l for l in out.splitlines() if 'BLOCK' in l and ('PASSED' in l or 'FAILED' in l)]
        print(f"MUT {m['id']}: rc={r.returncode} {summ[-1] if summ else 'no-summary'}")
        for f in fails: print('   ',f[:220])
    finally:
        open(p,'w').write(src)
