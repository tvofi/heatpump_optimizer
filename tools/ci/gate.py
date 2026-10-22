#!/usr/bin/env python3
"""The umbrella's one required check (DESIGN-P2 4.1; R10-CI-LAYOUT P2a, unit U0a).

    python3 -I tools/ci/gate.py --pr N --base B --kind K   # judge this run's head
    python3 -I tools/ci/gate.py --refresh                  # re-run stale green gates here
    python3 -I tools/ci/gate.py --sweep --run ID           # tools/ci/sweep.py's (U0b)
    python3 -I tools/ci/gate.py --self-test

The predicate is `measure/rev/gate_model.py` at 1371a0a6, ported line for line
(`gate`, `judging`); dev/audit/harnesses/r10_ci_gate_core.py drives the
design's replays (gate_replay2.py, gate_sim.py) against THIS file. `--pr`,
`--base` and `--kind` are the prelude's outputs, only cross-checked: the gate
derives what the event owes from the event itself (prelude.derive).

Order (rev3, R3-1): the event, then git (D-2's three-dot diff), then the
Actions and pulls reads as the LAST step, then the summary. The first stdout
token is the outcome: `PASS` (exit 0), `FAIL <reason>` (exit 1), or
`RATE-LIMITED reset_epoch=<n>` (exit 3, A1 item 4): a rate limit fails closed
and is never PASS.

REQUIRED is keyed by event class (contract item 4). The 17 contexts of ruleset
23698884 are renamed `<file stem> / <job>`; `arch-score / arch-score` joins
when the diff reaches custom_components/ (D-2); on `push`, every job whose
failure reddens today's Tests push run joins (B3, enumerated from tests.yml by
the harness's `b3` arm, never from memory). `tests / arch-instrument` is
P2b's (U5b), added to REQUIRED and to that enumeration together.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                      # -I drops the script's directory
import ghapi  # noqa: E402
from prelude import BODY_UNITS, CODE_UNITS, context, derive, parse_title, title, workset  # noqa: E402,F401

UNITS = {                                          # every name a unit owes at a PR head
    "tests": ("fast (3.14)", "browser", "briefs", "typing", "mutation", "closures", "closure-scope"),
    "codeql": ("Analyze (actions)", "Analyze (javascript-typescript)", "Analyze (python)"),
    "governance": ("policy-docs", "wave-script", "env-matrix"),
    "hassfest": ("hassfest",),
    "validate": ("validate-hacs",),
    "arch-score": ("arch-score",),                 # owner ruling D-2
    "budget-raise-gate": ("budget-raise-gate",),
    "pr-contract": ("pr-contract",),
}
PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet", "ci-ratchet")}      # B3
CODE = {u: UNITS[u] for u in CODE_UNITS}
BODY = {u: UNITS[u] for u in BODY_UNITS}
ATTEMPT_CAP = 45     # GitHub fails a run's 51st attempt; the hooks never take a run past 45 (4.3)


def _names(units, drop=(), extra=None) -> tuple[str, ...]:
    return tuple(f"{u} / {n}" for u in units for n in UNITS[u] + (extra or {}).get(u, ()) if n not in drop)


REQUIRED: dict[str, tuple[str, ...]] = {
    "push": _names(CODE_UNITS, drop=("closure-scope",), extra=PUSH_ONLY),   # closure-scope never runs on push
    "no-pr": _names(CODE_UNITS),                                         # a dispatch naming no PR
    "pr": _names(CODE_UNITS + ("budget-raise-gate", "pr-contract")),
    "pr-cc": _names(CODE_UNITS + BODY_UNITS),                            # D-2
}


def event_class(event_name: str, pr: str, reaches_cc) -> str:
    if event_name == "push":
        return "push"
    if not pr:
        return "no-pr"
    return "pr-cc" if reaches_cc else "pr"


def gate_required() -> list[str]:
    """The fixture's `gate_required`: every name REQUIRED can hold."""
    return sorted({n for names in REQUIRED.values() for n in names})


def judging(run: dict) -> bool:
    """A run that can add no source is not waited on (rev2 N2, rev3 R3-2): its
    `gate` is listed, no listed prelude or unit job is unfinished, and every name
    its own title's workset owes is listed and completed (`tests /
    closure-scope` aside when it names no PR)."""
    jobs = run.get("jobs") or {}
    if "gate" not in jobs or not all(st[0] == "completed" for k, st in jobs.items()
                                     if k == "prelude" or k.split(" / ")[0] in UNITS):
        return False
    t = parse_title(run.get("title") or "")
    if t is None:
        return False                        # unreadable: never treated as finished (gate() also refuses it)
    for u in workset(t[0], t[1]) & set(UNITS):
        for n in UNITS[u]:
            if u == "tests" and n == "closure-scope" and not t[1]:
                continue
            st = jobs.get(f"{u} / {n}")
            if st is None or st[0] != "completed":
                return False
    return True


