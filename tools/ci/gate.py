#!/usr/bin/env python3
"""The umbrella's one required check (DESIGN-P2 4.1; R10-CI-LAYOUT P2a, unit U0a).

    python3 -I tools/ci/gate.py --pr N --base B --kind K   # judge this run's head
    python3 -I tools/ci/gate.py --refresh                  # re-run stale green gates here
    python3 -I tools/ci/gate.py --sweep --run ID           # tools/ci/sweep.py's (U0b)
    python3 -I tools/ci/gate.py --self-test

The predicate is `measure/rev/gate_model.py` at 1371a0a6, ported line for line
(`gate` here, `judging` in prelude.py, which its wait shares);
dev/audit/harnesses/r10_ci_gate_core.py drives the design's replays
(gate_replay2.py, gate_sim.py) against THIS file. `--pr`,
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
the harness's `b3` arm, never from memory) except PUSH_REPORT_ONLY's ci-ratchet,
which the push summary reports in one line and never grades. `tests / arch-instrument`, the
architecture-score pair's own job beside `fast` (P2b, U5b), is a tests name
like the rest: required on pull requests and push alike.

DEFERRAL (R10-GATE-DEFER; r10-gate-busy-defer-3). A run still adding a source
at this head (`busy`) makes this verdict undecided. The gate then FAILs with
the deferral AT ONCE and holds no runner while the decider runs: it never
passes early, and gate-sweep.yml re-runs it when the deciding run completes
(tools/ci/sweep.py: the green, newest-covering gate's branch; or `settle`,
where no gate is green). The re-run reads the finished sources, so its verdict
is the one every gate at the head computes from them: a red source stays red.
The waits this replaced (up to GATE_WAIT_MAX_S, re-reading every POLL_S) held
a runner for a decider that, for a C3 edit run (prelude.defer_to, R10-CI-SLIM
card C3), is a code run some 30 minutes from its gate: #3282's edit gate
42367457809 held one 11:18-11:30Z and failed deferring anyway.
Deferrals stay acyclic in the order judging() and busy() give: a gate defers
only to runs not yet `judging` (judging() reads a deferring run's skipped
`pr-contract` caller as a unit it never ran, r10-gate-busy-defer-2), and two
runs whose gates have both started are broken by id (`busy`): the lower decides,
the higher defers to it. Where a lagging listing still makes two gates defer
to each other, both are red, and settle re-runs both once each has concluded.
Settle re-runs a gate at most once per source change, and a skipped job is no
source: GitHub re-stamps it at every gate re-run (sweep.py's module doc;
R10-HOTFIX-SWEEP-SETTLE-LOOP, where reading those stamps looped two runs).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                      # -I drops the script's directory
import ghapi  # noqa: E402
from prelude import (BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, derive, judging, parse_title, prior_jobs,  # noqa: E402,F401
                     run_jobs, standing, title, workset)

PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet")}      # B3
# The push-only job that is graded on its own and never fails the gate: a red
# ci-ratchet is a debt the follow-up pays, and the merge it grades already
# happened (tests.yml: "Not a required context"). It still runs, and
# machinery_line() reports its conclusion.
PUSH_REPORT_ONLY = {"tests": ("ci-ratchet",)}
CODE = {u: UNITS[u] for u in CODE_UNITS}
BODY = {u: UNITS[u] for u in BODY_UNITS}
ATTEMPT_CAP = 45     # GitHub fails a run's 51st attempt; the hooks never take a run past 45 (4.3)
# The bound on re-reading this run's own lagging jobs listing (lag_bound; a
# deferral is published at once, r10-gate-busy-defer-3): ci.yml's gate job has
# 15 min; the job's checkout, restore and reads take under a minute without a
# wait (#2754's edit gate: 21 s), so 12 min of re-reading plus one poll leaves two
# minutes. The self-test pins it under the job's `timeout-minutes`.
GATE_WAIT_MAX_S = 720
# An own job not yet listed at all: measured lag 20 s (41289450679), while a
# structural ABSENT (a renamed job) is absent on every run, so its wait is short.
GATE_ABSENT_MAX_S = 2 * POLL_S


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


def started(run: dict) -> bool:
    """Whether the run's `gate` job has started: listed `in_progress` or `completed`,
    never merely listed (GitHub lists it `waiting` from the run's start, R3-2)."""
    return (run.get("jobs") or {}).get("gate", ("",))[0] in STARTED


def busy(ctx: dict, runs_at_head: list[dict]) -> list:
    """The OTHER runs at this head still adding a source: unfinished, not held, not
    judging, and not a LATER run whose `gate` has started. A started gate has run
    every unit it needs (ci.yml's `needs`; a merely listed one has not: GitHub
    lists it `waiting` from the run's start, R3-2), yet judging() can still read
    it busy:
    a deferring edit run never lists the `pr-contract / pr-contract` its title
    owes (C3). Two such gates then each deferred to the other and none judged
    (#3241 at 95c7e604, runs 42192623509 and 42193153511). The tie-break: the
    lower id decides, the higher waits on it, so the waits stay acyclic."""
    return sorted(r["id"] for r in runs_at_head
                  if r["id"] != ctx["run_id"] and r["status"] not in ("completed", "action_required") and not judging(r)
                  and not (r["id"] > ctx["run_id"] and started(r)))


def deferral(ids: list) -> str:
    return f"run(s) {ids} at this head are still being judged; their gate decides"


OWN_PENDING = ": PENDING (this run)"
OWN_ABSENT = ": ABSENT (this run)"


def lag_bound(why: list[str]) -> int:
    """Seconds judge() may re-read when every reason is the jobs listing lagging
    this run's own graph, else 0. `gate` needs prelude and every unit of its own
    run (through pr-contract), so an own job listed unfinished, or not listed,
    has finished and the listing lags it (run 41870314676: closures done
    17:36:51Z, read pending at 17:37:43Z; dev/audit/rca/r10-gate-stale-jobs.md).
    A unit outside this run's workset is never ABSENT (gate() names no source),
    and an unlisted prelude is no lag reason. A lagging job never reads as
    success, so the bound exhausted is still a FAIL, and any other reason beside
    it is published at once."""
    if not why or not all(w.endswith((OWN_PENDING, OWN_ABSENT)) for w in why):
        return 0
    return GATE_ABSENT_MAX_S if any(w.endswith(OWN_ABSENT) for w in why) else GATE_WAIT_MAX_S


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
        listed_unfinished = pre.get("status") not in (None, "completed")
        return False, ["prelude" + OWN_PENDING if listed_unfinished else f"prelude: {pre.get('conclusion')}"]
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
    own = pre.get("workset")                # the units the prelude ran here; a deferring edit run ran fewer (C3)
    waiting = busy(ctx, others)
    if waiting:
        return False, [deferral(waiting)]
    required: dict[str, list[str]] = {}
    for name in REQUIRED[event_class(ev, pr, api.get("reaches_cc"))]:
        u, n = name.split(" / ", 1)
        required.setdefault(u, []).append(n)
    me = {"id": ctx["run_id"], "title": title(kind, pr, base, ctx.get("sha", "")), "status": "completed",
          "jobs": api["jobs"], "starts": api.get("starts") or {}}

    def fresh(r, names):
        """A unit's source order: the run whose jobs for it started LATEST read the head's live
        state last (arch-score and budget-raise-gate read the PR at their start), then the higher
        id. GitHub numbers a same-second push and body edit out of order (r10-ci-edit-runner:
        the edit run lower in 27 of 94 pairs), and a re-run executes a lower run's unit afresh.
        This run's own unit while its listing lags is never displaced: its needs ran it."""
        if r is me and any((r["jobs"].get(f"{unit} / {n}") or ("",))[0] != "completed" for n in names):
            return "~", r["id"]
        return max(((r.get("starts") or {}).get(f"{unit} / {n}") or "" for n in names), default=""), r["id"]
    # One standing view per run for busy() and the source read alike (GATE-BUSY-REQUEUED-NEEDS):
    # a gate the overlay released judges the re-running run's need where busy() read it.
    others = [{**r, **dict(zip(("jobs", "starts"), standing(r)))} for r in others]
    for unit, names in required.items():
        src = None
        for r in sorted(others + [me], key=lambda r: fresh(r, names), reverse=True):
            if r["status"] == "action_required":
                continue
            t = parse_title(r["title"])
            if t is None:
                bad.append(f"run {r['id']}: unreadable title {r['title']!r}")
                continue
            if t[1] != pr or t[2] != judge_base or unit not in (
                    own if r is me and own is not None else workset(t[0], t[1])):
                continue
            js = [r["jobs"].get(f"{unit} / {n}") for n in names]
            if r is not me and all(j is not None and j[1] == "skipped" for j in js):
                continue                    # a unit that run deferred (C3) judged nothing: no source
            if r is not me and all(j is not None and j[1] in ("cancelled", "success") for j in js) and any(
                    j[1] == "cancelled" for j in js):
                continue                    # a cancelled unit judged nothing whole; a red beside it is the source
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
                bad.append(f"{unit} / {n}: ABSENT ({where})" if src is not me else f"{unit} / {n}{OWN_ABSENT}")
            elif st[0] != "completed":
                bad.append(f"{unit} / {n}: PENDING ({where})" if src is not me else f"{unit} / {n}{OWN_PENDING}")
            elif st[1] != "success":
                bad.append(f"{unit} / {n}: {st[1].upper() if st[1] == 'skipped' else st[1]} ({where})")
    return not bad, sorted(set(bad), key=bad.index)


def _pull(get, repo: str, pr: str) -> dict:
    st, _, lp = get(f"repos/{repo}/pulls/{pr}")
    if st != 200 or not isinstance(lp, dict):
        msg = lp.get("message", "") if isinstance(lp, dict) else ""
        raise ghapi.ApiError(f"repos/{repo}/pulls/{pr}", st, msg)
    return lp


def read_api(ctx: dict, claim: dict, reaches_cc, get) -> dict:
    """Every Actions and pulls read the predicate needs, in one place: the last step."""
    repo, (_, pr, _) = ctx["repo"], derive(ctx)
    starts: dict = {}
    jobs = run_jobs(get, repo, ctx["run_id"], starts)
    status, conclusion = jobs.get("prelude") or (None, None)
    api = {"prelude": {"status": status, "conclusion": conclusion, **claim}, "starts": starts,
           "jobs": jobs, "reaches_cc": reaches_cc, "live_pr": None, "open_pr_heads": set()}
    if pr and ctx["event_name"] != "merge_group":
        lp = _pull(get, repo, pr)
        api["live_pr"] = {"head_sha": lp["head"]["sha"], "base_ref": lp["base"]["ref"], "state": lp["state"],
                          "same_repo": (lp["head"].get("repo") or {}).get("full_name") == repo}
    elif ctx["event_name"] == "workflow_dispatch":
        api["open_pr_heads"] = {p["head"]["sha"] for p in ghapi.paginate(f"repos/{repo}/pulls", {"state": "open"}, get=get)}
    runs = ghapi.paginate(f"repos/{repo}/actions/workflows/ci.yml/runs", {"head_sha": ctx["head"]}, get=get)
    api["runs_at_head"] = []
    for r in runs:
        if r["id"] != ctx["run_id"]:
            st: dict = {}
            row = {"id": r["id"], "title": r.get("display_title") or "", "status": r["status"],
                   "attempt": r.get("run_attempt"), "run_started_at": r.get("run_started_at"),
                   "starts": st, "jobs": {} if r["status"] == "action_required"
                   else run_jobs(get, repo, r["id"], st)}
            if r["status"] not in ("completed", "action_required"):     # only an unfinished run is busy()'s to judge
                row["prior"] = prior_jobs(get, repo, row)
            api["runs_at_head"].append(row)
    return api


def reaches_custom_components(base: str, head: str) -> bool:
    """D-2's three-dot diff, from the checkout; unknown reads as reaching (fail closed)."""
    p = subprocess.run(["git", "diff", "--name-only", f"origin/{base}...{head}", "--", "custom_components/"],
                       capture_output=True, text=True)
    return p.returncode != 0 or bool(p.stdout.strip())


def machinery_line(jobs: dict, owed) -> str:
    """The push summary's one report-only line: the conclusion of every job of
    this run no class requires (the instrument self-tests, ci-ratchet, the
    other non-required jobs). It changes no verdict."""
    rest = [f"{k}={v[1] or v[0]}" for k, v in sorted(jobs.items()) if k not in owed]
    return "machinery (report-only, never gating): " + (", ".join(rest) or "no other job listed")


def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components, sleep=time.sleep,
          now=time.monotonic) -> tuple[str, list[str], list[str]]:
    """(outcome, reasons, this run's other jobs: reported, never gating). A verdict
    that only waits on this run's own lagging jobs (lag_bound) is never published
    while its bound allows a re-read; a deferral is published at once (DEFERRAL)."""
    kind, pr, base = derive(ctx)
    cc = reaches(base, ctx["head"]) if pr else None     # git first; the API reads are last (R3-1)
    t0, lagged = now(), []
    while True:
        api = read_api(ctx, claim, cc, get)
        ok, why = gate(ctx, api)
        if ok or now() - t0 + POLL_S > lag_bound(why):   # a deferral's bound is 0: published at once
            break
        lagged = lagged or why
        sleep(POLL_S)
    owed = {n for names in REQUIRED.values() for n in names} | {"prelude", "gate"}
    if ctx["event_name"] == "push":
        notes = [machinery_line(api["jobs"], owed)]
    else:
        notes = [f"{k}: {v[1] or v[0]}" for k, v in sorted(api["jobs"].items()) if k not in owed]
    if lagged:                                   # the listing lagged this run: say so (RCA countermeasure 4)
        notes.append(f"listing lag: {lagged[0]} re-read for {int(now() - t0)} s")
    return ("PASS" if ok else f"FAIL {why[0]}"), why, notes


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


