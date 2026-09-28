import json, sys
from jsonschema import Draft7Validator, RefResolver

REPO = "/home/claude/heatpump_optimizer"
INTAKE = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/intake"
SCRATCH = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad"

with open(f"{REPO}/tools/audit/finding.schema.json") as f:
    full_schema = json.load(f)

finding_schema = full_schema["definitions"]["finding"]
resolver = RefResolver.from_schema(full_schema)
validator = Draft7Validator(finding_schema, resolver=resolver)

def load(path):
    with open(path) as f:
        return json.load(f)

accepted = load(f"{INTAKE}/accepted.json")
lead_findings = load(f"{INTAKE}/lead_findings.json")
b2 = load(f"{SCRATCH}/reports-B2.json")
d3s2_findings = b2["reports"]["D3-s2"]["findings"]
for f_ in d3s2_findings:
    f_["seat"] = "D3-s2"
    f_["catch_up_batch"] = True

all_items = []
for f_ in accepted:
    f_["_source"] = "accepted"
    all_items.append(f_)
for f_ in lead_findings:
    f_["_source"] = "lead_findings"
    all_items.append(f_)
for f_ in d3s2_findings:
    f_["_source"] = "d3s2_catchup"
    all_items.append(f_)

results = []
rejected = []
for item in all_items:
    errors = sorted(validator.iter_errors(item), key=lambda e: e.path)
    if errors:
        msgs = []
        for e in errors:
            loc = "/".join(str(p) for p in e.path)
            msgs.append(f"{loc}: {e.message}" if loc else e.message)
        rejected.append({
            "id": item.get("id", "<no id>"),
            "seat": item.get("seat", item.get("scope", "?")),
            "source": item["_source"],
            "errors": msgs,
        })
    else:
        results.append(item)

print(f"Total items: {len(all_items)}")
print(f"Valid: {len(results)}")
print(f"Rejected: {len(rejected)}")
for r in rejected:
    print("---")
    print(r["id"], r["seat"], r["source"])
    for m in r["errors"]:
        print("   ", m)

with open(f"{SCRATCH}/validated.json", "w") as f:
    json.dump(results, f, indent=2)
with open(f"{SCRATCH}/rejected_at_intake.json", "w") as f:
    json.dump(rejected, f, indent=2)
