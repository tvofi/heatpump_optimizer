"""D13 / round 8 / seat s1 -- REST transport for the round-4 D11 instruments.

Not a harness. `tools/audit/round4/D11/d11lib.py` shells out to `gh api` (and
GraphQL for `merged_prs`); this box has no `gh` binary and the agent proxy
refuses GraphQL, so this module supplies a drop-in `api(path, paginate)` over
GET-only urllib with `GITHUB_TOKEN`/`GH_TOKEN`, installs it as `d11lib.api`, and
keeps d11lib's two properties: CACHED (under D13S1_CACHE, default
/home/claude/audit-r8/tmp/D13-s1/ghcache) and FAILURE-COUNTING (appends to
`d11lib.FAILURES`, so `d11lib.footer()` prints `api_failures`). A paginated
call returns a LIST OF PAGES, as `gh api --paginate --slurp` does, so
`d11lib.check_runs` runs unchanged. Read-only: no method but GET is issued.
"""
import json
import os
import pathlib
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "round4", "D11")))
import d11lib as L  # noqa: E402

REPO = L.REPO
CACHE = pathlib.Path(os.environ.get("D13S1_CACHE", "/home/claude/audit-r8/tmp/D13-s1/ghcache"))
L.CACHE = CACHE
L.BASELINE_SHA = os.environ.get("D13S1_BASELINE", "cdf82daabcfe3777d98b31489f36df5555ec9d82")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
CALLS = [0]


def _get(url):
    req = urllib.request.Request(url, method="GET", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "hpo-audit-r8-d13-s1"})
    for attempt in range(4):
        try:
            CALLS[0] += 1
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode()), r.headers.get("Link", "")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 502, 503) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(5)
                continue
            raise


def api(path, paginate=False, cache=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (L._key(path) + (".page.json" if paginate else ".json"))
    if cache and f.exists() and f.stat().st_size:
        return json.loads(f.read_text())
    url = "https://api.github.com/" + path.lstrip("/")
    try:
        if not paginate:
            data, _ = _get(url)
        else:
            data = []
            nxt = url
            while nxt:
                page, link = _get(nxt)
                data.append(page)
                nxt = None
                for part in link.split(","):
                    if 'rel="next"' in part:
                        nxt = part[part.index("<") + 1:part.index(">")]
    except Exception as e:  # noqa: BLE001
        L.FAILURES.append((path, str(e)[:200]))
        return None
    f.write_text(json.dumps(data))
    return data


L.api = api


def flat(pages, key=None):
    """Join a --slurp page list: arrays concatenate, objects contribute `key`."""
    out = []
    for p in pages or []:
        out.extend(p.get(key, []) if key else p)
    return out
