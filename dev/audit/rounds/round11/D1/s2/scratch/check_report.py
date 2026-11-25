import json, re
S = json.load(open("dev/audit/config/finding.schema.json"))
R = json.load(open("dev/audit/rounds/round11/D1/s2/REPORT.json"))
errs = []
for k in S["required"]:
    if k not in R:
        errs.append(f"missing {k}")
fd = S["definitions"]["finding"]
ev = S["definitions"]["evidence"]
classes = set(fd["properties"]["class_guess"]["enum"])
for f in R["findings"]:
    for k in fd["required"]:
        if k not in f:
            errs.append(f"{f.get('id')}: missing {k}")
    if not re.match(fd["properties"]["id"]["pattern"], f["id"]):
        errs.append(f"{f['id']}: id pattern")
    if len(f["title"]) > 120:
        errs.append(f"{f['id']}: title {len(f['title'])}")
    if len(f["metric_definition"]) > 200:
        errs.append(f"{f['id']}: metric_definition {len(f['metric_definition'])}")
    if f["class_guess"] not in classes:
        errs.append(f"{f['id']}: class")
    if f["severity"] not in fd["properties"]["severity"]["enum"]:
        errs.append(f"{f['id']}: severity")
    for k in ev["required"]:
        if k not in f["evidence"]:
            errs.append(f"{f['id']}: evidence missing {k}")
    if not re.match(ev["properties"]["harness_path"]["pattern"], f["evidence"]["harness_path"]):
        errs.append(f"{f['id']}: harness_path")
    if f["evidence"]["cpu_or_wall"] not in ev["properties"]["cpu_or_wall"]["enum"]:
        errs.append(f"{f['id']}: cpu_or_wall")
    if f["perturbation"]["expected_direction"] not in fd["properties"]["perturbation"]["properties"]["expected_direction"]["enum"]:
        errs.append(f"{f['id']}: direction")
    if "leave_one_out" in f and f["leave_one_out"]["cells"] < 5:
        errs.append(f"{f['id']}: loo cells")
for h in R["harnesses"]:
    if not re.match(S["properties"]["harnesses"]["items"]["pattern"], h):
        errs.append(f"harness {h}")
for c in R["coverage"]:
    for k in S["properties"]["coverage"]["items"]["required"]:
        if k not in c:
            errs.append(f"coverage missing {k}")
    if c["examined"] != c["universe"] and not c["not_reached"]:
        errs.append("coverage does not close")
for l in R["leads"]:
    if not re.match(S["properties"]["leads"]["items"]["properties"]["owner_seat"]["pattern"], l["owner_seat"]):
        errs.append("lead seat")
print("ERRORS:", errs or "none")
