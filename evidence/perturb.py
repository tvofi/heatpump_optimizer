import sys, re
sys.path[:0] = ["tests/hastub", "tests", "custom_components", "tests"]
import doc_claims as d
tree = d._tracked()
base_read = d._read_tracked(tree)
docs = {p: (d.ROOT / p).read_text() for p in d.NAMED_DOCS}
def run(tree=tree, edits=None, docs=docs):
    edits = edits or {}
    def read(p):
        t = base_read(p) if p in tree else None
        if t is not None and p in edits:
            old, new = edits[p]
            assert (old.search(t) if isinstance(old, re.Pattern) else old in t), (p, old)
            t = t.replace(old, new) if not isinstance(old, re.Pattern) else old.sub(new, t)
        return t
    f, pend, n = d.named_element_findings(docs, tree, read)
    return f, pend, n
f, p, n = run()
print("NULL findings", len(f), "pending", len(p), dict(n))
P = "custom_components/heatpump_optimizer"
cases = [
 ("ci.yml job prelude", {".github/workflows/ci.yml": ("\n  prelude:", "\n  preamble:")}),
 ("tests.yml matrix 3.14", {".github/workflows/tests.yml": ("3.14", "3.15")}),
 ("bus.sh push-verdict", {"tools/audit/seat/bus.sh": (re.compile(r"(?<![\w-])push-verdict(?![\w-])"), "push-verdictX")}),
 ("heartbeat.sh --once", {"tools/audit/seat/heartbeat.sh": (re.compile(r"(?<![\w-])--once(?![\w-])"), "--oneX")}),
 ("ledger KINDS handoff-no-pr", {"tools/audit/seat/ledger.py": ('"handoff-no-pr"', '"handoff-no-prX"')}),
 ("services.yaml simulate_plan", {P+"/services.yaml": (re.compile(r"^simulate_plan:", re.M), "simulate_planX:")}),
]
for name, e in cases:
    try:
        f, _, _ = run(edits=e)
        print(f"{name}: {len(f)} finding(s)", f[:2])
    except AssertionError as ex:
        print(name, "EDIT NOT APPLIED", ex)
# module list: drop sysid from tree
t2 = {x for x in tree if not (x == P+"/sysid.py" or x.startswith(P+"/sysid/"))}
f, _, _ = run(tree=t2); print("module sysid removed:", len(f), f[:2])
f, _, _ = run(edits={"custom_components/heatpump_optimizer/inputs.py": ("class InputReader", "class InputReading")}); print("class InputReader renamed in custom_components/heatpump_optimizer/inputs.py:", len(f), f[:3])
