import json, subprocess, sys, time
nums = json.load(open(sys.argv[1]))
merged=[]; open_=[]; unmerged=[]; errors=[]
for n in nums:
    r = subprocess.run(["gh","api",f"repos/tvofi/heatpump_optimizer/pulls/{n}"],
                       capture_output=True,text=True)
    if r.returncode!=0:
        errors.append((n, r.stderr.strip()[:80])); continue
    d=json.loads(r.stdout)
    if d.get("merged") is True: merged.append(n)
    elif d.get("state")=="open": open_.append(n)
    else: unmerged.append((n,d.get("state")))
print("queried:", len(nums))
print("MERGED:", len(merged))
print("genuinely OPEN:", len(open_), open_)
print("closed-unmerged:", len(unmerged), unmerged)
print("ERRORS:", len(errors), errors)
