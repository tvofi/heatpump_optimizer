"""Hand check of report.json against tools/audit/finding.schema.json (no jsonschema here).

    python tools/audit/round2/D4/validate_report.py tools/audit/round2/D4/report.json
"""
import json
import re
import sys

schema = json.load(open("tools/audit/finding.schema.json"))
rep = json.load(open(sys.argv[1]))
errs = []
for k in schema["required"]:
    if k not in rep:
        errs.append(f"top-level missing {k}")
if not re.match(schema["properties"]["dimension"]["pattern"], rep.get("dimension", "")):
    errs.append("dimension pattern")
fin_req = schema["definitions"]["finding"]["required"]
ev_req = schema["definitions"]["evidence"]["required"]
for f in rep.get("findings", []):
    for k in fin_req:
        if k not in f:
            errs.append(f"{f.get('id')}: missing {k}")
    if not re.match(r"^D(10|[0-9])-[0-9]{2}$", f.get("id", "")):
        errs.append(f"{f.get('id')}: id pattern")
    if len(f.get("title", "")) > 120:
        errs.append(f"{f.get('id')}: title > 120")
    if len(f.get("metric_definition", "")) > 200:
        errs.append(f"{f.get('id')}: metric_definition > 200 ({len(f['metric_definition'])})")
    if f.get("severity") not in ("critical", "high", "medium", "low"):
        errs.append(f"{f.get('id')}: severity")
    if f.get("stop_rule_class") not in ("bug", "hygiene"):
        errs.append(f"{f.get('id')}: stop_rule_class")
    ev = f.get("evidence", {})
    for k in ev_req:
        if k not in ev:
            errs.append(f"{f.get('id')}: evidence missing {k}")
    if ev.get("cpu_or_wall") not in ("cpu", "wall", "count", "bytes", "ratio", "n/a"):
        errs.append(f"{f.get('id')}: cpu_or_wall")
    if ev.get("cpu_or_wall") in ("cpu", "wall") and "null_control" not in f:
        errs.append(f"{f.get('id')}: null_control required")
    if not re.match(r"^tools/audit/round[0-9]+/D(10|[0-9])/", ev.get("harness_path", "")):
        errs.append(f"{f.get('id')}: harness_path pattern")
    p = f.get("perturbation", {})
    for k in ("change", "expected_direction"):
        if k not in p:
            errs.append(f"{f.get('id')}: perturbation missing {k}")
    if p.get("expected_direction") not in ("up", "down", "to_zero", "sign_flip"):
        errs.append(f"{f.get('id')}: expected_direction")
    loo = f.get("leave_one_out")
    if loo and loo.get("cells", 5) < 5:
        errs.append(f"{f.get('id')}: leave_one_out cells < 5")
for n in rep.get("non_findings", []):
    for k in ("claim", "command", "value"):
        if k not in n:
            errs.append(f"non_finding missing {k}: {n}")
for h in rep.get("harnesses", []):
    if not re.match(r"^tools/audit/round[0-9]+/D(10|[0-9])/", h):
        errs.append(f"harness path pattern: {h}")
print("\n".join(errs) if errs else f"OK: {len(rep['findings'])} findings, {len(rep['non_findings'])} non-findings, {len(rep['harnesses'])} harnesses")
sys.exit(1 if errs else 0)
