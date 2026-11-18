"""Revision 3's objective block, derived (decision 0018; plan_audit.py's OBJECTIVE_KEYS).

Run from the repository root at the plan branch:
  python3 -I dev/audit/rounds/round11/PLAN/build_objective.py --start <UTC> [--plan-a <replan A json>]
It rewrites PLAN.json's `objective` block and adds a `groups` row for every
open group of the draft roster the seam plan did not carry. Ranks are derived
by plan_audit.derived_rank's rule from the keys written here; nothing is typed.
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ROSTER = "dev/audit/rounds/round11/PLAN/wave-r11-groups.json"
VERIFIED = ("verified", "weakened")
CLOSED = {"done", "rca-done", "absorbed", "refused", "deferred"}
# Open cards a roster group builds (EVALUATION.json's cards, round 11).
CARDS = {"R11-INTAKE-R10-RESIDUE": ["E11-N-INTAKE-BUILDER"]}
# The dimension whose close pass examines a rank-2 group's merged diff.
PASS = {"R11-ARCH-cycle-surface": "D7", "R11-ARCH-fabric-learner": "D7",
        "R11-CARRY-DRAWMAP": "D2", "R11-CARRY-ROOM-LIFT": "D16",
        "R11-CLOSEOUT-CLEANUP": "D11", "R11-OUTSIDE-HONEST-DHW-RUNS": "D16",
        "R11-OUTSIDE-ROOMS-P3": "D17", "R11-OUTSIDE-SELF-SETTING-PUMP": "D16",
        "R11-PRE-HANDOFF-BOOKKEEPING": "D11", "R11-PRE-SECURITY-PRIVACY": "D11",
        "R11-PRE-SHARED-FILES": "D11", "R11-PRE-TOKEN-LEDGER": "D13",
        "R11-PREPR-STEP-TIMING": "D11", "R11-PRODUCT-TEXT-PINS": "D6",
        "R11-SEAM-comments-production": "D5", "R11-SEAM-comments-tests": "D5",
        "R11-SEAM-dead-state": "D7", "R11-SEAM-docs": "D6",
        "R11-SEAM-governance-text": "D11", "R11-SEAM-kernel-layering": "D7",
        "R11-SEAM-ratchet-raise": "D7"}
TERMS = {
    "first_pass": {"direction": "hold", "basis":
                   "the one term read in the baseline; this plan changes no review rule or "
                   "contract clause, and section 5 lets first_pass rank nothing while injected "
                   "and escapes are NO-READ"},
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    args = ap.parse_args()
    plan = json.loads((HERE / "PLAN.json").read_text())
    roster = json.loads((ROOT / ROSTER).read_text())
    judge = json.loads((ROOT / "dev/audit/rounds/round11/JUDGE.json").read_text())["verdicts"]
    baseline = json.loads((ROOT / "dev/audit/yardstick/round10/OBJECTIVE.json").read_text())
    terms = json.loads((ROOT / "dev/audit/config/objective.json").read_text())["terms"]
    classes = {k for k in json.loads((ROOT / "dev/audit/config/bugclasses.json").read_text())
               if not k.startswith("_")}
    bug = {f["id"]: f for f in judge
           if f["verdict"] in VERIFIED and f["stop_rule_class"] == "bug"}
    known = {f["id"] for f in judge}
    planned = {g["group"]: g for g in plan["groups"]}
    is_open = lambda g: (g.get("resume") or {}).get("stage") not in CLOSED
    by_name = {g["group"]: g for g in roster["groups"]}
    # A group every open dependency of which is deferred is held, and replan.py marks it done.
    held = {n for n, g in by_name.items() if is_open(g) and any(
        (by_name[a].get("resume") or {}).get("stage") == "deferred" for a in g.get("after") or [])}
    open_names = [g["group"] for g in roster["groups"] if is_open(g) and g["group"] not in held]
    plan["groups"] = [g for g in plan["groups"] if g["group"] in open_names]
    for name in open_names:
        if name not in planned:
            g = by_name[name]
            plan["groups"].append({
                "group": name, "findings": [], "size": g.get("size"),
                "seam": g.get("seam") or g.get("kind"), "after": g.get("after") or [],
                "origin": "roster", "stage": (g.get("resume") or {}).get("stage"),
                "architect_note": "Carried from the roster at the pin, not cut by this plan: "
                                  "ranked and projected here, its brief and edges stay the roster's."})
    groups = {}
    for g in plan["groups"]:
        name = g["group"]
        removes = [f for f in g.get("findings") or [] if f in known]
        entry = {}
        if removes:
            entry["removes"] = removes
        keyed = sorted({bug[f]["class"] for f in removes if f in bug and bug[f].get("class") in classes})
        if keyed:
            entry["classes"] = keyed
        if CARDS.get(name):
            entry["cards"] = CARDS[name]
        rank1 = any(f in bug for f in removes) or bool(entry.get("classes") or entry.get("cards"))
        entry["rank"] = 1 if rank1 else 2
        if not rank1:
            entry["examined_by"] = (f"round-11 close pass of {PASS[name]}: a finder pass over the "
                                    f"group's merged diff before the closeout stamp, reporting its "
                                    f"universe and denominator")
        groups[name] = entry
    stated = {}
    for term in terms:
        if term in TERMS:
            stated[term] = TERMS[term]
        else:
            unread = baseline["terms"][term]
            assert "value" not in unread, term
            stated[term] = {"direction": "undecided", "builder": unread["builder"]}
    blob = lambda path: subprocess.run(["git", "-C", str(ROOT), "hash-object", path],
                                       capture_output=True, text=True, check=True).stdout.strip()
    old = plan.get("objective") or {}
    plan["objective"] = {
        "baseline": {"record": "dev/audit/yardstick/round10/OBJECTIVE.json"},
        "pin": {"roster_path": ROSTER, "roster_blob": blob(ROSTER), "start": args.start,
                "durations_blob": blob("tools/plan/durations.json")},
        "terms": stated, "groups": groups,
        "edges": old.get("edges") or [], "dispositions": old.get("dispositions") or {},
    }
    (HERE / "PLAN.json").write_text(json.dumps(plan, indent=1) + "\n")
    r1 = sorted(g for g, e in groups.items() if e["rank"] == 1)
    print(f"objective block: {len(groups)} group(s), rank 1 {len(r1)}, rank 2 {len(groups) - len(r1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
