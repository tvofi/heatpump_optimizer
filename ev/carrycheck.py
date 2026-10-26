import json,re,sys
body=open("body_live.md").read()
item=re.search(r'The exact carry text: "(.*?)" Carry: R10-ERREXIT', body, re.S).group(1)
for r in ["95e478db3","origin_handoff_audit-r10-roster"]:
    d=json.load(open(f"roster_{r}.json"))
    gs=d["groups"]; it=gs.items() if isinstance(gs,dict) else [(g.get("id"),g) for g in gs]
    g=[v for k,v in it if k=="R10-ERREXIT-COUNTERMEASURES" or (isinstance(v,dict) and v.get("group")=="R10-ERREXIT-COUNTERMEASURES")][0]
    print(r,"keys",sorted(g.keys()),"resume",g.get("resume"),"after",g.get("after"))
    c=g.get("carry") or []
    txt=[x if isinstance(x,str) else (x.get("text") or json.dumps(x)) for x in c]
    joined="\n".join(txt)+"\n"+(g.get("brief") or "")
    for i,x in enumerate(txt): print(" carry",i,len(x),repr(x[:130]))
    segs=[s.strip() for s in re.split(r'(?=\(\d\) )', item) if s.strip()]
    for s in segs: print("  seg",repr(s[:45]),"verbatim-in-roster:", s in joined)
    print(" whole item verbatim:", item in joined)
    for k in ["mutation proof","null","REFUSED","hits=0","re-measure","e0ffb1213"]: print("   has",k, k in joined)
