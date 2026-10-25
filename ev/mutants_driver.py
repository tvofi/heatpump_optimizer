import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
M = [
 ("M7-sweep-lower-only", "tools/ci/sweep.py", 'runs if r["id"] != v["id"]', 'runs if r["id"] < v["id"]', ["sweep"], "editcode"),
 ("M7b-sweep-higher-only", "tools/ci/sweep.py", 'runs if r["id"] != v["id"]', 'runs if r["id"] > v["id"]', ["sweep"], "cascade"),
 ("M5-prelude-id-order", "tools/ci/prelude.py", '(run["id"] < run_id or t is None or t[0] == "code")', '(run["id"] < run_id)', ["prelude"], "2754"),
 ("M5b-prelude-code-always-waits", "tools/ci/prelude.py", 'or t is None or t[0] == "code")', 'or True)', ["prelude"], "pair"),
 ("M6-prelude-until-finished", "tools/ci/prelude.py", 'if not judging(run):', 'if True:', ["prelude"], "2754"),
 ("M1-judge-never-waits", "tools/ci/gate.py", 'if ok or why != [deferral(waiting)] or now() - t0 + POLL_S > GATE_WAIT_MAX_S:', 'if True:', ["gate"], "pair"),
 ("M4-defer-as-pass", "tools/ci/gate.py", '"PASS" if ok', '"PASS" if ok or why == [deferral(waiting)]', ["gate"], "2754-red"),
]
for name, f, old, new, tests, scen in M:
    p = root / f; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        print(f"### {name}: {f}: {old!r} -> {new!r}")
        for t in tests:
            r = subprocess.run([sys.executable, "-I", f"tools/ci/{t}.py", "--self-test"], cwd=root, capture_output=True, text=True, timeout=300)
            fails = [l for l in r.stdout.splitlines() if "FAIL" in l]
            print(f"  {t} self-test rc={r.returncode}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]}")
            for l in fails[:6]: print("    " + l)
        args = [sys.executable, "-I", "dev/audit/harnesses/r10_gate_defer_race.py"] + (["--edit-s", "760"] if scen == "editcode" else []) + [scen]
        r = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=600)
        print("  harness: " + " | ".join(l for l in r.stdout.splitlines() if l.startswith(scen + ":")))
    finally:
        p.write_text(src)
print("git status:", subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True).stdout or "clean")
