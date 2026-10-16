import subprocess, sys, collections
sys.path.insert(0, "tools/audit/seat")
import ref_privacy as rp
from urllib.parse import unquote
host = rp.Identity.of_host(); null = rp.Identity.made(set(), set(), None)
out = subprocess.run(["git","log","origin/main","--format=%H%x1f%ae%x1f%ce%x1f%B%x1e"],capture_output=True,text=True).stdout
recs=[r.strip("\n").split("\x1f",3) for r in out.split("\x1e") if r.strip()]
for name, ident in (("host", host), ("identity-free", null)):
    c=collections.Counter(k for _,_,_,m in recs for k in rp.leaks(m, ident))
    print(f"{name}: {len(recs)} messages, by class: {dict(c)}")
changed=sum(1 for _,_,_,m in recs if rp.leaks(m,host)!=rp._leaks(m,host))
print("messages whose verdict URL-decoding changes:", changed)
ids=collections.Counter()
for sha,ae,ce,m in recs:
    for e in (ae,ce):
        ids["refused" if rp.email_leaks(e,host) else "passed"]+=1
commits_refused=sum(1 for sha,ae,ce,m in recs if rp.email_leaks(ae,host) or rp.email_leaks(ce,host))
noreply=[r for r in recs if r[1].endswith("noreply.github.com") or r[1].endswith("anthropic.com")]
print("identities (author+committer):", dict(ids), "; commits with a refused identity:", commits_refused,
      "; commits with noreply author refused:", sum(1 for r in noreply if rp.email_leaks(r[1],host)))
