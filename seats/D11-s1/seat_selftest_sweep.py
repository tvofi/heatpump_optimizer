#!/usr/bin/env python3
"""D11-s1 round 11: does every seat instrument answer `--self-test` with a self-test?

dev/audit/README.md's layout line says tools/audit/seat/ holds "the stateless
seat instruments; each carries --self-test", and D11.md M1 makes `--self-test`
the positive control of every non-policy_lint row. This drives that control.

Metric (one line): of the top-level scripts in tools/audit/seat/ (*.py, *.sh,
*.mjs), how many, invoked as `<interp> <script> --self-test`, reach a LIVE
GitHub call (a `gh` invocation the shim on PATH logs) or a `sleep` -- i.e. run
their production body instead of a self-test. Count key: the shim log the
production process writes, never the script's text.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/seat_selftest_sweep.py [--jobs 4] [--only NAME...]
    ... --perturb   # the one-line edit: codeql-triage-poll.sh gains
                    # `[ "${1:-}" = --self-test ] && { echo ok; exit 0; }` as line 2 -> live_on_selftest down by 1
Each script runs in a temp COPY of the export, with PATH led by shims for gh
(logs argv, exits 1), sleep (logs, returns at once) and curl (logs, exits 1):
no live call leaves the box and the export is never written.
Expected at the baseline: RESULT live_on_selftest=<n> (exact, listed by name).
Null control: a script whose self-test is real (e.g. pr_cap.py) logs no shim call.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: each tools/audit/seat/<script>:main entry, driven as a process.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import concurrent.futures as cf
import shutil
import subprocess
import sys
import tempfile
import time

PY = sys.executable
ARGS = sys.argv[1:]
PERTURB = "--perturb" in ARGS
JOBS = int(ARGS[ARGS.index("--jobs") + 1]) if "--jobs" in ARGS else 4
ONLY = ARGS[ARGS.index("--only") + 1:] if "--only" in ARGS else None
TIMEOUT = 240
SEAT = "tools/audit/seat"

TMP = tempfile.mkdtemp(prefix="d11s1-seat-")
TREE = os.path.join(TMP, "tree")
shutil.copytree(".", TREE, ignore=shutil.ignore_patterns(".git", "__pycache__"), symlinks=True)
with open(os.path.join(TREE, ".git"), "w") as f:      # keep the worktree's git dir, read-only use
    f.write(open(".git").read())
if PERTURB:
    p = os.path.join(TREE, SEAT, "codeql-triage-poll.sh")
    lines = open(p).read().split("\n")
    lines.insert(1, '[ "${1:-}" = --self-test ] && { echo "self-test ok"; exit 0; }')
    open(p, "w").write("\n".join(lines))

SHIMS = os.path.join(TMP, "shims")
os.makedirs(SHIMS)
for name, rc in (("gh", 1), ("sleep", 0), ("curl", 1)):
    with open(os.path.join(SHIMS, name), "w") as f:
        f.write(f'#!/bin/sh\necho "{name} $*" >> "$D11S1_SHIM_LOG"\nexit {rc}\n')
    os.chmod(os.path.join(SHIMS, name), 0o755)

scripts = sorted(f for f in os.listdir(os.path.join(TREE, SEAT))
                 if f.endswith((".py", ".sh", ".mjs")) and os.path.isfile(os.path.join(TREE, SEAT, f)))
if ONLY:
    scripts = [s for s in scripts if s in ONLY]


def drive(name):
    log = os.path.join(TMP, f"{name}.shimlog")
    open(log, "w").close()
    interp = [PY, "-I"] if name.endswith(".py") else ["bash"] if name.endswith(".sh") else ["node"]
    env = {**os.environ, "PATH": f"{SHIMS}:{os.environ['PATH']}", "D11S1_SHIM_LOG": log,
           "HPO_PLANDATA": os.path.join(TMP, f"pd-{name}"), "GH_TOKEN": "", "GITHUB_TOKEN": "",
           # no push or fetch reaches GitHub: every github.com URL is rewritten to a dead path
           "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "url.file:///nonexistent-d11s1/.insteadOf",
           "GIT_CONFIG_VALUE_0": "https://github.com/"}
    t = time.time()
    try:
        r = subprocess.run(interp + [os.path.join(SEAT, name), "--self-test"], cwd=TREE, env=env,
                           capture_output=True, text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL)
        rc, out = r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired as e:
        rc, out = "timeout", str(e.stdout or "")
    calls = [l for l in open(log).read().splitlines() if l]
    gh = [c for c in calls if c.startswith("gh ")]
    sl = [c for c in calls if c.startswith("sleep ")]
    return name, rc, len(gh), len(sl), round(time.time() - t, 1), (out.strip().splitlines() or [""])[-1][:120], gh[:1]


c0 = time.process_time()
with cf.ThreadPoolExecutor(JOBS) as ex:
    res = list(ex.map(drive, scripts))
live = []
for name, rc, ngh, nsl, secs, tail, first in res:
    flag = ngh > 0 or nsl > 0
    if flag:
        live.append(name)
    print(f"{'LIVE ' if flag else '     '}{name:42s} rc={rc!s:8s} gh={ngh:<3d} sleep={nsl:<3d} {secs:6.1f}s  {tail}  {first[0][:100] if first else ''}")
print(f"RESULT scripts={len(res)} scripts")
print(f"RESULT live_on_selftest={len(live)} scripts")
print(f"RESULT nonzero_or_timeout={sum(1 for r in res if r[1] != 0)} scripts")
print("RESULT thread_factor=1.000")   # the parent only waits; the work is in child processes
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
shutil.rmtree(TMP, ignore_errors=True)
