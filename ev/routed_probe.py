# Reviewer-built companion: the same four reasons, routed as the tree routes them (HELD_BY).
from custom_components.heatpump_optimizer import learner_progress as lp
house = lp.LearnerInputs(True, 5, lambda n: n >= 50, None, None, 2.0)
for reason in ["stale:lower_floor_temp_entity", "stale:dhw_temp_entity", "stale:indoor_temp_entity"]:
    rec = {"lower": (reason, None)} if "lower" in reason else {"dhw": (reason, None)} if "dhw" in reason else {"house": (reason, None), "lower": (reason, None)}
    for card in ("house", "solar", "gains", "lower"):
        got = lp.learner_progress(house, rec.get(lp.HELD_BY[card]))
        print(f"RESULT routed {reason!r} card {card}: {got['phase']}")
