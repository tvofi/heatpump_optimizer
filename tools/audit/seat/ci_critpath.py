#!/usr/bin/env python3
"""One workflow run's critical path, and what a changed job graph would end at.

    python3 tools/audit/seat/ci_critpath.py --self-test
    python3 tools/audit/seat/ci_critpath.py --repo OWNER/NAME --run ID \\
        [--drop-edge NEED:JOB ...] [--delete-job JOB ...] [--charge JOB=SECONDS ...]
    python3 tools/audit/seat/ci_critpath.py --repo OWNER/NAME --workflow FILE.yml \\
        --last N [--event E] [--branch B] [counterfactual flags as above]

R10-FLOW-TOOLKIT-MEASURE, generalising the CI design archive's phase-2
method (tag archive/probe/design-ci-rev4, measure/p2/critpath.py and
c1_counterfactual.py), which was written for one edge of one workflow.

THE RULE. A run's jobs are the API's jobs that ran: completed, not skipped,
with both timestamps; a skipped job leaves the graph, and an edge to it with
it. A job's needs are its `needs:` in the run's own workflow file, read at
the run's head SHA (never the tree's), and an API name maps to a key by its
`name:` or, for a matrix instance `key (a, b)`, by the key. For each job:

    ready    = the latest end of its needs, or the run's start without any
    queue    = its start - ready        duration = its end - its start
    wall     = the latest job end - the run's start

The critical path walks back from the job that ended last through the need
that ended last. THE COUNTERFACTUAL holds every queue and duration fixed
and replays the graph in topological order with the named edges dropped,
the named jobs deleted (their dependents lose them as needs) and each
`--charge` added to that job's duration; it prints the new wall and the
gain (old - new; negative is slower). This is the archive's V1 "drop C1":
`--drop-edge coverage:closures --delete-job composed-proof --charge
closures=239.1`. A charge is the bare cost the change adds, stated by the
caller with its source; this tool never infers one.

OVER RUNS (`--last N`): the workflow's last N completed runs, newest first,
neither cancelled nor skipped, filtered by `--event`/`--branch`; median and
p90 (nearest rank: the ceil(0.9 n)-th smallest) of wall, counterfactual wall
and gain. API reads are paged (100 a page), each run's jobs and each head's
needs are cached under `--cache` (default the git common dir's
`ci-critpath/`), so a re-run reads nothing but `--last`'s run list (the
newest runs move), and a run needing more than
`--max-reads` (default 200) reads refuses rather than run unbounded.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tools/audit/seat/fixtures/ci_critpath"
PAGE = 100
MATRIX_RE = re.compile(r"^(.+?) \(.*\)$")
JOB_RE = re.compile(r"^  ([A-Za-z_][\w-]*):\s*(?:#.*)?$")
FIELD_RE = re.compile(r"^    (name|needs):\s*(.*?)\s*(?:#.*)?$")
ITEM_RE = re.compile(r"^      -\s*([\w-]+)")


def ts(s: str | None) -> float | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


class Api:
    """`gh api` reads, paged, cached under `cache`, bounded by `max_reads`."""

    def __init__(self, repo: str, cache: Path, max_reads: int, get=None):
        self.repo, self.cache, self.max_reads, self.reads = repo, cache, max_reads, 0
        self._get = get or self._gh
        cache.mkdir(parents=True, exist_ok=True)

    def _gh(self, path: str, raw: bool = False) -> str:
        argv = ["gh", "api", path] + (["-H", "Accept: application/vnd.github.raw"] if raw else [])
        p = subprocess.run(argv, capture_output=True, text=True)
        if p.returncode:
            raise SystemExit(f"ci_critpath: gh api {path} failed: {p.stderr.strip()[:300]}")
        return p.stdout

    def get(self, path: str, raw: bool = False) -> str:
        if self.reads >= self.max_reads:
            raise SystemExit(f"ci_critpath: refused: more than --max-reads {self.max_reads} API reads")
        self.reads += 1
        return self._get(f"repos/{self.repo}/{path}", raw)

    def cached(self, name: str, fill):
        f = self.cache / name
        if f.exists():
            return json.loads(f.read_text())
        val = fill()
        f.write_text(json.dumps(val))
        return val

    def run(self, rid: int) -> dict:
        def fill():
            r = json.loads(self.get(f"actions/runs/{rid}"))
            if r.get("conclusion") is None:
                raise SystemExit(f"ci_critpath: refused: run {rid} has not concluded, so its jobs would cache unfinished")
            return r
        return self.cached(f"run_{rid}.json", fill)

    def jobs(self, rid: int) -> list[dict]:
        def fill():
            out, page = [], 1
            while True:
                d = json.loads(self.get(f"actions/runs/{rid}/jobs?per_page={PAGE}&page={page}"))
                out += d["jobs"]
                if len(d["jobs"]) < PAGE or len(out) >= d.get("total_count", 0):
                    return out
                page += 1
        return self.cached(f"jobs_{rid}.json", fill)

    def needs(self, sha: str, path: str) -> dict:
        def fill():
            p = subprocess.run(["git", "-C", str(ROOT), "show", f"{sha}:{path}"], capture_output=True, text=True)
            return workflow_needs(p.stdout if p.returncode == 0
                                  else self.get(f"contents/{path}?ref={sha}", raw=True))
        return self.cached(f"needs_{sha}_{path.replace('/', '_')}.json", fill)

    def runs(self, workflow: str, last: int, event: str | None, branch: str | None) -> list[dict]:
        q = "".join(f"&{k}={v}" for k, v in (("event", event), ("branch", branch)) if v)
        out, page = [], 1
        while len(out) < last:
            d = json.loads(self.get(f"actions/workflows/{workflow}/runs?status=completed&per_page={PAGE}&page={page}{q}"))
            out += [r for r in d["workflow_runs"] if r["conclusion"] not in ("cancelled", "skipped")]
            if len(d["workflow_runs"]) < PAGE:
                break
            page += 1
        for r in out[:last]:
            (self.cache / f"run_{r['id']}.json").write_text(json.dumps(r))
        return out[:last]


def workflow_needs(text: str) -> dict:
    """{key: {"name": its name: or None, "needs": [keys]}} from a workflow file's `jobs:` block.

    Read by line at the layout every workflow here uses (a job key at two
    spaces, its `name:`/`needs:` at four, a block list's items at six), so the
    seat's system Python needs no YAML package; a flow mapping or an anchor is
    not read. A `name:` holding an expression keeps the text before its
    ` (${{` as the name a matrix instance's API name starts with.
    """
    out, job, field, inside = {}, None, None, False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            inside, job = line.rstrip() == "jobs:", None
            continue
        m = JOB_RE.match(line) if inside else None
        if m:
            job, field = m[1], None
            out[job] = dict(name=None, needs=[])
            continue
        f = FIELD_RE.match(line) if job else None
        if f:
            field, val = f[1], f[2].strip("'\"")
            if field == "name":
                out[job]["name"] = val.split(" (${{")[0] if val.endswith(")") and " (${{" in val else (
                    None if "${{" in val else val)
            elif val.startswith("["):
                out[job]["needs"] = [x.strip().strip("'\"") for x in val.strip("[]").split(",") if x.strip()]
            elif val:
                out[job]["needs"] = [val]
            continue
        if not line.startswith("     "):
            field = None
        i = ITEM_RE.match(line) if field == "needs" else None
        if i:
            out[job]["needs"].append(i[1])
    return out


def graph(jobs: list[dict], needs: dict) -> tuple[dict, list[str]]:
    """{api name: job dict with s, e, needs (api names)} for the jobs that ran, and the unmapped names."""
    by_name = {v["name"]: k for k, v in needs.items() if v["name"]}
    ran = {j["name"]: j for j in jobs if j.get("conclusion") not in (None, "skipped")
           and j.get("started_at") and j.get("completed_at")}
    key_of, unmapped = {}, []
    for n in ran:
        m = MATRIX_RE.match(n)
        k = by_name.get(n) or (n if n in needs else None) or (m and (by_name.get(m[1]) or (m[1] if m[1] in needs else None)))
        if k is None:
            unmapped.append(n)
        key_of[n] = k
    inst = {}
    for n, k in key_of.items():
        inst.setdefault(k, []).append(n)
    g = {}
    for n, j in ran.items():
        k = key_of[n]
        dep = [x for nk in (needs.get(k, {}).get("needs", []) if k else []) for x in inst.get(nk, [])]
        g[n] = dict(s=ts(j["started_at"]), e=ts(j["completed_at"]), needs=dep, steps=j.get("steps") or [])
    return g, unmapped


def replay(g: dict, start: float, drop: set = frozenset(), delete: set = frozenset(),
           charge: dict | None = None) -> dict:
    """{job: new end} holding each job's queue and duration, with edges dropped, jobs deleted, charges added."""
    charge = charge or {}
    new: dict = {}
    for n in topo(g):
        if n in delete:
            continue
        q = g[n]["s"] - max((g[x]["e"] for x in g[n]["needs"]), default=start)
        kept = [x for x in g[n]["needs"] if x not in delete and (x, n) not in drop]
        s = max((new[x] for x in kept), default=start) + q
        new[n] = s + (g[n]["e"] - g[n]["s"]) + charge.get(n, 0.0)
    return new


def topo(g: dict) -> list[str]:
    seen, out = set(), []
    def visit(n, path=()):
        if n in path:
            raise SystemExit(f"ci_critpath: refused: a needs cycle through {n}")
        if n not in seen:
            for x in g[n]["needs"]:
                visit(x, path + (n,))
            seen.add(n)
            out.append(n)
    for n in sorted(g):
        visit(n)
    return out


def critical_path(g: dict, ends: dict) -> list[str]:
    n = max(ends, key=lambda x: ends[x])
    path = [n]
    while True:
        live = [x for x in g[n]["needs"] if x in ends]
        if not live:
            return path[::-1]
        n = max(live, key=lambda x: ends[x])
        path.append(n)


def analyse(run: dict, jobs: list[dict], needs: dict, cf: dict) -> dict:
    g, unmapped = graph(jobs, needs)
    start = ts(run["run_started_at"])
    ends = {n: j["e"] for n, j in g.items()}
    for (a, b) in cf["drop"]:
        if a in g and b in g and a not in g[b]["needs"]:
            raise SystemExit(f"ci_critpath: refused: {b} does not need {a} in run {run['id']}")
    new = replay(g, start, cf["drop"], cf["delete"], cf["charge"]) if any(cf.values()) else None
    wall = max(ends.values()) - start
    return dict(id=run["id"], g=g, start=start, unmapped=unmapped, wall=wall,
                path=critical_path(g, ends), cf=None if new is None else max(new.values()) - start,
                cf_path=None if new is None else critical_path({n: g[n] for n in new}, new))


def p90(xs: list[float]) -> float:
    return sorted(xs)[math.ceil(0.9 * len(xs)) - 1]


def counterfactual(a) -> dict:
    drop = set()
    for e in a.drop_edge:
        need, _, job = e.partition(":")
        drop.add((need, job))
    charge = {}
    for c in a.charge:
        job, _, sec = c.rpartition("=")
        charge[job] = float(sec)
    return dict(drop=drop, delete=set(a.delete_job), charge=charge)


def report(r: dict) -> None:
    g, st = r["g"], r["start"]
    print(f"run {r['id']}: wall {r['wall']:.0f} s ({r['wall'] / 60:.1f} min), {len(g)} jobs ran")
    for n in r["unmapped"]:
        print(f"  unmapped: {n} (no key or name in the workflow file; read with no needs)")
    print("  critical path (queue / duration / longest step):")
    for n in r["path"]:
        j = g[n]
        ready = max((g[x]["e"] for x in j["needs"]), default=st)
        steps = [(ts(s["completed_at"]) - ts(s["started_at"]), s["name"]) for s in j["steps"]
                 if s.get("started_at") and s.get("completed_at")]
        top = max(steps, default=(0, "-"))
        print(f"    {n:28} q {j['s'] - ready:6.0f}  d {j['e'] - j['s']:6.0f}  ends +{j['e'] - st:6.0f}  {top[1][:50]} ({top[0]:.0f} s)")
    if r["cf"] is not None:
        print(f"  counterfactual: wall {r['cf']:.0f} s ({r['cf'] / 60:.1f} min), gain {r['wall'] - r['cf']:.0f} s; "
              f"path {' > '.join(r['cf_path'])}")


def default_cache() -> Path:
    p = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True)
    return Path(p.stdout.strip()) / "ci-critpath"


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", metavar="OWNER/NAME")
    ap.add_argument("--run", type=int, action="append", default=[])
    ap.add_argument("--workflow", metavar="FILE.yml")
    ap.add_argument("--last", type=int, default=0)
    ap.add_argument("--event")
    ap.add_argument("--branch")
    ap.add_argument("--drop-edge", action="append", default=[], metavar="NEED:JOB")
    ap.add_argument("--delete-job", action="append", default=[], metavar="JOB")
    ap.add_argument("--charge", action="append", default=[], metavar="JOB=SECONDS")
    ap.add_argument("--cache", type=Path)
    ap.add_argument("--max-reads", type=int, default=200)
    ap.add_argument("--self-test", action="store_true")
    return ap


