import re,sys
for f in sys.argv[1:]:
    rows={}
    for l in open(f):
        m=re.match(r'\s*(spread|flat) \(([\d.]+), ([\d.]+), (\w+), (\w+)\) plan (\w+).*savings (\S+)',l)
        if m: d,s,v,w,sp,h,sv=m.groups(); rows[(d,s,float(v),w,sp)]=(h,sv)
    same=diff=0; nob={}
    for (d,s,v,w,sp),(h,sv) in rows.items():
        if v>0:
            h0=rows[(d,s,0.0,w,sp)][0]
            same+= h==h0; diff+= h!=h0
    print(f, 'cells',len(rows),'buffer-plan identical to no-buffer twin:',same,'differ:',diff)
