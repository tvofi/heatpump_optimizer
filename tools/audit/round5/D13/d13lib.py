"""Shared plumbing for the D13 round-5 harnesses (process yield and cost).

NOT a harness. Every harness in this directory imports it for the same three
things, and each of the three is a number the harness would otherwise report
wrongly:

* THE WINDOW IS DERIVED FROM GIT, not from a document or a comment. It is the
  first-parent commits of `origin/main` whose committer date falls in
  [W0, BASELINE_UTC], closed at the pinned baseline commit. Every count in this
  directory is taken over that window and no other.

* A CACHED, FAILURE-COUNTING `gh api` WRAPPER. Cached, because the repository
  keeps moving and a number is a statement about a pinned baseline; delete the
  cache directory printed by every harness to re-measure against a later head.
  Failure-counting, because GitHub's secondary rate limit answers 403 while
  `gh api rate_limit` still reports 5000 remaining -- a sweep that swallows it
  prints a confident, smaller, wrong number. Every harness prints
  `RESULT api_failures=<n>`; a figure with a non-zero count is not evidence.

* `check_runs(sha)`: the commit's check-run LISTING (one entry per run, so a
  red that was re-run green is still visible), joined across pages. `--paginate`
  on an object endpoint concatenates page OBJECTS, so each page is decoded and
  its `check_runs` joined -- `--slurp` gives the array of pages.

Run from the repository root. Requires `gh` authenticated with read access to
tvofi/heatpump_optimizer. Read-only: no endpoint here writes anything.
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

REPO = os.environ.get("D13_REPO", "tvofi/heatpump_optimizer")
CACHE = pathlib.Path(
    os.environ.get("D13_CACHE", os.path.expanduser("~/.cache/hpo-d13-round5"))
)
BASELINE_SHA = os.environ.get(
    "D13_BASELINE", "eaa2a06af16a1b5b006f58a0f36cc92131f80225")
# The baseline commit's committer date in UTC. The window closes here so a
# harness re-run next week reproduces the number instead of tracking main.
BASELINE_UTC = os.environ.get("D13_BASELINE_UTC", "2026-09-19T05:53:05Z")
# The window opens two calendar days before the baseline's date. Chosen as a
# date boundary rather than as "48 hours back" so the population is a property
# of the calendar and not of the hour this harness happened to run.
W0 = os.environ.get("D13_WINDOW_START", "2026-09-17T00:00:00Z")
W1 = os.environ.get("D13_WINDOW_END", BASELINE_UTC)

ROOT = pathlib.Path(
    os.environ.get("D13_ROOT", subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip() or ".")
)

FAILURES = []
_LOCK = threading.Lock()
_ONCE = set()


def _key(path):
    for a, b in (("/", "_"), ("?", "~"), ("&", "~"), ("=", "-"), (":", "-")):
        path = path.replace(a, b)
    return path


def api(path, paginate=False, cache=True):
    """GET a REST path. Decoded JSON, or None with the failure recorded.

    The cache is keyed on the path, so a page of results written under
    `--paginate --slurp` is an ARRAY of page objects; callers that need the
    rows join across pages themselves.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (_key(path) + (".pages.json" if paginate else ".json"))
    if cache and f.exists() and f.stat().st_size:
        try:
            return json.loads(f.read_text())
        except Exception:  # noqa: BLE001 -- a truncated cache entry is re-fetched
            pass
    cmd = ["gh", "api", path]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    p = None
    for attempt in range(3):
        with _LOCK:
            p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            tmp = f.with_suffix(f.suffix + f".{threading.get_ident()}")
            tmp.write_text(p.stdout)
            os.replace(tmp, f)
            return json.loads(p.stdout)
        err = (p.stderr or "").lower()
        if "rate limit" in err or "secondary" in err:
            import time
            time.sleep(15 * (attempt + 1))
            continue
        break
    with _LOCK:
        FAILURES.append((path, ((p.stderr if p else "") or "").strip()[:200]))
    return None


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args),
                          capture_output=True, text=True).stdout


