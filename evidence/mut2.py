import re,subprocess,os,pathlib,sys
C=pathlib.Path('.'); Y=C/'.github/workflows/governance.yml'; F=C/'tools/policy/policy_lint.mjs'
yo=Y.read_text(); fo=F.read_text(); py=sys.argv[1]
def m0(t):
    out=[];skip=False
    lines=t.split('\n');i=0
    while i<len(lines):
        l=lines[i]
        if l.startswith('      - name: GITHUB_TOKEN rate limit'):
            # drop the step up to the next step/comment at 6 spaces or blank
            i+=1
            while i<len(lines) and lines[i].startswith('        '): i+=1
            continue
        out.append(l);i+=1
    n='\n'.join(out); assert 'rate_limit' not in n.split('jobs:')[1].split('delivery-status:')[0].replace('rate_limit"','') or True; return n
M=[('M0 both rate_limit steps deleted',Y,m0),
   ('M2 concurrency block deleted',Y,lambda t:t.replace("    concurrency:\n      group: governance-record\n      cancel-in-progress: false\n","")),
   ('M1-yaml all --window-cache flags dropped from the job',Y,lambda t:t.replace(' --window-cache "$RUNNER_TEMP/window.json"','').replace('            --window-cache "$RUNNER_TEMP/window.json" \\\n','')),
   ('R1b ok-guard on map write deleted',F,lambda t:t.replace("  if (fetched.ok) writeWindowCache(cacheFile, since, { pullsBySha:","  writeWindowCache(cacheFile, since, { pullsBySha:")),
]
for name,f,fn in M:
    Y.write_text(yo);F.write_text(fo)
    t=f.read_text();n=fn(t);assert n!=t,name;f.write_text(n)
    d=subprocess.run(['git','diff','--stat'],capture_output=True,text=True).stdout.strip().splitlines()[-1]
    a=subprocess.run(['node','tools/policy/policy_lint.mjs'],capture_output=True,text=True)
    al=[l[:200] for l in a.stdout.splitlines() if l.startswith('FIXTURE')]
    e=subprocess.run([py,'tests/entities.py'],capture_output=True,text=True,env={**os.environ,'PYTHONPATH':'tests/hastub'})
    el=(e.stdout+e.stderr).strip().splitlines()[-1]
    w=subprocess.run(['node','tools/policy/check-wave-script.mjs'],capture_output=True,text=True)
    wl=(w.stdout+w.stderr).strip().splitlines()[-1][:150] if (w.stdout+w.stderr).strip() else ''
    print(f"MUTANT {name} ({d})\n  acceptance rc={a.returncode} {al}\n  entities rc={e.returncode} {el}\n  check-wave-script rc={w.returncode} {wl}",flush=True)
Y.write_text(yo);F.write_text(fo)
print('restored:',subprocess.run(['git','status','--porcelain'],capture_output=True,text=True).stdout or 'clean')
