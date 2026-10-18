"""Event-level replay of the umbrella: concurrency, waits, re-runs, the gate.

    python3 -I measure/rev/gate_sim.py > measure/rev/gate_sim.txt

Review items 1, 2, 3, 4, 10 and 12(c). Each scenario is a timed sequence of PR
events. The simulator applies GitHub's documented concurrency rule (design review
ev/gh_docs_actions-group-concurrency.md: at most one running and ONE pending run per
group; a newly queued run CANCELS the pending one whatever cancel-in-progress says;
cancel-in-progress additionally cancels the running one), runs each run's jobs with
fixed durations, lets body readers read the body and reviews at their own start, and
evaluates the gate job with the gate function at the gate job's own time.

Two layouts are replayed over the SAME scenarios:
  P2   phase 2 as written (one `CI-<pr>` group, cancel only on a non-edit
       pull_request, governance/hassfest/validate guarded on `action != 'edited'`,
       applicability from the prelude's `pr`, the newest completed non-cancelled code
       run carried with no base check, the prelude waits only for code runs). It is
       the review seat's `gate41_model.py` reading, given each run's kind for free.
  REV1 revision 1 (DESIGN-P2.md 2.2, 4.1, 4.3): code / edit / review lanes; verdict
       preludes wait for EVERY earlier run at the head; every code unit guarded on the
       prelude's kind; gate_model.gate (kind from run-name, applicability from the
       event, sources at the PR's live base, red while another run at the head is
       being judged); the REFRESH hook (a PR event's run re-runs the `gate` job of
       every completed green run at its head, REFRESH s after it starts) and the SWEEP
       hook (a green `gate` re-runs the `gate` job of every older red run at its head,
       SWEEP s later).

The ORACLE is independent of both: once every run has completed, the PR should be
mergeable iff every code unit is green at (final head, final base) and the body
readers are green for the final body and reviews. Each row prints the merge box under
THREE readings of which `gate` check binds when several exist at one head: the newest
by creation, the newest completed, and every suite's latest attempt (the tree records
"GitHub's ruleset refuses a merge while any suite at the head carries a non-success
run", tools/policy/budget_raise_gate.py:604, #2009); then the longest window in which
the merge box read green while the oracle read red. Exit 0 only when REV1 agrees with
the oracle on every unplanted scenario under all three readings, has no false-green
window longer than WINDOW_OK seconds, and refuses every planted defect under all
three. The P2 rows are printed for comparison. A last block removes each hook from
REV1 in turn, to show each is load-bearing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_model as G  # noqa: E402

DUR = {"tests": 2000, "codeql": 1300, "governance": 190, "hassfest": 30, "validate": 50,
       "arch-score": 60, "budget-raise-gate": 16, "pr-contract": 28}
PRELUDE, GATE, CANCEL_LAG, WINDOW_OK = 5, 15, 5, 120
REFRESH, SWEEP = 10, 20      # seconds from a PR event's run start to its refresh re-runs; from a green gate to the sweep
CODE_U = list(G.CODE)


class World:
    def __init__(self, layout, truth, plant=None, ablate=()):
        self.layout, self.truth, self.plant, self.ablate = layout, truth, plant or {}, set(ablate)
        self.runs, self.t, self.nid = [], 0, 100
        self.head, self.base, self.body, self.review = "H1", "main", "b1", "none"
        self.gates = []          # {"created", "completed", "ok", "run", "head"}
        self.todo = []           # (time, action, run): scheduled gate re-runs
        self.log = []

    # ---- concurrency -------------------------------------------------------
    def group(self, r):
        if r["event"] == "pull_request" and not r["bot"]:
            if self.layout == "P2":
                return "CI-pr"
            return {"code": "code", "edit": "edit"}[r["kind"]]
        if r["event"] == "pull_request_review":
            return "CI-pr" if self.layout == "P2" else "review"
        return f"run-{r['id']}"

    def cancels_running(self, r):
        if self.layout == "P2":
            return r["event"] == "pull_request" and r["action"] != "edited" and not r["bot"]
        return r["event"] in ("pull_request", "pull_request_review") and not r["bot"]

    def new_run(self, **kw):
        self.nid += 1
        r = {"held": False, "bot": False, "action": "", "changes_base": False, **kw,
             "id": self.nid, "created": self.t, "status": "pending", "jobs": {}, "start": None, "end": None}
        kind, pr, base = G.derive({"event_name": r["event"], "action": r["action"],
                                   "changes_base": r["changes_base"], "pr_number": "7",
                                   "base_ref": r.get("base_ref", ""), "input_pr": r.get("input_pr", ""),
                                   "input_base": r.get("input_base", "")})
        r.update(kind=kind, pr=pr, base=base, title=G.title(kind, pr, base))
        if r["held"]:
            r["status"] = "action_required"
            self.runs.append(r)
            return r
        g = self.group(r); r["group"] = g
        for o in self.runs:
            if o.get("group") == g and o["status"] == "pending":
                o["status"], o["conclusion"], o["end"] = "completed", "cancelled", self.t
            if o.get("group") == g and o["status"] == "in_progress" and self.cancels_running(r):
                o["cancel_at"] = self.t + CANCEL_LAG
        self.runs.append(r)
        return r

    # ---- one run's jobs ------------------------------------------------------
    def units_for(self, r):
        if self.layout == "P2":
            u = set()
            if r["kind"] == "code":
                u |= {"tests", "codeql"}
            if not (r["action"] == "edited" or r["event"] == "pull_request_review"):
                u |= {"governance", "hassfest", "validate"}
            pr = "" if self.plant.get("prelude_pr_blank") else r["pr"]
            if pr:
                u |= set(G.BODY)
            return u
        if self.plant.get("unit_if_false") and r["kind"] == "code":
            return G.workset(r["kind"], r["pr"]) - {self.plant["unit_if_false"]}
        return G.workset(r["kind"], r["pr"])

    def outcome(self, unit, r, at):
        if unit in G.CODE:
            return self.truth["code"](r["head"], r["base"]).get(unit, True)
        if unit == "budget-raise-gate":
            return self.truth["brg"](self.review_at(at))
        return self.truth["body"](self.body_at(at))

    def body_at(self, at):
        return [v for (t, v) in self.body_hist if t <= at][-1]

    def review_at(self, at):
        return [v for (t, v) in self.review_hist if t <= at][-1] if any(t <= at for t, _ in self.review_hist) else "none"

    def try_start(self, r):
        if r["status"] != "pending":
            return
        g = r["group"]
        if any(o is not r and o.get("group") == g and o["status"] == "in_progress" for o in self.runs):
            return
        r["status"], r["start"] = "in_progress", self.t
        r["prelude_done"] = self.t + PRELUDE
        if self.layout == "REV1" and r["event"] in ("pull_request", "pull_request_review") and "refresh" not in self.ablate:
            self.todo.append((self.t + REFRESH, "refresh", r))

    def wait_over(self, r):
        if r["kind"] == "code":
            return True
        for o in self.runs:
            if o["head"] != r["head"] or o is r or o["status"] in ("completed", "action_required"):
                continue
            if self.layout == "P2":
                if o["kind"] == "code" and o["id"] < r["id"]:
                    return False
            elif o["id"] < r["id"]:
                return False
        return True

    def step_run(self, r):
        if r["status"] != "in_progress":
            return
        if r.get("cancel_at") is not None and self.t >= r["cancel_at"]:
            for u in r.get("sched", {}):
                if f"{u}" not in r["done"]:
                    for n in G.REQUIRED[u]:
                        r["jobs"][f"{u} / {n}"] = ("completed", "cancelled")
            r["status"], r["conclusion"], r["end"] = "completed", "cancelled", self.t
            return
        if self.t < r["prelude_done"]:
            return
        if "sched" not in r:
            if not self.wait_over(r):
                return
            units = self.units_for(r)
            r["units"] = units
            r["sched"], r["done"] = {}, set()
            for u in units:
                if u != "pr-contract":
                    r["sched"][u] = (self.t, self.t + DUR[u])
            for u in set(G.REQUIRED) - units:          # skipped caller rows
                for n in G.REQUIRED[u]:
                    r["jobs"][f"{u} / {n}"] = ("completed", "skipped")
        for u, (s, e) in list(r["sched"].items()):
            if u not in r["done"] and self.t >= e:
                ok = self.outcome(u, r, s)
                for n in G.REQUIRED[u]:
                    r["jobs"][f"{u} / {n}"] = ("completed", "success" if ok else "failure")
                r["done"].add(u)
        others = [u for u in r["sched"] if u != "pr-contract"]
        if "pr-contract" in r["units"] and "pr-contract" not in r["sched"] and all(u in r["done"] for u in others):
            r["sched"]["pr-contract"] = (self.t, self.t + DUR["pr-contract"])
        if all(u in r["done"] for u in r["sched"]) and ("pr-contract" not in r["units"] or "pr-contract" in r["done"]):
            if "gate_at" not in r:
                r["gate_at"] = self.t
                r["gate_entry"] = {"created": self.t, "completed": None, "ok": None, "run": r["id"], "head": r["head"]}
                self.gates.append(r["gate_entry"])
            if self.t >= r["gate_at"] + GATE:
                self.finish_gate(r)

    def finish_gate(self, r):
        ok, why = self.eval_gate(r)
        r["gate_entry"].update(completed=self.t, ok=ok)
        r["why"] = why
        r["status"], r["conclusion"], r["end"] = "completed", "success" if ok else "failure", self.t
        if ok and self.layout == "REV1" and "sweep" not in self.ablate:
            self.todo.append((self.t + SWEEP, "sweep", r))

    # ---- the two re-run hooks of revision 1 (DESIGN-P2.md 4.3) ---------------------
    def latest_gate(self, r):
        es = [g for g in self.gates if g["run"] == r["id"]]
        return max(es, key=lambda g: g["created"]) if es else None

    def hooks(self):
        for item in [x for x in self.todo if x[0] == self.t]:
            self.todo.remove(item)
            _, what, src = item
            for o in self.runs:
                if o is src or o["head"] != src["head"] or o["status"] != "completed":
                    continue
                g = self.latest_gate(o)
                if g is None or g["completed"] is None:
                    continue
                # refresh: re-judge every green gate an event may have made stale;
                # sweep: re-judge every older red gate once a gate at the head is green
                if (what == "refresh" and g["ok"]) or (what == "sweep" and not g["ok"] and o["id"] < src["id"]):
                    o["status"], o["rerun_at"] = "in_progress", self.t
                    o["gate_entry"] = {"created": self.t, "completed": None, "ok": None, "run": o["id"], "head": o["head"]}
                    self.gates.append(o["gate_entry"])
        for o in self.runs:
            if o.get("rerun_at") is not None and self.t >= o["rerun_at"] + GATE:
                o["rerun_at"] = None
                self.finish_gate(o)

    def eval_gate(self, r):
        ctx = {"event_name": r["event"], "action": r["action"], "changes_base": r["changes_base"],
               "pr_number": "7", "base_ref": r.get("base_ref", ""), "input_pr": r.get("input_pr", ""),
               "input_base": r.get("input_base", ""), "sha": r["head"], "run_id": r["id"]}
        at_head = [dict(id=o["id"], title=o["title"], status=o["status"], jobs=o["jobs"])
                   for o in self.runs if o["head"] == r["head"] and o is not r]
        if self.layout == "P2":
            pr = "" if self.plant.get("prelude_pr_blank") else r["pr"]
            jobs = dict(r["jobs"])
            if r["kind"] != "code":
                done = [o for o in self.runs if o["head"] == r["head"] and o["kind"] == "code"
                        and o["status"] == "completed" and o.get("conclusion") != "cancelled" and o["id"] < r["id"]]
                if not done:
                    return False, ["no code verdict at this head"]
                jobs.update({k: v for k, v in done[-1]["jobs"].items() if k.split(" / ")[0] in G.CODE})
            bad = []
            for u, names in G.REQUIRED.items():
                if u in G.BODY and not pr:
                    continue
                if u == "arch-score" and not self.truth.get("reaches_cc", True):
                    continue
                for n in names:
                    st = jobs.get(f"{u} / {n}")
                    if st is None or st[1] != "success":
                        bad.append(f"{u} / {n}: {st and st[1] or 'ABSENT'}")
            return not bad, bad
        pre_pr = "" if self.plant.get("prelude_pr_blank") else r["pr"]
        api = {"prelude": {"conclusion": self.plant.get("prelude_conclusion", "success"),
                           "kind": self.plant.get("prelude_kind", r["kind"]), "pr": pre_pr},
               "jobs": r["jobs"], "runs_at_head": at_head,
               "live_pr": {"head_sha": self.head, "base_ref": self.base, "state": "open"},
               "open_pr_heads": {self.head}, "reaches_cc": self.truth.get("reaches_cc", True)}
        return G.gate(ctx, api)

    # ---- the clock -------------------------------------------------------------
    def run(self, events, until=9000):
        self.body_hist, self.review_hist = [(0, "b1")], []
        evs = sorted(events, key=lambda e: e[0])
        series = []
        for self.t in range(0, until):
            for e in [e for e in evs if e[0] == self.t]:
                self.apply(e[1], e[2] if len(e) > 2 else {})
            for r in sorted(self.runs, key=lambda r: r["id"]):
                self.try_start(r)
                self.step_run(r)
            self.hooks()
            series.append((self.t, self.binding("created"), self.binding("completed"), self.binding("every"),
                           self.oracle()))
        return series

    def apply(self, kind, p):
        pr_ev = dict(event="pull_request", head=self.head, base_ref=self.base, bot=p.get("bot", False))
        if kind == "push":
            self.head = p["head"]; pr_ev["head"] = self.head
            self.new_run(action="synchronize", held=p.get("held", False), **pr_ev)
        elif kind == "open":
            self.new_run(action="opened", **pr_ev)
        elif kind == "edit":
            self.body_hist.append((self.t, p["body"]))
            self.new_run(action="edited", **pr_ev)
        elif kind == "retarget":
            self.base = p["base"]; pr_ev["base_ref"] = self.base
            self.new_run(action="edited", changes_base=True, **pr_ev)
        elif kind == "review":
            self.review_hist.append((self.t, p["state"]))
            self.new_run(event="pull_request_review", head=self.head, base_ref=self.base, bot=False)
        elif kind == "dispatch":
            self.new_run(event="workflow_dispatch", head=self.head, input_pr=p.get("pr", ""),
                         input_base=p.get("base", ""), bot=True)

    def binding(self, how):
        """The merge box's `gate` under three readings: the newest check run by
        creation, the newest completed one, or EVERY suite's latest attempt (#2009:
        "GitHub's ruleset refuses a merge while any suite at the head carries a
        non-success run"). True = mergeable, False = refused, None = nothing yet."""
        gs = [g for g in self.gates if g["head"] == self.head and g["created"] <= self.t]
        done = [g for g in gs if g["completed"] is not None and g["completed"] <= self.t]
        if how == "created":
            if not gs:
                return None
            g = max(gs, key=lambda g: (g["created"], g["run"]))
            return g["ok"] if g in done else None
        if how == "completed":
            return max(done, key=lambda g: (g["completed"], g["run"]))["ok"] if done else None
        latest = {}
        for g in gs:
            if g["run"] not in latest or g["created"] >= latest[g["run"]]["created"]:
                latest[g["run"]] = g
        if not latest:
            return None
        if any(g not in done for g in latest.values()):
            return False if any(g in done and not g["ok"] for g in latest.values()) else None
        return all(g["ok"] for g in latest.values())

    def oracle(self):
        code = self.truth["code"](self.head, self.base)
        ok = all(code.get(u, True) for u in G.CODE)
        ok &= self.truth["brg"](self.review_at(self.t))
        ok &= self.truth["body"](self.body_at(self.t))
        return ok


