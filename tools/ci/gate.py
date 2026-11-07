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
the harness's `b3` arm, never from memory). `tests / arch-instrument`, the
architecture-score pair's own job beside `fast` (P2b, U5b), is a tests name
like the rest: required on pull requests and push alike.

DEFERRAL (R10-GATE-DEFER). A run still adding a source at this head
(`busy`) makes this verdict undecided. The judge then WAITS, re-reading every
POLL_S (60 s, tvofi's floor), up to GATE_WAIT_MAX_S, and judges once nothing
is busy: a deferring gate publishes no red for an undecided head, and the
verdict it then publishes is the one every gate at the head computes from the
same finished sources, so a red source stays red and no wait masks it. The
waits are acyclic: a gate waits only on runs that are not yet `judging`, and
nothing waits on a judging run (prelude.wait_sources), so two gates that
start together each find the other judging on a re-read. Two runs whose
gates have both started are broken by id (`busy`): the lower decides, the higher
waits on it, so a run whose listing lags its resolved jobs cannot make two gates
defer to each other. Only past the bound, a run still busy after
GATE_WAIT_MAX_S, does the gate FAIL deferring, for gate-sweep.yml to re-judge.
A deferring body run (prelude.defer_to, R10-CI-EDIT-RUNNER) is the one gate
that never waits: it ran no unit, so it publishes SELF_DEFERRED at once, and
the code run's gate, once that run is judging, re-runs it (`redispatch`) and
waits on it; the re-run's own attempt then replaces that red with a verdict.
Every other gate waits on the latest deferring run of each kind (`pending`)
as on a busy one, so no gate passes the head before its latest body and review
are judged. A deferring run of R10-CI-SLIM card C3's shape (arch-score and
budget-raise-gate run, `pr-contract` skipped) waited instead (#3263: run
42338396358 red in 2 s beside code run 42338396871, when judging() read the
skipped `pr-contract` caller as owed and the at-once bound dodged a cycle).
judging() reads a caller listed completed under its bare name as a unit the
run never ran, so a deferring run is judging once its gate is listed and its
own units are done, and nothing waits on it through busy(). The waits then
form one order: a code run's prelude waits on nothing; another prelude only on
an earlier run, or on a code run, that is not judging, and a body run's
prelude not even on that code run; a gate only on runs not judging, past the
busy() tie-break, and on a pending run, which waits on nothing. No run that is
judging waits on a run that is not, so no cycle closes.
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
from prelude import (BODY_KINDS, BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, deferring,  # noqa: E402,F401
                     derive, judging, parse_title, run_jobs, title, workset)

PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet", "ci-ratchet")}      # B3
CODE = {u: UNITS[u] for u in CODE_UNITS}
BODY = {u: UNITS[u] for u in BODY_UNITS}
ATTEMPT_CAP = 45     # GitHub fails a run's 51st attempt; the hooks never take a run past 45 (4.3)
# The deferral's wait bound: ci.yml's gate job has 15 min; the job's checkout,
# restore and reads take under a minute without a wait (#2754's edit gate: 21 s),
# so 12 min of waiting plus one poll leaves two minutes. The self-test pins it
# under the job's `timeout-minutes`.
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


# R10-CI-EDIT-RUNNER. A body run (edit, review) beside an unfinished code run
# that is not judging runs no unit (prelude.defer_to). Until it is re-run it is
# the latest event's unjudged body or review, so every gate at the head waits
# on the latest such run of each kind (`pending`) as on a busy one, and the
# code run's gate, the one gate that run's deferral names, re-runs it
# (`redispatch`), at most once per judge(). The re-run's prelude finds that
# code run judging, so it runs its full workset and waits on nothing. An
# earlier deferring run of a kind is superseded by the latest: its event's
# body or review is read again by the later run.
SELF_DEFERRED = "this run deferred to an unfinished code run at this head, whose gate re-runs it"


