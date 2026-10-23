import subprocess,pathlib,re,sys
F=pathlib.Path('.github/workflows/governance.yml'); orig=F.read_text()
C=' --window-cache "$RUNNER_TEMP/window.json"'
lines=orig.split('\n')
def drop_line(s,i): 
    L=s.split('\n'); assert C.strip() in L[i-1], (i,L[i-1]); 
    L[i-1]=L[i-1].replace('--window-cache "$RUNNER_TEMP/window.json"','');return '\n'.join(L)
def nth(s,n,new):
    idx=-1
    for _ in range(n+1): idx=s.index(C,idx+1)
    return s[:idx]+new+s[idx+len(C):]
M={
 'M1-yaml': orig.replace(C,''),
 'Y1': nth(orig,3,''),
 'E1-sunset-tools-only': nth(orig,4,''),
 'E2-record-only': drop_line(orig,1249),
 'E3-other-file': nth(orig,2,' --window-cache "$RUNNER_TEMP/window2.json"'),
 'E4-stats-claude-only': nth(orig,1,''),
}
assert orig.count(C)==5-1 or True
print('occurrences of the flag on one line form:',orig.count(C))
names=sys.argv[1:] or ['null']+list(M)
for n in names:
    F.write_text(orig if n=='null' else M[n])
    r=subprocess.run([sys.executable,'tests/entities.py'],capture_output=True,text=True,env={'PYTHONPATH':'tests/hastub','PATH':'/opt/hpo/venv-ci/bin:/opt/node22/bin:/usr/bin:/bin'})
    out=r.stdout+r.stderr
    hits=[l for l in out.splitlines() if ('window-cache' in l or "record job's three" in l or 'record-job invocation' in l)]
    tail=out.strip().splitlines()[-1:] 
    print(f'== {n} rc={r.returncode}'); print('\n'.join(hits[:6])); print(' tail:',tail)
F.write_text(orig)
