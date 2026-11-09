"""Reviewer's own probe (not the finder's): does `open_ = open_ - set(held)` change
a plan? Held groups compete for slots under slots=1. Also the gates() conjunct
of held_behind_deferred: P deferred, R refuted after P, D after R."""
import sys, json, datetime as dt, pathlib
root = pathlib.Path(sys.argv[1]); sys.path[:0] = [str(root / "tools/plan"), str(root / "tools/audit/seat")]
import replan, roster_lib
durations = {"sizes_hours": {"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0}, "live_remaining_fraction": 0.7,
 "batch_window_minutes": 20, "stamp_lead_minutes": 60, "closure_lead_minutes": 120,
 "ci": {"fast (3.14)": {"median_minutes": 50.0}, "closures": {"median_minutes": 22.0},
        "Analyze (python)": {"median_minutes": 27.0, "cancelled_rate": 0.04}}, "provenance": {}}
durations.update(first_round_hours=dict(durations["sizes_hours"]), review_rounds={k: 1.0 for k in durations["sizes_hours"]},
                 round_hours=0.0, carry_part_hours=1.0, carries_per_part=1.0)
def fx(n, size="S", stage="not-started", after=()):
    return {"group": n, "size": size, "lane": "Core model", "kind": "defect", "after": list(after), "resume": {"stage": stage}}
start = dt.datetime(2026, 1, 5)
for slots in (1, 6):
    caps = dict(replan.DEFAULT_CAPS, slots=slots, seats=8)
    p = replan.build_plan({"groups": [fx("R10-P", stage="deferred"), fx("R10-Q", "XL", after=["R10-P"]), fx("R10-U", "S")]},
                          durations, caps, start, "v1.0.0", round_n=2)
    print(f"RESULT probe slots={slots}:", {n: (g["start"], g.get("held_behind")) for n, g in p["groups"].items()}, "check:", replan.check_plan(p))
G = roster_lib.groups_of({"groups": [fx("P", stage="deferred"), fx("R", stage="refuted", after=["P"]), fx("D", after=["R"])]})
print("RESULT probe held_behind_deferred(P deferred, R refuted after P, D after R):", roster_lib.held_behind_deferred(G))
