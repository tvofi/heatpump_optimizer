"""D13 / round 9 / seat s1 -- shared GitHub-API plumbing. Not a harness.

A cached, failure-counting, READ-ONLY (GET) REST client over urllib, because
this container has no `gh` binary (d11lib.py shells out to `gh api`). Token
from $GH_TOKEN or $GITHUB_TOKEN; proxy from the environment (urllib honours
HTTPS_PROXY). The raw cache lives under $D13_CACHE (default
$TMPDIR/hpo-d13-r9-s1); the harnesses read the committed, derived snapshot
`window.json.gz` beside this file, so a judge re-runs them offline and exactly.
`fetch_window.py` (re)builds the snapshot.

Every figure a harness prints is paired with RESULT api_failures=<n>: a
secondary rate limit answers 403 while the quota query says plenty remains,
and a swallowed 403 prints a confident, smaller number.
"""

import gzip
import hashlib
import json
import re
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

REPO = os.environ.get("D13_REPO", "tvofi/heatpump_optimizer")
HERE = pathlib.Path(__file__).resolve().parent
SNAPSHOT = HERE / "window.json.gz"
CACHE = pathlib.Path(os.environ.get(
    "D13_CACHE", os.path.join(tempfile.gettempdir(), "hpo-d13-r9-s1")))
BASELINE_SHA = "1936d5ca72a06556eeed4e8e5bf3dea520e517e1"
WINDOW_SINCE = os.environ.get("D13_SINCE", "v6.6.0")
WINDOW_HEAD = os.environ.get("D13_HEAD", BASELINE_SHA)
FAILURES = []


def _token():
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""


def _get(url):
    """One GET through curl (the container's CA bundle and proxy are curl's
    defaults; CPython 3.14's strict X.509 mode rejects the proxy CA, and
    relaxing verification is not an option). Raises HTTPError-like on >=400."""
    hdr = tempfile.NamedTemporaryFile(delete=False)
    hdr.close()
    try:
        p = subprocess.run(
            ["curl", "-sS", "--max-time", "60", "-D", hdr.name,
             "-H", "Accept: application/vnd.github+json",
             "-H", f"Authorization: Bearer {_token()}",
             "-H", "X-GitHub-Api-Version: 2022-11-28",
             "-w", "\n%{http_code}", url],
            capture_output=True, text=True, check=False)
        headers = open(hdr.name).read()
    finally:
        os.unlink(hdr.name)
    if p.returncode != 0:
        raise OSError(p.stderr.strip()[:200])
    body, _, code = p.stdout.rpartition("\n")
    code = int(code or 0)
    if code >= 400:
        raise urllib.error.HTTPError(url, code, body[:200], None, None)
    link = ""
    for line in headers.splitlines():
        if line.lower().startswith("link:"):
            link = line.split(":", 1)[1]
    return json.loads(body), link


def _next(link):
    for part in link.split(","):
        if 'rel="next"' in part:
            nxt = part[part.index("<") + 1:part.index(">")]
            # GitHub's next link uses /repositories/<id>/...; this container's
            # egress policy answers that form 403, so ask by owner/name.
            return re.sub(r"/repositories/\d+/", f"/repos/{REPO}/", nxt)
    return None


def api(path, paginate=False):
    """GET a REST path (under /repos/... etc). paginate=True returns a list of
    page payloads (decode each; an object endpoint's pages are NOT one array).
    None on failure, recorded in FAILURES."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1((path + str(paginate)).encode()).hexdigest()
    f = CACHE / (key + ".json")
    if f.exists() and f.stat().st_size:
        return json.loads(f.read_text())
    url = "https://api.github.com/" + path.lstrip("/")
    pages = []
    err = None
    while url:
        for attempt in range(4):
            try:
                data, link = _get(url)
                break
            except urllib.error.HTTPError as e:
                err = f"HTTP {e.code}"
                if e.code in (403, 429, 502, 503):
                    time.sleep(15 * (attempt + 1))
                    continue
                data = None
                break
            except Exception as e:  # network
                err = repr(e)[:120]
                time.sleep(5)
                data = None
        else:
            data = None
        if data is None:
            FAILURES.append((path, err))
            return None
        pages.append(data)
        url = _next(link) if paginate else None
    out = pages if paginate else pages[0]
    f.write_text(json.dumps(out))
    return out


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          check=False).stdout


def load_snapshot():
    with gzip.open(SNAPSHOT, "rt") as fh:
        return json.load(fh)


def result(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def footer(api_failures):
    """Contention-immune counts: GitHub-reported data, no local timing.
    load1/thread_factor/swapins are printed because the harness contract asks
    for them at the end of every measurement; none of these numbers is a
    local timing, so none depends on them."""
    result("api_failures", api_failures)
    try:
        result("load1", round(os.getloadavg()[0], 2))
    except OSError:
        result("load1", "na")
    pc, tc = time.process_time(), time.thread_time()
    result("thread_factor", round(pc / tc, 3) if tc else 1.0)
    swap = "na"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swap = int(line.split()[1])
    except OSError:
        pass
    result("swapins", swap)
    result("baseline_sha", BASELINE_SHA)


def thread_pin():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(k, "1")


if __name__ == "__main__":
    sys.exit("r9lib.py is a library; run fetch_window.py or a harness")
