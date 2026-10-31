"""R10-RCA-HARNESS-FRICTION: blocked verdicts and round times per PR.

Usage: python3 rounds.py <dir>, where <dir> holds one <PR>.tsv per merged pull
request of the window: created_at TAB first line, for every issue comment and
review (gh api --paginate repos/tvofi/heatpump_optimizer/issues/<PR>/comments
and .../pulls/<PR>/reviews, --jq ".[]|[.created_at,(.body|split(\"
\")[0])]|@tsv", submitted_at for a review, which has no created_at).
Prints PR, time, class, reason first word, key (harness: class-open folded onto
class-open), and minutes to the next verdict on the same PR; then SUM lines.
"""
import sys,re,glob,os,datetime as dt
rx=re.compile(r'^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})(?:\s+([A-Za-z0-9-]+)\s*:\s*(.*))?')
tot={}
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.tsv'))):
    pr=os.path.basename(f)[:-4]; rows=[]
    for line in open(f):
        t,_,b=line.rstrip('\n').partition('\t'); m=rx.match(b.strip())
        if m and t: rows.append((t,m))
    rows.sort(key=lambda r:r[0])
    for i,(t,m) in enumerate(rows):
        if m.group(1)!='blocked': continue
        cls=m.group(3) or '-'; why=(m.group(4) or '')
        sub=why.split()[0] if why else '-'
        key = 'class-open' if cls=='class-open' or (cls=='harness' and sub=='class-open') else f'{cls}:{sub}' if cls=='harness' else cls
        nxt=rows[i+1][0] if i+1<len(rows) else None
        mins=None
        if nxt:
            p=lambda s:dt.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ')
            mins=round((p(nxt)-p(t)).total_seconds()/60)
        print(f'#{pr}\t{t}\t{cls}\t{sub}\t{key}\t{mins}')
        if key.startswith('class-open') or cls in('harness','class-open'):
            tot.setdefault(key,[]).append(mins or 0)
for k,v in tot.items(): print('SUM',k,len(v),'entries',sum(v),'min')
