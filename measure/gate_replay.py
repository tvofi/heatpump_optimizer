"""The gate's null control, replayed over measured heads, plus its perturbations.

    python3 -I measure/gate_replay.py measure/raw > measure/gate_replay.txt

For each saved head (raw/checks_<sha>.json = GET commits/<sha>/check-runs):
  RULESET  = today's verdict: each of ruleset 23698884's 17 contexts has a newest
             check run (budget-raise-gate: app 15368 only) that completed
             success/skipped/neutral.
  GATE     = the proposed gate over the same check runs: each required job's
             newest run concluded success, or skipped AND the skip is a declared
             scope decision. Anything else (absent, pending, skipped by no
             decision, failure, cancelled, timed_out) fails.
Exit 0 only when GATE == RULESET on every head where no required job was skipped
(the only place the two may differ, by design), and every perturbation below
moves the gate the way the design says.
"""
import copy, json, sys
from pathlib import Path

CONTEXTS = ["fast (3.14)", "browser", "briefs", "closure-scope", "closures", "typing",
            "hassfest", "validate-hacs", "policy-docs", "wave-script", "pr-contract",
            "env-matrix", "Analyze (actions)", "Analyze (javascript-typescript)",
            "Analyze (python)", "mutation", "budget-raise-gate"]
SCOPE_SKIPPABLE = {"browser"}  # the only required job a scope output skips at job level
GREEN = {"success", "skipped", "neutral"}

def newest(runs, name):
    c = [r for r in runs if r["name"] == name and (name != "budget-raise-gate" or r["app"]["id"] == 15368)]
    return max(c, key=lambda r: (r.get("started_at") or "", r["id"])) if c else None

def ruleset(runs):
    bad = []
    for n in CONTEXTS:
        r = newest(runs, n)
        if r is None: bad.append(f"{n}=ABSENT")
        elif r["status"] != "completed" or r["conclusion"] not in GREEN: bad.append(f"{n}={r['conclusion'] or r['status']}")
    return bad

def gate(runs, declared_scope_skips):
    bad = []
    for n in CONTEXTS:
        r = newest(runs, n)
        if r is None: bad.append(f"{n}=ABSENT")
        elif r["status"] != "completed": bad.append(f"{n}=PENDING")
        elif r["conclusion"] == "success": pass
        elif r["conclusion"] == "skipped":
            if n not in declared_scope_skips: bad.append(f"{n}=SKIPPED-UNDECLARED")
        else: bad.append(f"{n}={r['conclusion']}")
    return bad

def declared(runs):
    # replay proxy for the prelude's declaration: browser skipped while closure-scope succeeded
    cs = newest(runs, "closure-scope"); b = newest(runs, "browser")
    return {"browser"} if b and b["conclusion"] == "skipped" and cs and cs["conclusion"] == "success" else set()

raw = Path(sys.argv[1]); rc = 0; heads = sorted(raw.glob("checks_*.json"))
agree = differ_by_skip = 0
print(f"{'head':10s} {'RULESET':8s} {'GATE':8s} rows  reasons")
sample_green = None
for f in heads:
    runs = json.loads(f.read_text())["check_runs"]
    a, g = ruleset(runs), gate(runs, declared(runs))
    skips = [n for n in CONTEXTS if (r := newest(runs, n)) and r["conclusion"] == "skipped"]
    same = (not a) == (not g)
    agree += same
    if not same and skips: differ_by_skip += 1
    elif not same: rc = 1
    if not a and not g and sample_green is None: sample_green = runs
    print(f"{f.stem[7:17]:10s} {'pass' if not a else 'FAIL':8s} {'pass' if not g else 'FAIL':8s} {len(runs):4d}  "
          f"{'; '.join(sorted(set(a) | set(g)))[:150]}{'  skipped:' + ','.join(skips) if skips else ''}")
print(f"\nheads {len(heads)}: agree {agree}, differ only where a required job was skipped {differ_by_skip}")

print("\n## perturbations of one green head (each must print the expected verdicts)")
def perturb(label, fn, want_rs, want_g, decl=frozenset()):
    global rc
    runs = copy.deepcopy(sample_green); fn(runs)
    a, g = ruleset(runs), gate(runs, set(decl))
    got = ("pass" if not a else "FAIL", "pass" if not g else "FAIL")
    ok = got == (want_rs, want_g); rc |= not ok
    print(f"  {'ok ' if ok else 'BAD'} {label:58s} ruleset {got[0]:4s} gate {got[1]:4s}  {'; '.join(g)}")
def setc(name, concl):
    def f(runs):
        for r in runs:
            if r["name"] == name: r["conclusion"] = concl
    return f
def drop(name):
    def f(runs): runs[:] = [r for r in runs if r["name"] != name]
    return f
def pend(name):
    def f(runs):
        for r in runs:
            if r["name"] == name: r["status"], r["conclusion"] = "in_progress", None
    return f
if sample_green is None:
    print("  no green head saved; perturbations not run"); rc = 1
else:
    perturb("null: unchanged green head", lambda r: None, "pass", "pass")
    perturb("required job absent (closures)", drop("closures"), "FAIL", "FAIL")
    perturb("required job pending (fast (3.14))", pend("fast (3.14)"), "FAIL", "FAIL")
    perturb("required job failed (mutation)", setc("mutation", "failure"), "FAIL", "FAIL")
    perturb("required job cancelled (typing)", setc("typing", "cancelled"), "FAIL", "FAIL")
    perturb("required job SKIPPED, no scope decision (fast (3.14))", setc("fast (3.14)", "skipped"), "pass", "FAIL")
    perturb("required job skipped BY the scope decision (browser)", setc("browser", "skipped"), "pass", "pass", {"browser"})
    perturb("browser skipped, prelude declared no skip", setc("browser", "skipped"), "pass", "FAIL")
    perturb("non-required red (delivery-status)", setc("delivery-status", "failure"), "pass", "pass")
    perturb("non-required red (nightly-status)", setc("nightly-status", "failure"), "pass", "pass")
print(f"\nGATE-REPLAY rc {rc}")
sys.exit(rc)
