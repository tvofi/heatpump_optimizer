#!/usr/bin/env python3
"""Late D3 intake, verifier V2 (independent) for D3-s1-01.

Metric (one line): unpinned inventory sites in the 12 D3-s1 cell files that lie
in tests/env_drift.py's measured closure, on a line some compiled instruction
maps to, and that a sys.monitoring LINE recorder (this file's own hook, not
mutation_table.REACH_HOOK) never sees fire during one
`env_drift.py --capture <tree> <out> --all` child run at the baseline.
Plus a hook-propagation probe: a child launched the way env_drift.py:2984
launches its capture (PYTHONPATH reset to <tree>/tests/hastub) loads a
sitecustomize placed on the parent's PYTHONPATH or not.

Run (from a baseline tree root):
  PYTHONPATH=tests/hastub python3 <this> [--reuse <lines.json>]
RESULT capture_never_executes_v2=<n>  RESULT executed_v2=<n>
RESULT child_loads_parent_hook=<0|1>
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402  (universe definition only)

CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]
HOOK = r'''
import os, sys, json, atexit
_out = os.environ.get("V2_LINES_OUT")
if _out:
    _mon = sys.monitoring
    _T = 4
    _mon.use_tool_id(_T, "v2lines")
    _seen = {}
    _pref = os.environ["V2_PROD"]
    def _line(code, ln):
        f = code.co_filename
        if f.startswith(_pref):
            _seen.setdefault(f, set()).add(ln)
        return _mon.DISABLE
    _mon.register_callback(_T, _mon.events.LINE, _line)
    _mon.set_events(_T, _mon.events.LINE)
    def _dump():
        p = os.path.join(_out, f"{os.getpid()}.json")
        json.dump({k: sorted(v) for k, v in _seen.items()}, open(p, "w"))
    atexit.register(_dump)
'''


def executable(path):
    seen = set()

    def walk(c):
        seen.update(ln for _, _, ln in c.co_lines() if ln is not None)
        for k in c.co_consts:
            if hasattr(k, "co_lines"):
                walk(k)
    walk(compile(path.read_text(), str(path), "exec"))
    return seen


def main():
    tmp = Path(tempfile.mkdtemp(prefix="v2-d3s1-"))
    hookdir = tmp / "hook"
    hookdir.mkdir()
    (hookdir / "sitecustomize.py").write_text(HOOK)
    # Probe: does a child launched with PYTHONPATH reset see the parent's hook?
    probe_out = tmp / "probe"
    probe_out.mkdir()
    env = dict(os.environ, V2_LINES_OUT=str(probe_out), V2_PROD="/nonexistent",
               PYTHONPATH=f"{hookdir}{os.pathsep}tests/hastub")
    child = ("import os,subprocess,sys;e=dict(os.environ);"
             "e['PYTHONPATH']=os.path.join(os.getcwd(),'tests','hastub');"
             "subprocess.run([sys.executable,'-c','pass'],env=e,check=True)")
    subprocess.run([sys.executable, "-c", child], env=env, check=True)
    n_rec = len(list(probe_out.glob("*.json")))
    print(f"RESULT probe_processes_started=2 probe_recorded={n_rec}")
    print(f"RESULT child_loads_parent_hook={int(n_rec >= 2)}")

    if "--reuse" in sys.argv:
        lines = json.loads(Path(sys.argv[sys.argv.index("--reuse") + 1]).read_text())
    else:
        out = tmp / "lines"
        out.mkdir()
        env = dict(os.environ, V2_LINES_OUT=str(out),
                   V2_PROD=str(ROOT / "custom_components"),
                   PYTHONPATH=f"{hookdir}{os.pathsep}{ROOT / 'tests' / 'hastub'}")
        t0 = time.time()
        r = subprocess.run([sys.executable, "tests/env_drift.py", "--capture",
                            str(ROOT), str(tmp / "cap.json"), "--all"], env=env)
        print(f"RESULT capture_rc={r.returncode} "
              f"capture_wall_s={time.time() - t0:.1f} (provisional)")
        lines = {}
        for p in out.glob("*.json"):
            for f, ls in json.loads(p.read_text()).items():
                lines.setdefault(f, set()).update(ls)
        lines = {k: sorted(v) for k, v in lines.items()}
        (tmp / "lines.json").write_text(json.dumps(lines))
        print(f"RESULT lines_json={tmp / 'lines.json'} "
              f"processes_recorded={len(list(out.glob('*.json')))}")
    budgets = mt.load_budgets()
    inv = mt.inventory(sorted(mt.PRODUCTION / (c + ".py") for c in CELLS))
    sites = mt.unpinned_sites(budgets, inv)
    clos = mt.load_closures()["tests/env_drift.py"]
    exe = {}
    never = execd = noexe = 0
    for m in sites:
        if m["file"] not in clos:
            continue
        rel = m["file"]
        if rel not in exe:
            exe[rel] = executable(ROOT / rel)
        if m["line"] not in exe[rel]:
            noexe += 1
            continue
        hit = set(lines.get(str(ROOT / rel), ()))
        if m["line"] in hit:
            execd += 1
        else:
            never += 1
    print(f"RESULT capture_never_executes_v2={never}")
    print(f"RESULT executed_v2={execd}")
    print(f"RESULT no_instruction_line={noexe}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
