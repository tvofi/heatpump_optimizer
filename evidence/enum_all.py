import re,subprocess,sys
sys.path.insert(0,'tools/audit/seat'); import bare_array as b
names=[n for n in subprocess.check_output(['git','ls-files'],text=True).split() if n.endswith('.sh')]
ANY=re.compile(r'\$\{!?#?([A-Za-z_]\w*)\[[@*]\][^}]*\}')
setu_loose=re.compile(r'\bset\b[^\n#]*(-[a-zA-Z]*u|nounset)')
for p in sorted(names):
    t=open(p).read()
    strict=bool(b.SET_U.search(t)); loose=bool(setu_loose.search(t))
    if loose!=strict: print("SETU-MISMATCH",p,strict,loose)
    for n,l in enumerate(t.splitlines(),1):
        if l.lstrip().startswith('#'): continue
        for m in ANY.finditer(l):
            s=m.group(0)
            if s.startswith('${#') : continue
            pre=l[:m.start()]
            if pre.endswith('${%s[@]+'%m.group(1)) or pre.endswith('${%s[@]+"'%m.group(1)) : continue
            if s=='${%s[@]+'%m.group(1): continue
            q = pre.endswith('"') and l[m.end():m.end()+1]=='"'
            if b.MARK.search(l): continue
            print(("U" if (strict or loose) else "n"),p,n,s,("Q" if q else "x"))
