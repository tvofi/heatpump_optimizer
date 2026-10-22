#!/usr/bin/env python3
"""The umbrella's prelude: what one `ci.yml` run is, computed once (DESIGN-P2 2.3).

    python3 -I tools/ci/prelude.py [--changed-from FILE] >> "$GITHUB_OUTPUT"
    python3 -I tools/ci/prelude.py --self-test

Prints `key=value` lines: kind, pr, base, head, scope, legs, workset. It reads
the event from GITHUB_EVENT_NAME / GITHUB_EVENT_PATH and nothing else of the
run. `derive` and `title` are also the gate's (gate.py derives the event's kind
itself and only cross-checks this job's outputs) and `run-name`'s: ci.yml's
title is the string `title` returns, `sha=` token included (rev2 item 5).

KIND (the same expression as `run-name`):
  review          pull_request_review
  edit            pull_request edited without changes.base
  kernel-points   pull_request labeled with the `kernel-points` label (A2 item 2)
  label           pull_request labeled with any other label: it owns no unit,
                  so its gate only re-judges
  code            everything else (a retarget, every other pull_request action,
                  push, merge_group, workflow_dispatch)
WORKSET is the units a kind's run owns; a code run on a PR carrying the
`kernel-points` label also owns `kernel-points`, which is never required.

A dispatch naming `pr` is VERIFIED against the live PR (open, from this
repository, headed by this SHA, based on `base`) or the prelude fails, and the
gate, which re-verifies, fails with it. A non-code run waits until every
EARLIER ci.yml run at its head has finished (a held run aside), polling at
POLL_S (tvofi's 60 s floor, 2026-10-19), one runs listing per poll. A rate
limit prints `RATE-LIMITED` and fails closed (A1 item 4).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                      # -I drops the script's directory
import ghapi  # noqa: E402

CODE_UNITS = ("tests", "codeql", "governance", "hassfest", "validate")
BODY_UNITS = ("arch-score", "budget-raise-gate", "pr-contract")
BODY_ON_EDIT = frozenset(BODY_UNITS)
BODY_ON_REVIEW = frozenset({"budget-raise-gate"})  # owner variant: a review re-runs only budget-raise-gate
KP = "kernel-points"
UNFINISHED = ("queued", "pending", "waiting", "requested", "in_progress")
POLL_S = 60
WAIT_MAX_S = 8700       # inside the job's 150-minute timeout: the wait fails before the runner kills it
_QUEUE_PR = re.compile(r"/pr-([0-9]+)-[0-9a-f]{40}$")


def context(event_name: str, ev: dict, env: dict) -> dict:
    """The flat context `derive` and gate.py read, from the event payload."""
    pr = ev.get("pull_request") or {}
    mg = ev.get("merge_group") or {}
    inputs = ev.get("inputs") or {}
    q = _QUEUE_PR.search(mg.get("head_ref") or "")
    return {
        "event_name": event_name, "action": ev.get("action", ""),
        "changes_base": bool((ev.get("changes") or {}).get("base")),
        "label": (ev.get("label") or {}).get("name", ""),
        "labels": [x.get("name") for x in pr.get("labels") or []],
        "pr_number": str(pr.get("number") or ""), "base_ref": (pr.get("base") or {}).get("ref")
        or (mg.get("base_ref") or "").removeprefix("refs/heads/"),
        "queue_pr": q.group(1) if q else "",
        "input_pr": inputs.get("pr") or "", "input_base": inputs.get("base") or "",
        "head": (pr.get("head") or {}).get("sha") or mg.get("head_sha") or env.get("GITHUB_SHA", ""),
        "sha": env.get("GITHUB_SHA", ""), "repo": env.get("GITHUB_REPOSITORY", ""),
        "run_id": int(env.get("GITHUB_RUN_ID") or 0), "run_attempt": int(env.get("GITHUB_RUN_ATTEMPT") or 1),
    }


def derive(ctx: dict) -> tuple[str, str, str]:
    """(kind, pr, base) from the event alone."""
    ev = ctx["event_name"]
    if ev == "pull_request_review":
        return "review", str(ctx["pr_number"]), ctx["base_ref"]
    if ev == "pull_request":
        if ctx["action"] == "labeled":
            return (KP if ctx.get("label") == KP else "label"), str(ctx["pr_number"]), ctx["base_ref"]
        k = "edit" if ctx["action"] == "edited" and not ctx.get("changes_base") else "code"
        return k, str(ctx["pr_number"]), ctx["base_ref"]
    if ev == "merge_group":
        return "code", str(ctx.get("queue_pr") or ""), ctx.get("base_ref") or ""
    if ev == "workflow_dispatch":
        return "code", ctx.get("input_pr") or "", ctx.get("input_base") or ""
    return "code", "", ""                    # push


def title(kind: str, pr: str, base: str, sha: str = "") -> str:
    """The run's `run-name`, fixed at creation: a past run's kind is read from it."""
    return f"CI {kind} pr={pr or '-'} base={base or '-'} sha={sha or '-'}"


def parse_title(t: str) -> tuple[str, str, str] | None:
    p = t.split()
    if (len(p) != 5 or p[0] != "CI" or not p[2].startswith("pr=") or not p[3].startswith("base=")
            or not p[4].startswith("sha=")):
        return None
    pr, base = p[2][3:], p[3][5:]
    return p[1], ("" if pr == "-" else pr), ("" if base == "-" else base)


def title_sha(t: str) -> str:
    """The `sha=` token of a title parse_title accepts ('' for '-')."""
    v = t.split()[4][4:]
    return "" if v == "-" else v


def workset(kind: str, pr: str, labels=()) -> set[str]:
    if kind == "edit":
        return set(BODY_ON_EDIT)
    if kind == "review":
        return set(BODY_ON_REVIEW)
    if kind == KP:
        return {KP}
    if kind != "code":
        return set()                         # another label: re-judges only
    return set(CODE_UNITS) | (set(BODY_UNITS) if pr else set()) | ({KP} if KP in labels else set())


def verify_dispatch(ctx: dict, get) -> str:
    """'' when a dispatch's `pr`/`base` name the open PR this SHA heads; else why not."""
    pr, base = ctx["input_pr"], ctx["input_base"]
    if not pr:
        return "" if not base else "dispatch names base without pr"
    if not base:
        return f"dispatch pr={pr} without base"
    st, _, lp = get(f"repos/{ctx['repo']}/pulls/{pr}")
    if st != 200 or not isinstance(lp, dict):
        return f"pulls/{pr}: HTTP {st}"
    if lp.get("state") != "open" or lp["head"]["sha"] != ctx["sha"]:
        return f"dispatch pr={pr} does not name the open PR headed by {ctx['sha'][:12]}"
    if (lp["head"].get("repo") or {}).get("full_name") != ctx["repo"]:
        return f"PR {pr}: its head is not in this repository"
    if lp["base"]["ref"] != base:
        return f"dispatch base={base}, PR {pr} is based on {lp['base']['ref']}"
    return ""