def T(code=None, brg=None, body=None, reaches_cc=True):
    return {"code": code or (lambda h, b: {}), "brg": brg or (lambda rv: True),
            "body": body or (lambda b: True), "reaches_cc": reaches_cc}


SCEN = [
    ("A  null: open, all green", [(0, "open")], T(), {}),
    ("B  planted: prelude emits pr='' on a pull_request run", [(0, "open")], T(), {"prelude_pr_blank": True}),
    ("B2 planted: prelude concludes failure", [(0, "open")], T(), {"prelude_conclusion": "failure"}),
    ("B3 planted: prelude says kind=edit on a synchronize", [(0, "open")], T(), {"prelude_kind": "edit"}),
    ("B4 planted: a required unit given if:false on a code run", [(0, "open")], T(), {"unit_if_false": "hassfest"}),
    ("C  retarget runs to completion, code green at the new base",
     [(0, "open"), (2500, "retarget", {"base": "release"})], T(), {}),
    ("C2 retarget, code RED at the new base",
     [(0, "open"), (2500, "retarget", {"base": "release"})],
     T(code=lambda h, b: {"tests": b == "main"}), {}),
    ("D  retarget queued behind a running code run, then a body edit (case D)",
     [(0, "open"), (100, "retarget", {"base": "release"}), (103, "edit", {"body": "b2"})],
     T(code=lambda h, b: {"tests": b == "main"}), {}),
    ("D2 an edit's run is waiting when a retarget lands at the same head",
     [(0, "open"), (300, "edit", {"body": "b2"}), (400, "retarget", {"base": "release"})],
     T(code=lambda h, b: {"tests": b == "main"}), {}),
    ("D3 the same, code green at the new base",
     [(0, "open"), (300, "edit", {"body": "b2"}), (400, "retarget", {"base": "release"})], T(), {}),
    ("E  push while the old head runs, edit 2 s later (case E)",
     [(0, "open"), (100, "push", {"head": "H2"}), (102, "edit", {"body": "b2"})], T(), {}),
    ("F  budget raise: red until the owner approves",
     [(0, "open"), (2600, "review", {"state": "approved"})], T(brg=lambda rv: rv == "approved"), {}),
    ("F2 approval arrives while the code run is in flight",
     [(0, "open"), (300, "review", {"state": "approved"})], T(brg=lambda rv: rv == "approved"), {}),
    ("G  approval then dismissal", [(0, "open"), (2600, "review", {"state": "approved"}),
                                   (2700, "review", {"state": "dismissed"})], T(brg=lambda rv: rv == "approved"), {}),
    ("H  edit that breaks the contract, then a review 1 s later",
     [(0, "open"), (2600, "edit", {"body": "bad"}), (2601, "review", {"state": "approved"})],
     T(body=lambda b: b != "bad"), {}),
    ("H2 two edits 1 s apart while code runs, the second fixes the body",
     [(0, "open"), (300, "edit", {"body": "bad"}), (301, "edit", {"body": "b3"})], T(body=lambda b: b != "bad"), {}),
    ("H3 two edits 1 s apart while code runs, the second breaks the body",
     [(0, "open"), (300, "edit", {"body": "b3"}), (301, "edit", {"body": "bad"})], T(body=lambda b: b != "bad"), {}),
    ("I  bot head: held pull_request run + dispatch -f pr -f base",
     [(0, "push", {"head": "H1", "held": True}), (1, "dispatch", {"pr": "7", "base": "main"})], T(), {}),
    ("I2 bot head: held run + dispatch with NO pr (unnamed at a PR head)",
     [(0, "push", {"head": "H1", "held": True}), (1, "dispatch", {})], T(), {}),
    ("I3 bot head: dispatch names the wrong base",
     [(0, "push", {"head": "H1", "held": True}), (1, "dispatch", {"pr": "7", "base": "release"})], T(), {}),
    ("I4 bot head, then a body edit carried onto the dispatch run",
     [(0, "push", {"head": "H1", "held": True}), (1, "dispatch", {"pr": "7", "base": "main"}),
      (2200, "edit", {"body": "b2"})], T(), {}),
    ("K  D-2: arch-score red, diff misses custom_components/",
     [(0, "open")], T(body=lambda b: True, reaches_cc=False), {}),
]

