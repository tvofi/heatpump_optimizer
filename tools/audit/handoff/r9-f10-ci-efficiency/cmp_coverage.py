import json,sys
def load(p):
    d=json.load(open(p)); f=d['files']
    return d['totals'], {k:(tuple(sorted(v['executed_lines'])),v['summary']['num_statements']) for k,v in f.items()}
ta,a=load(sys.argv[1]); tb,b=load(sys.argv[2])
print('totals', ta['percent_covered'], ta['covered_lines'], ta['num_statements'], '|', tb['percent_covered'], tb['covered_lines'], tb['num_statements'])
diff=[k for k in set(a)|set(b) if a.get(k)!=b.get(k)]
print('files differing:',len(diff))
for k in sorted(diff)[:10]:
    ea=set(a.get(k,((),0))[0]); eb=set(b.get(k,((),0))[0]); print(' ',k,'only-first',sorted(ea-eb)[:12],'only-second',sorted(eb-ea)[:12])
