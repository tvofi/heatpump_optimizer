import random,re
BASE = r"\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n"
HEAD = (r"\n  replay:\n(?:    .*\n| {0,3}\n| {0,3}\t[ \t]*\n)*?" r"    timeout-minutes: (\d+)\n")
r=random.Random(1);A=" \t\n\rx:timeout-minutes: 45"
d=0;m=0
for i in range(200000):
    s="\n  replay:\n"+"".join(r.choice([""," ","  ","   ","    ","\t","x","\r",":"]) + r.choice(["","\n","timeout-minutes: 4\n","    timeout-minutes: 4\n"]) for _ in range(r.randint(0,8)))
    b=re.search(BASE,s);h=re.search(HEAD,s)
    kb=(b.span(),b.group(1)) if b else None;kh=(h.span(),h.group(1)) if h else None
    m+=b is not None; d+=kb!=kh
print("random corpus 200000, base matched",m,"disagree",d)
