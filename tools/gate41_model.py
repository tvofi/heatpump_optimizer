"""Model of phase 2 DESIGN.md section 4.1's gate predicate, AS WRITTEN, plus the
job guards of section 2.2 and GitHub's documented single-pending concurrency rule.
Review seat's own instrument (not the designers'). Inputs are synthetic run shapes;
job names follow the design's naming rule `<unit> / <job>`.

    python3 -I gate41_model.py
"""
REQUIRED = {
    "tests": ["fast (3.14)", "browser", "briefs", "typing", "mutation", "closures", "closure-scope"],
    "governance": ["policy-docs", "wave-script", "env-matrix"],
    "codeql": ["Analyze (actions)", "Analyze (javascript-typescript)", "Analyze (python)"],
    "hassfest": ["hassfest"], "validate": ["validate-hacs"],
    "pr-contract": ["pr-contract"], "budget-raise-gate": ["budget-raise-gate"],
}
BODY = {"pr-contract", "budget-raise-gate"}          # "† only when a PR is named"
CODE_UNITS = {"tests", "codeql", "governance", "hassfest", "validate"}  # 2.2 "# code units"

def unit_jobs(units, concl="success"):
    return {f"{u} / {n}": concl for u in units for n in REQUIRED[u]}

def run(event, action, kind, pr, base, changes_base=False):
    """Jobs one ci.yml run produces under section 2.2's guards."""
    units = set()
    if kind == "code": units |= {"tests", "codeql"}                        # if: kind == 'code'
    if not (action == "edited" or event == "pull_request_review"):         # governance/hassfest/validate guard
        units |= {"governance", "hassfest", "validate"}
    if pr != "": units |= BODY                                              # if: pr != ''
    return {"event": event, "kind": kind, "pr": pr, "base": base, "jobs": unit_jobs(units)}

def gate(this, code_runs_at_head):
    """Section 4.1, line for line."""
    jobs = dict(this["jobs"])
    if this["kind"] == "verdict":
        done = [r for r in code_runs_at_head if r["kind"] == "code"]
        if not done: return "FAIL no code verdict at this head"
        carried = done[-1]
        jobs.update({k: v for k, v in carried["jobs"].items() if k.split(" / ")[0] in CODE_UNITS})
    bad = []
    for unit, names in REQUIRED.items():
        if unit in BODY and this["pr"] == "": continue                     # applicability from prelude's pr
        for n in names:
            if n == "closure-scope" and this["event"] == "push": continue
            c = jobs.get(f"{unit} / {n}")
            if c is None: bad.append(f"{unit} / {n}: ABSENT")
            elif c != "success": bad.append(f"{unit} / {n}: {c}")
    return "pass" if not bad else "FAIL " + "; ".join(bad[:3]) + (" ..." if len(bad) > 3 else "")

def pending_replace(group_pending, new):
    """GitHub concurrency (docs, actions-group-concurrency.md): a new queued run
    CANCELS any existing pending run in the group, whatever cancel-in-progress says."""
    return [new]   # the old pending run is cancelled before it creates any job

cases = []
C1 = run("pull_request", "synchronize", "code", "7", base="main")
cases.append(("A null: synchronize code run, all units green", gate(C1, []), "pass"))

B = run("pull_request", "synchronize", "code", "", base="main")   # prelude emitted pr='' (planted)
cases.append(("B prelude emits pr='' on a pull_request code run: pr-contract and budget-raise-gate never run",
              gate(B, []), "pass = GREEN WITH TWO REQUIRED JOBS NEVER RUN"))

R = run("pull_request", "edited", "code", "7", base="release", changes_base=True)
cases.append(("C retarget (edited + changes.base, kind=code) runs to completion",
              gate(R, [C1]), "FAIL: governance/hassfest/validate skipped by their action!='edited' guard"))

# D: retarget R queues behind an in-progress run (cancel-in-progress is false for
# action == 'edited'); a body edit V arrives; GitHub cancels pending R, V takes its place.
pend = pending_replace([R], "V")
V = run("pull_request", "edited", "verdict", "7", base="release")
cases.append(("D retarget R pending, then a body edit: R cancelled unstarted, V carries C1 (OLD base)",
              gate(V, [C1]), "pass = GREEN, no code unit ever ran against the new base"))

# E: push H2 while C0 (H1) runs: C2 cancels C0 but is PENDING until C0 stops; the
# body edit measured 0-4 s after the push (13 of 14 edits, ev/edit_after_push.txt)
# replaces pending C2. No code run exists at H2.
V2 = run("pull_request", "edited", "verdict", "7", base="main")
cases.append(("E synchronize C2 pending behind cancelling C0, edit 0-4 s later replaces it",
              gate(V2, []), "FAIL, and nothing re-queues a code run: stuck until a new push"))

for label, got, expect in cases:
    print(f"{label}\n    gate: {got}\n    expected by review: {expect}\n")
