#!/usr/bin/env python3
"""Review strength from the verdict bus: real-catch blocks per reviewed PR.

    python3 tools/audit/seat/review_strength.py --self-test
    python3 tools/audit/seat/review_strength.py [--fetch] \\
        --window E=2026-10-15T12:37Z..2026-10-19T14:50Z \\
        --window L=2026-10-19T14:50Z..2026-10-21T14:50Z \\
        [--by kind|class|prior-merge|origin|size|product|fixer[+...] ...] \\
        [--roster REF:PATH] [--as-of T]

R10-FLOW-YIELD-PROBE (owner ruling R13). Everything is read over git: no
REST call, so no rate limit and no 403. `--fetch` first fetches
`refs/heads/{review,verdict,probe}/*` and the tags from the remote.

THE RULE. A verdict is a commit on a `review/<pr>` ref, or on its
`archive/review/<pr>` tag once prune_refs.py has archived the ref (and a
`verdict/<pr>` copy likewise), whose subject matches
`verdict: #<pr> Fix review: merge|blocked <40hex>`; a blocked one carries
`<class>:` after the sha. A commit reachable from several review refs counts
once. A window holds the verdicts whose COMMITTER time falls in
[from, until); its reviewed PRs are the distinct PRs of those verdicts.
A blocked verdict is REAL when its class is in REAL_CATCH (the flow study's
"Guardrail baselines" list) or in `--real-extra`, otherwise BOOKKEEPING. A subject that names the
grammar's prefix but not its shape is printed on its own `outside` row,
never folded in.

THE VOCABULARY. The block classes the reviewer is taught are read from
`--tree`'s web-fix-wave.js VERDICT_CLASSES literal, never copied here; a
tree without one refuses. REAL_CATCH is the study's judgement of which words
name a catch, and is the one list this file types: the header prints it
split into the taught real words, the taught words it leaves bookkeeping
(so a newly taught class shows there until REAL_CATCH judges it) and the
untaught real words reviewers wrote. `--by route` keys a block on the class
the wave routes it to: its word when taught, else `other` (parseVerdict's
rule). Each subject names ONE class, so a verdict blocked for two
reasons counts once, under the class its reviewer wrote first.

    real per PR = real blocks / reviewed PRs  (one PR blocked in 6 rounds
                  counts 6, so a few long PRs dominate it)
    incidence   = reviewed PRs with >= 1 real block / reviewed PRs

STRATA (`--by`). kind: `cloud` when the verdict's bus nonce prefix names a
probe return, a ref `probe/rev-<pr>-<nonce[:8]>` or tag
`archive/probe/rev-<pr>-<nonce[:8]>` (cloud_relay.sh's return path), or its
`verdict/<pr>` copy's `bus-confirmed:` id starts with `cloud` or ends in
`-cloud`; `local` otherwise. route: above. prior-merge: the PR already had a `merge`
verdict on the bus (a re-review a carry could replace). class: the raw class
word, `(merge)` for a merge verdict, `(no class)` for a block naming none. origin, fixer: from the roster file at `--roster REF:PATH`, joined on
the first `R<n>-...` group token of `dev/programme/delivery/<pr>.md` at
`--tree`, else on the roster `resume.branch`; origin is `finding` when the
group lists issues, findings or fixes, `group` when it lists none, `none`
with no group. size, product: the PR's diff, `--tree`'s first-parent merge of
it when there is one, else its last verdict's head against its merge base
with `--tree`, delivery rows excluded; product means it touches
`custom_components/` or `blueprints/`. `a+b` crosses two strata.

AS OF (`--as-of T`, default the latest window's until). The four fact strata
are taken as of T, so a verdict, merge or roster edit after T moves none of
them: the last verdict is the last one before T, and `--tree` and the roster
REF are each resolved to their last first-parent commit dated at or before
T (both printed). A PR with no verdict before T reads `(unreviewed at T)`
in every fact stratum. Every figure is then a function of the bus, the two refs
and T, not of a tip's position when it is run.
first-pass m/n: of the PRs whose FIRST bus verdict falls in the window, the
m whose first verdict is `merge`.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

REAL_CATCH = frozenset({
    "harness", "class-open", "test-vacuous", "vacuous-test", "vacuous-check",
    "mutation-vacuous", "mutant-survives", "mutation-survivor",
    "mutation-untriaged", "mutation", "architecture-unsound", "metric-gamed",
    "defect", "product-tradeoff-regression", "policy-regression",
    "figures-false"})
VERDICT_RE = re.compile(
    r"verdict: #(\d+) Fix review: (merge|blocked) ([0-9a-f]{40})(?: ([^\s:]+):)?")
PREFIX_RE = re.compile(r"verdict: #(\d+) Fix review:")
NONCE_RE = re.compile(r"^bus-nonce:\s*([0-9a-f]{32})", re.M)
PROBE_RE = re.compile(r"rev-(\d+)-([0-9a-f]{8})$")
CONFIRMED_RE = re.compile(r"^bus-confirmed:\s*(\S+) \(review/\d+ at ([0-9a-f]{40})\)", re.M)
GROUP_RE = re.compile(r"\b(R\d+-[A-Z0-9][A-Z0-9-]*[A-Z0-9])\b")
MERGE_RE = re.compile(r"Merge pull request #(\d+) from \S+?/(\S+)")
STRATA = ("kind", "class", "route", "prior-merge", "origin", "size", "product", "fixer")
WAVE_SCRIPT = ".claude/workflows/web-fix-wave.js"
CLASSES_RE = re.compile(r"const VERDICT_CLASSES = \[([^\]]*)\]")
WORD_RE = re.compile(r"'([a-z][a-z0-9-]*)'")
FACT_STRATA = {"origin", "fixer", "size", "product"}


def git(repo: Path, *a: str, check: bool = True) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                          text=True, check=check).stdout


def when(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def refs(repo: Path, pattern: str) -> list[str]:
    return git(repo, "for-each-ref", "--format=%(refname)", pattern).split()


def load(repo: Path, remote: str, real: frozenset = REAL_CATCH) -> tuple[list[dict], list[str]]:
    """Every verdict on the bus, oldest first, and the outside-grammar subjects."""
    probes = set()
    for r in refs(repo, f"refs/remotes/{remote}/probe/") + refs(repo, "refs/tags/archive/probe/"):
        m = PROBE_RE.search(r)
        if m:
            probes.add((int(m[1]), m[2]))
    confirmed = {}
    for r in refs(repo, f"refs/remotes/{remote}/verdict/") + refs(repo, "refs/tags/archive/verdict/"):
        for m in CONFIRMED_RE.finditer(git(repo, "log", "--format=%B", r)):
            confirmed[m[2]] = m[1]
    seen, out, outside = set(), [], []
    for r in refs(repo, f"refs/remotes/{remote}/review/") + refs(repo, "refs/tags/archive/review/"):
        for line in git(repo, "log", "--format=%H%x09%cI%x09%s", r).splitlines():
            sha, t, subj = line.split("\t", 2)
            if sha in seen or not PREFIX_RE.match(subj):
                continue
            seen.add(sha)
            m = VERDICT_RE.match(subj)
            if not m:
                outside.append(subj)
                continue
            body = git(repo, "show", f"{sha}:VERDICT.md", check=False)
            n = NONCE_RE.search(body)
            nonce = n[1] if n else ""
            rid = confirmed.get(sha, "")
            cloud = (int(m[1]), nonce[:8]) in probes or rid.startswith("cloud") or rid.endswith("-cloud")
            out.append(dict(pr=int(m[1]), t=when(t), kind=m[2], head=m[3],
                            cls=m[4] or "", real=m[2] == "blocked" and m[4] in real,
                            reviewer="cloud" if cloud else "local"))
    out.sort(key=lambda v: v["t"])
    merged = set()
    for v in out:
        v["prior_merge"] = v["pr"] in merged
        if v["kind"] == "merge":
            merged.add(v["pr"])
    return out, outside


def verdict_classes(text: str) -> tuple[str, ...]:
    """The block classes the wave script teaches, read from its VERDICT_CLASSES literal; refuses without one."""
    m = CLASSES_RE.search(text)
    words = tuple(WORD_RE.findall(m[1])) if m else ()
    if not words:
        raise SystemExit(f"review_strength: no VERDICT_CLASSES literal in {WAVE_SCRIPT}")
    return words


def class_sets(taught: tuple[str, ...], real: frozenset) -> dict[str, list[str]]:
    """REAL's words split by whether the vocabulary teaches them, and the taught words REAL leaves out."""
    return {"taught real": sorted(set(taught) & real), "taught bookkeeping": sorted(set(taught) - real),
            "untaught real": sorted(real - set(taught))}


