"""Reviewer-built cases for PR 3584 (the reviewer's own, not the fixer's). Run with the tree's tools/ci on sys.path:
    python3 rev_cases.py <tree>
"""
import sys
sys.path.insert(0, sys.argv[1] + "/tools/ci")
import sweep  # noqa: E402
import sweep_selftest as T  # noqa: E402

D, R1, R2 = T.D3544, T.R1_3544, T.R2_3544
DISPATCH = "repos/o/r/actions/workflows/ci.yml/dispatches"
rerun = lambda rid: f"repos/o/r/actions/jobs/{rid * 10}/rerun"
res = []


def case(name, w, want):
    rc, out = w.sweep()
    got = "dispatch" if DISPATCH in w.posts else ("rerun-in-place" if w.posts else "nothing")
    res.append((name, got, want, w.posts))
    print(f"RESULT {name}: got={got} want={want} posts={w.posts} attempt_reads={getattr(w, 'attempt_reads', '-')}")


def real_red(runs):
    """R1's gate judged a REAL red at 08:02:00-08:02:30, after every required source anywhere had finished
    (it is not a deferral: busy() read nothing)."""
    runs[R1]["gate"].update(started_at="2026-11-14T08:02:00Z", completed_at="2026-11-14T08:02:30Z")


# A. Null: real red, nothing else late -> dispatch (the fixer's null, rebuilt here with no own-job row).
case("A real red, no late source, green R2 covering", T.world3544(ids=(R1, R2), edit=real_red), "dispatch")


# B. Mine: the same real red, but R2 (green, covering) has ONE job outside gate's needs that finished after R1's gate
#    started -- a report-only job such as governance / delivery-status-publish or tests / nightly-status, which ci.yml
#    runs beside gate. busy() never read it (R2's gate had started and R2 is a higher id), so R1's red is a verdict.
def late_report_job(runs):
    real_red(runs)
    runs[R2]["units"].append({"id": R2 * 10 + 9, "name": "tests / nightly-status", "status": "completed",
                              "conclusion": "failure", "started_at": "2026-11-14T08:01:50Z",
                              "completed_at": "2026-11-14T08:02:10Z"})
case("B real red, R2 report-only job finished after R1 gate start", T.world3544(ids=(R1, R2), edit=late_report_job),
     "dispatch")


# C. Mine: real red, and a third run (pull_request_review R3, created before R2's gate started) still has a job in
#    progress (completed_at None -> '~'), its gate already green-free -- here R3 has no gate yet listed as a source.
def unfinished_other(runs):
    real_red(runs)
    r3 = dict(runs[R1], id=R2 + 1, event="pull_request_review", created_at="2026-11-14T07:59:00Z",
              conclusion="success", run_attempt=1, triggering_actor={"login": "tvofi"})
    r3["gate"] = {"id": r3["id"] * 10, "name": "gate", "status": "completed", "conclusion": "success",
                  "started_at": "2026-11-14T08:03:00Z", "completed_at": "2026-11-14T08:03:30Z"}
    r3["units"] = [{"id": r3["id"] * 10 + 1, "name": "governance / delivery-status-publish", "status": "completed",
                    "conclusion": "success", "started_at": "2026-11-14T08:03:31Z", "completed_at": "2026-11-14T08:04:00Z"}]
    runs[r3["id"]] = r3
case("C real red, another run's post-gate job finished after it", T.world3544(ids=(R1, R2), edit=unfinished_other),
     "dispatch")


# D. Two deferrals, nothing green (#3261 shape): R2's gate red too -> still dispatches once.
def two_reds(runs):
    runs[R2]["gate"].update(conclusion="failure")
    runs[R2]["conclusion"] = "failure"
case("D #3261 pair: both deferral reds, nothing green", T.world3544(ids=(R1, R2), v_id=R2, edit=two_reds), "dispatch")


# E. Cap: an in-place deferral re-run at attempt 44 (cap-1) is left; at 43 it is re-run.
for att, want in ((sweep.ATTEMPT_CAP - 1, "nothing"), (sweep.ATTEMPT_CAP - 2, "rerun-in-place")):
    case(f"E deferral at attempt {att}",
         T.world3544(ids=(R1, R2), edit=lambda runs, a=att: runs[R1].update(run_attempt=a)), want)


# F. Unreadable first attempt (404) of a dispatch red at attempt 2 -> not a judge -> dispatch.
def d_red_unreadable(w):
    w.runs[D].pop("attempts")
w = T.world3544(edit=real_red); d_red_unreadable(w)
case("F dispatch red at attempt 2, attempt 1 unreadable (404)", w, "dispatch")

# F2. First attempt listing readable but its gate is beyond the page (no gate row) -> dispatch.
w = T.world3544(edit=real_red)
w.runs[D]["attempts"] = {}   # 404 too; simulate gate absent by a non-gate row instead:
orig_get = w.get
def get_nogate(path, params=None, _o=orig_get):
    if "/attempts/1/jobs" in path:
        w.attempt_reads += 1
        return 200, {}, {"jobs": [{"name": "u1", "conclusion": "success"}]}
    return _o(path, params)
w.get = get_nogate
case("F2 dispatch red at attempt 2, attempt-1 listing without a gate row", w, "dispatch")

bad = [r for r in res if r[1] != r[2]]
print(f"SUMMARY: {len(res)} cases, {len(bad)} differ from want: {[r[0] for r in bad]}")
