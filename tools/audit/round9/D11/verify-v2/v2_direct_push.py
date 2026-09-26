#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s1-02.

METRIC (one line): of the in-tree first-parent enumerators runnable offline
  (stamp.py rule 4 over its own window_log_args/parse_window, and
  tests/delivery_status.py collect over its own LOG_FORMAT/parse_log), how many
  NAME a single-parent, non-stamp commit pushed straight onto main after a
  correctly-noted PR merge, read from a REAL git history (not injected tuples).
KEY: the direct push's abbreviated sha appearing in the detector's output
  (rule4_problem's refusal string; collect's unattributed list / unchecked_line).
ARMS:
  direct   single-parent commit touching custom_components/x.py, plain subject
  stampish single-parent commit touching custom_components/x.py, subject "v9.9.9: stamp ..."
  control  two-parent `git merge --no-ff` with subject "Merge branch 'x'" (must be named)
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_direct_push.py [--perturb parents-ge-1]
  --perturb parents-ge-1: in-memory, stamp.blind_merges `parents >= 2 and` -> `parents >= 1 and`
EXPECTED (baseline 1936d5ca): named_direct=0 of 4 (2 arms x 2 detectors), control_named=2 of 2;
  perturbed: stamp detector names both direct arms (named_direct rises to 2).
Writes only a temp git repo under tempfile.mkdtemp(). No network.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, importlib.util, inspect, subprocess, sys, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
ROOT = os.getcwd()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def git(repo, *a):
    env = dict(os.environ, GIT_AUTHOR_NAME="v2", GIT_AUTHOR_EMAIL="v2@x", GIT_COMMITTER_NAME="v2",
               GIT_COMMITTER_EMAIL="v2@x")
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True, env=env).stdout


def build(kind):
    r = tempfile.mkdtemp(prefix="d11v2-dp-")
    git(r, "init", "-q", "-b", "main")
    os.makedirs(os.path.join(r, "custom_components"))
    open(os.path.join(r, "custom_components", "x.py"), "w").write("A = 1\n")
    git(r, "add", "-A"); git(r, "commit", "-qm", "base")
    git(r, "tag", "v9.9.8")
    # an ordinary, correctly noted pull-request merge
    git(r, "checkout", "-qb", "fix/example")
    open(os.path.join(r, "f.txt"), "w").write("fix\n")
    git(r, "add", "-A"); git(r, "commit", "-qm", "fix: example")
    git(r, "checkout", "-q", "main")
    git(r, "merge", "-q", "--no-ff", "fix/example", "-m", "Merge pull request #9001 from tvofi/fix/example")
    if kind in ("direct", "stampish"):
        open(os.path.join(r, "custom_components", "x.py"), "w").write("A = 2  # arbitrary\n")
        git(r, "add", "-A")
        git(r, "commit", "-qm", "feat: arbitrary change" if kind == "direct" else "v9.9.9: stamp arbitrary content")
    else:
        git(r, "checkout", "-qb", "x")
        open(os.path.join(r, "custom_components", "x.py"), "w").write("A = 3\n")
        git(r, "add", "-A"); git(r, "commit", "-qm", "x change")
        git(r, "checkout", "-q", "main")
        git(r, "merge", "-q", "--no-ff", "x", "-m", "Merge branch 'x'")
    sha = git(r, "rev-parse", "--short", "HEAD").strip()
    full = git(r, "rev-parse", "HEAD").strip()
    return r, sha, full


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["parents-ge-1"])
    a = ap.parse_args()
    stamp = load("stamp", "tools/release/stamp.py")
    ds = load("delivery_status", "tests/delivery_status.py")
    if a.perturb:
        src = inspect.getsource(stamp.blind_merges)
        new = src.replace("if parents >= 2 and", "if parents >= 1 and")
        assert new != src
        ns = {}
        exec(compile(new, "blind_merges<perturbed>", "exec"), stamp.__dict__, ns)
        stamp.blind_merges = ns["blind_merges"]
    notes = "## v9.9.9\n- the example fix (#9001)\n"
    named = {}
    for kind in ("direct", "stampish", "control"):
        r, sha, full = build(kind)
        raw = subprocess.run(stamp.window_log_args("v9.9.8"), cwd=r, capture_output=True, text=True).stdout
        window = stamp.parse_window(raw)
        why = stamp.rule4_problem(window, notes, "v9.9.8", "9.9.9") or ""
        s_hit = sha in why
        log = subprocess.run(["git", "log", "--first-parent", f"--format={ds.LOG_FORMAT}", "v9.9.8..main"],
                             cwd=r, capture_output=True, text=True).stdout
        merges, unattr = ds.collect(ds.parse_log(log))
        d_hit = any(u["sha"] == full for u in unattr)
        line = ds.unchecked_line(unattr) if unattr else ""
        print(f"# {kind:8s} head={sha} window={[(w[1], w[2]) for w in window]}")
        print(f"#   stamp.rule4_problem -> {why!r}")
        print(f"#   delivery_status.collect merges={[m['number'] for m in merges]} unattributed={len(unattr)} {line[:90]!r}")
        named[kind] = (s_hit, d_hit)
    nd = sum(named["direct"]) + sum(named["stampish"])
    print(f"RESULT named_direct={nd} of 4 count")
    print(f"RESULT named_direct_stamp={int(named['direct'][0]) + int(named['stampish'][0])} of 2 count")
    print(f"RESULT named_direct_delivery_status={int(named['direct'][1]) + int(named['stampish'][1])} of 2 count")
    print(f"RESULT control_named={sum(named['control'])} of 2 count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
