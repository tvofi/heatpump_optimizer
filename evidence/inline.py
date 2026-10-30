import sys, json
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import cloud_dispatch as cd
h = "883e8452fafbef8ecc6c686924e27c054f85bf54"
out = {}
for role, kw in (("fixer", dict(topic="t-1")), ("reviewer", dict(pr="7", nonce="abc123")), ("probe", dict(topic="t-1"))):
    out[role] = json.dumps(cd.render(role, h, env_id="env_x", model="m-1", repo="owner/name", brief="B.\n", **kw), sort_keys=True)
print(json.dumps(out))
