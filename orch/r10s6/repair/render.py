import sys, json, importlib.util, os
spec = importlib.util.spec_from_file_location("cd", "/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/cloud_dispatch.py")
cd = importlib.util.module_from_spec(spec); sys.modules["cd"] = cd; spec.loader.exec_module(cd)
topic, head, pr, brieffile = sys.argv[1:5]
env = os.environ
import argparse
known = cd._config(argparse.Namespace(overlay="/Users/timmalmstrom/hpo-orch/r10s6/cloud-overlay.json", env_id=None, model="claude-opus-5-5", repo=None), env)
payload = cd.render("fixer", head, env_id=known["env_id"], model="claude-opus-5-5", repo=known["repo"], pr=pr, topic=topic, nonce="", brief=open(brieffile).read())
ref = f"dispatch/fixer-{topic}"
cd._publish("/Users/timmalmstrom/hpo-seats/r10s6/orch-wt", ref, {"PAYLOAD.json": json.dumps(payload), "PROMPT.md": payload["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]})
print(ref)
