import json, sys, re, subprocess
sys.path.insert(0, "tools/audit/seat")
import plan_page as P
W = sys.argv[1]
plan = json.load(open(f"{W}/plan.json"))
gen = plan["generated"]
roster = json.load(open(f"{W}/roster.json"))
iss = sorted({n for g in P.roster_lib.groups_of(roster).values() if P.roster_lib.is_open(g) for n in (g.get("issues") or [])})
print("RESULT roster_open_group_issues=", len(iss))
def run(name, snap):
    try:
        s = P.issues_section(roster, plan, snap)
    except Exception as e:
        print(f"RESULT case={name} error={type(e).__name__}:{e}"); return
    pts = re.search(r'<polyline points="([^"]+)"', s)
    ys = sorted({p.split(',')[1] for p in pts.group(1).split()}) if pts else None
    print(f"RESULT case={name} polyline={'yes' if pts else 'no'} distinct_y={len(ys) if ys else 0} open_now={re.findall(r'(\\d+) open now', s)} note={re.findall(r'class=\"note\">([^<]*)', s)[0][:160]!r}")
run("empty-issue-set", {"issues": [], "open_prs": [], "merged_prs": []})
run("all-closed", {"issues": [{"number": n, "state": "CLOSED"} for n in iss], "open_prs": [], "merged_prs": []})
run("all-open", {"issues": [{"number": n, "state": "OPEN"} for n in iss] + [{"number": 201, "state": "OPEN"}], "open_prs": [], "merged_prs": []})
# flat: every carrier unplanned
p2 = json.loads(json.dumps(plan))
for g in p2["groups"].values(): g["finish"] = None
plan_bak, plan = plan, p2
run("all-unplanned-flat", {"issues": [{"number": n, "state": "OPEN"} for n in iss], "open_prs": [], "merged_prs": []})
plan = plan_bak
run("offline", {"issues": [], "open_prs": [], "merged_prs": [], "offline": True})
