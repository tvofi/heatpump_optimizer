#!/usr/bin/env python3
"""The bounded retry of GitHub READS for the seat's Python instruments (R10-FLY-GH-READ-RETRY).

    printf '%s' "$stderr" | python3 tools/audit/seat/gh_read.py --classify   # exit 0: transient

`self_test()` runs inside record_row.py's self-test, which CI runs; this file
has no self-test entry point of its own to wire.

One unretried read killed train 8 (`the head commit at <sha> could not be
read: Get "https://api.github.com/...": net/http...`, merge_train.py's own
read) and record_row.py's push run (`HTTP Error 500`). The rule is
`app_push.sh`'s read-back rule, stated once in `INSTRUMENTS.md`: 4 reads,
settling READ_SLEEP_S * 3^(n-1), 5/15/45 s, and only on a failure a later read
can ride out -- a transport error, HTTP 5xx, 429, or a 403 whose status line
names the secondary rate limit. Every other failure -- 401, a permission 403,
404, 422, an unclassified one -- refuses after its one call, and so does a read
that answers but answers wrong: those are judged by the callers, after a
COMPLETED read, and never reach this loop. Writes are never retried: `is_read`
lets only a `gh api` GET and `gh pr view` through.

A failure that names its own wait (Retry-After, or, on a rate-limit response
-- a 429, or a 403 naming a rate limit -- a spent bucket's `x-ratelimit-reset`) is read again no sooner than that wait, and a named wait
beyond the schedule's longest settle refuses at once, naming it: a spent hourly
bucket is not transient, and the loop never sleeps out an hour. Any other
status refuses or retries by its code alone, whatever bucket it carries.

`tools/pr/app_approve.sh`'s `gh_transient` is this classifier's bash twin;
its self-test drives both over its alternatives table and compares them.
"""
from __future__ import annotations

import email.utils
import http.client
import re
import sys
import time
import urllib.error
from typing import Callable

READ_TRIES = 4
READ_SLEEP_S = 5
#: The schedule's longest settle, 45 s: a failure naming a longer wait refuses.
WAIT_CAP_S = READ_SLEEP_S * 3 ** (READ_TRIES - 2)

#: `gh api`'s status line (`gh: Bad Gateway (HTTP 502)`), app_approve.sh's sed.
GH_STATUS = re.compile(r"^gh: (.*\()?HTTP (?P<code>[0-9]{3})\)?$")
#: Every other gh command's (`HTTP 502: Bad Gateway (https://api.github.com/graphql)`):
#: `gh pr view` reads over GraphQL, which app_approve.sh never calls.
GO_STATUS = re.compile(r"^HTTP (?P<code>[0-9]{3})(: .*)? \(https?://[^ ]+\)$")
#: A transport failure: Go's `Get "https://...": ` (`Post` is `gh pr view`'s
#: GraphQL query, a read), or gh's `error connecting to `.
TRANSPORT = re.compile(r'^(Get|Post) "https?://[^"]*": |^error connecting to ')
SECONDARY = "secondary rate limit"
#: What a 403 names when it is a rate-limit response, primary or secondary.
RATE_LIMIT = "rate limit"
#: The `gh api` flags that make it POST unless a method says otherwise: a
#: short one alone or attached (`-fbody=x`), a long one alone or with `=`.
SHORT_FIELD_FLAGS = ("-f", "-F")
LONG_FIELD_FLAGS = ("--field", "--raw-field", "--input")


def http_transient(code: int, line: str) -> bool:
    """Whether a later read may ride out an HTTP failure, given its status line."""
    if 500 <= code <= 599 or code == 429:
        return True
    return code == 403 and SECONDARY in line.lower()


