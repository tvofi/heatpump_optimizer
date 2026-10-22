import sys, inspect, datetime as dt
sys.path.insert(0, sys.argv[1] + "/tests")
import nightly_status as ns
UTC = dt.timezone.utc
made = dt.datetime(2026, 10, 22, 8, 5, 56, tzinfo=UTC)
wf = {"path": ".github/workflows/nightly.yml", "state": "active", "created_at": "2026-10-22T10:05:56+02:00"}
has_wf = "workflow" in inspect.signature(ns.verdict).parameters
def v(h, w):
    now = made + dt.timedelta(hours=h)
    r = ns.verdict(None, None, [], now, workflow=w) if has_wf else ns.verdict(None, None, [], now)
    txt = " | ".join(r[2])
    return r[0], r[1], ("inactivity" in txt), txt[:160]
for label, h, w in [("young-9h", 9, wf), ("edge-24.9h", 24.9, wf), ("edge-25.0h", 25.0, wf),
                    ("late-26h", 26, wf), ("late-72h", 72, wf),
                    ("disabled-9h", 9, {**wf, "state": "disabled_inactivity"}),
                    ("norecord-9h", 9, None)]:
    s, c, inact, t = v(h, w)
    print(f"RESULT {label} state={s} exit={c} inactivity_claim={inact} :: {t}")