def main(argv: list[str], get=None) -> int:
    ap = parser()
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.repo or not (a.run or (a.workflow and a.last > 0)):
        ap.error("--repo and either --run ID or --workflow FILE --last N")
    api = Api(a.repo, a.cache or default_cache(), a.max_reads, get)
    cf = counterfactual(a)
    runs = [api.run(i) for i in a.run] + (api.runs(a.workflow, a.last, a.event, a.branch) if a.workflow else [])
    rows = []
    for run in runs:
        r = analyse(run, api.jobs(run["id"]), api.needs(run["head_sha"], run["path"]), cf)
        report(r)
        rows.append(r)
    if len(rows) > 1:
        w = [r["wall"] for r in rows]
        print(f"runs {len(rows)}: wall median {statistics.median(w):.0f} s p90 {p90(w):.0f} s")
        if rows[0]["cf"] is not None:
            c = [r["cf"] for r in rows]
            gain = [r["wall"] - r["cf"] for r in rows]
            print(f"  counterfactual wall median {statistics.median(c):.0f} s p90 {p90(c):.0f} s; "
                  f"gain median {statistics.median(gain):.0f} s p90 {p90(gain):.0f} s, runs slower {sum(x < 0 for x in gain)}")
    print(f"API reads: {api.reads} (max {a.max_reads})")
    return 0