def gh_transient(text: str) -> bool:
    """gh's output on a failed read -> True when another read may ride it out.

    The last whole status line decides: it is the response gh read last. With
    none, a transport line on any line does."""
    status = None
    for line in text.splitlines():
        m = GH_STATUS.search(line) or GO_STATUS.search(line)
        if m:
            status = (int(m.group("code")), line)
    if status is not None:
        return http_transient(*status)
    return any(TRANSPORT.search(line) for line in text.splitlines())


def gh_wait(text: str) -> float | None:
    """`retry`'s classifier for gh output: gh prints no headers, so no wait is named."""
    return 0.0 if gh_transient(text) else None


def rate_limited(code: int, line: str) -> bool:
    """Whether an HTTP failure is a rate-limit response, given its status line:
    a 429, or a 403 naming a rate limit, primary or secondary. Only these are
    read for a bucket: GitHub sends the bucket headers on every response, so a
    404 that spends the last request carries `remaining: 0` as well."""
    return code == 429 or (code == 403 and RATE_LIMIT in line.lower())


def named_wait(headers, now: float, spent: bool) -> float | None:
    """The wait (s) a response names: Retry-After, or, when `spent` (a
    rate-limit response with no request left), the bucket's reset. One already
    past is negative, which the schedule's settle outweighs."""
    after = headers.get("Retry-After") or ""
    if after.isdigit():
        return float(after)
    try:
        return email.utils.parsedate_to_datetime(after).timestamp() - now
    except ValueError:  # no Retry-After, or one that is not an HTTP date
        pass
    reset = headers.get("x-ratelimit-reset") or ""
    if spent and reset.isdigit():
        return int(reset) - now
    return None


def urllib_wait(failure: BaseException, now: Callable[[], float] = time.time) -> float | None:
    """`retry`'s classifier for urllib: an HTTPError by its status and message,
    and by its bucket only when those make it a rate-limit response; a
    connection-level failure as transport; anything else refuses."""
    if isinstance(failure, urllib.error.HTTPError):
        headers = failure.headers or {}
        try:
            body = failure.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 -- an unreadable body is no message
            body = ""
        line = f"{failure.reason} {body}"
        spent = rate_limited(failure.code, line) and headers.get("x-ratelimit-remaining") == "0"
        wait = named_wait(headers, now(), spent)
        if spent:
            return wait  # a spent bucket: only its reset, never the schedule
        if not http_transient(failure.code, line):
            return None
        return wait or 0.0
    if isinstance(failure, (urllib.error.URLError, http.client.HTTPException,
                            ConnectionError, TimeoutError)):
        return 0.0
    return None


def retry(attempt, wait_for, sleep, note=lambda line: None):
    """Run `attempt` under the read rule -> (value, failure, attempts, why).

    `attempt()` -> (value, failure); a None failure is an answer. `wait_for`
    -> None for a refusal, else the least wait (s) the failure names (0: none).
    `why` is "" for an answer or a refusal at once, else what stopped the loop."""
    n, delay = 0, READ_SLEEP_S
    while True:
        n += 1
        value, failure = attempt()
        if failure is None:
            return value, None, n, ""
        wait = wait_for(failure)
        if wait is None:
            return value, failure, n, "" if n == 1 else f"(after {n} attempts)"
        if wait > WAIT_CAP_S:
            return value, failure, n, f"(it names a {wait:.0f} s wait, past the {WAIT_CAP_S} s cap: not retried)"
        if n == READ_TRIES:
            return value, failure, n, f"(after {n} attempts)"
        settle = max(delay, wait)
        note(f"read {n}/{READ_TRIES}: {one_line(failure)}; sleeping {settle:g}s")
        sleep(settle)
        delay *= 3


def one_line(failure) -> str:
    return " ".join(str(failure).split())


