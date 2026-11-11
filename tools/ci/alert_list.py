#!/usr/bin/env python3
"""The code-scanning alerts behind a pull request's merge ref, one red each.

pr-contract's "List the red checks" step lists the alerts of the analyses its
code-scanning wait matched (owner ruling R-10, option B; DESIGN-P2.md 4.3 step 5).
Pure decision code over JSON: every read goes through an injected
`get(path, params=None, headers=None) -> (status, headers, json)` (the P2a
interface contract, item 2). This module imports no HTTP client, and a
`RateLimited` raised by `get` propagates unchanged: it is never an empty list.
`headers` is the one addition to the contract's signature: the SARIF read needs
`Accept`. `bind` is the P2a glue's binding to ghapi.get, which takes the same
optional `headers`; this module's paths are relative to repos/<repo>/.

  step 4: for each leg S uploaded, the newest entry of
      code-scanning/analyses?ref=R&tool_name=CodeQL (sort and direction pinned,
      PINS below) whose category is "/language:<leg>" and whose commit_sha is M, the
      `sha=` token of S's run-name (title_sha). Its `id` is the match.
  step 5: GET code-scanning/analyses/<id> with Accept: application/sarif+json; every
      result carries properties["github/alertNumber"]. Subtract the alerts open on
      refs/heads/<base> when `base_repeats`. Then read each remaining alert itself
      (no ref) and drop it when its state is dismissed (N5-2). Each one left is a
      line "code-scanning alert <n> (<rule id>)", the text `--red` must carry.
  Any failed read (an analysis or alert answering 404 included), a result with no
  alert number, or a leg with no match FAILs closed.

Never `alerts?ref=R&state=open`: that listing follows the NEWEST analysis per
category, so a newer analysis at R that is not M's silently drops M's alerts.

  python3 -I tools/ci/alert_list.py --self-test
  python3 -I tools/ci/alert_list.py --pins        # the listing's pinned sort/direction
"""
from __future__ import annotations

import argparse
import os
import sys

ACCEPT_SARIF = "application/sarif+json"
PINS = {"sort": "created", "direction": "desc"}      # N5-3: newest first, stated, not defaulted
LISTING = "code-scanning/analyses"


class ReadFailed(Exception):
    pass


def title_sha(display_title):
    """S's github.sha from its run-name: the token after 'sha='."""
    toks = [t[4:] for t in display_title.split() if t.startswith("sha=")]
    if len(toks) != 1 or not toks[0]:
        raise ReadFailed(f"no sha= token in {display_title!r}")
    return toks[0]


def read(get, path, what, params=None, headers=None):
    status, _, body = get(path, params, headers) if headers else get(path, params)
    if status != 200:
        raise ReadFailed(f"{what}: HTTP {status}")
    return body


def pages(get, path, params):
    """Every page of a paginated listing; a failed page fails the whole read."""
    out, page = [], 1
    while True:
        body = read(get, path, f"{path} page {page}", {**params, "per_page": 100, "page": page})
        if not isinstance(body, list):
            raise ReadFailed(f"{path} page {page}: not a list")
        out += body
        if len(body) < 100:
            return out
        page += 1


def match(get, ref, sha, legs):
    """Step 4: {leg: analysis id}; a leg with no entry yet is absent."""
    rows = pages(get, LISTING, {"ref": ref, "tool_name": "CodeQL", **PINS})
    out = {}
    for leg in legs:
        hit = next((a for a in rows if a.get("category") == f"/language:{leg}" and a.get("commit_sha") == sha), None)
        if hit is not None:
            out[leg] = hit["id"]
    return out


