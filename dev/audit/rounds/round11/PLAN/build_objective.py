"""Revision 4's objective block, derived (decision 0018; plan_audit.py's OBJECTIVE_KEYS).

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
CARDS = {"R11-READS-RESIDUE": ["E11-N-INTAKE-BUILDER"]}
# Revision 4: the intake group's triage (INTAKE-TRIAGE.json beside this file).
INTAKE = "R11-INTAKE-R10-RESIDUE"
READS = "R11-READS-RESIDUE"
READS_TEMPLATE = "R11-PREPR-STEP-TIMING"   # an S instrument row, for the roster's field set
# Stages the roster lags its refs on, each with the ref that shows it.
LIVE = {"R11-SEAM-cycle-solve": ("in-progress", 3738)}
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
# The roster commit the draft is cut from, and revision 3's order changes to it.
ROSTER_REF = "c7e683a6d469fd050096f284399308b087474a52"
ROSTER_SRC = "dev/programme/rosters/wave-r11-groups.json"
BEHAVIOUR = "R11-SEAM-product-text"   # comments follow the seams product text follows (ADR-010)
ADD_AFTER = {"R11-SEAM-dead-state": ["R11-SEAM-store"],
             # Revision 4: the first-wave slot goes to the rank-1 reads, not to rank-2 text pins.
             "R11-PRODUCT-TEXT-PINS": ["R11-READS-RESIDUE"]}
# Verified `bug` findings deferred to round 12: the owner card that rules the deferral.
FREEZE_CARD = "P11"
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
    roster = json.loads(subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{ROSTER_REF}:{ROSTER_SRC}"],
        capture_output=True, text=True, check=True).stdout)
    rows = {g["group"]: g for g in roster["groups"]}
    rows["R11-SEAM-comments-production"]["after"] = list(rows[BEHAVIOUR]["after"])
    for name, more in ADD_AFTER.items():
        rows[name]["after"] = list(rows[name].get("after") or []) + more
    triage = json.loads((HERE / "INTAKE-TRIAGE.json").read_text())["carries"]
    intake = rows[INTAKE]
    kept = [intake["carry"][t["carry"]] for t in triage if t["into"] == READS]
    assert len(kept) == 2, kept
    # The intake group keeps only the carries deferred to round 12 with no deferred owner.
    intake["resume"] = dict(intake["resume"], stage="deferred",
                            next_step="round 12 architect triage of the carries INTAKE-TRIAGE.json leaves here",
                            note="plan revision 4: triaged (INTAKE-TRIAGE.md); deferred to round 12, "
                                 "holding no in-round work")
    if READS not in rows:
        new = json.loads(json.dumps(rows[READS_TEMPLATE]))
        new.update({
            "group": READS, "after": [], "issues": [], "fixes": [], "carry": kept,
            "files": ["tools/audit/product_reads.py", "tools/audit/seat/plant_recall.py",
                      "dev/audit/rounds/round11/product-reads/operation.tsv"],
            "hot_files": [], "findings": [],
            "architect_note": "Cut by plan revision 4 from the intake group's two carries on the "
                              "product reads (card E11-N-INTAKE-BUILDER): the population levels of "
                              "both axes and the operation seed ledger re-cut to per-state cells.",
            "brief": "Round 11. Finish the product reads decision 0018's terms are first read from "
                     "at this round's close: the two carries below. Re-measure each at your own "
                     "merge base.",
            "resume": dict(new["resume"], stage="not-started", branch="handoff/r11-reads-residue",
                           commit=None, last_step=None, pr=None, note="cut by plan revision 4",
                           next_step="dispatch the fixer"),
        })
        # At the intake group's place: replan.py hands slots out in roster order.
        roster["groups"].insert(roster["groups"].index(intake) + 1, new)
        rows[READS] = new
    for name, (stage, pr) in LIVE.items():
        rows[name]["resume"] = dict(rows[name]["resume"], stage=stage, pr=pr)
    (ROOT / ROSTER).write_text(json.dumps(roster, indent=1) + "\n")
    judge = json.loads((ROOT / "dev/audit/rounds/round11/JUDGE.json").read_text())["verdicts"]
    baseline = json.loads((ROOT / "dev/audit/yardstick/round10/OBJECTIVE.json").read_text())
    terms = json.loads((ROOT / "dev/audit/config/objective.json").read_text())["terms"]
    classes = {k for k in json.loads((ROOT / "dev/audit/config/bugclasses.json").read_text())
               if not k.startswith("_")}
    bug = {f["id"]: f for f in judge
           if f["verdict"] in VERIFIED and f["stop_rule_class"] == "bug"}
    known = {f["id"] for f in judge}
    planned = {g["group"]: g for g in plan["groups"]}
    for row in plan["triage"]:
        if row["id"] in bug and row["verdict"] == "defer":
            row["card"] = FREEZE_CARD
    for g in plan["groups"]:
        if g["group"] in rows and g.get("origin") != "roster":
            g["after"] = list(rows[g["group"]].get("after") or [])
    plan["revision"] = 4
    plan["draft"] = ROSTER
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
