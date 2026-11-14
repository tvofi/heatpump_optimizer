"""Invariant over census_head.txt: every raised row reads below < target <= above <= min(max, 70), above-below == step, written < target - margin."""
import ast, sys
bad = n = 0
for line in open(sys.argv[1]):
    lo, hi, step, ev, d, hold, rest = line.split(" ", 6)
    rest = rest.strip()
    if rest == "None":
        continue
    n += 1
    p = dict(ast.literal_eval(rest)); lo, hi, step, d = map(float, (lo, hi, step, d))
    b, a, w = float(p["below"]), float(p["above"]), float(p["written"])
    m = 0.5 if hold == "True" else 1.0
    if not (b < d <= a <= min(hi, 70) and abs(a - b - step) < 1e-9 and w < d - m):
        bad += 1; print("BAD", line.strip())
print(f"CENSUS-CHECK raised={n} bad={bad}")
