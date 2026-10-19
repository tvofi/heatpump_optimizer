"""Round-3 review seat: plants past revision 2's `<job>|order` row.
    python3 -I tools/plant_unitcheck3.py <rev2>/measure/rev/unitcheck2.py <rev2>/measure/rev/fixtures/tests.yml
G1 a map-admitted GAINED step inserted at the job's first position (before checkout);
G2 the same gained step appended at the end (null for G1: both are what the map admits);
G3 a map-admitted RENAME moved to the end of the job (the order row follows renames);
D1 two same-key unnamed steps swapped when their bodies differ (keys get #2 by position);
Q1 control: revision 2's own refusal of an unmapped swap."""
import copy, importlib.util, sys
from pathlib import Path
import yaml
spec = importlib.util.spec_from_file_location("uc2", sys.argv[1]); U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
doc = yaml.safe_load(Path(sys.argv[2]).read_text())
J = "coverage"
def run(label, after, m):
    print(label); rc = U.static(doc, after, m, quiet=False); print(f"  -> rc {rc}  ({'refused' if rc else 'PASSED'})\n")
NEW = {"name": "Say the decision", "run": "echo decided"}
a = copy.deepcopy(doc); a["jobs"][J]["steps"].insert(0, dict(NEW))
run("G1 gained step (map: gained) inserted at position 0 of coverage, before its checkout", a, {"gained": [f"{J}|Say the decision"]})
a = copy.deepcopy(doc); a["jobs"][J]["steps"].append(dict(NEW))
run("G2 the same gained step appended at the end (what the map meant)", a, {"gained": [f"{J}|Say the decision"]})
a = copy.deepcopy(doc); st = a["jobs"][J]["steps"]
i = next(k for k, s in enumerate(st) if s.get("name") and k < len(st) - 2)
old = st[i]["name"]; s = st.pop(i); s["name"] = old + " (renamed)"; st.append(s)
run(f"G3 step {old!r} renamed by the map AND moved to the end", a, {"renames": {f"{J}|{old}": f"{J}|{old} (renamed)"}})
# D1: find a job with two steps sharing a key
d1 = None
for jid, job in doc["jobs"].items():
    keys = {}
    for k, s in enumerate(job.get("steps") or []):
        nm = s.get("name") or (f"run:{str(s['run']).strip().splitlines()[0]}" if "run" in s else f"uses:{s.get('uses')}")
        nm = U.SHA.sub("<sha>", nm); keys.setdefault(nm, []).append(k)
    for nm, ks in keys.items():
        if len(ks) > 1 and job["steps"][ks[0]] != job["steps"][ks[1]]:
            d1 = (jid, nm, ks[0], ks[1]); break
    if d1: break
if d1:
    jid, nm, x, y = d1; a = copy.deepcopy(doc); st = a["jobs"][jid]["steps"]; st[x], st[y] = st[y], st[x]
    run(f"D1 swap the two {nm!r} steps of {jid} (positions {x}, {y})", a, {})
else:
    print("D1 no job has two same-key steps with different bodies in this fixture\n")
a = copy.deepcopy(doc); st = a["jobs"][J]["steps"]; st[2], st[3] = st[3], st[2]
run("Q1 control: unmapped swap of coverage steps 2,3", a, {})
print(f"null: rc {U.static(doc, copy.deepcopy(doc), {}, quiet=True)}")
