import sys, json, importlib.util, os, argparse, subprocess
spec = importlib.util.spec_from_file_location("cd", "/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/cloud_dispatch.py")
cd = importlib.util.module_from_spec(spec); sys.modules["cd"] = cd; spec.loader.exec_module(cd)
group, rosterref, prefixfile, head = sys.argv[1:5]
repo = "/Users/timmalmstrom/hpo-seats/r10s6/orch-wt"
roster = json.loads(subprocess.run(["git","-C",repo,"show",f"{rosterref}:dev/programme/rosters/wave-r10-groups.json"],capture_output=True,text=True,check=True).stdout)
g = next(x for x in roster["groups"] if x["group"] == group)
topic = g["resume"]["branch"].removeprefix("handoff/")
brief = open(prefixfile).read().rstrip("\n") + "\n\n" + (g.get("brief") or "") + "\n\nCarried findings (roster " + rosterref + ", all owed in this PR):\n" + "".join(f"\n[carry {i+1}] {c}\n" for i, c in enumerate(g.get("carry") or []))
known = cd._config(argparse.Namespace(overlay="/Users/timmalmstrom/hpo-orch/r10s6/cloud-overlay.json", env_id=None, model="claude-opus-5-5", repo=None), os.environ)
payload = cd.render("fixer", head, env_id=known["env_id"], model="claude-opus-5-5", repo=roster.get("repo") or known["repo"], pr="", topic=topic, nonce="", brief=brief)
ref = f"dispatch/fixer-{topic}"
cd._publish(repo, ref, {"PAYLOAD.json": json.dumps(payload), "PROMPT.md": payload["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]})
print(ref, "carries", len(g.get("carry") or []))
