#!/usr/bin/env python3
"""The bounded retry of GitHub READS for the seat's Python instruments (R10-FLY-GH-READ-RETRY).

    printf '%s' "$stderr" | python3 tools/audit/seat/gh_read.py --classify   # exit 0: transient
    printf '%s' "$stderr" | python3 tools/audit/seat/gh_read.py --classify-git   # git's, exit 0: transient
    python3 tools/audit/seat/gh_read.py --git-retry git fetch -q origin main     # git under run_git_retry

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

THE BULK READ (the corpus mirror, tools/audit/seat/corpus_mirror.py; tvofi
2026-11-15: a scan of every pull request, comment and run must not starve the
shared token). Three things, each used by that one stream:
  read_conditional  one `gh api -i` read under this file's retry, sent with
                    `If-None-Match` when an ETag is cached. A 304 is
                    `unchanged`, an answer and never a failure -- gh exits
                    non-zero on it, so it is read off the status line before
                    the classifier sees the output -- and costs nothing
                    against the primary limit.
  budget/below_floor  `gh api rate_limit` (free) and the buckets under a
                    floor. A scan on the shared token starts a batch only
                    while core and graphql each keep FLOOR_SHARED of their
                    limit: the three existing refusers trip at 20 %, and
                    dev/audit/rca/ratelimit-recur.md records two readers
                    taking 82 % of an hour, so a scan capped at 40 % leaves
                    the train and the seats twice their refusal margin. On a
                    read-only identity of its own the floor is FLOOR_OWN.
                    An unreadable answer is below every floor.
  rate_wait         the wait a failed read names when it is a rate-limit
                    answer (a secondary limit's Retry-After, a spent bucket's
                    reset): the scan pauses at its cursor on one, whatever the
                    wait, where `retry` would refuse a long one.
BATCH reads between two budget checks and MIN_GAP_S between two reads are the
scan's pace; `is_query` admits a GraphQL document that only queries.
"""
from __future__ import annotations

import email.utils
import hashlib
import json
import os
import http.client
import re
import sys
import time
import urllib.error
from pathlib import Path
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
#: A body that is not JSON, with no status line: gh's `--jq` parsing what a
#: failing front end sent (#2579's pr-contract run 39681234360, job
#: 119504172159: `invalid character 'S' looking for beginning of value`, and a
#: sibling read a second earlier answered). GitHub's refusals are JSON, so
#: this is no refusal; a status line, when gh prints one, still decides.
NON_JSON = re.compile(r"^invalid character '.{1,6}' looking for beginning of value$")
SECONDARY = "secondary rate limit"
#: What a 403 names when it is a rate-limit response, primary or secondary.
RATE_LIMIT = "rate limit"
#: The `gh api` flags that make it POST unless a method says otherwise: a
#: short one alone or attached (`-fbody=x`), a long one alone or with `=`.
SHORT_FIELD_FLAGS = ("-f", "-F")
LONG_FIELD_FLAGS = ("--field", "--raw-field", "--input")


#: The bulk read's pace and floors (the docstring argues them).
BATCH = 200
MIN_GAP_S = 1.0
FLOOR_SHARED = 0.60
FLOOR_OWN = 0.10
GATED = ("core", "graphql")


#: R10-TRAIN-MERGE-LOOP-2: a `git fetch`/`git push` is GitHub transport too.
#: git's own stderr, measured: smart-HTTP and socket failures a later call rides out.
GIT_TRANSIENT = re.compile(
    r"returned error: 5\d\d|RPC failed; HTTP 5\d\d|unexpected disconnect while reading sideband"
    r"|early EOF|the remote end hung up unexpectedly|Connection reset by peer|Could not resolve host"
    r"|Failed to connect|Operation timed out|GnuTLS recv error|SSL_ERROR_SYSCALL|unable to access.*timed? ?out")
#: A refusal or a rejected update: never retried, whatever else the output says.
GIT_REFUSED = re.compile(
    r"non-fast-forward|\[rejected\]|Permission denied|Authentication failed|\b40[34]\b"
    r"|couldn't find remote ref|protected branch hook declined|stale info|remote rejected")


def git_transient(output: str) -> bool:
    """git's stderr on a failed fetch/push -> True when another call may ride it out."""
    return not GIT_REFUSED.search(output) and bool(GIT_TRANSIENT.search(output))


GIT_TRIES = 3


