"""Reviewer's probes at the head: the round-1 probes P0-P8 and R12 ported to evaluation_gaps'
six-callback signature (source read from the commit, not the checkout), plus new ones N1-N8."""
import json, subprocess, copy
git = lambda *a: subprocess.check_output(["git", *a], text=True)
src = git("show", "HEAD:tools/audit/check_scopes.py").rsplit("\nmain()", 1)[0]
ns = {"__name__": "cs", "__file__": "tools/audit/check_scopes.py"}; exec(compile(src, "check_scopes.py", "exec"), ns)
gaps, match, OBJ, og = ns["evaluation_gaps"], ns["match"], ns["OBJECTIVE"], ns["object_globs"]
tree = set(git("ls-tree", "-r", "--name-only", "HEAD").split("\n")) - {""}
spec = json.loads(git("show", "HEAD:" + OBJ)); objs = sorted(match(tree, og(spec)))
prev, path = "dev/audit/yardstick/round10/OBJECTIVE.json", "dev/audit/yardstick/round11/EVALUATION.json"
ME = "tools/audit/check_scopes.py"
def run(ev, terms, revdoc=None):
    files = {OBJ: json.dumps(spec), prev: json.dumps({"terms": terms}), path: json.dumps(ev)}
    sh = lambda f, at=None: (revdoc or json.dumps({"objects": ev.get("objects")})) if at else files[f]
    return gaps(11, tree | set(files), sh, lambda s: s in ("rev", "abc", "old", "root"),
                lambda a, b: (a, b) in (("old", "rev"), ("rev", "rev"), ("root", "rev")),
                lambda c: {"abc": {ME}, "old": {ME}}.get(c, set()))
nr = lambda b="R11-PRE-ROUND-METRICS": {"no_read": "no enumerator", "would_read": "the record", "builder": b}
noread = {t: nr() for t in spec["terms"]}
owner = {}
for i, k in enumerate(list(spec["thresholds"]) ):
    owner[f"T{i}"] = {"decision": "deferred", "ruling": "tvofi, review of #N", "threshold": k}
for d, p in spec["owner_criteria"].items():
    if p is None: owner[f"K{d}"] = {"decision": "deferred", "ruling": "tvofi, review of #N", "criterion": d}
good = {"round": 11, "reads": prev, "evaluator": "evaluator-r11", "reviewer": "evalreview-r11",
        "review": {"verdict": "approve", "sha": "rev"},
        "objects": {f: {"verdict": "keep", "evidence": "NO-READ: the token ledger"} for f in objs}, "cards": copy.deepcopy(owner)}
old_noread = {t: {"no_read": "x"} for t in spec["terms"]}
old_base = {"round": 11, "reads": prev, "evaluator": "evaluator-r11", "reviewer": "reviewer-r11",
            "objects": {f: {"verdict": "keep", "evidence": "NO-READ"} for f in objs}, "cards": {}}
def P(name, ev, terms=noread, **kw):
    g = run(ev, terms, **kw); print(f"RESULT {name}: {len(g)} gap(s) -> {'ACCEPTED' if not g else 'refused: ' + g[0][:110]}")
def E(fn, base=good):
    c = copy.deepcopy(base); fn(c); return c
P("C  control: complete record (NO-READ terms with builder, owner values carded, approve review)", good)
P("C2 control: a real read with a tracked enumerator", good, dict(noread, first_pass={"value": 0.5, "enumerator": "python3 tools/audit/seat/flow_metrics.py --window"}))
P("P0 round-1 control verbatim (all NO-READ 'x', all keep, no cards, no review)", old_base, old_noread)
P("P1 evaluator 'orchestrator-r10'", E(lambda e: e.update(evaluator="orchestrator-r10")))
P("P2 evaluator 'the orchestrator', reviewer 'Orchestrator'", E(lambda e: e.update(evaluator="the orchestrator", reviewer="Orchestrator")))
def p3(e): e["objects"][objs[0]] = {"verdict": "remove", "evidence": "e", "card": "C1"}; e["cards"]["C1"] = {"decision": "accepted", "ruling": "r", "merged": "root", "object": objs[0]}
P("P3 accepted card merged at an ancestor of the review (the root commit)", E(p3))
P("P4 a value whose enumerator is 'by hand'", good, dict(noread, escapes={"value": 0, "enumerator": "by hand"}))
P("P5 a null value with an enumerator", good, dict(noread, regret={"value": None, "enumerator": "python3 " + ME}))
def p6(e): e["objects"][objs[0]] = {"verdict": "remove", "evidence": "NO-READ: none", "card": "C1"}; e["cards"]["C1"] = {"decision": "rejected", "ruling": "r"}
P("P6 a remove on NO-READ evidence", E(p6))
P("P7 unset owner values with no card", E(lambda e: e.update(cards={})))
P("P7b unowned read 2 with one unowned card", E(lambda e: e["cards"].update(U={"decision": "deferred", "ruling": "r", "unowned": "u"})), dict(noread, unowned={"value": 2, "enumerator": "python3 " + ME}))
P("P8 an object row outside the globs", E(lambda e: e["objects"].update({"README.md": {"verdict": "keep", "evidence": "e"}})))
P("R12 a verdict outside keep/change/remove ('retain') with a card", E(lambda e: (e["objects"].update({objs[0]: {"verdict": "retain", "evidence": "e", "card": "T0"}}))))
print("--- new probes")
P("N1 every NO-READ builder a group that does not exist ('R99-NOBODY'), all keep, owner cards all 'deferred'", good, {t: nr("R99-NOBODY") for t in spec["terms"]})
def n2(e): e["objects"][objs[0]] = {"verdict": "remove", "evidence": "unscored (NO-READ: no ledger)", "card": "T0"}
P("N2 a remove whose evidence says NO-READ but does not start with it", E(n2))
def n2b(e): e["objects"][objs[0]] = {"verdict": "remove", "evidence": "no-read: none", "card": "T0"}
P("N2b a remove on lower-case 'no-read: none'", E(n2b))
P("N3 evaluator 'orch-r10' (the orchestrator abbreviated), reviewer 'orch-r10-b'", E(lambda e: e.update(evaluator="orch-r10", reviewer="orch-r10-b")))
P("N4 a read whose enumerator is 'CLAUDE.md by hand'", good, dict(noread, escapes={"value": 0, "enumerator": "CLAUDE.md by hand"}))
P("N5 a read of NaN", good, dict(noread, escapes={"value": float("nan"), "enumerator": "python3 " + ME}))
P("N6 review 'approve' at a sha whose EVALUATION.json graded other objects", good, revdoc=json.dumps({"objects": {}}))
P("N7 keep rows with bare evidence 'NO-READ' (0017 s3: NO-READ: and the record that would score it)", E(lambda e: e.update(objects={f: {"verdict": "keep", "evidence": "NO-READ"} for f in objs})))
def n8(e): e["cards"]["T0"]["decision"] = "accepted"; e["cards"]["T0"].update(merged="abc", paths=[ME])
P("N8 threshold card 'accepted', merged commit changes check_scopes.py and not objective.json (value still null)", E(n8))
print("objects by class:", {k: len(match(tree, v)) for k, v in spec["objects"].items()}, "total", len(objs))
