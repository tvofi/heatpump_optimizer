"""Self-test of round_metrics.py: the empty-input null control, a planted case per read, and one mutant per predicate.

Run through round_metrics.py's own test mode. Offline: planted state dirs, a throwaway git
repository (tests/throwaway_git.py) for the roster-entry clock, the merge classes, the round
windows and the gate check count, and a fake paginator for the producer's API half. The mutants
edit a temp copy of round_metrics.py; a mutant that survives, or whose copy does not run, fails.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

T0 = 1_800_000_000  # 2027-01-15T08:00Z; every planted stamp is T0 plus hours
H = 3600
D = 86400


def chk(f) -> bool:
    """A case that raises reads False, so a mutant that crashes a read is killed by its case's FAIL line."""
    try:
        return bool(f())
    except Exception:
        return False


def load(path: Path):
    spec = importlib.util.spec_from_file_location("round_metrics_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def at(m, hours: float) -> str:
    return m.datetime.fromtimestamp(T0 + hours * H, m.timezone.utc).isoformat().replace("+00:00", "Z")


def tsv(rows) -> str:
    return "sha\tpr\tct\tclass\ttokens\tgroup\tentered\n" + "".join(
        f"s{i}\t{i}\t{T0 + ct * H}\t{c}\tb\t{g}\t{'' if e is None else T0 + e * H}\n" for i, (ct, c, g, e) in enumerate(rows))


def state(td: Path, merges=None, runs=None, jobs=None, ci=None, tokens=None) -> Path:
    d = td / "sc"
    (d / "jobs").mkdir(parents=True, exist_ok=True)
    if merges is not None:
        (d / "merges.tsv").write_text(tsv(merges))
    if runs is not None:
        (d / "runs.json").write_text(json.dumps(runs))
    if ci is not None:
        (d / "ci_runs.json").write_text(json.dumps(ci))
    for rid, doc in (jobs or {}).items():
        (d / "jobs" / f"jobs_{rid}.json").write_text(json.dumps(doc))
    if tokens is not None:
        (d / "tokens.tsv").write_text("t\tseat_class\ttokens\n" + "".join(f"{t}\t{c}\t{n}\n" for t, c, n in tokens))
    return d


def gate_doc(*concl, attempt=1):
    """A job listing whose gate job concluded concl[k] at attempt k+1."""
    return {"attempt": attempt, "jobs": [{"name": "gate", "conclusion": c, "run_attempt": k + 1,
                                          "started_at": None, "completed_at": None} for k, c in enumerate(concl)]}


def git_cases(m, tests: Path, r: dict) -> None:
    sys.path.insert(0, str(tests))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        env = throwaway_git_init(repo, "-q", "-b", "main")

        def commit(when: int, files: dict, msg="c", merge_of=None):
            for f, text in files.items():
                (repo / f).parent.mkdir(parents=True, exist_ok=True)
                (repo / f).write_text(text)
            subprocess.run(["git", "add", "-A"], cwd=repo, env=env, check=True)
            e = dict(env, GIT_COMMITTER_DATE=f"{when} +0000", GIT_AUTHOR_DATE=f"{when} +0000")
            if merge_of:
                subprocess.run(["git", "merge", "-q", "--no-ff", "-m", msg, merge_of], cwd=repo, env=e, check=True)
            else:
                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", msg], cwd=repo, env=e, check=True)
            return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, env=env, capture_output=True, text=True).stdout.strip()

        ros = "dev/programme/rosters/wave-r1-groups.json"
        g = lambda *names: json.dumps({"groups": [{"group": n, "resume": {"pr": 7} if n == "G-PR" else {}} for n in names]},
                                      indent=1)
        commit(T0, {ros: g("G-A"), "tools/ci/gate.py": "REQUIRED = {'push': ('a', 'b')}\n",
                   "dev/audit/rounds/round1/JUDGE.json": "[]"}, "base")
        subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, env=env, check=True)
        commit(T0 + 2 * H, {ros: g("G-A", "G-B", "G-PR")}, "add G-B")
        subprocess.run(["git", "tag", "v1.0.0"], cwd=repo, env=env, check=True)
        commit(T0 + 3 * H, {ros: g("G-PR", "G-B", "G-A")}, "reorder: no group is added again")
        subprocess.run(["git", "checkout", "-q", "-b", "fix/g-b-p2"], cwd=repo, env=env, check=True)
        commit(T0 + 4 * H, {"custom_components/x.py": "x = 1\n"})
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
        commit(T0 + 5 * H, {}, "Merge pull request #5 from o/fix/g-b-p2", merge_of="fix/g-b-p2")
        subprocess.run(["git", "checkout", "-q", "-b", "fix/other"], cwd=repo, env=env, check=True)
        commit(T0 + 6 * H, {"tools/ci/gate.py": "REQUIRED = {'push': ('a', 'b', 'c')}\n"})
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
        commit(T0 + 7 * H, {}, "Merge pull request #7 from o/fix/other", merge_of="fix/other")
        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=repo, env=env, check=True)

        e = m.roster_entries(repo, "main", {})
        r["roster clock: a group's entry is the commit that first added it, not a later reorder"] = \
            e["entered"] == {"G-A": T0, "G-B": T0 + 2 * H, "G-PR": T0 + 2 * H}
        e2 = m.roster_entries(repo, "main", {"tip": e["tip"], "entered": {"G-A": 1}})
        r["roster clock: an incremental scan from the cached tip keeps the cache"] = e2["entered"] == {"G-A": 1}
        groups = m.rosters_at(repo, "main")
        rows = m.merge_rows(repo, T0, [], groups, e["entered"])
        r["merges: classes by machinery_ratchet, a split part maps to its group, resume.pr wins"] = \
            [(x["pr"], x["class"], x["group"], x["entered"]) for x in rows] == \
            [(5, "production", "G-B", T0 + 2 * H), (7, "machinery", "G-PR", T0 + 2 * H)]
        r["merges: a cached class is not re-derived"] = \
            m.merge_rows(repo, T0, [{"sha": rows[0]["sha"], "class": "record"}], groups, {})[0]["class"] == "record"
        w = m.round_window(repo, 2, T0 + 9 * H)
        r["window: an open round runs from its opening tag to now"] = w == (float(T0 + 2 * H), float(T0 + 9 * H), "open")
        r["window: a closed round runs from its opening tag to its own"] = \
            m.round_window(repo, 1, T0 + 9 * H) == (float(T0), float(T0 + 2 * H), "closed")
        r["window: a round with no opening tag is unread"] = m.round_window(repo, 5, T0) is None
        r["window: the open round is one past the newest major tag"] = m.open_round(repo) == 2
        r["gate checks: REQUIRED['push'] counted at the window's two ends"] = \
            m.gate_checks(repo, T0 + H, T0 + 8 * H) == "2 at the window's start, 3 at its end"
        r["gate checks: a commit without gate.py is unread"] = m.gate_checks_at(repo, "HEAD~9999") is None
        r["round_groups: each group carries its roster's round"] = [k for k, _ in m.round_groups(repo, "main")] == [1, 1, 1]

        # a late production merge after round 2's one finder baseline (merge #5), and the plan history
        subprocess.run(["git", "checkout", "-q", "-b", "fix/g-a"], cwd=repo, env=env, check=True)
        commit(T0 + 10 * H, {"custom_components/y.py": "y = 1\n"})
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
        commit(T0 + 11 * H, {}, "Merge pull request #9 from o/fix/g-a", merge_of="fix/g-a")
        rounds = "dev/audit/rounds/round{}/"
        judge = repo / rounds.format(2) / "JUDGE.json"
        commit(T0 + 12 * H, {rounds.format(2) + "LEADS.json": json.dumps([{"baseline_sha": rows[0]["sha"][:12]}]),
                             rounds.format(4) + "X.json": '{"baseline_sha": "deadbeefdead"}', str(judge.relative_to(repo)): "[]"})
        judge.unlink()
        commit(T0 + 13 * H, {}, "the register leaves")
        commit(T0 + 14 * H, {str(judge.relative_to(repo)): "[]"}, "and comes back: the first add is the register")
        commit(T0 + 15 * H, {"dev/programme/rosters/wave-r2-groups.json": json.dumps({"groups": [
            {"group": "R2-A", "kind": "feature", "resume": {"stage": "deferred"}},
            {"group": "R2-B", "kind": "fix", "resume": {"stage": "done"}}, {"note": "no group key"}]})}, "round 2's roster")
        subprocess.run(["git", "checkout", "-q", "-b", "plan1", "v0.0.0"], cwd=repo, env=env, check=True)
        for k, day in enumerate((20, 22, 21)):  # round 1's pages, each half an hour apart inside its closed window
            commit(T0 + (k + 1) * H // 2, {"handoff/round1/state/PLAN.html": f"<p>merge batches, closure 2027-01-{day}T08:00Z.</p>"})
        subprocess.run(["git", "update-ref", "refs/remotes/origin/handoff/audit-r1-plan", "plan1"], cwd=repo, env=env, check=True)
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
        subprocess.run(["git", "checkout", "-q", "-b", "plan"], cwd=repo, env=env, check=True)
        page = "handoff/round2/state/PLAN.html"
        for hr, text in ((20, "merge batches, closure 2027-01-20T08:00:00Z."), (21, "UNAVAILABLE"),
                         (46, "merge batches, closure 2027-01-21T08:00Z.")):  # the last page a day after the first
            commit(T0 + hr * H, {page: f"<p>{text}</p>"})
        for ref, at_ in (("refs/remotes/origin/main", "main"), ("refs/remotes/origin/handoff/audit-r2-plan", "plan")):
            subprocess.run(["git", "update-ref", ref, at_], cwd=repo, env=env, check=True)
        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)

        rows2 = m.merge_rows(repo, T0, [], groups, {})
        d = Path(td) / "sc"
        d.mkdir()
        (d / "groups.json").write_text(json.dumps({"G-A": {"kind": "feature"}, "G-B": {"kind": "fix"}}))
        rnd = lambda n: {"n": n, "repo": repo}
        r["unexamined: production merges no finder baseline contains, by roster group kind"] = chk(
            lambda: m.unexamined_line(d, rnd(2), rows2, T0, T0 + 20 * H) ==
            "unexamined 1/2 = 50% (production merges in the window no finder baseline of round 2 contains; "
            "1 baselines; by kind feature 1)")
        r["unexamined: a baseline that resolves to no commit is unread, never partial"] = chk(
            lambda: m.unexamined_line(d, rnd(4), rows2, T0, T0 + 20 * H) ==
            "unexamined unread (1 finder baselines of round 4 resolve to no commit: deadbeefdead)")
        r["unexamined: a round with no baseline, no round, no merges and no production merge are unread"] = chk(
            lambda: [m.unexamined_line(d, x, y, T0, b).split(" (")[0] for x, y, b in
                     ((rnd(3), rows2, T0 + 20 * H), (None, rows2, T0 + 20 * H), (rnd(2), None, T0 + 20 * H),
                      (rnd(2), rows2, T0 + H))] == ["unexamined unread"] * 4)
        h = m.plan_history(repo, 2, {})
        r["plan history: one forecast per page commit, an UNAVAILABLE page null, the register the first add"] = \
            h["history"] == [[T0 + 20 * H, T0 + 5 * D], [T0 + 21 * H, None], [T0 + 46 * H, T0 + 6 * D]] \
            and h["register"] == T0 + 12 * H
        r["plan history: an incremental scan from the cached tip keeps the cache"] = chk(
            lambda: m.plan_history(repo, 2, {"tip": h["tip"], "history": [[1, 2]]})["history"] == [[1, 2]])
        r["plan history: a round with no state ref keeps its cached history"] = chk(
            lambda: m.plan_history(repo, 3, {"history": [[1, 2]]}) == {"history": [[1, 2]], "register": None})
        producer_cases(m, tests, repo, Path(td), r)
        # the checkout leaves origin/main: a branch drops round 2's baseline and first adds round 3's register
        subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=repo, env=env, check=True)
        (repo / rounds.format(2) / "LEADS.json").unlink()
        commit(T0 + 30 * H, {rounds.format(3) + "JUDGE.json": "[]"}, "a branch the reads must not see")
        side = lambda: m.git(repo, "ls-tree", "--name-only", "HEAD", rounds.format(2)).split() == [rounds.format(2) + "JUDGE.json"] and \
            m.git(repo, "log", "--format=%ct", "HEAD", "--", rounds.format(3) + "JUDGE.json").strip() == str(T0 + 30 * H)
        r["unexamined: the baselines are origin/main's, not the checkout's"] = chk(
            lambda: side() and m.round_baselines(repo, 2) == ([rows[0]["sha"]], []))
        r["plan history: a register first added on a branch is no register"] = chk(
            lambda: side() and m.plan_history(repo, 3, {})["register"] is None)


