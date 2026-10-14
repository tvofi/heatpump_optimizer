import re,sys,ast,os,statistics as st
rows=[]
for line in open(sys.argv[1]):
    rid,ts,sha,ev,jid,jc=line.split()
    p=f"logs/{jid}.log"
    if not os.path.exists(p): continue
    t=open(p,errors='replace').read()
    cl=re.findall(r"cycles over \d+ entities.*?cost (\{[^}]*\})",t)
    hot=re.findall(r"cpu doubled at \S+ cost (\{[^}]*\})",t)
    mem=re.findall(r"memory doubled at \S+ cost (\{[^}]*\})",t)
    nc=len(cl);nh=len(hot)
    if not cl or not hot: rows.append((ts[:10],rid,ev,jc,nc,nh,None,None,None,None));continue
    c=ast.literal_eval(cl[0]);h=ast.literal_eval(hot[0]);m=ast.literal_eval(mem[0]) if mem else {}
    rows.append((ts[:10],rid,ev,jc,nc,nh,c['cpu_ratio'],h['cpu_ratio'],h['cpu_ratio']/c['cpu_ratio'],(m.get('peak_kib',0)/c['peak_kib']) if m else None))
for r in rows: print(*[f"{x:.4f}" if isinstance(x,float) else x for x in r])
ok=[r for r in rows if r[8]]
print("timed:",len(ok),"of",len(rows)," ev:",{e:sum(1 for r in ok if r[2]==e) for e in ('schedule','workflow_dispatch')})
print("hot/clean min %.4f max %.4f"%(min(r[8] for r in ok),max(r[8] for r in ok)))
print("clean min %.4f (%s) max %.4f"%(min(r[6] for r in ok),min(ok,key=lambda r:r[6])[0],max(r[6] for r in ok)))
mm=[r[9] for r in ok if r[9]];print("mem hot/clean %.4f-%.4f"%(min(mm),max(mm)))
print("red (hot<=3.576? no: hot>... ) arms under cap:",[(r[0],r[1],r[7]) for r in ok if r[7]<=3.576])
