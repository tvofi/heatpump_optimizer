# Reviewer's harness (builder: reviewer), the r1 verdict's unguarded-domain cases re-driven
# through merge_train.introduced_at, plus new attacks. Usage: python3 domain.py <tree>
import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as m, inspect
S = m.SELFTESTS
def job(i, concl, status="completed"): return {"name": S, "id": i, "status": status, "conclusion": concl}
new = "base_runs" in str(inspect.signature(m.introduced_at)) or True
def run(label, hj, bj, steps):
    reads = []
    def js(i): reads.append(i); return steps.get(i)
    hr = [hj] if hj else []
    br = [bj] if bj else []
    try:
        try:
            r = m.introduced_at(hr, lambda: br, js)
        except TypeError:
            r = m.introduced_at(hr, br, js)
        out = r[0]
    except ValueError as e:
        out = f"STOP({str(e)[:60]})"
    except Exception as e:
        out = f"ERR({type(e).__name__}: {e})"
    print(f"{label}: {out} job reads {len(reads)}")
hang = [{"name": "hang", "conclusion": "cancelled"}, {"name": "after", "conclusion": "skipped"}]
green = [{"name": "hang", "conclusion": "success"}, {"name": "after", "conclusion": "success"}]
fail = [{"name": "hang", "conclusion": "failure"}, {"name": "after", "conclusion": "success"}]
drift = next(iter(m.SELFTESTS_PUSH_ONLY))
print("--- r1 verdict cases (positive: must be non-empty or STOP) ---")
run("V1 head failure + step cancelled, base success", job(1, "failure"), job(2, "success"), {1: hang, 2: green})
run("V2 head timed_out + step cancelled, base success", job(1, "timed_out"), job(2, "success"), {1: hang, 2: green})
run("V3 head cancelled, base success", job(1, "cancelled"), job(2, "success"), {1: hang, 2: green})
run("V4 step timed_out+cancelled in failed job", job(1, "failure"), job(2, "success"),
    {1: [{"name": "a", "conclusion": "timed_out"}, {"name": "b", "conclusion": "cancelled"}], 2: green})
print("--- nulls (must be []) ---")
run("N1 same step failing head and base", job(1, "failure"), job(2, "failure"), {1: fail, 2: fail})
run("N2 head success", job(1, "success"), job(2, "failure"), {})
run("N3 timeout inherited same step", job(1, "timed_out"), job(2, "timed_out"), {1: hang, 2: hang})
run("N4 head only push-only drift red", job(1, "failure"), job(2, "success"), {1: [{"name": drift, "conclusion": "failure"}], 2: green})
print("--- reviewer's attacks ---")
run("A1 head timed_out, base failure on same step (hang behind red)", job(1, "timed_out"), job(2, "failure"), {1: hang, 2: fail})
run("A2 head in_progress", job(1, None, "in_progress"), job(2, "success"), {})
run("A3 head queued", job(1, None, "queued"), job(2, "success"), {})
run("A4 head action_required", job(1, "action_required"), job(2, "success"), {})
run("A5 head stale", job(1, "stale"), job(2, "success"), {})
run("A6 head completed conclusion None", job(1, None), job(2, "success"), {})
run("A7 base in_progress, head failure", job(1, "failure"), job(2, None, "in_progress"), {1: fail, 2: green})
run("A8 base startup_failure, head failure", job(1, "failure"), job(2, "startup_failure"), {1: fail})
run("A9 no base run, head timed_out", job(1, "timed_out"), None, {1: hang})
run("A10 head timed_out, all steps success (impossible?)", job(1, "timed_out"), job(2, "success"), {1: green, 2: green})
run("A11 head timed_out whose only red step is push-only drift", job(1, "timed_out"), job(2, "success"), {1: [{"name": drift, "conclusion": "cancelled"}], 2: green})
run("A12 head failure, step unknown conclusion 'neutral'", job(1, "failure"), job(2, "success"), {1: [{"name": "x", "conclusion": "neutral"}], 2: green})
run("A13 head failure, step conclusion None (step still listed incomplete)", job(1, "failure"), job(2, "success"), {1: [{"name": "x", "conclusion": None}], 2: green})
run("A14 base timed_out, head failure on a different step", job(1, "failure"), job(2, "timed_out"), {1: [{"name": "z", "conclusion": "failure"}], 2: hang})
run("A15 base neutral (skipped-ish), head failure", job(1, "failure"), job(2, "neutral"), {1: fail, 2: []})
