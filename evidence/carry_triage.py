import json,subprocess as s,re
f="dev/programme/rosters/wave-r10-groups.json"
g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]}
a,b=g("origin/main"),g("HEAD")
for k,B in b.items():
    ca=(a.get(k) or {}).get("carry") or []
    for c in B.get("carry") or []:
        if c in ca: continue
        t=c if isinstance(c,str) else json.dumps(c)
        V=re.findall(r'\bV1\d\d\b',t); P=re.findall(r'\bP2\d\d\b',t); T=re.findall(r'triage[^ "]*\.md[^ "]*|s\d+-batch\d+[^ ,."]*',t)
        print(k,"| V",V,"| P",P,"| triage",T,"| tail:",t[-260:].replace("\n"," "))