def as_of(repo: Path, ref: str, t: datetime) -> str:
    """`ref`'s last first-parent commit dated at or before `t`; refuses when it has none."""
    sha = git(repo, "rev-list", "-1", "--first-parent", f"--before={t.isoformat()}", ref).strip()
    if not sha:
        raise SystemExit(f"review_strength: {ref} has no commit at or before {t:%Y-%m-%dT%H:%MZ}")
    return sha


def pr_facts(repo: Path, tree: str, roster: str | None, verdicts: list[dict],
             until: datetime) -> dict[int, dict]:
    """origin, fixer, size and product per PR (the strata needing more than the bus), as of `until`."""
    groups = {}
    tree = as_of(repo, tree, until)
    ref = ""
    if roster:
        ref, path = roster.split(":", 1)
        ref = as_of(repo, ref, until)
        for g in json.loads(git(repo, "show", f"{ref}:{path}"))["groups"]:
            groups[g["group"]] = g
    print(f"facts as of {until:%Y-%m-%dT%H:%MZ}: tree {tree[:12]} roster {ref[:12] or '-'}")
    merges = {}
    for line in git(repo, "log", "--first-parent", "--format=%H%x09%P%x09%s", tree).splitlines():
        sha, parents, subj = line.split("\t", 2)
        m = MERGE_RE.match(subj)
        if m and len(parents.split()) == 2 and int(m[1]) not in merges:
            merges[int(m[1])] = (sha, parents.split()[1], m[2])
    last = {v["pr"]: v["head"] for v in verdicts if v["t"] < until}
    facts = {}
    for pr, head in last.items():
        row = git(repo, "show", f"{tree}:dev/programme/delivery/{pr}.md", check=False)
        g = GROUP_RE.search(row)
        grp = groups.get(g[1]) if g else None
        if pr in merges:
            base, head, branch = merges[pr][0] + "^1", merges[pr][1], merges[pr][2]
        else:
            base, branch = tree, ""
        if grp is None and branch:
            grp = next((x for x in groups.values()
                        if (x.get("resume") or {}).get("branch") in (branch, branch.removesuffix("-pr"))), None)
        mb = git(repo, "merge-base", base, head, check=False).strip()
        lines, files = 0, []
        for ln in git(repo, "diff", "--numstat", mb, head, check=False).splitlines() if mb else []:
            a, d, f = ln.split("\t", 2)
            files.append(f)
            if not f.startswith("dev/programme/delivery/"):
                lines += (int(a) if a != "-" else 0) + (int(d) if d != "-" else 0)
        facts[pr] = dict(
            origin="none" if grp is None else "finding" if (grp.get("issues") or grp.get("findings") or grp.get("fixes")) else "group",
            fixer=((grp or {}).get("model") or {}).get("fixer") or "none",
            size="?" if not mb else "S<150" if lines < 150 else "M<600" if lines < 600 else "L>=600",
            product=any(f.startswith(("custom_components/", "blueprints/")) for f in files))
    return facts


def stratum(by: str, v: dict, facts: dict[int, dict], taught: tuple[str, ...] = ()) -> str:
    if "+" in by:
        return "+".join(stratum(b, v, facts, taught) for b in by.split("+"))
    if by == "all":
        return "all"
    if by == "kind":
        return v["reviewer"]
    if by == "class":
        return v["cls"] or ("(merge)" if v["kind"] == "merge" else "(no class)")
    if by == "route":
        return "(merge)" if v["kind"] == "merge" else v["cls"] if v["cls"] in taught else "other"
    if by == "prior-merge":
        return "after-a-merge-verdict" if v["prior_merge"] else "no-merge-yet"
    return str(facts[v["pr"]][by]) if v["pr"] in facts else "(unreviewed at T)"


def tally(verdicts: list[dict], a: datetime, b: datetime, key) -> dict[str, dict]:
    out = defaultdict(lambda: dict(prs=set(), verdicts=0, real=0, book=0, caught=set(), first=[]))
    seen = set()
    for v in verdicts:
        first = v["pr"] not in seen
        seen.add(v["pr"])
        if a <= v["t"] < b:
            o = out[key(v)]
            if first:
                o["first"].append(v["kind"] == "merge")
            o["prs"].add(v["pr"])
            o["verdicts"] += 1
            if v["kind"] == "blocked":
                o["real" if v["real"] else "book"] += 1
                if v["real"]:
                    o["caught"].add(v["pr"])
    return out


def fmt(o: dict) -> str:
    n = len(o["prs"])
    r = lambda x: f"{x / n:.2f}" if n else "-"
    return (f"PRs {n} verdicts {o['verdicts']} real {o['real']} ({r(o['real'])}/PR) "
            f"book {o['book']} ({r(o['book'])}/PR) incidence {len(o['caught'])}/{n} ({r(len(o['caught']))}) "
            f"first-pass {sum(o['first'])}/{len(o['first'])}")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--tree", default="origin/main")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--window", action="append", default=[], metavar="NAME=FROM..UNTIL")
    ap.add_argument("--by", action="append", default=[], metavar="S[+S...]",
                    help="one of " + ", ".join(STRATA) + "; joined with + to cross them")
    ap.add_argument("--roster", metavar="REF:PATH")
    ap.add_argument("--as-of", metavar="T", help="the time the fact strata are taken at; default the latest window's until")
    ap.add_argument("--real-extra", default="", metavar="W[,W...]",
                    help="class words counted REAL beside REAL_CATCH (a sensitivity run)")
    ap.add_argument("--self-test", action="store_true")
    return ap


