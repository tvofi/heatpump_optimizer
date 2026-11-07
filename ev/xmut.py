# Reviewer's extra mutants (X*) run through the PR's own sliced checks, reusing the fixer harness's SLICE runner.
import sys, pathlib, tempfile, os, importlib.util
spec = importlib.util.spec_from_file_location("h", sys.argv[1] + "/dev/audit/harnesses/r10_nightly_status_mutants.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
root = pathlib.Path(sys.argv[1]); src = (root / "tests/nightly_status.py").read_text()
X = [("X1-first-bad-only", 'for j in bad):', 'for j in bad[:1]):'),
     ("X2-runfailed-kept", "bad, run_failed = [], False\n", "bad, run_failed = [], run_failed\n"),
     ("X3-gt-to-lt", '"created_at")) > started:', '"created_at")) < started:'),
     ("X4-greens-any-conclusion", 'if j.get("conclusion") == "success"}', '}'),
     ("X5-main-fetch-unconditional", "if (in_flight is not None and concluded is not None\n                and failing_jobs(jobs)):", "if (in_flight is not None and concluded is not None):"),
     ("X6-swallow-all", "            except Unreadable:\n                fly_jobs = None", "            except Exception:\n                fly_jobs = None")]
with tempfile.TemporaryDirectory() as t:
    for lab, o, n in X:
        if src.count(o) != 1: print(lab, "NA", src.count(o)); continue
        d = os.path.join(t, lab); os.makedirs(d); pathlib.Path(d, "nightly_status.py").write_text(src.replace(o, n))
        rc = h.run(d, root / "tests/entities.py"); print(f"RESULT {lab} rc={rc} {'KILLED' if rc else 'SURVIVED'}")