def is_read(argv) -> bool:
    """A `gh` call that reads GitHub and writes nothing: `gh api` with no
    method but GET and no field or input (gh POSTs those), or `gh pr view`."""
    argv = list(argv)
    if argv[:3] == ["gh", "pr", "view"]:
        return True
    if argv[:2] != ["gh", "api"]:
        return False
    method = "GET"
    for k, a in enumerate(argv[2:], start=2):
        if a in ("--method", "-X"):
            method = argv[k + 1] if k + 1 < len(argv) else ""
        elif a.startswith("--method="):
            method = a[len("--method="):]
        elif a.startswith("-X"):
            method = a[2:]
        elif a[:2] in SHORT_FIELD_FLAGS or a.split("=", 1)[0] in LONG_FIELD_FLAGS:
            return False
    return method.upper() == "GET"


def _alternatives(pattern: str) -> list[str]:
    """Every `|` alternative of `pattern` at every level of nesting, as source
    text; a level with one alternative contributes nothing, and a pattern
    with none at its top level is itself one alternative."""
    levels: list[list[int]] = [[-1]]  # per open group: its start and each `|`
    spans: list[list[int]] = []
    k, depth_cls = 0, False
    while k < len(pattern):
        ch = pattern[k]
        if ch == "\\":
            k += 2
            continue
        if depth_cls:
            depth_cls = ch != "]"
        elif ch == "[":
            depth_cls = True
        elif ch == "(":
            levels.append([k + (3 if pattern.startswith("(?:", k) else 0)])
        elif ch == "|":
            levels[-1].append(k)
        elif ch == ")":
            spans.append(levels.pop() + [k])
        k += 1
    spans.append(levels.pop() + [len(pattern)])
    out = []
    for cuts in spans:
        if len(cuts) > 2:
            out += [pattern[a + 1:b] for a, b in zip(cuts, cuts[1:])]
    if len(spans[-1]) == 2:
        out.append(pattern)
    return out


def ALTERNATIVES() -> set[str]:  # noqa: N802 -- named for the bash table's ALTS
    """The classifier's alternatives, derived from this file's source."""
    import ast
    from pathlib import Path
    tree = ast.parse(Path(__file__).read_text())
    out = {"default"}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "compile"
                and node.args and isinstance(node.args[0], ast.Constant)):
            out.update(_alternatives(node.args[0].value))
        elif isinstance(node, ast.FunctionDef) and node.name == "http_transient":
            out.update(str(c.value) for c in ast.walk(node)
                       if isinstance(c, ast.Constant) and type(c.value) is int)
        elif (isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "SECONDARY" for t in node.targets)
              and isinstance(node.value, ast.Constant)):
            out.add(node.value.value)
    return out


