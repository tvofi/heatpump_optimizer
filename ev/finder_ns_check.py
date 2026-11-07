# Reviewer harness: the PR's entity check verbatim (arms A) + reviewer probes (arms B).
import sys; sys.path.insert(0, sys.argv[1])
from datetime import datetime, UTC
import nightly_status as _nstatus
_NS_NOW = datetime(2026, 9, 10, 12, 0, tzinfo=UTC)
def _ns_run(rid, when, status="completed", conclusion="success"):
    return {"id": rid, "created_at": when, "status": status, "conclusion": conclusion,
            "head_sha": "0"*40, "html_url": f"https://example.invalid/{rid}"}
def _ns_job(name, conclusion): return {"name": name, "conclusion": conclusion, "html_url": ""}
_NS_LIVE = [_ns_job("nightly-ha (stable)", "success"), _ns_job("nightly-ha (2025.2.0)", "success"),
            _ns_job("slow", "success"), _ns_job("mutation-nightly", "success"),
            _ns_job("mutation-ledger", "success"), _ns_job("mutation-ledger-push", "success"),
            _ns_job("fast", "skipped")]
_ns_bad = _ns_run(21, "2026-09-10T02:17:00Z", conclusion="failure")
_ns_badjobs = [j if j["name"] != "slow" else _ns_job("slow", "failure") for j in _NS_LIVE]
_ns_newer = _ns_run(22, "2026-09-10T08:00:00Z", "in_progress", None)
_ns_older = _ns_run(20, "2026-09-09T08:00:00Z", "in_progress", None)
_ns_green = [_ns_job("slow", "success"), _ns_job("mutation-nightly", None)]
V = lambda *a, **k: _nstatus.verdict(*a, **k)[0]
A = {
 "superseded": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=_ns_green),
 "nothing newer": V(_ns_bad, None, _ns_badjobs, _NS_NOW),
 "newer slow failed": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=[_ns_job("slow", "failure")]),
 "newer slow pending": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=[_ns_job("slow", None)]),
 "in-flight older": V(_ns_bad, _ns_older, _ns_badjobs, _NS_NOW, in_flight_jobs=_ns_green),
}
EXP_A = {"superseded": "PASSED", "nothing newer": "FAILED", "newer slow failed": "FAILED",
         "newer slow pending": "FAILED", "in-flight older": "FAILED"}
two_bad = [j if j["name"] not in ("slow", "mutation-ledger") else _ns_job(j["name"], "failure") for j in _NS_LIVE]
same_ts = _ns_run(22, "2026-09-10T02:17:00Z", "in_progress", None)
B = {
 "B1 two failed, one superseded": V(_ns_bad, _ns_newer, two_bad, _NS_NOW, in_flight_jobs=_ns_green),
 "B2 newer slow skipped": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=[_ns_job("slow", "skipped")]),
 "B3 in-flight same created_at": V(_ns_bad, same_ts, _ns_badjobs, _NS_NOW, in_flight_jobs=_ns_green),
 "B4 run failed, no failing job": V(_ns_bad, _ns_newer, _NS_LIVE, _NS_NOW, in_flight_jobs=[_ns_job(j["name"], "success") for j in _NS_LIVE]),
 "B5 newer slow neutral": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=[_ns_job("slow", "neutral")]),
 "B6 empty in_flight_jobs": V(_ns_bad, _ns_newer, _ns_badjobs, _NS_NOW, in_flight_jobs=[]),
}
EXP_B = {k: "FAILED" for k in B}
a_ok = {k: str(v) for k, v in A.items()} == EXP_A
b_bad = {k: v for k, v in B.items() if str(v) != EXP_B[k]}
print("PR-CHECK", "PASS" if a_ok else "FAIL", {k: str(v) for k, v in A.items()})
print("PROBES", "PASS" if not b_bad else f"FAIL {b_bad}")
sys.exit(0 if a_ok else 1)
