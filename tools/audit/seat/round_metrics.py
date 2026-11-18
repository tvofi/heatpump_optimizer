#!/usr/bin/env python3
"""round_metrics.py -- decision 0018's flow reads per round and per week, and the scorecard's input producer.

    python3 -I round_metrics.py report --dir D --repo R (--round N | --since ISO [--until ISO]) [--weeks]
    python3 -I round_metrics.py produce --dir D --repo R --gh-repo OWNER/NAME [--roster-ref REF]
    python3 -I round_metrics.py --self-test [--no-mutants] [--tests DIR]

WHY (owner ruling 2026-11-13, cards P3 and P8; the round-10 process convergence
audit d5d7ff81, section 6 row a3): the scorecard had no producer for its inputs,
and the audit's per-round and per-week figures came from out-of-tree scratch
scripts. `produce` refreshes D (the beat's `<state>/scorecard/`); `report` reads
only D and, for windows and gate checks, the checkout's git.

THE WINDOW of round N runs from tag v(N-1).0.0 to tag vN.0.0 (decision 0016, a
major version is a closed round), or to now while vN.0.0 does not exist; a round
whose opening tag is missing is unread. `--weeks` cuts it into 7-day spans from
its start; the last may be shorter and says so.

THE READS (0018 section 2; each prints `unread (<why>)`, never a number, when its
input is absent, and a partial ledger is a NO-READ, never a partial value):
  merges          first-parent merges of main in the window by machinery_ratchet's
                  class (production, machinery, record).
  lead_time       per class, hours from the commit that ADDED the group to a roster
                  (`"group": "<G>"` first appearing in dev/programme/rosters/ or
                  .claude/workflows/ at the roster ref, never a field anyone fills)
                  to the group's latest merge of that class in the window; p50 and
                  p90 by nearest rank over groups. A merge maps to a group by the
                  roster's resume.pr, else by its branch (owner prefix and
                  fix/|handoff/|hotfix/ dropped, upper-cased, a split part's -pN
                  suffix dropped) naming a group. A merge naming no group, and a
                  group entered after its merge (unknowable, fixer.md step 16), are
                  counted beside, never in the term.
  product_green   main's concluded (success or failure) `CI` push runs in the window
                  whose `gate` job (latest attempt) succeeded; cancelled beside; a
                  concluded run with no job listing makes it unread; beside it the
                  check count `tools/ci/gate.py` REQUIRED["push"] holds at the
                  window's first and last main commit.
  restore         median hours from a main run whose gate failed after a green one
                  to the next run whose gate succeeded, over red spells closed in
                  the window; an open spell beside.
  runner_s        job seconds (completed_at - started_at, every attempt) of every
                  completed `CI` run created in the window, over the window's
                  merges; one run with no job listing makes it unread.
  tokens          0018's tokens_per_change: the ledger `tokens.tsv` (t, seat_class,
                  tokens) summed over the window, over production merges; a seat
                  class of SEAT_CLASSES with no row in the window makes it unread.
  closure_slip    a round's read (`--round`): over the round's plan pages after its
                  register (the commit first adding dev/audit/rounds/round<N>/JUDGE.json
                  to main), in the window, sampled once a day (each day's last page with
                  a forecast, days counted from the register; SLIP_SAMPLE_S), the days the
                  forecast closure moved later between consecutive samples (an earlier
                  move pays nothing back), over the days between the first and last
                  sample; beside it the samples and pages read, the net move (the
                  last daily sample's forecast less the first's), pages
                  with no forecast (an UNAVAILABLE page), the threshold
                  `closure_slip_ceiling` of dev/audit/config/objective.json (null is
                  undecided), round start to closure in days (the vN.0.0 tag, else the
                  newest forecast) and the round's groups at stage `deferred`. Fewer
                  than two daily samples read no slope: unread.
  unexamined      a round's read: production merges in the window that are no ancestor
                  of any finder baseline the round recorded (every `"baseline_sha"`
                  under dev/audit/rounds/round<N>/ on origin/main), over the window's
                  production merges; beside it the unexamined merges by roster group
                  kind. A baseline that does not resolve makes it unread (a partial
                  ledger), and so does a round with none (no finder pass, no "after
                  the baseline").

INPUTS under D, written by `produce` (one REST batch: the CI run listing since the
open round's start, and each completed run's job listing not yet cached, at most
JOB_FETCH_MAX per pass):
  runs.json       [{id, t, c, attempt}] main `CI` push runs (scorecard.py's A lines)
  ci_runs.json    [{id, t, c, attempt}] every completed `CI` run
  jobs/jobs_<id>.json  {"attempt", "jobs": [{name, conclusion, started_at, completed_at, run_attempt}]}
  merges.tsv      sha, pr, ct, class, tokens, group, entered (scorecard.py's H line)
  entries.json    {"tip", "entered": {group: epoch}} the roster-entry scan's cache
  verdicts.json   review_strength.load's bus;  roster.json  the newest roster
  plans.json      {"<N>": {"tip", "register", "history": [[t, closure epoch or null]]}}
                  rounds N-1 and N's PLAN.html forecast per commit on their state ref
                  handoff/audit-r<N>-plan, scanned from the cached tip; a deleted ref
                  keeps the cached history
  groups.json     {group: {"kind", "stage", "round"}} over every wave-r<N> roster
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSES = ("production", "machinery", "record")
SEAT_CLASSES = ("orchestrator", "local", "cloud")
WEEK_S = 7 * 86400
JOB_FETCH_MAX = 400
MERGES_MIN = 200  # merges.tsv keeps at least the newest 200, so scorecard's last-50 windows read
ROSTER_PATHS = ("dev/programme/rosters/", ".claude/workflows/")
SUBJECT = re.compile(r"^Merge pull request #(\d+) from [^/\s]+/(\S+)")
ADDED = re.compile(r'^\+\s*"group":\s*"([^"]+)"')
TSV = ("sha", "pr", "ct", "class", "tokens", "group", "entered")
DAY_S = 86400
# closure_slip samples the plan history once a day (each day's last page, days counted from the register): summing
# the later moves of every page makes the read a function of how often the page is committed (round 10's history:
# 2.57 days per day over all 563 forecast pages, 1.27 over its 15 daily samples), so only a fixed cadence compares rounds.
SLIP_SAMPLE_S = DAY_S
PLAN_REF = "origin/handoff/audit-r{n}-plan"
PLAN_PAGE = "handoff/round{n}/state/PLAN.html"
REGISTER = "dev/audit/rounds/round{n}/JUDGE.json"
# plan_page.py's slots note: "... merge batches, closure <plan.json summary.closure>."
CLOSURE = re.compile(r"merge batches, closure (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z)")
BASELINE = re.compile(r'"baseline_sha":\s*"([0-9a-f]{7,40})"')


def epoch(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def iso(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def rank(xs: list[float], p: float) -> float:
    """Nearest-rank percentile: the smallest value with at least p of the sample at or below it."""
    s = sorted(xs)
    return s[max(0, math.ceil(p * len(s)) - 1)]


def git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, check=True).stdout


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


# ------------------------------------------------------------------ windows

def tag_time(repo: Path, n: int) -> float | None:
    out = git(repo, "for-each-ref", "--format=%(creatordate:unix)", f"refs/tags/v{n}.0.0").strip()
    return float(out) if out else None


def round_window(repo: Path, n: int, now: float) -> tuple[float, float, str] | None:
    a, b = tag_time(repo, n - 1), tag_time(repo, n)
    if a is None:
        return None
    return a, (b if b is not None else now), ("closed" if b is not None else "open")


def open_round(repo: Path) -> int | None:
    tags = [int(m[1]) for m in re.finditer(r"^v(\d+)\.0\.0$", git(repo, "tag", "-l", "v*.0.0"), re.M)]
    return max(tags) + 1 if tags else None


def weeks(a: float, b: float) -> list[tuple[float, float]]:
    out, t = [], a
    while t < b:
        out.append((t, min(t + WEEK_S, b)))
        t += WEEK_S
    return out


# ------------------------------------------------------------------ reads over D

def load_merges(d: Path) -> list[dict] | None:
    try:
        text = (d / "merges.tsv").read_text()
    except OSError:
        return None
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    for r in rows:
        r["ct"] = int(r["ct"])
    return rows


def gate_conclusions(d: Path) -> dict[int, str]:
    """Run id -> the conclusion of its `gate` job at the run's latest listed attempt."""
    out: dict[int, str] = {}
    for f in sorted((d / "jobs").glob("jobs_*.json")) if (d / "jobs").is_dir() else []:
        doc = read_json(f)
        try:
            gates = [j for j in doc["jobs"] if j["name"] == "gate"]
            if gates:
                out[int(f.stem.split("_")[1])] = max(gates, key=lambda j: j.get("run_attempt") or 0)["conclusion"]
        except (TypeError, KeyError, IndexError, ValueError):
            continue
    return out


