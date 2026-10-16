import subprocess, sys, collections, re
sys.path.insert(0, "tools/audit/seat")
import ref_privacy as rp
host = rp.Identity.of_host()
null = rp.Identity.made(set(), set(), None)   # judges only the identity-free classes
out = subprocess.run(["git","log","--all" if "--all" in sys.argv else "origin/main","--format=%H%x1f%B%x1e"],capture_output=True,text=True).stdout
recs=[r.strip("\n").split("\x1f",1) for r in out.split("\x1e") if r.strip()]
for name, ident in (("host", host), ("identity-free", null)):
    c=collections.Counter(); examples=collections.defaultdict(list)
    for sha,msg in recs:
        for k in rp.leaks(msg, ident):
            c[k]+=1
            if k=="host-path" and ident is null and len(examples[k])<12:
                # print only the matched span with names masked
                m=rp._HOST_PATH.search(msg); ctx=msg[max(0,m.start()-25):m.end()+25].replace("\n"," ")
                for h in host.homes: ctx=re.sub(re.escape(h),"<HOME>",ctx,flags=re.I)
                for n in host.names: ctx=re.sub(re.escape(n),"<NAME>",ctx,flags=re.I)
                examples[k].append(sha[:10]+" "+ctx)
    print(f"{name}: {len(recs)} messages, by class: {dict(c)}")
    for e in examples["host-path"]: print("   ", e)