def reds(get, ref, sha, legs, base, base_repeats):
    """(ok, [red names] or reason) for the alerts of the uploaded legs at (ref, sha)."""
    try:
        if not legs:
            return True, []
        ids = match(get, ref, sha, legs)
        missing = [leg for leg in legs if leg not in ids]
        if missing:
            return False, f"no analysis at {ref} with commit_sha {sha} for leg(s) {', '.join(missing)}"
        found = {}
        for leg in legs:
            sarif = read(get, f"{LISTING}/{ids[leg]}", f"analysis {ids[leg]} ({leg})", headers={"Accept": ACCEPT_SARIF})
            if not isinstance(sarif, dict):
                raise ReadFailed(f"analysis {ids[leg]} ({leg}): not an object")
            for run in sarif.get("runs", []):
                for res in run.get("results", []):
                    n = (res.get("properties") or {}).get("github/alertNumber")
                    if not isinstance(n, int):
                        raise ReadFailed(f"analysis {ids[leg]} ({leg}): a result of {res.get('ruleId')} has no alert number")
                    found[n] = res.get("ruleId", "?")
        on_base = set()
        if base_repeats:
            rows = pages(get, "code-scanning/alerts", {"ref": f"refs/heads/{base}", "tool_name": "CodeQL", "state": "open"})
            on_base = {a["number"] for a in rows}
        out = []
        for n in sorted(found):
            if n in on_base:
                continue
            alert = read(get, f"code-scanning/alerts/{n}", f"alert {n}")      # N5-2: alert-level, no ref
            if not isinstance(alert, dict):
                raise ReadFailed(f"alert {n}: not an object")
            if alert.get("state") != "dismissed":
                out.append(f"code-scanning alert {n} ({found[n]})")
        return True, out
    except ReadFailed as e:
        return False, f"FAIL closed: {e}"


def bind(get, repo):
    """ghapi.get as this module calls it: the path under repos/<repo>/, headers forwarded."""
    return lambda path, params=None, headers=None: get(f"repos/{repo}/{path}", params, headers)


def main(argv, get):
    ap = argparse.ArgumentParser(prog="alert_list.py")
    ap.add_argument("--ref", required=True, help="the merge ref, refs/pull/<N>/merge")
    ap.add_argument("--title", required=True, help="the code run's display title, carrying sha=<M>")
    ap.add_argument("--base", required=True)
    ap.add_argument("--base-repeats", action="store_true")
    ap.add_argument("--legs", default="", help="comma-separated legs S uploaded")
    a = ap.parse_args(argv)
    try:
        sha = title_sha(a.title)
    except ReadFailed as e:
        print(f"FAIL closed: {e}")
        return 1
    ok, got = reds(get, a.ref, sha, [x for x in a.legs.split(",") if x], a.base, a.base_repeats)
    print("\n".join(got) if ok else got)
    return 0 if ok else 1


# ---- the self-test: synthetic API responses ----------------------------------------------
R, M, M2, BASE = "refs/pull/77/merge", "m1", "m2", "main"
TITLE = f"CI code pr=77 base={BASE} sha={M}"
PLANT = "py/code-injection"
LEGS = ("actions", "javascript-typescript", "python")


class FakeRateLimited(Exception):
    pass


def sarif(*results):
    return {"runs": [{"tool": {"driver": {"name": "CodeQL"}},
                      "results": [{"ruleId": rule, "properties": {"github/alertNumber": n}} for n, rule in results]}]}


def alert(n, rule, state):
    return {"number": n, "rule": {"id": rule}, "state": state}


def an(aid, leg, commit):
    return {"id": aid, "category": f"/language:{leg}", "commit_sha": commit, "ref": R}


THREE = [an(13, "python", M), an(12, "javascript-typescript", M), an(11, "actions", M)]
EMPTY = {12: sarif(), 11: sarif()}


