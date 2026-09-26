import json, collections

SCRATCH = "/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad"
INTAKE = f"{SCRATCH}/intake"

def load(p):
    with open(p) as f:
        return json.load(f)

validated = load(f"{SCRATCH}/validated.json")
rejected = load(f"{SCRATCH}/rejected_at_intake.json")
reports = load(f"{INTAKE}/reports.json")

seats_by_dim = collections.defaultdict(set)
for seat in reports["reports"].keys():
    dim = seat.split("-s")[0]
    seats_by_dim[dim].add(seat)

# D3-s2 catch-up reported via handoff branch, not in reports.json
seats_by_dim["D3"].add("D3-s2")

valid_by_dim = collections.defaultdict(list)
for f in validated:
    dim = f["scope"].split("-s")[0]
    valid_by_dim[dim].append(f)

rejected_by_dim = collections.defaultdict(list)
for r in rejected:
    # scope may be in id (D2-s3-01) -> dim D2
    seat = r.get("seat", "?")
    dim = seat.split("-s")[0] if "-s" in seat else "?"
    rejected_by_dim[dim].append(r)

dims = [f"D{n}" for n in range(15)]
for dim in dims:
    print(dim, "seats_reported=", len(seats_by_dim.get(dim, [])),
          "accepted=", len(valid_by_dim.get(dim, [])),
          "rejected=", len(rejected_by_dim.get(dim, [])))

print("TOTAL valid", len(validated), "TOTAL rejected", len(rejected))
print("rejected dims check:")
for r in rejected:
    print(" ", r["id"], r.get("seat"), r["source"])