def pending(ctx: dict, runs: list[dict]) -> list:
    """The ids of the latest run of each body kind for this PR, when that run is
    deferring (prelude.deferring): owed a re-run, then a judgement. `runs`
    includes this run itself when the caller wants it considered."""
    _, pr, _ = derive(ctx)
    latest: dict[str, dict] = {}
    for r in runs:
        t = parse_title(r.get("title") or "")
        if pr and t is not None and t[0] in BODY_KINDS and t[1] == pr and r["id"] > latest.get(t[0], {"id": -1})["id"]:
            latest[t[0]] = r
    return sorted(r["id"] for r in latest.values() if r.get("status") != "action_required" and deferring(r))


def waiting_on(ctx: dict, others: list[dict]) -> list:
    """What this gate waits on: the busy runs and the pending deferred ones."""
    return sorted(set(busy(ctx, others)) | set(pending(ctx, others)))


def redispatch(ctx: dict, runs: list[dict], post, done: set) -> list[str]:
    """A code run's gate re-runs each pending deferred run that has completed and
    that this judge() has not re-run yet; the reasons a re-run failed."""
    kind, pr, _ = derive(ctx)
    if kind != "code" or not pr or post is None:
        return []
    bad = []
    for r in runs:
        if r["id"] in done or r["id"] not in pending(ctx, runs) or r.get("status") != "completed":
            continue
        done.add(r["id"])
        if int(r.get("attempt", 1)) >= ATTEMPT_CAP:
            bad.append(f"deferred run {r['id']} is at attempt {r['attempt']}, the cap: push a new commit")
            continue
        st, _, _ = post(f"repos/{ctx['repo']}/actions/runs/{r['id']}/rerun")
        if st not in (201, 204):
            bad.append(f"re-run of deferred run {r['id']}: HTTP {st}")
    return bad


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
    own = pre.get("workset")                # the units the prelude ran here; a deferring body run ran none
    me = {"id": ctx["run_id"], "title": title(kind, pr, base, ctx.get("sha", "")), "status": "completed",
          "jobs": api["jobs"]}
    waiting = waiting_on(ctx, others)
    if kind in BODY_KINDS and own == set() and deferring(me) and (waiting or ctx["run_id"] in pending(ctx, others + [me])):
        return False, [SELF_DEFERRED]       # never waits: the code run's gate re-runs the latest deferring run
    if waiting:
        return False, [deferral(waiting)]
    required: dict[str, list[str]] = {}
    for name in REQUIRED[event_class(ev, pr, api.get("reaches_cc"))]:
        u, n = name.split(" / ", 1)
        required.setdefault(u, []).append(n)
    for unit, names in required.items():
        src = None
        for r in sorted(others + [me], key=lambda r: r["id"], reverse=True):
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
    jobs = run_jobs(get, repo, ctx["run_id"])
    status, conclusion = jobs.get("prelude") or (None, None)
    api = {"prelude": {"status": status, "conclusion": conclusion, **claim},
           "jobs": jobs, "reaches_cc": reaches_cc, "live_pr": None, "open_pr_heads": set()}
    if pr and ctx["event_name"] != "merge_group":
        lp = _pull(get, repo, pr)
        api["live_pr"] = {"head_sha": lp["head"]["sha"], "base_ref": lp["base"]["ref"], "state": lp["state"],
                          "same_repo": (lp["head"].get("repo") or {}).get("full_name") == repo}
    elif ctx["event_name"] == "workflow_dispatch":
        api["open_pr_heads"] = {p["head"]["sha"] for p in ghapi.paginate(f"repos/{repo}/pulls", {"state": "open"}, get=get)}
    runs = ghapi.paginate(f"repos/{repo}/actions/workflows/ci.yml/runs", {"head_sha": ctx["head"]}, get=get)
    api["runs_at_head"] = [{"id": r["id"], "title": r.get("display_title") or "", "status": r["status"],
                            "attempt": int(r.get("run_attempt") or 1),
                            "jobs": {} if r["status"] == "action_required" else run_jobs(get, repo, r["id"])}
                           for r in runs if r["id"] != ctx["run_id"]]
    return api


