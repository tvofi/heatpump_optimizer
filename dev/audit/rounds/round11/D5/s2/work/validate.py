import json, re
s = json.load(open("dev/audit/config/finding.schema.json"))
r = json.load(open("dev/audit/rounds/round11/D5/s2/REPORT.json"))
fin = s["definitions"]["finding"]; ev = s["definitions"]["evidence"]
errs = []
for k in s["required"]:
    if k not in r: errs.append("missing " + k)
for c in r["coverage"]:
    for k in s["properties"]["coverage"]["items"]["required"]:
        if k not in c: errs.append(f"cov missing {k}")
    if c["examined"] > c["universe"]: errs.append("examined>universe")
    if (c["examined"] == c["universe"]) != (not c["not_reached"]): errs.append("not_reached mismatch " + c["step"])
enum = set(fin["properties"]["class_guess"]["enum"])
for f in r["findings"]:
    for k in fin["required"]:
        if k not in f: errs.append(f"{f.get('id')} missing {k}")
    for k in ev["required"]:
        if k not in f["evidence"]: errs.append(f"{f['id']} evidence missing {k}")
    if not re.match(fin["properties"]["id"]["pattern"], f["id"]): errs.append("id " + f["id"])
    if f["class_guess"] not in enum: errs.append("class " + f["class_guess"])
    if len(f["title"]) > 120: errs.append(f"title long {f['id']} {len(f['title'])}")
    if len(f["metric_definition"]) > 200: errs.append(f"metric long {f['id']} {len(f['metric_definition'])}")
    if f["evidence"]["cpu_or_wall"] not in ev["properties"]["cpu_or_wall"]["enum"]: errs.append("cow " + f["id"])
    if f["perturbation"]["expected_direction"] not in ["up", "down", "to_zero", "sign_flip"]: errs.append("dir " + f["id"])
    if not re.match(ev["properties"]["harness_path"]["pattern"], f["evidence"]["harness_path"]): errs.append("hp " + f["id"])
    if not isinstance(f["evidence"]["load1"], (int, float)) or not isinstance(f["evidence"]["thread_factor"], (int, float)):
        errs.append("num " + f["id"])
for h in r["harnesses"]:
    if not re.match(s["properties"]["harnesses"]["items"]["pattern"], h): errs.append("harness " + h)
for l in r["leads"]:
    if not re.match(s["properties"]["leads"]["items"]["properties"]["owner_seat"]["pattern"], l["owner_seat"]): errs.append("lead " + l["owner_seat"])
print(errs or "OK", [(f["id"], f["severity"], f["step"]) for f in r["findings"]])
