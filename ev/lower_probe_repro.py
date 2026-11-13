# Reviewer-built probe (not the finder's): one freeze is handed to every learner by
# learner_progress_view (coordinator.py:1776). The lower learner records its own probe's
# reason first (coordinator.py:5884 runs lower before house; 5930-5931 records it), and the
# house learner overwrites it only when the house itself is frozen (5775-5776).
from custom_components.heatpump_optimizer import learner_progress as lp
house = lp.LearnerInputs(True, 5, lambda n: n >= 50, None, None, 2.0)  # counting, folding samples
plain = lp.learner_progress(house)
for reason in ["stale:lower_floor_temp_entity", "unavailable:lower_floor_temp_entity",
               "stale:dhw_temp_entity",  # null control: the body's excluded probe
               "stale:indoor_temp_entity"]:  # a probe the house learner does freeze on
    got = lp.learner_progress(house, (reason, None))
    print(f"RESULT house learner, recorded reason {reason!r}: phase {plain['phase']} -> {got['phase']}")