def reaches_custom_components(base: str, head: str) -> bool:
    """D-2's three-dot diff, from the checkout; unknown reads as reaching (fail closed)."""
    p = subprocess.run(["git", "diff", "--name-only", f"origin/{base}...{head}", "--", "custom_components/"],
                       capture_output=True, text=True)
    return p.returncode != 0 or bool(p.stdout.strip())


def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components, sleep=time.sleep,
          now=time.monotonic, post=None) -> tuple[str, list[str], list[str]]:
    """(outcome, reasons, this run's other jobs: reported, never gating). A verdict
    that only defers, or only waits on this run's own lagging jobs (lag_bound),
    is never published while its bound allows a re-read. A code run's gate
    re-runs the deferred body runs it finds (`redispatch`, with `post`) before
    it judges; a deferring run's own gate publishes SELF_DEFERRED at once."""
    kind, pr, base = derive(ctx)
    cc = reaches(base, ctx["head"]) if pr else None     # git first; the API reads are last (R3-1)
    t0, lagged, rerun = now(), [], set()
    while True:
        api = read_api(ctx, claim, cc, get)
        failed = redispatch(ctx, api["runs_at_head"], post, rerun)
        ok, why = (False, failed) if failed else gate(ctx, api)
        waiting = waiting_on(ctx, api["runs_at_head"])
        bound = GATE_WAIT_MAX_S if why == [deferral(waiting)] else 0 if failed else lag_bound(why)
        if ok or now() - t0 + POLL_S > bound:
            break
        if why != [deferral(waiting)]:
            lagged = lagged or why
        sleep(POLL_S)
    owed = {n for names in REQUIRED.values() for n in names} | {"prelude", "gate"}
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
        outcome, why, notes = judge(ctx, claim, get, post=post)
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
    check("B3: push owes the Tests push run's ratchets", {"tests / ci-ratchet", "tests / coverage-ratchet"} <= set(REQUIRED["push"]), True)
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
    dctx = context("workflow_dispatch", {"inputs": {}}, env)
    dapi = {**api, "prelude": {"conclusion": "success", "kind": "code", "pr": ""}, "jobs": jobs, "runs_at_head": []}
    check("an unnamed dispatch at an open PR's head is refused", gate(dctx, {**dapi, "open_pr_heads": {"M"}})[1],
          ["this SHA heads an open PR: dispatch with -f pr=N -f base=REF"])
    check("... and judged as usual at no PR's head (null)", gate(dctx, {**dapi, "open_pr_heads": {"X"}}), (True, []))
    # R10-GATE-DEFER: a deferral waits, bounded, and publishes no red for an undecided head.
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
    in_prelude = [{"name": "prelude", "status": "in_progress", "conclusion": None, "id": 1}]
    check("R3-2: a run whose gate is listed but an owed job is not still adds a source",
          busy(ctx, [{"id": 99, "title": title("code", "7", "main", "M"), "status": "in_progress",
                      "jobs": {"gate": ("completed", "success")}}]), [99])
    get, naps, nap, now = scene([run(101, "edit", "in_progress", in_prelude), run(102, "review", "queued", [])],
                                [run(101, "edit", "in_progress", owed("edit")),
                                 run(102, "review", "in_progress", owed("review"))])
    check("#2754 shape: a gate beside a busy edit run and a queued review run waits, then judges once, no red",
          (verdict(ctx, get, nap, now), naps), ("PASS", [POLL_S]))
    get, naps, nap, now = scene([run(101, "code", "in_progress", owed("code", gate=False))],
                                [run(101, "code", "in_progress", owed("code"))])
    check("simultaneous completion, side A: the other's gate not yet listed -> wait, then a decider",
          verdict(ctx, get, nap, now), "PASS")
    bctx = {**ctx, "run_id": 101}
    get, naps, nap, now = scene([run(100, "code", "in_progress", owed("code", gate=False)),
                                 run(101, "code", "in_progress", owed("code"))],
                                [run(100, "code", "in_progress", owed("code")), run(101, "code", "in_progress", owed("code"))],
                                me=101)
    check("simultaneous completion, side B: the same, so the pair never deadlocks red-red",
          verdict(bctx, get, nap, now), "PASS")
    get, naps, nap, now = scene([run(101, "edit", "in_progress", owed("edit", gate=False, state="in_progress"))],
                                [run(101, "edit", "completed", owed("edit", red=("pr-contract / pr-contract",)))])
    check("a deferring gate published after the decider's red is that red, never a PASS",
          verdict(ctx, get, nap, now), "FAIL pr-contract / pr-contract: failure (run 101)")
    # C3 (option A): an edit run beside a code run that has not started its
    # pr-contract ran arch-score and budget-raise-gate only; its caller job
    # `pr-contract` is listed skipped, under the caller's bare name.
    ectx = context("pull_request", {**ev, "action": "edited"}, env)
    deferred = [{"name": "prelude", "status": "completed", "conclusion": "success", "id": 1},
                {"name": "arch-score / arch-score", "status": "completed", "conclusion": "success", "id": 1},
                {"name": "budget-raise-gate / budget-raise-gate", "status": "completed", "conclusion": "success",
                 "id": 1},
                {"name": "pr-contract", "status": "completed", "conclusion": "skipped", "id": 1}]
    eclaim3 = {"kind": "edit", "pr": "7", "workset": {"arch-score", "budget-raise-gate"}}
    busy_code = [run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))]
    get, naps, nap, now = scene(busy_code, [run(99, "code", "completed", owed("code"))], mine=deferred)
    check("C3 (r10-gate-busy-defer-2): a deferring edit gate beside a busy code run waits on it, then judges "
          "its sources, no red", (verdict(ectx, get, nap, now, eclaim3), naps), ("PASS", [POLL_S]))
    get, naps, nap, now = scene(busy_code, mine=deferred)
    verdict(ectx, get, nap, now, {"kind": "edit", "pr": "7"})
    check("... null control: the same gate with the full edit workset waits on it, bounded, as before",
          (bool(naps), sum(naps) <= GATE_WAIT_MAX_S), (True, True))
    # r10-gate-busy-defer: #3241 head 95c7e604, attempt 2 -- two deferring edit
    # runs, each gate listed, each read the other as busy (its pr-contract never
    # listed), so both published the deferral and no gate judged. judging() now
    # reads that listing as judging (r10-gate-busy-defer-2); the id tie-break still
    # orders two started gates whose listing lags a caller already resolved (a gate
    # needs pr-contract, so its `pr-contract` read unfinished is the listing's lag).
    lo, hi = 42192623509, 42193153511
    at_gate = deferred + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
    lagging = [dict(j, status="in_progress", conclusion=None) if j["name"] == "pr-contract" else j for j in at_gate]
    pair = [{"id": i, "title": title("edit", "7", "main", "M"), "status": "in_progress",
             "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in lagging}} for i in (lo, hi)]
    check("busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower",
          (busy({**ctx, "run_id": lo}, pair), busy({**ctx, "run_id": hi}, pair)), ([], [lo]))
    honest = [{**r, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in at_gate}} for r in pair]
    check("busy-defer-2: listed as GitHub lists it (`pr-contract` skipped), neither started gate waits on the other",
          (busy({**ctx, "run_id": lo}, honest), busy({**ctx, "run_id": hi}, honest)), ([], []))
    coded = run(99, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed",
                                                                "conclusion": "success", "id": 9}])
    get, naps, nap, now = scene([coded, run(hi, "edit", "in_progress", at_gate)], me=lo, mine=deferred)
    check("busy-defer: the lower deferring edit gate judges at once beside the higher one",
          (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("PASS", []))
    get, naps, nap, now = scene([coded, run(lo, "edit", "in_progress", lagging)],
                                [coded, run(lo, "edit", "completed", deferred + [{"name": "gate", "status": "completed",
                                                                          "conclusion": "success", "id": 9}])],
                                me=hi, mine=deferred)
    check("busy-defer: the higher deferring edit gate waits on the lower whose listing lags, "
          "then judges, never a red deferral", (verdict({**ectx, "run_id": hi}, get, nap, now, eclaim3), naps),
          ("PASS", [POLL_S]))
    get, naps, nap, now = scene([coded, run(lo, "edit", "in_progress", at_gate)], me=hi, mine=deferred)
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
        get, naps, nap, now = scene([coded, run(hi, "edit", "in_progress", hi_jobs)],
                                    [coded, run(hi, "edit", "completed", owed("edit")[:-1] + [
                                        {"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])],
                                    me=lo, mine=deferred)
        check(f"prelude/gate order: a deferring gate beside a later edit run {label} waits on it (that run's "
              "prelude no longer waits on this one), then judges",
              (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("PASS", [POLL_S]))
    # #3246 round 2: the same scene with an EARLIER deferring edit run whose gate has
    # started beside hi: that earlier run is judging, so lo waits on hi alone.
    early_gate = 42192000000
    egr = run(early_gate, "edit", "in_progress", deferred + [{"name": "gate", "status": "in_progress",
                                                              "conclusion": None, "id": 9}])
    get, naps, nap, now = scene([coded, egr, run(hi, "edit", "in_progress", in_prelude)],
                                [coded, egr, run(hi, "edit", "completed", owed("edit")[:-1] + [
                                    {"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])],
                                me=lo, mine=deferred)
    check("prelude/gate order: beside an earlier started deferring gate and a later edit run in its prelude, "
          "it waits on the later run only, then judges",
          (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("PASS", [POLL_S]))
    lo_run = {"id": lo, "title": title("edit", "7", "main", "M")}
    gate_run = {"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}
    check("the cycle's other edge: a deferring run at its gate is judging (its bare `pr-contract` caller "
          "skipped), so no prelude or gate waits on it",
          judging({**lo_run, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in deferred + [gate_run]}}),
          True)
    check("... null: a caller still running (not completed) still owes its unit",
          judging({**lo_run, "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in
                                      [dict(j, status="in_progress", conclusion=None) if j["name"] == "pr-contract"
                                       else j for j in deferred] + [gate_run]}}), False)
    done_edit = run(101, "edit", "completed", deferred + [{"name": "gate", "status": "completed",
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
    for label, red, want in (("green", (), "PASS"),
                             ("its pr-contract red", ("pr-contract / pr-contract",),
                              "FAIL pr-contract / pr-contract: failure (run 99)")):
        get, naps, nap, now = scene([run(99, "code", "completed", owed("code", red=red))], me=101, mine=deferred)
        check(f"C3: the deferred gate re-judged once the code run ended ({label}) is that run's verdict",
              verdict({**ectx, "run_id": 101}, get, nap, now, eclaim3), want)
    late = deferred[:3] + [{"name": "pr-contract / pr-contract", "status": "completed", "conclusion": "failure",
                            "id": 1}]
    get, naps, nap, now = scene([run(99, "code", "completed", owed("code"))], mine=late)
    check("C3: a body edited after the code run's gate passed is still judged (this run's own pr-contract)",
          verdict(ectx, get, nap, now, {**eclaim3, "workset": set(BODY_UNITS)}),
          "FAIL pr-contract / pr-contract: failure (this run)")
    get, naps, nap, now = scene([run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))])
    out = verdict(ctx, get, nap, now)
    check("past the bound, the deferral FAILs (for gate-sweep.yml), and the wait stays inside the bound",
          (out.startswith("FAIL run(s) [99] at this head are still being judged"), bool(naps),
           sum(naps) <= GATE_WAIT_MAX_S), (True, True, True))
    get, naps, nap, now = scene([run(99, "code", "in_progress", owed("code", gate=False, state="in_progress"))])
    check("a decided red never waits: the prelude cross-check beside a busy run",
          (verdict(ctx, get, nap, now, {"kind": "code", "pr": ""}).startswith("FAIL prelude says"), naps), (True, []))
    get, naps, nap, now = scene([])
    check("null: no other run at the head, no wait", (verdict(ctx, get, nap, now), naps), ("PASS", []))
    reds = [run(i, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed",
                                                                "conclusion": "failure", "id": 9}]) for i in (90, 91, 92)]
    get, naps, nap, now = scene(reds + [run(99, "review", "queued", [])],
                                reds + [run(99, "review", "in_progress", owed("review"))])
    check("rerun cascade: three completed red deferring gates, a queued decider, and a re-run of an older gate: "
          "it waits for the decider, never re-defers red", (verdict({**ctx, "run_attempt": 2}, get, nap, now), naps),
          ("PASS", [POLL_S]))
    rerun = run(100, "code", "in_progress", owed("code")[:-1] + [{"name": "gate", "status": "queued",
                                                                  "conclusion": None, "id": 9}])
    check("... and the decider never waits on that re-run: a run whose only open job is its gate is judging",
          busy({**ctx, "run_id": 99}, [{**r, "title": r["display_title"],
                                        "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in r["jobs"]}}
                                       for r in reds + [rerun]]), [])
    # R10-CI-EDIT-RUNNER: a deferring body run ran no unit (prelude.defer_to); its
    # gate never waits, and the code run's gate re-runs the latest one of each kind.
    skipped = lambda kind: ([{"name": "prelude", "status": "completed", "conclusion": "success", "id": 1}]  # noqa: E731
                            + [{"name": u, "status": "completed", "conclusion": "skipped", "id": 1}
                               for u in sorted(workset(kind, "7") & set(UNITS))])
    g_in = [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
    g_red = [{"name": "gate", "status": "completed", "conclusion": "failure", "id": 9}]
    nothing = {"kind": "edit", "pr": "7", "workset": set()}
    get, naps, nap, now = scene(busy_code, mine=skipped("edit") + g_in, me=101)
    check("edit-runner: a deferring edit gate beside a busy code run publishes at once, holding no runner",
          (verdict({**ectx, "run_id": 101}, get, nap, now, nothing), naps), ("FAIL " + SELF_DEFERRED, []))
    rctx = context("pull_request_review", {**ev, "action": "submitted"}, env)
    get, naps, nap, now = scene(busy_code, mine=skipped("review") + g_in, me=102)
    check("edit-runner: a deferring review gate beside a busy code run publishes at once",
          (verdict({**rctx, "run_id": 102}, get, nap, now, {"kind": "review", "pr": "7", "workset": set()}), naps),
          ("FAIL " + SELF_DEFERRED, []))

    def code_scene(*frames):
        posts = []
        get, naps, nap, now = scene(*frames)
        return get, naps, nap, now, posts, lambda path, body=None: (posts.append(path), (201, {}, None))[1]
    gone = run(95, "edit", "completed", skipped("edit") + g_red)
    e_done = run(101, "edit", "completed", skipped("edit") + g_red)
    r_done = run(102, "review", "completed", skipped("review") + g_red)
    get, naps, nap, now, posts, post = code_scene(
        [gone, e_done, r_done],
        [gone, run(101, "edit", "in_progress", owed("edit", gate=False, state="in_progress")),
         run(102, "review", "queued", [])],
        [gone, run(101, "edit", "in_progress", owed("edit")), run(102, "review", "in_progress", owed("review"))])
    check("edit-runner: the code run's gate re-runs the latest deferring edit and review run once each, "
          "waits for them, then judges",
          (judge(ctx, claim, get, cc, nap, now, post)[0], posts, naps),
          ("PASS", ["repos/o/r/actions/runs/101/rerun", "repos/o/r/actions/runs/102/rerun"], [POLL_S, POLL_S]))
    get, naps, nap, now, posts, post = code_scene(
        [gone, run(101, "edit", "in_progress", skipped("edit") + g_in)], [gone, e_done],
        [gone, run(101, "edit", "in_progress", owed("edit"))])
    check("edit-runner: a deferring run still at its own gate (judging, a later id) is waited on, then re-run",
          (judge(ctx, claim, get, cc, nap, now, post)[0], posts), ("PASS", ["repos/o/r/actions/runs/101/rerun"]))
    get, naps, nap, now, posts, post = code_scene([run(101, "edit", "completed", owed("edit")), gone])
    check("edit-runner null: beside a finished edit run that ran its units, the code gate re-runs nothing, "
          "judges at once", (judge(ctx, claim, get, cc, nap, now, post)[0], posts, naps), ("PASS", [], []))
    get, naps, nap, now, posts, _ = code_scene([e_done])
    check("edit-runner: a refused re-run is published at once, never a PASS",
          (judge(ctx, claim, get, cc, nap, now, lambda path, body=None: (403, {}, None))[0], naps),
          ("FAIL re-run of deferred run 101: HTTP 403", []))
    get, naps, nap, now, posts, post = code_scene([{**e_done, "run_attempt": ATTEMPT_CAP}])
    check("edit-runner: a deferred run at the attempt cap is not re-run",
          (judge(ctx, claim, get, cc, nap, now, post)[0].startswith("FAIL deferred run 101 is at attempt"), posts),
          (True, []))
    get, naps, nap, now, posts, post = code_scene([e_done])
    lctx = context("pull_request", {**ev, "action": "labeled", "label": {"name": "x"}}, env)
    judge(lctx, {"kind": "label", "pr": "7"}, get, cc, nap, now, post)
    check("edit-runner: only a code run's gate re-runs; another gate waits on the pending run, bounded",
          (posts, 0 < sum(naps) <= GATE_WAIT_MAX_S), ([], True))
    get, naps, nap, now = scene([run(99, "code", "completed", owed("code")),
                                 run(110, "edit", "completed", owed("edit"))], mine=skipped("edit") + g_in, me=101)
    check("edit-runner null: a superseded deferring gate re-run once nothing is pending judges like every "
          "other gate (the sweep's re-run converges)",
          (verdict({**ectx, "run_id": 101}, get, nap, now, nothing), naps), ("PASS", []))
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

    def replay(head, rid):
        rows = fx["heads"][head]
        me, t0, pt = fx_me(head, rid)
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
    check("#3263 (42338396358 beside code run 42338396871): the deferring edit gate never publishes the "
          "deferral before its bound",
          (not out.startswith("FAIL " + deferral([code3263])) or sum(naps) + POLL_S > GATE_WAIT_MAX_S,
           out != "UNBOUNDED"), (True, True))
    _, t0, _ = fx_me(h3263, edit3263)
    seen = [{"id": r["id"], "title": r["display_title"], "status": r["status"],
             "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in r["jobs"]}}
            for r in at_time(fx["heads"][h3263], t0) if r["id"] != code3263]
    check("#3263: the code run's gate never waits on that deferring edit run (the edge that closed the cycle)",
          busy(fx_ctx(h3263, "3263", code3263, 1), seen), [])
    for rid in (42307493684, 42307798573):
        check(f"#3261 ({rid}, its sibling edit run at its gate): judges, never the pair's deferral",
              replay("e17fadc1795ebbaaf0f01ed067fbb59aeba90dee", rid)[0], "PASS")
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
    print(f"gate self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
