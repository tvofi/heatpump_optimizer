import sys, json, tempfile, pathlib
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root/"tests"))
import closure
base = json.loads((root/"tests/closures.json").read_text())
FILES = [["dev/programme/delivery/9999.md"], ["dev/programme/rosters/wave-r10-groups.json"], ["dev/programme/HANDOVER.md"]]
for label, add in (("committed table", []), ("with the two entries", ["dev/programme/rosters/critical-path.json","dev/programme/rosters/wave-r9-groups.json"])):
    p = json.loads(json.dumps(base)); p["inert_reads"]["tests/entities.py"] = sorted(set(p["inert_reads"]["tests/entities.py"]) | set(add))
    t = pathlib.Path(tempfile.mktemp(suffix=".json")); t.write_text(json.dumps(p)); closure.CLOSURES = t
    for f in FILES:
        r = closure.affected(f)
        print(label, f, r["case"], "entities.py" if "tests/entities.py" in r["rederive"] else "-", r["why"].get("tests/entities.py",{}).get("via",""))
