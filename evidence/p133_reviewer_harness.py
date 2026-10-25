import json,re,sys
d=json.load(open(sys.argv[1])); G={g["group"]:g for g in d["groups"]}
DONE={"done","absorbed","merged"}
PFX=("custom_components/","tools/","tests/","dev/","docs/",".github/",".claude/")
def carries(g):
    c=g.get("carry") or []
    return [x if isinstance(x,str) else json.dumps(x) for x in (c if isinstance(c,list) else [c])]
def touched(g):
    paths=set(g.get("files") or []); bases=set()
    for t in carries(g):
        for tok in re.findall(r"[A-Za-z0-9_./\-]+",t):
            tok=tok.strip(".")
            if tok.startswith(PFX): paths.add(tok)
            elif re.fullmatch(r"[A-Za-z0-9_\-]+\.(py|sh|mjs)",tok): bases.add(tok)
    paths.discard("tools/audit/seat/INSTRUMENTS.md")
    return paths,bases
def inter(P,D):
    pp,pb=touched(P); dp,db=touched(D)
    pbase={p.rsplit("/",1)[-1] for p in pp}|pb; dbase={p.rsplit("/",1)[-1] for p in dp}|db
    return sorted((pp&dp)|(pbase&dbase))
stage=lambda g:(g.get("resume") or {}).get("stage")
src=[n for n,g in G.items() if stage(g)=="carries-open"]+["R10-UPDATE-PR-SIGNALS"]
for p in src:
    P=G[p]; print(f"## {p} stage={stage(P)} carries={len(carries(P))}")
    for n,g in G.items():
        if p in (g.get("after") or []) and stage(g) not in DONE:
            note=g.get("architect_note"); seam = bool(note) and p in json.dumps(note)
            print(f"   {n} [{stage(g)}] closes_round={g.get('closes_round')} seam_note_names_P={seam} shared={inter(P,g)}")
