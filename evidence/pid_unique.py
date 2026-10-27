import re,glob,os,collections
rounds=collections.defaultdict(collections.Counter)
for f in sorted(glob.glob("dev/programme/triage/*.md")):
    base=os.path.basename(f); m=re.match(r"(s\d+)",base)
    if not m: continue
    for pid in re.findall(r"^## (P\d+):", open(f,encoding="utf-8").read(), re.M):
        rounds[m.group(1)][pid]+=1
for rnd,c in sorted(rounds.items()):
    dup={k:v for k,v in c.items() if v>1}
    print(f"RESULT round {rnd}: headings={sum(c.values())} unique={len(c)} duplicates={dup}")
