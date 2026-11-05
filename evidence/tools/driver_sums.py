"""Reviewer's own harness (not the finder's): driver points vs grade - SCORE_REFERENCE."""
import random, sys
sys.path[:0] = ["tests/hastub", "."]
from custom_components.heatpump_optimizer import coordinator as C, driving_grade as D
rng = random.Random(3198)
worst_raw = worst_pub = 0.0; n = 0; empty_ok = True; pubs_off = 0
for trial in range(2000):
    drivers, grade = {}, None
    if rng.random() < 0.3:  # a grade folded before drivers were kept
        grade = rng.uniform(0, 100)
    for d in range(rng.randint(1, 30)):
        book = {"day": "x", "kwh": 0.0, "sek": 0.0, "spot_sum": 0.0, "spot_h": 0.0}
        for h in range(24):
            spot = rng.uniform(-0.2, 3.0); kwh = rng.uniform(0, 3)
            book = D.tally(book, kwh, kwh * spot, spot, 1.0)
        mean = book["spot_sum"] / book["spot_h"]
        if mean <= 0.01 or book["kwh"] < 0.2: continue
        grade = D.fold(drivers, grade, book, mean)
        pub = D.published(drivers, grade)
        worst_raw = max(worst_raw, abs(sum(p["points"] for p in pub) - (grade - C.SCORE_REFERENCE["operation"])))
        s = C.compose_scores((None, "x", []), (None, "y", []), (grade, None, pub))
        gap = abs(sum(p["points"] for p in s["operation_drivers"]) - (s["operation"] - C.SCORE_REFERENCE["operation"]))
        worst_pub = max(worst_pub, gap); pubs_off += gap > 0.05; n += 1
# machine
mw = 0.0
for k in range(500):
    stat = rng.uniform(0, 2 * C.COP_HEALTH_THRESHOLD)
    base = {(0, False): [3.0, C.COP_BASELINE_MIN_SAMPLES]}
    g, why, dr = C.machine_score(base, stat)
    mw = max(mw, abs(sum(p["points"] for p in dr) - (g - C.SCORE_REFERENCE["machine"])))
g, why, dr = C.machine_score({}, 0.0)
s = C.compose_scores((None, "a", []), (g, why, dr), (None, "b", D.published({"cheap_hours": 5.0}, None)), C.machine_evidence({}, 0))
empty_ok = s["machine_drivers"] == [] and s["operation_drivers"] == [] and s["envelope_drivers"] == [] and "machine_evidence" in s
print(f"RESULT operation_folds={n} raw_max_gap={worst_raw:.2e} published_max_gap={worst_pub:.3f} published_gaps_over_0.05={pubs_off}")
print(f"RESULT machine_max_gap={mw:.2e}")
print(f"RESULT empty_with_no_grade={empty_ok} reasons={s['reasons']}")
