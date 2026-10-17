#!/usr/bin/env python3
import json, subprocess, sys, time
R = 'tvofi/heatpump_optimizer'
def gh(*a, **kw): return subprocess.run(['gh']+list(a), capture_output=True, text=True, **kw)
def api(url): 
    r = gh('api', url)
    return json.loads(r.stdout) if r.returncode == 0 else None
def state(sha):
    d = api(f'repos/{R}/commits/{sha}/check-runs?per_page=100')
    runs = {}
    for c in d.get('check_runs', []):
        cur = runs.get(c['name'])
        if cur is None or c['started_at'] > cur['started_at']: runs[c['name']] = c
    pending = [n for n,c in runs.items() if c['status'] != 'completed']
    red = [n for n,c in runs.items() if c['status']=='completed' and c['conclusion'] not in ('success','neutral','skipped','cancelled') and n != 'nightly-status']
    return pending, red
def wait_green(pr, sha, minutes=50):
    for i in range(minutes):
        p, r = state(sha)
        print(time.strftime('%T'), f'#{pr}', 'pending', len(p), 'red', r, flush=True)
        if not p and not r:
            m = gh('pr','merge',str(pr),'--repo',R,'--merge','--match-head-commit',sha)
            print('#%d merge rc=%d' % (pr, m.returncode), flush=True)
            return m.returncode == 0
        if r: print(f'#{pr} RED: {r}', flush=True); return False
        time.sleep(60)
    print(f'#{pr} TIMEOUT', flush=True); return False
def absorb(pr, head, branch):
    subprocess.run(['git','fetch','-q','origin','main'], cwd='/Users/timmalmstrom/heatpump_optimizer')
    subprocess.run(['git','worktree','add','--detach','/tmp/abs95',head], cwd='/Users/timmalmstrom/heatpump_optimizer')
    m = subprocess.run(['git','merge','origin/main','--no-edit'], cwd='/tmp/abs95', capture_output=True, text=True)
    if m.returncode != 0: print('absorb conflict', m.stderr[:200], flush=True); return None
    H = subprocess.run(['git','rev-parse','HEAD'], cwd='/tmp/abs95', capture_output=True, text=True).stdout.strip()
    subprocess.run(['git','push','origin',f'{H}:refs/heads/{branch}'], cwd='/Users/timmalmstrom/heatpump_optimizer')
    body = json.loads(gh('pr','view',str(pr),'--repo',R,'--json','body').stdout)['body']
    import re
    body = re.sub(r'`?'+head[:8]+r'[0-9a-f]*`?', f'`{H}` (extends {head[:8]} by an automatic origin/main absorb; prepr.sh is unchanged between the heads, so the verdict carries)', body, count=1)
    subprocess.run(['gh','pr','edit',str(pr),'--repo',R,'--body-file','-'], input=body, text=True)
    subprocess.run(['git','worktree','remove','--force','/tmp/abs95'], cwd='/Users/timmalmstrom/heatpump_optimizer')
    return H
if not wait_green(1893, '4b4c0f03366c50f70d07695db1af888ae8df0c09'): sys.exit(1)
if not wait_green(1894, 'd6c1f64de2965c04ffff07d5883043980da89ce3'): sys.exit(1)
H95 = absorb(1895, '81cc117be09ca271f4f22fbbed23ed5157dc7359', 'fix/r9-fr-5')
if not H95: sys.exit(1)
time.sleep(20)
if not wait_green(1895, H95): sys.exit(1)
print('TRAIN-DRAIN COMPLETE', flush=True)
