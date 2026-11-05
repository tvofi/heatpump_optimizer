import sys, os, json, shutil, subprocess, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser('~/wt/tests'))
from pathlib import Path
WT = Path(os.path.expanduser('~/wt'))
os.chdir(WT)
import mutation_table as mt
want = {'ledger.py': {309}, 'optimizer.py': {454, 485, 488, 493, 497, 500, 512, 515}}
muts = []
for f, ls in want.items():
    p = (Path('custom_components/heatpump_optimizer') / f).resolve()
    for m in mt._generate(p, True):
        if m['line'] in ls and m['kind'] in mt.RATCHETED:
            muts.append(dict(file='custom_components/heatpump_optimizer/' + f, line=m['line'], kind=m['kind'], old=m['old'], new=m['new']))
src = (WT / 'custom_components/heatpump_optimizer/optimizer.py').read_text().splitlines()
zl = [i + 1 for i, l in enumerate(src) if l.strip() == 'zone = lowers'][0]
muts.append(dict(file='custom_components/heatpump_optimizer/optimizer.py', line=zl, kind='EXTRA_M2', old=src[zl - 1], new=src[zl - 1].replace('lowers', 'rooms')))
lsrc = (WT / 'custom_components/heatpump_optimizer/ledger.py').read_text().splitlines()
bl = [i + 1 for i, l in enumerate(lsrc) if 'baseline_sek = ' in l and '+ stored_sek' in l][0]
muts.append(dict(file='custom_components/heatpump_optimizer/ledger.py', line=bl, kind='PROOF', old=lsrc[bl - 1], new=lsrc[bl - 1].replace(' + stored_sek', '')))
muts.append(dict(file=None, line=0, kind='NULL', old='', new=''))
def run(k_m):
    k, m = k_m
    d = Path(os.path.expanduser(f'~/rv/mut/t{k}'))
    if d.exists(): shutil.rmtree(d)
    shutil.copytree(WT, d, ignore=shutil.ignore_patterns('.git'))
    if m['file']:
        f = d / m['file']; L = f.read_text().split('\n')
        assert L[m['line'] - 1] == m['old'], m
        L[m['line'] - 1] = m['new']; f.write_text('\n'.join(L))
    r = subprocess.run([sys.executable, 'tests/features.py'], cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH='tests/hastub'), timeout=1800)
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if l.startswith('FAIL') or 'FAIL ' in l[:8]]
    summ = [l for l in out.splitlines() if 'FEATURE CHECKS' in l]
    (Path(os.path.expanduser('~/rv/mut')) / f'{k:02d}_{m["kind"]}_{m["line"]}.log').write_text(json.dumps(m) + '\n' + out[-6000:])
    shutil.rmtree(d)
    return k, m, r.returncode, summ[-1] if summ else out[-300:], fails[:6]
with cf.ThreadPoolExecutor(4) as ex:
    for k, m, rc, s, fails in ex.map(run, enumerate(muts)):
        print(f"RESULT mutant {m['file'] and m['file'].split('/')[-1]}:{m['line']} {m['kind']} new=`{m['new'].strip()}` rc={rc} {s}", flush=True)
        for f in fails: print('    ', f[:220], flush=True)
