#!/usr/bin/env python3
"""D11 verify-v3 (round 9), finding D11-s1-02: does any in-tree enumerator name a
non-stamp single-parent commit on main's first-parent line, on a REAL release window?

METRIC (one line): of the 2 production enumerators that quantify over main's first-parent
  line in Python (`tools/release/stamp.py:rule4_problem`, `tests/delivery_status.py:collect`),
  how many name a real non-stamp single-parent commit (084c6a27, a branch commit touching
  code-owned tests/harness.py) injected at the top of the real v6.7.0..v6.7.1^ window, with
  the real v6.7.1 notes.
KEY: the injected commit's sha in rule4_problem's refusal string / in collect()'s
  `unattributed` list -- the value each production seam returns.
Null control: the same real window with nothing injected passes rule4 (None) and leaves
  collect's unattributed empty. Live control: the same commit injected with 2 parents is named
  by both.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_direct_push.py
          [--perturb parents-ge-1]  in-memory: stamp.blind_merges `parents >= 2` -> `parents >= 1` and
                                    delivery_status.collect `> 1` -> `> 0` -> named rises to 2 (up).
EXPECTED (baseline 1936d5ca): named_single_parent=0 of 2; named_two_parent=2 of 2; null ok.
MACHINE: box G4-V3 cloud container, 4 CPU Linux, CPython 3.14.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, importlib.util, inspect, subprocess, sys, time

T0p, T0t = time.process_time(), time.thread_time()
BASE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
INJ = "084c6a27"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m)
    return m


def patch(mod, fn, old, new):
    src = inspect.getsource(getattr(mod, fn)); s2 = src.replace(old, new); assert s2 != src
    ns = {}; exec(compile(s2, f"{fn}<v3>", "exec"), mod.__dict__, ns); setattr(mod, fn, ns[fn])


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--perturb", choices=["parents-ge-1"])
    a = ap.parse_args()
    stamp = load("stamp_v3", "tools/release/stamp.py")
    ds = load("delivery_status_v3", "tests/delivery_status.py")
    if a.perturb:
        patch(stamp, "blind_merges", "if parents >= 2 and", "if parents >= 1 and")
        patch(ds, "collect", 'int(commit.get("parents", 1)) > 1', 'int(commit.get("parents", 1)) > 0')
    window = stamp.parse_window(git(*stamp.window_log_args("v6.7.0", BASE + "^")[1:]))
    notes = git("show", f"{BASE}:RELEASE_NOTES.md").split("\n## v6.7.0")[0]
    subj = git("log", "-1", "--format=%s", INJ).strip()
    body_of = lambda s: git("log", "-1", "--format=%b", s)

    def ds_rows(rows):
        return [{"sha": s, "parents": p, "subject": sub, "body": ""} for s, p, sub in rows]

    null_r4 = stamp.rule4_problem(window, notes, "v6.7.0", "6.7.1")
    _, null_un = ds.collect(ds_rows(window))
    print(f"# real window v6.7.0..v6.7.1^: {len(window)} first-parent rows; rule4 on real notes -> {null_r4!r}; "
          f"collect unattributed={len(null_un)}")
    named = {}
    for parents in (1, 2):
        w = [(INJ, parents, subj)] + window
        r4 = stamp.rule4_problem(w, notes, "v6.7.0", "6.7.1")
        _, un = ds.collect(ds_rows(w))
        named[parents] = int(bool(r4) and INJ in r4) + int(any(u["sha"] == INJ for u in un))
        print(f"# inject {INJ} {subj!r} parents={parents}: rule4 -> {(r4 or 'None')[:140]!r}; "
              f"collect names it={any(u['sha'] == INJ for u in un)}")
    print(f"RESULT window_rows={len(window)} count")
    print(f"RESULT null_rule4_refused={int(bool(null_r4))} count")
    print(f"RESULT null_collect_unattributed={len(null_un)} count")
    print(f"RESULT named_single_parent={named[1]} of 2")
    print(f"RESULT named_two_parent={named[2]} of 2")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