def producer_cases(m, tests: Path, repo: Path, td: Path, r: dict) -> None:
    """produce over the fixture: groups.json and plans.json read from its output, then main's --round read of them."""
    for p in (tests.parent / "tools/audit/seat", tests.parent / "tools/ci"):
        sys.path.insert(0, str(p))
    d = td / "produced"
    notes = m.produce(d, repo, "o/r", "main", lambda path, params: [])
    r["producer: groups.json carries each roster group's kind, resume.stage and round"] = chk(
        lambda: notes == [] and json.loads((d / "groups.json").read_text()) == {
            "G-A": {"kind": None, "stage": None, "round": 1}, "G-B": {"kind": None, "stage": None, "round": 1},
            "G-PR": {"kind": None, "stage": None, "round": 1},
            "R2-A": {"kind": "feature", "stage": "deferred", "round": 2}, "R2-B": {"kind": "fix", "stage": "done", "round": 2}})
    half = lambda k: T0 + k * H // 2
    r["producer: plans.json caches rounds N-1 and N from their state refs"] = chk(
        lambda: json.loads((d / "plans.json").read_text()) == {
            "1": {"tip": m.git(repo, "rev-parse", "plan1").strip(), "register": T0,
                  "history": [[half(1), T0 + 5 * D], [half(2), T0 + 7 * D], [half(3), T0 + 6 * D]]},
            "2": {"tip": m.git(repo, "rev-parse", "plan").strip(), "register": T0 + 12 * H,
                  "history": [[T0 + 20 * H, T0 + 5 * D], [T0 + 21 * H, None], [T0 + 46 * H, T0 + 6 * D]]}})
    obj = repo / "dev/audit/config/objective.json"
    obj.parent.mkdir(parents=True, exist_ok=True)

    def report(value) -> list[str]:
        obj.write_text(json.dumps({"thresholds": {"closure_slip_ceiling": {"value": value, "proposed": 0.2}}}))
        out, clock = io.StringIO(), m.time
        m.time = type("Clock", (), {"time": staticmethod(lambda: T0 + 40 * D)})  # round 2 stays open to T0 + 40 days
        try:
            with contextlib.redirect_stdout(out):
                rc = m.main(["report", "--round", "2", "--dir", str(d), "--repo", str(repo)])
        finally:
            m.time = clock
        return [ln for ln in out.getvalue().splitlines() if rc == 0 and ln.startswith("closure_slip ")]
    slip = ("closure_slip 0.92 days per day (1.00 days later over 1.08 days of plan history after the register, "
            "2 daily samples of 3 pages; net +1.00 days; 1 pages without a forecast; {}; round start to closure "
            "5.9 days (forecast); 1 groups deferred out)")
    r["report --round: a set ceiling is read from objective.json's value"] = chk(
        lambda: report(0.5) == [slip.format("over the ceiling 0.5")])
    r["report --round: a null ceiling is undecided"] = chk(lambda: report(None) == [slip.format("ceiling unset, undecided")])


