import json,re,sys,urllib.request as u
for f,pk in [(sys.argv[1]+"/tests/requirements-ci.txt",[("aiohttp","3.14.5")]),(sys.argv[1]+"/tests/requirements-typing.txt",[("aiohttp","3.14.5"),("pillow","13.0.0"),("certifi","2026.10.19"),("uv","0.13.4")])]:
    t=open(f).read()
    for n,v in pk:
        b=re.search(r'(?ms)^'+n+'==(\S+).*?(?=^[A-Za-z0-9][A-Za-z0-9._-]*==|\Z)',t)
        assert b.group(1)==v,(n,b.group(1))
        hs=set(re.findall(r'sha256:([0-9a-f]{64})',b.group(0)))
        idx={x['digests']['sha256'] for x in json.load(u.urlopen(f'https://pypi.org/pypi/{n}/{v}/json'))['urls']}
        print("RESULT",f.split('/')[-1],n,v,len(hs),len(idx),hs==idx)
