import re,sys,glob,os,json
card=open(sys.argv[1]).read(); shots=sys.argv[2]
keys=["score.driver_cop_shortfall","score.driver_cheap_hours","score.driver_dear_hours","score.driver_earlier_days","score.driver_typical_machine","score.driver_typical_operation","score.evidence_bands","score.evidence_band","score.evidence_band_dhw","score.evidence_empty","score.evidence_frozen","score.part_machine","score.part_operation"]
def texts(k):
    out=[]
    for m in re.finditer(r'"%s"\s*:\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)'%re.escape(k),card):
        out.append("".join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"',m.group(1))))
    return out
def rx(t):
    parts=re.split(r'(\{[a-z_]+\})',t); r=""
    for p in parts:
        if re.fullmatch(r'\{[a-z_]+\}',p): r+=r'[\s\S]*?'
        else: r+=r'\s+'.join(re.escape(w) for w in p.split(' ')) 
    return re.compile(r)
files=sorted(glob.glob(shots+"/score_open*.txt"))
print("cells:",[os.path.basename(f) for f in files])
miss=0
for k in keys:
    t=texts(k)[:2]; assert len(t)==2,(k,len(t))
    for lang,tx in (("en",t[0]),("sv-SE",t[1])):
        r=rx(tx)
        for theme in ("light","dark"):
            fs=[f for f in files if f.endswith(f"-{theme}-{lang}.txt")]
            if not fs: continue
            hit=[os.path.basename(f).split("-375")[0] for f in fs if r.search(open(f).read())]
            if not hit: miss+=1
            print(f"{'MATCH' if hit else 'MISS '} {k} {lang} {theme}: {','.join(hit) or '-'}")
print(f"RESULT label-trace: {miss} miss(es) over {len(keys)} keys")
