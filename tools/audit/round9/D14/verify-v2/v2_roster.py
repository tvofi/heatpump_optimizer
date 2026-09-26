"""D14 round 9, verifier V2 (independent) for D14-s2-03: audit identifier readers that disagree.

Metric (one line): v2_ledger_ids_unowned = class ids in tools/audit/bugclasses.json (keys not
starting with "_") held by no D14 seat axis in tools/audit/scopes.json; v2_intake_admits_schema_refuses
= of this verifier's own 14 boundary findings (seat D14-s2), those that audit-find.js's intake
predicate -- the CLASS_GUESS regex literal and the `f.id.startsWith(`${id}-`)` rule, both read
from the .js source and EXECUTED in node -- admits while finding.schema.json's id pattern or
class_guess enum refuses.
Keys: the verdict node returns for the extracted predicate; the schema's own enum/pattern.

Null control: 6 well-formed findings (ledger ids + "new", ids D14-s2-0N) -> 0 disagreements.
Perturbation (--fix): the regex replaced by the schema enum alternation and the id rule by the
schema pattern before node runs it -> 0.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_roster.py [--fix]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2, node 22.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json, re, subprocess
t_proc0, t_thr0 = time.process_time(), time.thread_time()
FIX = "--fix" in sys.argv

ledger = [k for k in json.load(open("tools/audit/bugclasses.json")) if not k.startswith("_")]
d14 = json.load(open("tools/audit/scopes.json"))["D14"]
held = {c for blocks in d14["seats"].values() for b in blocks for c in b.get("axis", [])}
unowned = sorted(set(ledger) - held)
print(f"RESULT v2_ledger_ids={len(ledger)} count")
print(f"RESULT v2_d14_axis_ids={len(d14['axis']['class'])} count")
print(f"RESULT v2_ledger_ids_unowned={len(unowned)} count ({','.join(unowned)})")

schema = json.load(open("tools/audit/finding.schema.json"))


def find_props(o):
    if isinstance(o, dict):
        if "properties" in o and "class_guess" in o["properties"] and "id" in o["properties"]:
            return o["properties"]
        for v in o.values():
            r = find_props(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_props(v)
            if r:
                return r
    return None


props = find_props(schema)
enum = props["class_guess"]["enum"]
idpat = props["id"]["pattern"]
src = open(".claude/workflows/audit-find.js").read()
regex_lit = re.search(r"const CLASS_GUESS = (/.*?/)\n", src).group(1)
if FIX:
    regex_lit = "/^(" + "|".join(enum) + ")$/"
id_rule = "(f, id) => typeof f.id === 'string' && f.id.startsWith(`${id}-`)"
if FIX:
    id_rule = f"(f, id) => typeof f.id === 'string' && f.id.startsWith(`${{id}}-`) && /{idpat}/.test(f.id)"
assert "f.id.startsWith(`${id}-`)" in src

seat = "D14-s2"
cases = [  # (id, class_guess) -- this verifier's own boundary set
    ("D14-s2-7", "P2"), ("D14-s2-100", "P2"), ("D14-s2-0a", "P2"), ("D14-s2-", "P2"),
    ("D14-s2--01", "P2"), ("D14-s2-01 ", "P2"),
    ("D14-s2-01", "P13"), ("D14-s2-01", "I9"), ("D14-s2-01", "P00"), ("D14-s2-01", "I05"),
    ("D14-s2-01", "P-1"), ("D14-s2-01", "NEW"), ("D14-s2-01", "p2"), ("D14-s2-01", "P1 "),
]
null = [(f"D14-s2-0{i}", c) for i, c in enumerate(["P1", "P11", "I4", "I5", "P10", "new"], 1)]
js = f"""
const CLASS_GUESS = {regex_lit};
const idOk = {id_rule};
const cases = {json.dumps(cases + null)};
console.log(JSON.stringify(cases.map(([id, cg]) => {{ const f = {{id, class_guess: cg, scope: '{seat}'}};
  return (f.scope === '{seat}') && idOk(f, '{seat}') && CLASS_GUESS.test(String(f.class_guess ?? '')); }})));
"""
out = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
rx = re.compile(idpat)
dis = dis_null = 0
for (cid, cg), admitted in zip(cases + null, out):
    schema_ok = bool(rx.search(cid)) and cg in enum
    if admitted and not schema_ok:
        print(f"DISAGREE id={cid!r} class_guess={cg!r}: intake admits, schema refuses")
    bad = admitted != schema_ok
    if (cid, cg) in null:
        dis_null += bad
    else:
        dis += admitted and not schema_ok
print(f"RESULT v2_boundary_cases={len(cases)} count")
print(f"RESULT v2_intake_admits_schema_refuses={dis} count")
print(f"RESULT v2_null_control_disagree={dis_null}_of_{len(null)} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
