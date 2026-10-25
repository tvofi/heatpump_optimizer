#!/usr/bin/env python3
"""The one GitHub REST client of `tools/ci/` (R10-CI-LAYOUT P2a, contract item 1).

    from ghapi import get, post, paginate, RateLimited, ApiError
    python3 -I tools/ci/ghapi.py --self-test

Every other module under `tools/ci/` is decision code over JSON that takes an
injected `get`/`post` of exactly these signatures; this is the only module
there that imports urllib (contract item 2), stdlib only.

    get(path, params=None) -> Resp       Resp = (status: int, headers: dict, json)
    get(path, params, headers)           headers: extra request headers (alert_list's
                                         SARIF `Accept`); additive, the contract's form stands
    post(path, body=None)  -> Resp
    paginate(path, params) -> list       every item of every page, Link-followed

A GET retries a 5xx twice (RETRY_5XX backoffs) before answering. A non-2xx
answer is returned, never raised, so the caller names it -- except a
RATE LIMIT (A1 item 4): a 403 or 429 whose body says the rate limit was
exceeded raises `RateLimited`, carrying `reset_epoch` from `X-RateLimit-Reset`
(else now + `Retry-After`), so no caller can read it as an ordinary red and no
hook re-runs before the reset. GitHub words the primary limit "API rate limit
exceeded" and the secondary one "You have exceeded a secondary rate limit":
both are matched. `paginate` raises `ApiError` on any non-200 page. The token
is GITHUB_TOKEN, else GH_TOKEN.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
RETRY_5XX = (2, 6)      # GET only: the backoffs, in seconds, before each retry of a 5xx answer
MAX_PAGES = 50          # 5000 items at per_page=100: far past any head's runs; a Link loop ends here
_NEXT = re.compile(r'<([^>]+)>;\s*rel="next"')


class RateLimited(Exception):
    def __init__(self, path: str, reset_epoch: int, message: str = ""):
        super().__init__(f"{path}: rate limited until {reset_epoch} ({message})")
        self.path, self.reset_epoch = path, reset_epoch


class ApiError(Exception):
    def __init__(self, path: str, status: int, message: str = ""):
        super().__init__(f"{path}: HTTP {status} {message}".rstrip())
        self.path, self.status = path, status


def _open(req):
    """The transport; the self-test swaps it for a fake."""
    return urllib.request.urlopen(req, timeout=30)


def _rate_limited(path: str, status: int, headers: dict, raw: bytes) -> None:
    text = raw.decode("utf-8", "replace").lower()
    if status in (403, 429) and "rate limit" in text and "exceed" in text:
        h = {k.lower(): v for k, v in headers.items()}
        reset = h.get("x-ratelimit-reset")
        if reset is None or not str(reset).isdigit():
            retry = str(h.get("retry-after", "60"))
            reset = int(time.time()) + (int(retry) if retry.isdigit() else 60)
        raise RateLimited(path, int(reset), text[:120])


def _request(method: str, path: str, params=None, body=None, headers=None):
    url = path if path.startswith("http") else f"{API}/{path.lstrip('/')}"
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "hpo-tools-ci")
    for k, v in (headers or {}).items():          # replaces a default of the same name
        req.add_header(k, v)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with _open(req) as r:
            status, headers, raw = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, headers, raw = e.code, dict(e.headers or {}), e.read() or b""
    _rate_limited(path, status, headers, raw)
    try:
        doc = json.loads(raw) if raw else None
    except ValueError:
        doc = None
    return status, headers, doc


def _sleep(seconds: float) -> None:
    """The backoff; the self-test swaps it for a recorder."""
    time.sleep(seconds)


def get(path: str, params=None, headers=None):
    """A 5xx is GitHub's transient (M-5b: a gate FAILed on one HTTP 502), so a GET retries it
    after each backoff in RETRY_5XX and then returns what it got; any other status, a rate limit
    included, answers at once. A POST is never retried."""
    resp = _request("GET", path, params, headers=headers)
    for nap in RETRY_5XX:
        if resp[0] < 500:
            break
        _sleep(nap)
        resp = _request("GET", path, params, headers=headers)
    return resp


def post(path: str, body=None):
    return _request("POST", path, body=body)


def paginate(path: str, params=None, get=get) -> list:
    """Every item of every page. A page that is an object contributes its one
    list-valued member (`workflow_runs`, `jobs`, ...)."""
    out: list = []
    url, query = path, dict(params or {}, per_page=100)
    for _ in range(MAX_PAGES):
        status, headers, doc = get(url, query)
        if status != 200:
            raise ApiError(path, status, (doc or {}).get("message", "") if isinstance(doc, dict) else "")
        if isinstance(doc, dict):
            lists = [v for v in doc.values() if isinstance(v, list)]
            if len(lists) != 1:
                raise ApiError(path, status, "no single list in the page")
            doc = lists[0]
        out += doc or []
        nxt = _NEXT.search({k.lower(): v for k, v in headers.items()}.get("link", ""))
        if not nxt:
            return out
        url, query = nxt.group(1), None
    raise ApiError(path, 200, f"more than {MAX_PAGES} pages")


def self_test() -> int:
    global _open
    n, fails = 0, 0

    def check(name, got, want):
        nonlocal n, fails
        n += 1
        if got != want:
            fails += 1
            print(f"FAIL {name}: got {got!r}, want {want!r}")

    class Fake:
        def __init__(self, status, body, headers=None):
            self.status, self._body, self.headers = status, body, headers or {}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self._body

    seen = []

    def serve(status, body, headers=None):
        def fake(req):
            seen.append(req)
            if status >= 400:
                raise urllib.error.HTTPError(req.full_url, status, "x", headers or {}, _Body(body))
            return Fake(status, body, headers)
        return fake

    class _Body:
        def __init__(self, b):
            self.b = b

        def read(self, *a):
            return self.b

        def close(self):
            pass

    saved, env = _open, {k: os.environ.pop(k, None) for k in ("GITHUB_TOKEN", "GH_TOKEN")}
    try:
        os.environ["GH_TOKEN"] = "tok"
        _open = serve(200, b'{"a": 1}')
        check("200 parses", get("repos/o/r", {"x": 1}), (200, {}, {"a": 1}))
        check("query string", seen[-1].full_url, f"{API}/repos/o/r?x=1")
        check("token from GH_TOKEN", seen[-1].get_header("Authorization"), "Bearer tok")
        check("default Accept", seen[-1].get_header("Accept"), "application/vnd.github+json")
        get("x", None, {"Accept": "application/sarif+json"})
        check("an extra header replaces the default", seen[-1].get_header("Accept"), "application/sarif+json")
        _open = serve(403, b'{"message": "API rate limit exceeded for installation ID 1"}', {"X-RateLimit-Reset": "1700000000"})
        try:
            get("repos/o/r/pulls/1")
            check("rate limit raises", "returned", "raised")
        except RateLimited as e:
            check("rate limit raises, reset from the header", e.reset_epoch, 1700000000)
        _open = serve(429, b'{"message": "You have exceeded a secondary rate limit"}', {"Retry-After": "30"})
        try:
            get("x")
            check("secondary limit raises", "returned", "raised")
        except RateLimited as e:
            check("secondary limit: reset from Retry-After", 25 <= e.reset_epoch - int(time.time()) <= 31, True)
        _open = serve(403, b'{"message": "Resource not accessible by integration"}')
        check("ordinary 403 is returned, not raised", get("x")[0], 403)
        _open = serve(404, b"")
        check("empty body", get("x"), (404, {}, None))
        pages = iter([Fake(200, b'{"total_count": 3, "jobs": [1, 2]}', {"Link": f'<{API}/p2?page=2>; rel="next"'}),
                      Fake(200, b'{"total_count": 3, "jobs": [3]}')])
        _open = lambda req: (seen.append(req), next(pages))[1]  # noqa: E731
        check("paginate follows Link", paginate("p", {"q": 1}), [1, 2, 3])
        check("paginate's next page is the Link URL", seen[-1].full_url, f"{API}/p2?page=2")
        _open = serve(404, b'{"message": "boom"}')
        try:
            paginate("p")
            check("paginate raises on a bad page", "returned", "raised")
        except ApiError as e:
            check("paginate raises on a bad page", e.status, 404)
        # A transient 5xx on a GET is retried, twice, with a short backoff (R10-CI-LAYOUT P2 step
        # 11a: M-5b's gate FAILed on one HTTP 502, and a 5xx on the newest run's gate is red until
        # the next event, since the sweep re-runs only older reds).
        global _sleep
        saved_sleep, naps = _sleep, []
        _sleep = naps.append
        try:
            seq = iter([502, 200])
            calls = []

            def flaky(req):
                calls.append(req)
                st = next(seq)
                if st >= 400:
                    raise urllib.error.HTTPError(req.full_url, st, "x", {}, _Body(b'{"message": "Server Error"}'))
                return Fake(st, b'{"ok": true}')
            _open = flaky
            check("a 502 then a 200 on a GET answers the 200", get("repos/o/r/actions/runs/1/jobs")[0], 200)
            check("after one retry", len(calls), 2)
            check("and a backoff before it", len(naps) >= 1 and all(0 < t <= 10 for t in naps), True)
            calls.clear()
            _open = lambda req: (calls.append(req), serve(404, b"")(req))[1]  # noqa: E731
            check("a 404 is not retried (null control)", (get("x")[0], len(calls)), (404, 1))
            calls.clear()
            _open = lambda req: (calls.append(req), serve(503, b"")(req))[1]  # noqa: E731
            check("a 5xx that persists is returned after two retries, not looped", (get("x")[0], len(calls)), (503, 3))
            calls.clear()
            _open = lambda req: (calls.append(req), serve(502, b"")(req))[1]  # noqa: E731
            check("a POST is never retried (a re-run request is not repeated)", (post("x")[0], len(calls)), (502, 1))
        finally:
            _sleep = saved_sleep
        _open = serve(200, b"{}")
        post("repos/o/r/actions/jobs/9/rerun")
        check("post method", seen[-1].get_method(), "POST")
    finally:
        _open = saved
        for k, v in env.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v
    print(f"ghapi self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    print(__doc__.strip().splitlines()[2], file=sys.stderr)
    sys.exit(2)