def main(argv: list[str]) -> int:
    ap = parser()
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = Path(a.repo)
    if not a.window:
        ap.error("at least one --window NAME=FROM..UNTIL")
    used = {s for by in a.by for s in by.split("+")}
    if used - set(STRATA):
        ap.error(f"unknown stratum {sorted(used - set(STRATA))}; one of {', '.join(STRATA)}")
    if {"origin", "fixer"} & used and not a.roster:
        ap.error("--by origin|fixer needs --roster REF:PATH")
    if a.fetch:
        git(repo, "fetch", "-q", "--tags", a.remote, *(f"+refs/heads/{f}/*:refs/remotes/{a.remote}/{f}/*"
                                                      for f in ("review", "verdict", "probe")))
    extra = frozenset(w for w in a.real_extra.split(",") if w)
    verdicts, outside = load(repo, a.remote, REAL_CATCH | extra)
    if extra:
        print(f"REAL = the study's list + {', '.join(sorted(extra))}")
    wins = []
    for w in a.window:
        name, span = w.split("=", 1)
        f, u = span.split("..", 1)
        wins.append((name, when(f), when(u)))
    t = when(a.as_of) if a.as_of else max(u for _, _, u in wins)
    facts = pr_facts(repo, a.tree, a.roster, verdicts, t) if FACT_STRATA & used else {}
    print(f"verdicts on the bus: {len(verdicts)}; outside the grammar: {len(outside)}")
    for s in outside:
        print(f"  outside: {s[:100]}")
    taught = verdict_classes(git(repo, "show", f"{a.tree}:{WAVE_SCRIPT}"))
    for k, words in class_sets(taught, REAL_CATCH | extra).items():
        print(f"{k}: {', '.join(words) or '-'}")
    for by in ["all", *a.by]:
        print(f"## {by}")
        rows = {name: tally(verdicts, f, u, lambda v: stratum(by, v, facts, taught)) for name, f, u in wins}
        for k in sorted({k for r in rows.values() for k in r}):
            for name, _, _ in wins:
                o = rows[name].get(k) or dict(prs=set(), verdicts=0, real=0, book=0, caught=set(), first=[])
                print(f"  {k:24} {name:6} {fmt(o)}")
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
        g("commit", "-q", "--allow-empty", "-m", "root")
        N = {i: f"{i:x}" * 32 for i in range(1, 10)}
        H = "a" * 40

        def verdict(ref: str, subj: str, nonce: str, t: str, pre: str = "") -> str:
            (R / "VERDICT.md").write_text(f"{subj.split(' ', 2)[2]}\n\n{pre}bus-nonce: {nonce}\n")
            g("add", "VERDICT.md")
            par = g("rev-parse", "-q", "--verify", ref) if subprocess.run(
                ["git", "-C", d, "rev-parse", "-q", "--verify", ref], capture_output=True).returncode == 0 else None
            tree = g("write-tree")
            sha = g("commit-tree", tree, *(["-p", par] if par else []), "-m", subj,
                    e={"GIT_COMMITTER_DATE": t, "GIT_AUTHOR_DATE": t})
            g("update-ref", ref, sha)
            return sha

        rv = lambda pr: f"refs/remotes/origin/review/{pr}"
        # PR 1: blocked real (local), then merge, then a re-review after the merge.
        verdict(rv(1), f"verdict: #1 Fix review: blocked {H} harness: class open", N[1], "2026-10-01T01:00:00Z")
        verdict(rv(1), f"verdict: #1 Fix review: merge {H}", N[2], "2026-10-01T02:00:00Z")
        verdict(rv(1), f"verdict: #1 Fix review: merge {H}", N[3], "2026-10-01T03:00:00Z")
        # PR 2: bookkeeping block returned by a cloud probe, then merge.
        s2 = verdict(rv(2), f"verdict: #2 Fix review: blocked {H} carry-missing: no dest", N[4], "2026-10-01T04:00:00Z")
        g("update-ref", f"refs/remotes/origin/probe/rev-2-{N[4][:8]}", s2)
        verdict(rv(2), f"verdict: #2 Fix review: merge {H}", N[5], "2026-10-01T05:00:00Z")
        # PR 3: a real block in the later window; confirmed by a cloud id on verdict/3.
        s3 = verdict(rv(3), f"verdict: #3 Fix review: blocked {H} mutation-survivor: x", N[6], "2026-10-02T01:00:00Z")
        vs = g("commit-tree", g("write-tree"), "-m", f"verdict: #3\n\nbus-confirmed: cloud-rev-3 (review/3 at {s3})")
        g("update-ref", "refs/remotes/origin/verdict/3", vs)
        # PR 4: a subject shaped outside the grammar, and the same commit reachable from two refs.
        s4 = verdict(rv(4), f"verdict: #4 Fix review: PASS\tmerge {H}", N[7], "2026-10-02T02:00:00Z")
        g("update-ref", rv(44), s4)
        vlist, outside = load(R, "origin")
        a, b, c = when("2026-10-01T00:00Z"), when("2026-10-02T00:00Z"), when("2026-10-03T00:00Z")
        e = tally(vlist, a, b, lambda v: "all")["all"]
        check("window E: 2 PRs, 5 verdicts, 1 real, 1 bookkeeping",
              (len(e["prs"]), e["verdicts"], e["real"], e["book"]) == (2, 5, 1, 1))
        check("incidence counts a PR once: 1 of 2", len(e["caught"]) == 1)
        lw = tally(vlist, b, c, lambda v: "all")["all"]
        check("window L: [from, until) excludes E's verdicts", (len(lw["prs"]), lw["real"]) == (1, 1))
        check("an out-of-grammar subject is its own row, never a verdict",
              len(outside) == 1 and "PASS" in outside[0] and all(v["pr"] != 4 for v in vlist))
        check("a commit on two refs is read once", len(outside) == 1)
        kinds = {(v["pr"], v["kind"]): v["reviewer"] for v in vlist}
        check("probe ref rev-<pr>-<nonce8> marks the verdict cloud", kinds[(2, "blocked")] == "cloud")
        check("bus-confirmed cloud-* id marks the verdict cloud", kinds[(3, "blocked")] == "cloud")
        check("no probe and no cloud id reads local", kinds[(1, "blocked")] == "local")
        pm = tally(vlist, a, b, lambda v: stratum("prior-merge", v, {}))
        check("one re-review after a merge verdict", pm["after-a-merge-verdict"]["verdicts"] == 1)
        check("first-pass: PR 1 opened blocked, PR 2 blocked -> 0 of 2 in E",
              sorted(e["first"]) == [False, False])
        x = tally(vlist, a, c, lambda v: stratum("kind+prior-merge", v, {}))
        check("crossed strata key on both: local+after-a-merge-verdict holds PR 1's re-review",
              x["local+after-a-merge-verdict"]["verdicts"] == 1 and "cloud+no-merge-yet" in x)
        # Perturbation: re-shape PR 2's block out of the grammar -> one fewer bookkeeping block.
        verdict(rv(2), f"verdict: #2 Fix review: blocked {H} carry-missing no colon", N[8], "2026-10-01T06:00:00Z")
        e2 = tally(load(R, "origin")[0], a, b, lambda v: "all")["all"]
        check("a class word without its colon is a block of class '' (bookkeeping), not real",
              (e2["book"], e2["real"]) == (2, 1))
        ex = tally(load(R, "origin", REAL_CATCH | {"carry-missing"})[0], a, b, lambda v: "all")["all"]
        check("--real-extra moves a word from bookkeeping to real, and only that word",
              (ex["real"], ex["book"]) == (2, 1))
        check("window: [from, until) excludes a verdict at until (PR 2's block at 04:00)",
              tally(vlist, a, when("2026-10-01T04:00Z"), lambda v: "all")["all"]["verdicts"] == 3)

        # pr_facts: a roster, delivery rows, a merged PR (5) and an unmerged one (6).
        def mk(parent: str | None, files: dict[str, str], msg: str, t: str) -> str:
            ix = {"GIT_INDEX_FILE": str(R / ".git" / "fixture-index")}
            g("read-tree", *([parent.split()[0]] if parent else ["--empty"]), e=ix)
            for path, text in files.items():
                (R / "blob").write_text(text)
                g("update-index", "--add", "--cacheinfo", f"100644,{g('hash-object', '-w', str(R / 'blob'))},{path}", e=ix)
            return g("commit-tree", g("write-tree", e=ix), *(x for q in (parent or "").split() for x in ("-p", q)),
                     "-m", msg, e={**ix, "GIT_COMMITTER_DATE": t, "GIT_AUTHOR_DATE": t})

        lines = lambda n: "".join(f"{i}\n" for i in range(n))
        grp = lambda name, issues, fixer: dict(group=name, issues=issues, model=dict(fixer=fixer))
        # R1-FIX lists fixes alone and is joined only on its resume.branch (PR 7 has no row).
        fix = dict(group="R1-FIX", issues=[], fixes=["f1"], model=dict(fixer="haiku"), resume=dict(branch="fix/r1-fix"))
        # R1-FINDS lists findings alone (PR 8's row); R1-RES is joined on a resume.branch that keeps
        # its -pr (PR 14); R1-EMPTY's empty resume.branch must join no unmerged, unrowed PR.
        more = [dict(group="R1-FINDS", issues=[], findings=["x1"], model=dict(fixer="opus")),
                dict(group="R1-RES", issues=[], model=dict(fixer="gpt"), resume=dict(branch="fix/r1-res-pr")),
                dict(group="R1-EMPTY", issues=[], model=dict(fixer="empty"), resume=dict(branch=""))]
        RP = "ro:ster.json"  # a colon in the path: the roster splits REF:PATH at the first one
        r1 = mk(None, {RP: json.dumps(dict(groups=[grp("R1-FIND", [7], "opus"), grp("R1-GRP", [], "sonnet"), fix, *more]))},
                "roster", "2026-10-01T00:00:00Z")
        r2 = mk(r1, {RP: json.dumps(dict(groups=[grp("R1-FIND", [], "opus"), grp("R1-GRP", [], "sonnet"), fix, *more]))},
                "roster: R1-FIND loses its issues", "2026-10-05T12:00:00Z")
        g("update-ref", "refs/remotes/origin/roster", r2)
        m0 = g("rev-parse", "main")
        m1 = mk(m0, {"dev/programme/delivery/6.md": "| 6 | R1-GRP |\n", "dev/programme/delivery/8.md": "| 8 | R1-FINDS |\n",
                     WAVE_SCRIPT: "const VERDICT_CLASSES = [\n  'harness', 'carry-missing',\n]\n",
                     "docs/base.md": lines(300)}, "row 6", "2026-10-01T12:00:00Z")
        c1 = mk(m1, {"custom_components/x.py": lines(20)}, "pr 5 first", "2026-10-02T01:00:00Z")
        c2 = mk(c1, {"custom_components/x.py": lines(160)}, "pr 5 second", "2026-10-02T03:00:00Z")
        m2 = mk(f"{m1} {c2}", {"custom_components/x.py": lines(160)},
                "Merge pull request #5 from tvofi/fix/r1-find", "2026-10-03T00:00:00Z")
        m3 = mk(m2, {"dev/programme/delivery/5.md": "| 5 | R1-FIND |\n"}, "row 5", "2026-10-03T01:00:00Z")
        # PR 7, from branch fix/r1-fix-pr, merged twice: 20 lines, then 700 more.
        e1 = mk(m1, {"docs/a.md": lines(20)}, "pr 7 first", "2026-10-02T02:30:00Z")
        e2 = mk(e1, {"docs/b.md": lines(700)}, "pr 7 second", "2026-10-03T01:30:00Z")
        m4 = mk(f"{m3} {e1}", {"docs/a.md": lines(20)},
                "Merge pull request #7 from tvofi/fix/r1-fix-pr", "2026-10-03T02:00:00Z")
        m5 = mk(f"{m4} {e2}", {"docs/b.md": lines(700)},
                "Merge pull request #7 from tvofi/fix/r1-fix-pr", "2026-10-03T03:00:00Z")
        g("update-ref", "refs/heads/main", m5)
        # PR 6's own delivery row (200 lines) is excluded from its size.
        d1 = mk(m1, {"docs/y.md": lines(20), "dev/programme/delivery/6.md": "| 6 | R1-GRP |\n" + lines(200)},
                "pr 6 first", "2026-10-02T01:00:00Z")
        d2 = mk(d1, {"custom_components/z.py": lines(5)}, "pr 6 second", "2026-10-05T00:00:00Z")
        verdict(rv(5), f"verdict: #5 Fix review: merge {c1}", N[9], "2026-10-02T02:00:00Z")
        verdict(rv(6), f"verdict: #6 Fix review: blocked {d1} harness: x", N[9], "2026-10-02T02:00:00Z")
        verdict(rv(6), f"verdict: #6 Fix review: merge {d2}", N[9], "2026-10-05T01:00:00Z")
        s7 = verdict(rv(7), f"verdict: #7 Fix review: merge {e1}", N[9], "2026-10-02T03:00:00Z")
        vs = g("commit-tree", g("write-tree"), "-m", f"verdict: #7\n\nbus-confirmed: seat-7-cloud (review/7 at {s7})")
        g("update-ref", "refs/remotes/origin/verdict/7", vs)
        # PR 8: reviewed FIRST (09-30) though numbered after 1..7, blocked real; its head is no commit.
        verdict(rv(8), f"verdict: #8 Fix review: blocked {H} harness: x", N[1], "2026-09-30T00:00:00Z")
        # PRs 10-13, unmerged, each on one side of a size cut: 149 lines and a binary file, 150 and a
        # binary file under blueprints/, 599, and 300 deleted plus 300 added. PR 9 ties PR 10's first verdict.
        h10 = mk(m1, {"docs/s10.md": lines(149), "docs/b.bin": "\0bin"}, "pr 10", "2026-10-05T01:00:00Z")
        h11 = mk(m1, {"blueprints/x.yaml": lines(150), "blueprints/x.bin": "\0bin"}, "pr 11", "2026-10-05T01:00:00Z")
        h12 = mk(m1, {"docs/s12.md": lines(599)}, "pr 12", "2026-10-05T01:00:00Z")
        h13 = mk(m1, {"docs/base.md": "".join(f"x{i}\n" for i in range(300))}, "pr 13", "2026-10-05T01:00:00Z")
        h14 = mk(m1, {"docs/s14.md": lines(145)}, "pr 14", "2026-10-05T01:00:00Z")
        verdict(rv(9), f"verdict: #9 Fix review: merge {H}", N[2], "2026-10-05T02:00:00Z")
        verdict(rv(10), f"verdict: #10 Fix review: blocked {h10} harness: x", N[2], "2026-10-05T02:00:00Z")
        s11 = verdict(rv(11), f"verdict: #11 Fix review: merge {h11} harness: a class on a merge", N[3], "2026-10-05T03:00:00Z")
        g("tag", f"archive/probe/rev-11-{N[3][:8]}", s11)
        g("update-ref", "refs/remotes/origin/probe/not-a-return", s11)
        g("update-ref", rv(12), mk(None, {"NOTE.md": "x"}, "note: a review-ref commit that is no verdict",
                                   "2026-10-05T03:30:00Z"))
        verdict(rv(12), f"verdict: #12 Fix review: merge {h12}", N[4], "2026-10-05T04:00:00Z")
        verdict(rv(13), f"verdict: #13 Fix review: merge {h13}", N[5], "2026-10-05T05:00:00Z")
        # PR 14's verdict commit carries no VERDICT.md (so no nonce).
        g("update-ref", rv(14), mk(None, {}, f"verdict: #14 Fix review: merge {h14}", "2026-10-05T06:00:00Z"))
        # main grows: PR 14 merged from fix/r1-res-pr with 10 lines the merge itself adds; an octopus
        # merge naming PR 10 (700 lines on its side x1); a two-parent merge whose subject holds a tab;
        # a one-parent commit subject-shaped like a PR merge (12).
        m6 = mk(f"{m5} {h14}", {"docs/s14.md": lines(145), "docs/resolution.md": lines(10)},
                "Merge pull request #14 from tvofi/fix/r1-res-pr", "2026-10-05T06:30:00Z")
        x1 = mk(m1, {"docs/oct.md": lines(700)}, "x1", "2026-10-05T01:00:00Z")
        x2 = mk(m1, {"docs/oct2.md": lines(1)}, "x2", "2026-10-05T01:00:00Z")
        m7 = mk(f"{m6} {x1} {x2}", {"docs/oct.md": lines(700), "docs/oct2.md": lines(1)},
                "Merge pull request #10 from tvofi/fix/octopus", "2026-10-05T07:00:00Z")
        y1 = mk(m1, {"docs/y1.md": lines(1)}, "y1", "2026-10-05T01:00:00Z")
        m8 = mk(f"{m7} {y1}", {"docs/y1.md": lines(1)}, "Merge branch\t'y1'", "2026-10-05T07:30:00Z")
        m9 = mk(m8, {"docs/z.md": lines(1)}, "Merge pull request #12 from tvofi/fix/one-parent", "2026-10-05T08:00:00Z")
        g("update-ref", "refs/heads/main", m9)
        fv = load(R, "origin")[0]
        check("bus-confirmed *-cloud id marks the verdict cloud",
              [v["reviewer"] for v in fv if v["pr"] == 7] == ["cloud"])
        check("as of: --tree resolves to its first-parent commit (m1), never side-branch c2 dated nearer T",
              as_of(R, "main", when("2026-10-02T12:00Z")) == m1)
        f4 = pr_facts(R, "main", f"refs/remotes/origin/roster:{RP}", fv, when("2026-10-04T00:00Z"))
        f6 = pr_facts(R, "main", f"refs/remotes/origin/roster:{RP}", fv, when("2026-10-06T00:00Z"))
        fb = pr_facts(R, "main", f"refs/remotes/origin/roster:{RP}", fv, when("2026-10-02T12:00Z"))
        check("origin: a group listing issues is finding, one listing none is group",
              (f4[5]["origin"], f4[6]["origin"]) == ("finding", "group"))
        check("fixer: the joined group's model.fixer, opus for 5 and sonnet for 6",
              (f4[5]["fixer"], f4[6]["fixer"]) == ("opus", "sonnet"))
        check("size: merged PR 5 reads its merge diff (160 lines, M<600); unmerged 6 its verdict head (20, S<150)",
              (f4[5]["size"], f4[6]["size"]) == ("M<600", "S<150"))
        check("product: 5 touches custom_components/, 6 only docs/",
              (f4[5]["product"], f4[6]["product"]) == (True, False))
        check("as of: a verdict after T moves no fact (6's later head is product, read only after it)",
              f6[6]["product"] is True and f4[6]["product"] is False)
        check("size: PR 7 merged twice reads its newest merge (700 lines, L>=600)", f4[7]["size"] == "L>=600")
        check("join: merge branch fix/r1-fix-pr, -pr stripped, finds R1-FIX's resume.branch (fixer haiku)",
              f4[7]["fixer"] == "haiku")
        check("origin: a group listing fixes alone is finding", f4[7]["origin"] == "finding")
        check("as of: the roster is read at T (R1-FIND loses its issues after 10-05T12)",
              f6[5]["origin"] == "group")
        check("as of: --tree is read at T (before the merge, 5 reads its verdict head and no row)",
              (fb[5]["size"], fb[5]["origin"]) == ("S<150", "none"))

        # The sweep's cases (dev/audit/harnesses/r10_review_strength_mutants.py): each pins one
        # ordering, branch or threshold a one-node mutant moved while every check above passed.
        T6 = when("2026-10-06T00:00Z")
        RR = f"refs/remotes/origin/roster:{RP}"
        quiet = io.StringIO()
        with contextlib.redirect_stdout(quiet):
            f6 = pr_facts(R, "main", RR, fv, T6)
            f5 = pr_facts(R, "main", RR, fv, when("2026-10-05T01:00Z"))
            fn = pr_facts(R, "main", None, fv, T6)
        check("size: 149 lines plus a binary file is S<150, 150 plus one is M<600, 599 is M<600, 300+300 changed is L>=600",
              [f6[p]["size"] for p in (10, 11, 12, 13)] == ["S<150", "M<600", "M<600", "L>=600"])
        check("size: a head that is no commit is '?'", f6[8]["size"] == "?")
        check("product: blueprints/ is product (11), docs/ is not (12)", (f6[11]["product"], f6[12]["product"]) == (True, False))
        check("origin: a group listing findings alone is finding (8, R1-FINDS)", f6[8]["origin"] == "finding")
        check("merge join: only a two-parent PR merge is a merge; an octopus naming 10 and a one-parent 12 are not",
              (f6[10]["size"], f6[12]["size"]) == ("S<150", "M<600"))
        check("size: a merged PR reads its branch's diff, not the 10 lines its merge commit adds (14: 145, S<150)",
              f6[14]["size"] == "S<150")
        check("join: merge branch fix/r1-res-pr matches a resume.branch that keeps its -pr (14: fixer gpt)",
              f6[14]["fixer"] == "gpt")
        check("join: an empty resume.branch joins no unmerged PR (1: origin none)", f6[1]["origin"] == "none")
        check("as of: a verdict exactly at T is after T (6's 10-05T01 head is not read at 10-05T01)",
              f5[6]["product"] is False)
        check("no roster: every origin is none, the fixer none, and the roster prints '-'",
              {x["origin"] for x in fn.values()} == {"none"} and {x["fixer"] for x in fn.values()} == {"none"}
              and quiet.getvalue().splitlines()[2] == f"facts as of 2026-10-06T00:00Z: tree {m9[:12]} roster -")
        check("facts print the tree and roster resolved at T, 12 hex each",
              quiet.getvalue().splitlines()[0]
              == f"facts as of 2026-10-06T00:00Z: tree {m9[:12]} roster {r2[:12]}")
        try:
            pr_facts(R, "main", "refs/remotes/origin/roster:missing.json", fv, T6)
            check("a roster path that is not in the roster ref refuses", False)
        except subprocess.CalledProcessError:
            check("a roster path that is not in the roster ref refuses", True)
        try:
            as_of(R, "main", when("2000-01-01T00:00Z"))
            check("as of: a ref with no commit at or before T refuses", False)
        except SystemExit as exc:
            check("as of: a ref with no commit at or before T refuses", "has no commit" in str(exc))
        vv = {(v["pr"], v["kind"]): v for v in fv}
        check("cloud: an archive/probe tag marks the verdict cloud (11)", vv[(11, "merge")]["reviewer"] == "cloud")
        check("real: a class word on a MERGE verdict is never a real block (11)", vv[(11, "merge")]["real"] is False)
        check("a verdict commit without VERDICT.md is still read (14, no nonce)", (14, "merge") in vv)
        check("a review-ref commit that is no verdict and a non-return probe ref leave the outside row alone",
              len(load(R, "origin")[1]) == 1)
        check("window: [from, until) includes a verdict exactly at from (3's block at 10-02T01)",
              tally(vlist, when("2026-10-02T01:00Z"), c, lambda v: "all")["all"]["real"] == 1)
        tz = os.environ.get("TZ")
        os.environ["TZ"] = "EST+5"
        time.tzset()
        try:
            check("a Z stamp is UTC whatever the local zone", when("2026-10-01T00:00Z").hour == 0)
        finally:
            os.environ.pop("TZ") if tz is None else os.environ.__setitem__("TZ", tz)
            time.tzset()
        study = (ROOT / "dev/audit/rounds/round10/D13/yield-probe.md").read_text()
        listed = re.search(r"^- The real-catch list: (.*?)\.$", study, re.M | re.S)
        check("REAL_CATCH is the study record's real-catch list, word for word",
              listed is not None and set(re.findall(r"`([^`]+)`", listed[1])) == set(REAL_CATCH))
        _self_test_main(R, d, m9, r2, RP, check)
        d0 = parser().parse_args([])
        check("defaults: --repo is the checkout the tool runs from, --tree origin/main, --remote origin",
              (d0.repo, d0.tree, d0.remote) == (str(ROOT), "origin/main", "origin"))
        check("first-pass: a PR whose first verdict precedes the window is no first pass in it (6's merge alone)",
              tally(fv, when("2026-10-05T00:30Z"), when("2026-10-05T01:30Z"), lambda v: "all")["all"]["first"] == [])
        check("defaults: --remote is the option's name", parser().parse_args(["--remote", "up"]).remote == "up")
        check("tally: a verdict outside the window keys no row (10-05T03:30..04:30 holds 12's merge alone)",
              set(tally(fv, when("2026-10-05T03:30Z"), when("2026-10-05T04:30Z"),
                        lambda v: stratum("class", v, {}))) == {"(merge)"})
        _self_test_seams(R, g, mk, verdict, lines, m1, RP, r2, check)
        _self_test_vocabulary(R, g, verdict, check)
    print(f"review_strength self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def _self_test_vocabulary(R: Path, g, verdict, check) -> None:
    """The archived bus (prune_refs.py's tags) and the vocabulary read from the wave script."""
    H = "b" * 40
    n = len(load(R, "origin")[0])
    s40 = verdict("refs/tags/archive/review/40", f"verdict: #40 Fix review: blocked {H} defect: x",
                  "40" * 16, "2026-08-01T00:00:00Z")
    vs = g("commit-tree", g("write-tree"), "-m", f"verdict: #40\n\nbus-confirmed: cloud-40 (review/40 at {s40})")
    g("update-ref", "refs/tags/archive/verdict/40", vs)
    got = [v for v in load(R, "origin")[0] if v["pr"] == 40]
    check("a review ref archived as archive/review/<pr> is still read, once",
          len(got) == 1 and len(load(R, "origin")[0]) == n + 1)
    check("its archive/verdict/<pr> copy's cloud id still marks it cloud", got[0]["reviewer"] == "cloud")
    # Decoys before the literal, each read by a looser extractor: another *_CLASSES list, the name in a
    # comment and after a non-`const` word; inside it, a comment's apostrophe, a word opening with a
    # digit, and words holding each digit.
    decoy = ("Konst VERDICT_CLASSES = ['k1']\n// VERDICT_CLASSES = ['c1']\nconst ROOT_CLASSES = ['r1']\n"
             "const VERDICT_CLASSES = [\n  // the wave's own words, never '9lives'\n  'r0', 'x5', 'b9', 'a-b',\n]\n")
    check("verdict_classes reads only the VERDICT_CLASSES literal, and only its quoted words opening with a letter",
          verdict_classes(decoy) == ("r0", "x5", "b9", "a-b"))
    # Eight and six words each, given out of order: a set's iteration order matching sorted order by chance
    # is then about 1 in 40320 and 1 in 720, where two words match it every other run.
    letters = "abcdefghijklmn"
    check("class sets are sorted", class_sets(tuple(reversed(letters)), frozenset("hgfedcbazy"))
          == {"taught real": list("abcdefgh"), "taught bookkeeping": list("ijklmn"), "untaught real": ["y", "z"]})
    check("route crosses with another stratum (kind+route)",
          stratum("kind+route", dict(kind="blocked", cls="conflict", reviewer="local"), {}, ("conflict",))
          == "local+conflict")
    # A bus-confirmed copy or a verdict commit under any other archive family is not the bus.
    s41 = verdict("refs/tags/archive/handoff/41", f"verdict: #41 Fix review: merge {H}", "41" * 16, "2026-08-01T00:00:00Z")
    s43 = verdict("refs/remotes/origin/review/43", f"verdict: #43 Fix review: merge {H}", "43" * 16, "2026-08-01T00:00:00Z")
    g("update-ref", "refs/tags/archive/other/43",
      g("commit-tree", g("write-tree"), "-m", f"verdict: #43\n\nbus-confirmed: cloud-43 (review/43 at {s43})"))
    got = {v["pr"]: v for v in load(R, "origin")[0]}
    check("a verdict commit under another archive family (archive/handoff/) is not read", 41 not in got and s41)
    check("a bus-confirmed copy under another archive family (archive/other/) marks nothing cloud",
          got[43]["reviewer"] == "local")
    try:
        verdict_classes("const VERDICT_RE = 1\n")
        check("a wave script without VERDICT_CLASSES refuses", False)
    except SystemExit as e:
        check("a wave script without VERDICT_CLASSES refuses", "no VERDICT_CLASSES" in str(e))
    live = verdict_classes((ROOT / WAVE_SCRIPT).read_text())
    sets = class_sets(live, REAL_CATCH)
    check("the live vocabulary is read: harness and conflict are taught, defect is not",
          {"harness", "conflict"} <= set(live) and "defect" not in live)
    check("class sets: taught real and untaught real are REAL_CATCH; taught bookkeeping shares no word with it",
          set(sets["taught real"]) | set(sets["untaught real"]) == REAL_CATCH
          and not set(sets["taught bookkeeping"]) & REAL_CATCH and "conflict" in sets["taught bookkeeping"])
    route = lambda kind, cls: stratum("route", dict(kind=kind, cls=cls), {}, live)
    check("route: a taught word is itself, an untaught one other, a merge (merge)",
          (route("blocked", "conflict"), route("blocked", "defect"), route("merge", "harness")) == ("conflict", "other", "(merge)"))


def _self_test_seams(R: Path, g, mk, verdict, lines, m1: str, RP: str, r2: str, check) -> None:
    """PRs 16-18: the literal, regex, ref-scope and merge-walk seams the mutation sweep found unpinned."""
    rv = lambda pr: f"refs/remotes/origin/review/{pr}"
    N16, N17 = "09abcdef1234567876543210fedcba98", "90fedcba" * 4
    # PR 16: 145 lines plus one each in files a prefix cut would wrongly read: the delivery
    # exclusion and the product prefixes all hold at their trailing '/', and tests/ and tools/
    # are top-level directories outside the product (150 lines, M<600, not product).
    h16 = mk(m1, {"docs/s16.md": lines(145), "dev/programme/delivery.md": lines(1), "tests/t16.py": lines(1),
                  "tools/t16.py": lines(1), "custom_components.md": lines(1), "blueprints.md": lines(1)},
             "pr 16", "2026-10-05T01:00:00Z")
    # Its VERDICT.md quotes another nonce mid-line before its own; its nonce holds a 0 and a 9, and
    # its first 8 hex recur nowhere in it, so only nonce[:8] matches the probe ref.
    s16 = verdict(rv(16), f"verdict: #16 Fix review: merge {h16}", N16, "2026-10-05T09:00:00Z",
                  pre=f"quoting bus-nonce: {'1' * 32}\n")
    g("update-ref", f"refs/remotes/origin/probe/rev-16-{N16[:8]}", s16)
    # PR 17: local; every decoy below names it but sits outside the shape or scope the tool reads.
    h17 = mk(m1, {"docs/s17b.md": lines(5)}, "pr 17", "2026-10-05T01:00:00Z")
    s17 = verdict(rv(17), f"verdict: #17 Fix review: merge {h17}", N17, "2026-10-05T09:30:00Z")
    verdict(rv(17), f"verdict: #17 Fix review: blocked {h17} harness: after", N17, "2026-10-05T11:00:00Z")
    vs = g("commit-tree", g("write-tree"), "-m",
           f"verdict: #17\n\nbus-confirmed: clou9-xcloud (review/17 at {s17})\n"
           f"quoted bus-confirmed: cloud-17 (review/17 at {s17})")
    g("update-ref", "refs/remotes/origin/verdict/17", vs)
    for decoy in (f"refs/remotes/origin/probe/dev-17-{N17[:8]}", f"refs/remotes/origin/probe/rev-17-{N17[:8]}-old",
                  f"refs/tags/archive/other/rev-17-{N17[:8]}"):
        g("update-ref", decoy, s17)
    # Review-ref commits outside the grammar's start: a prefixed subject is no verdict and not outside;
    # one that opens with the prefix but matches the shape only later is outside, printed cut at 100.
    g("update-ref", rv(19), mk(None, {}, f"re: verdict: #19 Fix review: merge {'c' * 40}", "2026-10-05T09:40:00Z"))
    long = f"verdict: #19 Fix review: PASS, see verdict: #19 Fix review: merge {'d' * 40} for the {'x' * 20}"
    g("update-ref", rv(119), mk(None, {}, long, "2026-10-05T09:41:00Z"))
    g("update-ref", rv(219), mk(None, {}, "verdict: #19 Fix reviewer: no verdict", "2026-10-05T09:42:00Z"))
    # PR 18: merged into main under a subject holding a tab (700 lines, L>=600).
    h18 = mk(m1, {"docs/s18.md": lines(700)}, "pr 18", "2026-10-05T01:00:00Z")
    s18 = verdict(rv(18), f"verdict: #18 Fix review: merge {h18}", "18" * 16, "2026-10-05T09:45:00Z")
    # A remote ref outside review/, verdict/ and probe/: a verdict-shaped subject for 18, a cloud
    # confirmation for 18's merge, and a probe-shaped name for 17.
    g("update-ref", f"refs/remotes/origin/elsewhere/rev-17-{N17[:8]}",
      g("commit-tree", g("write-tree"), "-m",
        f"verdict: #18 Fix review: blocked {'b' * 40} harness: x\n\nbus-confirmed: cloud-18 (review/18 at {s18})"))
    # PR 20: a verdict commit authored a month before it was committed (a rebased verdict); the
    # window reads committer time.
    g("update-ref", rv(20), g("commit-tree", g("hash-object", "-t", "tree", "-w", os.devnull), "-m",
                              f"verdict: #20 Fix review: merge {'e' * 40}",
                              e={"GIT_COMMITTER_DATE": "2026-10-05T09:47:00Z", "GIT_AUTHOR_DATE": "2026-09-05T09:47:00Z"}))
    # PR 21: a class is the word up to its own colon: a block whose first word has none names no
    # class, and one whose word is followed by a second colon names the word alone.
    verdict(rv(21), f"verdict: #21 Fix review: blocked {'e' * 40} conflict also harness: x", "21" * 16,
            "2026-10-05T09:51:00Z")
    verdict(rv(21), f"verdict: #21 Fix review: blocked {'e' * 40} harness:x: y", "21" * 16, "2026-10-05T09:52:00Z")
    # PR 22: a nonce with no space after its colon, returned by a probe; PR 23: a cloud confirmation
    # with no space after its colon.
    N22 = "22" * 16
    s22 = mk(None, {"VERDICT.md": f"x\n\nbus-nonce:{N22}\n"}, f"verdict: #22 Fix review: merge {'e' * 40}",
             "2026-10-05T09:53:00Z")
    g("update-ref", rv(22), s22)
    g("update-ref", f"refs/remotes/origin/probe/rev-22-{N22[:8]}", s22)
    s23 = verdict(rv(23), f"verdict: #23 Fix review: merge {'e' * 40}", "23" * 16, "2026-10-05T09:54:00Z")
    g("update-ref", "refs/remotes/origin/verdict/23",
      g("commit-tree", g("write-tree"), "-m", f"verdict: #23\n\nbus-confirmed:cloud-23 (review/23 at {s23})"))
    tip = g("rev-parse", "main")
    # main: rows naming groups whose letters hold a 0 and a 9 at every position the group regex
    # reads, a digit inside the ranges at each (R1-555), and a group holding three dashes as the
    # real bus's do; a merge of 17 reached only through a side branch; 18's merge; and a two-parent commit
    # whose subject names 16's merge after a prefix.
    m10 = mk(tip, {"dev/programme/delivery/16.md": "| 16 | R1-0909 |\n",
                   "dev/programme/delivery/17.md": "| 17 | R1-9090 |\n",
                   "dev/programme/delivery/18.md": "| 18 | R10-FLOW-YIELD-PROBE |\n",
                   "dev/programme/delivery/20.md": "| 20 | R1-555 |\n"}, "rows 16 17 18 20",
             "2026-10-05T09:50:00Z")
    side1 = mk(m1, {"docs/s17.md": lines(700)}, "side", "2026-10-05T01:00:00Z")
    side = mk(f"{m1} {side1}", {"docs/s17.md": lines(700)}, "Merge pull request #17 from tvofi/fix/side",
              "2026-10-05T02:00:00Z")
    m11 = mk(f"{m10} {side}", {"docs/s17.md": lines(700)}, "Merge branch 'side'", "2026-10-05T10:00:00Z")
    m12 = mk(f"{m11} {h18}", {"docs/s18.md": lines(700)}, "Merge pull request #18 from tvofi/fix/r18\tx",
             "2026-10-05T10:10:00Z")
    y16 = mk(m1, {"docs/y16.md": lines(700)}, "y16", "2026-10-05T01:00:00Z")
    m13 = mk(f"{m12} {y16}", {"docs/y16.md": lines(700)}, 'Revert "Merge pull request #16 from tvofi/x"',
             "2026-10-05T10:20:00Z")
    g("update-ref", "refs/heads/main", m13)
    grp = lambda name, fixer: dict(group=name, issues=["i"], model=dict(fixer=fixer))
    old = json.loads(g("show", f"{r2}:{RP}"))["groups"]
    r3 = mk(r2, {RP: json.dumps(dict(groups=[*old, grp("R1-0909", "g0"), grp("R1-9090", "g9"),
                                             grp("R10-FLOW", "cut"), grp("R10-FLOW-YIELD-PROBE", "dashes"),
                                             grp("R1-555", "g5")]))},
            "roster: digit groups", "2026-10-05T13:00:00Z")
    g("update-ref", "refs/remotes/origin/roster", r3)
    vl, outside = load(R, "origin")
    with contextlib.redirect_stdout(io.StringIO()):
        f = pr_facts(R, "main", f"refs/remotes/origin/roster:{RP}", vl, when("2026-10-06T00:00Z"))
    kind = {v["pr"]: v["reviewer"] for v in vl if v["pr"] in (16, 17, 18, 22, 23) and v["kind"] == "merge"}
    check("size: delivery rows are excluded at their '/', other dev/programme/ files count (16: 150, M<600)",
          f[16]["size"] == "M<600")
    check("product: tests/, tools/, custom_components.md and blueprints.md are not under the product prefixes (16)",
          f[16]["product"] is False)
    check("cloud: the nonce is the line-start bus-nonce, read in full hex, matched to a probe ref (16)",
          kind[16] == "cloud")
    check("cloud: no decoy marks 17 (id clou9-xcloud, a mid-line confirmation, dev-/-old/archive-other "
          "probe names, a ref outside verdict/ and probe/)", kind[17] == "local")
    check("only review/ and verdict/ refs are read: the ref outside them adds no verdict for 18 and no cloud id",
          [v["kind"] for v in vl if v["pr"] == 18] == ["merge"] and kind[18] == "local")
    check("a subject that only CONTAINS the grammar is no verdict and not outside (19)",
          all(v["pr"] != 19 for v in vl) and not any(o.startswith("re:") for o in outside))
    check("outside: the prefix 'Fix review:' exactly, and the shape matched from the start (19 twice)",
          sorted(outside) == sorted([long, "verdict: #4 Fix review: PASS\tmerge " + "a" * 40]))
    check("a verdict counts at its committer time, not its author time (20: in 10-05T09:46..09:48)",
          tally(vl, when("2026-10-05T09:46Z"), when("2026-10-05T09:48Z"), lambda v: "all")["all"]["prs"] == {20})
    check("merge walk: first-parent only; 17's side-branch merge is not its merge (17: 5 lines, S<150)",
          f[17]["size"] == "S<150")
    check("merge subject: a tab inside it leaves the parents field whole (18 merged: 700, L>=600)",
          f[18]["size"] == "L>=600")
    check("merge subject: a two-parent commit naming a PR merge after a prefix is no merge (16 stays M<600)",
          f[16]["size"] == "M<600")
    check("group regex: 0 and 9 at every position (16 R1-0909 fixer g0, 17 R1-9090 fixer g9)",
          (f[16]["fixer"], f[17]["fixer"]) == ("g0", "g9"))
    check("group regex: a digit inside the ranges at every position (20 R1-555 fixer g5)", f[20]["fixer"] == "g5")
    check("cloud: a nonce and a confirmation with no space after the colon are read (22, 23)",
          (kind[22], kind[23]) == ("cloud", "cloud"))
    check("class: the word up to its own colon, none when the first word has none (21: '' and harness)",
          sorted(v["cls"] for v in vl if v["pr"] == 21) == ["", "harness"])
    check("group regex: a group's inner dashes are part of it (18 R10-FLOW-YIELD-PROBE, not R10-FLOW)",
          f[18]["fixer"] == "dashes")
    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        main(["--repo", str(R), "--tree", "main", "--window", "A=2026-10-05T00:00Z..2026-10-06T00:00Z"])
    check("main prints the bus line once and each outside subject cut at 100",
          text.getvalue().count("verdicts on the bus:") == 1 and f"  outside: {long[:100]}\n" in text.getvalue())


def _self_test_main(R: Path, d: str, tip: str, roster: str, path: str, check) -> None:
    """main() end to end over self_test's fixture: its printed rows, each stratum alone, refusals, --fetch."""
    err = io.StringIO()

    def run(*argv: str) -> tuple[int, str]:
        out = io.StringIO()
        err.truncate(0)
        err.seek(0)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = main(["--repo", d, "--tree", "main", *argv])
            except SystemExit as exc:
                rc = exc.code
        return rc, out.getvalue()

    wins = ("--window", "E=2026-09-29T00:00Z..2026-10-02T00:00Z", "--window", "L=2026-10-02T00:00Z..2026-10-06T00:00Z")
    rr = ("--roster", f"refs/remotes/origin/roster:{path}")
    rc, text = run(*wins, *(x for s in STRATA for x in ("--by", s)), "--by", "kind+origin", *rr)
    expected = (
        f"facts as of 2026-10-06T00:00Z: tree {tip[:12]} roster {roster[:12]}\n"
        "verdicts on the bus: 18; outside the grammar: 1\n"
        "  outside: verdict: #4 Fix review: PASS\tmerge aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
        "taught real: harness\n"
        "taught bookkeeping: carry-missing\n"
        "untaught real: architecture-unsound, class-open, defect, figures-false, metric-gamed, mutant-survives, mutation, "
        "mutation-survivor, mutation-untriaged, mutation-vacuous, policy-regression, product-tradeoff-regression, "
        "test-vacuous, vacuous-check, vacuous-test\n"
        "## all\n"
        "  all                      E      PRs 3 verdicts 7 real 2 (0.67/PR) book 2 (0.67/PR) incidence 2/3 (0.67) first-pass 0/3\n"
        "  all                      L      PRs 10 verdicts 11 real 3 (0.30/PR) book 0 (0.00/PR) incidence 3/10 (0.30) first-pass 7/10\n"
        "## kind\n"
        "  cloud                    E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/1\n"
        "  cloud                    L      PRs 3 verdicts 3 real 1 (0.33/PR) book 0 (0.00/PR) incidence 1/3 (0.33) first-pass 2/3\n"
        "  local                    E      PRs 3 verdicts 6 real 2 (0.67/PR) book 1 (0.33/PR) incidence 2/3 (0.67) first-pass 0/2\n"
        "  local                    L      PRs 7 verdicts 8 real 2 (0.29/PR) book 0 (0.00/PR) incidence 2/7 (0.29) first-pass 5/7\n"
        "## class\n"
        "  (merge)                  E      PRs 2 verdicts 3 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/2 (0.00) first-pass 0/0\n"
        "  (merge)                  L      PRs 7 verdicts 7 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/7 (0.00) first-pass 6/6\n"
        "  (no class)               E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/0\n"
        "  (no class)               L      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  carry-missing            E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/1\n"
        "  carry-missing            L      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  harness                  E      PRs 2 verdicts 2 real 2 (1.00/PR) book 0 (0.00/PR) incidence 2/2 (1.00) first-pass 0/2\n"
        "  harness                  L      PRs 3 verdicts 3 real 2 (0.67/PR) book 0 (0.00/PR) incidence 2/3 (0.67) first-pass 1/3\n"
        "  mutation-survivor        E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  mutation-survivor        L      PRs 1 verdicts 1 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        # route: PR 11's merge verdict naming a class is a merge (the class stratum keys it harness), the
        # classless block and the untaught mutation-survivor route to other, which keeps its realness.
        "## route\n"
        "  (merge)                  E      PRs 2 verdicts 3 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/2 (0.00) first-pass 0/0\n"
        "  (merge)                  L      PRs 8 verdicts 8 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/8 (0.00) first-pass 7/7\n"
        "  carry-missing            E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/1\n"
        "  carry-missing            L      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  harness                  E      PRs 2 verdicts 2 real 2 (1.00/PR) book 0 (0.00/PR) incidence 2/2 (1.00) first-pass 0/2\n"
        "  harness                  L      PRs 2 verdicts 2 real 2 (1.00/PR) book 0 (0.00/PR) incidence 2/2 (1.00) first-pass 0/2\n"
        "  other                    E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/0\n"
        "  other                    L      PRs 1 verdicts 1 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        "## prior-merge\n"
        "  after-a-merge-verdict    E      PRs 2 verdicts 2 real 0 (0.00/PR) book 1 (0.50/PR) incidence 0/2 (0.00) first-pass 0/0\n"
        "  after-a-merge-verdict    L      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  no-merge-yet             E      PRs 3 verdicts 5 real 2 (0.67/PR) book 1 (0.33/PR) incidence 2/3 (0.67) first-pass 0/3\n"
        "  no-merge-yet             L      PRs 10 verdicts 11 real 3 (0.30/PR) book 0 (0.00/PR) incidence 3/10 (0.30) first-pass 7/10\n"
        "## origin\n"
        "  finding                  E      PRs 1 verdicts 1 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        "  finding                  L      PRs 1 verdicts 1 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/1 (0.00) first-pass 1/1\n"
        "  group                    E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  group                    L      PRs 3 verdicts 4 real 1 (0.33/PR) book 0 (0.00/PR) incidence 1/3 (0.33) first-pass 2/3\n"
        "  none                     E      PRs 2 verdicts 6 real 1 (0.50/PR) book 2 (1.00/PR) incidence 1/2 (0.50) first-pass 0/2\n"
        "  none                     L      PRs 6 verdicts 6 real 2 (0.33/PR) book 0 (0.00/PR) incidence 2/6 (0.33) first-pass 4/6\n"
        "## size\n"
        "  ?                        E      PRs 3 verdicts 7 real 2 (0.67/PR) book 2 (0.67/PR) incidence 2/3 (0.67) first-pass 0/3\n"
        "  ?                        L      PRs 2 verdicts 2 real 1 (0.50/PR) book 0 (0.00/PR) incidence 1/2 (0.50) first-pass 1/2\n"
        "  L>=600                   E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  L>=600                   L      PRs 2 verdicts 2 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/2 (0.00) first-pass 2/2\n"
        "  M<600                    E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  M<600                    L      PRs 3 verdicts 3 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/3 (0.00) first-pass 3/3\n"
        "  S<150                    E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  S<150                    L      PRs 3 verdicts 4 real 2 (0.67/PR) book 0 (0.00/PR) incidence 2/3 (0.67) first-pass 1/3\n"
        "## product\n"
        "  False                    E      PRs 3 verdicts 7 real 2 (0.67/PR) book 2 (0.67/PR) incidence 2/3 (0.67) first-pass 0/3\n"
        "  False                    L      PRs 7 verdicts 7 real 2 (0.29/PR) book 0 (0.00/PR) incidence 2/7 (0.29) first-pass 5/7\n"
        "  True                     E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  True                     L      PRs 3 verdicts 4 real 1 (0.33/PR) book 0 (0.00/PR) incidence 1/3 (0.33) first-pass 2/3\n"
        "## fixer\n"
        "  gpt                      E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  gpt                      L      PRs 1 verdicts 1 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/1 (0.00) first-pass 1/1\n"
        "  haiku                    E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  haiku                    L      PRs 1 verdicts 1 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/1 (0.00) first-pass 1/1\n"
        "  none                     E      PRs 2 verdicts 6 real 1 (0.50/PR) book 2 (1.00/PR) incidence 1/2 (0.50) first-pass 0/2\n"
        "  none                     L      PRs 6 verdicts 6 real 2 (0.33/PR) book 0 (0.00/PR) incidence 2/6 (0.33) first-pass 4/6\n"
        "  opus                     E      PRs 1 verdicts 1 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        "  opus                     L      PRs 1 verdicts 1 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/1 (0.00) first-pass 1/1\n"
        "  sonnet                   E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  sonnet                   L      PRs 1 verdicts 2 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        "## kind+origin\n"
        "  cloud+finding            E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  cloud+finding            L      PRs 1 verdicts 1 real 0 (0.00/PR) book 0 (0.00/PR) incidence 0/1 (0.00) first-pass 1/1\n"
        "  cloud+none               E      PRs 1 verdicts 1 real 0 (0.00/PR) book 1 (1.00/PR) incidence 0/1 (0.00) first-pass 0/1\n"
        "  cloud+none               L      PRs 2 verdicts 2 real 1 (0.50/PR) book 0 (0.00/PR) incidence 1/2 (0.50) first-pass 1/2\n"
        "  local+finding            E      PRs 1 verdicts 1 real 1 (1.00/PR) book 0 (0.00/PR) incidence 1/1 (1.00) first-pass 0/1\n"
        "  local+finding            L      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  local+group              E      PRs 0 verdicts 0 real 0 (-/PR) book 0 (-/PR) incidence 0/0 (-) first-pass 0/0\n"
        "  local+group              L      PRs 3 verdicts 4 real 1 (0.33/PR) book 0 (0.00/PR) incidence 1/3 (0.33) first-pass 2/3\n"
        "  local+none               E      PRs 2 verdicts 5 real 1 (0.50/PR) book 1 (0.50/PR) incidence 1/2 (0.50) first-pass 0/1\n"
        "  local+none               L      PRs 4 verdicts 4 real 1 (0.25/PR) book 0 (0.00/PR) incidence 1/4 (0.25) first-pass 3/4\n"
    )
    check("main: every row of the bundle over the fixture, as printed (hand-derived from the fixture's verdicts)",
          rc == 0 and text == expected)
    sections = dict(x.split("\n", 1) for x in text.split("## ")[1:])
    for s in STRATA:
        rc1, alone = run(*wins, "--by", s, *rr)
        check(f"main --by {s} alone prints the same {s} rows", rc1 == 0 and alone.split(f"## {s}\n")[-1] == sections[s])
    rc, text = run(*wins, "--real-extra", "zeta,carry-missing,omega,beta,kappa,delta")
    check("main --real-extra names the words, sorted, and moves PR 2's block to real (E: real 3, book 1)",
          text.startswith("REAL = the study's list + beta, carry-missing, delta, kappa, omega, zeta\n") and " E      PRs 3 verdicts 7 real 3 " in text
          and "book 1 (0.33/PR)" in text)
    check("main: a class set left empty prints '-' (carry-missing judged real leaves no taught bookkeeping word)",
          "\ntaught bookkeeping: -\n" in text)
    rc, text = run(*wins, "--by", "size", "--as-of", "2026-10-04T00:00Z")
    check("main --as-of takes the facts at T, not at the latest until; a PR first reviewed after T is its own row",
          text.startswith("facts as of 2026-10-04T00:00Z: ")
          and "  (unreviewed at T)        L      PRs 6 verdicts 6 real 1 " in text)
    rc, text = run(*wins, "--window", "A=2026-10-03T00:00Z..2026-10-05T00:00Z", "--by", "size")
    check("main: the facts default to the LATEST until of any window, not the last named's (A, 10-05)",
          text.startswith("facts as of 2026-10-06T00:00Z: "))
    check("main: no fact stratum asked, no facts taken (the bus line comes first)",
          run(*wins, "--by", "kind")[1].startswith("verdicts on the bus: "))
    for why, argv in (("no window", ()), ("an unknown stratum", (*wins, "--by", "nope")),
                      ("origin without --roster", (*wins, "--by", "kind+origin")),
                      ("fixer without --roster", (*wins, "--by", "fixer"))):
        check(f"main refuses {why} (exit 2)", run(*argv)[0] == 2)
    run(*wins, "--by", "nope+aa+zz+mm+bb+kk")
    check("main names the unknown strata sorted",
          "unknown stratum ['aa', 'bb', 'kk', 'mm', 'nope', 'zz']" in err.getvalue())
    run(*wins, "--by", "nope+origin")
    check("main: an unknown stratum is refused before a missing --roster", "unknown stratum ['nope']" in err.getvalue())
    # --fetch reads the remote's refs/heads/{review,probe,verdict}/* into refs/remotes/<remote>/*/*, by
    # its own refspecs (the remote carries no configured fetch refspec), forced, with every tag.
    from throwaway_git import throwaway_git_env, throwaway_git_init
    env = throwaway_git_env()
    g = lambda *x, at=d: subprocess.run(["git", "-C", at, *x], capture_output=True, text=True, check=True,
                                        env=env).stdout.strip()
    up = os.path.join(d, ".git", "upstream.git")
    throwaway_git_init(up, "-q", "--bare")
    g("config", "remote.origin.url", up)
    s13, s12 = g("rev-parse", "refs/remotes/origin/review/13"), g("rev-parse", "refs/remotes/origin/review/12")
    s5, nonce = g("rev-parse", "refs/remotes/origin/review/5"), NONCE_RE.search(g("show", f"{s13}:VERDICT.md"))[1]
    vc = g("commit-tree", g("rev-parse", f"{s12}^{{tree}}"), "-m",
           f"verdict: #12\n\nbus-confirmed: cloud-12 (review/12 at {s12})")
    g("push", "-q", up, f"{s13}:refs/heads/review/15", f"{s12}:refs/heads/review/12",
      f"{s13}:refs/heads/probe/rev-13-{nonce[:8]}", f"{vc}:refs/heads/verdict/12")
    # The tag names a commit only the remote holds, so no history fetched carries it: only --tags brings it.
    only = g("commit-tree", g("hash-object", "-t", "tree", "-w", os.devnull, at=up), "-m", "remote only", at=up)
    g("update-ref", f"refs/tags/archive/probe/rev-5-{NONCE_RE.search(g('show', f'{s5}:VERDICT.md'))[1][:8]}",
      only, at=up)
    g("update-ref", "-d", "refs/remotes/origin/review/13")
    # review/12 locally points at 13's verdict, which its remote tip does not descend from: only a forced
    # fetch moves it back.
    g("update-ref", "refs/remotes/origin/review/12", s13)
    check("main --fetch refuses a missing window, an unknown stratum and a missing --roster before it fetches",
          run("--fetch")[0] == 2 and run(*wins, "--fetch", "--by", "nope")[0] == 2
          and run(*wins, "--fetch", "--by", "origin")[0] == 2
          and not g("for-each-ref", "refs/remotes/origin/review/15"))
    before = run(*wins, "--by", "kind")[1]
    after = run(*wins, "--by", "kind", "--fetch")[1]
    check("main --fetch reads the remote's review, probe and verdict refs and its tags (13 back; 12, 13 and 5 now cloud)",
          "verdicts on the bus: 17;" in before and "verdicts on the bus: 18;" in after
          and "  cloud                    L      PRs 3 " in before and "  cloud                    L      PRs 6 " in after)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
