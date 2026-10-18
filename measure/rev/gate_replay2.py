"""Review item 10: replay section 4.1's OWN function over the measured heads.

    python3 -I measure/rev/gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt > measure/rev/gate_replay2.txt

Phase 2's gate_replay.py compared the ruleset with a newest-check-per-name rule of
its own, so its 22/22 said nothing of section 4.1. This script imports
gate_model.gate, the function tools/ci/gate.py ports, and drives it three ways:

1. HISTORY. Each saved head's check runs become one synthetic `pull_request`
   synchronize run of ci.yml: every required context's newest check run is renamed
   `<unit> / <name>` and becomes that run's job. RULESET is phase 2's own reading of
   ruleset 23698884 (17 contexts, a skip passes). The two may differ only where the
   design says so: a skipped required job (the gate refuses it), and owner ruling
   D-2 (arch-score is required when the diff reaches custom_components/). Any other
   difference fails the run.
2. PERTURBATIONS of one green head, each with its expected (ruleset, gate) pair.
3. EVENT PATHS the history cannot show: push (closure-scope exempt, body units not
   applicable), an edit run carrying the code units (12(c)), a source at another
   base, a retarget, a cancelled-pending run and its replacement (running, red,
   green), an unreadable title, a held run, and an older run's gate re-judged (the
   sweep). The full event-sequence replay with concurrency is gate_sim.py.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_model as G  # noqa: E402

CONTEXTS = [n for u, ns in G.REQUIRED.items() if u != "arch-score" for n in ns]   # the ruleset's 17
GREEN = {"success", "skipped", "neutral"}
UNIT_OF = {n: u for u, ns in G.REQUIRED.items() for n in ns}


def newest(runs, name):
    c = [r for r in runs if r["name"] == name and (name != "budget-raise-gate" or r["app"]["id"] == 15368)]
    return max(c, key=lambda r: (r.get("started_at") or "", r["id"])) if c else None


def ruleset(runs):
    bad = []
    for n in CONTEXTS:
        r = newest(runs, n)
        if r is None:
            bad.append(f"{n}=ABSENT")
        elif r["status"] != "completed" or r["conclusion"] not in GREEN:
            bad.append(f"{n}={r['conclusion'] or r['status']}")
    return bad


def as_run(runs):
    jobs = {}
    for n, u in UNIT_OF.items():
        r = newest(runs, n)
        if r is not None:
            jobs[f"{u} / {n}"] = (r["status"], r["conclusion"])
    return jobs


CTX = {"event_name": "pull_request", "action": "synchronize", "pr_number": "7", "base_ref": "main",
       "sha": "H", "run_id": 1000}


def api_for(jobs, reaches, prelude=None, runs_at_head=()):
    return {"prelude": prelude or {"conclusion": "success", "kind": "code", "pr": "7"}, "jobs": jobs,
            "runs_at_head": list(runs_at_head), "live_pr": {"head_sha": "H", "base_ref": "main", "state": "open"},
            "open_pr_heads": {"H"}, "reaches_cc": reaches}


def main(raw: Path, reach_file: Path) -> int:
    rc = 0
    reach = {}
    for line in reach_file.read_text().splitlines():
        if line and not line.startswith("#"):
            h, _, n = line.split()
            reach[h] = None if n == "UNKNOWN" else int(n) > 0
    print("## 1. history: 22 heads, ruleset 23698884 against gate_model.gate")
    print(f"{'head':10s} {'RULESET':8s} {'GATE':8s} reaches_cc  class      reasons")
    green = None
    counts = {"agree": 0, "designed": 0, "other": 0}
    for f in sorted(raw.glob("checks_*.json")):
        head = f.stem.split("_")[1]
        runs = json.loads(f.read_text())["check_runs"]
        a = ruleset(runs)
        rs = reach.get(head)
        verdicts = set()
        reasons = []
        for r_cc in ([rs] if rs is not None else [True, False]):
            ok, why = G.gate(CTX, api_for(as_run(runs), r_cc))
            verdicts.add(ok); reasons += why
        g = verdicts.pop() if len(verdicts) == 1 else None
        if (not a) == g:
            cls = "agree"
        else:
            jobs = as_run(runs)
            skipped = [k for k, v in jobs.items() if v[1] == "skipped"]
            arch = jobs.get("arch-score / arch-score")
            designed = (not a) and g is not True and (skipped or (arch and arch[1] != "success" and rs is not False))
            cls = "designed" if designed else "other"
        counts[cls] += 1
        if cls == "other":
            rc = 1
        if not a and g and green is None:
            green = runs
        print(f"{head[:10]} {'pass' if not a else 'FAIL':8s} {fmt(g):8s} {str(rs):10s}  {cls:9s}  "
              f"{'; '.join(sorted(set(reasons)))[:120]}")
    print(f"\nheads {sum(counts.values())}: agree {counts['agree']}, differ by design {counts['designed']}, "
          f"differ otherwise {counts['other']}")

    print("\n## 2. perturbations of one green head (expected ruleset, expected gate)")

    def perturb(label, fn, want_rs, want_g, reaches=True, ctx=None, prelude=None, runs_at_head=()):
        nonlocal rc
        runs = copy.deepcopy(green); fn(runs)
        a = ruleset(runs)
        jobs = as_run(runs)
        ok, why = G.gate(ctx or CTX, api_for(jobs, reaches, prelude, runs_at_head))
        got = ("pass" if not a else "FAIL", "pass" if ok else "FAIL")
        good = got == (want_rs, want_g); rc |= not good
        print(f"  {'ok ' if good else 'BAD'} {label:62s} ruleset {got[0]:4s} gate {got[1]:4s}  {'; '.join(why)[:110]}")

    def setc(name, concl, status="completed"):
        def f(runs):
            for r in runs:
                if r["name"] == name:
                    r["conclusion"], r["status"] = concl, status
        return f

    def drop(name):
        def f(runs):
            runs[:] = [r for r in runs if r["name"] != name]
        return f

    def add_arch(concl):
        def f(runs):
            runs[:] = [r for r in runs if r["name"] != "arch-score"]
            runs.append({"name": "arch-score", "status": "completed", "conclusion": concl, "app": {"id": 15368},
                         "started_at": "9", "id": 1})
        return f

    nop = lambda r: None  # noqa: E731
    perturb("null: unchanged green head", nop, "pass", "pass")
    perturb("required job absent (closures)", drop("closures"), "FAIL", "FAIL")
    perturb("required job pending (fast (3.14))", setc("fast (3.14)", None, "in_progress"), "FAIL", "FAIL")
    perturb("required job failed (mutation)", setc("mutation", "failure"), "FAIL", "FAIL")
    perturb("required job cancelled (typing)", setc("typing", "cancelled"), "FAIL", "FAIL")
    perturb("required job skipped (fast (3.14))", setc("fast (3.14)", "skipped"), "pass", "FAIL")
    perturb("browser skipped (4.2: no required job may skip)", setc("browser", "skipped"), "pass", "FAIL")
    perturb("non-required red (delivery-status)", setc("delivery-status", "failure"), "pass", "pass")
    perturb("non-required red (nightly-status)", setc("nightly-status", "failure"), "pass", "pass")
    perturb("D-2: arch-score red, diff reaches custom_components/", add_arch("failure"), "pass", "FAIL", reaches=True)
    perturb("D-2: arch-score red, diff misses custom_components/", add_arch("failure"), "pass", "pass", reaches=False)
    perturb("D-2: arch-score absent, diff reaches custom_components/", drop("arch-score"), "pass", "FAIL", reaches=True)
    perturb("item 2: prelude concluded failure", nop, "pass", "FAIL",
            prelude={"conclusion": "failure", "kind": "code", "pr": "7"})
    perturb("item 2: prelude emits pr='' on a pull_request run", nop, "pass", "FAIL",
            prelude={"conclusion": "success", "kind": "code", "pr": ""})
    perturb("item 2: pr-contract and budget-raise-gate never ran", lambda r: (drop("pr-contract")(r), drop("budget-raise-gate")(r)),
            "FAIL", "FAIL")
    print("\n## 3. event paths")

    def code_run(rid, title, jobs, status="completed"):
        return {"id": rid, "title": title, "status": status, "jobs": jobs}

    green_jobs = as_run(green)
    push_ctx = {"event_name": "push", "sha": "H", "run_id": 1000}
    push_jobs = {k: v for k, v in green_jobs.items() if k != "tests / closure-scope"}
    for u in G.BODY:
        for n in G.BODY[u]:
            push_jobs[f"{u} / {n}"] = ("completed", "skipped")
    perturb("push: closure-scope absent (never runs on push), body units not applicable", drop("closure-scope"), "FAIL", "pass", ctx=push_ctx,
            prelude={"conclusion": "success", "kind": "code", "pr": ""})
    ok, why = G.gate(push_ctx, {**api_for(push_jobs, True), "prelude": {"conclusion": "success", "kind": "code", "pr": ""}})
    show("push run as the umbrella writes it (closure-scope never runs, body rows skipped)", ok, True); rc |= not ok
    edit_ctx = {**CTX, "action": "edited", "run_id": 2000}
    edit_jobs = {k: (("completed", "skipped") if k.split(" / ")[0] in G.CODE else v) for k, v in green_jobs.items()}
    epre = {"conclusion": "success", "kind": "edit", "pr": "7"}
    C = code_run(1500, G.title("code", "7", "main"), green_jobs)

    def edit_case(label, runs_at_head, want, live_base="main"):
        nonlocal rc
        api = {**api_for(edit_jobs, True, epre), "runs_at_head": runs_at_head}
        api["live_pr"] = {**api["live_pr"], "base_ref": live_base}
        ok, why = G.gate(edit_ctx, api)
        show(label, ok, want, why); rc |= ok != want

    edit_case("edit run: code rows skipped HERE, carried from the code run (12(c): the carry wins)", [C], True)
    edit_case("edit run: the only code run judged another base", [code_run(1500, G.title("code", "7", "release"), green_jobs)], False)
    edit_case("edit run after a retarget to release: its own body units judged main", [C], False, live_base="release")
    cancelled = code_run(1600, G.title("code", "7", "main"), {})
    edit_case("edit run: a newer code run was cancelled pending, its replacement still running",
              [C, cancelled, code_run(1700, G.title("code", "7", "main"), {}, "in_progress")], False)
    red = {**green_jobs, "tests / closures": ("completed", "failure")}
    edit_case("... and the replacement completed red: the newest evaluation wins",
              [C, cancelled, code_run(1700, G.title("code", "7", "main"), red)], False)
    edit_case("... and the replacement completed green",
              [code_run(1500, G.title("code", "7", "main"), red), cancelled, code_run(1700, G.title("code", "7", "main"), green_jobs)], True)
    edit_case("edit run: an earlier run at the head has an unreadable title", [C, code_run(1600, "Tests", {})], False)
    edit_case("edit run: a held run at the head is neither waited for nor a source",
              [C, {**code_run(1600, G.title("code", "7", "main"), {}), "status": "action_required"}], True)
    code_skip = dict(green_jobs); code_skip["hassfest / hassfest"] = ("completed", "skipped")
    ok, why = G.gate({**CTX, "run_id": 3000}, {**api_for(code_skip, True), "runs_at_head": [C]})
    show("code run: hassfest skipped in the NEWEST run that owns it: never filled from an older one (12(c))", ok, False, why); rc |= ok
    ok, why = G.gate({**CTX, "run_id": 1500}, {**api_for(red, True), "runs_at_head": [code_run(2000, G.title("edit", "7", "main"), edit_jobs)]})
    show("an older code run's gate re-judged after a newer edit: still red, its code is red", ok, False, why); rc |= ok
    ok, why = G.gate({**CTX, "run_id": 1500}, {**api_for(red, True), "runs_at_head": [code_run(2000, G.title("edit", "7", "main"), edit_jobs),
                                                                                     code_run(2100, G.title("code", "7", "main"), green_jobs)]})
    show("... re-judged after a newer green code run at the same head: green (the sweep's case)", ok, True, why); rc |= not ok
    print(f"\nGATE-REPLAY2 rc {rc}")
    return rc


def show(label, ok, want, why=()):
    print(f"  {'ok ' if ok == want else 'BAD'} {label:90s} gate {'pass' if ok else 'FAIL'}  {'; '.join(why)[:90]}")


def fmt(v):
    return {True: "pass", False: "FAIL", None: "SPLIT"}[v]


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