def gate(ctx: dict, api: dict) -> tuple[bool, list[str]]:
    """The 4.1 predicate over what gate.py read (gate_model.gate's `api` shape):
    prelude, jobs (this run's, latest), runs_at_head (every OTHER run here,
    with its latest jobs), live_pr, open_pr_heads, reaches_cc. A green result
    certifies the head's CURRENT state."""
    bad: list[str] = []
    kind, pr, base = derive(ctx)
    ev = ctx["event_name"]
    pre = api["prelude"]
    if pre.get("conclusion") != "success":
        return False, [f"prelude: {pre.get('conclusion')}"]
    if (pre.get("kind"), pre.get("pr", "")) != (kind, pr):
        return False, [f"prelude says kind={pre.get('kind')} pr={pre.get('pr')!r}, the event says kind={kind} pr={pr!r}"]
    if int(ctx.get("run_attempt", 1)) >= ATTEMPT_CAP:
        return False, [f"attempt {ctx.get('run_attempt')} of this run is at the cap ({ATTEMPT_CAP}): push a new commit"]
    if ev == "workflow_dispatch":
        if pr:
            lp = api.get("live_pr")
            if not lp or lp["state"] != "open" or lp["head_sha"] != ctx["sha"]:
                return False, [f"dispatch pr={pr} does not name the open PR headed by this SHA"]
        elif ctx["sha"] in api.get("open_pr_heads", set()):
            return False, ["this SHA heads an open PR: dispatch with -f pr=N -f base=REF"]
    judge_base = base                       # the PR's base NOW: a run that judged another base is no source
    if pr and ev != "merge_group":
        lp = api.get("live_pr")
        if not lp:
            return False, [f"PR {pr} could not be read"]
        judge_base = lp["base_ref"]
        if lp.get("same_repo") is not True:  # R3-4: no supersession or refresh reaches a fork head
            return False, [f"PR {pr}: its head is not in this repository (a fork PR is not gated here)"]
    others = [r for r in api["runs_at_head"] if r["id"] != ctx["run_id"]]
    busy = sorted(r["id"] for r in others if r["status"] not in ("completed", "action_required") and not judging(r))
    if busy:
        return False, [f"run(s) {busy} at this head are still being judged; their gate decides"]
    required: dict[str, list[str]] = {}
    for name in REQUIRED[event_class(ev, pr, api.get("reaches_cc"))]:
        u, n = name.split(" / ", 1)
        required.setdefault(u, []).append(n)
    me = {"id": ctx["run_id"], "title": title(kind, pr, base, ctx.get("sha", "")), "status": "completed",
          "jobs": api["jobs"]}
    for unit, names in required.items():
        src = None
        for r in sorted(others + [me], key=lambda r: r["id"], reverse=True):
            if r["status"] == "action_required":
                continue
            t = parse_title(r["title"])
            if t is None:
                bad.append(f"run {r['id']}: unreadable title {r['title']!r}")
                continue
            if t[1] != pr or t[2] != judge_base or unit not in workset(t[0], t[1]):
                continue
            js = [r["jobs"].get(f"{unit} / {n}") for n in names]
            if r is me or all(j is not None and j[0] == "completed" for j in js):
                src = r                     # this run's own unit always counts (its needs ran it)
                break
        if src is None:
            bad.append(f"{unit}: no run at this head judged base {judge_base!r}")
            continue
        where = "this run" if src is me else f"run {src['id']}"
        for n in names:
            st = src["jobs"].get(f"{unit} / {n}")
            if st is None:
                bad.append(f"{unit} / {n}: ABSENT ({where})")
            elif st[0] != "completed":
                bad.append(f"{unit} / {n}: PENDING ({where})")
            elif st[1] != "success":
                bad.append(f"{unit} / {n}: {st[1].upper() if st[1] == 'skipped' else st[1]} ({where})")
    return not bad, sorted(set(bad), key=bad.index)


def _jobs(get, repo: str, run_id) -> dict:
    return {j["name"]: (j["status"], j["conclusion"]) for j in
            ghapi.paginate(f"repos/{repo}/actions/runs/{run_id}/jobs", {"filter": "latest"}, get=get)}


