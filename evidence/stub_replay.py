# Reviewer's own instrument: run the real launcher + waiter + bg_unread steps of a workflow
# exactly as GitHub does (bash -e, no pipefail unless the step sets it), with the five
# detached commands replaced by fast stubs. argv: WF FAILNAME|none [drop-step-name] [lib-old lib-new]
import sys, re, subprocess, tempfile, os, yaml
wf, fail = sys.argv[1], sys.argv[2]
drop = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
sub = (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else None
st = yaml.safe_load(open(wf))['jobs']['instrument-self-tests']['steps']
L = "Start the five slowest self-tests beside the rest of the job"
tally = {'prepr': 'prepr self-test: 3 checks, 0 failed',
         'beatd': 'beatd self-test: 3 checks, 0 failed',
         'open-pr': 'delivery_row self-test: 2 checks, 0 failed\npr_args self-test: 2 checks, 0 failed',
         'pr-args': 'pr_args self-test: 2 checks, 0 failed',
         'update-pr': 'delivery_row self-test: 2 checks, 0 failed\npr_args self-test: 2 checks, 0 failed'}
def stub(n):
    if n == fail: return f"bash -c 'sleep 2; printf \"%s\\n\" \"{tally[n]}\"; exit 3'"
    return f"bash -c 'sleep 2; printf \"%s\\n\" \"{tally[n]}\"'"
env = dict(os.environ, RUNNER_TEMP=tempfile.mkdtemp())
red = False
for s in st:
    if 'run' not in s: continue
    r = s['run']
    if s['name'] == L:
        if sub: assert r.count(sub[0]) == 1, 'mutant not applied'; r = r.replace(*sub)
        r = re.sub(r'(bg_(?:start|run) (prepr|beatd|open-pr|pr-args|update-pr)) .*?(?= \) <|\n|$)', lambda m: f"{m.group(1)} {stub(m.group(2))}", r)
    elif not re.search(r'\bbg_(wait|unread)\b', r): continue
    if drop and s['name'] == drop: continue
    if red and '!cancelled()' not in s.get('if', ''): print('SKIP', s['name']); continue
    f = tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False); f.write(r); f.close()
    p = subprocess.run(['bash', '--noprofile', '--norc', '-e', f.name], env=env, capture_output=True, text=True)
    red |= p.returncode != 0
    print('OK  ' if p.returncode == 0 else 'FAIL', s['name'], '|', (p.stderr.strip().splitlines() or [''])[-1])
print('JOB', 'RED' if red else 'GREEN')
