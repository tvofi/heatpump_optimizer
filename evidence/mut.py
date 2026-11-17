import subprocess, sys, pathlib
F = pathlib.Path(sys.argv[1]) / "tools/audit/regret_oracle.py"
orig = F.read_text()
M = [
 ("least-inverted", "        if c < c_same - EPS:\n", "        if c > c_same + EPS:\n"),
 ("admit-bounds-dropped", "self.in_limits(space, dhw) and v <= ref[0] + VIOL_TOL", "self.in_limits(space, dhw) and True"),
 ("admit-terminal-dropped", "(not terminal or all(", "(True or all("),
 ("admit-limits-dropped", "return (self.in_limits(space, dhw) and v", "return (True and v"),
 ("greedy-unadmitted", "    if L.admits(g, dhw, ref):\n", "    if True:\n"),
 ("perturbed-unadmitted", "cc < best_c - EPS and L.admits(c, dhw, ref)", "cc < best_c - EPS"),
 ("regret-sign", "regret, gap = c_real - c_same,", "regret, gap = c_same - c_real,"),
 ("greedy-dearest", "np.argsort(price, kind=\"stable\")", "np.argsort(-price, kind=\"stable\")"),
 ("plant-model-never", "            cands.append((\"plant-model\", L.cost(s2, d2)))", "            pass"),
 ("null-comment", "def greedy(space", "# noop\ndef greedy(space"),
]
try:
    for name, a, b in M:
        assert orig.count(a) == 1, name
        F.write_text(orig.replace(a, b))
        r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], cwd=sys.argv[1], capture_output=True, text=True, timeout=600)
        last = (r.stdout + r.stderr).strip().splitlines()[-1:] 
        fails = [l for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l][:3]
        print(("KILLED" if r.returncode else "SURVIVED"), name, "rc=%d" % r.returncode, last, fails, flush=True)
finally:
    F.write_text(orig)
    print("restored", flush=True)
