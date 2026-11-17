import re,sys,glob
tot=0;files=set()
for f in sorted(glob.glob('.claude/hooks/*.sh')+glob.glob('.claude/workflows/*.js')):
    paras=[];cur=[]
    for l in open(f):
        s=l.strip()
        m=re.match(r'(#|//|\*|/\*\*?)\s?(.*)',s)
        if m and not s.startswith('#!'):
            t=m.group(2).rstrip('*/ ').strip()
            if t: cur.append(t)
            else: paras.append(' '.join(cur));cur=[]
        else: paras.append(' '.join(cur));cur=[]
    paras.append(' '.join(cur))
    for p in paras:
        for s in re.split(r'(?<=[.!?])\s+',p):
            n=len(s.split())
            if n>40: tot+=1;files.add(f); 
            if n>40 and f.endswith('pre-edit.sh'): print(f,n,s[:50])
print(tot,len(files))