# ----------------------------------------------------------------- self-test
def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"FAIL {name}")

    def run(queue, wait_for=gh_wait):
        """Drive `retry` over a queue of failures, answered by "ok" once spent."""
        calls, sleeps, notes = [], [], []

        def attempt():
            calls.append(1)
            return ("ok", None) if not queue else (None, queue.pop(0))
        got = retry(attempt, wait_for, sleeps.append, notes.append)
        return got, len(calls), sleeps, notes

    T = 'Get "https://api.github.com/repos/o/r/commits/a": net/http: TLS handshake timeout'
    got, n, sleeps, notes = run([T])
    check("one transport failure, then an answer: answered after exactly 2 calls",
          got[:2] == ("ok", None) and n == 2 and sleeps == [5])
    check("and the settle is printed, never implied",
          notes == [f"read 1/4: {T}; sleeping 5s"])
    got, n, sleeps, _ = run(["gh: Not Found (HTTP 404)"])
    check("a 404 refuses after exactly 1 call, with no settle and no attempt count",
          got[1] == "gh: Not Found (HTTP 404)" and n == 1 and sleeps == [] and got[3] == "")
    got, n, sleeps, _ = run(["gh: HTTP 502", "gh: Not Found (HTTP 404)"])
    check("a 502 then a 404: the refusal stops it after 2 calls, naming the count",
          n == 2 and got[1] == "gh: Not Found (HTTP 404)" and got[3] == "(after 2 attempts)")
    spent = ["gh: Server Error (HTTP 500)", T, "gh: HTTP 502", "gh: Service Unavailable (HTTP 503)",
             "gh: Gateway Timeout (HTTP 504)"]
    got, n, sleeps, _ = run(list(spent))
    check("five transient failures queued, one past the budget: refused after exactly 4 calls",
          n == 4 and got[0] is None and got[3] == "(after 4 attempts)")
    check("naming the last error read, settling 5/15/45 s",
          got[1] == "gh: Service Unavailable (HTTP 503)" and sleeps == [5, 15, 45])
    got, n, _, _ = run(spent[:3])
    check("three transient failures and an answer on the budget's last read: answered (4 calls)",
          got[:2] == ("ok", None) and n == 4)
    check("(every line of the spent queue is transient, so only the budget stops it)",
          all(gh_transient(s) for s in spent))

    class Hdr(dict):
        def get(self, k, d=None):
            return {a.lower(): b for a, b in self.items()}.get(k.lower(), d)

    def hterr(code, msg="", **headers):
        e = urllib.error.HTTPError("https://api.github.com/x", code, "Error", Hdr(headers), None)
        e.read = lambda: msg.encode() if isinstance(msg, str) else msg  # the JSON body's message stands for it
        return e
    got, n, sleeps, _ = run([hterr(500, "Server Error"), hterr(500, "Server Error")], urllib_wait)
    check("record_row's shape: a 500 twice, then 200, records after exactly 3 calls",
          got[:2] == ("ok", None) and n == 3 and sleeps == [5, 15])
    got, n, _, _ = run([hterr(404, "Not Found")], urllib_wait)
    check("a urllib 404 refuses after exactly 1 call", n == 1 and got[1].code == 404)
    got, n, _, _ = run([hterr(403, "Resource not accessible by integration")], urllib_wait)
    check("a permission 403 refuses after exactly 1 call", n == 1)
    got, n, sleeps, _ = run([hterr(403, "You have exceeded a secondary rate limit", **{"Retry-After": "30"})],
                            urllib_wait)
    check("a secondary-limit 403 with Retry-After 30 settles 30 s, not 5, then answers",
          got[:2] == ("ok", None) and n == 2 and sleeps == [30])
    got, n, sleeps, _ = run([hterr(429, "", **{"Retry-After": "2"})], urllib_wait)
    check("a 429 naming less than the schedule settles the schedule's 5 s", n == 2 and sleeps == [5])
    got, n, sleeps, _ = run([hterr(429, "", **{"Retry-After": "45"})], urllib_wait)
    check("a 429 naming exactly the 45 s cap is waited out, not refused (the cap is inclusive)",
          got[:2] == ("ok", None) and n == 2 and sleeps == [45])
    got, n, sleeps, _ = run([hterr(429, "", **{"Retry-After": "3600"})], urllib_wait)
    check("a 429 naming an hour refuses at once, naming the wait (never sleeps it out)",
          n == 1 and sleeps == [] and "3600 s wait, past the 45 s cap" in got[3])
    now = float(int(time.time()))
    spent_bucket = hterr(403, "API rate limit exceeded for installation ID 1",
                        **{"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(int(now) + 1200)})
    got, n, sleeps, _ = run([spent_bucket], urllib_wait)
    check("a spent hourly bucket resetting in 20 min refuses after 1 call, naming the wait",
          n == 1 and sleeps == [] and "past the 45 s cap" in got[3])
    soon = hterr(403, "API rate limit exceeded for installation ID 1",
                **{"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(int(now) + 20)})
    got, n, sleeps, _ = run([soon], lambda f: urllib_wait(f, lambda: now))
    check("a spent bucket resetting in 20 s is read once more, after its reset (20 s, past the 5 s settle)",
          got[:2] == ("ok", None) and n == 2 and sleeps == [20])
    check("a spent bucket with no reset header is a refusal",
          urllib_wait(hterr(403, "API rate limit exceeded", **{"x-ratelimit-remaining": "0"})) is None)
    check("Retry-After as an HTTP date names the seconds until it",
          abs(named_wait(Hdr({"Retry-After": email.utils.formatdate(now + 40, usegmt=True)}), now, False) - 40) < 1.01)
    check("an unparseable Retry-After names nothing", named_wait(Hdr({"Retry-After": "soon"}), now, True) is None)
    got, n, _, _ = run([urllib.error.URLError("timed out"), ConnectionResetError(104, "reset"),
                        http.client.RemoteDisconnected("closed")], urllib_wait)
    check("URLError, a reset connection and a dropped one are transport: answered after 4 calls",
          got[:2] == ("ok", None) and n == 4)
    check("a non-transport exception (ValueError) refuses", urllib_wait(ValueError("x")) is None)
    check("the secondary-limit phrase is read in the body, past a non-UTF-8 byte",
          urllib_wait(hterr(403, b"\xff You have exceeded a secondary rate limit")) == 0.0)
    unread = urllib.error.HTTPError("https://api.github.com/x", 403, "secondary rate limit", Hdr(), None)
    unread.read = lambda: (_ for _ in ()).throw(OSError("closed"))
    check("a body that cannot be read is no message: the status line's reason still decides",
          urllib_wait(unread) == 0.0)
    past = hterr(403, "API rate limit exceeded",
                 **{"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(int(now) - 10)})
    got, n, sleeps, _ = run([past], lambda f: urllib_wait(f, lambda: now))
    check("a spent bucket whose reset is already past is read again after the schedule's 5 s",
          got[:2] == ("ok", None) and n == 2 and sleeps == [5])
    # GitHub sends the bucket headers on every response, so the request that
    # spends the last token returns its own status with `remaining: 0`: the
    # bucket is read only on a rate-limit response, never on these.
    for code, msg in ((404, "Not Found"), (401, "Bad credentials"),
                      (422, "Validation Failed"), (403, "Resource not accessible by integration"),
                      (403, "the limit on this repository's rate of forks"),
                      (404, "API rate limit exceeded")):
        got, n, sleeps, _ = run([hterr(code, msg, **{"x-ratelimit-remaining": "0",
                                                     "x-ratelimit-reset": str(int(now) + 20)})],
                                lambda f: urllib_wait(f, lambda: now))
        check(f"a {code} {msg!r} on a spent bucket resetting in 20 s refuses after exactly 1 call",
              n == 1 and sleeps == [] and got[3] == "")
    for code, msg in ((429, ""), (403, "API Rate Limit Exceeded")):
        got, n, sleeps, _ = run([hterr(code, msg, **{"x-ratelimit-remaining": "0",
                                                     "x-ratelimit-reset": str(int(now) + 20)})],
                                lambda f: urllib_wait(f, lambda: now))
        check(f"a rate-limit {code} {msg!r} on a spent bucket waits out its 20 s reset, then answers",
              got[:2] == ("ok", None) and n == 2 and sleeps == [20])
    got, n, sleeps, _ = run([hterr(500, "Server Error", **{"x-ratelimit-remaining": "0",
                                                           "x-ratelimit-reset": str(int(now) + 1200)})],
                            lambda f: urllib_wait(f, lambda: now))
    check("a 500 on a spent bucket keeps the schedule's 5 s: its reset is no wait a 500 names",
          got[:2] == ("ok", None) and n == 2 and sleeps == [5])

    # Every alternative of gh_transient, pinned from both sides: an input it
    # must classify transient and a near-miss it must refuse. ALTERNATIVES
    # derives the keys from this file's source, never a list: each `|`
    # alternative, at every level, of each module `re.compile` pattern (a
    # pattern with none is one alternative), each integer of http_transient,
    # the SECONDARY phrase, and `default` (the fall-through) -- and the table
    # must key exactly that set, each key holding both classes but `default`.
    # GO_STATUS and `Post` are this twin's own: `gh pr view` reads over
    # GraphQL, which app_approve.sh never calls; the rest are its table's rows.
    S, G = GH_STATUS.pattern, GO_STATUS.pattern
    TR1 = TRANSPORT.pattern.split("|^")[0]
    rows = [
        (S, True, "gh: HTTP 502"), (S, True, "gh: Bad Gateway (HTTP 502)"),
        (S, True, "gh: Not Found (HTTP 404)\ngh: Bad Gateway (HTTP 502)"),
        (S, False, "gh: Bad Gateway (HTTP 502)\ngh: Not Found (HTTP 404)"),
        (S, False, "warning: gh: Bad Gateway (HTTP 502)"), (S, False, "Bad Gateway (HTTP 502)"),
        (S, False, "gh: Bad Gateway (HTTP 5020)"), (S, False, "gh: Bad Gateway (HTTP 502) after 3 pages"),
        (S, True, "gh: Bad Gateway (HTTP 502)\nwarning: gh: Not Found (HTTP 404)"),
        (G, True, "HTTP 502: Bad Gateway (https://api.github.com/graphql)"),
        (G, True, "HTTP 503 (https://api.github.com/graphql)"),
        (G, True, "HTTP 404: Not Found (https://api.github.com/graphql)\nHTTP 502: Bad Gateway (http://x/graphql)"),
        (G, False, "HTTP 502: Bad Gateway (https://api.github.com/graphql)\ngh: Not Found (HTTP 404)"),
        (G, False, "HTTP 502: Bad Gateway"), (G, False, "x HTTP 502: Bad Gateway (https://a/b)"),
        (G, False, "HTTP 502: Bad Gateway (https://api.github.com/graphql) after 3 pages"),
        (G, False, "HTTP 5020: Bad Gateway (https://a/b)"), (G, False, "HTTP 502: Bad Gateway (ftp://a/b)"),
        (G, False, "HTTP 502: Bad Gateway (https://a b)"), (G, False, "HTTP 502 Bad Gateway (https://a/b)"),
        (TR1, True, 'Get "https://api.github.com/x": EOF'),
        (TR1, True, 'A new release of gh is available\nGet "http://127.0.0.1:1/x": connection refused'),
        (TR1, False, 'post-step: Get "https://api.github.com/x": EOF'), (TR1, False, 'Get "https://x" EOF'),
        (TR1, False, "Get https://x: EOF"), (TR1, False, 'Get "ftp://x": EOF'),
        (TR1, False, 'Get "https://x":EOF'),
        ("Get", True, 'Get "https://api.github.com/x": EOF'), ("Get", False, 'Gets "https://x": EOF'),
        ("Post", True, 'Post "https://api.github.com/graphql": EOF'), ("Post", False, 'Put "https://x": EOF'),
        ("Post", True, 'Post "https://api.github.com/graphql": dial tcp: i/o timeout'),
        ("Post", False, 'Patch "https://api.github.com/x": EOF'),
        ("^error connecting to ", True, "error connecting to api.github.com\ncheck your connection"),
        ("^error connecting to ", False, "proxy: error connecting to api.github.com"),
        ("^error connecting to ", False, "error connecting api.github.com"),
        ("500", True, "gh: Server Error (HTTP 500)"), ("500", False, "gh: Client Closed Request (HTTP 499)"),
        ("599", True, "gh: Network Connect Timeout Error (HTTP 599)"), ("599", False, "gh: HTTP 600"),
        ("429", True, "gh: API rate limit exceeded (HTTP 429)"), ("429", False, "gh: HTTP 428"),
        ("429", False, "gh: HTTP 430"),
        ("403", True, "gh: You have exceeded a secondary rate limit. (HTTP 403)"),
        ("403", False, "gh: Resource not accessible by integration (HTTP 403)"),
        ("403", False, "gh: You have exceeded a secondary rate limit.\ngh: Forbidden (HTTP 403)"),
        ("403", False, "gh: You have exceeded a secondary rate limit. (HTTP 401)"),
        (SECONDARY, True, "gh: You have exceeded a Secondary Rate Limit (HTTP 403)"),
        (SECONDARY, True, "HTTP 403: Request blocked by secondary rate limits (https://api.github.com/graphql)"),
        (SECONDARY, False, "gh: API rate limit exceeded for installation ID 1. (HTTP 403)"),
        (SECONDARY, False, "gh: secondary limit reached (HTTP 403)"),
        (SECONDARY, False, "gh: secondary rate exceeded (HTTP 403)"),
        (SECONDARY, False, "gh: secondary rate limit (HTTP 404)"),
        ("default", False, "something gh never says"), ("default", False, ""),
        ("default", False, "gh: Not Found (HTTP 404)\nerror connecting to api.github.com"),
    ]
    for key, want, line in rows:
        check(f"alternative {key!r}: gh_transient({line!r}) is {want}", gh_transient(line) is want)
    check("(the table keys exactly the alternatives gh_read's source holds)",
          {k for k, _, _ in rows} == ALTERNATIVES())
    check("(and every alternative but default holds both a transient input and a refused near-miss)",
          all({w for k2, w, _ in rows if k2 == k} == {True, False}
              for k in ALTERNATIVES() - {"default"}))

    for argv, want in ((["gh", "api", "repos/o/r/commits/a", "--jq", ".sha"], True),
                       (["gh", "api", "--paginate", "--slurp", "repos/o/r/pulls/1/reviews"], True),
                       (["gh", "api", "-X", "GET", "repos/o/r/x"], True),
                       (["gh", "api", "--method=GET", "repos/o/r/x"], True),
                       (["gh", "pr", "view", "1", "--json", "body"], True),
                       (["gh", "api", "--method", "POST", "repos/o/r/git/commits"], False),
                       (["gh", "api", "--method=PATCH", "repos/o/r/git/refs/x"], False),
                       (["gh", "api", "-X", "POST", "repos/o/r/actions/runs/1/rerun"], False),
                       (["gh", "api", "-XDELETE", "repos/o/r/git/refs/x"], False),
                       (["gh", "api", "--method"], False),
                       (["gh", "api", "repos/o/r/issues/1/comments", "-f", "body=x"], False),
                       (["gh", "api", "repos/o/r/x", "--input", "-"], False),
                       (["gh", "api", "repos/o/r/x", "--raw-field=a=b"], False),
                       (["gh", "pr", "merge", "1"], False), (["gh", "pr", "review", "1", "--approve"], False),
                       (["gh", "workflow", "run", "t.yml"], False), (["gh", "auth", "token"], False),
                       (["gh", "api", "-XGET", "repos/o/r/x"], True),
                       (["gh", "api", "repos/o/r/x", "-X", "GET"], True),
                       (["gh", "api", "repos/o/r/x", "-fbody=x"], False),
                       (["gh", "api", "repos/o/r/x", "-F"], False),
                       (["gh", "api", "repos/o/r/x", "-Fn=1"], False),
                       (["gh", "api", "repos/o/r/x", "--field", "a=b"], False),
                       (["gh", "api", "repos/o/r/x", "--field=a=b"], False),
                       (["gh", "api", "repos/o/r/x", "--input=f.json"], False),
                       (["gh", "alias", "set", "x", "y"], False), (["gh"], False),
                       (("gh", "pr", "view", "1"), True),
                       (["git", "fetch", "origin"], False)):
        check(f"is_read({' '.join(argv)}) is {want}", is_read(argv) is want)

    print(f"gh_read self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--classify"]:
        return 0 if gh_transient(sys.stdin.read()) else 1
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