def cases(m, tests: Path) -> dict[str, bool]:
    r: dict[str, bool] = {}
    with tempfile.TemporaryDirectory() as td:
        none = {"n": 1, "repo": Path(td), "start": T0, "end": T0 + 100 * H, "state": "open", "ceiling": None}
        empty = m.window_lines(Path(td) / "none", T0, T0 + 100 * H, "unread", none)
        r["null: an empty input directory prints every read unread"] = len(empty) == 8 and all(" unread (" in x for x in empty)
        rows = [(10, "production", "A", 0), (20, "production", "A", 0), (30, "production", "B", 20), (40, "production", "C", 10),
                (50, "production", "", None), (60, "production", "D", 70), (15, "machinery", "M", 5), (200, "production", "Z", 0)]
        d = state(Path(td), merges=rows)
        lt = m.lead_lines(m.load_merges(d), T0, T0 + 100 * H)
        r["lead_time: the latest merge per group, p50 and p90 by nearest rank"] = \
            lt[0].startswith("lead_time production p50 20.0 h p90 30.0 h (n=3 groups;")
        r["lead_time: a merge naming no group and a group entered after its merge are beside"] = \
            "1 production merges name no roster group; 1 groups entered after their merge" in lt[0]
        r["lead_time: each class its own line; a class with none merged is unread"] = \
            lt[1].startswith("lead_time machinery p50 10.0 h") and lt[2].startswith("lead_time record unread (")
        r["merges: the window's merges by class"] = \
            m.window_lines(d, T0, T0 + 100 * H, "x")[0] == "merges 7: production 6, machinery 1, record 0"
        r["rank: nearest rank"] = m.rank([1, 2, 3, 4], 0.5) == 2 and m.rank([1, 2, 3, 4], 0.9) == 4 and m.rank([5], 0.9) == 5

    with tempfile.TemporaryDirectory() as td:
        runs = [{"id": i, "t": at(m, h), "c": c} for i, (h, c) in enumerate(
            [(1, "success"), (2, "failure"), (3, "failure"), (5, "success"), (6, "cancelled"), (7, "failure"), (9, "success"),
             (11, "failure")])] + [{"id": 8, "t": at(m, 8), "c": "failure"}]
        jobs = {0: gate_doc("success"), 1: gate_doc("failure"), 2: gate_doc("failure", "success", attempt=2),
                3: gate_doc("success"), 5: gate_doc("failure"), 6: gate_doc("success"), 7: gate_doc("failure"),
                8: gate_doc("failure")}
        d = state(Path(td), runs=runs, jobs=jobs)
        g, rs = m.green_lines(m.read_json(d / "runs.json"), m.gate_conclusions(d), T0, T0 + 12 * H, "2 at x")
        r["product_green: concluded runs whose gate (latest attempt) succeeded; cancelled beside"] = \
            g == "product_green 4/8 = 50% (concluded main CI push runs; cancelled 1; gate checks 2 at x)"
        r["product_green: a run failing outside its gate counts green (null)"] = \
            m.green_lines([{"id": 1, "t": at(m, 1), "c": "failure"}], {1: "success"}, T0, T0 + 2 * H, "x")[0].startswith(
                "product_green 1/1 = 100%")
        r["restore: median over red spells closed in the window, an open spell beside"] = \
            rs == f"restore median 1.0 h over 2 red spells closed in the window (longest 2.0 h; open red spell since {m.iso(T0 + 11 * H)})"
        r["restore: a spell closed before the window is not counted"] = \
            m.green_lines(runs, m.gate_conclusions(d), T0 + 6 * H, T0 + 10 * H, "x")[1].startswith("restore median 2.0 h over 1 red")
        r["restore: no red spell is a read, not unread"] = \
            m.green_lines(runs[:1], {0: "success"}, T0, T0 + 2 * H, "x")[1] == "restore no red spell closed in the window (1 concluded runs read)"
        del jobs[3]
        (d / "jobs" / "jobs_3.json").unlink()
        g, rs = m.green_lines(runs, m.gate_conclusions(d), T0, T0 + 12 * H, "x")
        r["product_green: a concluded run with no job listing makes it unread (a partial ledger)"] = \
            g.startswith("product_green unread (1 of 8 concluded runs have no job listing") and rs.startswith("restore unread (")
        r["product_green: a cancelled run with no listing does not blind it"] = \
            m.green_lines(runs[:4], {0: "success", 1: "failure", 2: "success", 3: "success"}, T0, T0 + 12 * H, "x")[0].startswith(
                "product_green 3/4")

    with tempfile.TemporaryDirectory() as td:
        job = lambda a, b: {"name": "j", "conclusion": "success", "started_at": at(m, a), "completed_at": at(m, b), "run_attempt": 1}
        ci = [{"id": 1, "t": at(m, 1), "c": "success", "attempt": 1}, {"id": 2, "t": at(m, 2), "c": "failure", "attempt": 2},
              {"id": 3, "t": at(m, 50), "c": "success", "attempt": 1}]
        jobs = {1: {"attempt": 1, "jobs": [job(1, 1.5), job(1, 1), {"name": "s", "started_at": None, "completed_at": None}]},
                2: {"attempt": 2, "jobs": [job(2, 2.25), job(3, 3.25)]}}
        d = state(Path(td), merges=[(1, "machinery", "", None), (3, "production", "", None)], ci=ci, jobs=jobs,
                  tokens=[(at(m, 1), "orchestrator", 100), (at(m, 2), "local", 50), (at(m, 3), "cloud", 50), (at(m, 60), "cloud", 9)])
        merges = m.load_merges(d)
        r["runner_s: job seconds of the window's CI runs over its merges"] = \
            m.runner_line(d, merges, T0, T0 + 10 * H) == "runner_s 1800 per merge (3600 job seconds of 2 CI runs over 2 merges)"
        jobs[2]["attempt"] = 1
        (d / "jobs" / "jobs_2.json").write_text(json.dumps(jobs[2]))
        r["runner_s: a run whose listing is of an older attempt makes it unread"] = \
            m.runner_line(d, merges, T0, T0 + 10 * H).startswith("runner_s unread (1 of 2 CI runs")
        r["tokens: the ledger over the window, over production merges"] = \
            m.token_line(d, merges, T0, T0 + 10 * H) == "tokens 200 per production merge (window total 200; 1 production merges)"
        r["tokens: a seat class with no row in the window makes it unread"] = \
            m.token_line(d, merges, T0 + 2.5 * H, T0 + 10 * H) == \
            "tokens unread (seat classes with no ledger row: orchestrator, local; production merges 1)"
        r["weeks: 7-day spans from the start, the last short"] = \
            m.weeks(T0, T0 + 10 * 86400) == [(T0, T0 + 7 * 86400), (T0 + 7 * 86400, T0 + 10 * 86400)]
        r["group_of: resume.pr, then the branch, then the branch less a part suffix"] = \
            (m.group_of(9, "fix/x", {9: "P"}, {"X"}), m.group_of(1, "handoff/x-p3", {}, {"X"}),
             m.group_of(1, "fix/x-pr", {}, {"X"}), m.group_of(1, "hotfix/x", {}, {"X"})) == ("P", "X", "", "X")

        calls = []

        def fake(path, params):
            calls.append(path)
            if path.endswith("/runs"):
                return [{"id": 11, "created_at": at(m, 1), "conclusion": "success", "run_attempt": 2, "event": "push", "head_branch": "main"},
                        {"id": 12, "created_at": at(m, 2), "conclusion": "failure", "run_attempt": 1, "event": "pull_request", "head_branch": "x"}]
            return [{"name": "gate", "conclusion": "success", "run_attempt": 2, "started_at": None, "completed_at": None, "id": 5}]
        out = Path(td) / "fetched"
        m.fetch_runs(out, "o/r", T0, fake)
        r["producer: main push runs in runs.json, every run in ci_runs.json, each listing fetched"] = \
            [x["id"] for x in m.read_json(out / "runs.json")] == [11] and len(m.read_json(out / "ci_runs.json")) == 2 \
            and m.read_json(out / "jobs" / "jobs_11.json")["attempt"] == 2 and len(calls) == 3
        calls.clear()
        m.fetch_runs(out, "o/r", T0, fake)
        r["producer: a listing cached at the run's latest attempt is not fetched again"] = len(calls) == 1
    slip_cases(m, r)
    git_cases(m, tests, r)
    return r