def lead_lines(rows: list[dict] | None, a: float, b: float) -> list[str]:
    if rows is None:
        return ["lead_time unread (merges.tsv)"]
    out = []
    for cls in CLASSES:
        w = sorted((r for r in rows if r["class"] == cls and a <= r["ct"] < b), key=lambda r: r["ct"])
        latest = {r["group"]: r for r in w}
        nogroup = sum(not r["group"] for r in w)
        hrs = [(r["ct"] - int(r["entered"])) / 3600 for r in latest.values() if r["entered"]]
        ahead = sum(1 for h in hrs if h < 0)
        hrs = [h for h in hrs if h >= 0]
        side = f"{nogroup} {cls} merges name no roster group; {ahead} groups entered after their merge"
        if not hrs:
            out.append(f"lead_time {cls} unread (no {cls} group with a roster entry merged in the window; {side})")
        else:
            out.append(f"lead_time {cls} p50 {rank(hrs, 0.5):.1f} h p90 {rank(hrs, 0.9):.1f} h "
                       f"(n={len(hrs)} groups; {side})")
    return out


def green_lines(runs: list | None, gate: dict, a: float, b: float, checks: str) -> list[str]:
    if runs is None:
        return ["product_green unread (runs.json)", "restore unread (runs.json)"]
    seq = sorted((r for r in runs if r["c"] in ("success", "failure")), key=lambda r: r["t"])
    w = [r for r in seq if a <= epoch(r["t"]) < b]
    cancelled = sum(r["c"] == "cancelled" and a <= epoch(r["t"]) < b for r in runs)
    if not w:
        return ["product_green unread (no concluded main CI push run in the window)",
                "restore unread (no concluded main CI push run in the window)"]
    blind = [r for r in seq if r["id"] not in gate and epoch(r["t"]) < b]
    if any(a <= epoch(r["t"]) for r in blind):
        why = f"{sum(a <= epoch(r['t']) for r in blind)} of {len(w)} concluded runs have no job listing"
        return [f"product_green unread ({why}: a partial ledger is no read)", f"restore unread ({why})"]
    ok = sum(gate.get(r["id"]) == "success" for r in w)
    green = (f"product_green {ok}/{len(w)} = {100 * ok / len(w):.0f}% (concluded main CI push runs; "
             f"cancelled {cancelled}; gate checks {checks})")
    spells, start = [], None
    for r in (r for r in seq if r["id"] in gate and epoch(r["t"]) < b):
        if gate[r["id"]] != "success" and start is None:
            start = epoch(r["t"])
        elif gate[r["id"]] == "success" and start is not None:
            if epoch(r["t"]) >= a:
                spells.append((epoch(r["t"]) - start) / 3600)
            start = None
    tail = f"; open red spell since {iso(start)}" if start is not None else ""
    if not spells:
        return [green, f"restore no red spell closed in the window ({len(w)} concluded runs read{tail})"]
    return [green, f"restore median {rank(spells, 0.5):.1f} h over {len(spells)} red spells closed in the window "
                   f"(longest {max(spells):.1f} h{tail})"]


