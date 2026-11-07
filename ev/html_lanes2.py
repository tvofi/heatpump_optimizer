import re,json,collections
def parse(path):
    s=open(path).read()
    k=[m.start() for m in re.finditer(r'<svg viewBox="0 0 1180 \d+" width="1180" role="img" aria-label="Swimlanes"',s)][-1]
    svg=s[k:s.index('</svg>',k)]
    lanes=[(int(y),int(h),l) for y,h,l in re.findall(r'<rect x="0" y="(\d+)" width="1180" height="(\d+)" class="lane"/><text x="10" y="\d+" class="lanelab">([^<]+)</text>',svg)]
    out={}
    for t,y in re.findall(r'<title>R10-([^:]+):.*?</title><rect x="[\d.]+" y="(\d+)"',svg):
        for ly,h,l in lanes:
            if ly<=int(y)<ly+h: out[t]=l
    return lanes,out
lb,db=parse("plan-wtbase.html");lh,dh=parse("plan-wt.html")
P=json.load(open("plan-wt.json"))["groups"];PB=json.load(open("plan-wtbase.json"))["groups"]
print("lanes",[l for _,_,l in lh])
for tag,d,pj in(("base",db,PB),("head",dh,P)):
    bad=[n for n,l in d.items() if pj["R10-"+n]["lane"]!=l]
    print(tag,"drawn",len(d),"html!=json",len(bad),dict(collections.Counter(d.values())))
mv=sorted(n for n in dh if db.get(n)!=dh[n])
print("drawn moved",len(mv),collections.Counter((db.get(n),dh[n]) for n in mv))
print("drawn moved json-moved check:",all(PB["R10-"+n]["lane"]!=P["R10-"+n]["lane"] for n in mv))
print(mv)
# table lanec per row
for f,pj in(("plan-wtbase.html",PB),("plan-wt.html",P)):
    s=open(f).read()
    rows=re.findall(r'<td class="g">([^<]+)<div class="lanec">([^<]+)</div>',s)
    print(f,"table rows",len(rows),"table!=json",sum(1 for n,l in rows if pj["R10-"+n]["lane"]!=l))