def summary(outcome: str, why: list[str], notes=()) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write(f"### gate: {outcome.split()[0]}\n\n" + "".join(f"- {w}\n" for w in why)
                     + ("\nNot gating:\n" + "".join(f"- {x}\n" for x in notes) if notes else ""))


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
            import sweep                               # tools/ci/sweep.py, bound to this get/post
            return sweep.main(["--run", str(a.run)], get, post)
        ctx = context(env["GITHUB_EVENT_NAME"], json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text()), env)
        if a.refresh:
            rc, log = refresh(ctx, get, post)
            print("\n".join(log) or "NOTICE no green gate to refresh")
            return rc
        if a.kind is None or a.pr is None:
            print("FAIL usage: --pr N --base B --kind K (the prelude's outputs)")
            return 1
        claim = {"kind": a.kind, "pr": a.pr}
        if env.get("WORKSET") is not None:          # the prelude's workset output (ci.yml's gate step)
            claim["workset"] = set(env["WORKSET"].split())
        outcome, why, notes = judge(ctx, claim, get)
    except ghapi.RateLimited as e:
        outcome, why = f"RATE-LIMITED reset_epoch={e.reset_epoch} {e.path}", [str(e)]
        # The annotation is how the sweep tells this red from any other (check-runs/<job>/annotations).
        print(f"{outcome}\n::error title=RATE-LIMITED::reset_epoch={e.reset_epoch}")
        summary(outcome, why)
        return 3
    except ghapi.ApiError as e:
        outcome, why, notes = f"FAIL {e}", [str(e)], []
    print("\n".join([outcome] + why[1:]))
    summary(outcome, why, notes)
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
    check("D-2: arch-score only when the diff reaches custom_components/",
          set(REQUIRED["pr-cc"]) - set(REQUIRED["pr"]), {"arch-score / arch-score"})
    check("B3: push owes coverage-ratchet and no longer ci-ratchet (report-only)",
          ("tests / coverage-ratchet" in REQUIRED["push"], "tests / ci-ratchet" in gate_required()), (True, False))
    check("push owes no closure-scope and no body unit", [x for x in REQUIRED["push"] if "closure-scope" in x
                                                            or x.split(" / ")[0] in BODY], [])
    check("arch-instrument is required on every event class (U5b)",
          [c for c, names in sorted(REQUIRED.items()) if "tests / arch-instrument" not in names], [])
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
    extra = green + [{"name": "tests / nightly-status", "status": "completed", "conclusion": "failure"}]
    check("a red job no class requires is reported, never gating", judge(ctx, claim, fake(extra), cc)[::2],
          ("PASS", ["tests / nightly-status: failure"]))
    pctx = context("push", {}, {**env, "GITHUB_SHA": head})
    pclaim = {"kind": "code", "pr": ""}
    pgreen = [{"name": "prelude", "status": "completed", "conclusion": "success"}] + [
        {"name": x, "status": "completed", "conclusion": "success", "id": 1} for x in REQUIRED["push"]]
    ratchet_red = pgreen + [{"name": "tests / ci-ratchet", "status": "completed", "conclusion": "failure"}]
    check("null: a push with every job green prints the machinery line and passes",
          judge(pctx, pclaim, fake(pgreen), cc)[::2],
          ("PASS", ["machinery (report-only, never gating): no other job listed"]))
    check("a push with ci-ratchet red passes and reports it in the one machinery line",
          judge(pctx, pclaim, fake(ratchet_red + [{"name": "tests / selftest", "status": "completed",
                                                   "conclusion": "success"}]), cc)[::2],
          ("PASS", ["machinery (report-only, never gating): tests / ci-ratchet=failure, tests / selftest=success"]))
    cov_red = [dict(j, conclusion="failure") if j["name"] == "tests / coverage-ratchet" else j for j in ratchet_red]
    check("a push with coverage-ratchet red still fails", judge(pctx, pclaim, fake(cov_red), cc)[0],
          "FAIL tests / coverage-ratchet: failure (this run)")
    check("on a pull request the notes stay one line per job, no machinery line",
          [x for x in judge(ctx, claim, fake(green + ratchet_red[-1:]), cc)[2] if x.startswith("machinery")], [])
    red = [dict(j, conclusion="failure") if j["name"] == "tests / closures" else j for j in green]
    check("a red required job", judge(ctx, claim, fake(red), cc)[0], "FAIL tests / closures: failure (this run)")
    skip = [dict(j, conclusion="skipped") if j["name"] == "tests / browser" else j for j in green]
    check("a skipped required job (4.2)", judge(ctx, claim, fake(skip), cc)[0], "FAIL tests / browser: SKIPPED (this run)")
    naps = []
    check("a run without tests / arch-instrument (U5b): re-read, inside the ABSENT bound, then red",
          (judge(ctx, claim, fake([j for j in green if j["name"] != "tests / arch-instrument"]), cc, naps.append,
                 lambda: sum(naps))[0], 0 < sum(naps) <= GATE_ABSENT_MAX_S),
          ("FAIL tests / arch-instrument: ABSENT (this run)", True))
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
    # R10-HOTFIX-GATE-REDISPATCH-LOOP arm 1 (#3445): cancelling a newer redundant run left its jobs
    # completed and started latest, so it was the source and the gate read CANCELLED at the head.
    eapi = {**api, "prelude": {"conclusion": "success", "kind": "edit", "pr": "7"}, "jobs": body}
    ectx1 = {**ctx, "action": "edited"}
    tests_jobs = [k for k in jobs if k.startswith("tests / ")]

    def newer(conclude):
        return {"id": 95, "title": title("code", "7", "main"), "status": "completed", "starts": {k: "9" for k in jobs},
                "jobs": {k: (("completed", conclude(k)) if k in tests_jobs else v) for k, v in jobs.items()}}
    check("a newer cancelled run over an older green one at the head is no source: green",
          gate(ectx1, {**eapi, "runs_at_head": [older, newer(lambda k: "cancelled")]}), (True, []))
    check("null: a newer failed run over an older green one is the source: red",
          gate(ectx1, {**eapi, "runs_at_head": [older, newer(lambda k: "failure")]}),
          (False, [f"{k}: failure (run 95)" for k in tests_jobs]))
    first = tests_jobs[0]
    check("null: a newer run whose unit failed once and fail-fast cancelled the rest is the source: red",
          gate(ectx1, {**eapi, "runs_at_head": [older, newer(lambda k: "failure" if k == first else "cancelled")]}),
          (False, [f"{k}: {'failure' if k == first else 'cancelled'} (run 95)" for k in tests_jobs]))
    check("a newer run cancelled after part of its unit passed is no source either: the older green judges",
          gate(ectx1, {**eapi, "runs_at_head": [older, newer(lambda k: "success" if k == first else "cancelled")]}),
          (True, []))
    oldred = {**older, "jobs": {k: (("completed", "failure") if k in tests_jobs else v) for k, v in jobs.items()}}
    check("null: a newer green run over an older red one is the source: green",
          gate(ectx1, {**eapi, "runs_at_head": [oldred, newer(lambda k: "success")]}), (True, []))
    check("null: with only the cancelled run at the head the unit has no source: red",
          "tests: no run at this head judged base 'main'" in gate(ectx1, {**eapi, "runs_at_head": [
              newer(lambda k: "cancelled")]})[1], True)
    dctx = context("workflow_dispatch", {"inputs": {}}, env)
    dapi = {**api, "prelude": {"conclusion": "success", "kind": "code", "pr": ""}, "jobs": jobs, "runs_at_head": []}
    check("an unnamed dispatch at an open PR's head is refused", gate(dctx, {**dapi, "open_pr_heads": {"M"}})[1],
          ["this SHA heads an open PR: dispatch with -f pr=N -f base=REF"])
    check("... and judged as usual at no PR's head (null)", gate(dctx, {**dapi, "open_pr_heads": {"X"}}), (True, []))
    # R10-GATE-DEFER: a deferral never passes early; r10-gate-busy-defer-3: it is published at once.
    def owed(kind, gate=True, red=(), state="completed"):
        names = ["prelude"] + [f"{u} / {n}" for u in sorted(workset(kind, "7") & set(UNITS)) for n in UNITS[u]]
        return ([{"name": x, "status": state if x != "prelude" else "completed",
                  "conclusion": ("failure" if x in red else "success") if state == "completed" or x == "prelude"
                  else None, "id": 1} for x in names]
                + ([{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}] if gate else []))

    def run(i, kind, status, jobs):
        return {"id": i, "display_title": title(kind, "7", "main", "M"), "status": status, "jobs": jobs}

    def scene(*frames, me=100, mine=None):
        """A get whose runs and jobs at the head move one frame per nap; `now` is the naps' sum."""
        naps = []

        def get(path, params=None):
            if sum(naps) > 2 * GATE_WAIT_MAX_S:
                raise TimeoutError("waited past twice the bound")
            frame = frames[min(len(naps), len(frames) - 1)]
            if path.endswith("/pulls/7"):
                return 200, {}, pull
            if path.endswith("ci.yml/runs"):
                return 200, {}, {"workflow_runs": [{k: v for k, v in r.items() if k != "jobs"} for r in frame]}
            rid = int(path.split("/runs/")[1].split("/")[0])
            if rid == me:
                return 200, {}, {"jobs": mine or green}
            return 200, {}, {"jobs": next(r["jobs"] for r in frame if r["id"] == rid)}
        return get, naps, naps.append, lambda: sum(naps)

    def verdict(c, get, nap, now, kl=claim):
        try:
            return judge(c, kl, get, cc, nap, now)[0]
        except TimeoutError as e:
            return f"UNBOUNDED: {e}"

    def defer_then(c, first, then, kl=claim, me=100, mine=None):
        """(verdict over `first`, its naps, the verdict gate-sweep.yml's re-run reads over `then`)."""
        get, naps, nap, now = scene(first, me=me, mine=mine)
        out = verdict(c, get, nap, now, kl)
        get, _, nap, now = scene(then, me=me, mine=mine)
        return out, naps, verdict(c, get, nap, now, kl)

    def deferred(*ids):
        return "FAIL " + deferral(list(ids))
    in_prelude = [{"name": "prelude", "status": "in_progress", "conclusion": None, "id": 1}]
    check("R3-2: a run whose gate is listed but an owed job is not still adds a source",
          busy(ctx, [{"id": 99, "title": title("code", "7", "main", "M"), "status": "in_progress",
                      "jobs": {"gate": ("completed", "success")}}]), [99])
    # r10-gate-busy-defer-3: a deferral is published at once and holds no runner; gate-sweep.yml
    # re-runs the gate once the decider concludes (sweep.py: green branch, or `settle`), and that
    # re-run reads the decided head: `defer_then`'s third value.
    check("#2754 shape: a gate beside a busy edit run and a queued review run defers at once, no nap; "
          "re-run once they decide, it judges",
          defer_then(ctx, [run(101, "edit", "in_progress", in_prelude), run(102, "review", "queued", [])],
                     [run(101, "edit", "in_progress", owed("edit")), run(102, "review", "in_progress", owed("review"))]),
          (deferred(101, 102), [], "PASS"))
    check("simultaneous completion, side A: the other's gate not yet listed -> the deferral at once; re-run, "
          "it judges", defer_then(ctx, [run(101, "code", "in_progress", owed("code", gate=False))],
                                  [run(101, "code", "in_progress", owed("code"))]), (deferred(101), [], "PASS"))
    bctx = {**ctx, "run_id": 101}
    check("simultaneous completion, side B: the same, red-red at once, which settle re-runs (sweep self-test), "
          "and each re-run judges",
          defer_then(bctx, [run(100, "code", "in_progress", owed("code", gate=False)),
                            run(101, "code", "in_progress", owed("code"))],
                     [run(100, "code", "in_progress", owed("code")), run(101, "code", "in_progress", owed("code"))],
                     me=101), (deferred(100), [], "PASS"))
    check("a deferring gate re-judged after the decider's red is that red, never a PASS",
          defer_then(ctx, [run(101, "edit", "in_progress", owed("edit", gate=False, state="in_progress"))],
                     [run(101, "edit", "completed", owed("edit", red=("pr-contract / pr-contract",)))]),
          (deferred(101), [], "FAIL pr-contract / pr-contract: failure (run 101)"))
    # C3 (option A): an edit run beside a code run that has not started its
    # pr-contract ran arch-score and budget-raise-gate only; its caller job
    # `pr-contract` is listed skipped, under the caller's bare name.
    ectx = context("pull_request", {**ev, "action": "edited"}, env)
    deferred_jobs = [{"name": "prelude", "status": "completed", "conclusion": "success", "id": 1},
                {"name": "arch-score / arch-score", "status": "completed", "conclusion": "success", "id": 1},
                {"name": "budget-raise-gate / budget-raise-gate", "status": "completed", "conclusion": "success",
                 "id": 1},
                {"name": "pr-contract", "status": "completed", "conclusion": "skipped", "id": 1}]
    eclaim3 = {"kind": "edit", "pr": "7", "workset": {"arch-score", "budget-raise-gate"}}
    busy_code = [run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))]
    check("C3: a deferring edit gate beside a busy code run defers at once, no nap; re-run once the code run "
          "ends, it judges its sources",
          defer_then(ectx, busy_code, [run(99, "code", "completed", owed("code"))], eclaim3, mine=deferred_jobs),
          (deferred(99), [], "PASS"))
    get, naps, nap, now = scene(busy_code, mine=deferred_jobs)
    check("... null control: the same gate with the full edit workset defers at once too (no gate holds a runner)",
          (verdict(ectx, get, nap, now, {"kind": "edit", "pr": "7"}), naps), (deferred(99), []))
    # r10-gate-busy-defer: #3241 head 95c7e604, attempt 2 -- two deferring edit
    # runs, each gate listed, each read the other as busy (its pr-contract never
    # listed), so both published the deferral and no gate judged. judging() now
    # reads that listing as judging (r10-gate-busy-defer-2); the id tie-break still
    # orders two started gates whose listing lags a caller already resolved (a gate
    # needs pr-contract, so its `pr-contract` read unfinished is the listing's lag).
    lo, hi = 42192623509, 42193153511
    at_gate = deferred_jobs + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
    lagging = [dict(j, status="in_progress", conclusion=None) if j["name"] == "pr-contract" else j for j in at_gate]
    pair = [{"id": i, "title": title("edit", "7", "main", "M"), "status": "in_progress",
             "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in lagging}} for i in (lo, hi)]
    check("busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower",
          (busy({**ctx, "run_id": lo}, pair), busy({**ctx, "run_id": hi}, pair)), ([], [lo]))
    # #3244 at a2582125, attempt 2: three edit gates started 21:46:18-20Z, after the code run's gate
    # went green (21:45:53Z), and each deferred to the other two under pinned program 9cbd7dd0 (before
    # #3246), so none judged. With every caller's listing lagging, the ids still leave one judging.
    trio = [{**pair[0], "id": i} for i in (42286558101, 42286624031, 42293328283)]
    check("busy-defer, three gates (#3244): the lowest defers to none, each other only to the gates below it",
          [busy({**ctx, "run_id": r["id"]}, trio) for r in trio],
          [[], [trio[0]["id"]], [trio[0]["id"], trio[1]["id"]]])
    honest = [{**r, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in at_gate}} for r in pair]
    check("busy-defer-2: listed as GitHub lists it (`pr-contract` skipped), neither started gate waits on the other",
          (busy({**ctx, "run_id": lo}, honest), busy({**ctx, "run_id": hi}, honest)), ([], []))
    coded = run(99, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed",
                                                                "conclusion": "success", "id": 9}])
    get, naps, nap, now = scene([coded, run(hi, "edit", "in_progress", at_gate)], me=lo, mine=deferred_jobs)
    check("busy-defer: the lower deferring edit gate judges at once beside the higher one",
          (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("PASS", []))
    check("busy-defer: the higher deferring edit gate defers at once to the lower whose listing lags; re-run, "
          "it judges", defer_then({**ectx, "run_id": hi}, [coded, run(lo, "edit", "in_progress", lagging)],
                                  [coded, run(lo, "edit", "completed", deferred_jobs + [
                                      {"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])],
                                  eclaim3, me=hi, mine=deferred_jobs), (deferred(lo), [], "PASS"))
    get, naps, nap, now = scene([coded, run(lo, "edit", "in_progress", at_gate)], me=hi, mine=deferred_jobs)
    check("busy-defer-2: the higher deferring edit gate beside the lower one listed as GitHub lists it judges at once",
          (verdict({**ectx, "run_id": hi}, get, nap, now, eclaim3), naps), ("PASS", []))
    early = [{"id": lo, "title": title("code", "7", "main", "M"), "status": "in_progress",
              "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in owed("code", gate=False, state="in_progress")}}]
    check("busy-defer null: a genuinely earlier run still adding sources is still deferred to",
          busy({**ctx, "run_id": hi}, early), [lo])
    late_busy = [{**early[0], "id": hi}]
    check("busy-defer null: a later run whose gate is not listed is still deferred to (no gate yet: it adds sources)",
          busy({**ctx, "run_id": lo}, late_busy), [hi])
    late_waiting = [{**early[0], "id": hi, "jobs": {**early[0]["jobs"], "gate": ("waiting", None)}}]
    check("busy-defer null (R3-2 EARLY): a later run whose gate is listed `waiting` beside running units is "
          "still deferred to", busy({**ctx, "run_id": lo}, late_waiting), [hi])
    # #3246 review: the same deferring gate (lo) beside a LATER edit run (hi) still
    # in its prelude, the code run done. hi's prelude read lo busy, so #3246 made lo
    # publish at once; judging() now reads lo judging, so lo waits on hi, acyclic.
    for label, hi_jobs in (("still in its prelude", in_prelude),
                           ("in its prelude, gate listed `waiting` (R3-2)",
                            in_prelude + [{"name": "gate", "status": "waiting", "conclusion": None, "id": 9}])):
        check(f"prelude/gate order: a deferring gate beside a later edit run {label} defers to it at once (that "
              "run's prelude no longer waits on this one); re-run, it judges",
              defer_then({**ectx, "run_id": lo}, [coded, run(hi, "edit", "in_progress", hi_jobs)],
                         [coded, run(hi, "edit", "completed", owed("edit")[:-1] + [
                             {"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])],
                         eclaim3, me=lo, mine=deferred_jobs), (deferred(hi), [], "PASS"))
    # #3246 round 2: the same scene with an EARLIER deferring edit run whose gate has
    # started beside hi: that earlier run is judging, so lo waits on hi alone.
    early_gate = 42192000000
    egr = run(early_gate, "edit", "in_progress", deferred_jobs + [{"name": "gate", "status": "in_progress",
                                                              "conclusion": None, "id": 9}])
    check("prelude/gate order: beside an earlier started deferring gate and a later edit run in its prelude, "
          "it defers to the later run only; re-run, it judges",
          defer_then({**ectx, "run_id": lo}, [coded, egr, run(hi, "edit", "in_progress", in_prelude)],
                     [coded, egr, run(hi, "edit", "completed", owed("edit")[:-1] + [
                         {"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])],
                     eclaim3, me=lo, mine=deferred_jobs), (deferred(hi), [], "PASS"))
    lo_run = {"id": lo, "title": title("edit", "7", "main", "M")}
    gate_run = {"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}
    check("the cycle's other edge: a deferring run at its gate is judging (its bare `pr-contract` caller "
          "skipped), so no prelude or gate waits on it",
          judging({**lo_run, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in deferred_jobs + [gate_run]}}),
          True)
    check("... null: a caller still running (not completed) still owes its unit",
          judging({**lo_run, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in
                                      [dict(j, status="in_progress", conclusion=None) if j["name"] == "pr-contract"
                                       else j for j in deferred_jobs] + [gate_run]}}), False)
    done_edit = run(101, "edit", "completed", deferred_jobs + [{"name": "gate", "status": "completed",
                                                           "conclusion": "failure", "id": 9}])
    get, naps, nap, now = scene([done_edit])
    check("C3: the code run's gate takes the edit run's body units, its own pr-contract (it read the latest body)",
          verdict(ctx, get, nap, now), "PASS")
    skipped_named = {**done_edit, "jobs": [j if j["name"] != "pr-contract" else
                                           {**j, "name": "pr-contract / pr-contract"} for j in done_edit["jobs"]]}
    get, naps, nap, now = scene([skipped_named])
    check("C3: a unit a run deferred is no source even under its full job name (skipped)",
          verdict(ctx, get, nap, now), "PASS")
    red_edit = {**done_edit, "jobs": [j if j["name"] != "arch-score / arch-score" else
                                      {**j, "conclusion": "failure"} for j in done_edit["jobs"]]}
    get, naps, nap, now = scene([red_edit])
    check("C3: the edit run's red arch-score (the latest body) is the code gate's source, not its own older green",
          verdict(ctx, get, nap, now), "FAIL arch-score / arch-score: failure (run 101)")
    # r10-ci-edit-runner 27233708: GitHub numbered the edit run BELOW its code run (27 of 94 same-second
    # pairs), so the code run's own arch-score shadowed the edit run's read of the latest body by id alone.
    def stamped(jobs, at):
        return [dict(j, started_at=at.get(j["name"], "2026-11-01T10:00:00Z")) for j in jobs]
    arch = "arch-score / arch-score"
    for label, at, want in (("started after the code run's own", "2026-11-01T10:05:00Z",
                             "FAIL arch-score / arch-score: failure (run 99)"),
                            ("null: started before it", "2026-11-01T09:55:00Z", "PASS")):
        get, naps, nap, now = scene([{**red_edit, "id": 99, "jobs": stamped(red_edit["jobs"], {arch: at})}],
                                    mine=stamped(green, {}))
        check(f"source order: a LOWER-id edit run's red arch-score {label} -> the code gate reads the later start",
              verdict(ctx, get, nap, now), want)
    lagged = [dict(j, status="queued", conclusion=None, started_at=None) if j["name"] == arch else j
              for j in stamped(green, {})]
    get, naps, nap, now = scene([{**done_edit, "id": 101, "jobs": stamped(done_edit["jobs"], {arch: "2026-11-01T10:05:00Z"})}],
                                mine=lagged)
    check("source order null: this run's own unit, listed lagging, is never displaced by a later sibling's green",
          verdict(ctx, get, nap, now), "FAIL arch-score / arch-score: PENDING (this run)")
    for label, red, want in (("green", (), "PASS"),
                             ("its pr-contract red", ("pr-contract / pr-contract",),
                              "FAIL pr-contract / pr-contract: failure (run 99)")):
        get, naps, nap, now = scene([run(99, "code", "completed", owed("code", red=red))], me=101, mine=deferred_jobs)
        check(f"C3: the deferred gate re-judged once the code run ended ({label}) is that run's verdict",
              verdict({**ectx, "run_id": 101}, get, nap, now, eclaim3), want)
    late = deferred_jobs[:3] + [{"name": "pr-contract / pr-contract", "status": "completed", "conclusion": "failure",
                            "id": 1}]
    get, naps, nap, now = scene([run(99, "code", "completed", owed("code"))], mine=late)
    check("C3: a body edited after the code run's gate passed is still judged (this run's own pr-contract)",
          verdict(ectx, get, nap, now, {**eclaim3, "workset": set(BODY_UNITS)}),
          "FAIL pr-contract / pr-contract: failure (this run)")
    get, naps, nap, now = scene([run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))])
    check("a deferral FAILs at once (for gate-sweep.yml) and holds no runner: no nap",
          (verdict(ctx, get, nap, now), naps), (deferred(99), []))
    get, naps, nap, now = scene([run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))])
    check("a decided red never waits: the prelude cross-check beside a busy run",
          (verdict(ctx, get, nap, now, {"kind": "code", "pr": ""}).startswith("FAIL prelude says"), naps), (True, []))
    get, naps, nap, now = scene([])
    check("null: no other run at the head, no wait", (verdict(ctx, get, nap, now), naps), ("PASS", []))
    reds = [run(i, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed",
                                                                "conclusion": "failure", "id": 9}]) for i in (90, 91, 92)]
    check("rerun cascade: three completed red deferring gates, a queued decider, and a re-run of an older gate: "
          "it defers to the decider only, at once; re-run once that decides, it judges",
          defer_then({**ctx, "run_attempt": 2}, reds + [run(99, "review", "queued", [])],
                     reds + [run(99, "review", "in_progress", owed("review"))]), (deferred(99), [], "PASS"))
    rerun = run(100, "code", "in_progress", owed("code")[:-1] + [{"name": "gate", "status": "queued",
                                                                  "conclusion": None, "id": 9}])
    check("... and the decider never waits on that re-run: a run whose only open job is its gate is judging",
          busy({**ctx, "run_id": 99}, [{**r, "title": r["display_title"],
                                        "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in r["jobs"]}}
                                       for r in reds + [rerun]]), [])
    # r10-gate-busy-defer-2: replay recorded runs (#3263, #3261) through judge() as the API read then.
    fx = json.loads((HERE / "fixtures" / "gate_busy_defer_runs.json").read_text())
    frepo = fx["repo"]

    def epoch(x):
        return None if x is None else datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp()

    def at_time(rows, t):
        """The Actions API as it read at epoch t, from the recorded timestamps."""
        out = []
        for r in rows:
            if epoch(r["created_at"]) > t:
                continue
            jobs = []
            for j in r["jobs"]:
                if epoch(j["created_at"]) > t:
                    continue
                if j["status"] == "completed" and j["completed_at"] and epoch(j["completed_at"]) <= t:
                    st, cc_ = "completed", j["conclusion"]
                elif j.get("started_at") and epoch(j["started_at"]) <= t:
                    st, cc_ = "in_progress", None
                else:
                    st, cc_ = "queued", None
                jobs.append({"name": j["name"], "status": st, "conclusion": cc_, "id": 1})
            done = r["status"] == "completed" and epoch(r["updated_at"]) <= t
            out.append({"id": r["id"], "display_title": r["display_title"],
                        "status": "completed" if done else "in_progress", "jobs": jobs})
        return out

    def fx_ctx(head, pr, rid, attempt):
        return context("pull_request", {"action": "edited", "pull_request": {"number": int(pr),
                       "base": {"ref": "main"}, "head": {"sha": head}}},
                       {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": frepo, "GITHUB_RUN_ID": str(rid),
                        "GITHUB_RUN_ATTEMPT": str(attempt)})

    def fx_me(head, rid):
        me = next(r for r in fx["heads"][head] if r["id"] == rid)
        t0 = epoch(next(j for j in me["jobs"] if j["name"] == "gate")["judge_started_at"])
        return me, t0, parse_title(me["display_title"])

    def replay(head, rid, at=None):
        """judge() over the recording from the gate's `Judge this head` start, or from epoch `at`."""
        rows = fx["heads"][head]
        me, t0, pt = fx_me(head, rid)
        t0 = t0 if at is None else at
        pr, naps = pt[1], []

        def get(path, params=None):
            if sum(naps) > 2 * GATE_WAIT_MAX_S:
                raise TimeoutError("waited past twice the bound")
            rs = at_time(rows, t0 + sum(naps))
            if path.endswith(f"/pulls/{pr}"):
                return 200, {}, {"state": "open", "head": {"sha": head, "repo": {"full_name": frepo}},
                                 "base": {"ref": "main"}}
            if path.endswith("ci.yml/runs"):
                return 200, {}, {"workflow_runs": [{k: r[k] for k in ("id", "display_title", "status")} for r in rs]}
            i = int(path.split("/runs/")[1].split("/")[0])
            return 200, {}, {"jobs": next(r["jobs"] for r in rs if r["id"] == i)}
        c = fx_ctx(head, pr, rid, me["run_attempt"])
        fclaim = {"kind": pt[0], "pr": pr, "workset": set(fx["gates"][str(rid)]["workset"].split())}
        try:
            return judge(c, fclaim, get, lambda b, h: True, naps.append, lambda: sum(naps))[0], naps
        except TimeoutError:
            return "UNBOUNDED", naps
    h3263, edit3263, code3263 = "02e92e7cbcb95c32fbb2ad3a7a46a8d465a436d8", 42338396358, 42338396871
    out, naps = replay(h3263, edit3263)
    check("#3263 (42338396358 beside code run 42338396871): the deferring edit gate publishes CI's deferral "
          "at once, no nap", (out, naps), (fx["gates"][str(edit3263)]["verdict"], []))
    _, t0, _ = fx_me(h3263, edit3263)
    seen = [{"id": r["id"], "title": r["display_title"], "status": r["status"],
             "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in r["jobs"]}}
            for r in at_time(fx["heads"][h3263], t0) if r["id"] != code3263]
    check("#3263: the code run's gate never waits on that deferring edit run (the edge that closed the cycle)",
          busy(fx_ctx(h3263, "3263", code3263, 1), seen), [])
    for rid in (42307493684, 42307798573):
        check(f"#3261 ({rid}, its sibling edit run at its gate): judges, never the pair's deferral",
              replay("e17fadc1795ebbaaf0f01ed067fbb59aeba90dee", rid)[0], "PASS")
    # r10-gate-busy-defer-3: #3282 at 024a0201, the recorded edit gate 42367457809 (attempt 1) beside code
    # run 42367457479 and review run 42367461228. Live it waited 11:18-11:30Z and failed deferring.
    h3282, edit3282, code3282 = "024a0201fbd531e21c0caef4f522a71711acea10", 42367457809, 42367457479
    out, naps = replay(h3282, edit3282)
    check("#3282: the deferring edit gate publishes CI's deferral at once and holds no runner",
          (out, naps), (fx["gates"][str(edit3282)]["verdict"], []))
    import sweep as sweep_mod                       # gate-sweep.yml's program, over the same recording
    rows3282 = fx["heads"][h3282]
    t_sweep = epoch(next(r for r in rows3282 if r["id"] == code3282)["updated_at"]) + 12   # its live read: +11 s

    def swept(t, red=True):
        """at_time's listing in sweep.py's shape; the edit gate's attempt 1 completed red, no human re-run."""
        out = []
        for r in at_time(rows3282, t):
            rec = next(x for x in rows3282 if x["id"] == r["id"])
            jobs = []
            for j, rj in zip(r["jobs"], [x for x in rec["jobs"] if epoch(x["created_at"]) <= t]):
                j = {**j, "id": r["id"] * 10 if j["name"] == "gate" else 1, "started_at": rj["started_at"],
                     "completed_at": rj["completed_at"] if j["status"] == "completed" else None}
                if r["id"] == edit3282 and j["name"] == "gate" and red:
                    j.update(status="completed", conclusion="failure")
                jobs.append(j)
            out.append({**r, "created_at": rec["created_at"], "run_attempt": 1, "path": sweep_mod.CI_PATH,
                        "head_sha": h3282, "pull_requests": [{"number": 3282}], "jobs": jobs})
        return out
    clock3282, posts3282 = [t_sweep], []

    def sget(path, params=None):
        rs = swept(clock3282[0])
        if path.endswith("/pulls/3282"):
            return 200, {}, {"head": {"sha": h3282}}
        if path.endswith("/actions/runs"):
            return 200, {}, {"workflow_runs": rs}
        i = int(path.split("/runs/")[1].split("/")[0])
        r = next(r for r in rs if r["id"] == i)
        return 200, {}, ({"jobs": r["jobs"]} if path.endswith("/jobs") else r)
    sweep_mod.main(["--run", str(code3282), "--repo", frepo], sget,
                   lambda path, body=None: (posts3282.append(path), (201, {}, {}))[1], lambda x: None,
                   lambda s: clock3282.__setitem__(0, clock3282[0] + s), lambda: clock3282[0])
    check("#3282: the sweep for the code run's completion re-runs that deferring gate, no human",
          posts3282, [f"repos/{frepo}/actions/jobs/{edit3282 * 10}/rerun"])
    check("#3282: ... and that re-run, judged over the recording 20 s later, passes (the code run decided green)",
          replay(h3282, edit3282, at=t_sweep + 20), ("PASS", []))
    # R10-HOTFIX-GATE-STALE-JOBS: this run's own jobs read stale, then fresh.
    def own(*frames):
        naps = []

        def get(path, params=None):
            if sum(naps) > 2 * GATE_WAIT_MAX_S:
                raise TimeoutError("waited past twice the bound")
            if path.endswith("/runs/100/jobs"):
                return 200, {}, {"jobs": frames[min(len(naps), len(frames) - 1)]}
            return fake()(path, params)
        return get, naps, naps.append, lambda: sum(naps)

    def jset(**over):
        return [dict(j, **over[j["name"]]) if j["name"] in over else j for j in green]
    lag = {"status": "in_progress", "conclusion": None}
    stale = jset(**{"tests / mutation": lag, "tests / closures": lag})
    get, naps, nap, now = own(stale, green)
    check("run 41870314676 shape: own jobs read in_progress, then completed -> one re-read, PASS",
          (verdict(ctx, get, nap, now), naps), ("PASS", [POLL_S]))
    get, naps, nap, now = own(jset(**{"tests / mutation": lag, "tests / closures": {"conclusion": "failure"}}), green)
    out, why, _ = judge(ctx, claim, get, cc, nap, now)
    check("null: a unit really failed beside a lagging one stays red, no wait",
          (out.startswith("FAIL"), "tests / closures: failure (this run)" in why, naps), (True, True, []))
    get, naps, nap, now = own(stale)
    out = verdict(ctx, get, nap, now)
    check("null: own jobs still pending past the bound stay red, the wait inside the bound",
          (out, bool(naps), sum(naps) <= GATE_WAIT_MAX_S), ("FAIL tests / mutation: PENDING (this run)", True, True))
    get, naps, nap, now = own(jset(**{"tests / browser": {"conclusion": "skipped"}}), green)
    check("null: a skipped own unit is unchanged, no wait",
          (verdict(ctx, get, nap, now), naps), ("FAIL tests / browser: SKIPPED (this run)", []))
    pend = {"status": "in_progress", "conclusion": None}
    get, naps, nap, now = own(stale, green)
    check("a cleared lag is noticed: one note names the job and the wait; a fresh listing notes nothing (null)",
          ([x for x in judge(ctx, claim, get, cc, nap, now)[2] if x.startswith("listing lag")],
           [x for x in judge(ctx, claim, fake(), cc)[2] if x.startswith("listing lag")]),
          (["listing lag: tests / mutation: PENDING (this run) re-read for 60 s"], []))
    get, naps, nap, now = own(jset(prelude=pend), green)
    check("41863133083 shape: prelude listed unfinished, then success -> one re-read, PASS",
          (verdict(ctx, get, nap, now), naps), ("PASS", [POLL_S]))
    get, naps, nap, now = own(jset(prelude=pend), jset(prelude={"conclusion": "failure"}))
    check("41094975103 shape: prelude listed unfinished, then failure -> its true reason, after the re-read",
          (verdict(ctx, get, nap, now), naps), ("FAIL prelude: failure", [POLL_S]))
    get, naps, nap, now = own([j for j in green if j["name"] != "prelude"])
    check("null: prelude not listed at all is no lag, no wait (only a listed unfinished prelude waits)",
          (verdict(ctx, get, nap, now), naps), ("FAIL prelude: None", []))
    get, naps, nap, now = own([j for j in green if j["name"] != "pr-contract / pr-contract"], green)
    check("41289450679 shape: an own job not yet listed, then listed -> one re-read, PASS",
          (verdict(ctx, get, nap, now), naps), ("PASS", [POLL_S]))
    get, naps, nap, now = own(jset(**{"tests / mutation": lag}), [j for j in green if j["name"] != "hassfest / hassfest"])
    out = verdict(ctx, get, nap, now)
    check("an own job never listed stays red, its wait inside the shorter ABSENT bound",
          (out, 0 < sum(naps) <= GATE_ABSENT_MAX_S), ("FAIL hassfest / hassfest: ABSENT (this run)", True))
    ectx, eclaim = {**ctx, "action": "edited"}, {"kind": "edit", "pr": "7"}
    get, naps, nap, now = own([j for j in green if j["name"] == "prelude" or j["name"].split(" / ")[0] in BODY])
    out, why, _ = judge(ectx, eclaim, get, cc, nap, now)
    check("null (workset): an edit run lists no code unit; that is no ABSENT and no wait",
          (out.startswith("FAIL") and any(w.endswith("judged base 'main'") for w in why),
           [w for w in why if "ABSENT" in w], naps), (True, [], []))
    import re
    ci = (HERE.parents[1] / ".github" / "workflows" / "ci.yml").read_text()
    m = re.search(r"\n  gate:\n(?:    .*\n)*?    timeout-minutes: (\d+)\n", ci)
    check("the ABSENT bound is shorter than the pending bound, and pinned to two polls",
          (GATE_ABSENT_MAX_S < GATE_WAIT_MAX_S, GATE_ABSENT_MAX_S), (True, 120))
    check("the wait bound, one poll and two minutes fit the gate job's timeout-minutes",
          bool(m) and GATE_WAIT_MAX_S + POLL_S + 120 <= int(m.group(1)) * 60, True)

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
            if want == 3:
                check("the sweep's annotation", buf.getvalue().split("\n")[1], "::error title=RATE-LIMITED::reset_epoch=1700000000")
        check("the 403's reason is printed", "HTTP 403 Resource not accessible" in first, True)
        import types
        calls, saved = [], sys.modules.get("sweep")
        try:
            import sweep
            check("--sweep binds tools/ci/sweep.py", Path(sweep.__file__).resolve(), HERE / "sweep.py")
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
    # GATE-BUSY-REQUEUED-NEEDS: a gate re-run re-queues its skipped needs; the run is then busy() to
    # every other gate until they finish. The constructed two-attempt fixture (attempt 1 every need
    # concluded, attempt 2 `pr-contract / pr-contract` queued) is read through read_api().
    rq = json.loads((HERE / "fixtures" / "gate_requeued_needs_runs.json").read_text())
    rq_id = rq["run"]["id"]
    me_id = rq_id + 1                       # the higher id: a started gate beside it is not excused by busy()'s tie-break
    rq_ctx = {**ctx, "run_id": me_id}

    def requeue_world(attempt=2, prior=None, status=200, listing=None):
        reads = []

        def get(path, params=None):
            if path.endswith("/pulls/7"):
                return 200, {}, pull
            if path.endswith("ci.yml/runs"):
                return 200, {}, {"workflow_runs": [{"id": me_id, "display_title": "x", "status": "in_progress", "run_attempt": 1},
                                                   {**rq["run"], "run_attempt": attempt}]}
            if path.endswith(f"/runs/{me_id}/jobs"):
                return 200, {}, {"jobs": green}
            if path.endswith(f"/runs/{rq_id}/jobs"):
                return 200, {}, {"jobs": listing or rq["attempts"]["2"]}
            if "/attempts/" in path:
                reads.append(path)
                return status, {}, {"jobs": prior or rq["attempts"]["1"]}
            raise AssertionError(path)
        return get, reads

    def requeue_busy(**kw):
        import contextlib
        import io
        get, reads = requeue_world(**kw)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            api = read_api(rq_ctx, claim, True, get)
        return busy(rq_ctx, api["runs_at_head"]), len(reads), err.getvalue()
    got = requeue_busy()
    check("requeued needs: a run whose only unfinished job is its re-queued need, finished in attempt 1, is not "
          "busy; one extra read", got[:2], ([], 1))
    got = requeue_busy(attempt=1)
    check("requeued needs null: a single-attempt run makes no extra read, and its unfinished need keeps it busy",
          got[:2], ([rq_id], 0))
    pend = [dict(j, status="queued", conclusion=None) if j["name"] == "pr-contract / pr-contract" else j
            for j in rq["attempts"]["1"]]
    got = requeue_busy(prior=pend)
    check("requeued needs null: a need unfinished in the previous attempt too is still busy()", got[:2], ([rq_id], 1))
    got = requeue_busy(status=404)
    check("requeued needs: an unreadable previous attempt keeps today's reading and logs why",
          (got[0], got[1], "unread" in got[2] and "HTTP 404" in got[2]), ([rq_id], 1, True))
    got = requeue_busy(listing=rq["attempts"]["1"])
    check("requeued needs null: an attempt-2 run with every need finished makes no extra read",
          got[:2], ([], 0))
    got = requeue_busy(prior=[j for j in rq["attempts"]["1"] if j["name"] != "pr-contract / pr-contract"])
    check("requeued needs null: a need the previous attempt never listed stays busy", got[:2], ([rq_id], 1))
    # Repair round (review blocked at 868f8a72): the overlay's domain is the run's OWN gate re-run, and
    # gate()'s source read takes the same standing view as busy(). A need is read from the previous
    # attempt only when (R1) the run is past attempt 1, (R2) the latest attempt did not re-run the
    # prelude (a re-run-all did: its prelude started at or after run_started_at), (R3) the need is
    # owed and listed unfinished, and (R4) its previous attempt concluded success or skipped; a
    # failed, cancelled or timed-out need is what "re-run failed jobs" re-queues, a new source.
    MUT, PRC = "tests / mutation", "pr-contract / pr-contract"
    a1 = {j["name"]: j for j in rq["attempts"]["1"]}
    queued = {"status": "queued", "conclusion": None, "started_at": None}

    def shape(was=None, now=None):
        return ([dict(j, **(was or {}).get(j["name"], {})) for j in rq["attempts"]["1"]],
                [dict(j, **(now or {}).get(j["name"], {})) for j in rq["attempts"]["2"]])
    p1, l2 = shape({MUT: {"conclusion": "failure"}, "gate": {"conclusion": "failure"}},
                   {MUT: queued, "gate": queued, PRC: a1[PRC]})
    check("requeued needs, re-run failed jobs: a unit that failed in attempt 1 and is queued again keeps the run "
          "busy (the reviewer's attack shape)", requeue_busy(prior=p1, listing=l2)[:2], ([rq_id], 1))
    p1, l2 = shape({MUT: {"conclusion": "cancelled"}}, {MUT: queued})
    check("requeued needs, re-run failed jobs: a unit cancelled in attempt 1 and queued again keeps the run busy",
          requeue_busy(prior=p1, listing=l2)[:2], ([rq_id], 1))
    p1, l2 = shape({MUT: {"conclusion": "failure"}}, {MUT: queued})
    check("requeued needs, re-run failed jobs beside the re-queued need: the failed unit still holds the run busy",
          requeue_busy(prior=p1, listing=[dict(j, **queued) if j["name"] == PRC else j for j in l2])[:2], ([rq_id], 1))
    rerun_all = [dict(j, started_at="2026-11-11T14:09:00Z") if j["status"] == "completed" else j
                 for j in rq["attempts"]["2"]]
    check("requeued needs, re-run all: the prelude re-ran in this attempt, so a queued need is a new source: busy, "
          "no extra read", requeue_busy(listing=rerun_all)[:2], ([rq_id], 0))
    check("requeued needs, re-run all: a prelude still queued in this attempt: busy, no extra read",
          requeue_busy(listing=[dict(j, **queued) if j["name"] == "prelude" else j for j in rerun_all])[:2],
          ([rq_id], 0))
    p1, _ = shape({PRC: {"conclusion": "skipped"}})
    check("requeued needs: a need the previous attempt skipped (C3, the gate re-run's documented re-queue) is not "
          "busy", requeue_busy(prior=p1)[:2], ([], 1))
    no_start = {**rq["run"]}
    no_start.pop("run_started_at")
    rq_saved, rq["run"] = rq["run"], no_start
    check("requeued needs null: a run listing no run_started_at keeps today's reading: busy, no extra read",
          requeue_busy()[:2], ([rq_id], 0))
    rq["run"] = rq_saved
    # One-sided (verdict point 2): a gate released by the overlay judges the re-running run's unit from
    # the same standing source busy() read, never from an older run behind it.
    get, _ = requeue_world()
    api = read_api(rq_ctx, claim, True, get)
    stale = {k: v for k, v in api["runs_at_head"][0]["jobs"].items()}
    api["runs_at_head"].append({"id": 5, "title": title("code", "7", "main"), "status": "completed",
                                "jobs": {**{k: ("completed", "success") for k in stale}, PRC: ("completed", "failure")},
                                "starts": {PRC: "2026-11-11T12:00:00Z"}})
    check("requeued needs, one source read: the released gate takes the re-running run's standing pr-contract "
          "(attempt 1 success, started after the older red) as busy() did", gate(rq_ctx, api), (True, []))
    p1, _ = shape({PRC: {"conclusion": "skipped"}})
    get, _ = requeue_world(prior=p1)
    api = read_api(rq_ctx, claim, True, get)
    api["runs_at_head"].append({"id": 5, "title": title("code", "7", "main"), "status": "completed",
                                "jobs": {**{k: ("completed", "success") for k in stale}, PRC: ("completed", "failure")},
                                "starts": {PRC: "2026-11-11T12:00:00Z"}})
    check("requeued needs, one source read: a need skipped before the re-run is no source there either, so the "
          "older red stands", gate(rq_ctx, api), (False, ["pr-contract / pr-contract: failure (run 5)"]))
    print(f"gate self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