def runner_line(d: Path, merges: list | None, a: float, b: float) -> str:
    runs = read_json(d / "ci_runs.json")
    if runs is None or merges is None:
        return "runner_s unread (ci_runs.json or merges.tsv)"
    w = [r for r in runs if a <= epoch(r["t"]) < b]
    m = sum(a <= r["ct"] < b for r in merges)
    if not w or not m:
        return f"runner_s unread ({len(w)} completed CI runs and {m} merges in the window)"
    sec, blind = 0.0, 0
    for r in w:
        doc = read_json(d / "jobs" / f"jobs_{r['id']}.json")
        if not doc or doc.get("attempt") != r["attempt"]:
            blind += 1
            continue
        for j in doc["jobs"]:
            if j.get("started_at") and j.get("completed_at"):
                sec += max(0.0, epoch(j["completed_at"]) - epoch(j["started_at"]))
    if blind:
        return f"runner_s unread ({blind} of {len(w)} CI runs have no job listing at their latest attempt)"
    return f"runner_s {sec / m:.0f} per merge ({sec:.0f} job seconds of {len(w)} CI runs over {m} merges)"


def token_line(d: Path, merges: list | None, a: float, b: float) -> str:
    try:
        rows = list(csv.DictReader(io.StringIO((d / "tokens.tsv").read_text()), delimiter="\t"))
    except OSError:
        return "tokens unread (no token ledger tokens.tsv; R11-PRE-TOKEN-LEDGER builds it)"
    w = [r for r in rows if a <= epoch(r["t"]) < b]
    missing = [c for c in SEAT_CLASSES if not any(r["seat_class"] == c for r in w)]
    prod = sum(r["class"] == "production" and a <= r["ct"] < b for r in merges or [])
    if missing or not prod:
        return f"tokens unread (seat classes with no ledger row: {', '.join(missing) or 'none'}; production merges {prod})"
    total = sum(int(r["tokens"]) for r in w)
    return f"tokens {total / prod:.0f} per production merge (window total {total}; {prod} production merges)"


