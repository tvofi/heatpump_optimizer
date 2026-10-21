#!/usr/bin/env python3
"""Review strength from the verdict bus: real-catch blocks per reviewed PR.

    python3 tools/audit/seat/review_strength.py --self-test
    python3 tools/audit/seat/review_strength.py [--fetch] \\
        --window E=2026-10-15T12:37Z..2026-10-19T14:50Z \\
        --window L=2026-10-19T14:50Z..2026-10-21T14:50Z \\
        [--by kind|class|prior-merge|origin|size|product|fixer[+...] ...] \\
        [--roster REF:PATH] [--guardrail N --p0 P]

R10-FLOW-YIELD-PROBE (owner ruling R13). Everything is read over git: no
REST call, so no rate limit and no 403. `--fetch` first fetches
`refs/heads/{review,verdict,probe}/*` and the tags from the remote.

THE RULE. A verdict is a commit on a `review/<pr>` ref whose subject matches
`verdict: #<pr> Fix review: merge|blocked <40hex>`; a blocked one carries
`<class>:` after the sha. A commit reachable from several review refs counts
once. A window holds the verdicts whose COMMITTER time falls in
[from, until); its reviewed PRs are the distinct PRs of those verdicts.
A blocked verdict is REAL when its class is in REAL_CATCH (the flow study's
"Guardrail baselines" list) or in `--real-extra`, otherwise BOOKKEEPING. A subject that names the
grammar's prefix but not its shape is printed on its own `outside` row,
never folded in. Each subject names ONE class, so a verdict blocked for two
reasons counts once, under the class its reviewer wrote first.

    real per PR = real blocks / reviewed PRs  (one PR blocked in 6 rounds
                  counts 6, so a few long PRs dominate it)
    incidence   = reviewed PRs with >= 1 real block / reviewed PRs

STRATA (`--by`). kind: `cloud` when the verdict's bus nonce prefix names a
probe return, a ref `probe/rev-<pr>-<nonce[:8]>` or tag
`archive/probe/rev-<pr>-<nonce[:8]>` (cloud_relay.sh's return path), or its
`verdict/<pr>` copy's `bus-confirmed:` id starts with `cloud` or ends in
`-cloud`; `local` otherwise. prior-merge: the PR already had a `merge`
verdict on the bus (a re-review a carry could replace). class: the raw class
word. origin, fixer: from the roster file at `--roster REF:PATH`, joined on
the first `R<n>-...` group token of `dev/programme/delivery/<pr>.md` at
`--tree`, else on the roster `resume.branch`; origin is `finding` when the
group lists issues, findings or fixes, `group` when it lists none, `none`
with no group. size, product: the PR's diff, `--tree`'s first-parent merge of
it when there is one, else its last verdict's head against its merge base
with `--tree`, delivery rows excluded; product means it touches
`custom_components/` or `blueprints/`. `a+b` crosses two strata.
first-pass m/n: of the PRs whose FIRST bus verdict falls in the window, the
m whose first verdict is `merge`.

GUARDRAIL (`--guardrail N --p0 P`). The last N reviewed PRs by first verdict
time before the last window's `until`, their incidence k/N, and the binomial
P(X <= k | N, P). It prints `would-trip` when that is below 0.05, else `ok`;
it decides nothing (R13: the guardrail reports and trips on nothing until
the owner adopts a threshold).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

REAL_CATCH = frozenset({
    "harness", "class-open", "test-vacuous", "vacuous-test", "vacuous-check",
    "mutation-vacuous", "mutant-survives", "mutation-survivor",
    "mutation-untriaged", "mutation", "architecture-unsound", "metric-gamed",
    "defect", "product-tradeoff-regression", "policy-regression",
    "figures-false"})
VERDICT_RE = re.compile(
    r"^verdict: #(\d+) Fix review: (merge|blocked) ([0-9a-f]{40})(?: ([^\s:]+):)?")
PREFIX_RE = re.compile(r"^verdict: #(\d+) Fix review:")
NONCE_RE = re.compile(r"^bus-nonce:\s*([0-9a-f]{32})", re.M)
PROBE_RE = re.compile(r"rev-(\d+)-([0-9a-f]{8})$")
CONFIRMED_RE = re.compile(r"^bus-confirmed:\s*(\S+) \(review/\d+ at ([0-9a-f]{40})\)", re.M)
GROUP_RE = re.compile(r"\b(R\d+-[A-Z0-9][A-Z0-9-]*[A-Z0-9])\b")
MERGE_RE = re.compile(r"^Merge pull request #(\d+) from \S+?/(\S+)")
ALPHA = 0.05
STRATA = ("kind", "class", "prior-merge", "origin", "size", "product", "fixer")
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
    for r in refs(repo, f"refs/remotes/{remote}/verdict/"):
        for body in git(repo, "log", "--format=%B%x00", r).split("\0"):
            m = CONFIRMED_RE.search(body)
            if m:
                confirmed[m[2]] = m[1]
    seen, out, outside = set(), [], []
    for r in refs(repo, f"refs/remotes/{remote}/review/"):
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
    out.sort(key=lambda v: (v["t"], v["pr"]))
    merged = set()
    for v in out:
        v["prior_merge"] = v["pr"] in merged
        if v["kind"] == "merge":
            merged.add(v["pr"])
    return out, outside


def pr_facts(repo: Path, tree: str, roster: str | None, verdicts: list[dict]) -> dict[int, dict]:
    """origin, fixer, size and product per PR (the strata needing more than the bus)."""
    groups = {}
    if roster:
        ref, path = roster.split(":", 1)
        for g in json.loads(git(repo, "show", f"{ref}:{path}"))["groups"]:
            groups[g["group"]] = g
    merges = {}
    for line in git(repo, "log", "--first-parent", "--format=%H%x09%P%x09%s", tree).splitlines():
        sha, parents, subj = line.split("\t", 2)
        m = MERGE_RE.match(subj)
        if m and len(parents.split()) == 2 and int(m[1]) not in merges:
            merges[int(m[1])] = (sha, parents.split()[1], m[2])
    last = {v["pr"]: v["head"] for v in verdicts}
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
            if not f.startswith("dev/programme/delivery/"):
                files.append(f)
                lines += (int(a) if a != "-" else 0) + (int(d) if d != "-" else 0)
        facts[pr] = dict(
            origin="none" if grp is None else "finding" if (grp.get("issues") or grp.get("findings") or grp.get("fixes")) else "group",
            fixer=((grp or {}).get("model") or {}).get("fixer") or "none",
            size="?" if not mb else "S<150" if lines < 150 else "M<600" if lines < 600 else "L>=600",
            product=any(f.startswith(("custom_components/", "blueprints/")) for f in files))
    return facts


def stratum(by: str, v: dict, facts: dict[int, dict]) -> str:
    if "+" in by:
        return "+".join(stratum(b, v, facts) for b in by.split("+"))
    if by == "all":
        return "all"
    if by == "kind":
        return v["reviewer"]
    if by == "class":
        return v["cls"] or "(merge)"
    if by == "prior-merge":
        return "after-a-merge-verdict" if v["prior_merge"] else "no-merge-yet"
    return str(facts[v["pr"]][by])


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


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def guardrail(verdicts: list[dict], until: datetime, n: int, p0: float) -> str:
    first, caught = {}, set()
    for v in verdicts:
        if v["t"] < until:
            first.setdefault(v["pr"], v["t"])
            if v["real"]:
                caught.add(v["pr"])
    last = sorted(first, key=lambda p: first[p])[-n:]
    if len(last) < n:
        return f"GUARDRAIL insufficient: {len(last)} reviewed PRs < N={n}"
    k = sum(p in caught for p in last)
    cdf = binom_cdf(k, n, p0)
    return (f"GUARDRAIL last {n} PRs (first verdict {first[last[0]]:%m-%dT%H:%MZ}..{first[last[-1]]:%m-%dT%H:%MZ}): "
            f"incidence {k}/{n}; P(X<={k}|{n},{p0}) = {cdf:.3f} -> {'would-trip' if cdf < ALPHA else 'ok'} (report-only)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(ROOT))
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--tree", default="origin/main")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--window", action="append", default=[], metavar="NAME=FROM..UNTIL")
    ap.add_argument("--by", action="append", default=[], metavar="S[+S...]",
                    help="one of " + ", ".join(STRATA) + "; joined with + to cross them")
    ap.add_argument("--roster", metavar="REF:PATH")
    ap.add_argument("--guardrail", type=int, metavar="N")
    ap.add_argument("--p0", type=float, metavar="P", help="the baseline incidence; required with --guardrail")
    ap.add_argument("--real-extra", default="", metavar="W[,W...]",
                    help="class words counted REAL beside REAL_CATCH (a sensitivity run)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = Path(a.repo)
    if a.fetch:
        rm = a.remote
        git(repo, "fetch", "-q", "--tags", rm, *(f"+refs/heads/{f}/*:refs/remotes/{rm}/{f}/*"
                                                for f in ("review", "verdict", "probe")))
    if not a.window:
        ap.error("at least one --window NAME=FROM..UNTIL")
    used = {s for by in a.by for s in by.split("+")}
    if used - set(STRATA):
        ap.error(f"unknown stratum {sorted(used - set(STRATA))}; one of {', '.join(STRATA)}")
    if {"origin", "fixer"} & used and not a.roster:
        ap.error("--by origin|fixer needs --roster REF:PATH")
    extra = frozenset(w for w in a.real_extra.split(",") if w)
    verdicts, outside = load(repo, a.remote, REAL_CATCH | extra)
    if extra:
        print(f"REAL = the study's list + {', '.join(sorted(extra))}")
    facts = pr_facts(repo, a.tree, a.roster, verdicts) if FACT_STRATA & used else {}
    wins = []
    for w in a.window:
        name, span = w.split("=", 1)
        f, u = span.split("..", 1)
        wins.append((name, when(f), when(u)))
    print(f"verdicts on the bus: {len(verdicts)}; outside the grammar: {len(outside)}")
    for s in outside:
        print(f"  outside: {s[:100]}")
    for by in ["all", *a.by]:
        print(f"## {by}")
        rows = {name: tally(verdicts, f, u, lambda v: stratum(by, v, facts)) for name, f, u in wins}
        for k in sorted({k for r in rows.values() for k in r}):
            for name, _, _ in wins:
                o = rows[name].get(k) or dict(prs=set(), verdicts=0, real=0, book=0, caught=set(), first=[])
                print(f"  {k:24} {name:6} {fmt(o)}")
    if a.guardrail:
        if a.p0 is None:
            ap.error("--guardrail needs --p0")
        print(guardrail(verdicts, wins[-1][2], a.guardrail, a.p0))
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

        def verdict(ref: str, subj: str, nonce: str, t: str) -> str:
            (R / "VERDICT.md").write_text(f"{subj.split(' ', 2)[2]}\n\nbus-nonce: {nonce}\n")
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
        s4 = verdict(rv(4), f"verdict: #4 Fix review: PASS merge {H}", N[7], "2026-10-02T02:00:00Z")
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
        check("binomial: P(X<=0|20,0.15) = 0.039", abs(binom_cdf(0, 20, 0.15) - 0.0388) < 1e-3)
        check("guardrail: 3 PRs < N=5 is insufficient, never a trip",
              "insufficient" in guardrail(vlist, c, 5, 0.18))
        check("guardrail: 2/3 at p0=0.5 is ok (P(X<=2) = 0.875)",
              guardrail(vlist, c, 3, 0.5).endswith("incidence 2/3; P(X<=2|3,0.5) = 0.875 -> ok (report-only)"))
        check("guardrail: 1/2 before L at p0=0.99 would trip (P(X<=1) = 0.020)",
              guardrail(vlist, b, 2, 0.99).endswith("= 0.020 -> would-trip (report-only)"))
    print(f"review_strength self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
