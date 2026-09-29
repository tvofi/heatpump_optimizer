"""D13 / round 8 / verifier v1 -- GET-only GitHub REST reader with its own cache. Not a harness.

Cache: $D13V1_CACHE (default /home/claude/audit-r8/tmp/D13-v1/v1cache). Failures are
counted in FAILURES and every harness prints api_failures. No method but GET.
"""
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

REPO = "tvofi/heatpump_optimizer"
CACHE = pathlib.Path(os.environ.get("D13V1_CACHE", "/home/claude/audit-r8/tmp/D13-v1/v1cache"))
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
FAILURES = []


def _get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
        "User-Agent": "hpo-audit-r8-d13-v1"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode()), r.headers.get("Link", "")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            if i == 3 or (isinstance(e, urllib.error.HTTPError) and e.code not in (403, 429, 502, 503)):
                raise
            time.sleep(5 * (i + 1))


def pages(path):
    """Every element of a paginated list endpoint, joined."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(path.encode()).hexdigest() + ".json")
    if f.exists():
        return json.loads(f.read_text())
    out, url = [], "https://api.github.com/" + path
    try:
        while url:
            data, link = _get(url)
            out.extend(data)
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part[part.index("<") + 1:part.index(">")]
    except Exception as e:  # noqa: BLE001
        FAILURES.append((path, str(e)[:200]))
        return []
    f.write_text(json.dumps(out))
    return out


def one(path):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (hashlib.sha1(path.encode()).hexdigest() + ".one.json")
    if f.exists():
        return json.loads(f.read_text())
    try:
        data, _ = _get("https://api.github.com/" + path)
    except Exception as e:  # noqa: BLE001
        FAILURES.append((path, str(e)[:200]))
        return None
    f.write_text(json.dumps(data))
    return data


def R(k, v):
    print(f"RESULT {k}={json.dumps(v) if isinstance(v, (dict, list)) else v}")
