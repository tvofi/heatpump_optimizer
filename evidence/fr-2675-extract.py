import re,sys
src=open("tests/features.py").read().split("\n")
head=src[:91]; blk=src[67990:]
pre=src[91:67990]
# index top-level defs in pre
defs={}
i=0
while i<len(pre):
    l=pre[i]
    m=re.match(r"(?:async )?def (\w+)\(",l) or re.match(r"class (\w+)\b",l)
    if m:
        j=i+1
        while j<len(pre) and (pre[j].startswith((" ","\t")) or pre[j]=="" ):
            j+=1
        # include decorators above
        k=i
        while k>0 and pre[k-1].startswith("@"): k-=1
        defs.setdefault(m.group(1),[]).append((k,j))
        i=j; continue
    m=re.match(r"(\w+) = ",l)
    if m and not l.startswith(" "):
        j=i+1
        while j<len(pre) and pre[j][:1] in (" ",")","]","}"): j+=1
        defs.setdefault(m.group(1),[]).append((i,j))
    m=re.match(r"from \S+ import \(?(.*)",l)
    i+=1
need=set(); out=[]
chosen={}
def scan(text,pos):
    for n in set(re.findall(r"(?<![.\w])([A-Za-z_]\w*)\b",text)):
        if n in defs and n not in need and (n.startswith("_") or n.isupper()):
            c=[d for d in defs[n] if d[0]<pos]
            if not c: continue
            need.add(n); a,b=c[-1]; chosen[n]=(a,b); scan("\n".join(pre[a:b]),a)
scan("\n".join(blk),len(pre))
# imports in pre (top-level)
imps=["try:\n    "+l.split("#")[0]+"\nexcept Exception:\n    pass" for l in pre if re.match(r"(from|import) ",l) and "(" not in l and re.search(r"heatpump_optimizer|homeassistant|harness|hastub|profiles|^(import|from) (asyncio|math|json|types|dataclasses|datetime|contextlib|functools|unittest|copy|time|os|itertools|collections)\b",l)]
spans=sorted(chosen.values())
body=[]
for a,b in spans: body+=pre[a:b]+[""]
open("tests/_fr_ls_block.py","w").write("\n".join(head+imps+body+blk))
print(sorted(need))
