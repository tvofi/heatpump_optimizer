"""Reviewer's own mutants (local-reviewer-s10, #2910) over the head's ci_predict.py.

Each mutant is applied to a copy loaded from a scratch module, and the arm's own
self-test (self_test_reads_self_test) is run against the head tree. Prints RESULT.
"""
import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()
src = (root / "tools" / "pr" / "ci_predict.py").read_text()
MUTANTS = {
    "R0-unmutated": None,
    "R1-record-not-rekeyed-to-host": ('{**rec, "script": host}', "rec"),
    "R2-window-zero": ("SELF_TEST_WINDOW = 12", "SELF_TEST_WINDOW = 0"),
    "R3-hosts-union-inert_reads-again": ("hosts = self_test_hosts(root, f, closures)",
        "hosts = self_test_hosts(root, f, {**closures, **{k: list(set(closures.get(k, ())) | set(v)) for k, v in inert_reads.items()}})"),
    "R4-under-scoped-header-unparsed": ('"UNDER-SCOPED" if line.startswith("UNDER-SCOPED") else None', "None"),
    "R5-no-self-test-filter-negated": ('if "--self-test" not in (root / f).read_text(errors="replace"):',
                                       'if "--self-test" in (root / f).read_text(errors="replace"):'),
    "R6-host-may-be-file-itself": ("if script == f or f not in", "if f not in"),
    "R7-window-huge": ("SELF_TEST_WINDOW = 12", "SELF_TEST_WINDOW = 10000"),
    "R8-no-self-test-word-needed": ('re.search(r"self[-_]test", ln)', 'True'),
}
for name, sub in MUTANTS.items():
    s = src
    if sub:
        assert sub[0] in s, name
        s = s.replace(sub[0], sub[1], 1)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "ci_predict_mut.py"
        p.write_text(s)
        spec = importlib.util.spec_from_file_location("ci_predict_mut", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bad = m.self_test_reads_self_test(root)
        for k in [k for k in sys.modules if k == "closure"]:
            del sys.modules[k]
        fails = [ln.strip() for ln in buf.getvalue().splitlines() if "FAIL" in ln]
        verdict = "baseline" if sub is None else ("KILLED" if bad else "SURVIVED")
        print(f"RESULT mutant={name} fails={bad} {verdict}")
        for f in fails:
            print("   ", f[:160])
