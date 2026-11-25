"""D10-s2 gold rule repair-issues: every repair notice the integration raises
has a title and a description (or a fix flow) in every shipped catalogue,
with the placeholders the raise site passes, and a fixable notice has a flow.

Sites: every call of issues.create_issue / issues.set_issue (and their
aliases) and ir.async_create_issue in the package, read from the AST; the
translation key is the call's translation_key, or for set_issue its issue_id
(issues.set_issue keys the notice on its id), with module-level string
constants resolved across the package.
Metric: bad = (site, catalogue) pairs failing: key unresolvable, key absent,
no title, neither description nor fix_flow, or literal placeholders differing
from the message's fields; plus fixable sites whose key repairs.py's
async_create_fix_flow does not route to a flow with that step.
Key: the raise site's own arguments as written, against the catalogue text
Home Assistant renders.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s2/repair_issues.py [--perturb]
Expected at baseline 92d38ecb: RESULT bad=0, exact; RESULT sites printed.
--perturb deletes the de catalogue's "solve_failures" issue (in memory):
bad rises by at least 1.
Instrumented symbol: heatpump_optimizer.issues:set_issue / create_issue
callers and custom_components/heatpump_optimizer/translations/*.json.
Machine: local macOS box B2, Python 3.14 venv-ci.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import resource
import string
import sys
import time
from pathlib import Path

PKG = Path("custom_components/heatpump_optimizer")
CATS = {n: json.loads((PKG / f).read_text()).get("issues", {}) for n, f in (
    ("strings", "strings.json"), ("en", "translations/en.json"),
    ("sv", "translations/sv.json"), ("de", "translations/de.json"))}
if "--perturb" in sys.argv:
    del CATS["de"]["solve_failures"]
TREES = {p: ast.parse(p.read_text()) for p in sorted(PKG.glob("*.py"))}
CONSTS = {}
for tree in TREES.values():
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        for t in targets:
            if isinstance(t, ast.Name) and isinstance(value, ast.Constant) and isinstance(value.value, str):
                CONSTS[t.id] = value.value
CREATE = {"create_issue", "_create_issue", "async_create_issue"}
SET = {"set_issue", "report"}


def fname(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None


def resolve(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.Name) and node.id in CONSTS:
        return [CONSTS[node.id]]
    if isinstance(node, ast.Attribute) and node.attr in CONSTS:
        return [CONSTS[node.attr]]
    if isinstance(node, ast.IfExp):
        a, b = resolve(node.body), resolve(node.orelse)
        return a + b if a and b else None
    return None


def fields(msg):
    return {f for _, f, _, _ in string.Formatter().parse(msg or "") if f}


def catalogue_text(entry):
    text = (entry.get("title") or "") + (entry.get("description") or "")
    for step in (entry.get("fix_flow") or {}).get("step", {}).values():
        text += (step.get("title") or "") + (step.get("description") or "")
    return text


sites, bad, dynamic, fixable = 0, [], [], []
for path, tree in TREES.items():
    if path.name == "issues.py":
        continue  # the writer itself; its callers are the sites
    # ConfigNotices.report is a writer too: its callers are the sites.
    writer = {id(n) for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef)
              and fn.name == "report" for n in ast.walk(fn)}
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call) or fname(call) not in CREATE | SET or id(call) in writer:
            continue
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        where = f"{path.name}:{call.lineno}"
        if fname(call) in SET and len(call.args) > 2 and isinstance(call.args[2], ast.Constant) \
                and call.args[2].value is False:
            continue  # a clear, not a raise
        if fname(call) == "report":
            key_node = call.args[1] if len(call.args) > 1 else kw.get("issue_id")
            ph = call.args[3] if len(call.args) > 3 else kw.get("placeholders")
            fix = None
        elif fname(call) in SET:
            key_node = call.args[1] if len(call.args) > 1 else kw.get("issue_id")
            ph = kw.get("placeholders")
            fix = kw.get("fixable")
        else:
            key_node = kw.get("translation_key")
            ph = kw.get("translation_placeholders")
            fix = kw.get("is_fixable")
        sites += 1
        keys = resolve(key_node) if key_node is not None else None
        if not keys:
            bad.append(f"{where} unresolvable key {ast.unparse(key_node) if key_node else None}")
            continue
        passed = None
        if isinstance(ph, ast.IfExp) and isinstance(ph.body, ast.Dict):
            ph = ph.body  # the raise arm; the other arm is the clear
        if isinstance(ph, ast.Dict):
            passed = {k.value for k in ph.keys if isinstance(k, ast.Constant)}
        elif ph is not None:
            dynamic.append(f"{where} {keys} placeholders {ast.unparse(ph)}")
        else:
            passed = set()
        if isinstance(fix, ast.Constant) and fix.value is True:
            fixable.extend(keys)
        for key in keys:
            for name, cat in CATS.items():
                entry = cat.get(key)
                if not entry:
                    bad.append(f"{where} key {key} missing in {name}")
                    continue
                if not entry.get("title"):
                    bad.append(f"{where} key {key} no title in {name}")
                if not entry.get("description") and not entry.get("fix_flow"):
                    bad.append(f"{where} key {key} no description/fix_flow in {name}")
                if passed is not None and fields(catalogue_text(entry)) - passed:
                    bad.append(f"{where} key {key} {name} needs {sorted(fields(catalogue_text(entry)) - passed)} not passed")
for line in dynamic:
    print("DYNAMIC", line)
print("FIXABLE", sorted(set(fixable)))
for line in bad:
    print("BAD", line)
used = set()
for path, tree in TREES.items():
    for call in ast.walk(tree):
        if isinstance(call, ast.Call) and fname(call) in CREATE | SET:
            kw = {k.arg: k.value for k in call.keywords if k.arg}
            node = (call.args[1] if fname(call) in SET and len(call.args) > 1 else kw.get("translation_key"))
            used.update(resolve(node) or [])
orphans = sorted(set(CATS["strings"]) - used)
print("ORPHAN_CATALOGUE_KEYS", orphans)
print(f"RESULT sites={sites} count")
print(f"RESULT dynamic_placeholders={len(dynamic)} count")
print(f"RESULT orphan_keys={len(orphans)} count")
print(f"RESULT bad={len(bad)} count")
print(f"RESULT thread_factor={time.process_time() / (time.thread_time() or 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
