import json

REPO = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/register-wt"
INTAKE = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/intake"

with open(f"{REPO}/tools/audit/rotation.json") as f:
    rotation = json.load(f)

with open(f"{INTAKE}/ledger_round9.json") as f:
    ledger = json.load(f)

for dim, entry in ledger.items():
    assert dim in rotation, f"unknown dimension {dim}"
    rotation[dim]["rounds"]["9"] = entry

with open(f"{REPO}/tools/audit/rotation.json", "w") as f:
    json.dump(rotation, f, indent=2, sort_keys=True)
    f.write("\n")
