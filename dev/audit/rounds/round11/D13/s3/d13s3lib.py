"""Shared REST plumbing for the round-11 D13-s3 harnesses (not a harness itself).

Why a new library rather than `tools/audit/round4/D11/d11lib.py`: its
`merged_prs()` is GraphQL, and a session whose token reaches the REST API only
(this seat's: `gh api graphql` answers HTTP 403) cannot run it, so
`dora_keys.py` and `governance_cost.py` cannot run end to end here. This
library reads REST alone: the window's merges are main's first-parent merge
commits, and each one's pull request comes from `/commits/<sha>/pulls`, the
API mode of `policy_lint.mjs`'s `enumerateMerges`.

CACHED under a private temp root (`$D13S3_CACHE`, default
`$TMPDIR/d13s3-r11-cache`) and FAILURE-COUNTING: every harness prints
`RESULT api_failures=<n>`; a figure beside a non-zero count is not evidence.

WINDOW. Seven days closed 7 h before the baseline commit so every run at a
window merge has concluded when it is read:
  W0 = 2026-11-09T12:00:00Z, W1 = 2026-11-16T12:00:00Z (override D13S3_W0/W1).
"""

import concurrent.futures as cf
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import threading
import time

REPO = os.environ.get("D13S3_REPO", "tvofi/heatpump_optimizer")
BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
W0 = os.environ.get("D13S3_W0", "2026-11-09T12:00:00Z")
W1 = os.environ.get("D13S3_W1", "2026-11-16T12:00:00Z")
CACHE = pathlib.Path(os.environ.get(
    "D13S3_CACHE", os.path.join(tempfile.gettempdir(), "d13s3-r11-cache")))
ROOT = next(p for p in pathlib.Path(__file__).resolve().parents
            if (p / "tests/layout.py").is_file())
FAILURES = []


def _key(path):
    return re.sub(r"[^A-Za-z0-9._-]", "_", path)


def api(path, paginate=False):
    """GET a REST path through `gh api`; decoded JSON, or None plus a failure.

    `paginate` walks `&page=N` itself and returns the list of page bodies:
    `gh --paginate` follows the Link header, whose `repositories/<id>/...` form
    this seat's proxy refuses (HTTP 403), so it failed on every second page."""
    if paginate:
        pages = []
        for n in range(1, 60):
            d = api(f"{path}{'&' if '?' in path else '?'}page={n}")
            if d is None:
                return None
            pages.append(d)
            items = d if isinstance(d, list) else next(
                (v for v in d.values() if isinstance(v, list)), [])
            if len(items) < 100:
                break
        return pages
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (_key(path) + ".json")
    if f.exists() and f.stat().st_size:
        return json.loads(f.read_text())
    cmd = ["gh", "api", path]
    p = None
    for attempt in range(4):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            f.write_text(p.stdout)
            return json.loads(p.stdout)
        if "rate limit" in (p.stderr or "").lower() or "50" in (p.stderr or "")[:40]:
            time.sleep(10 * (attempt + 1))
            continue
        break
    FAILURES.append((path, ((p.stderr if p else "") or "").strip()[:200]))
    return None


WORKER_CPU = [0.0]
_LOCK = threading.Lock()


def pmap(fn, items, workers=8):
    """Map over a thread pool; each task's thread CPU is summed into WORKER_CPU
    so the footer prints the contract's residual thread_factor."""
    def run(x):
        c0 = time.thread_time()
        try:
            return fn(x)
        finally:
            with _LOCK:
                WORKER_CPU[0] += time.thread_time() - c0
    with cf.ThreadPoolExecutor(workers) as ex:
        return list(ex.map(run, items))


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args),
                          capture_output=True, text=True).stdout


def utc(ts):
    d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return d.astimezone(datetime.timezone.utc).replace(microsecond=0) \
        .isoformat().replace("+00:00", "Z")


def t(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def first_parent(ref=BASELINE):
    """[(sha, committer_utc, nparents, subject)] oldest first, first-parent of ref."""
    out = []
    for line in git("log", "--first-parent", "--reverse",
                    "--format=%H%x09%cI%x09%P%x09%s", ref).splitlines():
        sha, ci, parents, subj = line.split("\t", 3)
        out.append((sha, utc(ci), len(parents.split()), subj))
    return out


def window_merges():
    """[(sha, utc)] first-parent merge commits whose committer date is in [W0, W1]."""
    return [(s, c) for s, c, np_, _ in first_parent() if np_ == 2 and W0 <= c <= W1]


def pr_of(sha):
    """The merged pull request `/commits/<sha>/pulls` returns for a merge commit."""
    d = api(f"repos/{REPO}/commits/{sha}/pulls")
    if d is None:
        return None
    hit = [p for p in d if (p.get("merge_commit_sha") == sha)] or \
          [p for p in d if p.get("merged_at")]
    return hit[0] if hit else {}


def check_runs(sha, all_attempts=False):
    """The commit's check-runs listing; `all_attempts` adds `filter=all` (re-run attempts)."""
    q = "&filter=all" if all_attempts else ""
    d = api(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100{q}", paginate=True)
    if d is None:
        return None
    return [c for page in d for c in page.get("check_runs", [])]


def pr_commits(num):
    d = api(f"repos/{REPO}/pulls/{num}/commits?per_page=100", paginate=True)
    if d is None:
        return None
    return [c["sha"] for page in d for c in page]


def dur(c):
    """Seconds of a CONCLUDED run; a skipped run's negative span counts 0."""
    if not c.get("conclusion") or not c.get("started_at") or not c.get("completed_at"):
        return 0.0
    return max(0.0, (t(c["completed_at"]) - t(c["started_at"])).total_seconds())


def result(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def footer():
    result("api_failures", len(FAILURES))
    for path, err in FAILURES[:20]:
        print(f"  API FAILURE {path}: {err}", file=sys.stderr)
    # contention-immune counts; the contract's three fields, quoted not gated
    pc, tc = time.process_time(), time.thread_time()
    result("worker_thread_cpu", round(WORKER_CPU[0], 2), "s")
    result("thread_factor", round((pc - WORKER_CPU[0]) / tc, 3) if tc else 1.0)
    result("load1", round(os.getloadavg()[0], 2))
    swp = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swp = int(line.split()[1])
    except OSError:
        pass
    result("swapins", swp)
    result("cache_dir", str(CACHE))
    result("baseline_sha", BASELINE)
    result("window", f"{W0}..{W1}")