def wait_earlier(ctx: dict, get, sleep=time.sleep, now=time.monotonic) -> str:
    """'' once every earlier ci.yml run at this head is finished; else why it stopped."""
    t0 = now()
    while True:
        st, _, doc = get(f"repos/{ctx['repo']}/actions/workflows/ci.yml/runs",
                         {"head_sha": ctx["head"], "per_page": 100})
        if st != 200 or not isinstance(doc, dict):
            return f"runs at {ctx['head'][:12]}: HTTP {st}"
        busy = sorted(r["id"] for r in doc.get("workflow_runs", [])
                      if r["id"] < ctx["run_id"] and r["status"] in UNFINISHED)
        if not busy:
            return ""
        if now() - t0 + POLL_S > WAIT_MAX_S:
            return f"earlier run(s) {busy} still unfinished after {WAIT_MAX_S} s"
        sleep(POLL_S)


def outputs(ctx: dict, changed: list[str] | None, get, sleep=time.sleep) -> tuple[dict, str]:
    """(the outputs, '' or why the prelude fails)."""
    kind, pr, base = derive(ctx)
    ev = ctx["event_name"]
    out = {"kind": kind, "pr": pr, "base": base, "head": ctx["head"],
           "scope": "full" if ev == "push" else "auto",
           "workset": " ".join(sorted(workset(kind, pr, ctx.get("labels", ()))))}
    sys.path.insert(0, str(HERE.parent / "pr"))
    import codeql_scope
    out["legs"] = json.dumps({leg: codeql_scope.decide(leg, ev, changed or [])[0]
                              for leg in codeql_scope.LEGS}, separators=(",", ":"))
    why = verify_dispatch(ctx, get) if ev == "workflow_dispatch" else ""
    if not why and kind != "code":
        why = wait_earlier(ctx, get, sleep)
    return out, why


def main(argv: list[str], get=ghapi.get, env=os.environ) -> int:
    if argv == ["--self-test"]:
        return self_test()
    changed = None
    if argv[:1] == ["--changed-from"] and len(argv) == 2:
        changed = Path(argv[1]).read_text().split()
    elif argv:
        print("usage: prelude.py [--changed-from FILE] | --self-test", file=sys.stderr)
        return 2
    ev = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text())
    try:
        out, why = outputs(context(env["GITHUB_EVENT_NAME"], ev, env), changed, get)
    except ghapi.RateLimited as e:
        print(f"RATE-LIMITED reset_epoch={e.reset_epoch} {e.path}", file=sys.stderr)
        return 3
    for k, v in out.items():
        print(f"{k}={v}")
    if why:
        print(f"FAIL {why}", file=sys.stderr)
        return 1
    return 0


