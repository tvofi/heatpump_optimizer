import json,subprocess as s
f="dev/programme/rosters/wave-r10-groups.json"
g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]}
a,b=g("origin/main"),g("HEAD")
for k,B in b.items():
    r=B.get("resume") or {}
    if r.get("stage")!="done": continue
    changed = a.get(k)!=B
    c=r.get("commit")
    if not c: print("DONE-NOCOMMIT",k,"changed" if changed else "unchanged-from-main"); continue
    rc=s.run(["git","merge-base","--is-ancestor",c,"origin/main"],capture_output=True).returncode
    print("DONE",k,c[:12],"on-main" if rc==0 else f"NOT-ON-MAIN rc={rc}","pr",r.get("pr"),"changed" if changed else "")
