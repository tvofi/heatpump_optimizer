import re
def norm(s): return " ".join(re.findall(r"[a-z0-9]+", s.lower()))
units=[(l.split(": ",1)[0][4:], norm(l.split(": ",1)[1])) for l in open("theirs.txt") if l.startswith("CUT ")]
un=0
for l in open("mine.txt"):
    if not l.startswith("GONE "): continue
    f, frag = l[5:].split(": ",1)
    n=norm(frag)
    # a wrapped-line fragment may span two units; check each half-run of >=3 words
    hit=[i+1 for i,(uf,u) in enumerate(units) if uf==f and (n in u or any(" ".join(n.split()[k:k+3]) in u for k in range(len(n.split())-2)))]
    if not hit: un+=1; print("UNMAPPED", f, frag.strip()[:200])
print("unmapped", un)
