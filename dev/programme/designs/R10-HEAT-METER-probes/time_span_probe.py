"""Design R10-HEAT-METER revision 2, point A: a time-closed span against the learner's strict bound.

Home Assistant schedules the next refresh after the previous one ends
(update_coordinator.py:276 in venv-ha), so the cadence is interval + solve time.
Solve times: 2.5 s is the largest measured solve_cpu_ms in the tree
(dev/audit/rounds/round10/catchup/d9/out/cont_fuse.txt, winter_two_zone_no_dhw,
x86); 25 s is that x10 as a Pi-class allowance; 120 s is a stress row.
Event-driven refreshes (an options save, a service call) land at random times
with probability EVENT per cycle; such a refresh resets HA's schedule.
Rule: close at the first read with elapsed >= MAX - interval_h - allowance;
refuse (and re-baseline) a span whose elapsed exceeds MAX. MAX and MIN are the
learner's own HOUSE_LOSS_MAX/MIN_SAMPLE_HOURS; its check is strict (dt_h > MAX).
Null: a cycle-count close (K = 3) at solve > 0 is refused every time."""
import random
MAX, MIN, INTERVAL = 1.5, 0.15, 0.5
def run(solve_s, event, allowance_h, rule, spans=20000, seed=7):
    rnd = random.Random(seed); ok = ref = 0; t = 0.0; start = 0.0; n = 0; dts = []
    while ok + ref < spans:
        gap = INTERVAL + solve_s / 3600.0
        if rnd.random() < event:
            gap = rnd.uniform(0.0, gap)          # an event-driven refresh, then HA re-schedules
        t += gap; n += 1; el = t - start
        close = (n >= 3) if rule == "cycles" else (el >= MAX - INTERVAL - allowance_h)
        if close:
            if MIN <= el <= MAX: ok += 1; dts.append(el)
            else: ref += 1
            start = t; n = 0
    return ok, ref, (min(dts), max(dts)) if dts else None
for solve in (2.5, 25.0, 120.0):
    for event in (0.0, 0.05):
        for rule, allow in (("cycles", 0.0), ("time", 0.0), ("time", 0.05)):
            ok, ref, rng = run(solve, event, allow, rule)
            r = f"dt_h {rng[0]:.3f}-{rng[1]:.3f}" if rng else "no span"
            print(f"solve {solve:5.1f} s event {event:.2f} rule {rule:6s} allowance {allow:.2f} h: accepted {ok}, refused {ref} ({r})")
