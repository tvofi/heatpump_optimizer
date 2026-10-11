import sys, random, itertools
sys.path.insert(0, "tests")
import importlib.util
spec = importlib.util.spec_from_file_location("closuremod", "tests/closure.py")
# closure.py may be huge; import as module without running main
m = importlib.util.module_from_spec(spec)
sys.modules["closuremod"] = m
spec.loader.exec_module(m)

names = ["tests/plan_view.py", "tests/card.mjs", "tests/card_drift.mjs",
         "tests/features.py", "tests/dst_checks.py", "tests/wood_advisor.py",
         "tests/doc_claims.py", "tests/layout.py", "tests/structure.py",
         "tests/golden.py", "tests/arch_score.py", "tests/env_drift.py"]

def edges_of(plan):
    bad = []
    flat = [s for ln in plan for s in ln]
    lanes = {s: i for i, ln in enumerate(plan) for s in ln}
    # PRODUCERS: plan_view before each card, same lane
    for cons in ("tests/card.mjs", "tests/card_drift.mjs"):
        if cons in flat:
            p = "tests/plan_view.py"
            if lanes.get(p) != lanes.get(cons) or flat.index(p) > flat.index(cons):
                bad.append(("PRODUCERS", p, cons, plan))
    c, d = "tests/dst_checks.py", "tests/features.py"
    if c in flat and d in flat:
        if lanes.get(c) != lanes.get(d) or flat.index(d) > flat.index(c):
            bad.append(("DRIVEN", d, c, plan))
    # coverage: every input exactly once
    if sorted(flat) != sorted(names):
        bad.append(("COVERAGE", sorted(flat), plan))
    return bad

random.seed(2131)
failures = []
tables = 0
# adversarial: extreme seconds; huge producer, tiny consumer; equal; zero; missing
for trial in range(4000):
    rec = {}
    for n in names:
        choice = random.random()
        if choice < 0.2: rec[n] = {"seconds": 0.0}
        elif choice < 0.4: rec[n] = {"seconds": 100000.0}
        elif choice < 0.5: rec[n] = 500.0  # non-dict legacy shape
        else: rec[n] = {"seconds": random.choice([0.001, 1, 5, 30, 60, 300, 1725])}
    tables += 1
    lanes = random.choice([1,2,3,4,5,9])
    order = list(names); random.shuffle(order)
    try:
        plan = m.lane_plan(order, rec, lanes)
    except ValueError as e:
        failures.append(("RAISED", str(e))); continue
    failures += edges_of(plan)
print(f"tables={tables} failures={len(failures)}")
for f in failures[:5]: print(f)

# worst-case handcrafted: producer 1e6s alone (would be LPT-first, alone), consumers 1s
rec = {n: {"seconds": 1.0} for n in names}
rec["tests/plan_view.py"] = {"seconds": 1_000_000.0}
rec["tests/features.py"] = {"seconds": 999_999.0}
plan = m.lane_plan(list(names), rec, 3)
print("handcrafted plan:", plan)
print("handcrafted failures:", edges_of(plan))
# group atomicity: card trio must be one lane
lanesof = {s: i for i, ln in enumerate(plan) for s in ln}
print("trio lanes:", {s: lanesof[s] for s in ("tests/plan_view.py","tests/card.mjs","tests/card_drift.mjs")})
