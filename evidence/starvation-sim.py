import sys, random
sys.path.insert(0, "tools/pr")
import cancel_superseded as cs
def sim(n, lag, seed):
    rnd = random.Random(seed)
    runs = [{"id": 1, "head_branch": "main", "event": "push", "status": "completed", "conclusion": "success"}]
    pending_cancel = []  # (due_step, id)
    for step in range(2, n + 2):
        runs.append({"id": step, "head_branch": "main", "event": "push", "status": "in_progress", "conclusion": None})
        for d, rid in [p for p in pending_cancel if p[0] <= step]:
            r = next(r for r in runs if r["id"] == rid); r.update(status="completed", conclusion="cancelled")
        pending_cancel = [p for p in pending_cancel if p[0] > step]
        p = cs.main_plan(runs)
        for rid in p["cancel"]:
            pending_cancel.append((step + rnd.randint(0, lag), rid))
    for d, rid in pending_cancel:
        next(r for r in runs if r["id"] == rid).update(status="completed", conclusion="cancelled")
    st = [("C" if r["conclusion"] == "cancelled" else "K") for r in runs[1:]]
    row = mx = 0
    for s in st[:-1]:
        row = row + 1 if s == "C" else 0; mx = max(mx, row)
    return "".join(st), mx
worst = 0
for lag in (0, 1, 3):
    for seed in range(50):
        s, mx = sim(40, lag, seed); worst = max(worst, mx)
        if seed == 0: print(f"lag={lag} {s} longest-cancelled-row={mx}")
print("worst longest row of cancelled runs over 150 sims:", worst, "(bound MAIN_ROW_MAX =", cs.MAIN_ROW_MAX, ")")
