#!/usr/bin/env python3
"""Would carrying a row-only head's CI results save CI? (R10-FLY-ROW-HEAD-CARRY, arm a)

    python3 dev/audit/harnesses/r10_row_head_carry.py --since 2026-10-28 --limit 40 \\
        [--cache pairs.jsonl]
    python3 dev/audit/harnesses/r10_row_head_carry.py --self-test

The carry arm proposed: when a PR's new head R differs from its first parent P
by exactly `dev/programme/delivery/<N>.md` (open_pr.sh's second push), keep
P's ci.yml run instead of cancelling it, and let R skip the four code units
(tests, codeql, hassfest, validate) and reuse P's. GitHub cancels a run, never
a part of one, so keeping P keeps ALL of P's run.

THE RULES.
- Row-only: `git diff --name-only R^1 R` is exactly `[dev/programme/delivery/<N>.md]`
  for the PR's own N (`classify`). The window is every first-parent
  "Merge pull request #N" commit on origin/main since --since; a PR's commits
  are `M^1..M^2`. The newest --limit row-only pairs are read from the API.
- Job-seconds: per ci.yml run at a head, latest attempt, the sum over jobs of
  `completed_at - started_at`, grouped by the job name's unit (text before
  ` / `). Job-seconds, not billed minutes.
- Per pair, from the CODE runs (display_title `CI code ...`):
  gain = P's job-seconds already spent in the four units (today wasted by the
  cancel, under the carry kept and reused);
  loss = R's code-run job-seconds outside the four units (what P's kept run
  would also spend: prelude, governance, body units, gate) minus what P
  already spent outside them;
  net = gain - loss, summed over the pairs (`net`). Negative: the carry costs CI.
- gap = R's first code run created minus P's (s): the lead time a carry could save.

NULL CONTROL (`--self-test`, offline). The classifier reads a row-only head
as row-only and refuses each other shape the brief named (the row plus a
CLAUDE.md byte, another PR's row, a new unclassified .md). `net` reads
negative on a pair whose P was cancelled at once and POSITIVE on the same pair
had P run to completion (P's spend equal to R's): had the premise "P is
cancelled early" been false, the harness would have said the carry pays.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime

REPO = "tvofi/heatpump_optimizer"
CARRIED = ("tests", "codeql", "hassfest", "validate")


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def api(path: str) -> dict:
    return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)


def classify(pr: str, files: list[str]) -> str:
    row = f"dev/programme/delivery/{pr}.md"
    return "row-only" if files == [row] else ("row+other" if row in files else "other")


def pairs(since: str) -> tuple[list[tuple[str, str, str]], dict]:
    """[(pr, P, R)] row-only, newest merge first; and the class counts over every PR commit."""
    out, counts = [], {}
    for line in git("log", "--first-parent", "--merges", f"--since={since}", "--format=%H %s", "origin/main").splitlines():
        m = re.match(r"(\w+) Merge pull request #(\d+) ", line)
        if not m:
            continue
        merge, pr = m.groups()
        for c in git("rev-list", f"{merge}^1..{merge}^2").split():
            p = git("rev-parse", f"{c}^1").strip()
            cls = classify(pr, git("diff", "--name-only", p, c).split())
            counts[cls] = counts.get(cls, 0) + 1
            if cls == "row-only":
                out.append((pr, p, c))
    return out, counts


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def runs_at(sha: str) -> list[dict]:
    out = []
    for r in api(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={sha}&per_page=100")["workflow_runs"]:
        units: dict[str, float] = {}
        for j in api(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=latest&per_page=100")["jobs"]:
            if j["started_at"] and j["completed_at"]:
                u = j["name"].split(" / ")[0]
                units[u] = units.get(u, 0) + max((_ts(j["completed_at"]) - _ts(j["started_at"])).total_seconds(), 0)
        out.append({"id": r["id"], "title": r["display_title"], "conclusion": r["conclusion"] or r["status"],
                    "created": r["created_at"], "units_s": units})
    return out


def net(p_runs: list[dict], r_runs: list[dict]) -> dict | None:
    """One pair's figures from its CODE runs; None when either head has none."""
    pc = [r for r in p_runs if r["title"].startswith("CI code")]
    rc = [r for r in r_runs if r["title"].startswith("CI code")]
    if not pc or not rc:
        return None

    def spent(runs, inside):
        return sum(v for r in runs for u, v in r["units_s"].items() if (u in CARRIED) == inside)
    gain = spent(pc, True)
    loss = spent(rc, False) - spent(pc, False)
    return {"gap_s": (min(_ts(r["created"]) for r in rc) - min(_ts(r["created"]) for r in pc)).total_seconds(),
            "p_spent_s": sum(sum(r["units_s"].values()) for r in p_runs), "gain_s": gain, "loss_s": loss,
            "net_s": gain - loss, "r_carried_s": spent(rc, True),
            "r_all_s": sum(sum(r["units_s"].values()) for r in r_runs),
            "p_code": ",".join(r["conclusion"] for r in pc), "r_code": ",".join(r["conclusion"] for r in rc)}


