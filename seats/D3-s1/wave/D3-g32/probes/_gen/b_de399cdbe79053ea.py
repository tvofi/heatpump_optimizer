import numpy as np
from custom_components.heatpump_optimizer import sysid

mut = mutate(sysid.SystemIdentification, "_over_excursion",
             "            and abs(room_temp - base) > self.config.max_excursion_c",
             "            and abs(room_temp - base) >= self.config.max_excursion_c")
s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
lim = s.config.max_excursion_c
ties = moved = 0
# sensor-resolution readings: baselines 15.0..25.0 in 0.1 steps, rooms at baseline +- the bound, rounded to 0.1
for i in range(150, 251):
    base = i / 10.0
    s._baseline_temp = base
    for room in (round(base + lim, 1), round(base - lim, 1)):
        if abs(room - base) == lim:
            ties += 1
        moved += sysid.SystemIdentification._over_excursion(s, room) != mut(s, room)
print(f"RESULT readings_scanned=202 count")
print(f"RESULT exact_float_ties={ties} count")
print(f"RESULT readings_moved={moved} count  (baseline False -> mutant True: the experiment aborts)")
s._baseline_temp = 0.2
print(f"RESULT tie_base0.2_room1.0_baseline={sysid.SystemIdentification._over_excursion(s, 1.0)} mutant={mut(s, 1.0)}")
# null control: an excursion clearly inside / outside the bound
s._baseline_temp = 20.0
print(f"RESULT null_delta={sum(sysid.SystemIdentification._over_excursion(s, r) != mut(s, r) for r in (20.3, 19.5, 21.5, 18.0))} count")
# exact ties need |room|,|base| < 1 C (0.8 is not a multiple of ulp(x) for x >= 1): a random scan of indoor floats
import random
rng = random.Random(11)
ties = 0
for _ in range(200000):
    base = rng.uniform(5.0, 30.0)
    s._baseline_temp = base
    room = base + rng.choice((-lim, lim))
    for r in (room, float(np.nextafter(room, 0)), float(np.nextafter(room, 99))):
        ties += sysid.SystemIdentification._over_excursion(s, r) != mut(s, r)
print(f"RESULT random_indoor_moved={ties} count  (600000 readings, base uniform in [5, 30] C, room base+-0.8 and both float neighbours)")
tail()