def run_git_retry(run, argv, sleep, log=lambda line: None, **kw):
    """`run(argv)` for a git fetch/push, repeated up to GIT_TRIES times (settling 5/15 s)
    while the failure is git_transient; a rejection or a success answers at once.
    merge_train.py's fetches and pushes, and `--git-retry`'s shell callers, share it."""
    for n in range(1, GIT_TRIES + 1):
        code, o = run(argv, **kw)
        if not code or n == GIT_TRIES or not git_transient(o):
            return code, o
        log(f"{' '.join(argv)[:120]}: git {n}/{GIT_TRIES}: {' '.join(o.split())[:120]}")
        sleep(READ_SLEEP_S * 3 ** (n - 1))


def _run_captured(argv):
    import subprocess
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def http_transient(code: int, line: str) -> bool:
    """Whether a later read may ride out an HTTP failure, given its status line."""
    if 500 <= code <= 599 or code == 429:
        return True
    return code == 403 and SECONDARY in line.lower()


def gh_transient(text: str) -> bool:
    """gh's output on a failed read -> True when another read may ride it out.

    The last whole status line decides: it is the response gh read last. With
    none, a transport line, or a body that did not parse as JSON, on any line does."""
    status = None
    for line in text.splitlines():
        m = GH_STATUS.search(line) or GO_STATUS.search(line)
        if m:
            status = (int(m.group("code")), line)
    if status is not None:
        return http_transient(*status)
    return any(TRANSPORT.search(line) or NON_JSON.search(line) for line in text.splitlines())


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


#: One page of a paged list, GitHub's maximum, and the walk's bound: past
#: MAX_PAGES full pages the read refuses rather than return a truncated list.
PER_PAGE = 100
MAX_PAGES = 100


def read_pages(read, path: str, key: str = "", per_page: int = PER_PAGE, max_pages: int = MAX_PAGES):
    """Every item of the paged list at <path> -> (code, items, why); items is
    None and why the failure on a failed, unparseable or unbounded walk.

    Page by explicit `page=N`, never `gh api --paginate`: that follows the Link
    header, which names `repositories/<id>/...`, and a cloud seat's proxy
    answers that URL 403 (S14-CLOUD-CLASSIFY-PAGINATE: `merge_train.py
    classify` exited 2 on it). A short page ends the walk. `read` is the
    caller's runner -- `merge_train`'s carries this file's retry rule -- and
    <key> names the list in an object page (`check_runs`), "" an array page."""
    sep = "&" if "?" in path else "?"
    items: list = []
    for n in range(1, max_pages + 1):
        code, out = read(["gh", "api", f"{path}{sep}per_page={per_page}&page={n}",
                          "--jq", f".{key}[]" if key else ".[]"])
        if code:
            return code, None, out
        try:
            page = [json.loads(x) for x in out.splitlines() if x.strip()]
        except ValueError:
            return 1, None, f"page {n} of {path} is not JSON: {one_line(out)[-120:]}"
        items += page
        if len(page) < per_page:  # mut:short-page
            return 0, items, ""
    return 1, None, f"{path}: more than {max_pages} pages of {per_page}: refused, not truncated"


# ----------------------------------------------------- conditional (ETag) reads
# (no module-level re.compile here: ALTERNATIVES() reads those as the bash twin's table)
#: A conditional read the server answers 304 costs no core-bucket call (P596 measured
#: five of them moving `used` by 0, five plain reads by 6). The stored ETag and body sit
#: under the caller's state directory ($HPO_STATE_DIR, default ~/.local/state/hpo), one file
#: per path, shared by every process reading under that same directory; a process under
#: another state directory keeps its own store and pays its own first plain read per path.


def etag_dir() -> Path:
    return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo") / "gh-etag"


def parse_include(out: str) -> "tuple[int | None, dict, str]":
    """`gh api -i`'s output -> (status, lower-cased headers, body); status None when the
    output holds no response status line (a transport failure, or an error gh printed itself)."""
    head, _, body = out.replace("\r\n", "\n").partition("\n\n")
    lines = head.splitlines()
    m = re.match(r"HTTP/\S+ (?P<code>[0-9]{3})\b", lines[0]) if lines else None
    if m is None:
        m2 = [GH_STATUS.search(x) for x in out.splitlines()]
        code = next((int(x.group("code")) for x in reversed(m2) if x), None)
        return code, {}, ""
    headers = {k.strip().lower(): v.strip() for k, _, v in (x.partition(":") for x in lines[1:])}
    return int(m.group("code")), headers, body


def _etag_file(path: str, cache: Path) -> Path:
    return cache / (hashlib.sha256(path.encode()).hexdigest()[:32] + ".json")


