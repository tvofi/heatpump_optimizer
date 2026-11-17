import json, subprocess, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import postmerge as pm
body = open(sys.argv[2]).read()
roster = json.loads(subprocess.check_output(["git", "show", sys.argv[3] + ":dev/programme/rosters/wave-r10-groups.json"]))
ops, owed = pm.derive_marks(body, roster, "R11-PRE-HANDOFF-BOOKKEEPING", "f"*40)
print(len(ops), "ops;", len(owed), "owed"); print("\n".join(ops + owed))