def self_test() -> int:
    n, fails = 0, 0

    def check(name, got, want):
        nonlocal n, fails
        n += 1
        if got != want:
            fails += 1
            print(f"FAIL {name}: got {got!r}, want {want!r}")

    env = {"GITHUB_SHA": "H", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "50"}
    pr = {"number": 7, "base": {"ref": "main"}, "head": {"sha": "H"}, "labels": []}

    def ctx(ev_name, **ev):
        return context(ev_name, ev, env)
    check("synchronize", derive(ctx("pull_request", action="synchronize", pull_request=pr)), ("code", "7", "main"))
    check("body edit", derive(ctx("pull_request", action="edited", pull_request=pr)), ("edit", "7", "main"))
    check("retarget is code", derive(ctx("pull_request", action="edited", changes={"base": {"ref": {}}},
                                         pull_request=pr))[0], "code")
    check("review", derive(ctx("pull_request_review", action="submitted", pull_request=pr))[0], "review")
    check("labeled kernel-points", derive(ctx("pull_request", action="labeled", label={"name": KP},
                                              pull_request=pr))[0], KP)
    check("labeled other", derive(ctx("pull_request", action="labeled", label={"name": "x"}, pull_request=pr))[0], "label")
    check("kernel-points workset", workset(KP, "7"), {KP})
    check("other label owns nothing", workset("label", "7"), set())
    check("synchronize with the label adds kernel-points", KP in workset("code", "7", [KP]), True)
    check("code without the label", KP in workset("code", "7", []), False)
    check("push names no PR", derive(ctx("push")), ("code", "", ""))
    check("merge queue PR from its ref", derive(ctx("merge_group", merge_group={
        "head_ref": "refs/heads/gh-readonly-queue/main/pr-12-" + "a" * 40, "base_ref": "refs/heads/main"})), ("code", "12", "main"))
    check("dispatch inputs", derive(ctx("workflow_dispatch", inputs={"pr": "7", "base": "main"})), ("code", "7", "main"))
    t = title("edit", "7", "main", "abc")
    check("title round-trip", (parse_title(t), title_sha(t)), (("edit", "7", "main"), "abc"))
    check("unparseable title", parse_title("Tests"), None)
    check("label kind parses", parse_title(title("kernel-points", "7", "main"))[0], KP)
    live = {"state": "open", "head": {"sha": "H", "repo": {"full_name": "o/r"}}, "base": {"ref": "main"}}
    g = lambda lp: (lambda path, params=None: (200, {}, lp))  # noqa: E731
    dctx = ctx("workflow_dispatch", inputs={"pr": "7", "base": "main"})
    check("dispatch verified", verify_dispatch(dctx, g(live)), "")
    check("dispatch at another head refused", bool(verify_dispatch(dctx, g({**live, "head": {**live["head"], "sha": "X"}}))), True)
    check("dispatch naming the wrong base refused", bool(verify_dispatch(dctx, g({**live, "base": {"ref": "rel"}}))), True)
    check("dispatch of a fork PR refused", bool(verify_dispatch(dctx, g({**live, "head": {"sha": "H", "repo": {"full_name": "f/r"}}}))), True)
    check("dispatch pr without base refused", bool(verify_dispatch(ctx("workflow_dispatch", inputs={"pr": "7"}), g(live))), True)
    listings = iter([[{"id": 40, "status": "in_progress"}, {"id": 60, "status": "queued"}],
                     [{"id": 40, "status": "completed"}, {"id": 45, "status": "action_required"}]])
    naps = []
    w = wait_earlier(ctx("pull_request_review", pull_request=pr),
                     lambda p, q=None: (200, {}, {"workflow_runs": next(listings)}), naps.append)
    check("waits for an earlier run, not a later or held one", (w, naps), ("", [POLL_S]))
    check("poll floor is 60 s", POLL_S >= 60, True)
    clock = iter(range(0, 10 ** 6, 3000))
    w = wait_earlier(ctx("pull_request_review", pull_request=pr),
                     lambda p, q=None: (200, {}, {"workflow_runs": [{"id": 1, "status": "queued"}]}),
                     lambda s: None, lambda: next(clock))
    check("the wait is bounded", w.startswith("earlier run(s) [1]"), True)
    out, why = outputs(ctx("push"), None, g(live))
    check("push: full scope, code units", (out["scope"], out["workset"], why), ("full", "codeql governance hassfest tests validate", ""))
    out, _ = outputs(ctx("pull_request", action="synchronize", pull_request=pr), ["README.md"], g(live))
    check("legs from codeql_scope", json.loads(out["legs"]), {"actions": "skip", "javascript-typescript": "skip", "python": "skip"})

    def limited(path, params=None):
        raise ghapi.RateLimited(path, 99)
    path = _tmp_event({"inputs": {"pr": "7", "base": "main"}})
    try:
        check("rate limit fails closed", main([], limited, {**env, "GITHUB_EVENT_NAME": "workflow_dispatch",
                                                             "GITHUB_EVENT_PATH": path}), 3)
    finally:
        os.unlink(path)
    print(f"prelude self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def _tmp_event(doc: dict) -> str:
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".json")
    os.write(fd, json.dumps(doc).encode())
    os.close(fd)
    return path


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
