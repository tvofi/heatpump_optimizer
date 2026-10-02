"""F10.11 review: do the three new controls kill mutants of run_bounded?"""
import os, sys, types
sys.path.insert(0, "tests")
src = open("tests/harness_headers.py").read()
MUTANTS = {
    "none (null control)": (None, None),
    "A no RLIMIT_CPU (preexec_fn dropped)": ("timeout=wall_s, preexec_fn=limit,", "timeout=wall_s,"),
    "B no wall timeout": ("timeout=wall_s, preexec_fn=limit,", "preexec_fn=limit,"),
    "C rlimit on wall arg": ("(cpu_s, cpu_s + 5)", "(wall_s, wall_s + 5)"),
    "D comment-only": ("# The hang bound is CPU seconds", "# The hang bound is CPU-seconds"),
}
env = dict(os.environ)
for name, (a, b) in MUTANTS.items():
    s = src if a is None else src.replace(a, b)
    assert a is None or s != src, name
    m = types.ModuleType("hh"); m.__file__ = "tests/harness_headers.py"
    exec(compile(s, "hh", "exec"), m.__dict__)
    idle = [sys.executable, "-c", "import time; time.sleep(3)"]
    spin = [sys.executable, "-c", "while True: pass"]
    c1 = m.run_bounded(idle, env, 1, 30)[0] == 0
    c2 = m.run_bounded(spin, env, 1, 30)[0] < 0
    c3 = m.run_bounded(idle, env, 30, 1)[0] == 124
    print(f"{name}: idle-not-killed={c1} spin-killed={c2} wall-124={c3} ->",
          "SURVIVES" if (c1 and c2 and c3) else "KILLED")
