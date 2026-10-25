import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mutation_table as _mut
class _R:
    fails=0
    def check(self,name,ok,detail=""):
        print(("ok   " if ok else "FAIL ")+name[:90]+("" if ok else "  :: "+detail[:400]))
        if not ok: self.fails+=1
R=_R()
_RCH_DRIVER = """\
import os, subprocess, sys
sys.path.insert(0, os.getcwd())
from custom_components.heatpump_optimizer import fx
fx.hit()
child = ("import os, sys, time; sys.path.insert(0, os.getcwd()); "
         "from custom_components.heatpump_optimizer import fx; fx.child_only(); "
         "sys.stdout.write('x'); sys.stdout.flush(); time.sleep(60)")
env = None
if os.environ.get("RCH_STRIP"):
    env = {k: v for k, v in os.environ.items() if k != "HPO_REACH_OUT"}
if os.environ.get("RCH_PATH"):
    env = {**os.environ, "PYTHONPATH": os.getcwd()}
p = subprocess.Popen([sys.executable, "-c", child], stdout=subprocess.PIPE,
                     env=env, close_fds=not os.environ.get("RCH_NOCLOSE"))
p.stdout.read(1)
p.kill()
p.wait()
if os.environ.get("RCH_READ"):
    open(fx.__file__).read()
if os.environ.get("RCH_FORK"):
    pid = os.fork()
    if pid == 0:
        fx.missed()
        os._exit(0)
    os.waitpid(pid, 0)
if os.environ.get("RCH_GIT"):
    subprocess.run(["git", "--version"], capture_output=True)
if os.environ.get("RCH_SPAWN"):
    import shutil
    os.waitpid(os.posix_spawn(shutil.which("git"), ["git", "--version"],
                              os.environ), 0)
sys.exit(int(os.environ.get("RCH_RC", "0")))
"""
_RCH_FX = "def hit():\n    return 1\n\n\ndef missed():\n    return 2\n\n\ndef child_only():\n    return 3\n"
_RCH_REL = "custom_components/heatpump_optimizer/fx.py"


def _rch_run(**env: str):
    with tempfile.TemporaryDirectory() as _d:
        _t = Path(_d)
        (_t / "custom_components/heatpump_optimizer").mkdir(parents=True)
        (_t / "custom_components/__init__.py").write_text("")
        (_t / "custom_components/heatpump_optimizer/__init__.py").write_text("")
        (_t / _RCH_REL).write_text(_RCH_FX)
        (_t / "driver.py").write_text(_RCH_DRIVER)
        _run, _reach = _mut.traced_baseline(
            _mut.run_script, "driver.py", _t, 120, [],
            {f"RCH_{k}": v for k, v in env.items()})
        return _run, _reach, _mut.executable_lines(_t / _RCH_REL)


_RCH_RUN, _RCH, _RCH_EXE = _rch_run()
_rch_never = {ln: _mut.never_reaches(_RCH, _RCH_REL, ln, _RCH_EXE)
              for ln in (2, 6, 10)}
R.check(
    "the reach tracer reads a clean run's row: an executed line is reached, "
    "one no process executed is never, and a SIGKILLed child's line counts",
    _RCH_RUN.rc == 0 and _RCH is not None
    and _rch_never == {2: False, 6: True, 10: False}
    and _RCH["processes"] == {"started": 2, "recorded": 2},
    f"rc={_RCH_RUN.rc} never={_rch_never} "
    f"processes={_RCH and _RCH['processes']} problems="
    f"{_mut.reach_problems(_RCH)}",
)
_rch_refused = {}
for _k, _env in (("read", {"READ": "1"}), ("git", {"GIT": "1"}),
                 ("spawn", {"SPAWN": "1"}),
                 ("strip", {"STRIP": "1"}), ("path", {"PATH": "1"}),
                 ("red", {"RC": "1"})):
    _r, _x, _e = _rch_run(**_env)
    _rch_refused[_k] = (_r.rc, _x is not None,
                        _x is not None and _mut.never_reaches(_x, _RCH_REL, 6, _e))
R.check(
    "and every way the row can be blind refuses the skip: a source read, a "
    "non-Python child (through subprocess or a bare os.posix_spawn), a "
    "Python child without the tracer's environment or "
    "its PYTHONPATH (started, never recorded), and a red run, which "
    "returns no row at all",
    _rch_refused == {"read": (0, True, False), "git": (0, True, False),
                     "spawn": (0, True, False),
                     "strip": (0, True, False), "path": (0, True, False),
                     "red": (1, False, False)},
    f"(rc, has row, skipped) per arm: {_rch_refused}",
)
# Popen starts its child through os.posix_spawn wherever it can close fds
# in the spawn (CPython 3.13+ on glibc 2.34+, CI's runner) and through
# fork_exec elsewhere, so the clean row depends on the interpreter's build.
# close_fds=False takes the posix_spawn route on every 3.13+, so a box
# whose Python lacks POSIX_SPAWN_CLOSEFROM still drives it.
_r, _x, _e = _rch_run(NOCLOSE="1")
R.check(
    "and a Popen child started through os.posix_spawn reads the same clean row",
    _r.rc == 0 and _x is not None and not _mut.reach_problems(_x)
    and {ln: _mut.never_reaches(_x, _RCH_REL, ln, _e) for ln in (2, 6, 10)}
    == {2: False, 6: True, 10: False},
    f"rc={_r.rc} problems={_x and _mut.reach_problems(_x)} "
    f"processes={_x and _x['processes']}",
)
# A forked child inherits the tracer, and the line it alone executes is
# reached, with every process accounted for -- a row the skip may still use.
_r, _x, _e = _rch_run(FORK="1")
R.check(
    "and a forked child's executed line counts, the row still clean",
    _r.rc == 0 and _x is not None and not _mut.reach_problems(_x)
    and not _mut.never_reaches(_x, _RCH_REL, 6, _e),
    f"rc={_r.rc} problems={_x and _mut.reach_problems(_x)} "
    f"processes={_x and _x['processes']}",
)
# A red traced run is re-run untraced and returns no reach (traced_baseline):
# the tracer can drop rows, never turn a baseline red. A pair with no row,
# or on a line no instruction is attributed to, is driven.
R.check(
    "and no row, a red run's row or an instruction-less line drives the pair",
    not _mut.never_reaches(None, _RCH_REL, 6, _RCH_EXE)
    and not _mut.never_reaches({**_RCH, "rc": 1}, _RCH_REL, 6, _RCH_EXE)
    and not _mut.never_reaches(_RCH, _RCH_REL, 3, _RCH_EXE)
    and 3 not in _RCH_EXE,
    f"no-row={_mut.never_reaches(None, _RCH_REL, 6, _RCH_EXE)} "
    f"blank-line-executable={3 in _RCH_EXE}",
)


print('FAILS',R.fails)
