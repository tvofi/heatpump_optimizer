"""D14-s2 / class I4 -- the audit's finding identity is defined by several readers that disagree.

Concept: which bug-class ids exist, and which finding records are admissible.
Readers enumerated (seam rule: every file under tools/audit/ and .claude/workflows/
that parses a class id or a finding id -- `--seams` prints them):
  L  tools/audit/bugclasses.json keys                         (the ledger: the definition)
  S  tools/audit/finding.schema.json class_guess enum / id pattern
  A  tools/audit/scopes.json D14 axis.class                   (what the D14 seats are cut from)
  U  the union of the D14 seats' axis lists                   (what the D14 seats measure)
  R  .claude/workflows/audit-find.js intake (CLASS_GUESS and the id rule), executed in node
  Q  .claude/workflows/audit-find.js reportSchema class_guess (the agent's return schema)

Metric (one line): (reader, boundary case) verdicts that differ from the ledger+schema
  verdict, plus ledger class ids no D14 seat's cells hold.
Count key: the verdict each reader DELIVERS when executed on the case (the intake code
  run in a node vm on a synthetic report; check_scopes.check() run on the scopes) --
  never a reader's source text.

Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/i4_roster.py [--seams | --dims <ref>...]
  --dims HEAD 8d731d77^ : the dimension roster (positive control: R7-INSTR-01, DIMS stopped at D12)
Expected (baseline 1936d5ca): ledger_ids_no_d14_seat=1 (P11), exact;
  check_scopes_D14_ok=True while it is unowned; intake_admits_schema_refuses=11 of
  22 boundary cases, exact; schema_refuses_intake_admits=0.  Perturbations:
  (a) the D14 axis set to the ledger ids in memory -> check_scopes_D14_ok=False
      (the checker now sees the unowned P11 cells), and ledger_ids_no_d14_seat
      stays 1 until a seat is given P11;
  (b) the intake's CLASS_GUESS replaced by the ledger-built alternation and its
      id rule by the schema's pattern -> intake_admits_schema_refuses=0.
Null control: the cases every reader should admit (each ledger id with a
  well-formed id) -> 0 disagreements.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container B8,
  4 cores, 15 GB, CPython 3.14.0rc2, node v22.22.2. Counts only.
Instrumented symbols: tools/audit/check_scopes.py:check,
  .claude/workflows/audit-find.js:CLASS_GUESS (and the intake loop it gates).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path

_P0, _T0 = time.process_time(), time.thread_time()
NODE = os.environ.get("NODE", "/opt/node22/bin/node")
FIND = Path(".claude/workflows/audit-find.js")


def load_check_scopes():
    """tools/audit/check_scopes.py calls main() at import; load its functions without running it."""
    src = Path("tools/audit/check_scopes.py").read_text()
    src = re.sub(r"\nmain\(\)\s*$", "\n", src)
    mod = type(sys)("check_scopes")
    mod.__file__ = "tools/audit/check_scopes.py"
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def intake_block(text, class_re=None, id_rule=None):
    start = text.index("const CLASS_GUESS")
    end = text.index("// The scope wall's other side")
    block = text[start:end]
    if class_re is not None:
        block = re.sub(r"const CLASS_GUESS = /.*?/\n", f"const CLASS_GUESS = {class_re}\n", block, count=1)
    if id_rule is not None:
        block = block.replace("f.id.startsWith(`${id}-`)", id_rule)
    return block


def run_intake(block, seat, findings):
    driver = (
        "const vm = require('vm');\n"
        f"const block = {json.dumps(block)};\n"
        f"const ctx = {{ REPORTED: [{json.dumps(seat)}], reports: {{ {json.dumps(seat)}: {{ findings: {json.dumps(findings)} }} }}, JSON }};\n"
        "vm.createContext(ctx);\n"
        "vm.runInContext(block + '\\n;globalThis.__out = {accepted: accepted.map(f => f.id), rejected: rejected.map(r => r.id)};', ctx);\n"
        "console.log(JSON.stringify(ctx.__out));\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "drive.cjs"
        p.write_text(driver)
        out = subprocess.run([NODE, str(p)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def dim_roster(ref):
    """The dimension roster at a ref: the briefs define it; every other reader is compared."""
    def show(path):
        r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    briefs = sorted(re.findall(r"^tools/audit/briefs/(D\d+)\.md$",
                               subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "tools/audit/briefs/"],
                                              capture_output=True, text=True).stdout, re.M), key=lambda d: int(d[1:]))
    readers = {}
    find = show(".claude/workflows/audit-find.js")
    if find:
        m = re.search(r"^const DIMS = (\[.*?\])", find, re.M)
        if m:
            readers["audit-find.js:DIMS"] = json.loads(subprocess.run([NODE, "-e", f"console.log(JSON.stringify({m.group(1)}))"],
                                                                    capture_output=True, text=True, check=True).stdout)
    for path, key in (("tools/audit/scopes.json", "scopes.json keys"), ("tools/audit/rotation.json", "rotation.json keys")):
        t = show(path)
        if t:
            readers[key] = [k for k in json.loads(t) if not k.startswith("_")]
    sch = show("tools/audit/finding.schema.json")
    if sch:
        pat = re.compile(json.loads(sch)["properties"]["dimension"]["pattern"])
        probe = [f"D{i}" for i in range(0, 20)]
        readers["finding.schema.json:dimension"] = [d for d in probe if pat.match(d)]
    gaps = 0
    for name, got in readers.items():
        miss, extra = sorted(set(briefs) - set(got)), sorted(set(got) - set(briefs))
        gaps += bool(miss or extra)
        print(f"DIMS[{ref}] {name}: missing {miss} extra {extra}")
    print(f"RESULT dim_roster_readers_disagreeing[{ref}]={gaps} count (of {len(readers)})")
    return gaps


def main():
    if "--dims" in sys.argv:
        for ref in sys.argv[sys.argv.index("--dims") + 1:] or ["HEAD"]:
            dim_roster(ref)
        return
    ledger = json.loads(Path("tools/audit/bugclasses.json").read_text())
    L = sorted(k for k in ledger if not k.startswith("_"))
    schema = json.loads(Path("tools/audit/finding.schema.json").read_text())
    fin = schema["definitions"]["finding"]["properties"]
    S = sorted(fin["class_guess"]["enum"])
    id_re = re.compile(fin["id"]["pattern"])
    scopes = json.loads(Path("tools/audit/scopes.json").read_text())
    A = scopes["D14"]["axis"]["class"]
    U = sorted({c for blocks in scopes["D14"]["seats"].values() for b in blocks for c in b.get("axis", A)})

    if "--seams" in sys.argv:
        hits = subprocess.run(["grep", "-rnE", r"class_guess|CLASS_GUESS|bugclasses\.json|\"class\": \[", "tools/audit", ".claude/workflows",
                               "--include=*.py", "--include=*.js", "--include=*.mjs", "--include=*.json"], capture_output=True, text=True).stdout
        rows = [h for h in hits.splitlines() if "/round" not in h.split(":")[0]]
        for h in rows:
            print("SEAM", h[:160])
        print(f"RESULT i4_reader_sites={len(rows)} count")
        return

    print(f"LEDGER {L}")
    print(f"D14_AXIS {A}")
    missing_axis = sorted(set(L) - set(A))
    missing_seats = sorted(set(L) - set(U))
    print(f"RESULT ledger_ids_not_on_d14_axis={len(missing_axis)} count ({','.join(missing_axis)})")
    print(f"RESULT ledger_ids_no_d14_seat={len(missing_seats)} count ({','.join(missing_seats)})")
    print(f"RESULT schema_enum_equals_ledger={S == sorted(L + ['new'])}")

    cs = load_check_scopes()
    tree = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()) or {"x"}
    only = {"D14": scopes["D14"]}
    buf = io.StringIO()
    with redirect_stdout(buf):
        ok = cs.check(only, tree, {})
    print(f"RESULT check_scopes_D14_ok={ok}")
    bad = copy.deepcopy(only)
    bad["D14"]["axis"]["class"] = L
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        ok2 = cs.check(bad, tree, {})
    unowned = [l for l in buf2.getvalue().splitlines() if "unowned" in l]
    print(f"RESULT check_scopes_D14_ok[perturbed:axis=ledger]={ok2}")
    print(f"RESULT check_scopes_unowned_lines[perturbed]={len(unowned)} count")

    # intake vs schema on generated boundary cases
    seat = "D14-s2"
    cls_cases = ["P1", "I4", "P11", "new", "P0", "P12", "P99", "I0", "I6", "P011", "p1", "NEW", "X1", "", "P1 "]
    id_cases = ["D14-s2-01", "D14-s2-1", "D14-s2-001", "D14-s2-xx", "D14-s2-", "D14-s2-01a", "D14-s2-99"]
    findings = [{"id": f"{seat}-{i + 10:02d}", "scope": seat, "class_guess": c} for i, c in enumerate(cls_cases)]
    findings += [{"id": i, "scope": seat, "class_guess": "P2"} for i in id_cases]
    text = FIND.read_text()

    def schema_ok(f):
        return f["class_guess"] in S and bool(id_re.match(f["id"])) and f["scope"] == seat

    def compare(out, label):
        acc = set(out["accepted"])
        a_not_s = [f for f in findings if f["id"] in acc and not schema_ok(f)]
        s_not_a = [f for f in findings if f["id"] not in acc and schema_ok(f)]
        for f in a_not_s:
            print(f"DISAGREE[{label}] intake admits, schema refuses: id={f['id']!r} class_guess={f['class_guess']!r}")
        print(f"RESULT intake_admits_schema_refuses[{label}]={len(a_not_s)} count")
        print(f"RESULT schema_admits_intake_refuses[{label}]={len(s_not_a)} count")
        return len(a_not_s)

    print(f"RESULT boundary_cases={len(findings)} count")
    compare(run_intake(intake_block(text), seat, findings), "baseline")
    alt = "/^(" + "|".join(L + ["new"]) + ")$/"
    compare(run_intake(intake_block(text, class_re=alt, id_rule=f"/{fin['id']['pattern']}/.test(f.id) && f.id.startsWith(`${{id}}-`)"), seat, findings), "perturbed")
    # null control: only admissible cases
    good = [{"id": f"{seat}-{i + 40:02d}", "scope": seat, "class_guess": c} for i, c in enumerate(L + ["new"])]
    out = run_intake(intake_block(text), seat, good)
    print(f"RESULT null_control_disagree={len(good) - len(out['accepted'])} count (of {len(good)})")

    pc, tc = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 'n/a'}")


if __name__ == "__main__":
    main()
