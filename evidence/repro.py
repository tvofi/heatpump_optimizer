import yaml,subprocess,tempfile,sys
from pathlib import Path
# Mirrors tests/entities.py _pg_plan_defects' release-checkout run (scratch repo, no origin, bash -eo pipefail)
for label, rev in (("base bb6377b4", "bb6377b4dad4e398d1a28bde54d30036a5b25a82"), ("head e04a759e", "e04a759e943b5fcf01dfd39487d2454c47dd927b")):
    wf=yaml.safe_load(subprocess.run(["git","show",f"{rev}:.github/workflows/pages.yml"],capture_output=True,text=True,check=True).stdout)
    st=[s for s in wf['jobs']['pages-build']['steps'] if s.get('name')=='Check out the release'][0]['run']
    with tempfile.TemporaryDirectory() as tmp:
        repo=Path(tmp)/'repo'; repo.mkdir()
        g=['git','-c','user.name=t','-c','user.email=t@t']
        subprocess.run(['git','init','-q'],cwd=repo,check=True)
        for t in ('v1.9.0','v1.10.0','x9'):
            (repo/'f').write_text(t); subprocess.run(g+['add','f'],cwd=repo,check=True); subprocess.run(g+['commit','-qm',t],cwd=repo,check=True); subprocess.run(g+['tag',t],cwd=repo,check=True)
        r=subprocess.run(['bash','--noprofile','--norc','-eo','pipefail','-c',st],cwd=repo,capture_output=True,text=True)
        print(f"{label}: rc={r.returncode} f={(repo/'f').read_text()!r} -> {'PASS' if r.returncode==0 and (repo/'f').read_text()=='v1.10.0' else 'FAIL'}; stderr={r.stderr.strip().splitlines()[:1]}")