def world(analyses, sarifs, alerts, alerts_base=(), fail=(), limited=(), base_fails=False):
    """get(path, params, headers) over one fixture. Refuses (422/400) a listing without the
    pinned sort/direction, an alert read carrying a ref, and a SARIF read without Accept."""
    def get(path, params=None, headers=None):
        params = params or {}
        if any(f in path for f in fail):
            return 500, {}, None
        if any(f in path for f in limited):
            raise FakeRateLimited(path)
        if path.startswith(f"{LISTING}/"):
            aid = int(path.rsplit("/", 1)[1])
            ok = (headers or {}).get("Accept") == ACCEPT_SARIF and aid in sarifs
            return (200, {}, sarifs[aid]) if ok else (404, {}, None)
        if path.startswith("code-scanning/alerts/"):
            n = int(path.rsplit("/", 1)[1])
            hit = [a for a in alerts if a["number"] == n]
            return (400, {}, None) if "ref" in params else ((200, {}, hit[0]) if hit else (404, {}, None))
        page = params["page"]
        if base_fails and params.get("ref") == f"refs/heads/{BASE}":
            return 500, {}, None
        if path == LISTING:
            if {k: params.get(k) for k in PINS} != PINS:
                return 422, {}, None
            rows = list(analyses)
        else:
            rows = list(alerts_base) if params.get("ref") == f"refs/heads/{BASE}" else []
        return 200, {}, rows[(page - 1) * 100: page * 100]
    return get


def by_ref_reading(rows, sha, legs):
    """The rejected reading (the null control of the binding): open alerts on R, filtered to M."""
    return sorted(f"code-scanning alert {a['number']} ({a['rule']['id']})" for a in rows
                  if a["state"] == "open" and a["commit_sha"] == sha and a["leg"] in legs)


def cases():
    m = title_sha(TITLE)
    one = [f"code-scanning alert 7 ({PLANT})"]
    plant = {13: sarif((7, PLANT)), **EMPTY}
    yield "P  planted python-only finding is listed", world(THREE, plant, [alert(7, PLANT, "open")]), {}, True, one
    yield "N  null: the no-alert fixture lists nothing", world(THREE, {13: sarif(), **EMPTY}, []), {}, True, []
    yield ("C  carried: an edit run keyed on S's sha= token lists the same alert",
           world(THREE, plant, [alert(7, PLANT, "open")]), dict(M=title_sha("CI code pr=77 base=main sha=m1")), True, one)
    yield ("D  a newer analysis at R (m2) lacks the finding: listed from M's analysis",
           world([an(14, "python", M2)] + THREE, {13: sarif((7, PLANT)), 14: sarif(), **EMPTY}, [alert(7, PLANT, "open")]),
           {}, True, one)
    yield ("S  a newer CodeQL analysis at the SAME commit: step 4 takes the newest at M",
           world([an(15, "python", M)] + THREE, {15: sarif((7, PLANT)), 13: sarif(), **EMPTY}, [alert(7, PLANT, "open")]),
           {}, True, one)
    yield ("X  N5-2 plant: the alert dismissed (alert-level read): not listed",
           world(THREE, plant, [alert(7, PLANT, "dismissed")]), {}, True, [])
    yield ("X2 only the dismissed alert of two is dropped",
           world(THREE, {13: sarif((3, "py/old"), (7, PLANT)), **EMPTY}, [alert(3, "py/old", "dismissed"), alert(7, PLANT, "open")]),
           {}, True, one)
    both = world(THREE, {13: sarif((3, "py/old"), (7, PLANT)), **EMPTY},
                 [alert(3, "py/old", "open"), alert(7, PLANT, "open")], alerts_base=[alert(3, "py/old", "open")])
    yield "B  also open on the base, merge ref repeats base alerts: subtracted", both, dict(base_repeats=True), True, one
    yield ("B0 the same, merge ref does not repeat them: listed", both, {}, True,
           ["code-scanning alert 3 (py/old)"] + one)
    old = [an(1000 + i, "python", M2) for i in range(100)]
    yield ("G  pagination: M's analysis on page 2 of the listing is matched",
           world(old + THREE, plant, [alert(7, PLANT, "open")]), {}, True, one)
    yield "L  no leg uploaded: nothing read, nothing listed", world([], {}, []), dict(legs=()), True, []
    yield "F1 the SARIF read fails: FAIL closed", world(THREE, plant, [], fail=("analyses/13",)), {}, False, None
    yield ("F2 the analysis id answers 404 (case 7): FAIL closed",
           world(THREE, {**EMPTY}, [alert(7, PLANT, "open")]), {}, False, None)
    yield ("F3 the alert-level read fails: FAIL closed", world(THREE, plant, [], fail=("alerts/7",)), {}, False, None)
    yield ("F4 the alert answers 404: FAIL closed", world(THREE, plant, [alert(8, PLANT, "open")]), {}, False, None)
    yield ("F5 a result without an alert number: FAIL closed",
           world(THREE, {13: {"runs": [{"results": [{"ruleId": PLANT, "properties": {}}]}]}, **EMPTY}, []), {}, False, None)
    yield "F6 a leg uploaded but no analysis at M: FAIL closed", world(THREE[1:], EMPTY, []), {}, False, None
    yield ("F7 the base listing fails while it is used: FAIL closed",
           world(THREE, plant, [alert(7, PLANT, "open")], base_fails=True), dict(base_repeats=True), False, None)


