import sys, pathlib
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root/"tests"))
import closure
for f in (["dev/programme/delivery/9999.md"], ["dev/programme/rosters/critical-path.json"], ["dev/programme/rosters/wave-r9-groups.json"], ["dev/programme/rosters/wave-r10-groups.json"]):
    s = closure.select(f); a = closure.affected(f)
    print(f[0], "select:", s["mode"], "entities.py" in " ".join(s.get("run", [])), "| affected:", a["case"], "tests/entities.py" in a["rederive"])
