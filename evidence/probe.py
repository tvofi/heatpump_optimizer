import sys, math
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import duty_switch as m
t0 = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
def key(pub, k): return pub.get("duty_switch_dhw_space_" + k)
# P1 span_days under age alone (decay called by the pass, no observation)
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]
d.book(t0, True, 60.0)
seq = []
for day in range(0, 40):
    t = t0 + timedelta(days=day); d.decay(t); pub = L.published(t)
    seq.append((key(pub, "p"), key(pub, "n"), key(pub, "span_days")))
moves = [(i, a, b) for i, (a, b) in enumerate(zip(seq, seq[1:])) if a != b]
print("RESULT P1 age-alone moves (p,n,span_days) with decay() each day:", moves)
# P1b same with published() alone (no decay call)
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]; d.book(t0, True, 60.0)
seq = [tuple(key(L.published(t0 + timedelta(days=x)), k) for k in ("p", "n", "span_days")) for x in range(40)]
print("RESULT P1b reads only:", [(i, a, b) for i, (a, b) in enumerate(zip(seq, seq[1:])) if a != b])
# P2 upward steps of n: restamp jitter, 15-minute decay+read over 120 days after 40 mixed bookings
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]
for i in range(40): d.book(t0 + timedelta(hours=7 * i + i * i % 5), i % 3 != 0, 60.0)
t = t0 + timedelta(hours=300); prev = None; ups = 0; steps = 0; pmoves = 0; pprev = None
for i in range(96 * 120):
    t += timedelta(minutes=15); d.decay(t); pub = L.published(t); n = key(pub, "n"); p = key(pub, "p")
    if prev is not None and n != prev:
        steps += 1; ups += n > prev
        assert abs(n - prev) == 1.0, (n, prev)
    if pprev is not None and p != pprev: pmoves += 1
    prev, pprev = n, p
print(f"RESULT P2 restamped quarter-hour reads over 120 d: n steps={steps} upward={ups} p moves={pmoves} final n={prev}")
# P3 clock stepping back: n published can rise with no observation
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]
for i in range(6): d.book(t0, True, 60.0)
a = key(L.published(t0 + timedelta(days=5)), "n"); b = key(L.published(t0 - timedelta(days=1)), "n")
print("RESULT P3 read 5 d ahead then 1 d behind the stamp:", a, b)
# P4 published 5 <=> weight >= N_ON at the reading; and exact-integer weights
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]
for i in range(5): d.book(t0, True, 60.0)
print("RESULT P4 five at one instant:", key(L.published(t0), "n"), d.usable, "one second later:", key(L.published(t0 + timedelta(seconds=1)), "n"))
# P5 spread weight (body: five stops ten hours apart weigh under five)
d = m.Direction(); ws = []
for i in range(6):
    d.book(t0 + timedelta(hours=10 * i), True, 60.0); ws.append(round(d.n, 4))
print("RESULT P5 spread weights after each booking:", ws)
# P6 zero-evidence and void-only
L = m.DutySwitchLearner(); print("RESULT P6 empty learner:", L.published(t0))
L.directions["space_dhw"].void = 1; print("RESULT P6 void-only:", L.published(t0))
# P7 p for kept-only, and p where n floors to 0
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]; d.book(t0, False, None)
print("RESULT P7 kept-only:", L.published(t0)); d2 = L.directions["space_dhw"]; d2.book(t0, True, 30.0)
print("RESULT P7 one stop read 1 h later:", {k: v for k, v in L.published(t0 + timedelta(hours=1)).items() if "space_dhw" in k})
# P8 churn at the base resolution vs head, 96 reads over a day (body null control)
L = m.DutySwitchLearner(); d = L.directions["dhw_space"]
for i in range(6): d.book(t0 + timedelta(hours=i), True, 60.0)
reads = [t0 + timedelta(hours=6, minutes=15 * i) for i in range(96)]
pubs = [L.published(t) for t in reads]
print("RESULT P8 changes between consecutive reads over 96:", sum(a != b for a, b in zip(pubs, pubs[1:])), "keys:", sorted(pubs[0]))