def conditional_get(run, path: str, cache: "Path | None" = None) -> "tuple[int, str]":
    """The body of the single-page GET at <path> -> (code, body); code != 0 is UNREADABLE and
    the body then holds gh's output. `run(argv)` -> (code, output) is the caller's runner.

    With an ETag stored for <path> the read sends If-None-Match: a 304 serves the stored
    body, a 200 replaces both. With none stored (or a stored file that does not parse) it
    is the plain read. Any other status, or a transport failure, is UNREADABLE as a plain
    read's: a stale body is never served on a failure. A page past one page is no caller's:
    it reads one page and no Link header is followed."""
    cache = cache or etag_dir()
    f = _etag_file(path, cache)
    stored = None
    try:
        got = json.loads(f.read_text())
        if isinstance(got.get("etag"), str) and isinstance(got.get("body"), str) and got["etag"]:
            stored = got
    except (OSError, ValueError, AttributeError):
        pass
    argv = ["gh", "api", "-i"] + (["-H", f"If-None-Match: {stored['etag']}"] if stored else []) + [path]
    code, out = run(argv)
    status, headers, body = parse_include(out)
    if status == 304 and stored:
        return 0, stored["body"]
    if code or status != 200:
        return code or 1, out
    etag = headers.get("etag", "")
    if etag:
        try:
            cache.mkdir(parents=True, exist_ok=True)
            tmp = f.with_name(f"{f.name}.{os.getpid()}.tmp")
            tmp.write_text(json.dumps({"etag": etag, "body": body}))
            os.replace(tmp, f)
        except OSError:
            pass  # an unwritable state dir is the plain read, never a failure
    return 0, body


def ruleset_checks(run, repo: str, name: str, cache: "Path | None" = None) -> "tuple[bool, dict]":
    """(read ok, the `required_status_checks` rule's parameters) of the ruleset called <name>,
    both reads conditional (`conditional_get`). A ruleset list holding the name other than
    once, or a body that is not the shape GitHub sends, is not read."""
    code, out = conditional_get(run, f"repos/{repo}/rulesets", cache)
    try:
        ids = [r["id"] for r in json.loads(out) if r.get("name") == name] if not code else []
        if len(ids) != 1 or not isinstance(ids[0], int):
            return False, {}
        code, out = conditional_get(run, f"repos/{repo}/rulesets/{ids[0]}", cache)
        if code:
            return False, {}
        rules = [r for r in json.loads(out)["rules"] if r.get("type") == "required_status_checks"]
    except (ValueError, TypeError, KeyError, AttributeError):
        return False, {}
    return True, (rules[0].get("parameters") or {}) if rules else {}


def required_contexts(params: dict) -> "set[str]":
    """The context names a `required_status_checks` rule's parameters require."""
    return {c["context"].strip() for c in params.get("required_status_checks") or []
            if isinstance(c, dict) and isinstance(c.get("context"), str) and c["context"].strip()}


def fake_ruleset(argv, rid: str, contexts: str, strict: "str | None" = None, name: str = "main-protect-checks"):
    """The self-tests' GitHub for the two ruleset paths: <contexts> (newline-separated, "" the
    ruleset unreadable, a 404) answered as `gh api -i`, with an ETag a matching If-None-Match
    turns into a 304 -- gh's own rc 1. The one fake both instruments' self-tests share."""
    if not contexts:
        return 1, "gh: Not Found (HTTP 404)"
    path = next(a for a in argv if a.startswith("repos/"))
    if path.endswith("/rulesets"):
        body = json.dumps([{"id": int(rid), "name": name}])
    else:
        params = {"required_status_checks": [{"context": c} for c in contexts.splitlines() if c.strip()]}
        if strict in ("true", "false"):  # anything else: the key absent, an unreadable policy
            params["strict_required_status_checks_policy"] = strict == "true"
        body = json.dumps({"rules": [{"type": "required_status_checks", "parameters": params}]})
    etag = '"' + hashlib.sha256(body.encode()).hexdigest()[:16] + '"'
    if f"If-None-Match: {etag}" in argv:
        return 1, f"HTTP/2.0 304 Not Modified\nEtag: {etag}\n\ngh: HTTP 304"
    return 0, f"HTTP/2.0 200 OK\nEtag: {etag}\nContent-Type: application/json\n\n{body}"


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


