import sys; sys.path.insert(0, sys.argv[1])
from datetime import datetime, timezone, timedelta
import review_strength as rs
t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
for k in (3, 4, 5):
    vs = [dict(pr=i, t=t0 + timedelta(hours=i), real=i < k, kind="blocked" if i < k else "merge") for i in range(30)]
    print(f"k={k}:", rs.guardrail(vs, t0 + timedelta(days=5), 30, 0.28))
