import re,subprocess,json,urllib.request,sys
base=sys.argv[1]; head=sys.argv[2]
files=["tests/requirements-ci.txt","tests/requirements-coverage.txt","tests/requirements-typing.txt"]
bad=0;n=0
for f in files:
    old=subprocess.run(["git","show",f"{base}:{f}"],capture_output=True,text=True).stdout
    new=subprocess.run(["git","show",f"{head}:{f}"],capture_output=True,text=True).stdout
    def parse(t):
        d={};cur=None
        for line in t.splitlines():
            m=re.match(r'^([A-Za-z0-9_.\-]+)==(\S+)',line)
            if m: cur=(m.group(1).lower(),m.group(2)); d[cur]=set(); continue
            h=re.search(r'--hash=sha256:([0-9a-f]{64})',line)
            if h and cur: d[cur].add(h.group(1))
        return d
    o,nw=parse(old),parse(new)
    on={k[0]:k for k in o}; nn={k[0]:k for k in nw}
    if set(on)!=set(nn): print(f,"package set changed",set(on)^set(nn)); bad+=1
    for p,k in nn.items():
        if on.get(p)==k and o[on[p]]==nw[k]: continue
        if on.get(p)==k: print(f,p,"hashes changed without version change"); bad+=1; continue
        n+=1
        url=f"https://pypi.org/pypi/{p}/{k[1]}/json"
        js=json.load(urllib.request.urlopen(url,timeout=60))
        dig={u['digests']['sha256'] for u in js['urls']}
        extra=nw[k]-dig
        print(f"{f} {p} {on.get(p,('',None))[1]} -> {k[1]}: pinned {len(nw[k])} hashes, pypi {len(dig)}, not-on-pypi {len(extra)}, pypi-not-pinned {len(dig-nw[k])}")
        bad+= bool(extra) or not nw[k]
print("RESULT hashes: changed pins",n,"bad",bad)
