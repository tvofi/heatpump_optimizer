"""Event-level replay of the umbrella: concurrency, waits, re-runs, the gate.

    python3 -I measure/rev/gate_sim.py > measure/rev/gate_sim.txt

Review items 1, 2, 3, 4, 10 and 12(c); revision 2 adds round-2 items N1 and N2;
revision 3 adds round-3 items R3-1, R3-2 and R3-4 (see "Revision 3" below).
Each scenario is a timed sequence of PR events. The simulator applies GitHub's
documented concurrency rule (design review ev/gh_docs_actions-group-concurrency.md:
at most one running and ONE pending run per group; a newly queued run CANCELS the
pending one whatever cancel-in-progress says; cancel-in-progress additionally cancels
the running one), runs each run's jobs with fixed durations, lets body readers read
the body and reviews at their own start, and evaluates the gate job with the gate
function.

Two platform rules revision 2 adds to the model (round 2):
  N1  A RE-RUN IS AN ATTEMPT OF THE SAME RUN AND RE-ENTERS THE RUN'S GROUP, with the
      run's own key and cancel-in-progress: it cancels the group's pending run and,
      when its cancel-in-progress is true, the group's running one. The tree measured
      it (dev/audit/rca/R9-RC-PRCONTRACT.md:84-86, :188, :227; round-2 review
      ev/rerun_group_runs_api.json: attempt 4 of run 37315758446 cancelled the NEWER
      run 37324419853). Applied to every layout.
  N2  A `gate` attempt, first or re-run, is a job: it is LISTED (in_progress) when it
      starts, reads the API GATE_READ s later, and completes GATE s after it starts.
      Revision 1's simulator finished a hook re-run on the next tick (step_run saw the
      run in_progress with its old gate_at), so two gates one sweep re-ran together
      never saw each other running. Here two gates started together read together.

Three layouts are replayed over the SAME scenarios:
  P2   phase 2 as written (one `CI-<pr>` group, cancel only on a non-edit
       pull_request, governance/hassfest/validate guarded on `action != 'edited'`,
       applicability from the prelude's `pr`, the newest completed non-cancelled code
       run carried with no base check, the prelude waits only for code runs). It is
       the review seat's `gate41_model.py` reading, given each run's kind for free.
  REV1 revision 1 as written (code / edit / review lanes with cancel-in-progress;
       the defer rule waits for EVERY unfinished run at the head). Kept to show that
       the fixed model reproduces both round-2 defects.
  REV2 revision 2, carrying revision 3's rules since round 3 (the name is kept so the
       round-3 seat's instruments, which build World("REV2", ...), run unchanged)
       (DESIGN-P2.md 2.2, 4.1, 4.3): every run in its own run-id group
       (a re-run joins a group that holds only itself, so N1 cancels nothing);
       `cancel-superseded` (tools/pr/cancel_superseded.py, unchanged rule) cancels
       older runs at a DIFFERENT head only, CANCEL_SUP s after a run starts, from a
       run at the PR's live head; the defer rule waits only for runs that can still
       add a source (gate_model.judging). Verdict preludes still wait for every
       earlier run at the head; every code unit is guarded on the prelude's kind.
  Hooks (REV1, REV2): REFRESH (a PR event's run re-runs the `gate` job of every
       completed run at its head whose latest gate is green, REFRESH s after it
       starts) and SWEEP (a green `gate` re-runs the `gate` job of every older run at
       its head whose latest gate completed red, SWEEP s later). Both act only when
       their head is the PR's live head. Near GitHub's 50-attempt limit the last
       attempts are refresh's: the sweep never takes a run to ATTEMPT_CAP and
       refresh never past it, so an exhausted run is left red (fail closed: a new
       push resets it), never stale-green.
       CHAIN: whether a re-run attempt's own green completion fires the sweep again
       (a `workflow_run` per attempt). Unmeasured, so both arms are scored.

Revision 3 (round 3):
  R3-1 THE SWEEP POLLS. A gate attempt that read red while a newer run was busy can
       still be RUNNING when that run's green gate fires the sweep (job teardown and
       run finalisation lie between its read and its completion), and the sweep
       cannot re-run a running run. So `gate.py --sweep`, after re-running every older
       completed red gate at the head, polls every older run whose gate attempt is
       not completed (rev4, R4-3: queued, waiting or in progress), every SWEEP_POLL s
       for at most SWEEP_WAIT s, and re-runs each that
       completes red while the head is still live and the triggering run's latest gate
       is still green AND began after every run at the head was created (its verdict
       covers the newest event; else a newer run's own sweep owns convergence, and a
       chained sweep from an older run would re-run gates that read red again). A TAIL arm makes a re-run attempt (or every attempt) complete
       TAIL s later than its read; READ-LATE moves the read to 2 s before completion
       (the null: only the read-to-completion gap matters). REV2 must score 0 END-BAD
       over every TAIL; the `poll` ablation (revision 2's sweep) reproduces the
       round-3 failures.
  R3-2 EARLY LISTING. Arm EARLY lists a run's `gate` job as `waiting` from the moment
       its units are scheduled (the platform fact revision 2 relied on, reversed).
       REV2's hardened `judging` must still score; revision 2's (`listed` ablation)
       does not.
  R3-4 A fork PR: the plant `fork` is refused under all three readings.
  The gate is passed its run's attempt; an attempt at ATTEMPT_CAP reads red.

The ORACLE is independent of all three: once every run has completed, the PR should
be mergeable iff every code unit is green at (final head, final base) and the body
readers are green for the final body and reviews. Each row prints the merge box under
THREE readings of which `gate` check binds when several exist at one head: the newest
by creation, the newest completed, and every suite's latest attempt (the tree records
"GitHub's ruleset refuses a merge while any suite at the head carries a non-success
run", tools/policy/budget_raise_gate.py:604, #2009); then the longest window in which
the merge box read green while the oracle read red, and the most attempts any run
reached. Exit 0 only when REV2, under BOTH chain arms, agrees with the oracle on every
unplanted scenario under all three readings, has no false-green window longer than
WINDOW_OK seconds, refuses every planted defect under all three, and no run passes
ATTEMPT_CAP. REV1 and P2 rows are printed for comparison. A last block removes each
hook from REV2 in turn, then each of revision 2's two fixes (`runid`: revision 1's
lanes instead of run-id groups; `judging`: revision 1's defer rule), to show each is
load-bearing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_model as G  # noqa: E402

DUR = {"tests": 2000, "codeql": 1300, "governance": 190, "hassfest": 30, "validate": 50,
       "arch-score": 60, "budget-raise-gate": 16, "pr-contract": 28}
PRELUDE, GATE, GATE_READ, CANCEL_LAG, CANCEL_SUP, WINDOW_OK = 5, 15, 5, 5, 10, 120
REFRESH, SWEEP = 10, 20      # seconds from a PR event's run start to its refresh re-runs; from a green gate to the sweep
SWEEP_POLL, SWEEP_WAIT = 5, 600   # rev3, R3-1: the sweep polls running older gate attempts, bounded
ATTEMPT_CAP = G.ATTEMPT_CAP  # gate.py's hooks never take a run past this attempt (GitHub fails the 51st)
TAILS = (0, 20, 30, 35, 40, 45, 50, 60, 120, 300)   # rev3, R3-1: the round-3 seat's grid
CODE_U = list(G.CODE)


class World:
    tail, tail_all, read_late, early = 0, False, False, False      # rev3 arms (R3-1, R3-2)

    def __init__(self, layout, truth, plant=None, ablate=(), chain=True):
        self.layout, self.truth, self.plant, self.ablate, self.chain = layout, truth, plant or {}, set(ablate), chain
        self.runs, self.t, self.nid = [], 0, 100
        self.head, self.base, self.body, self.review = "H1", "main", "b1", "none"
        self.gates = []          # {"created", "completed", "ok", "run", "head"}
        self.todo = []           # (time, action, run): scheduled hooks and cancel-superseded
        self.log = []

    # ---- concurrency -------------------------------------------------------
    def group(self, r):
        if self.layout == "REV2" and "runid" not in self.ablate:
            return f"run-{r['id']}"
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
        if self.layout == "REV1" or "runid" in self.ablate:
            return r["event"] in ("pull_request", "pull_request_review") and not r["bot"]
        return False

    def enter_group(self, r, why):
        """The documented group rule, for a new run and (N1) for a re-run attempt."""
        g = r["group"]
        for o in self.runs:
            if o is r or o.get("group") != g:
                continue
            if o["status"] == "pending":
                self.cancel(o)
                self.log.append((self.t, f"{why} {r['id']} cancels pending {o['id']}"))
            elif o["status"] == "in_progress" and self.cancels_running(r) and o.get("cancel_at") is None:
                o["cancel_at"] = self.t + CANCEL_LAG
                if why == "re-run of":
                    self.log.append((self.t, f"re-run of {r['id']} cancels {o['id']}"))

    def new_run(self, **kw):
        self.nid += 1
        r = {"held": False, "bot": False, "action": "", "changes_base": False, **kw,
             "id": self.nid, "created": self.t, "status": "pending", "jobs": {}, "start": None, "end": None,
             "attempt": 1}
        kind, pr, base = G.derive({"event_name": r["event"], "action": r["action"],
                                   "changes_base": r["changes_base"], "pr_number": "7",
                                   "base_ref": r.get("base_ref", ""), "input_pr": r.get("input_pr", ""),
                                   "input_base": r.get("input_base", "")})
        r.update(kind=kind, pr=pr, base=base, title=G.title(kind, pr, base, r["head"]))
        if r["held"]:
            r["status"] = "action_required"
            self.runs.append(r)
            return r
        r["group"] = self.group(r)
        self.enter_group(r, "new run")
        self.runs.append(r)
        return r

    def cancel(self, o):
        for u in o.get("sched", {}):
            if u not in o["done"]:
                for n in G.REQUIRED[u]:
                    o["jobs"][f"{u} / {n}"] = ("completed", "cancelled")
        if o.get("gate_t0") is not None:                     # a gate attempt in flight is cancelled too
            o["gate_entry"].update(completed=self.t, ok=False)
            o["jobs"]["gate"] = ("completed", "cancelled")
            o["gate_t0"] = None
        o["status"], o["conclusion"], o["end"], o["cancel_at"] = "completed", "cancelled", self.t, None

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
        if self.layout != "P2" and r["event"] in ("pull_request", "pull_request_review") and "refresh" not in self.ablate:
            self.todo.append((self.t + REFRESH, "refresh", r))
        if self.layout == "REV2" and r["event"] == "pull_request" and not r["bot"]:
            self.todo.append((self.t + CANCEL_SUP, "supersede", r))

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
            self.cancel(r)
            return
        if r["attempt"] > 1 or self.t < r["prelude_done"]:   # N2: a re-run attempt is the gate's alone (gate_tick)
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
            if self.early:                             # rev3, R3-2: the gate job listed before its needs end
                r["jobs"]["gate"] = ("waiting", None)
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
            if "gate_entry" not in r:
                self.start_gate(r)

    def start_gate(self, r):
        """A `gate` attempt, the run's first or a hook's re-run: listed now, reads at
        +GATE_READ, completes at +GATE (N2)."""
        r["gate_t0"], r["gate_read"] = self.t, None
        r["jobs"]["gate"] = ("in_progress", None)
        x = self.tail if (r["attempt"] > 1 or self.tail_all) else 0      # rev3, R3-1: the TAIL arm
        r["gate_len"] = GATE + x
        r["gate_rd"] = (GATE - 2 + x) if self.read_late else GATE_READ
        r["gate_entry"] = {"created": self.t, "completed": None, "ok": None, "run": r["id"], "head": r["head"]}
        self.gates.append(r["gate_entry"])

    def gate_tick(self, r, phase):
        t0 = r.get("gate_t0")
        if t0 is None or r["status"] != "in_progress":
            return
        if phase == "read" and r["gate_read"] is None and self.t >= t0 + r.get("gate_rd", GATE_READ):
            r["gate_read"] = self.eval_gate(r)
        if phase == "finish" and self.t >= t0 + r.get("gate_len", GATE):
            self.finish_gate(r)

    def finish_gate(self, r):
        ok, why = r["gate_read"]
        r["gate_entry"].update(completed=self.t, ok=ok)
        r["why"] = why
        r["jobs"]["gate"] = ("completed", "success" if ok else "failure")
        r["gate_t0"] = None
        r["status"], r["conclusion"], r["end"] = "completed", "success" if ok else "failure", self.t
        if ok and self.layout != "P2" and "sweep" not in self.ablate and (self.chain or r["attempt"] == 1):
            self.todo.append((self.t + SWEEP, "sweep", r))

    # ---- the hooks (DESIGN-P2.md 4.3) and cancel-superseded --------------------------
    def latest_gate(self, r):
        es = [g for g in self.gates if g["run"] == r["id"]]
        return max(es, key=lambda g: g["created"]) if es else None

    def rerun_gate(self, o):
        o["attempt"] += 1
        o["status"], o["conclusion"] = "in_progress", None
        self.enter_group(o, "re-run of")                 # N1
        self.start_gate(o)

    def covers_newest(self, src):
        """rev3, R3-1: src's latest gate is green and completed, and it started after
        every run at its head was created, so its verdict covers the newest event.
        Otherwise a newer run exists whose own sweep owns convergence (and polls)."""
        g = self.latest_gate(src)
        newest = max(o["created"] for o in self.runs if o["head"] == src["head"])
        return bool(g and g["completed"] is not None and g["ok"] and g["created"] >= newest)

    def hooks(self):
        for item in [x for x in self.todo if x[0] == self.t]:
            self.todo.remove(item)
            what, src = item[1], item[2]
            if what == "sweep-poll":
                # rev3, R3-1: the sweep job is still polling run o's running gate attempt.
                o, deadline = item[3], item[4]
                if src["head"] != self.head:
                    continue                                   # a push left the head: stop, as --sweep does
                if o["status"] != "completed":
                    if self.t + SWEEP_POLL <= deadline:
                        self.todo.append((self.t + SWEEP_POLL, "sweep-poll", src, o, deadline))
                    else:
                        self.log.append((self.t, f"sweep: run {o['id']} still running at the bound; left as is"))
                    continue
                g = self.latest_gate(o)
                if g and g["completed"] is not None and not g["ok"] and self.covers_newest(src):
                    if o["attempt"] >= ATTEMPT_CAP - 1:
                        self.log.append((self.t, f"sweep: run {o['id']} at attempt {o['attempt']} not re-run"))
                        continue
                    self.log.append((self.t, f"sweep: polled run {o['id']} completed red; re-run"))
                    self.rerun_gate(o)
                continue
            if what == "supersede":
                # tools/pr/cancel_superseded.py: from a run at the live head, cancel every
                # older active pull_request / dispatch run at a DIFFERENT head.
                if src["status"] == "in_progress" and src["head"] == self.head:
                    for o in self.runs:
                        if (o["id"] < src["id"] and o["head"] != src["head"] and o["status"] in ("pending", "in_progress")
                                and o["event"] in ("pull_request", "workflow_dispatch") and o.get("cancel_at") is None):
                            o["cancel_at"] = self.t + CANCEL_LAG
                continue
            if src["head"] != self.head:                       # gate.py --refresh / --sweep: only at the live head
                continue
            if what == "sweep" and "poll" not in self.ablate and self.covers_newest(src):
                # rev3, R3-1: every older run whose gate attempt is RUNNING now is polled to
                # completion (it may have read red before src's gate went green).
                for o in self.runs:
                    if (o is not src and o["head"] == src["head"] and o["id"] < src["id"]
                            and o["status"] != "completed" and o.get("gate_t0") is not None):   # rev4, R4-3: not completed, not only in_progress
                        self.todo.append((self.t + SWEEP_POLL, "sweep-poll", src, o, self.t + SWEEP_WAIT))
            for o in self.runs:
                if o is src or o["head"] != src["head"] or o["status"] != "completed":
                    continue
                g = self.latest_gate(o)
                if g is None or g["completed"] is None:
                    continue
                # refresh: re-judge every green gate an event may have made stale;
                # sweep: re-judge every older red gate once a gate at the head is green
                if (what == "refresh" and g["ok"]) or (what == "sweep" and not g["ok"] and o["id"] < src["id"]):
                    if o["attempt"] >= (ATTEMPT_CAP if what == "refresh" else ATTEMPT_CAP - 1):
                        self.log.append((self.t, f"{what}: run {o['id']} at attempt {o['attempt']} not re-run"))
                        continue
                    self.rerun_gate(o)

    def eval_gate(self, r):
        ctx = {"event_name": r["event"], "action": r["action"], "changes_base": r["changes_base"],
               "pr_number": "7", "base_ref": r.get("base_ref", ""), "input_pr": r.get("input_pr", ""),
               "input_base": r.get("input_base", ""), "sha": r["head"], "run_id": r["id"],
               "run_attempt": r["attempt"]}
        # revision 1's defer rule: every unfinished run defers, listed gate or not
        hide = self.layout == "REV1" or "judging" in self.ablate
        at_head = [dict(id=o["id"], title=o["title"], status=o["status"],
                        jobs={k: v for k, v in o["jobs"].items() if not (hide and k == "gate")})
                   for o in self.runs if o["head"] == r["head"] and o is not r]
        if "listed" in self.ablate:
            # rev3, R3-2 ablation: revision 2's judging, which trusted a listed gate
            for o in at_head:
                js = o["jobs"]
                o["rev2_judging"] = "gate" in js and all(st[0] == "completed" for k, st in js.items()
                                                         if k == "prelude" or k.split(" / ")[0] in G.REQUIRED)
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
               "live_pr": {"head_sha": self.head, "base_ref": self.base, "state": "open",
                           "same_repo": not self.plant.get("fork")},
               "open_pr_heads": {self.head}, "reaches_cc": self.truth.get("reaches_cc", True)}
        if "listed" in self.ablate:
            saved = G.judging
            G.judging = lambda run: run.get("rev2_judging", False)
            try:
                return G.gate(ctx, api)
            finally:
                G.judging = saved
        return G.gate(ctx, api)

    # ---- the clock -------------------------------------------------------------
    def run(self, events, until=9000):
        self.body_hist, self.review_hist = [(0, "b1")], []
        evs = sorted(events, key=lambda e: e[0])
        series = []
        for self.t in range(0, until):
            for e in [e for e in evs if e[0] == self.t]:
                self.apply(e[1], e[2] if len(e) > 2 else {})
            order = sorted(self.runs, key=lambda r: r["id"])
            for r in order:
                self.try_start(r)
                self.step_run(r)
            for r in order:                    # every read due this tick sees the same state
                self.gate_tick(r, "read")
            for r in order:
                self.gate_tick(r, "finish")
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


APPROVE = T(brg=lambda rv: rv == "approved")
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
     [(0, "open"), (2600, "review", {"state": "approved"})], APPROVE, {}),
    ("F2 approval arrives while the code run is in flight",
     [(0, "open"), (300, "review", {"state": "approved"})], APPROVE, {}),
    ("G  approval then dismissal", [(0, "open"), (2600, "review", {"state": "approved"}),
                                   (2700, "review", {"state": "dismissed"})], APPROVE, {}),
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
    ("I5 planted: a fork PR (its head is not in this repository; rev3, R3-4)",
     [(0, "open"), (300, "edit", {"body": "b2"})], T(), {"fork": True}),
    # round 2 (N1): the review seat's tools/rerun_concurrency_sim.py scenarios
    ("R1 retarget after the code run is green (refresh re-runs C's gate)",
     [(0, "open"), (2100, "retarget", {"base": "release"})], T(), {}),
    ("R2 body edit after an earlier edit's gate is green, new body breaks the contract",
     [(0, "open"), (2100, "edit", {"body": "b2"}), (2400, "edit", {"body": "bad"})], T(body=lambda b: b != "bad"), {}),
    ("R3 approval, then dismissal 300 s later (scenario G, spaced)",
     [(0, "open"), (2600, "review", {"state": "approved"}), (2900, "review", {"state": "dismissed"})], APPROVE, {}),
    ("R4 edit and review both land while the code run is in flight",
     [(0, "open"), (300, "edit", {"body": "b2"}), (301, "review", {"state": "approved"})], APPROVE, {}),
    ("R5 a body that breaks the contract, then an edit 300 s later that fixes it",
     [(0, "open"), (2100, "edit", {"body": "bad"}), (2400, "edit", {"body": "b3"})], T(body=lambda b: b != "bad"), {}),
    ("R6 changes requested on a raise, then the owner approves 300 s later",
     [(0, "open"), (2600, "review", {"state": "changes"}), (2900, "review", {"state": "approved"})], APPROVE, {}),
    ("R7 an approval, then a plain comment review 300 s later",
     [(0, "open"), (2600, "review", {"state": "approved"}), (2900, "review", {"state": "approved"})], APPROVE, {}),
    ("R8 a review lands during a retarget's code run (item 1's outside actor)",
     [(0, "open"), (2100, "retarget", {"base": "release"}), (2300, "review", {"state": "approved"})], APPROVE, {}),
    # round 2 (N2): the review seat's tools/rerun_status_fix.py scenarios
    ("X1 edit and review 1 s apart, both during the code run",
     [(0, "open"), (300, "edit", {"body": "b2"}), (301, "review", {"state": "approved"})], APPROVE, {}),
    ("X3 edit, then review 600 s later, both during the code run",
     [(0, "open"), (300, "edit", {"body": "b2"}), (900, "review", {"state": "approved"})], APPROVE, {}),
    ("X4 two reviews 600 s apart during the code run (approve, approve)",
     [(0, "open"), (300, "review", {"state": "approved"}), (900, "review", {"state": "approved"})], APPROVE, {}),
    ("X5 three edits and two reviews during the code run",
     [(0, "open"), (200, "edit", {"body": "b2"}), (400, "review", {"state": "approved"}), (600, "edit", {"body": "b3"}),
      (800, "review", {"state": "approved"}), (1000, "edit", {"body": "b4"})], APPROVE, {}),
]
# N1 across heads: a push lands just before, inside and after the window between an edit
# run's green gate and the sweep it fires (the review seat's tools/sweep_crosshead.py).
_SWEEP_BASE = [(0, "open"), (300, "edit", {"body": "b2"})]
STRESS = [(f"{tag} {n} edits at one head after the code run, 150 s apart (attempt bound)",
           [(0, "open")] + [(2100 + 150 * i, "edit", {"body": f"b{i}"}) for i in range(n)], T(), {})
          for tag, n in (("S", 20), ("S2", 25))]
# S2 passes the cap on purpose: the expected end is red under every-suite (the code run's
# last attempt was refresh's), right under the other two, with no false green.
CAPPED = {"S2"}

# Expected verdicts where the oracle alone is not the point (planted defects).
MUST_FAIL = {"B", "B2", "B3", "B4", "I2", "I3", "I5"}


def crosshead():
    w = World("REV2", T(), {}); w.run(_SWEEP_BASE, until=3000)
    end = [r for r in w.runs if r["kind"] == "edit"][0]["gate_entry"]["completed"]
    return [(f"XH push lands {dt:+d} s from the edit run's green gate (sweep at +{SWEEP})",
             _SWEEP_BASE + [(end + dt, "push", {"head": "H2"})], T(), {}) for dt in (-5, 1, 10, 19, 25)]


def score(layout, chain, scen, ablate=(), **arm):
    """[(label, tag, verdicts, good, max attempt, why, log, end_ok)] for one layout and
    arm. end_ok judges the final merge box only (END-BAD is its negation); good adds
    the false-green window and the attempt cap. `arm` sets the rev3 World arms."""
    out = []
    for label, evs, truth, plant in scen:
        tag = label.split()[0]
        w = World(layout, truth, plant, ablate=ablate, chain=chain)
        for k, v in arm.items():
            setattr(w, k, v)
        # a tail serialises the verdict preludes' waits (S2: 25 edits, each gate +TAIL s), so the horizon grows with it
        s = w.run(evs, until=9000 + 40 * arm.get("tail", 0))
        _, bc, bd, be, orc = s[-1]
        if tag in MUST_FAIL:
            orc = False
        fg = max_win(s)
        att = max(r["attempt"] for r in w.runs)
        good = bc == orc and bd == orc and be == orc and fg <= WINDOW_OK and att <= ATTEMPT_CAP
        if tag in CAPPED:   # past the cap every-suite may read red (fail closed), never green against a red oracle
            good = bc == orc and bd == orc and be in (False, orc) and fg <= WINDOW_OK and att <= ATTEMPT_CAP
        if tag in MUST_FAIL:
            good = bc is False and bd is False and be is False and fg == 0
        end_ok = (bc, bd, be) == (False, False, False) if tag in MUST_FAIL else (
            (bc == orc and bd == orc and be in (False, orc)) if tag in CAPPED else (bc == orc and bd == orc and be == orc))
        why = next((r["why"][0] for r in reversed(w.runs) if r.get("why")), "")
        out.append((label, tag, (orc, bc, bd, be, fg), good, att, why, [m for _, m in w.log], end_ok))
    return out


def main() -> int:
    rc = 0
    scen = SCEN + crosshead() + STRESS
    unplanted = [x for x in scen if x[0].split()[0] not in MUST_FAIL | CAPPED]
    print(f"{'scenario':76s} {'layout':11s} {'oracle':6s} {'newest-created':14s} {'newest-completed':16s} "
          f"{'every-suite':11s} {'false-green s':>13s} {'attempts':>8s}")
    runs = {(lay, ch): score(lay, ch, scen) for lay, ch in (("P2", True), ("REV1", True), ("REV2", True), ("REV2", False))}
    for i, (label, *_rest) in enumerate(scen):
        for key in (("P2", True), ("REV1", True), ("REV2", True), ("REV2", False)):
            lab, tag, (orc, bc, bd, be, fg), good, att, why, log, _end = runs[key][i]
            name = key[0] if key[0] == "P2" else f"{key[0]}/{'chain' if key[1] else 'nochain'}"
            row = (f"{label[:76]:76s} {name:11s} {fmt(orc):6s} {fmt(bc):14s} {fmt(bd):16s} {fmt(be):11s} "
                   f"{fg:13d} {att:8d}")
            if key[0] != "P2":
                row += "  ok" if good else "  BAD"
                if key[0] == "REV2":
                    rc |= not good
                if why and (not good or tag in MUST_FAIL):
                    row += f"  ({why[:80]})"
                cancels = [m for m in log if "cancels" in m]
                if cancels:
                    row += f"  [{'; '.join(cancels)[:120]}]"
            print(row)
    print("\n## totals")
    for key in (("REV1", True), ("REV2", True), ("REV2", False)):
        rows = runs[key]
        bad = [r[1] for r in rows if not r[3]]
        print(f"  {key[0]}/{'chain' if key[1] else 'nochain'}: BAD {len(bad)} of {len(rows)} {bad}; "
              f"most attempts of any run {max(r[4] for r in rows if r[1] not in CAPPED)} (S2, past the cap: "
              f"{max(r[4] for r in rows if r[1] in CAPPED)}); "
              f"longest false-green window {max(r[2][4] for r in rows if r[1] not in MUST_FAIL)} s; "
              f"runs a re-run attempt cancelled (N1) {sum(m.startswith('re-run of') for r in rows for m in r[6])}")
    p2 = runs[("P2", True)]
    for how, j in (("newest-created", 1), ("newest-completed", 2), ("every-suite", 3)):
        n = sum(1 for r in p2 if r[1] not in MUST_FAIL | CAPPED and r[2][j] == r[2][0])
        print(f"  P2 agrees with the oracle under {how}: {n}/{len(unplanted)}")
    print(f"  P2 planted defects refused under all three readings: "
          f"{sum(1 for r in p2 if r[1] in MUST_FAIL and r[2][1:4] == (False, False, False))} of {len(MUST_FAIL)}")
    print("\n## each revision-2 element is load-bearing: revision 2 with one removed (unplanted scenarios, chain arm)")
    for abl in (("sweep",), ("refresh",), ("runid",), ("judging",)):
        rows = score("REV2", True, unplanted, ablate=abl)
        agree = [sum(r[2][j] == r[2][0] for r in rows) for j in (1, 2, 3)]
        print(f"  without {abl[0]:8s}: agree newest-created {agree[0]}/{len(rows)}, newest-completed "
              f"{agree[1]}/{len(rows)}, every-suite {agree[2]}/{len(rows)}; longest false-green window "
              f"{max(r[2][4] for r in rows)} s")
    rc |= rev3(scen, unplanted)
    print(f"\nGATE-SIM rc {rc}")
    return rc


def end_bad(rows):
    return [f"{r[1]}(oracle {fmt(r[2][0])}: created {fmt(r[2][1])} completed {fmt(r[2][2])} every {fmt(r[2][3])})"
            for r in rows if not r[7]]


def rev3(scen, unplanted) -> int:
    """Revision 3's arms (round-3 items R3-1 and R3-2). Every REV2 row must be END-BAD 0;
    every ablation row must move (END-BAD > 0), or the arm proves nothing."""
    rc = 0
    print("\n## rev3, R3-1: TAIL arm, REV2 (a gate attempt completes TAIL s after gate_sim's +15 s; its read stays at +5 s)")
    print("   END-BAD = the final merge box differs from the oracle under some reading (plants: not refused under all three);")
    print("   the false-green window grows with the tail by construction (the refresh attempt that turns a stale green red")
    print("   completes later), so it is printed, not scored, as the round-3 seat's instruments do")
    arms = [("re-run attempts", dict(tail=t)) for t in TAILS]
    arms += [("every attempt", dict(tail=t, tail_all=True)) for t in (35, 60, 120, 300)]
    arms += [("READ-LATE (null: read 2 s before completion)", dict(tail=t, read_late=True)) for t in (35, 120, 300)]
    for what, arm in arms:
        for chain in (True, False):
            rows = score("REV2", chain, scen, **arm)
            bad = end_bad(rows)
            rc |= bool(bad)
            print(f"  {what:44s} tail {arm['tail']:3d} s {'chain  ' if chain else 'nochain'} END-BAD {len(bad)}  "
                  f"false-green max {max(r[2][4] for r in rows if r[1] not in MUST_FAIL):4d} s  {'; '.join(bad)[:200]}")
    print("  null control: revision 2's sweep (no polling), the `poll` ablation; it must move")
    for t in (35, 120, 300):
        for chain in (True, False):
            bad = end_bad(score("REV2", chain, scen, ablate=("poll",), tail=t))
            rc |= not bad
            print(f"  without poll, tail {t:3d} s {'chain  ' if chain else 'nochain'} END-BAD {len(bad)}  {'; '.join(bad)[:200]}")
    print("\n## rev3, R3-2: EARLY arm (a run's `gate` job is listed `waiting` from the moment its units are scheduled)")
    def wins(rows):
        return max(r[2][4] for r in rows if r[1] not in MUST_FAIL), [f"{r[1]} {r[2][4]} s" for r in rows
                                                                    if r[1] not in MUST_FAIL and r[2][4] > 25]
    hard = 0
    for chain in (True, False):
        rows = score("REV2", chain, scen, early=True)
        bad = end_bad(rows)
        nogood = [r[1] for r in rows if not r[3]]
        rc |= bool(bad) or bool(nogood)
        fg, _ = wins(rows); hard = max(hard, fg)
        print(f"  REV2 (hardened judging) {'chain  ' if chain else 'nochain'} END-BAD {len(bad)}; rows not ok (window, cap) "
              f"{len(nogood)} {nogood}; false-green max {fg} s")
    print("  null control: revision 2's judging (trusts a listed gate); it must move, here the false-green window")
    for chain in (True, False):
        rows = score("REV2", chain, scen, ablate=("listed",), early=True)
        fg, where = wins(rows)
        rc |= fg <= hard
        print(f"  revision 2's judging, EARLY, {'chain  ' if chain else 'nochain'}: END-BAD {len(end_bad(rows))}; "
              f"false-green max {fg} s  [{'; '.join(where)}]")
    rows = score("REV2", True, scen, ablate=("listed",))
    rc |= bool(end_bad(rows)) or wins(rows)[0] > 25
    print(f"  ... and revision 2's judging without EARLY (the platform fact holds): END-BAD {len(end_bad(rows))}; "
          f"false-green max {wins(rows)[0]} s")
    print(f"\nREV3 arms rc {rc}")
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