def slip_line(d: Path, rnd: dict | None, a: float, b: float) -> str:
    if rnd is None:
        return "closure_slip unread (a round's read: --round names the round)"
    n = rnd["n"]
    doc = (read_json(d / "plans.json") or {}).get(str(n))
    if not doc or doc.get("register") is None:
        why = "no plan history in plans.json" if not doc else f"no register: {REGISTER.format(n=n)} is not on main"
        return f"closure_slip unread (round {n}: {why})"
    every = sorted(h for h in doc["history"] if h[0] >= doc["register"] and a <= h[0] < b)
    hist = [h for h in every if h[1] is not None]
    daily = list({(h[0] - doc["register"]) // SLIP_SAMPLE_S: h for h in hist}.values())  # each day's last page
    if len(daily) < 2:
        return (f"closure_slip unread ({len(daily)} daily samples of plan pages with a forecast closure after the "
                f"register in the window; a slope needs two)")
    later = sum(max(0.0, q[1] - p[1]) for p, q in zip(daily, daily[1:])) / DAY_S
    span = (daily[-1][0] - daily[0][0]) / DAY_S
    slip, cap = later / span, rnd.get("ceiling")
    held = ("ceiling unread (objective.json)" if cap == "unread" else "ceiling unset, undecided" if cap is None
            else f"{'within' if slip <= cap else 'over'} the ceiling {cap:g}")
    newest = max((h for h in doc["history"] if h[1] is not None), key=lambda h: h[0])[1]
    close = (rnd["end"], "closed") if rnd["state"] == "closed" else (newest, "forecast")
    groups = read_json(d / "groups.json")
    deferred = ("deferred unread (groups.json)" if groups is None else
                f"{sum(g.get('round') == n and g.get('stage') == 'deferred' for g in groups.values())} groups deferred out")
    return (f"closure_slip {slip:.2f} days per day ({later:.2f} days later over {span:.2f} days of plan history "
            f"after the register, {len(daily)} daily samples of {len(every)} pages; net "
            f"{(daily[-1][1] - daily[0][1]) / DAY_S:+.2f} days; {len(every) - len(hist)} pages without a forecast; "
            f"{held}; round start to closure "
            f"{(close[0] - rnd['start']) / DAY_S:.1f} days ({close[1]}); {deferred})")


def round_baselines(repo: Path, n: int) -> tuple[list[str], list[str]]:
    """Round n's recorded finder baselines on origin/main: (resolved commits, prefixes that resolve to none)."""
    p = subprocess.run(["git", "grep", "-h", "-E", BASELINE.pattern, "origin/main", "--", f"dev/audit/rounds/round{n}/"],
                       cwd=repo, capture_output=True, text=True)
    shas, bad = set(), []
    for s in sorted(set(BASELINE.findall(p.stdout))):
        r = subprocess.run(["git", "rev-parse", "-q", "--verify", f"{s}^{{commit}}"], cwd=repo, capture_output=True, text=True)
        if r.returncode:
            bad.append(s)
        else:
            shas.add(r.stdout.strip())
    return sorted(shas), bad


def unexamined_line(d: Path, rnd: dict | None, merges: list | None, a: float, b: float) -> str:
    if rnd is None:
        return "unexamined unread (a round's read: --round names the round)"
    if merges is None:
        return "unexamined unread (merges.tsv)"
    prod = [r for r in merges if r["class"] == "production" and a <= r["ct"] < b]
    if not prod:
        return "unexamined unread (no production merge in the window)"
    n = rnd["n"]
    shas, bad = round_baselines(rnd["repo"], n)
    if bad:
        return f"unexamined unread ({len(bad)} finder baselines of round {n} resolve to no commit: {', '.join(bad)})"
    if not shas:
        return f"unexamined unread (no finder baseline recorded under dev/audit/rounds/round{n}/ on origin/main)"
    seen = set(git(rnd["repo"], "rev-list", *shas).split())
    un = [r for r in prod if r["sha"] not in seen]
    groups = read_json(d / "groups.json")
    if groups is None:
        kinds = "by kind unread (groups.json)"
    else:
        tally: dict[str, int] = {}
        for r in un:
            k = (groups.get(r["group"]) or {}).get("kind") or ("no roster group" if not r["group"] else "unkinded")
            tally[k] = tally.get(k, 0) + 1
        kinds = "by kind " + (", ".join(f"{k} {c}" for k, c in sorted(tally.items())) or "none")
    return (f"unexamined {len(un)}/{len(prod)} = {100 * len(un) / len(prod):.0f}% (production merges in the window "
            f"no finder baseline of round {n} contains; {len(shas)} baselines; {kinds})")


def window_lines(d: Path, a: float, b: float, checks: str, rnd: dict | None = None) -> list[str]:
    merges = load_merges(d)
    out = []
    if merges is None:
        out.append("merges unread (merges.tsv)")
    else:
        n = {c: sum(r["class"] == c and a <= r["ct"] < b for r in merges) for c in CLASSES}
        out.append(f"merges {sum(n.values())}: " + ", ".join(f"{c} {n[c]}" for c in CLASSES))
    out += lead_lines(merges, a, b)
    out += green_lines(read_json(d / "runs.json"), gate_conclusions(d), a, b, checks)
    out.append(runner_line(d, merges, a, b))
    out.append(token_line(d, merges, a, b))
    out.append(slip_line(d, rnd, a, b))
    out.append(unexamined_line(d, rnd, merges, a, b))
    return out


# ------------------------------------------------------------------ git reads

def gate_checks_at(repo: Path, sha: str) -> int | None:
    """len(REQUIRED["push"]) of tools/ci/gate.py at <sha>, run from an archive of tools/ci there."""
    try:
        blob = subprocess.run(["git", "archive", sha, "tools/ci"], cwd=repo, capture_output=True, check=True).stdout
        with tempfile.TemporaryDirectory() as td:
            with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
                tf.extractall(td, filter="data")
            p = subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                                "import gate; print(len(gate.REQUIRED['push']))", f"{td}/tools/ci"],
                               capture_output=True, text=True, timeout=60)
        return int(p.stdout.strip()) if p.returncode == 0 else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, tarfile.TarError, ValueError, OSError):
        return None


