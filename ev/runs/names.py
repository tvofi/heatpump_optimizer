import json,subprocess,shutil,os,sys
spec=json.load(open('/root/ev-runs/spec.json'))
src='/root/wt'
for m in spec:
    d='/root/mut_'+m['name']
    shutil.rmtree(d,ignore_errors=True)
    subprocess.run(f"mkdir {d} && git -C {src} archive HEAD | tar -x -C {d}",shell=True,check=True)
    p=os.path.join(d,m['file']); s=open(p).read(); assert s.count(m['old'])==1
    open(p,'w').write(s.replace(m['old'],m['new']))
    r=subprocess.run(['bash','/root/ev-runs/cmdB_raw.sh'],cwd=d,capture_output=True,text=True)
    open(f"/root/ev-runs/B_{m['name']}.txt",'w').write(r.stdout+r.stderr)
    shutil.rmtree(d,ignore_errors=True)