# Expected verdicts where the oracle alone is not the point (planted defects).
MUST_FAIL = {"B", "B2", "B3", "B4", "I2", "I3"}


def main() -> int:
    rc = 0
    print(f"{'scenario':76s} {'layout':6s} {'oracle':6s} {'newest-created':14s} {'newest-completed':16s} {'every-suite':11s} {'false-green s':>13s}")
    for label, evs, truth, plant in SCEN:
        tag = label.split()[0]
        for layout in ("P2", "REV1"):
            w = World(layout, truth, plant)
            s = w.run(evs)
            t_end, bc, bd, be, orc = s[-1]
            if tag in MUST_FAIL:
                orc = False
            fg = max_win(s)
            row = f"{label[:76]:76s} {layout:6s} {fmt(orc):6s} {fmt(bc):14s} {fmt(bd):16s} {fmt(be):11s} {fg:13d}"
            if layout == "REV1":
                good = bc == orc and bd == orc and be == orc and fg <= WINDOW_OK
                if tag in MUST_FAIL:
                    good = bc is False and bd is False and be is False and fg == 0
                rc |= not good
                row += "  ok" if good else "  BAD"
                last = [r for r in w.runs if r.get("why")]
                if last and (not good or tag in MUST_FAIL):
                    row += f"  ({last[-1]['why'][0][:90]})"
            print(row)
    print("\n## the two hooks are load-bearing: revision 1 with one removed (unplanted scenarios)")
    for abl in (("sweep",), ("refresh",)):
        agree = {"created": 0, "completed": 0, "every": 0}; win = 0; n = 0
        for label, evs, truth, plant in SCEN:
            if label.split()[0] in MUST_FAIL:
                continue
            w = World("REV1", truth, plant, ablate=abl); s = w.run(evs); n += 1
            _, bc, bd, be, orc = s[-1]
            agree["created"] += bc == orc; agree["completed"] += bd == orc; agree["every"] += be == orc
            win = max(win, max_win(s))
        print(f"  without {abl[0]:8s}: agree newest-created {agree['created']}/{n}, newest-completed "
              f"{agree['completed']}/{n}, every-suite {agree['every']}/{n}; longest false-green window {win} s")
    print(f"\nGATE-SIM rc {rc}")
    return rc


def max_win(series):
    best = cur = 0
    for t, bc, bd, be, orc in series:
        if (bc or bd or be) and not orc:
            cur += 1; best = max(best, cur)
        else:
            cur = 0
    return best


def fmt(v):
    return {True: "pass", False: "FAIL", None: "none"}[v]


if __name__ == "__main__":
    sys.exit(main())