def gate_checks(repo: Path | None, a: float, b: float) -> str:
    if repo is None:
        return "unread"
    ends = []
    for t in (a, b):
        sha = git(repo, "rev-list", "-1", "--first-parent", f"--before={int(t)}", "origin/main").strip()
        n = gate_checks_at(repo, sha) if sha else None
        ends.append("unread" if n is None else str(n))
    return f"{ends[0]} at the window's start, {ends[1]} at its end"


def roster_entries(repo: Path, ref: str, cache: dict) -> dict:
    """{"tip", "entered"}: each group's first-adding commit time at <ref>, scanned from the cached tip."""
    tip = git(repo, "rev-parse", ref).strip()
    entered = dict(cache.get("entered") or {})
    old = cache.get("tip")
    span = f"{old}..{tip}" if old and subprocess.run(["git", "merge-base", "--is-ancestor", old, tip],
                                                       cwd=repo).returncode == 0 else tip
    t = None
    for ln in git(repo, "log", "--reverse", "-p", "-U0", "--no-renames", "--format=@@C %ct", span,
                  "--", *ROSTER_PATHS).splitlines():
        if ln.startswith("@@C "):
            t = int(ln[4:])
        elif (m := ADDED.match(ln)) and m[1] not in entered:
            entered[m[1]] = t
    return {"tip": tip, "entered": entered}


def group_of(pr: int | None, branch: str, by_pr: dict, names: set) -> str:
    if pr in by_pr:
        return by_pr[pr]
    k = re.sub(r"^(?:fix|handoff|hotfix)/", "", branch).upper()
    for c in (k, re.sub(r"-P\d+$", "", k)):
        if c in names:
            return c
    return ""


