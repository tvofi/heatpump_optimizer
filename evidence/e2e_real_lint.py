import sys, json
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import roster_edit as re_
S = sys.argv[2]; repo = "/home/user/heatpump_optimizer"
base = open(f"{S}/bad.json").read()
p = f"{S}/e2e/wave-r10-groups.json"
def gate(obj, b):
    open(p, "w").write(json.dumps(obj, indent=1))
    return re_.lint_gate(repo, repo, p, b)
live = [g["group"] for g in json.loads(base)["groups"] if (g.get("resume") or {}).get("stage") in ("not-started","carries-open") and g["group"]!="R10-ROSTER-WRITE-SWEEP"][0]
print("live group", live)
d2 = json.loads(base)
for g in d2["groups"]:
    if g["group"]==live: g["brief"] += " tools/audit/seat/bus.sh:999999"
ok, why = gate(d2, base); print("RESULT real-lint new-bad-cite-live-group ok=%s" % ok); print(why[:500])
d5 = json.loads(base)
for g in d5["groups"]:
    if g["group"]=="R10-ROSTER-WRITE-SWEEP": g["brief"] += " tools/audit/seat/bus.sh:999998"
ok, why = gate(d5, base); print("RESULT real-lint new-bad-cite-same-group ok=%s" % ok); print(why[:300])
d1 = json.loads(base); d1["groups"][0]["resume"]["note"] = "unrelated"
ok, why = gate(d1, None); print("RESULT real-lint no-base(old gate) unrelated ok=%s" % ok)
