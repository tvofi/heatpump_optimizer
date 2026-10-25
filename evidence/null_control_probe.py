# Reviewer's own null-control probe (not the finder's harness): calls plan_page.issues_section directly.
import re, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import plan_page as pp
roster = {"groups": [
    {"group": "A", "issues": [1, 2], "resume": {"stage": "fix"}},
    {"group": "B", "issues": [2, 3], "resume": {"stage": "fix"}}]}
plan = {"generated": {"start": "2026-01-01T00:00:00Z"}, "summary": {"closure": "2026-01-05T00:00:00Z"},
        "groups": {"A": {"finish": "2026-01-02T00:00:00Z"}, "B": {"finish": "2026-01-04T00:00:00Z"}}}
unpl = {**plan, "groups": {"A": {"finish": None}, "B": {"finish": None}}}
def ys(html):
    m = re.search(r'<polyline[^>]*points="([^"]*)"', html)
    return None if not m else sorted({p.split(",")[1] for p in m.group(1).split()})
def snap(states): return {"issues": [{"number": n, "state": s} for n, s in states]}
cases = {
  "empty-issue-set": (plan, snap([])),
  "all-closed": (plan, snap([(1, "CLOSED"), (2, "CLOSED"), (3, "CLOSED")])),
  "every-carrier-unplanned": (unpl, snap([(1, "OPEN"), (2, "OPEN"), (3, "OPEN")])),
  "all-open-planned": (plan, snap([(1, "OPEN"), (2, "OPEN"), (3, "OPEN"), (201, "OPEN")])),
}
for name, (p, s) in cases.items():
    h = pp.issues_section(roster, p, s)
    print(f"RESULT case={name} distinct_y={len(ys(h)) if ys(h) else 0} polyline={ys(h) is not None}")
print("RESULT proj(all-open-planned)", pp.project_issues(roster, plan, {1, 2, 3, 201}))
h = pp.issues_section(roster, plan, {"offline": True})
print(f"RESULT case=offline polyline={ys(h) is not None} omitted={'Omitted' in h}")
