import json, sys
p = sys.argv[1]
d = json.load(open(p))
if "data" in d:
    pr = d["data"]["repository"]["pullRequest"]
    print("  mergeStateStatus:", pr["mergeStateStatus"])
    for n in pr["commits"]["nodes"]:
        rc = n["commit"]["statusCheckRollup"]
        if rc is None:
            print("  statusCheckRollup: None -- the head carries NO check")
            continue
        print("  rollup state:", rc.get("state"))
        for c in rc.get("contexts", []):
            nm = c.get("name") or c.get("context")
            st = c.get("status") or c.get("state")
            print("    {:40s} {:14s} conclusion={}".format(nm, str(st), c.get("conclusion")))
else:
    print("  state:", d.get("state"), " total_status:", d.get("total_status"))
    for s in d.get("statuses", []):
        print("    {:38s} {}".format(s["context"], s["state"]))
