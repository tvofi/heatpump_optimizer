"""Review-2 seat: plants past revision 1's static half that its self-test does not try.
    python3 -I tools/plant_unitcheck2.py <rev1>/measure/rev/unitcheck2.py <rev1>/measure/rev/fixtures/tests.yml
Q1 swap two adjacent steps of one job (order is semantic: a check moved after the step
   it guards, a restore moved after the program it restores);
Q2 move a step from one job to another job under the same name (keyed <job>|<name>, so
   this one MUST be refused: a control the instrument should pass as refusing);
Q3 an unmapped `changed` row that only flips a YAML scalar's type ("true" -> true)."""
import copy, importlib.util, sys, tempfile
from pathlib import Path
import yaml
spec = importlib.util.spec_from_file_location("uc2", sys.argv[1]); U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
doc = yaml.safe_load(Path(sys.argv[2]).read_text())
jobs = doc["jobs"]
jid = max(jobs, key=lambda j: len(jobs[j].get("steps") or []))
def run(label, after):
    print(label); rc = U.static(doc, after, {}, quiet=False); print(f"  -> rc {rc}  ({'refused' if rc else 'PASSED'})\n")
a = copy.deepcopy(doc); st = a["jobs"][jid]["steps"]
i = next(k for k in range(1, len(st)) if st[k].get("name") and st[k-1].get("name"))
st[i-1], st[i] = st[i], st[i-1]
run(f"Q1 swap steps {i-1},{i} of {jid}: {doc['jobs'][jid]['steps'][i-1].get('name')!r} <-> {doc['jobs'][jid]['steps'][i].get('name')!r}", a)
# a step that guards: the first step whose name says check/verify/refuse, moved to the end
a = copy.deepcopy(doc); st = a["jobs"][jid]["steps"]
k = next((k for k, s in enumerate(st) if any(w in (s.get("name") or "").lower() for w in ("check", "verify", "refuse", "restore"))), 1)
s = st.pop(k); st.append(s)
run(f"Q1b move step {k} of {jid} ({s.get('name')!r}) to the end of the job", a)
a = copy.deepcopy(doc); other = next(j for j in jobs if j != jid and jobs[j].get("steps"))
s = a["jobs"][jid]["steps"].pop(1); a["jobs"][other]["steps"].append(s)
run(f"Q2 (control) move a step from {jid} to {other}", a)
print(f"null: rc {U.static(doc, copy.deepcopy(doc), {}, quiet=True)}")
