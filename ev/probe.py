import json, subprocess, copy, pathlib
src = pathlib.Path("tools/audit/check_scopes.py").read_text().rsplit("\nmain()", 1)[0]
ns = {"__name__": "cs", "__file__": "tools/audit/check_scopes.py"}; exec(compile(src, "check_scopes.py", "exec"), ns)
gaps, match, OBJ = ns["evaluation_gaps"], ns["match"], ns["OBJECTIVE"]
tree = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD"], text=True).split())
spec = json.load(open(OBJ)); objs = sorted(match(tree, spec["objects"].values()))
root = subprocess.check_output(["git", "rev-list", "--max-parents=0", "HEAD"], text=True).split()[0]
merged = lambda sha: subprocess.run(["git", "merge-base", "--is-ancestor", str(sha), "HEAD"], capture_output=True).returncode == 0
prev, path = "dev/audit/rounds/round10/OBJECTIVE.json", "dev/audit/rounds/round11/EVALUATION.json"
def run(ev, terms):
    files = {OBJ: open(OBJ).read(), prev: json.dumps({"terms": terms}), path: json.dumps(ev)}
    return gaps(11, tree | set(files), lambda f: files[f], merged)
noread = {t: {"no_read": "x"} for t in spec["terms"]}
base = {"round": 11, "reads": prev, "evaluator": "evaluator-r11", "reviewer": "reviewer-r11",
        "objects": {f: {"verdict": "keep", "evidence": "NO-READ"} for f in objs}, "cards": {}}
def P(name, ev=base, terms=noread):
    g = run(ev, terms); print(f"RESULT {name}: {len(g)} gap(s) -> {'ACCEPTED' if not g else 'refused: ' + g[0][:90]}")
P("P0 control: all 13 terms NO-READ 'x', all %d objects keep, no cards" % len(objs))
e = copy.deepcopy(base); e["evaluator"] = "orchestrator-r10"; P("P1 evaluator named 'orchestrator-r10'", e)
e = copy.deepcopy(base); e["evaluator"] = "the orchestrator"; e["reviewer"] = "Orchestrator"; P("P2 evaluator 'the orchestrator', reviewer 'Orchestrator'", e)
e = copy.deepcopy(base); e["objects"][objs[0]] = {"verdict": "remove", "evidence": "e", "card": "C1"}; e["cards"] = {"C1": {"decision": "accepted", "merged": root}}
P("P3 accepted card 'merged' at the repository's root commit", e)
P("P4 a value whose enumerator is 'by hand'", terms=dict(noread, escapes={"value": 0, "enumerator": "by hand"}))
P("P5 a value of null with an enumerator", terms=dict(noread, regret={"value": None, "enumerator": "cmd"}))
e = copy.deepcopy(base); e["objects"][objs[0]] = {"verdict": "remove", "evidence": "NO-READ: none", "card": "C1"}; e["cards"] = {"C1": {"decision": "rejected"}}
P("P6 a remove on NO-READ evidence (0017 s3: never on a NO-READ)", e)
P("P7 an unowned item / missing owner criterion with no card (0017 s6 'yields a card')")
e = copy.deepcopy(base); e["extra"] = 1; e["objects"]["CLAUDE.md"] = {"verdict": "remove"}; P("P8 an object row outside the globs, no evidence", e)
print("objects by class:", {k: len(match(tree, [g])) for k, g in spec["objects"].items()}, "total", len(objs))