def _pull(get, repo: str, pr: str) -> dict:
    st, _, lp = get(f"repos/{repo}/pulls/{pr}")
    if st != 200 or not isinstance(lp, dict):
        msg = lp.get("message", "") if isinstance(lp, dict) else ""
        raise ghapi.ApiError(f"repos/{repo}/pulls/{pr}", st, msg)
    return lp


def read_api(ctx: dict, claim: dict, reaches_cc, get) -> dict:
    """Every Actions and pulls read the predicate needs, in one place: the last step."""
    repo, (_, pr, _) = ctx["repo"], derive(ctx)
    jobs = _jobs(get, repo, ctx["run_id"])
    api = {"prelude": {"conclusion": (jobs.get("prelude") or (None, None))[1], **claim},
           "jobs": jobs, "reaches_cc": reaches_cc, "live_pr": None, "open_pr_heads": set()}
    if pr and ctx["event_name"] != "merge_group":
        lp = _pull(get, repo, pr)
        api["live_pr"] = {"head_sha": lp["head"]["sha"], "base_ref": lp["base"]["ref"], "state": lp["state"],
                          "same_repo": (lp["head"].get("repo") or {}).get("full_name") == repo}
    elif ctx["event_name"] == "workflow_dispatch":
        api["open_pr_heads"] = {p["head"]["sha"] for p in ghapi.paginate(f"repos/{repo}/pulls", {"state": "open"}, get=get)}
    runs = ghapi.paginate(f"repos/{repo}/actions/workflows/ci.yml/runs", {"head_sha": ctx["head"]}, get=get)
    api["runs_at_head"] = [{"id": r["id"], "title": r.get("display_title") or "", "status": r["status"],
                            "jobs": {} if r["status"] == "action_required" else _jobs(get, repo, r["id"])}
                           for r in runs if r["id"] != ctx["run_id"]]
    return api


def reaches_custom_components(base: str, head: str) -> bool:
    """D-2's three-dot diff, from the checkout; unknown reads as reaching (fail closed)."""
    p = subprocess.run(["git", "diff", "--name-only", f"origin/{base}...{head}", "--", "custom_components/"],
                       capture_output=True, text=True)
    return p.returncode != 0 or bool(p.stdout.strip())


def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components) -> tuple[str, list[str]]:
    kind, pr, base = derive(ctx)
    cc = reaches(base, ctx["head"]) if pr else None     # git first; the API reads are last (R3-1)
    ok, why = gate(ctx, read_api(ctx, claim, cc, get))
    return ("PASS" if ok else f"FAIL {why[0]}"), why


def refresh(ctx: dict, get, post) -> tuple[int, list[str]]:
    """Re-run the `gate` of every completed run at this live head whose latest gate is green."""
    _, pr, _ = derive(ctx)
    if ctx["event_name"] not in ("pull_request", "pull_request_review") or not pr:
        return 0, ["NOTICE refresh acts on pull_request and review events only"]
    lp = _pull(get, ctx["repo"], pr)
    if (lp["head"].get("repo") or {}).get("full_name") != ctx["repo"]:
        return 0, [f"NOTICE PR {pr}: a fork head; this token cannot re-run its gates"]
    if lp["head"]["sha"] != ctx["head"]:
        return 0, [f"NOTICE PR {pr} has moved past {ctx['head'][:12]}; nothing to refresh"]
    rc, log = 0, []
    for r in ghapi.paginate(f"repos/{ctx['repo']}/actions/workflows/ci.yml/runs", {"head_sha": ctx["head"]}, get=get):
        if r["id"] == ctx["run_id"] or r["status"] != "completed":
            continue
        g = [j for j in ghapi.paginate(f"repos/{ctx['repo']}/actions/runs/{r['id']}/jobs", {"filter": "latest"}, get=get)
             if j["name"] == "gate"]
        if not g or g[0]["conclusion"] != "success":
            continue
        if int(r.get("run_attempt", 1)) >= ATTEMPT_CAP:
            log.append(f"SKIP run {r['id']} at attempt {r['run_attempt']}: push a new commit")
            continue
        st, _, _ = post(f"repos/{ctx['repo']}/actions/jobs/{g[0]['id']}/rerun")
        log.append(f"{'RERUN' if st in (201, 204) else 'FAIL rerun'} run {r['id']} gate job {g[0]['id']}: HTTP {st}")
        rc |= st not in (201, 204)
    return rc, log