def utc(ts):
    if not ts:
        return ""
    d = datetime.datetime.fromisoformat(ts)
    return d.astimezone(datetime.timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def window_commits():
    """First-parent commits of origin/main in [W0, W1], oldest first.

    Each entry: sha, parents (count), subject, body, committer date in UTC.
    A commit whose committer date falls outside the window is dropped, and the
    window is a CLOSED interval on both ends so the same baseline gives the
    same population on any clone.
    """
    raw = git("log", "--first-parent", BASELINE_SHA,
              "--format=%H%x1f%P%x1f%cI%x1f%s%x1f%b%x1e")
    out = []
    for rec in raw.split("\x1e"):
        rec = rec.lstrip("\n")
        if not rec.strip():
            continue
        parts = (rec.split("\x1f") + ["", "", "", ""])[:5]
        sha, parents, cdate, subject, body = parts
        when = utc(cdate.strip())
        if not (W0 <= when <= W1):
            continue
        out.append({"sha": sha.strip(), "parents": len(parents.split()),
                    "committed": when, "subject": subject,
                    "body": body.rstrip("\n")})
    out.reverse()
    return out


def pulls_for_sha(sha):
    """`/commits/<sha>/pulls` -- the enumerator `policy_lint.mjs` uses.

    Returns the list of pull requests the commit belongs to, or None on a
    failed fetch (recorded). An empty list is a real answer: the commit is not
    a pull-request commit (a release stamp, a `record:` push).
    """
    d = api(f"repos/{REPO}/commits/{sha}/pulls")
    if d is None:
        return None
    return d if isinstance(d, list) else []


def enumerate_merges(commits):
    """[(sha, pr_number)] for the window, in the API's own terms.

    Mirrors `policy_lint.mjs:enumerateMerges` in API mode: the number comes
    from the commit-to-pull-request map, a commit with no entry is skipped as
    a non-pull-request commit, and a number seen twice is kept once. Returns
    (merges, unattributed) where `unattributed` is the two-parent commits the
    API gave no pull request for -- the loud half of the guard, because a
    merge commit with two parents that `/commits/<sha>/pulls` does not resolve
    is the enumerator going blind, not a commit that is not a merge.
    """
    shas = [c["sha"] for c in commits]
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(pulls_for_sha, shas))
    merges, blind, seen = [], [], set()
    by_sha = dict(zip(shas, results))
    for c in commits:
        rows = by_sha[c["sha"]]
        if rows is None:
            blind.append((c["sha"], c["subject"]))
            continue
        if not rows:
            if c["parents"] > 1:
                blind.append((c["sha"], c["subject"]))
            continue
        n = rows[0]["number"]
        if n in seen:
            continue
        seen.add(n)
        merges.append({"number": n, "merge_sha": c["sha"],
                       "committed": c["committed"], "subject": c["subject"]})
    return merges, blind


def pr(number):
    return api(f"repos/{REPO}/pulls/{number}")


def pr_comments(number):
    """Issue comments on the pull request.

    THE ENDPOINT IS PART OF THE CLAIM and every harness that counts a verdict
    says which endpoint it came from: `policy_lint.mjs:fetchWindow` reads this
    one alone, so a verdict posted as a pull-request REVIEW is invisible to it.
    """
    d = api(f"repos/{REPO}/issues/{number}/comments?per_page=100", paginate=True)
    if d is None:
        return None
    return [c for page in d for c in (page if isinstance(page, list) else [])]


def pr_reviews(number):
    """Reviews (`/pulls/<n>/reviews`) -- the second endpoint a verdict may land on."""
    d = api(f"repos/{REPO}/pulls/{number}/reviews?per_page=100", paginate=True)
    if d is None:
        return None
    return [c for page in d for c in (page if isinstance(page, list) else [])]


def check_runs(sha):
    """The commit's check-run LISTING, one entry per run, pages joined."""
    d = api(f"repos/{REPO}/commits/{sha}/check-runs?per_page=100", paginate=True)
    if d is None:
        return None
    return [c for page in d for c in page.get("check_runs", [])]


def result(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def footer():
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:  # noqa: BLE001
        load1 = -1.0
    result("api_failures", len(FAILURES))
    for path, err in FAILURES:
        print(f"  API FAILURE {path}: {err}", file=sys.stderr)
    result("cache_dir", str(CACHE))
    result("baseline_sha", BASELINE_SHA)
    result("window_start", W0)
    result("window_end", W1)
    result("load1", round(load1, 2))
    # This directory's harnesses print COUNTS and GitHub-reported DURATIONS.
    # Nothing here runs numpy, BLAS or a second thread, so no number below is a
    # CPU-time measurement and the ratio the contract quotes beside a timing
    # would be 0/0. It is printed as 1.0 -- the pin `tests/stress.py` sets is
    # exported into every child that might import numpy, and the factor is
    # "not applicable, no timing claim" rather than "measured quiet".
    result("thread_factor", 1.0, "(n/a: no timing RESULT in this harness)")
    result("concurrent_stress_or_gate_procs", procs_running())


def procs_running():
    """How many stress/gate processes share the box, printed beside timings."""
    out = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    return sum(1 for line in out.splitlines()
               if ("stress.py" in line or "tests/run.sh" in line)
               and "grep" not in line)