def round_groups(repo: Path, ref: str) -> list[tuple[int, dict]]:
    """(round, group) over every wave-r<N>-groups.json roster at <ref>, oldest round first."""
    out = []
    for f in git(repo, "ls-tree", "-r", "--name-only", ref, "dev/programme/rosters/").split():
        if m := re.search(r"wave-r(\d+)-groups\.json$", f):
            try:
                out += [(int(m[1]), g) for g in json.loads(git(repo, "show", f"{ref}:{f}")).get("groups", [])
                        if isinstance(g, dict)]
            except (ValueError, subprocess.CalledProcessError):
                continue
    return sorted(out, key=lambda x: x[0])


def rosters_at(repo: Path, ref: str) -> list[dict]:
    return [g for _, g in round_groups(repo, ref)]


def plan_history(repo: Path, n: int, cache: dict) -> dict:
    """Round n's {"tip", "register", "history"}: PLAN.html's forecast closure per commit on its state ref."""
    reg = git(repo, "log", "--diff-filter=A", "--format=%ct", "origin/main", "--", REGISTER.format(n=n)).split()
    out = dict(cache, register=int(reg[-1]) if reg else None)
    tip = subprocess.run(["git", "rev-parse", "-q", "--verify", PLAN_REF.format(n=n) + "^{commit}"], cwd=repo,
                         capture_output=True, text=True).stdout.strip()
    if not tip:
        return out
    old, page = cache.get("tip"), PLAN_PAGE.format(n=n)
    inc = bool(old) and subprocess.run(["git", "merge-base", "--is-ancestor", old, tip], cwd=repo).returncode == 0
    hist = list(cache.get("history") or []) if inc else []
    for ln in git(repo, "log", "--format=%H %ct", f"{old}..{tip}" if inc else tip, "--", page).splitlines():
        sha, t = ln.split()
        m = CLOSURE.search(git(repo, "show", f"{sha}:{page}"))
        hist.append([int(t), epoch(m[1]) if m else None])
    return dict(out, tip=tip, history=sorted(hist, key=lambda h: h[0]))


def merge_rows(repo: Path, since: float, old: list[dict], groups: list[dict], entered: dict) -> list[dict]:
    sys.path.insert(0, str(HERE.parent))
    import machinery_ratchet as mr
    cached = {r["sha"]: r["class"] for r in old}
    by_pr = {}
    for g in groups:
        p = (g.get("resume") or {}).get("pr")
        if isinstance(p, int):
            by_pr[p] = g["group"]
    names = {g["group"] for g in groups if "group" in g}
    rows = []
    for i, ln in enumerate(git(repo, "log", "--first-parent", "--merges", "--format=%H%x09%P%x09%ct%x09%s",
                                "origin/main").splitlines()):
        sha, parents, ct, subj = ln.split("\t", 3)
        if int(ct) < since and i >= MERGES_MIN:
            break
        m = SUBJECT.match(subj)
        pr, branch = (int(m[1]), m[2]) if m else (None, "")
        cls = cached.get(sha) or mr.diff_stats(str(repo), parents.split()[0], sha)["kind"]
        grp = group_of(pr, branch, by_pr, names)
        rows.append({"sha": sha, "pr": pr or "", "ct": int(ct), "class": cls, "tokens": branch, "group": grp,
                     "entered": entered.get(grp) or ""})
    return rows[::-1]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def produce(d: Path, repo: Path, gh_repo: str, roster_ref: str | None, paginate=None) -> list[str]:
    """Refresh every input under D; returns the notes it prints (jobs left for the next pass)."""
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parent.parent / "ci"))
    import roster_lib
    import review_strength
    if paginate is None:
        import ghapi
        paginate = ghapi.paginate
    n = open_round(repo)
    since = tag_time(repo, n - 1) if n else None
    if since is None:
        raise SystemExit("round_metrics: no v*.0.0 tag, so no open round to read from")
    ref = roster_lib.reader_ref(str(repo), roster_ref)
    pairs = round_groups(repo, ref)
    groups = [g for _, g in pairs]
    write(d / "groups.json", json.dumps({g["group"]: {"kind": g.get("kind"), "stage": (g.get("resume") or {}).get("stage"),
                                                      "round": k} for k, g in pairs if "group" in g}, sort_keys=True))
    plans = read_json(d / "plans.json") or {}
    for k in (n - 1, n):
        plans[str(k)] = plan_history(repo, k, plans.get(str(k)) or {})
    write(d / "plans.json", json.dumps(plans, sort_keys=True))
    entries = roster_entries(repo, ref, read_json(d / "entries.json") or {})
    write(d / "entries.json", json.dumps(entries, sort_keys=True))
    rows = merge_rows(repo, since, load_merges(d) or [], groups, entries["entered"])
    write(d / "merges.tsv", "\t".join(TSV) + "\n" + "".join("\t".join(str(r[k]) for k in TSV) + "\n" for r in rows))
    write(d / "roster.json", json.dumps(roster_lib.show_roster(str(repo), ref)))
    bus, _ = review_strength.load(repo, "origin")
    write(d / "verdicts.json", json.dumps({"verdicts": [dict(pr=v["pr"], head=v["head"], kind=v["kind"], cls=v["cls"],
                                                              t=v["t"].isoformat()) for v in bus]}))
    return fetch_runs(d, gh_repo, since, paginate)


