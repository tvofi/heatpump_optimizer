import json,subprocess,re,sys
S=sys.argv[1]
runs=json.load(open(S+'/runs.json'))
fail={'jobs':0,'log':0}
out=[]
for r in runs:
    rid=r['databaseId']
    p=subprocess.run(['gh','api','--paginate',f'repos/tvofi/heatpump_optimizer/actions/runs/{rid}/jobs?per_page=100','-q','.jobs[]|select(.name|test("slow"))|[.id,.name,.conclusion]|@tsv'],capture_output=True,text=True)
    if p.returncode: fail['jobs']+=1; print('JOBFAIL',rid,p.stderr[:200]); continue
    for line in p.stdout.strip().splitlines():
        jid,name,concl=line.split('\t')
        if concl in ('skipped','cancelled',''): out.append((rid,jid,name,concl,None,None,r['headSha'],r['event'],r['createdAt'])); continue
        lp=subprocess.run(['gh','api',f'repos/tvofi/heatpump_optimizer/actions/jobs/{jid}/logs','--allow-escape-sequences'],capture_output=True)
        if lp.returncode: fail['log']+=1; print('LOGFAIL',rid,jid,lp.stderr[:200]); continue
        t=lp.stdout.decode('utf-8','replace'); open(f'{S}/logs/{jid}.log','w').write(t)
        m=re.findall(r"cycles over .*?cost \{'cpu_ratio': ([0-9.]+).*?'ref_ms': ([0-9.]+)",t)
        out.append((rid,jid,name,concl,m[0][0] if m else None,m[0][1] if m else None,r['headSha'],r['event'],r['createdAt'],len(m)))
json.dump(out,open(S+'/table.json','w'))
print('FAILURES',fail,'slowjobs',len(out),'with_line',sum(1 for o in out if o[4]))
