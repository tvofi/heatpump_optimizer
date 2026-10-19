#!/usr/bin/env python3
"""Revision 4, owner ruling R-10 (option B): pr-contract lists the open code-scanning
alerts of the analyses 4.3's step 4 matched. DESIGN-P2.md 4.3, step 5.

This is the reference implementation the fixer ports into pr-contract's step "List
the red checks", as gate_model.py is for the gate. It reads only what a callback
returns, so the self-test drives it over synthetic API responses.

  step 4 (unchanged, rev2): for each leg S uploaded, the newest entry of
      code-scanning/analyses?ref=R&tool_name=CodeQL whose category is
      "/language:<leg>" and whose commit_sha is M (S's sha= token). Its `id` is the
      match.
  step 5 (rev4): for each match, GET code-scanning/analyses/<id> with
      Accept: application/sarif+json. Every result carries
      properties["github/alertNumber"]; those numbers are the alerts of M's analysis,
      and nothing newer at R can change them. Subtract the alerts R lists as
      `dismissed` (a person closed them; the only way an alert of M's analysis stops
      being open without a new commit). Subtract the alerts open on refs/heads/<base>
      only when U6 shows the merge ref repeats them (`base_repeats`). Each remaining
      alert is one red, named "code-scanning alert <n> (<rule id>)", which the body
      must answer in `## Red checks` as it answers a red check.
  Any read that fails, a result with no alert number, or a leg with no match FAILs
  the step closed.

Why the analysis and not `alerts?ref=R&state=open` (the `by_ref` ablation below):
the alerts listing has no sha or analysis filter, and an alert's state and
most_recent_instance on R follow the NEWEST analysis per category there. A newer
analysis at R that is not M's (an old-base code run that R-11 lets finish after a
retarget's, a hand upload) makes it disagree with M's: an alert it no longer reports
reads `fixed` (case D), and one it repeats carries the newer commit, so a
`commit_sha == M` filter drops it (case D2). Both are silent misses.

  python3 -I measure/rev/alert_list.py self-test      exit 0 iff every case is ok
"""
from __future__ import annotations

import sys

ACCEPT_SARIF = "application/sarif+json"


class ReadFailed(Exception):
    pass


def title_sha(display_title):
    """S's github.sha from its run-name (DESIGN-P2.md 2.2): the token after 'sha='."""
    toks = [t[4:] for t in display_title.split() if t.startswith("sha=")]
    if len(toks) != 1 or not toks[0]:
        raise ReadFailed(f"no sha= token in {display_title!r}")
    return toks[0]


def pages(get, path):
    """Every page of a paginated listing; a failed page fails the whole read."""
    out, page = [], 1
    while True:
        status, body = get(f"{path}&per_page=100&page={page}", None)
        if status != 200 or not isinstance(body, list):
            raise ReadFailed(f"{path} page {page}: HTTP {status}")
        out += body
        if len(body) < 100:
            return out
        page += 1


def match(get, R, M, legs):
    """Step 4: {leg: analysis id}. A leg with no entry yet is unmatched (step 4 polls
    until every leg matches or its bound passes; this returns the one read)."""
    rows = pages(get, f"code-scanning/analyses?ref={R}&tool_name=CodeQL")   # newest first
    out = {}
    for leg in legs:
        hit = next((a for a in rows if a.get("category") == f"/language:{leg}" and a.get("commit_sha") == M), None)
        if hit is not None:
            out[leg] = hit["id"]
    return out


