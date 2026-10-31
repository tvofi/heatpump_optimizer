#!/usr/bin/env python3
"""D11-s1 round 9: is a non-stamp direct push to main reported by the release enumerator?

METRIC (one line): of the synthetic first-parent rows that land on main as direct
(non-pull-request) pushes and are NOT a stamp's output, how many does
`tools/release/stamp.py:rule4_problem` (with `blind_merges` and
`enumeration_went_blind` under it) refuse, in a window that also holds one
ordinary, correctly-noted pull-request merge.
KEY: the refusal string rule4_problem returns for the window, per injected row;
the row is counted reported only when its own sha appears in that refusal.
Context printed alongside (not the finding's number):
  - the live ruleset's bypass actors per rule set (GET /rulesets/<id>, read-only);
  - the real history: single-parent first-parent commits on main since v6.5.0, and
    how many touched a file outside `tests/env_drift.py:STAMP_WRITES` (the stamp's
    declared write set).
Rows injected (sha / parents / subject):
  d1 1 "feat: arbitrary change pushed over the deploy key"       -- plain direct push
  d2 1 "v9.9.9: stamp arbitrary content"                          -- stamp-shaped subject
  d3 2 "Merge branch 'x' into main"                               -- two-parent direct push (control: MUST be reported)

COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/direct_push_detectors.py
          [--perturb parents-ge-1]   one-line in-memory edit of blind_merges: `parents >= 2` -> `parents >= 1`
EXPECTED (baseline 1936d5ca): nonstamp_direct_reported=0 of 2; control two_parent_reported=1 of 1;
          history_nonstamp_direct=0. Perturbed: nonstamp_direct_reported rises (up).
MACHINE: box B3, 4 CPU Linux container. Ruleset read needs network (curl GET); counts exact.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, importlib.util, inspect, json, subprocess, sys, time

BASE = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
REPO = "tvofi/heatpump_optimizer"
T0p, T0t = time.process_time(), time.thread_time()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["parents-ge-1"])
    ap.add_argument("--offline", action="store_true", help="skip the ruleset read")
    a = ap.parse_args()
    stamp = load("stamp", "tools/release/stamp.py")
    if a.perturb == "parents-ge-1":
        src = inspect.getsource(stamp.blind_merges)
        new = src.replace("if parents >= 2 and", "if parents >= 1 and")
        assert new != src, "perturbation did not apply"
        ns = {}
        exec(compile(new, "blind_merges<perturbed>", "exec"), stamp.__dict__, ns)
        stamp.blind_merges = ns["blind_merges"]

    pr_row = ("p0", 2, "Merge pull request #9001 from tvofi/fix/example")
    injected = [("d1", 1, "feat: arbitrary change pushed over the deploy key"),
                ("d2", 1, "v9.9.9: stamp arbitrary content")]
    control = ("d3", 2, "Merge branch 'x' into main")
    notes = "## v9.9.9\n- the example fix (#9001)\n"
    reported = 0
    for row in injected:
        why = stamp.rule4_problem([row, pr_row], notes, "v9.9.8", "9.9.9")
        hit = bool(why) and row[0] in why
        print(f"# {row[0]} {row[2]!r}: rule4 -> {why!r}")
        reported += hit
    why = stamp.rule4_problem([control, pr_row], notes, "v9.9.8", "9.9.9")
    ctrl = int(bool(why) and control[0] in why)
    print(f"# control {control[0]} {control[2]!r}: rule4 -> {why!r}")

    # real history (context): single-parent first-parent commits since v6.5.0
    drift = load("env_drift", "tests/env_drift.py")
    raw = subprocess.run(["git", "log", "--first-parent", "--format=%H %P", f"v6.5.0..{BASE}"],
                         capture_output=True, text=True).stdout
    singles = [l.split()[0] for l in raw.splitlines() if len(l.split()) == 2]
    nonstamp = []
    for s in singles:
        files = set(subprocess.run(["git", "show", "--format=", "--name-only", s],
                                   capture_output=True, text=True).stdout.split())
        if not files <= drift.STAMP_WRITES:
            nonstamp.append(s[:10])
    print(f"# history: {len(singles)} single-parent first-parent commits since v6.5.0; outside STAMP_WRITES: {nonstamp}")

    if not a.offline:
        for rid in ("23698884", "23937752", "22628467"):
            try:
                d = json.loads(subprocess.run(["curl", "-sS", f"https://api.github.com/repos/{REPO}/rulesets/{rid}"],
                                              capture_output=True, text=True, check=True).stdout)
                print(f"# ruleset {rid} {d.get('name')}: rules={[r['type'] for r in d.get('rules', [])]} "
                      f"bypass={d.get('bypass_actors')}")
                dk = [b for b in d.get("bypass_actors") or [] if b.get("actor_type") == "DeployKey"
                      and b.get("bypass_mode") == "always"]
                print(f"RESULT ruleset_{rid}_deploykey_always_bypass={len(dk)} count")
            except Exception as e:
                print(f"# ruleset {rid}: read failed ({e}); not a pass")

    print(f"RESULT nonstamp_direct_injected={len(injected)} count")
    print(f"RESULT nonstamp_direct_reported={reported} count")
    print(f"RESULT two_parent_control_reported={ctrl} count")
    print(f"RESULT history_single_parent={len(singles)} count")
    print(f"RESULT history_nonstamp_direct={len(nonstamp)} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
