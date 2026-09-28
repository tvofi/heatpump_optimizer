"""Null controls that the barrier cannot go green by skipping (in-memory mutants)."""
import contextlib, io, sys
sys.path.insert(0, "tests")
import ha_contract as hc
def run(label):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = hc.main([])
    fails = [l.strip() for l in buf.getvalue().splitlines() if l.strip().startswith("FAIL")]
    print(f"{label}: rc={rc} fails={len(fails)}")
    for f in fails: print("   ", f[:150])
run("unmutated (defect present)")
orig = dict(hc.HOOKS); hc.HOOKS.clear()
run("skip mutant: no hook declared"); hc.HOOKS.update(orig)
orig2 = hc.stub_dropped; hc.stub_dropped = lambda: {}
run("skip mutant: drop scan reads nothing"); hc.stub_dropped = orig2
orig3 = hc._assert_lines; hc._assert_lines = lambda fn: set()
run("blind mutant: vacuity arm counts no asserts"); hc._assert_lines = orig3