def reds(get, R, M, legs, base, base_repeats, ablate=()):
    """(ok, [red names] or reason) for the alerts of S's uploaded legs at (R, M)."""
    try:
        if not legs:
            return True, []
        if "by_ref" in ablate:      # the rejected reading: open alerts on R, filtered to M and the legs
            cats = {f"/language:{leg}" for leg in legs}
            rows = pages(get, f"code-scanning/alerts?ref={R}&tool_name=CodeQL&state=open")
            return True, sorted(f"code-scanning alert {a['number']} ({a['rule']['id']})" for a in rows
                                if a["most_recent_instance"]["commit_sha"] == M
                                and a["most_recent_instance"]["category"] in cats)
        ids = match(get, R, M, legs)
        missing = [leg for leg in legs if leg not in ids]
        if missing:
            return False, f"no analysis at {R} with commit_sha {M} for leg(s) {', '.join(missing)}"
        found = {}
        for leg in legs:
            status, sarif = get(f"code-scanning/analyses/{ids[leg]}", ACCEPT_SARIF)
            if status != 200 or not isinstance(sarif, dict):
                raise ReadFailed(f"analysis {ids[leg]} ({leg}): HTTP {status}")
            for run in sarif.get("runs", []):
                for res in run.get("results", []):
                    n = (res.get("properties") or {}).get("github/alertNumber")
                    if not isinstance(n, int):
                        raise ReadFailed(f"analysis {ids[leg]} ({leg}): a result of {res.get('ruleId')} has no alert number")
                    found[n] = res.get("ruleId", "?")
        dismissed = {a["number"] for a in pages(get, f"code-scanning/alerts?ref={R}&tool_name=CodeQL&state=dismissed")}
        on_base = set()
        if base_repeats:
            on_base = {a["number"] for a in pages(get, f"code-scanning/alerts?ref=refs/heads/{base}&tool_name=CodeQL&state=open")}
        return True, [f"code-scanning alert {n} ({found[n]})" for n in sorted(found) if n not in dismissed | on_base]
    except ReadFailed as e:
        return False, f"FAIL closed: {e}"


# ---- the self-test: synthetic API responses --------------------------------------------
R, M, M2, BASE = "refs/pull/77/merge", "m1", "m2", "main"
TITLE = f"CI code pr=77 base={BASE} sha={M}"


def sarif(*results):
    return {"runs": [{"tool": {"driver": {"name": "CodeQL"}},
                      "results": [{"ruleId": rule, "properties": {"github/alertNumber": n}} for n, rule in results]}]}


def alert(n, rule, state, commit, leg="python"):
    return {"number": n, "rule": {"id": rule}, "state": state,
            "most_recent_instance": {"ref": R, "commit_sha": commit, "category": f"/language:{leg}", "state": state}}


def world(analyses, sarifs, alerts_r, alerts_base=(), fail=()):
    """get(path, accept) over one fixture. analyses newest first; alerts_r all states."""
    def get(path, accept):
        if any(f in path for f in fail):
            return 500, None
        base, _, q = path.partition("?")
        if base.startswith("code-scanning/analyses/"):
            aid = int(base.rsplit("/", 1)[1])
            return (200, sarifs[aid]) if accept == ACCEPT_SARIF and aid in sarifs else (404, None)
        page = int(q.rsplit("page=", 1)[1])
        if base == "code-scanning/analyses":
            rows = list(analyses)
        elif f"ref=refs/heads/{BASE}" in q:
            rows = list(alerts_base)
        else:
            st = q.split("state=", 1)[1].split("&", 1)[0]
            rows = [a for a in alerts_r if a["state"] == st]
        return 200, rows[(page - 1) * 100: page * 100]
    return get


def an(aid, leg, commit):
    return {"id": aid, "category": f"/language:{leg}", "commit_sha": commit, "ref": R}


THREE = [an(13, "python", M), an(12, "javascript-typescript", M), an(11, "actions", M)]
EMPTY = {12: sarif(), 11: sarif()}
PLANT = "py/code-injection"
LEGS = ("actions", "javascript-typescript", "python")