def self_test() -> int:
    n = bad = 0

    def check(label, good, detail=""):
        nonlocal n, bad
        n += 1
        bad += not good
        print(f"{'ok ' if good else 'BAD'} {label}{detail}")

    for label, get, kw, want_ok, want in cases():
        ok, got = reds(get, R, kw.get("M", M), kw.get("legs", LEGS), BASE, kw.get("base_repeats", False))
        check(label, ok == want_ok and (not ok or got == want), f": {'listed ' + str(got) if ok else got}")
    # N5-3: the listing carries the pinned sort and direction, and --pins prints them.
    seen = []
    pinned = world(THREE, {13: sarif(), **EMPTY}, [])
    reds(lambda p, q=None, h=None: (seen.append((p, q)), pinned(p, q, h))[1], R, M, LEGS, BASE, False)
    lst = [q for p, q in seen if p == LISTING]
    check("T1 the analyses listing carries the pinned sort and direction",
          bool(lst) and all(q["sort"] == "created" and q["direction"] == "desc" for q in lst), f" {PINS}")
    check("T2 the alert-level read carries no ref",
          all("ref" not in (q or {}) for p, q in seen if p.startswith("code-scanning/alerts/")))
    # RateLimited is not a FAIL string and not an empty list: it propagates.
    for tag in ("analyses/13", "alerts/7"):
        try:
            reds(world(THREE, {13: sarif((7, PLANT)), **EMPTY}, [alert(7, PLANT, "open")], limited=(tag,)), R, M, LEGS, BASE, False)
            check(f"R  RateLimited at {tag} propagates", False)
        except FakeRateLimited:
            check(f"R  RateLimited at {tag} propagates", True)
    # the rejected reading: with M's analysis outranked by a newer one at R, it drops the alert
    rows = [{"number": 7, "rule": {"id": PLANT}, "state": "fixed", "commit_sha": M2, "leg": "python"}]
    check("A  null control: the rejected by_ref reading lists nothing where the analysis reading lists the alert",
          by_ref_reading(rows, M, LEGS) == [] and reds(world([an(14, "python", M2)] + THREE,
          {13: sarif((7, PLANT)), 14: sarif(), **EMPTY}, [alert(7, PLANT, "open")]), R, M, LEGS, BASE, False)[1] != [])
    calls = []
    bind(lambda *a: calls.append(a) or (200, {}, {}), "o/r")(f"{LISTING}/13", None, {"Accept": ACCEPT_SARIF})
    check("B  bind: the path is under repos/<repo>/ and the Accept header is forwarded",
          calls == [(f"repos/o/r/{LISTING}/13", None, {"Accept": ACCEPT_SARIF})], f" {calls}")
    check("M  main: title without sha= FAILs closed", main(["--ref", R, "--title", "no token", "--base", BASE], None) == 1)
    print(f"alert_list self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    if sys.argv[1:] == ["--pins"]:
        print(f"{LISTING} " + " ".join(f"{k}={v}" for k, v in PINS.items()))
        sys.exit(0)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ghapi                                     # the one REST client; bound here only for the command line
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("FAIL closed: GITHUB_REPOSITORY is unset")
        sys.exit(1)
    sys.exit(main(sys.argv[1:], bind(ghapi.get, repo)))