def self_test() -> int:
    n = fails = 0

    def check(name, got, want):
        nonlocal n, fails
        n += 1
        if got != want:
            fails += 1
            print(f"FAIL {name}: got {got!r}, want {want!r}")
    row = "dev/programme/delivery/7.md"
    check("a row-only head", classify("7", [row]), "row-only")
    check("null: the row plus a CLAUDE.md byte", classify("7", ["CLAUDE.md", row]), "row+other")
    check("null: the row plus a new unclassified .md", classify("7", [row, "notes.md"]), "row+other")
    check("null: another PR's row", classify("7", ["dev/programme/delivery/8.md"]), "other")
    t0, t1 = "2026-10-31T10:00:00Z", "2026-10-31T10:00:15Z"
    full = {"tests": 3000.0, "codeql": 300.0, "hassfest": 20.0, "validate": 10.0,
            "prelude": 30.0, "governance": 900.0, "pr-contract": 600.0, "gate": 700.0}
    r = [{"title": "CI code pr=7", "conclusion": "success", "created": t1, "units_s": full}]
    early = [{"title": "CI code pr=7", "conclusion": "cancelled", "created": t0,
              "units_s": {"prelude": 30.0, "tests": 60.0, "governance": 20.0}}]
    done = [{"title": "CI code pr=7", "conclusion": "success", "created": t0, "units_s": dict(full)}]
    e = net(early, r)
    check("P cancelled at once: the carry costs CI", (e["net_s"] < 0, e["gain_s"], e["loss_s"]), (True, 60.0, 2180.0))
    d = net(done, r)
    check("null: P run to completion: the same harness says the carry pays", (d["net_s"] > 0, d["net_s"]),
          (True, 3330.0))
    check("the gap", e["gap_s"], 15.0)
    check("no code run at a head: not a pair", net([], r), None)
    print(f"r10_row_head_carry self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--cache", help="JSONL of read pairs: read if present, else written")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.since:
        ap.error("--since is required")
    found, counts = pairs(a.since)
    print("classes over every PR commit in the window:", json.dumps(counts, sort_keys=True))
    print(f"PRs with a row-only head: {len({p for p, _, _ in found})}")
    rows = []
    try:
        rows = [json.loads(x) for x in open(a.cache)] if a.cache else []
    except FileNotFoundError:
        pass
    if not rows:
        for pr, p, r in found[: a.limit]:
            rows.append({"pr": pr, "P": p, "R": r, "P_runs": runs_at(p), "R_runs": runs_at(r)})
        if a.cache:
            with open(a.cache, "w") as fh:
                fh.writelines(json.dumps(x) + "\n" for x in rows)
    figs = []
    for x in rows:
        f = net(x["P_runs"], x["R_runs"])
        if f is None:
            print(x["pr"], "SKIP: no code run at one head")
            continue
        figs.append(f)
        print(x["pr"], *(f"{k}={v:.0f}" if isinstance(v, float) else f"{k}={v}" for k, v in f.items()))
    if not figs:
        print("RESULT pairs=0")
        return 1
    print(f"pairs={len(figs)} PRs #{rows[-1]['pr']}..#{rows[0]['pr']}")
    for k in ("gap_s", "p_spent_s", "gain_s", "loss_s", "net_s", "r_carried_s", "r_all_s"):
        v = [f[k] for f in figs]
        print(f"{k}: median={statistics.median(v):.0f} sum={sum(v):.0f} max={max(v):.0f}")
    for k in ("p_code", "r_code"):
        print(k, json.dumps({c: sum(f[k] == c for f in figs) for c in sorted({f[k] for f in figs})}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