def is_query(argv) -> bool:
    """A `gh api graphql` call that only queries: every field a raw `-f`, exactly one of
    them `query=`, its document read from the line (no `@file`) and naming no mutation
    or subscription. A read by content, where `is_read` judges by method."""
    argv = list(argv)
    if argv[:3] != ["gh", "api", "graphql"]:
        return False
    rest, docs, k = argv[3:], [], 0
    while k < len(rest):
        if rest[k] != "-f" or k + 1 >= len(rest) or "=" not in rest[k + 1]:
            return False
        name, value = rest[k + 1].split("=", 1)
        if value.startswith("@"):
            return False
        if name == "query":
            docs.append(value)
        k += 2
    return len(docs) == 1 and not any(w in docs[0].lower() for w in ("mutation", "subscription"))


def parse_included(out: str):
    """`gh api -i` output -> (status, headers with lower-case names, body); (None, {}, out)
    when it opens with no status line."""
    head, _, body = out.replace("\r\n", "\n").partition("\n\n")
    lines = head.split("\n")
    first = lines[0].split()
    if len(first) < 2 or not first[0].startswith("HTTP/") or not first[1].isdigit():
        return None, {}, out
    headers = {}
    for ln in lines[1:]:
        name, colon, value = ln.partition(":")
        if colon:
            headers[name.strip().lower()] = value.strip()
    return int(first[1]), headers, body


def _included(out: str, now: float):
    """(status, body, spent, the wait the response names) of a `gh api -i` answer."""
    status, h, body = parse_included(out)
    if status is None:
        return None, out, False, None
    spent = rate_limited(status, body) and h.get("x-ratelimit-remaining") == "0"
    wait = named_wait({"Retry-After": h.get("retry-after", ""), "x-ratelimit-reset": h.get("x-ratelimit-reset", "")}, now, spent)
    return status, body, spent, wait


def included_wait(out: str, now: Callable[[], float] = time.time) -> float | None:
    """`retry`'s classifier for `gh api -i` output, which carries the headers gh's plain
    output drops: urllib_wait's rule, read off the response text."""
    status, body, spent, wait = _included(out, now())
    if status is None:
        return gh_wait(out)
    if spent:
        return wait
    if not http_transient(status, body):
        return None
    return wait or 0.0


def rate_wait(out: str, now: Callable[[], float] = time.time) -> float | None:
    """The wait (s) a failed `gh api -i` read names when it is a rate-limit answer, at
    least 0; None for any other failure. A scan pauses on it; it never sleeps it out."""
    status, body, spent, wait = _included(out, now())
    if status is None or not (rate_limited(status, body) or (status == 403 and SECONDARY in body.lower())):
        return None
    return max(wait or 0.0, 0.0)


def read_conditional(run, path: str, etag: str = "", sleep=time.sleep, note=lambda line: None,
                     now: Callable[[], float] = time.time):
    """One page under the read rule -> (state, body, etag, raw): `fresh` with the body and
    its ETag, `unchanged` (a 304 to `If-None-Match: <etag>`; the cached page stands), or
    `failed` with the last output in `raw`, for `rate_wait` and the caller's report."""
    argv = ["gh", "api", "-i", path] + (["-H", f"If-None-Match: {etag}"] if etag else [])

    def attempt():
        code, out = run(argv)
        status, h, body = parse_included(out)
        if status == 304:
            return ("unchanged", "", etag), None
        if code == 0 and status is not None and 200 <= status < 300:
            return ("fresh", body, h.get("etag", "")), None
        return None, out

    value, failure, _, _ = retry(attempt, lambda f: included_wait(f, now), sleep, note)
    if failure is None:
        return (*value, "")
    return "failed", "", etag, failure


def budget(run):
    """{bucket: (limit, remaining, reset)} from `gh api rate_limit`, which costs nothing;
    None when it cannot be read or holds no bucket."""
    code, out = run(["gh", "api", "rate_limit"])
    if code:
        return None
    try:
        res = json.loads(out).get("resources") or {}
        got = {k: (int(v["limit"]), int(v["remaining"]), int(v["reset"])) for k, v in res.items() if isinstance(v, dict)}
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
    return got or None


