#!/bin/bash
set -e
nums="$1"; out="$2"
python3 - "$nums" "$out" <<'PY'
import json,subprocess,sys
nums=json.load(open(sys.argv[1]))
out=[]
B=40
for i in range(0,len(nums),B):
    chunk=nums[i:i+B]
    parts=[]
    for n in chunk:
        parts.append(f'p{n}: pullRequest(number:{n}){{ number merged state title headRefName mergeCommit{{ oid }} }}')
    q='query{ repository(owner:"tvofi",name:"heatpump_optimizer"){ '+ " ".join(parts) +' } }'
    r=subprocess.run(["gh","api","graphql","-f",f"query={q}"],capture_output=True,text=True)
    if r.returncode!=0:
        print("ERR",r.stderr[:300]); sys.exit(1)
    d=json.loads(r.stdout)["data"]["repository"]
    for n in chunk:
        p=d[f"p{n}"]
        out.append({"number":p["number"],"title":p["title"],"state":p["state"],
                    "head_ref":p["headRefName"],
                    "merge_sha":(p.get("mergeCommit") or {}).get("oid") or "",
                    "merged":p["merged"]})
json.dump(out,open(sys.argv[2],"w"),indent=1)
print("fetched",len(out),"prs; merged:",sum(1 for x in out if x["merged"]))
PY
