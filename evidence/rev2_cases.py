"""Round-2 reviewer cases for PR 3584: attacks on listed_at's reconstruction of busy() at a red gate's start.
    python3 rev2_cases.py <tree>
Every case: R1's gate red, started 08:02:00, completed 08:02:30 (T.real_red's stamps), R2 green and covering."""
import sys
sys.path.insert(0, sys.argv[1] + "/tools/ci")
import sweep  # noqa: E402,F401
import sweep_selftest as T  # noqa: E402
from gate import busy  # noqa: E402

R1, R2 = T.R1_3544, T.R2_3544
OLD = 43531447639                       # the fixer's lower-id run of REC3544
DISPATCH = "repos/o/r/actions/workflows/ci.yml/dispatches"
res = []


def red(runs):
    runs[R1]["gate"].update(started_at="2026-11-14T08:02:00Z", completed_at="2026-11-14T08:02:30Z")


def case(name, w, want, why):
    w.sweep()
    got = "dispatch" if DISPATCH in w.posts else ("rerun-in-place" if w.posts else "nothing")
    res.append((name, got == want))
    print(f"RESULT {name}: got={got} want={want} posts={w.posts}\n    why want: {why}")


# G. A held run (action_required, no jobs) created before the red's start. busy() excludes action_required by status;
#    listed_at ignores the run's status and reads a jobless run as in_progress.
def held(runs):
    red(runs)
    runs[OLD - 1] = {"id": OLD - 1, "event": "pull_request", "created_at": "2026-11-14T07:40:00Z",
                     "status": "action_required", "run_attempt": 1, "conclusion": None, "gate": None, "units": []}
case("G held (action_required) run at the head", T.world3544(ids=(R1, R2), edit=held), "dispatch",
     "busy() skips r['status']=='action_required' (gate.py busy), and read_api lists it with jobs={}")
print("    direct: busy() on the held run as read_api lists it ->",
      busy({"run_id": R1}, [{"id": OLD - 1, "title": "", "status": "action_required", "jobs": {}}]))
print("    direct: busy() on listed_at's row for it ->",
      busy({"run_id": R1}, [sweep.listed_at({"id": OLD - 1}, [], "2026-11-14T08:02:00Z")]))


# H. A lower-id run whose re-run-failed-jobs re-ran one unit AFTER the red's start: at 08:02 that run was completed
#    (busy() skips it); listed_at reads its latest stamps and finds a unit queued at 08:02.
def rerun_failed(runs):
    red(runs)
    runs[OLD]["units"].append({"name": "tests / fast (3.14)", "conclusion": "success",
                               "started_at": "2026-11-14T08:10:00Z", "completed_at": "2026-11-14T08:15:00Z"})
case("H lower-id run, completed at the red's start, one unit re-run after it", T.world3544(ids=(OLD, R1, R2), edit=rerun_failed),
     "dispatch", "the run's status at 08:02 was completed: busy() never reads it; a later re-run re-stamps the job")


# I. Read lag: gate.py reads busy() at the END of judge's setup (git diff first, API reads last, R3-1), not at the job's
#    started_at. A lower-id unit finishing 08:02:10, before R1's read (R1 completed 08:02:30), was finished to busy().
def lag(runs):
    red(runs)
    runs[OLD]["units"].append({"name": "tests / fast (3.14)", "conclusion": "success",
                               "started_at": "2026-11-14T07:55:00Z", "completed_at": "2026-11-14T08:02:10Z"})
case("I lower-id unit finishing 10 s after the red gate's start, before its read", T.world3544(ids=(OLD, R1, R2), edit=lag),
     "dispatch (if the read came after 08:02:10)", "busy() reads at the read instant, which is after started_at")

ok = sum(1 for _, g in res if g)
print(f"SUMMARY: {len(res)} cases, {len(res) - ok} differ from want: {[n for n, g in res if not g]}")
