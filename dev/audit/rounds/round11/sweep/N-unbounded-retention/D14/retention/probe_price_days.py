"""D14 sweep N-unbounded-retention: PriceShapeLearner.days_seen / quarter_days_seen.

Metric: keys PriceShapeLearner holds in memory (days_seen + quarter_days_seen)
after N simulated days of one long-lived learner folding each day's
15-minute prices once (what the coordinator does per price refresh, no
restart in between); slope per day between day 120 and day N. The learner's
own window is 90 days (store_payload keeps sorted(...)[-90:] of each, so a
bounded holder plateaus at 180 keys). Count key: len() of the production sets.
Arms:  baseline   | --perturb  (in-memory one-line trim after fold, the
                                payload's own [-90:] applied to memory -> slope 0)
       | --null    (the same learner restored from its own payload each day,
                    i.e. a restart per day: the store path bounds it -> slope 0)
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/retention/probe_price_days.py [--days 400] [--perturb|--null]
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import price_model as pm  # noqa: E402

args = sys.argv[1:]
DAYS = int(args[args.index("--days") + 1]) if "--days" in args else 400
learner = pm.PriceShapeLearner()
T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
series = []
for d in range(DAYS):
    day0 = T0 + timedelta(days=d)
    entries = [{"starts_at": (day0 + timedelta(minutes=15 * q)).isoformat(),
                "total": 0.5 + 0.3 * ((q // 4) % 24 in (7, 8, 17, 18, 19)) + 0.01 * (q % 4) + 0.001 * (d % 7)}
               for q in range(96)]
    learner.fold(entries)
    if "--perturb" in args:
        learner.days_seen = set(sorted(learner.days_seen)[-90:])
        learner.quarter_days_seen = set(sorted(learner.quarter_days_seen)[-90:])
    if "--null" in args:
        payload = learner.store_payload()
        learner = pm.PriceShapeLearner()
        learner.restore(payload)
    series.append(len(learner.days_seen) + len(learner.quarter_days_seen))
W = 120
slope = (series[-1] - series[W - 1]) / (DAYS - W)
print(f"# arm={'perturb' if '--perturb' in args else 'null' if '--null' in args else 'baseline'} days={DAYS}")
print(f"RESULT retained_keys_day{DAYS}={series[-1]} keys (window holds 180)")
print(f"RESULT retained_keys_slope={slope:.2f} keys/day")
print(f"RESULT payload_keys={len(learner.store_payload()['days_seen']) + len(learner.store_payload()['quarter_days_seen'])} keys")
