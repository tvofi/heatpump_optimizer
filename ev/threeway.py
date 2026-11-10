import json,re,subprocess,sys
P="custom_components/heatpump_optimizer/"
def show(rev,path): return subprocess.run(["git","show",f"{rev}:{P}{path}"],capture_output=True,text=True,check=True).stdout
def flat(d,p=""):
    o={}
    for k,v in d.items():
        kk=f"{p}.{k}" if p else k
        if isinstance(v,dict): o.update(flat(v,kk))
        else: o[kk]=v
    return o
def card(txt):
    # parse STRINGS = { lang: { "k": "v", ... }, ... }
    i=txt.index("const STRINGS = {"); body=txt[i:]
    out={}; lang=None
    for line in body.splitlines()[1:]:
        m=re.match(r'^  (\w+): \{\s*$',line)
        if m: lang=m.group(1); continue
        if re.match(r'^\};',line): break
        m=re.match(r'^    "([^"]+)":\s*(".*")\s*,?\s*$',line)
        if m and lang: out[(lang,m.group(1))]=m.group(2)
    return out
def load(rev,kind):
    return flat(json.loads(show(rev,"translations/de.json"))) if kind=="de" else card(show(rev,"www/heatpump-optimizer-card.js"))
def run(merge,ours,theirs,base,kind,merged_override=None):
    M=merged_override if merged_override is not None else load(merge,kind)
    O,T,B=load(ours,kind),load(theirs,kind),load(base,kind)
    branch_added=[k for k in O if k not in B]
    feat=[k for k in branch_added if k not in T]  # branch-only keys
    missing=[k for k in feat if k not in M]
    changed=[k for k in feat if k in M and M[k]!=O[k]]
    main_missing=[k for k in T if k not in M and k in O|B and False] + [k for k in T if k not in M]
    print(f"{kind} merge={merge} |M|={len(M)} |O|={len(O)} |T|={len(T)} |B|={len(B)} branch-only-keys={len(feat)} missing={missing} value-changed={changed} main-keys-missing={main_missing}")
    return feat,missing,changed,main_missing
if __name__=="__main__":
    merge,ours,theirs,base=sys.argv[1:5]
    bad=0
    for kind in ("de","card"):
        feat,mi,ch,mm=run(merge,ours,theirs,base,kind)
        if kind=="card":
            from collections import Counter; print("  card branch-only per language:",dict(Counter(l for l,_ in feat)), [k for _,k in feat])
        else: print("  de branch-only keys:",feat)
        bad|=bool(mi or ch or mm)
        if feat:  # null control: drop one feature key from the merged map
            M=load(merge,kind); M.pop(feat[0])
            _,mi2,_,_=run(merge,ours,theirs,base,kind,M)
            print("  NULL CONTROL", "DETECTS" if mi2 else "BLIND")
    print("RESULT threeway", "FAIL" if bad else "PASS")
