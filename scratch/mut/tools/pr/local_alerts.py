#!/usr/bin/env python3
"""The code-scanning alerts `pr-contract` will list for this branch, read locally.

    python3 -I tools/pr/local_alerts.py --repo O/R --branch B [--base main] [--base-repeats]
    python3 -I tools/pr/local_alerts.py --self-test

`prepr.sh` step 7c feeds the red names of the branch's pushed commits to the body
check. After the layout cut-over `pr-contract` also lists each open alert of the
CodeQL analyses behind the pull request's merge ref (R4-1, owner ruling R-10), so
a body drafted locally has to name them too. This module finds the open pull
request, the newest `code` run of `ci.yml` at its head and the legs that run
uploaded, then asks `tools/ci/alert_list.py` -- the one implementation, imported
and never restated -- for the lines. It is a pre-check: stdout is one
`code-scanning alert <n> (<rule id>)` line per alert and rc 0, or rc 3 and one line
saying the alerts were NOT READ (no open pull request, no code run yet, a token
that cannot read code scanning, a rate limit); `pr-contract` fails closed on what
this leaves unread. Every read goes through `ghapi.get`.
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ci"))
import alert_list  # noqa: E402
import ghapi  # noqa: E402

LEG_JOB = "codeql / Analyze ("


def read(get, path, params):
    status, _, body = get(path, params)
    if status != 200:
        raise alert_list.ReadFailed(f"{path}: HTTP {status}")
    return body


def listing(get, owner, branch, base="main", base_repeats=False):
    """(0, [alert lines]) or (3, [why the alerts were not read])."""
    try:
        prs = read(get, "pulls", {"head": f"{owner}:{branch}", "state": "open"})
        if not prs:
            return 3, [f"no open pull request has {branch} as its head"]
        pr = prs[0]
        runs = read(get, "actions/workflows/ci.yml/runs",
                    {"head_sha": pr["head"]["sha"], "event": "pull_request", "per_page": 30})["workflow_runs"]
        code = sorted((r for r in runs if (r.get("display_title") or "").startswith("CI code ")),
                      key=lambda r: r["created_at"])
        if not code:
            return 3, [f"no code run of ci.yml at {pr['head']['sha'][:10]} yet"]
        jobs = read(get, f"actions/runs/{code[-1]['id']}/jobs", {"per_page": 100})["jobs"]
        legs = sorted(j["name"][len(LEG_JOB):-1] for j in jobs
                      if j["name"].startswith(LEG_JOB) and j.get("conclusion") == "success")
        ok, got = alert_list.reds(get, f"refs/pull/{pr['number']}/merge",
                                  alert_list.title_sha(code[-1]["display_title"]), legs,
                                  pr["base"]["ref"] or base, base_repeats)
        return (0, got) if ok else (3, [got])
    except alert_list.ReadFailed as e:
        return 3, [str(e)]
    except ghapi.RateLimited as e:
        return 3, [f"rate limited until {e.reset_epoch}"]
    except OSError as e:          # no network, a refused connection: unread, never an empty list
        return 3, [f"{type(e).__name__}: {e}"]


def self_test() -> int:
    bad = 0

    def check(label, got, want):
        nonlocal bad
        bad += got != want
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}" + ("" if got == want else f": got {got!r}"))

    M = "m1"
    title = f"CI code pr=7 base=main sha={M}"
    ana = [alert_list.an(13, "python", M), alert_list.an(12, "javascript-typescript", M),
           alert_list.an(11, "actions", M)]

    def world(prs=True, runs=True, conclusion="success", alerts=((5, "py/x", "open"),), fail=()):
        inner = alert_list.world(ana, {i: alert_list.sarif(*[(n, r) for n, r, _ in alerts]) for i in (11, 12, 13)},
                                 [alert_list.alert(n, r, s) for n, r, s in alerts], fail=fail)

        def get(path, params=None, headers=None):
            if path == "pulls":
                return 200, {}, [{"number": 7, "head": {"sha": "h" * 40}, "base": {"ref": "main"}}] if prs else []
            if path == "actions/workflows/ci.yml/runs":
                return 200, {}, {"workflow_runs": [{"id": 9, "display_title": title, "created_at": "t"}] if runs else []}
            if path == "actions/runs/9/jobs":
                return 200, {}, {"jobs": [{"name": f"codeql / Analyze ({x})", "conclusion": conclusion}
                                          for x in ("actions", "javascript-typescript", "python")]
                                 + [{"name": "tests / closures", "conclusion": "failure"}]}
            return inner(path, params, headers)
        return get

    check("an open alert on the merge ref's analyses is listed", listing(world(), "o", "b"),
          (0, ["code-scanning alert 5 (py/x)"]))
    check("a dismissed alert is not (null)", listing(world(alerts=((5, "py/x", "dismissed"),)), "o", "b"), (0, []))
    check("no open pull request is NOT READ, never an empty list", listing(world(prs=False), "o", "b")[0], 3)
    check("no code run yet is NOT READ", listing(world(runs=False), "o", "b")[0], 3)
    check("a run whose legs did not succeed uploaded none, so lists none (null)",
          listing(world(conclusion="failure"), "o", "b"), (0, []))
    check("a code scanning read that fails is NOT READ", listing(world(fail=("code-scanning/analyses",)), "o", "b")[0], 3)
    print(f"local_alerts self-test: {bad} failed")
    return 1 if bad else 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="local_alerts.py")
    ap.add_argument("--repo")
    ap.add_argument("--branch")
    ap.add_argument("--base", default="main")
    ap.add_argument("--base-repeats", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not (a.repo and a.branch):
        ap.error("--repo and --branch are required")
    rc, lines = listing(alert_list.bind(ghapi.get, a.repo), a.repo.split("/")[0], a.branch, a.base, a.base_repeats)
    print("\n".join(lines) if rc == 0 else "code-scanning alerts NOT READ: " + "; ".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
