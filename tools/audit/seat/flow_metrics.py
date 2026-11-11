#!/usr/bin/env python3
"""A round's flow, from git alone: throughput, records, yield, absorbs, re-reviews, merge hours.

    python3 tools/audit/seat/flow_metrics.py --self-test
    python3 tools/audit/seat/flow_metrics.py [--fetch] --window FROM..UNTIL \\
        --roster REF:PATH --prefix R10- [--tree origin/main] [--record-prefix record/]

R10-FLOW-TOOLKIT-MEASURE: the Lean flow study's section-0 enumerators, with
no round constant in code -- the roster, the group-id prefix and the window
are arguments. Every read is over git (review_strength.py's bus reader, and
`--fetch` is its fetch), so no API call and no rate limit. A window is
[from, until), times in UTC; `hours` is (until - from) in hours.

THE RULES.
  groups added / closed per hour. The roster at REF:PATH as of `from`
    (its last first-parent commit at or before it; none, or no file there,
    is an empty roster),
    then each first-parent commit of REF in the window touching PATH, each
    compared with the one before: a group id with the prefix appearing is
    ADDED, one whose resume.stage enters roster_lib's DONE_STAGES is CLOSED
    (a group re-opened and re-closed counts twice). Each count / hours.
  records' share of merges. The first-parent merges of `--tree` committed in
    the window whose subject is a pull-request merge (review_strength's
    MERGE_RE); a RECORD is one whose branch starts with `--record-prefix`.
  first-pass yield. Of the window's non-record merged PRs with a bus verdict
    before their merge, the share whose first verdict is `merge`; the PRs
    with none are printed beside it, never folded in.
  main absorbs per fix branch. For each non-record merged PR, the merge
    commits in merge^1..merge^2 (the branch's own commits) with a parent on
    `--tree`'s first-parent line; mean and max over those PRs.
  merge-to-merge re-reviews of unchanged code. A bus verdict in the window
    whose PR's previous verdict was `merge`, both heads present locally, and
    whose PR diff (git patch-id of merge-base(head, tree)..head) equals the
    previous head's: the review of code a merge verdict already passed. A
    pair whose heads git does not hold is printed `unresolved`, never
    counted either way.
  share of hours with a merge. The window's whole hours [from + k h, +1 h)
    holding at least one of its first-parent PR merges, records included.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_strength as rs  # noqa: E402
from roster_lib import DONE_STAGES, groups_of  # noqa: E402

ROOT = rs.ROOT


def has(repo: Path, sha: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True).returncode == 0


def roster_events(repo: Path, ref: str, path: str, prefix: str, a: datetime, b: datetime) -> tuple[int, int]:
    """(added, closed) prefix groups over REF's first-parent commits touching PATH in [a, b)."""
    def state(sha: str) -> dict:
        text = rs.git(repo, "show", f"{sha}:{path}", check=False)
        g = groups_of(json.loads(text)) if text else {}
        return {k: (v.get("resume") or {}).get("stage") in DONE_STAGES for k, v in g.items() if k.startswith(prefix)}
    before = rs.git(repo, "rev-list", "-1", "--first-parent", f"--before={a.isoformat()}", ref).strip()
    prev = state(before) if before else {}
    added = closed = 0
    for line in reversed(rs.git(repo, "log", "--first-parent", "--format=%H%x09%cI", ref, "--", path).splitlines()):
        sha, t = line.split("\t")
        if not a <= rs.when(t) < b:
            continue
        cur = state(sha)
        added += len(cur.keys() - prev.keys())
        closed += sum(done and not prev.get(k, False) for k, done in cur.items())
        prev = cur
    return added, closed


def merges(repo: Path, tree: str, a: datetime, b: datetime) -> list[dict]:
    """The first-parent PR merges of `tree` committed in [a, b), oldest first."""
    out = []
    for line in rs.git(repo, "log", "--first-parent", "--format=%H%x09%P%x09%cI%x09%s", tree).splitlines():
        sha, parents, t, subj = line.split("\t", 3)
        m = rs.MERGE_RE.match(subj)
        if m and len(parents.split()) == 2 and a <= rs.when(t) < b:
            out.append(dict(sha=sha, head=parents.split()[1], t=rs.when(t), pr=int(m[1]), branch=m[2]))
    return out[::-1]