def cases():
    m = title_sha(TITLE)
    yield ("P  planted python-only finding is listed", world(THREE, {13: sarif((7, PLANT)), **EMPTY},
           [alert(7, PLANT, "open", M)]), dict(M=m), True, [f"code-scanning alert 7 ({PLANT})"], None)
    yield ("N  null: the plant removed lists nothing", world(THREE, {13: sarif(), **EMPTY}, []),
           dict(M=m), True, [], None)
    yield ("C  carried: an edit run keyed on S's sha= token lists the same alert",
           world(THREE, {13: sarif((7, PLANT)), **EMPTY}, [alert(7, PLANT, "open", M)]),
           dict(M=title_sha("CI code pr=77 base=main sha=m1")), True, [f"code-scanning alert 7 ({PLANT})"], None)
    # a newer analysis at R, another commit, without the finding: the alert reads fixed on R
    yield ("D  a newer analysis at R (commit m2) lacks the finding: listed from M's analysis",
           world([an(14, "python", M2)] + THREE, {13: sarif((7, PLANT)), 14: sarif(), **EMPTY},
                 [alert(7, PLANT, "fixed", M2)]), dict(M=m), True, [f"code-scanning alert 7 ({PLANT})"], [])
    yield ("D2 a newer analysis at R (commit m2) repeats it: still listed",
           world([an(14, "python", M2)] + THREE, {13: sarif((7, PLANT)), 14: sarif((7, PLANT)), **EMPTY},
                 [alert(7, PLANT, "open", M2)]), dict(M=m), True, [f"code-scanning alert 7 ({PLANT})"], [])
    yield ("S  a newer CodeQL analysis at the SAME commit: step 4 takes the newest at M (same tree, same results)",
           world([an(15, "python", M)] + THREE, {15: sarif((7, PLANT)), 13: sarif((7, PLANT)), **EMPTY},
                 [alert(7, PLANT, "open", M)]), dict(M=m), True, [f"code-scanning alert 7 ({PLANT})"], None)
    yield ("X  the planted alert dismissed by a person: not listed", world(THREE, {13: sarif((7, PLANT)), **EMPTY},
           [alert(7, PLANT, "dismissed", M)]), dict(M=m), True, [], None)
    yield ("B  an alert also open on the base, U6 says the merge ref repeats base alerts: subtracted",
           world(THREE, {13: sarif((3, "py/old"), (7, PLANT)), **EMPTY}, [alert(3, "py/old", "open", M), alert(7, PLANT, "open", M)],
                 alerts_base=[alert(3, "py/old", "open", "b0")]), dict(M=m, base_repeats=True), True,
           [f"code-scanning alert 7 ({PLANT})"], None)
    yield ("B0 the same, U6 says it does not repeat them: listed",
           world(THREE, {13: sarif((3, "py/old"), (7, PLANT)), **EMPTY}, [alert(3, "py/old", "open", M), alert(7, PLANT, "open", M)],
                 alerts_base=[alert(3, "py/old", "open", "b0")]), dict(M=m), True,
           ["code-scanning alert 3 (py/old)", f"code-scanning alert 7 ({PLANT})"], None)
    yield ("G  pagination: a dismissal on page 2 of the listing is seen",
           world(THREE, {13: sarif((7, PLANT), (250, "py/x")), **EMPTY},
                 [alert(1000 + i, "py/y", "dismissed", M) for i in range(150)] + [alert(250, "py/x", "dismissed", M)]),
           dict(M=m), True, [f"code-scanning alert 7 ({PLANT})"], None)
    yield ("L  no leg uploaded (every leg stood down): nothing read, nothing listed", world([], {}, []),
           dict(M=m, legs=()), True, [], None)
    yield ("F1 the SARIF read fails: FAIL closed", world(THREE, {13: sarif((7, PLANT)), **EMPTY}, [],
           fail=("analyses/13",)), dict(M=m), False, None, None)
    yield ("F2 a page of the dismissed listing fails: FAIL closed", world(THREE, {13: sarif((7, PLANT)), **EMPTY}, [],
           fail=("state=dismissed",)), dict(M=m), False, None, None)
    yield ("F3 a result without an alert number: FAIL closed",
           world(THREE, {13: {"runs": [{"results": [{"ruleId": PLANT, "properties": {}}]}]}, **EMPTY}, []),
           dict(M=m), False, None, None)
    yield ("F4 a leg uploaded but no analysis at M yet (step 4's bound passed): FAIL closed",
           world(THREE[1:], {**EMPTY}, []), dict(M=m), False, None, None)
    yield ("F5 the base listing fails while it is used: FAIL closed",
           world(THREE, {13: sarif((7, PLANT)), **EMPTY}, [], fail=("refs/heads/main",)),
           dict(M=m, base_repeats=True), False, None, None)


def self_test() -> int:
    n = bad = 0
    for label, get, kw, want_ok, want, by_ref_want in cases():
        n += 1
        ok, got = reds(get, R, kw["M"], kw.get("legs", LEGS), BASE, kw.get("base_repeats", False))
        good = ok == want_ok and (not ok or got == want)
        line = f"{'ok ' if good else 'BAD'} {label}: {'listed ' + str(got) if ok else got}"
        if by_ref_want is not None:     # the null control of the binding: the rejected reading must move here
            _, br = reds(get, R, kw["M"], kw.get("legs", LEGS), BASE, False, ablate=("by_ref",))
            moved = br == by_ref_want and br != want
            good &= moved
            line += f"\n      by_ref ablation (alerts?ref=R&state=open, commit_sha == M): listed {br} -> {'moves' if moved else 'DOES NOT MOVE'}"
        bad += not good
        print(line)
    print(f"\nALERT-LIST SELF-TEST {'ok' if not bad else 'FAILED'} ({n - bad}/{n})")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] != ["self-test"]:
        print(__doc__.strip().splitlines()[-1].strip())
        sys.exit(2)
    sys.exit(self_test())