def summary(outcome: str, why: list[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write(f"### gate: {outcome.split()[0]}\n\n" + "".join(f"- {w}\n" for w in why))


def main(argv: list[str], get=ghapi.get, post=ghapi.post, env=os.environ) -> int:
    ap = argparse.ArgumentParser(prog="gate.py")
    ap.add_argument("--pr", default=None)
    ap.add_argument("--base", default="")
    ap.add_argument("--kind", default=None)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    try:
        if a.sweep:
            try:
                import sweep
            except ImportError:
                print("FAIL sweep-unavailable: tools/ci/sweep.py (U0b) is not in this tree")
                return 1
            return sweep.main(["--run", str(a.run)], get, post)
        ctx = context(env["GITHUB_EVENT_NAME"], json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text()), env)
        if a.refresh:
            rc, log = refresh(ctx, get, post)
            print("\n".join(log) or "NOTICE no green gate to refresh")
            return rc
        if a.kind is None or a.pr is None:
            print("FAIL usage: --pr N --base B --kind K (the prelude's outputs)")
            return 1
        outcome, why = judge(ctx, {"kind": a.kind, "pr": a.pr}, get)
    except ghapi.RateLimited as e:
        outcome, why = f"RATE-LIMITED reset_epoch={e.reset_epoch} {e.path}", [str(e)]
        print(outcome)
        summary(outcome, why)
        return 3
    except ghapi.ApiError as e:
        outcome, why = f"FAIL {e}", [str(e)]
    print("\n".join([outcome] + why[1:]))
    summary(outcome, why)
    return 0 if outcome == "PASS" else 1


def self_test() -> int:
    n, fails = 0, 0

    def check(name, got, want):
        nonlocal n, fails
        n += 1
        if got != want:
            fails += 1
            print(f"FAIL {name}: got {got!r}, want {want!r}")

    fixture = json.loads((HERE.parent / "policy" / "fixtures" / "required-contexts.json").read_text())
    check("REQUIRED['pr'] is the 17 contexts, renamed", sorted(n.split(" / ", 1)[1] for n in REQUIRED["pr"]),
          sorted(fixture["contexts"]))
    check("D-2: arch-score only when the diff reaches custom_components/",
          set(REQUIRED["pr-cc"]) - set(REQUIRED["pr"]), {"arch-score / arch-score"})
    check("B3: push owes the Tests push run's ratchets", {"tests / ci-ratchet", "tests / coverage-ratchet"} <= set(REQUIRED["push"]), True)
    check("push owes no closure-scope and no body unit", [x for x in REQUIRED["push"] if "closure-scope" in x
                                                            or x.split(" / ")[0] in BODY], [])
    check("arch-instrument is P2b's", any("arch-instrument" in x for x in gate_required()), False)
    check("fixture gate_required == REQUIRED's union", fixture.get("gate_required"), gate_required())
    repo, head = "o/r", "H"
    env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": repo, "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
    ev = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": head}}}
    ctx = context("pull_request", ev, env)
    green = [{"name": "prelude", "status": "completed", "conclusion": "success"}] + [
        {"name": x, "status": "completed", "conclusion": "success", "id": 1} for x in REQUIRED["pr-cc"]]
    pull = {"state": "open", "head": {"sha": head, "repo": {"full_name": repo}}, "base": {"ref": "main"}}

    def fake(jobs=green, lp=pull, runs=(), status=200):
        def get(path, params=None):
            if path.endswith("/pulls/7"):
                return status, {}, (lp if status == 200 else {"message": "Resource not accessible by integration"})
            if path.endswith("/runs/100/jobs"):
                return 200, {}, {"jobs": jobs}
            if "/runs/" in path and path.endswith("/jobs"):
                return 200, {}, {"jobs": [{"name": "gate", "status": "completed", "conclusion": "success", "id": 9}]}
            if path.endswith("ci.yml/runs"):
                return 200, {}, {"workflow_runs": list(runs)}
            return 404, {}, None
        return get
    claim, cc = {"kind": "code", "pr": "7"}, (lambda b, h: True)
    check("null: every source green", judge(ctx, claim, fake(), cc)[0], "PASS")
    red = [dict(j, conclusion="failure") if j["name"] == "tests / closures" else j for j in green]
    check("a red required job", judge(ctx, claim, fake(red), cc)[0], "FAIL tests / closures: failure (this run)")
    skip = [dict(j, conclusion="skipped") if j["name"] == "tests / browser" else j for j in green]
    check("a skipped required job (4.2)", judge(ctx, claim, fake(skip), cc)[0], "FAIL tests / browser: SKIPPED (this run)")
    check("D-2 null: arch-score red, diff misses custom_components/",
          judge(ctx, claim, fake([dict(j, conclusion="failure") if j["name"].startswith("arch") else j for j in green]),
                lambda b, h: False)[0], "PASS")
    check("prelude cross-check", judge(ctx, {"kind": "code", "pr": ""}, fake(), cc)[0].startswith("FAIL prelude says"), True)
    fork = {**pull, "head": {"sha": head, "repo": {"full_name": "fork/r"}}}
    check("R3-4: a fork PR, every source green", judge(ctx, claim, fake(lp=fork), cc)[0].startswith("FAIL PR 7: its head is not"), True)
    check("cap: attempt 45", judge({**ctx, "run_attempt": 45}, claim, fake(), cc)[0].startswith("FAIL attempt 45"), True)
    jobs = {j["name"]: (j["status"], j["conclusion"]) for j in green}
    api = {"prelude": {"conclusion": "success", **claim}, "reaches_cc": True, "open_pr_heads": set(),
           "live_pr": {"head_sha": head, "base_ref": "main", "state": "open", "same_repo": True}}
    older = {"id": 90, "title": title("code", "7", "main"), "status": "completed", "jobs": jobs}
    gap = {k: v for k, v in jobs.items() if k != "hassfest / hassfest"}
    check("this run's own unit is never filled from an older run (12(c))",
          gate(ctx, {**api, "jobs": gap, "runs_at_head": [older]}), (False, ["hassfest / hassfest: ABSENT (this run)"]))
    held = {"id": 105, "title": title("edit", "7", "main"), "status": "action_required",
            "jobs": {**jobs, "pr-contract / pr-contract": ("completed", "failure")}}
    body = {k: v for k, v in jobs.items() if k.split(" / ")[0] in BODY}
    check("a newer held run is neither waited on nor a source", gate({**ctx, "action": "edited"}, {
        **api, "prelude": {"conclusion": "success", "kind": "edit", "pr": "7"}, "jobs": body,
        "runs_at_head": [older, held]}), (True, []))
    busy = [{"id": 99, "display_title": title("code", "7", "main", "M"), "status": "in_progress"}]
    check("defer on an earlier run still adding a source", judge(ctx, claim, fake(runs=busy), cc)[0].startswith("FAIL run(s) [99]"), True)

    def limited(path, params=None):
        raise ghapi.RateLimited(path, 1700000000, "api rate limit exceeded")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        Path(d, "ev.json").write_text(json.dumps(ev))
        menv = {**env, "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(Path(d, "ev.json"))}
        args = ["--pr", "7", "--base", "main", "--kind", "code"]
        import contextlib
        import io
        for label, g, want in (("A1 plant: a rate limit is RATE-LIMITED, never PASS", limited, 3),
                               ("A1 null: an ordinary 403 is FAIL with its reason", fake(status=403), 1)):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(args, g, None, menv)
            first = buf.getvalue().split("\n")[0]
            check(label, (rc, first.split()[0]), (want, "RATE-LIMITED" if want == 3 else "FAIL"))
        check("the 403's reason is printed", "HTTP 403 Resource not accessible" in first, True)
        import types
        calls, saved = [], sys.modules.get("sweep")
        try:
            sys.modules["sweep"] = None                # an import of None raises ImportError
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(["--sweep", "--run", "5"], fake(), None, menv)
            check("--sweep without sweep.py fails closed", (rc, buf.getvalue().split()[:2]), (1, ["FAIL", "sweep-unavailable:"]))
            sys.modules["sweep"] = types.SimpleNamespace(main=lambda argv, g, p: calls.append((argv, g, p)) or 7)
            g = fake()
            check("--sweep dispatches to sweep.main(argv, get, post)", (main(["--sweep", "--run", "5"], g, "P", menv), calls),
                  (7, [(["--run", "5"], g, "P")]))
        finally:
            sys.modules.pop("sweep")
            if saved is not None:
                sys.modules["sweep"] = saved
    posted = []
    done = [{"id": 50, "status": "completed", "run_attempt": 1}, {"id": 60, "status": "completed", "run_attempt": 45},
            {"id": 100, "status": "in_progress", "run_attempt": 1}]
    rc, log = refresh(ctx, fake(runs=done), lambda p, b=None: (posted.append(p), (201, {}, None))[1])
    check("refresh re-runs a completed green gate, never one at the cap, never its own run",
          (rc, posted), (0, [f"repos/{repo}/actions/jobs/9/rerun"]))
    check("refresh at a fork head is a notice", refresh(ctx, fake(lp=fork), None)[0], 0)
    print(f"gate self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
