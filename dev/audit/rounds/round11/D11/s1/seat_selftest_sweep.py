#!/usr/bin/env python3
"""D11-s1 round 11: does every seat instrument answer `--self-test` with a self-test?

dev/audit/README.md's layout line says tools/audit/seat/ holds "the stateless
seat instruments; each carries --self-test", and D11.md M1 makes `--self-test`
the positive control of every non-policy_lint row. This drives that control.

Metric (one line): of the top-level scripts in tools/audit/seat/ (*.py, *.sh,
*.mjs), how many, invoked as `<interp> <script> --self-test`, attempt a WRITE
to GitHub -- a `git push` whose remote is configured as a github.com URL, or a
`gh` call that writes (api -X PATCH/POST/PUT/DELETE, -f/-F fields, pr/issue
merge|create|comment|edit|close) -- through the shims on PATH: RESULT
github_writes_on_selftest. Count key: the shim log the production process
writes, never the script's text. Secondary screens: live_on_selftest (any gh
or sleep call) and no_selftest (no self-test verdict printed).

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/seat_selftest_sweep.py [--jobs 4] [--only NAME...]
    ... --perturb   # the one-line edit: wt_sync.sh gains a self-test answer as
                    # line 2 -> github_writes_on_selftest down by 1, no_selftest down by 1
Each script runs in a temp COPY of the export, with PATH led by shims for gh
(logs argv, exits 1), sleep (logs, returns at once), curl (logs, exits 1) and
git (logs a push to a github.com remote, then runs the real git, whose
github.com URLs are rewritten to a dead file:// path): no live call leaves the
box and the export is never written.
Expected at the baseline: RESULT real_repo_writes_on_selftest=1 (wt_sync.sh; github_writes_on_selftest=10 counts self-test fixture repos too: a
force-push of wip-sync/<slug> for every dirty worktree of the shared git dir), exact;
codeql-triage-poll.sh runs its production poll too (36 gh reads, a 6 h loop) and
reaches its PATCH dismissals only when alerts exist, which the gh shim never returns.
Expected at the baseline: RESULT no_selftest=<n> (scripts that print no self-test verdict at
all when asked for one; NO-SELFTEST lines name them), exact; live_on_selftest is a
screen only (many real self-tests call their own gh/sleep stubs through PATH).
Null control: a script whose self-test is real (e.g. pr_cap.py) logs no shim call.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: each tools/audit/seat/<script>:main entry, driven as a process.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import concurrent.futures as cf
import re
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
    p = os.path.join(TREE, SEAT, "wt_sync.sh")
    lines = open(p).read().split("\n")
    lines.insert(1, '[ "${1:-}" = --self-test ] && { echo "self-test ok"; exit 0; }')
    open(p, "w").write("\n".join(lines))

SHIMS = os.path.join(TMP, "shims")
os.makedirs(SHIMS)
for name, rc in (("gh", 1), ("sleep", 0), ("curl", 1)):
    with open(os.path.join(SHIMS, name), "w") as f:
        f.write(f'#!/bin/sh\necho "{name} $*" >> "$D11S1_SHIM_LOG"\nexit {rc}\n')
    os.chmod(os.path.join(SHIMS, name), 0o755)
REAL_GIT = shutil.which("git")
with open(os.path.join(SHIMS, "git"), "w") as f:
    # A push whose remote (a name or a URL among the args) is configured as github.com.
    f.write(f'''#!/bin/bash
for a in "$@"; do
  if [ "$a" = push ]; then
    for r in "$@"; do
      u=$(case "$r" in *github.com*) echo "$r";; -*) ;; *) {REAL_GIT} config --get "remote.$r.url" 2>/dev/null;; esac)
      case "$u" in *github.com*) echo "gitpush $*" >> "$D11S1_SHIM_LOG"; break 2;; esac
    done
  fi
done
exec {REAL_GIT} "$@"
''')
os.chmod(os.path.join(SHIMS, "git"), 0o755)
GH_WRITE = re.compile(r"^gh (api .*(-X ?(PATCH|POST|PUT|DELETE)|--method ?(PATCH|POST|PUT|DELETE)|\s-[fF] )|(pr|issue) (merge|create|comment|edit|close|review))")

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
        o = e.stdout or b""
        rc, out = "timeout", o.decode(errors="replace") if isinstance(o, bytes) else o
    calls = [l for l in open(log).read().splitlines() if l]
    gh = [c for c in calls if c.startswith("gh ")]
    sl = [c for c in calls if c.startswith("sleep ")]
    wr = [c for c in calls if c.startswith("gitpush ") or GH_WRITE.search(c)]
    # ANSWERED: the process printed a self-test verdict at all -- an `ok`/`FAIL`
    # row, a "N passed"/"N checks" tally, or a line naming a self-test -- before
    # it stopped. A usage error, an argparse refusal, a KeyError on the flag or a
    # production loop prints none of them.
    answered = bool(re.search(r"(?mi)^\s*(ok|FAIL|PASS)\b|\b\d+ (passed|checks?|failed)\b|self-test", out))
    return name, rc, len(gh), len(sl), round(time.time() - t, 1), (out.strip().splitlines() or [""])[-1][:120], gh[:1], answered, wr


c0 = time.process_time()
with cf.ThreadPoolExecutor(JOBS) as ex:
    res = list(ex.map(drive, scripts))
live = []
unanswered = [r[0] for r in res if not r[7]]
writers = [r[0] for r in res if r[8]]
for r in res:
    if r[8]:
        print(f"WRITE {r[0]}: {len(r[8])} attempt(s), first: {r[8][0][:150]}")
for name, rc, ngh, nsl, secs, tail, first, answered, _wr in res:
    flag = ngh > 0 or nsl > 0
    if not answered:
        print(f"NO-SELFTEST {name}")
    if flag:
        live.append(name)
    print(f"{'LIVE ' if flag else '     '}{name:42s} rc={rc!s:8s} gh={ngh:<3d} sleep={nsl:<3d} {secs:6.1f}s  {tail}  {first[0][:100] if first else ''}")
print(f"RESULT scripts={len(res)} scripts")
print(f"RESULT live_on_selftest={len(live)} scripts")
print(f"RESULT no_selftest={len(unanswered)} scripts")
print(f"RESULT github_writes_on_selftest={len(writers)} scripts")
# A push from a repository outside every temp root: the real shared git dir, not a self-test fixture repo.
_tmp = (tempfile.gettempdir().rstrip("/") + "/", "/tmp/")
real = [r[0] for r in res if any(not re.search(r"-C (\S+)", w) or not re.search(r"-C (\S+)", w).group(1).startswith(_tmp) for w in r[8])]
for n in real:
    print(f"REAL-REPO-WRITE {n}")
print(f"RESULT real_repo_writes_on_selftest={len(real)} scripts")
print(f"RESULT nonzero_or_timeout={sum(1 for r in res if r[1] != 0)} scripts")
print("RESULT thread_factor=1.000")   # the parent only waits; the work is in child processes
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
shutil.rmtree(TMP, ignore_errors=True)