def self_test() -> int:
    import contextlib
    import io
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"{'ok' if cond else 'FAIL'}: {name}")

    fx = {f.name: json.loads(f.read_text()) for f in FIXTURE.glob("*.json")}
    calls = []

    def get(path: str, raw: bool = False) -> str:
        calls.append(path)
        page = int((re.search(r"[?&]page=(\d+)", path) or [0, 1])[1])
        if "/workflows/" in path:
            fill = [fx[f"run_{i}.json"] for i in (39625218966, 39619839750)]
            fill += [dict(id=1, conclusion="cancelled")] * (PAGE - len(fill))
            return json.dumps(dict(workflow_runs=fill if page == 1 else []))
        rid = re.search(r"runs/(\d+)", path)
        if "/jobs?" in path:
            js = fx[f"jobs_{rid[1]}.json"]
            return json.dumps(dict(total_count=len(js), jobs=js[(page - 1) * PAGE:page * PAGE]))
        if rid:
            return json.dumps(fx[f"run_{rid[1]}.json"])
        return "jobs:\n  a:\n    runs-on: x\n  b:\n    needs: [a]\n"

    def run(*argv: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--repo", "o/r", "--cache", str(cache), *argv], get)
        return buf.getvalue()

    W1 = ("--drop-edge", "coverage:closures", "--delete-job", "composed-proof", "--charge", "closures=239.1")
    with tempfile.TemporaryDirectory() as d:
        cache = Path(d)
        # The heads' needs are recorded beside the runs: a CI checkout need not hold either head.
        for name, val in fx.items():
            if name.startswith("needs_"):
                (cache / name).write_text(json.dumps(val))
        out = run("--run", "39625218966")
        check("run 39625218966 walls 48.6 min (the study's figure)", "wall 2915 s (48.6 min)" in out)
        path = re.findall(r"^    (\S[^\n]*?)\s+q ", out, re.M)
        check("its critical path is closure-scope > coverage > closures > composed-proof",
              path == ["closure-scope", "coverage", "closures", "composed-proof"])
        check("the path names each job's longest step", "Re-record the closures (1172 s)" in out)
        n = len(calls)
        run("--run", "39625218966")
        check("a re-run reads nothing: the run, its jobs and its needs are cached", len(calls) == n)
        out = run("--run", "39625218966", *W1)
        cf = float(re.search(r"counterfactual: wall (\d+) s", out)[1]) / 60
        check(f"W1 on 39625218966 ends inside the study's 27-30 min ({cf:.1f})", 27 <= cf <= 30)
        out = run("--run", "39619839750", *W1)
        base = float(re.search(r"wall (\d+) s", out)[1]) / 60
        cf = float(re.search(r"counterfactual: wall (\d+) s", out)[1]) / 60
        check(f"run 39619839750 walls 47.8 min ({base:.1f}) and W1 about 41 ({cf:.1f})",
              round(base, 1) == 47.8 and 40 <= cf <= 42)
        # Perturbations, each the method's own null control.
        out = run("--run", "39625218966", "--charge", "typing=60")
        check("a charge off the critical path moves nothing (typing +60 s)", "gain 0 s" in out)
        out = run("--run", "39625218966", "--charge", "closures=60")
        check("a charge on the critical path moves the wall by exactly the charge", "gain -60 s" in out)
        out = run("--run", "39625218966", "--drop-edge", "coverage:closures")
        check("dropping only the edge keeps composed-proof, which still needs coverage and closures",
              "path closure-scope > coverage > composed-proof" in out)
        try:
            run("--run", "39625218966", "--drop-edge", "typing:closures")
            check("dropping an edge the workflow does not have refuses", False)
        except SystemExit as e:
            check("dropping an edge the workflow does not have refuses", "does not need typing" in str(e))
        out = run("--run", "39625218966", "--delete-job", "composed-proof")
        check("deleting the last job ends the run at its need's end (closures, +2837 s)",
              "counterfactual: wall 2837 s" in out)
        # Over runs: paging, the cancelled filter, median and p90.
        calls.clear()
        out = run("--workflow", "tests.yml", "--last", "5", *W1)
        check("--last reads the run list paged and skips cancelled runs (2 of 100 qualify)",
              "runs 2: wall median 2891 s p90 2915 s" in out)
        check("over runs: the counterfactual's median and p90 print", "counterfactual wall median" in out)
        check("a full first page reads a second; with each run's jobs cached nothing else is read",
              len(calls) == 2 and all("/workflows/tests.yml/runs" in c for c in calls))
        api = Api("o/r", cache, 5, get)
        check("needs at a head git does not hold are read from the contents API, raw",
              api.needs("0" * 40, "w.yml") == dict(a=dict(name=None, needs=[]), b=dict(name=None, needs=["a"]))
              and calls[-1] == f"repos/o/r/contents/w.yml?ref={'0' * 40}")
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        gapi = Api("o/r", cache / "git", 5, get)
        gapi.needs(head, ".github/workflows/tests.yml")
        check("needs at a head git holds are read from git, not the API (0 reads)", gapi.reads == 0)
        seen = []

        def qget(path: str, raw: bool = False) -> str:
            seen.append(path)
            main_only = "event=push&branch=main" in path
            return json.dumps(dict(workflow_runs=[dict(id=11 if main_only else 22, conclusion="success")]))
        qapi = Api("o/r", cache / "q", 5, qget)
        got = qapi.runs("tests.yml", 1, "push", "main")
        check("--event and --branch reach the run-list query, and only its rows return",
              [r["id"] for r in got] == [11] and "&event=push&branch=main" in seen[0])
        check("with neither flag the query carries no filter", [r["id"] for r in qapi.runs("tests.yml", 1, None, None)] == [22])
        check("p90 is nearest rank", p90([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 9 and p90([5]) == 5)
        try:
            Api("o/r", cache / "x", 1, get).get("a") and Api("o/r", cache / "x", 0, get).get("a")
            check("a read past --max-reads refuses", False)
        except SystemExit as e:
            check("a read past --max-reads refuses", "--max-reads 0" in str(e))
        js = [dict(name=f"j{i}", conclusion="success", started_at="2026-01-01T00:00:00Z",
                   completed_at="2026-01-01T00:00:01Z") for i in range(PAGE + 5)]
        pg = Api("o/r", cache / "pg", 10, lambda p, raw=False: json.dumps(dict(
            total_count=len(js), jobs=js[(int(re.search(r"[?&]page=(\d+)", p)[1]) - 1) * PAGE:][:PAGE])))
        check("a run with more than 100 jobs is read over two pages", len(pg.jobs(7)) == PAGE + 5 and pg.reads == 2)
        live = Api("o/r", cache / "live", 5, lambda p, raw=False: json.dumps(dict(id=8, conclusion=None)))
        try:
            live.run(8)
            check("a run still in progress refuses and caches nothing", False)
        except SystemExit as e:
            check("a run still in progress refuses and caches nothing",
                  "not concluded" in str(e) and not (cache / "live" / "run_8.json").exists())
    g, unmapped = graph([dict(name="fast (3.14)", conclusion="success", started_at="2026-01-01T00:00:10Z",
                              completed_at="2026-01-01T00:00:20Z"),
                         dict(name="Pretty", conclusion="success", started_at="2026-01-01T00:00:00Z",
                              completed_at="2026-01-01T00:00:05Z"),
                         dict(name="gone", conclusion="skipped", started_at="2026-01-01T00:00:00Z",
                              completed_at="2026-01-01T00:00:00Z"),
                         dict(name="stray", conclusion="success", started_at="2026-01-01T00:00:00Z",
                              completed_at="2026-01-01T00:00:01Z"),
                         dict(name="never", conclusion="cancelled", started_at=None, completed_at=None)],
                        dict(fast=dict(name=None, needs=["pre", "gone"]), pre=dict(name="Pretty", needs=[]),
                             gone=dict(name=None, needs=[])))
    check("a matrix instance maps to its key and a named job to its name:",
          g["fast (3.14)"]["needs"] == ["Pretty"])
    check("a skipped job leaves the graph, and its edge with it", "gone" not in g)
    check("a job cancelled before it started (no timestamps) leaves the graph", "never" not in g)
    check("a job the workflow file does not name is reported unmapped", unmapped == ["stray"])
    wf = ("on: push\njobs:\n  a:\n    name: ${{ x }}\n  b:\n    needs: a  # one\n  c:\n"
          "    name: 'Lint (${{ matrix.v }})'\n    needs:\n      - a\n      - b\n    steps:\n      - run: x\n"
          "  d:\n    needs: [a, \"c\"]\nenv:\n  e:\n    needs: z\n")
    check("workflow_needs: a scalar, a block list and an inline list; an expression name dropped, a matrix name's prefix kept",
          workflow_needs(wf) == dict(a=dict(name=None, needs=[]), b=dict(name=None, needs=["a"]),
                                     c=dict(name="Lint", needs=["a", "b"]), d=dict(name=None, needs=["a", "c"])))
    print(f"ci_critpath self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