def fetch_runs(d: Path, gh_repo: str, since: float, paginate) -> list[str]:
    """runs.json, ci_runs.json and the job listings not yet cached at a run's latest attempt."""
    listed = paginate(f"repos/{gh_repo}/actions/workflows/ci.yml/runs",
                      {"created": f">={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(since))}", "status": "completed"})
    ci = [{"id": r["id"], "t": r["created_at"], "c": r["conclusion"], "attempt": r["run_attempt"]} for r in listed]
    main = [x for x, r in zip(ci, listed) if r["event"] == "push" and r["head_branch"] == "main"]
    write(d / "ci_runs.json", json.dumps(ci))
    write(d / "runs.json", json.dumps(main))
    todo = [r for r in ci if (read_json(d / "jobs" / f"jobs_{r['id']}.json") or {}).get("attempt") != r["attempt"]]
    keep = ("name", "conclusion", "started_at", "completed_at", "run_attempt")
    for r in todo[:JOB_FETCH_MAX]:
        jobs = paginate(f"repos/{gh_repo}/actions/runs/{r['id']}/jobs", {"filter": "all"})
        write(d / "jobs" / f"jobs_{r['id']}.json",
              json.dumps({"attempt": r["attempt"], "jobs": [{k: j.get(k) for k in keep} for j in jobs]}))
    left = len(todo) - JOB_FETCH_MAX
    return [f"round_metrics: {left} job listings left for the next pass"] if left > 0 else []


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        import round_metrics_selftest
        tests = Path(argv[argv.index("--tests") + 1]) if "--tests" in argv else HERE.parents[2] / "tests"
        return round_metrics_selftest.run(Path(__file__), "--no-mutants" not in argv, tests)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["report", "produce"])
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--round", type=int)
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--weeks", action="store_true")
    ap.add_argument("--gh-repo")
    ap.add_argument("--roster-ref")
    a = ap.parse_args(argv)
    if a.cmd == "produce":
        if not a.gh_repo:
            ap.error("produce needs --gh-repo")
        print("\n".join(produce(a.dir, a.repo, a.gh_repo, a.roster_ref)))
        return 0
    now = time.time()
    if a.round is not None:
        w = round_window(a.repo, a.round, now)
        if w is None:
            print(f"round {a.round} unread (no tag v{a.round - 1}.0.0 opens it)")
            return 0
        start, end, state = w
        objective = read_json(a.repo / "dev/audit/config/objective.json")
        cap = ((objective.get("thresholds") or {}).get("closure_slip_ceiling") or {}).get("value") if objective else "unread"
        rnd = {"n": a.round, "repo": a.repo, "start": start, "end": end, "state": state, "ceiling": cap}
    elif a.since:
        start, end = epoch(a.since), epoch(a.until) if a.until else now
        state, rnd = "given", None
    else:
        ap.error("report needs --round or --since")
    spans = [(start, end)] + (weeks(start, end) if a.weeks else [])
    for k, (s, e) in enumerate(spans):
        name = "window" if k == 0 else f"week {k}" + (" (short)" if e - s < WEEK_S else "")
        print(f"== {name} {iso(s)} .. {iso(e)} ({state})")
        print("\n".join(window_lines(a.dir, s, e, gate_checks(a.repo, s, e), rnd)))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main(sys.argv[1:]))