def slip_cases(m, r: dict) -> None:
    reg = T0 + 10 * H
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        hist = [[T0 + 5 * H, T0 + 50 * D], [reg, T0 + 10 * D], [reg + D, T0 + 11 * D], [reg + 2 * D, None],
                [reg + 3 * D, T0 + 10.5 * D], [reg + 4 * D, T0 + 12.5 * D]]
        (d / "plans.json").write_text(json.dumps({"2": {"register": reg, "history": hist}, "3": {"register": None, "history": hist}}))
        (d / "groups.json").write_text(json.dumps({"A": {"round": 2, "stage": "deferred"}, "B": {"round": 1, "stage": "deferred"},
                                                   "C": {"round": 2, "stage": "done"}}))
        rnd = lambda n=2, **k: dict({"n": n, "start": T0, "end": T0 + 30 * D, "state": "open", "ceiling": 0.5}, **k)
        r["closure_slip: later moves only, over the plan-history days after the register"] = chk(
            lambda: m.slip_line(d, rnd(), T0, T0 + 30 * D) ==
            "closure_slip 0.75 days per day (3.00 days later over 4.00 days of plan history after the register, "
            "4 daily samples of 5 pages; net +2.50 days; 1 pages without a forecast; over the ceiling 0.5; round start to closure 12.5 days "
            "(forecast); 1 groups deferred out)")
        r["closure_slip: a closed round closes at its tag; a null ceiling is undecided"] = chk(
            lambda: "ceiling unset, undecided; round start to closure 20.0 days (closed)" in
            m.slip_line(d, rnd(state="closed", end=T0 + 20 * D, ceiling=None), T0, T0 + 30 * D))
        r["closure_slip: the window cuts the history"] = chk(
            lambda: m.slip_line(d, rnd(), T0, reg + 3.5 * D).startswith("closure_slip 0.33 days per day (1.00 days later over 3.00"))
        busy = [[reg, T0 + 10 * D], [reg + D / 4, T0 + 12 * D], [reg + D / 2, T0 + 10 * D], [reg + D, T0 + 11 * D],
                [reg + 2 * D, T0 + 11 * D]]
        (d / "plans.json").write_text(json.dumps({"2": {"register": reg, "history": busy}}))
        r["closure_slip: read at a fixed daily cadence, the last page of each day from the register"] = chk(
            lambda: m.slip_line(d, rnd(), T0, T0 + 30 * D).startswith(
                "closure_slip 0.67 days per day (1.00 days later over 1.50 days of plan history after the register, "
                "3 daily samples of 5 pages; net +1.00 days; 0 pages without a forecast;"))
        first = [[reg, T0 + 10 * D], [reg + D / 2, T0 + 12 * D], [reg + D + 1, T0 + 13 * D]]
        (d / "plans.json").write_text(json.dumps({"2": {"register": reg, "history": first}}))
        r["closure_slip: the net move is over the daily samples, the first day's last page to the last sample"] = chk(
            lambda: "2 daily samples of 3 pages; net +1.00 days;" in m.slip_line(d, rnd(), T0, T0 + 30 * D))
        (d / "plans.json").write_text(json.dumps({"2": {"register": reg, "history": hist}, "3": {"register": None, "history": hist}}))
        r["closure_slip: one page, no register, no history and no round are unread"] = chk(
            lambda: [m.slip_line(d, x, T0, b).split(" (")[0] for x, b in
                     ((rnd(), reg + 0.5 * D), (rnd(3), T0 + 30 * D), (rnd(5), T0 + 30 * D), (None, T0 + 30 * D))]
            == ["closure_slip unread"] * 4)


