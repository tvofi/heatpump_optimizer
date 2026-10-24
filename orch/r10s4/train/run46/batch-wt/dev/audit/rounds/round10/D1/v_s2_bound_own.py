"""Verifier V2 for D1-s2-01. Metric: leaves rewritten by store._bound_instants on a
payload holding 5 lead_pending dues at now+{1,3,6,12,24}h, under the snapshot
store's bound (lead=0) vs the accuracy store's (lead=max(LEAD_BUCKETS)).
Command: PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round10/D1/v_s2_bound_own.py"""
import logging; logging.basicConfig(level=logging.WARNING)
from datetime import timedelta
from homeassistant.util import dt as dt_util
from heatpump_optimizer import store
from heatpump_optimizer.accuracy import LEAD_BUCKETS
now = dt_util.as_utc(dt_util.now())
pl = {"snapshots": [{"learners": {"accuracy": {"lead_pending": [[(now + timedelta(hours=h)).isoformat(), 1.0] for h in (1, 3, 6, 12, 24)]}}}]}
for name, lead in (("snapshot_lead0", timedelta(0)), ("accuracy_lead", timedelta(hours=max(LEAD_BUCKETS)))):
    hits = []; store._bound_instants(pl, now + lead, name, None, hits)
    print(f"RESULT {name}_rewritten={len(hits)} of 5")