def absorbs(repo: Path, m: dict, mainline: set) -> int:
    n = 0
    for line in rs.git(repo, "log", "--merges", "--format=%P", f"{m['sha']}^1..{m['head']}").splitlines():
        n += any(p in mainline for p in line.split())
    return n


def pr_patch(repo: Path, tree: str, head: str) -> str:
    mb = rs.git(repo, "merge-base", head, tree, check=False).strip()
    diff = rs.git(repo, "diff", mb, head, check=False) if mb else ""
    p = subprocess.run(["git", "-C", str(repo), "patch-id", "--stable"], input=diff,
                       capture_output=True, text=True)
    return (p.stdout.split() or [""])[0]


def measure(repo: Path, remote: str, tree: str, roster: str, prefix: str, record: str,
            a: datetime, b: datetime) -> dict:
    hours = (b - a).total_seconds() / 3600
    ref, path = roster.split(":", 1)
    added, closed = roster_events(repo, ref, path, prefix, a, b)
    ms = merges(repo, tree, a, b)
    fixes = [m for m in ms if not m["branch"].startswith(record)]
    verdicts, _ = rs.load(repo, remote)
    first = {}
    for v in verdicts:
        first.setdefault(v["pr"], v)
    judged = [m for m in fixes if m["pr"] in first and first[m["pr"]]["t"] < m["t"]]
    mainline = set(rs.git(repo, "rev-list", "--first-parent", tree).split())
    ab = [absorbs(repo, m, mainline) for m in fixes]
    rereview = unresolved = 0
    last = {}
    for v in verdicts:
        p = last.get(v["pr"])
        last[v["pr"]] = v
        if not (p and p["kind"] == "merge" and a <= v["t"] < b):
            continue
        if not (has(repo, p["head"]) and has(repo, v["head"])):
            unresolved += 1
        elif p["head"] == v["head"] or pr_patch(repo, tree, p["head"]) == pr_patch(repo, tree, v["head"]):
            rereview += 1
    whole = int(hours)
    lit = {int((m["t"] - a).total_seconds() // 3600) for m in ms}
    return dict(hours=hours, added=added, closed=closed, merges=len(ms), records=len(ms) - len(fixes),
                judged=len(judged), first_pass=sum(first[m["pr"]]["kind"] == "merge" for m in judged),
                unjudged=len(fixes) - len(judged), fixes=len(fixes), absorbs=ab, rereview=rereview,
                unresolved=unresolved, whole=whole, lit=len({h for h in lit if h < whole}))


def report(r: dict) -> None:
    h = r["hours"]
    pct = lambda n, d: f"{n}/{d} ({n / d:.2f})" if d else f"{n}/0 (-)"
    print(f"window {h:.1f} h")
    print(f"  groups added {r['added']} ({r['added'] / h:.2f}/h), closed {r['closed']} ({r['closed'] / h:.2f}/h)")
    print(f"  merges {r['merges']}, records {pct(r['records'], r['merges'])}")
    print(f"  first-pass yield {pct(r['first_pass'], r['judged'])}; merged with no bus verdict {r['unjudged']}")
    ab = r["absorbs"]
    print(f"  main absorbs per fix branch: mean {sum(ab) / len(ab) if ab else 0:.2f} max {max(ab, default=0)} over {len(ab)}")
    print(f"  merge-to-merge re-reviews of unchanged code {r['rereview']}; unresolved {r['unresolved']}")
    print(f"  hours with a merge {pct(r['lit'], r['whole'])}")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--tree", default="origin/main")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--window", metavar="FROM..UNTIL")
    ap.add_argument("--roster", metavar="REF:PATH")
    ap.add_argument("--prefix", metavar="R<n>-", help="the round's group-id prefix")
    ap.add_argument("--record-prefix", default="record/")
    ap.add_argument("--self-test", action="store_true")
    return ap


def main(argv: list[str]) -> int:
    ap = parser()
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not (a.window and a.roster and a.prefix):
        ap.error("--window FROM..UNTIL, --roster REF:PATH and --prefix are required")
    repo = Path(a.repo)
    if a.fetch:
        rs.git(repo, "fetch", "-q", "--tags", a.remote, *(f"+refs/heads/{f}/*:refs/remotes/{a.remote}/{f}/*"
                                                         for f in ("review", "verdict", "probe")))
    f, u = (rs.when(x) for x in a.window.split("..", 1))
    report(measure(repo, a.remote, a.tree, a.roster, a.prefix, a.record_prefix, f, u))
    return 0


def self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"{'ok' if cond else 'FAIL'}: {name}")

    env = throwaway_git_env()
    with tempfile.TemporaryDirectory() as d:
        R = Path(d)
        throwaway_git_init(R, "-q", "-b", "main")
        g = lambda *x, **k: subprocess.run(["git", "-C", d, *x], capture_output=True, text=True,
                                           check=True, env={**env, **k.get("e", {})}).stdout.strip()

        def mk(parents: str, files: dict[str, str], msg: str, t: str) -> str:
            ix = {"GIT_INDEX_FILE": str(R / ".git" / "fixture-index")}
            g("read-tree", *([parents.split()[0]] if parents else ["--empty"]), e=ix)
            for p, text in files.items():
                (R / "blob").write_text(text)
                g("update-index", "--add", "--cacheinfo", f"100644,{g('hash-object', '-w', str(R / 'blob'))},{p}", e=ix)
            return g("commit-tree", g("write-tree", e=ix), *(x for q in parents.split() for x in ("-p", q)),
                     "-m", msg, e={**ix, "GIT_COMMITTER_DATE": t, "GIT_AUTHOR_DATE": t})

        def verdict(pr: int, kind: str, head: str, t: str) -> None:
            ref = f"refs/remotes/origin/review/{pr}"
            par = subprocess.run(["git", "-C", d, "rev-parse", "-q", "--verify", ref], capture_output=True, text=True)
            subj = f"verdict: #{pr} Fix review: {kind} {head}" + (" harness: x" if kind == "blocked" else "")
            sha = g("commit-tree", empty, *(["-p", par.stdout.strip()] if par.returncode == 0 else []),
                    "-m", subj, e={"GIT_COMMITTER_DATE": t, "GIT_AUTHOR_DATE": t})
            g("update-ref", ref, sha)

        T = lambda h, m=0: f"2026-10-01T{h:02d}:{m:02d}:00Z"
        grp = lambda gid, stage: dict(group=gid, resume=dict(stage=stage))
        ros = lambda *gs: {"ro.json": json.dumps(dict(groups=list(gs)))}
        empty = g("hash-object", "-t", "tree", "-w", "/dev/null")
        # Roster: before the window, R1-A open; in it, R1-B and X-C added (X-C lacks the prefix),
        # R1-A closed, R1-A re-opened and re-closed (counts twice), R1-B closed after the window.
        r0 = mk("", ros(grp("R1-A", "fix")), "r0", T(0))
        r1 = mk(r0, ros(grp("R1-A", "done"), grp("R1-B", "fix"), grp("X-C", "fix")), "r1", T(2))
        r2 = mk(r1, ros(grp("R1-A", "review"), grp("R1-B", "fix"), grp("X-C", "done")), "r2", T(3))
        r3 = mk(r2, ros(grp("R1-A", "rca-done"), grp("R1-B", "fix"), grp("X-C", "done")), "r3", T(4))
        r4 = mk(r3, ros(grp("R1-A", "done"), grp("R1-B", "done"), grp("X-C", "done")), "r4", T(9))
        g("update-ref", "refs/remotes/origin/roster", r4)
        # Main: m0 root; PR 1 fix branch absorbs main once and is merged at 02:30; a record PR at
        # 02:45; PR 2 merged at 05:10 after two merge verdicts on unchanged code; one merge at 11:00
        # (after the window).
        m0 = mk("", {"a": "0\n"}, "root", T(0))
        b1 = mk(m0, {"a": "0\n", "f1": "1\n"}, "pr1 work", T(1))
        m1 = mk(m0, {"a": "1\n"}, "direct", T(1, 30))
        b1b = mk(f"{b1} {m1}", {"a": "1\n", "f1": "1\n"}, "Merge remote-tracking branch 'origin/main'", T(2))
        M1 = mk(f"{m1} {b1b}", {"a": "1\n", "f1": "1\n"}, "Merge pull request #1 from o/fix/r1-a", T(2, 30))
        rc = mk(M1, {"a": "1\n", "f1": "1\n", "rec": "1\n"}, "row", T(2, 40))
        M2 = mk(f"{M1} {rc}", {"a": "1\n", "f1": "1\n", "rec": "1\n"}, "Merge pull request #9 from o/record/x", T(2, 45))
        b2 = mk(m0, {"a": "0\n", "f2": "2\n"}, "pr2 work", T(1))
        b2b = mk(f"{b2} {M2}", {"a": "1\n", "f1": "1\n", "rec": "1\n", "f2": "2\n"}, "Merge branch 'main'", T(4))
        M3 = mk(f"{M2} {b2b}", {"a": "1\n", "f1": "1\n", "rec": "1\n", "f2": "2\n"},
                "Merge pull request #2 from o/fix/r1-b", T(5, 10))
        M4 = mk(M3, {"a": "2\n", "f1": "1\n", "rec": "1\n", "f2": "2\n"}, "Merge pull request #3 from o/fix/late", T(11))
        g("update-ref", "refs/remotes/origin/main", M4)
        verdict(1, "blocked", b1, T(1, 10))
        verdict(1, "merge", b1b, T(2, 10))
        verdict(2, "merge", b2, T(1, 20))
        verdict(2, "merge", b2b, T(4, 30))
        verdict(2, "merge", "f" * 40, T(5))
        a, b = rs.when(T(1)), rs.when(T(6))
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "record/", a, b)
        check("window is 5.0 h", r["hours"] == 5.0)
        check("added: R1-B only (X-C lacks the prefix, R1-A predates the window)", r["added"] == 1)
        check("closed: R1-A twice (done, then rca-done after a re-open); R1-B closes after the window",
              r["closed"] == 2)
        check("merges in the window: #1, #9 and #2 (#3 is after it)", r["merges"] == 3)
        check("records: #9's record/ branch, 1 of 3", r["records"] == 1)
        check("first-pass: #1 opened blocked, #2 opened merge -> 1 of 2", (r["first_pass"], r["judged"]) == (1, 2))
        check("absorbs: #1 and #2 each merged main once", sorted(r["absorbs"]) == [1, 1])
        check("re-review: #2's second merge verdict re-read b2's unchanged diff", r["rereview"] == 1)
        check("a head git does not hold is unresolved, never counted", r["unresolved"] == 1)
        check("hours with a merge: 02:xx and 05:xx of 5", (r["lit"], r["whole"]) == (2, 5))
        # Perturbations.
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "fix/", a, b)
        check("--record-prefix is an argument: fix/ makes #1 and #2 the records", r["records"] == 2)
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "X-", "record/", a, b)
        check("--prefix is an argument: X- counts X-C added and closed", (r["added"], r["closed"]) == (1, 1))
        b2c = mk(f"{b2} {M2}", {"a": "1\n", "f1": "1\n", "rec": "1\n", "f2": "22\n"}, "pr2 changed", T(4, 40))
        verdict(2, "merge", b2c, T(4, 50))
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "record/", a, b)
        check("a merge verdict on a changed diff is not a re-review of unchanged code", r["rereview"] == 1)
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "record/", a, rs.when(T(5, 10)))
        check("[from, until): a merge at until is outside the window", r["merges"] == 2 and r["whole"] == 4)
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "record/", a, rs.when(T(5, 30)))
        check("hours: the partial last hour (05:00-05:30, holding #2's merge) is not a whole hour",
              (r["lit"], r["whole"]) == (1, 4))
        b4 = mk(M4, {"a": "2\n", "f1": "1\n", "rec": "1\n", "f2": "2\n", "f4": "4\n"}, "pr4 work", T(11, 5))
        g("update-ref", "refs/remotes/origin/main", mk(f"{M4} {b4}", {"a": "2\n", "f1": "1\n", "rec": "1\n", "f2": "2\n",
                                                                     "f4": "4\n"}, "Merge pull request #4 from o/fix/r1-d", T(11, 10)))
        verdict(4, "merge", b4, T(11, 30))
        r = measure(R, "origin", "origin/main", "origin/roster:ro.json", "R1-", "record/", a, rs.when(T(12)))
        check("first-pass: a PR first reviewed after its merge is unjudged, never a first pass (#4)",
              (r["judged"], r["unjudged"]) == (2, 1))
    print(f"flow_metrics self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