#: (needle in round_metrics.py, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "rank index": ("math.ceil(p * len(s)) - 1", "math.floor(p * len(s))", "rank: nearest rank"),
    "lead latest per group": ('key=lambda r: r["ct"])', 'key=lambda r: -r["ct"])', "lead_time: the latest merge"),
    "lead unknowable kept": ("hrs = [h for h in hrs if h >= 0]", "hrs = hrs", "lead_time: the latest merge"),
    "lead class filter": ('if r["class"] == cls and a <= r["ct"] < b', 'if a <= r["ct"] < b', "lead_time: each class"),
    "green concluded": ('if r["c"] in ("success", "failure")', 'if r["c"] != "x"', "product_green: concluded runs"),
    "green gate": ('ok = sum(gate.get(r["id"]) == "success" for r in w)', 'ok = sum(r["c"] == "success" for r in w)',
                   "product_green: a run failing outside"),
    "green partial ledger": ("    if any(a <= epoch(r[\"t\"]) for r in blind):", "    if False:",
                             "product_green: a concluded run with no job listing"),
    "gate latest attempt": ('key=lambda j: j.get("run_attempt") or 0)', 'key=lambda j: -(j.get("run_attempt") or 0))',
                            "product_green: concluded runs"),
    "restore window": ("            if epoch(r[\"t\"]) >= a:\n", "            if True:\n", "restore: a spell closed before"),
    "restore start kept": ('if gate[r["id"]] != "success" and start is None:', 'if gate[r["id"]] != "success":',
                           "restore: median"),
    "runner attempt": ('doc.get("attempt") != r["attempt"]', "False", "runner_s: a run whose listing is of an older"),
    "runner window": ('w = [r for r in runs if a <= epoch(r["t"]) < b]', "w = list(runs)", "runner_s: job seconds"),
    "tokens class": ("missing or not prod", "not prod", "tokens: a seat class"),
    "tokens production": ('r["class"] == "production" and a <= r["ct"] < b for r', 'a <= r["ct"] < b for r', "tokens: the ledger"),
    "roster first add": ("and m[1] not in entered", "", "roster clock: a group's entry"),
    "roster incremental": ('span = f"{old}..{tip}" if old and', 'span = tip if old and', "roster clock: an incremental"),
    "group part suffix": ('re.sub(r"-P\\d+$", "", k)', "k", "group_of:"),
    "group by pr": ("    if pr in by_pr:\n        return by_pr[pr]\n", "", "merges: classes"),
    "merge cached class": ("cached.get(sha) or ", "", "merges: a cached class"),
    "producer main filter": ('r["event"] == "push" and r["head_branch"] == "main"', "True", "producer: main push runs"),
    "producer cache": ('.get("attempt") != r["attempt"]]', ".get(\"attempt\") is not None or True]", "producer: a listing cached"),
    "window open": ('(b if b is not None else now)', "now", "window: a closed round"),
    "week span": ("min(t + WEEK_S, b)", "t + WEEK_S", "weeks:"),
    "slip later only": ("max(0.0, q[1] - p[1])", "(q[1] - p[1])", "closure_slip: later moves only"),
    "slip register": ('h[0] >= doc["register"] and ', "", "closure_slip: later moves only"),
    "slip window": (' and a <= h[0] < b)', ")", "closure_slip: the window cuts"),
    "slip blank page": ("hist = [h for h in every if h[1] is not None]", "hist = every", "closure_slip: later moves only"),
    "slip two pages": ("len(daily) < 2", "len(daily) < 1", "closure_slip: one page"),
    "slip daily cadence": ('(h[0] - doc["register"]) // SLIP_SAMPLE_S', "h[0]", "closure_slip: read at a fixed daily cadence"),
    "slip net daily": ("{(daily[-1][1] - daily[0][1]) / DAY_S:+.2f}", "{(hist[-1][1] - hist[0][1]) / DAY_S:+.2f}",
                       "closure_slip: the net move is over the daily samples"),
    "ceiling value key": ('.get("closure_slip_ceiling") or {}).get("value")', '.get("closure_slip_ceiling") or {})',
                          "report --round: a null ceiling"),
    "produce prior round": ("for k in (n - 1, n):", "for k in (n,):", "producer: plans.json"),
    "groups json round": ('"round": k} for k, g in pairs', '"round": 0} for k, g in pairs', "producer: groups.json"),
    "groups json stage": ('"stage": (g.get("resume") or {}).get("stage")', '"stage": None', "producer: groups.json"),
    "groups json kind": ('{"kind": g.get("kind"), "stage"', '{"kind": None, "stage"', "producer: groups.json"),
    "groups json write": ('    write(d / "groups.json", json.dumps({g["group"]',
                          '    (lambda *a: None)(d / "groups.json", json.dumps({g["group"]', "producer: groups.json"),
    "plans json write": ('    write(d / "plans.json", json.dumps(plans, sort_keys=True))\n', "", "producer: plans.json"),
    "baselines ref": ('BASELINE.pattern, "origin/main"', 'BASELINE.pattern, "HEAD"', "unexamined: the baselines are origin/main's"),
    "register ref": ('"--format=%ct", "origin/main", "--"', '"--format=%ct", "--all", "--"',
                     "plan history: a register first added on a branch"),
    "slip ceiling": ("slip <= cap", "slip >= cap", "closure_slip: later moves only"),
    "slip closed round": ('if rnd["state"] == "closed"', "if False", "closure_slip: a closed round"),
    "slip deferred round": ("g.get('round') == n and ", "", "closure_slip: later moves only"),
    "unexamined ancestry": ('if r["sha"] not in seen]', "]", "unexamined: production merges"),
    "unexamined production": ('prod = [r for r in merges if r["class"] == "production" and ', "prod = [r for r in merges if ",
                              "unexamined: production merges"),
    "unexamined partial": ("    if bad:\n", "    if False:\n", "unexamined: a baseline that resolves"),
    "unexamined none": ("    if not shas:\n", "    if False:\n", "unexamined: a round with no baseline"),
    "unexamined kind": ('(groups.get(r["group"]) or {}).get("kind")', "None", "unexamined: production merges"),
    "plan register first add": ("int(reg[-1])", "int(reg[0])", "plan history: one forecast"),
    "plan incremental": ('f"{old}..{tip}" if inc else tip', "tip", "plan history: an incremental"),
    "plan cache on a gone ref": ("    if not tip:\n        return out\n", "", "plan history: a round with no state ref"),
}


def run(path: Path, mutants: bool, tests: Path) -> int:
    bad: list[str] = []
    for name, ok in cases(load(path), tests).items():
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            bad.append(name)
    if mutants:
        src = path.read_text()
        here = Path(__file__).resolve()
        for name, (old, new, case) in MUTANTS.items():
            if src.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {src.count(old)} times")
                bad.append(name)
                continue
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / path.name).write_text(src.replace(old, new))
                (Path(td) / here.name).write_text(here.read_text())
                p = subprocess.run([sys.executable, "-I", str(Path(td) / here.name), str(tests), str(path.parents[1])],
                                   capture_output=True, text=True, timeout=300)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("round_metrics self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":  # a mutant copy runs its cases only: argv is the tests dir and tools/audit
    sys.path.insert(0, sys.argv[2])
    sys.exit(run(Path(__file__).with_name("round_metrics.py"), False, Path(sys.argv[1])))
