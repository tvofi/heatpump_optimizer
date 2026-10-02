import sys; sys.path.insert(0, "tests")
from datetime import datetime, UTC
import nightly_status as _nstatus
class _R:
    def check(self, name, ok, detail=""):
        print("RESULT", "ok" if ok else "FAIL", detail); self.ok = ok
R = _R()
def _ns_run(rid: int, when: str, status: str = "completed",
            conclusion: str | None = "success") -> dict:
    # The default is the ORDINARY nightly: a run that concluded `success`. It
    # was `failure` until the review of this pull request, and that is not a
    # detail -- under the classifier as first written, `verdict` never read the
    # run's own conclusion at all, so every fixture below was silently a run
    # that had FAILED and every one of them still read PASSED. The fixture
    # encoded the defect, which is why no check here caught it. Each case now
    # varies ONE property and leaves the rest ordinary.
    return {"id": rid, "created_at": when, "status": status,
            "conclusion": conclusion, "head_sha": "0" * 40,
            "html_url": f"https://example.invalid/{rid}"}


def _ns_job(name: str, conclusion: str | None) -> dict:
    return {"name": name, "conclusion": conclusion, "html_url": ""}


# Every lane in REQUIRED_LANES has to appear here, or the ordinary nightly
# reads ABSENT and all four states collapse -- which is how adding
# `mutation-nightly` to the reporter announced itself, four checks at once.
# `fast` is skipped on a schedule by design and is in the fixture for that.
_NS_LIVE = [_ns_job("nightly-ha (stable)", "success"),
            _ns_job("nightly-ha (2025.2.0)", "success"),
            _ns_job("slow", "success"),
            _ns_job("mutation-nightly", "success"),
            _ns_job("fast", "skipped")]
# --- one stale listing is not an absent nightly (2026-10-01) ----------------
#
# One run of `nightly-status` read the newest scheduled run as 2026-09-21 while
# the listing it queries held a 09:00Z run that same day, and 40 other runs of
# that day passed. `collect` took the first listing as the truth. Driven here at
# the seam the failure crossed: `_get` answers the newest-ten query with only
# the old run (the shape the red run saw) and the windowed re-ask with the whole
# history. The null control is the point of the check: when BOTH shapes agree
# the nightly is old, the reader must stay RED -- without it this passes on a
# reader that stopped looking at all.
_ns_stale_real_get, _ns_stale_real_sleep = _nstatus._get, _nstatus._sleep
_ns_stale_now = datetime(2026, 10, 1, 14, 7, tzinfo=UTC)
_ns_old = _ns_run(35575590367, "2026-09-21T07:59:34Z")
_ns_new = _ns_run(36839970966, "2026-10-01T09:00:52Z")


def _ns_stale_collect(first, windowed):
    _calls = []

    def _fake_get(url, _token):
        _calls.append(url)
        if "/jobs" in url:
            return {"total_count": len(_NS_LIVE), "jobs": _NS_LIVE}
        _runs = windowed if "created=" in url else first
        return {"workflow_runs": [r for r in _runs
                                  if r["event"] == url.split("event=")[1].split("&")[0]]}

    _nstatus._get, _nstatus._sleep = _fake_get, lambda _s: None
    try:
        _c, _f, _j = _nstatus.collect("o/r", "tests.yml", None, None,
                                      now=_ns_stale_now)
    finally:
        _nstatus._get, _nstatus._sleep = (_ns_stale_real_get,
                                          _ns_stale_real_sleep)
    return _c, _calls


_ns_ev = {"event": "schedule"}
_ns_rec, _ = _ns_stale_collect([{**_ns_old, **_ns_ev}],
                               [{**_ns_new, **_ns_ev}, {**_ns_old, **_ns_ev}])
_ns_dark, _ = _ns_stale_collect([{**_ns_old, **_ns_ev}], [{**_ns_old, **_ns_ev}])
_ns_fresh, _ns_fresh_calls = _ns_stale_collect([{**_ns_new, **_ns_ev}], [])
_ns_dark_state = _nstatus.verdict(_ns_dark, None, _NS_LIVE, _ns_stale_now)[0]
R.check(
    "a stale first listing is corroborated before the nightly is called "
    "ABSENT, and a nightly every listing agrees is old stays ABSENT",
    _ns_rec and _ns_rec["id"] == _ns_new["id"]
    and _ns_dark_state == _nstatus.ABSENT
    and _ns_fresh["id"] == _ns_new["id"]
    and not any("created=" in _u for _u in _ns_fresh_calls),
    f"recovered={_ns_rec and _ns_rec['id']}; every-shape-old={_ns_dark_state}; "
    f"fresh answer re-asked={any('created=' in _u for _u in _ns_fresh_calls)}",
)
sys.exit(0 if R.ok else 1)