def below_floor(buckets, floor: float, names=GATED) -> list[str]:
    """The gated buckets with less than `floor` of their limit left; an unread budget, or
    a gated bucket it does not hold, is below every floor."""
    if not buckets:
        return ["unread"]
    return [n for n in names if n not in buckets or buckets[n][1] < floor * buckets[n][0]]


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
    # git's rule (GIT_TRANSIENT, GIT_REFUSED) is a second classifier with its
    # own table in merge_train.py's self-test; app_approve.sh's gh twin has none of it.
    git = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
           and any(getattr(t, "id", "").startswith("GIT_") for t in n.targets)}
    for node in ast.walk(tree):
        if id(node) in git:
            continue
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
                      (404, "API rate limit exceeded"), (401, "API rate limit exceeded")):
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
        (NON_JSON.pattern, True, "invalid character 'S' looking for beginning of value"),
        (NON_JSON.pattern, True, "A new release of gh is available\ninvalid character '<' looking for beginning of value"),
        (NON_JSON.pattern, True, "invalid character '\\x00' looking for beginning of value"),
        (NON_JSON.pattern, False, "jq: invalid character 'S' looking for beginning of value"),
        (NON_JSON.pattern, False, "invalid character 'S' looking for beginning of value at offset 1"),
        (NON_JSON.pattern, False, "invalid character 'S' after top-level value"),
        (NON_JSON.pattern, False, "invalid character '' looking for beginning of value"),
        (NON_JSON.pattern, False, "invalid character 'Service' looking for beginning of value"),
        (NON_JSON.pattern, False, "gh: Not Found (HTTP 404)\ninvalid character 'S' looking for beginning of value"),
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

    # git's rule (R10-TRAIN-MERGE-LOOP-2): the loop, its runner and the CLI the
    # shell callers use. merge_train.py's self-test holds the classifier's table.
    import contextlib
    import io
    outs, logs, slept = [(1, "error: RPC failed; HTTP 502"), (0, "ok")], [], []
    got = run_git_retry(lambda argv: outs.pop(0), ["git", "fetch"], slept.append, logs.append)
    check("run_git_retry: a 502 then success answers the success after one 5 s settle, logged once",
          got == (0, "ok") and slept == [5] and len(logs) == 1 and "git 1/3" in logs[0])
    code, o = _run_captured(["git", "--version"])
    check("_run_captured: git's own output comes back, with its exit code", code == 0 and o.startswith("git version"))
    for text, rc in (("fatal: unable to access 'u': The requested URL returned error: 502", 0),
                     ("! [rejected] main -> main (non-fast-forward)", 1)):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            stdin, sys.stdin = sys.stdin, io.StringIO(text)
            try:
                got = main(["--classify-git"])
            finally:
                sys.stdin = stdin
        check(f"--classify-git exits {rc} on {text[:40]!r}", got == rc)
    for argv, rc, want in ((["git", "--version"], 0, "git version"), (["git", "--no-such-flag"], 129, "unknown option")):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            got = main(["--git-retry", *argv])
        check(f"--git-retry {' '.join(argv)}: rc {rc}, git's output on {'stdout' if rc == 0 else 'stderr'}",
              got == rc and want in (out if rc == 0 else err).getvalue())
    with contextlib.redirect_stderr(io.StringIO()):
        check("--git-retry refuses an argv that is not git (usage, rc 2)", main(["--git-retry", "ls"]) == 2)

    # S14-CLOUD-CLASSIFY-PAGINATE: a paged list read by explicit page number.
    def server(sizes, key="check_runs"):
        """A stub `gh api` serving len(sizes) pages of sizes[n-1] items; any
        followed Link header (`--paginate`, or a repositories/<id> URL) is the
        cloud proxy's 403."""
        calls = []

        def read(argv):
            calls.append(argv)
            a = " ".join(argv)
            if "--paginate" in argv or "repositories/" in a:
                return 1, "gh: Forbidden (HTTP 403)"
            n = int(argv[2].rsplit("&page=", 1)[1])
            base = sum(sizes[:n - 1])
            page = [{"id": base + i} for i in range(sizes[n - 1] if n <= len(sizes) else 0)]
            jq = argv[argv.index("--jq") + 1] if "--jq" in argv else ""
            if jq not in (f".{key}[]", ".[]"):
                return 1, f"unexpected --jq {jq!r}"
            return 0, "".join(json.dumps(x) + "\n" for x in page)
        return read, calls

    read, calls = server([2, 2, 1])
    code, items, why = read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs", per_page=2)
    check("a three-page answer reads every item, in order, in 3 reads",
          code == 0 and [x["id"] for x in items] == [0, 1, 2, 3, 4] and len(calls) == 3 and why == "")
    check("each read names its page explicitly and follows no Link header (the stub 403s one)",
          [c[2].rsplit("&page=", 1)[1] for c in calls] == ["1", "2", "3"]
          and not any("--paginate" in c for c in calls))
    read, calls = server([1])
    code, items, _ = read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs", per_page=2)
    check("null control: a one-page (short) answer makes exactly one read",
          code == 0 and len(items) == 1 and len(calls) == 1)
    read, calls = server([1])
    read_pages(read, "repos/o/r/commits/h/check-runs", "check_runs")
    check("by default a page is GitHub's maximum, 100 (the page size a short page is judged against)",
          calls[0][2] == "repos/o/r/commits/h/check-runs?per_page=100&page=1")
    read, calls = server([2, 2, 0], key="")
    code, items, _ = read_pages(read, "repos/o/r/pulls/1/reviews?state=x", per_page=2)
    check("a full last page ends on the empty page after it; a query string is extended with &",
          code == 0 and len(items) == 4 and len(calls) == 3
          and calls[0][2].startswith("repos/o/r/pulls/1/reviews?state=x&"))
    read, calls = server([2] * 9, key="")
    code, items, why = read_pages(read, "repos/o/r/x", per_page=2, max_pages=3)
    check("a walk past max_pages refuses, never truncates", code == 1 and items is None and "3 pages" in why)
    code, items, why = read_pages(lambda argv: (4, "gh: Not Found (HTTP 404)"), "repos/o/r/x")
    check("a failed read is the caller's failure: its code and its text, verbatim",
          code == 4 and items is None and why == "gh: Not Found (HTTP 404)")
    code, items, why = read_pages(lambda argv: (0, "{not json\n"), "repos/o/r/x")
    check("an unparseable page is a failure (rc 1), never an empty list",
          code == 1 and items is None and why.startswith("page 1 of repos/o/r/x is not JSON"))

    # THE BULK READ: the conditional read, the rate-limit wait, the budget and its floor.
    def inc(status, headers=(), body="", tail=""):
        return f"HTTP/2.0 {status}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in headers) + "\r\n" + body + tail

    def cond(queue, etag=""):
        """read_conditional over a queue of (code, output); a spent queue answers a 200."""
        calls, sleeps = [], []

        def run_(argv):
            calls.append(argv)
            return queue.pop(0) if queue else (0, inc(200, [("Etag", 'W/"new"')], "[1]"))
        return read_conditional(run_, "repos/o/r/issues?per_page=100&page=1", etag, sleeps.append, now=lambda: 1000.0), calls, sleeps

    got, calls, _ = cond([(0, inc(200, [("Etag", 'W/"a1"'), ("X-Ratelimit-Remaining", "4000")], '[{"n": 1}]'))])
    check("a first conditional read is fresh, with its body and ETag, and sends no If-None-Match",
          got == ("fresh", '[{"n": 1}]', 'W/"a1"', "") and calls == [["gh", "api", "-i", "repos/o/r/issues?per_page=100&page=1"]])
    got, calls, sleeps = cond([(1, inc(304, [("Etag", 'W/"a1"')], "", "gh: HTTP 304\n"))], 'W/"a1"')
    check("a 304 to the cached ETag is unchanged: an answer on the first call, though gh exits non-zero on it",
          got == ("unchanged", "", 'W/"a1"', "") and len(calls) == 1 and sleeps == []
          and calls[0][-2:] == ["-H", 'If-None-Match: W/"a1"'])
    check("null control: the same exit status with no 304 status line is a failure, not unchanged",
          cond([(1, inc(404, [], '{"message": "Not Found"}', "gh: Not Found (HTTP 404)\n"))], 'W/"a1"')[0][0] == "failed")
    got, calls, sleeps = cond([(1, inc(502, [], "", "gh: Bad Gateway (HTTP 502)\n"))])
    check("a 5xx is read again under the schedule, then answers", got[0] == "fresh" and len(calls) == 2 and sleeps == [READ_SLEEP_S])
    sec = inc(403, [("Retry-After", "7")], '{"message": "You have exceeded a secondary rate limit."}', "gh: (HTTP 403)\n")
    got, calls, sleeps = cond([(1, sec)])
    check("a secondary limit naming a short Retry-After is read again no sooner than it", got[0] == "fresh" and sleeps == [7.0])
    long_sec = sec.replace("Retry-After: 7", "Retry-After: 600")
    got, calls, sleeps = cond([(1, long_sec)])
    check("...and one naming a wait past the cap fails after its one call, with the wait readable for the scan's pause",
          got[0] == "failed" and len(calls) == 1 and sleeps == [] and rate_wait(got[3], lambda: 1000.0) == 600.0)
    spent = inc(403, [("X-Ratelimit-Remaining", "0"), ("X-Ratelimit-Reset", "4600")], '{"message": "API rate limit exceeded"}', "gh: (HTTP 403)\n")
    got, calls, sleeps = cond([(1, spent)])
    check("a spent core bucket fails after one call and names its reset as the wait",
          got[0] == "failed" and len(calls) == 1 and sleeps == [] and rate_wait(got[3], lambda: 1000.0) == 3600.0)
    got, calls, sleeps = cond([(1, spent.replace("4600", "1009"))])
    check("...while one resetting inside the schedule is read again after its reset, not refused",
          got[0] == "fresh" and len(calls) == 2 and sleeps == [9.0])
    perm = inc(403, [("X-Ratelimit-Remaining", "0"), ("X-Ratelimit-Reset", "4600")], '{"message": "Resource not accessible"}', "gh: (HTTP 403)\n")
    check("null control: a permission 403, a 404 and output with no status line name no rate-limit wait",
          rate_wait(perm, lambda: 1000.0) is None and rate_wait(inc(404, [], "{}"), lambda: 1000.0) is None
          and rate_wait("gh: Not Found (HTTP 404)", lambda: 1000.0) is None and cond([(1, perm)])[0][0] == "failed")
    check("parse_included reads the status, lower-cases header names and keeps the body; no status line gives None",
          parse_included(inc(200, [("ETag", "x"), ("Link", "<u>; rel=next")], "b\n\nc")) == (200, {"etag": "x", "link": "<u>; rel=next"}, "b\n\nc")
          and parse_included("[1]\n")[0] is None)
    rl = json.dumps({"resources": {"core": {"limit": 5000, "remaining": 3000, "reset": 9}, "graphql": {"limit": 5000, "remaining": 2999, "reset": 9},
                                   "search": {"limit": 30, "remaining": 0, "reset": 9}}})
    b = budget(lambda argv: (0, rl) if argv == ["gh", "api", "rate_limit"] else (1, ""))
    check("the budget is read from rate_limit alone, per bucket", b == {"core": (5000, 3000, 9), "graphql": (5000, 2999, 9), "search": (30, 0, 9)})
    check("a bucket exactly at the floor passes and one request under it does not; search is not gated",
          below_floor(b, FLOOR_SHARED) == ["graphql"] and below_floor({**b, "graphql": (5000, 3000, 9)}, FLOOR_SHARED) == []
          and below_floor(b, FLOOR_OWN) == [])
    check("an unreadable budget, or one missing a gated bucket, is below every floor (null control: never read as plenty)",
          budget(lambda argv: (1, "gh: (HTTP 502)")) is None and budget(lambda argv: (1, rl)) is None and budget(lambda argv: (0, "<html>")) is None
          and budget(lambda argv: (0, "{}")) is None and below_floor(None, FLOOR_OWN) == ["unread"]
          and below_floor({"core": (5000, 5000, 9)}, FLOOR_OWN) == ["graphql"])
    check("the scan's pace is declared: a positive batch and gap, and a shared floor above the own-identity floor",
          BATCH > 0 and MIN_GAP_S >= 1.0 and 0 < FLOOR_OWN < FLOOR_SHARED < 1)
    q = ["gh", "api", "graphql", "-f", "query=query($n:Int!){repository(owner:\"o\",name:\"r\"){id}}", "-f", "n=3"]
    check("is_query admits a document that only queries",
          is_query(q) and not is_read(q))
    check("...and refuses a mutation, a subscription, a document from a file, a typed field, a second document, or another path",
          not any(is_query(a) for a in (
              ["gh", "api", "graphql", "-f", "query=mutation{addComment(input:{})}"],
              ["gh", "api", "graphql", "-f", "query=subscription{x}"],
              ["gh", "api", "graphql", "-f", "query=@q.graphql"],
              ["gh", "api", "graphql", "-F", "query=query{viewer{login}}"],
              ["gh", "api", "graphql", "-f", "query=query{a}", "-f", "query=query{b}"],
              ["gh", "api", "graphql", "--input", "f.json"],
              ["gh", "api", "graphql"],
              ["gh", "api", "repos/o/r/issues", "-f", "query=query{a}"])))

    # ---- conditional reads (P596, P625): one helper, the ETag and body under the state dir
    import tempfile
    with tempfile.TemporaryDirectory() as cd:
        cache = Path(cd)
        seen: list = []
        world = {"body": '{"v": 1}', "etag": '"e1"', "rc": 0}

        def gh_(argv):
            seen.append(list(argv))
            inm = next((a for a in argv if a.startswith("If-None-Match: ")), None)
            if world["rc"]:
                return 1, "gh: Bad Gateway (HTTP 502)"
            if inm == f"If-None-Match: {world['etag']}":
                return 1, f"HTTP/2.0 304 Not Modified\nEtag: {world['etag']}\n\ngh: HTTP 304"
            return 0, f"HTTP/2.0 200 OK\r\nEtag: {world['etag']}\r\nX-A: b\r\n\r\n{world['body']}"

        P = "repos/o/r/rulesets"
        check("null control: with no stored ETag the plain read is made (no If-None-Match)",
              conditional_get(gh_, P, cache) == (0, '{"v": 1}') and not any("If-None-Match" in a for a in seen[0]))
        code, body = conditional_get(gh_, P, cache)
        check("a 304 serves the stored body, from one request that carried the stored ETag",
              (code, body) == (0, '{"v": 1}') and len(seen) == 2 and "If-None-Match: \"e1\"" in seen[1])
        world.update(body='{"v": 2}', etag='"e2"')
        check("a 200 replaces the stored body and ETag", conditional_get(gh_, P, cache) == (0, '{"v": 2}')
              and json.loads(_etag_file(P, cache).read_text()) == {"etag": '"e2"', "body": '{"v": 2}'})
        check("and the next read is the 304 of the new ETag", conditional_get(gh_, P, cache) == (0, '{"v": 2}')
              and "If-None-Match: \"e2\"" in seen[-1])
        world["rc"] = 1
        code, out = conditional_get(gh_, P, cache)
        check("any other failure is UNREADABLE, the stored body never served", code != 0 and "502" in out)
        world["rc"] = 0
        _etag_file(P, cache).write_text("{not json")
        n0 = len(seen)
        check("a corrupt stored file is the plain read", conditional_get(gh_, P, cache)[0] == 0
              and not any("If-None-Match" in a for a in seen[n0]))
        check("one stored file per path", conditional_get(gh_, P + "/7", cache)[0] == 0
              and len(list(cache.glob("*.json"))) == 2)
        check("a 304 with nothing stored is UNREADABLE, never an empty body",
              conditional_get(lambda argv: (1, "HTTP/2.0 304 Not Modified\n\ngh: HTTP 304"), "repos/o/r/x", cache)[0] != 0)
        # the ruleset reads: two reads each cold, none warm; the shared fake is the server
        calls = []

        def srv(argv):
            calls.append(argv)
            return fake_ruleset(argv, "7", "tests\nclosures\n", "true")
        with tempfile.TemporaryDirectory() as cd2:
            ok, params = ruleset_checks(srv, "o/r", "main-protect-checks", Path(cd2))
            ok2, params2 = ruleset_checks(srv, "o/r", "main-protect-checks", Path(cd2))
            check("ruleset_checks reads the required set and the strict flag",
                  ok and [c["context"] for c in params["required_status_checks"]] == ["tests", "closures"]
                  and params["strict_required_status_checks_policy"] is True and (ok2, params2) == (ok, params))
            check("a warm ruleset read serves both reads as 304s: 4 calls, the second pair conditional",
                  len(calls) == 4 and all("If-None-Match" in " ".join(c) for c in calls[2:])
                  and not any("If-None-Match" in " ".join(c) for c in calls[:2]))
            check("a ruleset by another name is not read",
                  ruleset_checks(srv, "o/r", "other", Path(cd2)) == (False, {}))
            check("an unreadable ruleset is not read", ruleset_checks(lambda a: (1, "HTTP 404"), "o/r", "x", Path(cd2)) == (False, {}))
        # the store's scope is the caller's $HPO_STATE_DIR (etag_dir), not the host
        saved = os.environ.get("HPO_STATE_DIR")
        try:
            def under(state):
                os.environ["HPO_STATE_DIR"] = str(state)
                n0 = len(seen)
                conditional_get(gh_, P)
                return any("If-None-Match" in a for a in seen[n0])
            (cache / "s1").mkdir()
            (cache / "s2").mkdir()
            cold1, warm1, other = under(cache / "s1"), under(cache / "s1"), under(cache / "s2")
            check("the ETag store is $HPO_STATE_DIR/gh-etag: a second read under the same state dir is conditional",
                  not cold1 and warm1 and etag_dir() == cache / "s2" / "gh-etag")
            check("and a read under another state dir finds nothing stored: its first read is plain", not other)
        finally:
            if saved is None:
                os.environ.pop("HPO_STATE_DIR", None)
            else:
                os.environ["HPO_STATE_DIR"] = saved
    print(f"gh_read self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--classify"]:
        return 0 if gh_transient(sys.stdin.read()) else 1
    if argv == ["--classify-git"]:
        return 0 if git_transient(sys.stdin.read()) else 1
    if argv[:1] == ["--git-retry"] and argv[1:2] == ["git"]:
        code, o = run_git_retry(_run_captured, argv[1:], time.sleep,
                                lambda line: print(f"gh_read: {line}", file=sys.stderr))
        (sys.stderr if code else sys.stdout).write(o)
        return code
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
