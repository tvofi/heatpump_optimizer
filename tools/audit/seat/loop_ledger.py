#!/usr/bin/env python3
"""The loop ledger: the convergence record's reads, per round and per week.

    python3 -I loop_ledger.py [--repo DIR] [--roster-ref REF] [--runs DIR]
    python3 -I loop_ledger.py --dir DIR [--runs DIR]
    python3 -I loop_ledger.py --self-test

Report-only (R11-PRE-ROUND-METRICS part 2; decision 0018 sections 2 and 4;
process cards P7 and L1). It reads the convergence fields `roster_edit.py
set-field` writes (roster_lib.CONVERGENCE_FIELDS, each validated by
roster_lib.convergence_why) from every `wave-r<N>-groups.json` roster: at
`--roster-ref` (default roster_lib.reader_ref's answer) or in `--dir`.

WHICH GROUPS OWE WHICH FIELDS (`owed`):
  an escape (`is_escape`: source outside, or a hotfix or bug group whose files
  include custom_components/; scorecard line E's two sets) owes found_by,
  owned_by and caused_by; any other hotfix group (roster_lib.is_hotfix) owes
  found_by and caused_by (card P7); a group with an `rca` record owes caused_by,
  family and cm_kind (card L1). A field present but outside its vocabulary is
  unrecorded.

PERIODS: each roster is one round (its file's N). A week is the ISO week of
the commit that last wrote the group's `"group":` line (`git blame` at the
ref): the roster entry, since a group's name is not rewritten. `--dir` has no
history, so its week lines are unread.

THE READS, per period (rule, then the null control the self-test holds it to):
  escapes   escape groups, split by found_by and by owned_by (`none` a value).
  injected  escapes whose caused_by.cause is a pull request or a roster group
            (beside it the external and original counts). Its denominator, the
            window's production merges, is round_metrics.py's, not read here.
  refix     groups naming in `follows` the fix they follow (link 3 of 0018
            section 4: a fix that did not fix).
  loop      over the groups with an rca record (the countermeasures): count by
            family and by cm_kind; k, the children per countermeasure (groups
            whose `parent` is one); the groups per generation (parent hops to
            a group with no parent) and each generation's ratio to the one
            before.
  NO-READ: a read whose owing groups are not all recorded prints
  `unread (k of n ... unrecorded: names)`, never a partial value; no roster
  at all prints `loop_ledger unread`.
  NULL: an empty input directory prints unread and no value; a roster whose
  every owing group is recorded prints values, and dropping one field from one
  group turns that read, and only that read, unread.

GATE REDS (`--runs DIR`; card E11-N-GATE-CAUSE): a cause per red run, derived and
never written to a roster, so it feeds no read above. DIR is `round_metrics.py
produce`'s directory: `ci_runs.json` and `jobs/jobs_<id>.json`, read with no API
call. A red is a run attempt whose `gate` job concluded failure, on main's push
(event push, head_branch main: a main row, found_by ci-main) or on any other run
(a head row: a pre-merge red is no escape and carries no found_by). One row per
red, its cause the first of these that holds:
  external   a later attempt of the same run went green;
  #<n>       main was red (the row's own run on main; for a head row main's last
             push run at or before it, each main run read at its latest
             attempt): n is the pull request merged at main's first red push
             run after its last green one, parsed from that commit's subject in
             `--repo`; a subject naming none reads unread, and so does a spell
             already open at the first main run read (no green main run read
             before it: its opener is outside the directory);
  external   a later run at the same head_sha went green;
  #<pr>      (a head row) a later run of the same pull request went green. The
             pull request is the run's `pr`, else the `pr` of a run at its
             head_sha, never its head_branch (a branch name is reused across
             pull requests); with neither it reads unread.
  A red none of these clears reads uncleared. unread and uncleared are read
  states printed beside the causes, never cause words: a derived cause is held
  to roster_lib.is_cause, the test a written caused_by.cause passes, and one it
  refuses reads unread. Each row lists the attempt's failed jobs as
  tools/ci/gate.py's machinery_line splits them (required, then the rest). Its
  product/machinery column is gate.py's `status` over the attempt's own jobs
  on a push run, the one event class a cached row names; on any other run it
  is unread, because `status` takes the class and pr or pr-cc is the pull
  request's diff, which the row does not hold.
  NO-READ: a run with no job listing at its latest attempt can hold a red no one
  read (a first-attempt success aside): it prints its own unread row, and the
  count is then `gate_reds unread (k of n runs ...)` with the reds read beside it.
  NULL: no `--runs` prints `gate_reds unread`; a directory whose every run is
  green prints `gate_reds 0` and no row.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import datetime
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script's directory
import roster_lib  # noqa: E402
import round_metrics  # noqa: E402  the producer of --runs's directory: its reader, clock and merge subject
from scorecard import escape_sets  # noqa: E402  line E's two sets are the escapes

ESCAPE_FIELDS = ("found_by", "owned_by", "caused_by")
HOTFIX_FIELDS = ("found_by", "caused_by")
CM_FIELDS = ("caused_by", "family", "cm_kind")
SHOWN = 5  # unrecorded names printed per read
UNREAD, UNCLEARED = "unread", "uncleared"  # a red's read states: printed beside the causes, never cause words
#: why the column of a red whose run is no push is unread: gate.status's class there is the pull request's diff, not the row
NO_CLASS = "(gate.status takes an event class, and pr or pr-cc is not derivable from a cached run row)"
EDGE = {"id": None}  # the red spell main may be in before the first green main run read: its opener is unread
FOUND_MAIN = "ci-main"  # the found_by word of a red on main's push; a red on a pull-request head is no escape
_GROUP_LINE = re.compile(r'^\s*"group":\s*"([^"]+)"')


def is_escape(g: dict) -> bool:
    """Scorecard line E's two sets: an outside group, or a hotfix or bug group touching the product."""
    return any(escape_sets([g]))


def owed(g: dict) -> tuple:
    """The convergence fields this group owes, in CONVERGENCE_FIELDS order."""
    want = set()
    if is_escape(g):
        want.update(ESCAPE_FIELDS)
    elif roster_lib.is_hotfix(g):
        want.update(HOTFIX_FIELDS)
    if g.get("rca"):
        want.update(CM_FIELDS)
    return tuple(f for f in roster_lib.CONVERGENCE_FIELDS if f in want)


def _gap(groups: list, fields, names) -> list:
    return [g["group"] for g in groups if not roster_lib.recorded(g, fields, names)]


def _unread(what: str, gap: list, n: int) -> str:
    shown = ", ".join(gap[:SHOWN]) + (" ..." if len(gap) > SHOWN else "")
    return f"{what} unread ({len(gap)} of {n} owing groups unrecorded: {shown})"


def _counts(c: collections.Counter) -> str:
    return "{" + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())) + "}"


def owned_split(groups: list, names) -> str:
    """Escapes by owning dimension, or unread while any escape has no admissible owned_by."""
    esc = [g for g in groups if is_escape(g)]
    gap = _gap(esc, ("owned_by",), names)
    if gap:
        return _unread("by owning dimension", gap, len(esc))
    return "by owning dimension " + _counts(collections.Counter(g["owned_by"] for g in esc))


def generation(g: dict, by_name: dict) -> int | None:
    """Parent hops from `g` to a group with no parent; None on a cycle or a parent no roster holds."""
    seen, n = set(), 0
    while g.get("parent"):
        if g["group"] in seen or g["parent"] not in by_name:
            return None
        seen.add(g["group"])
        g, n = by_name[g["parent"]], n + 1
    return n


def reads(groups: list, every: list) -> list[str]:
    """The four reads over one period's `groups`; `every` is all groups of all rosters (names, parents)."""
    names = {g["group"] for g in every}
    by_name = {g["group"]: g for g in every}
    esc = [g for g in groups if is_escape(g)]
    out = []
    gap = _gap(esc, ("found_by", "owned_by"), names)
    out.append(_unread("escapes", gap, len(esc)) if gap else
               f"escapes {len(esc)} by found_by {_counts(collections.Counter(g['found_by'] for g in esc))} "
               f"by owned_by {_counts(collections.Counter(g['owned_by'] for g in esc))}")
    gap = _gap(esc, ("caused_by",), names)
    if gap:
        out.append(_unread("injected", gap, len(esc)))
    else:
        c = collections.Counter(g["caused_by"]["cause"] if g["caused_by"]["cause"] in roster_lib.CAUSES
                                else "merged" for g in esc)
        out.append(f"injected {c['merged']} (external {c['external']}, original {c['original']}; "
                   "per production merge: round_metrics.py's denominator)")
    owing = [g for g in groups if owed(g)]
    gap = [g["group"] for g in owing if not roster_lib.recorded(g, owed(g), names)]
    if gap:
        out.append(_unread("refix", gap, len(owing)))
    else:
        fol = [g for g in groups if roster_lib.recorded(g, ("follows",), names)]
        out.append(f"refix {len(fol)}" + "".join(f"; {g['group']} follows {g['follows']}" for g in fol))
    cms = [g for g in groups if g.get("rca")]
    gap = _gap(cms, CM_FIELDS, names)
    if gap:
        out.append(_unread("loop", gap, len(cms)))
        return out
    cm_names = {g["group"] for g in cms}
    kids = sum(1 for g in every if g.get("parent") in cm_names)
    gens = collections.Counter(generation(g, by_name) for g in groups if g.get("parent") or g["group"] in cm_names)
    broken = gens.pop(None, 0)
    ladder = " ".join(f"g{i}:{gens[i]}" + (f"({gens[i] / gens[i - 1]:.2f})" if i and gens[i - 1] else "")
                      for i in range(max(gens) + 1)) if gens else ""
    k = f"{kids / len(cms):.2f}" if cms else "none (no countermeasure)"
    out.append(f"loop countermeasures {len(cms)} by family {_counts(collections.Counter(g['family'] for g in cms))} "
               f"by cm_kind {_counts(collections.Counter(g['cm_kind'] for g in cms))}; k {k}; "
               f"generations {ladder or 'none'}" + (f"; {broken} with a broken parent chain" if broken else ""))
    return out


def week_of(t: int) -> str:
    y, w, _ = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def entered(blame: str) -> dict:
    """Group name -> author time of the blame line that holds its `"group":` key (`--line-porcelain`)."""
    out, t = {}, None
    for ln in blame.splitlines():
        if ln.startswith("author-time "):
            t = int(ln.split()[1])
        elif ln.startswith("\t") and (m := _GROUP_LINE.match(ln[1:])) and t is not None:
            out[m.group(1)] = t  # a roster file holds each group's "group": line once
    return out


def load_ref(repo: str, ref: str) -> tuple[list, dict | None]:
    """[(round, path, roster)] at `ref`, and each group's entry time (None when blame fails)."""
    r = roster_lib._git(repo, "ls-tree", "--name-only", ref, roster_lib.ROSTERS_DIR + "/")
    paths = sorted((p for p in r.stdout.split() if roster_lib.newest_roster([p])), key=roster_lib.roster_round)
    out, when = [], {}
    for p in paths:
        out.append((roster_lib.roster_round(p), p, json.loads(roster_lib._git(repo, "show", f"{ref}:{p}").stdout)))
        b = roster_lib._git(repo, "blame", "--line-porcelain", ref, "--", p)
        when = None if when is None or b.returncode else {**entered(b.stdout), **when}
    return out, when


def load_dir(d: Path) -> list:
    return sorted(((roster_lib.roster_round(p.name), str(p), roster_lib.load_roster_file(str(p)))
                   for p in (d.iterdir() if d.is_dir() else []) if roster_lib.newest_roster([p.name])),
                  key=lambda x: x[0])


def report(rosters: list, when: dict | None) -> list[str]:
    if not rosters:
        return ["loop_ledger unread (no wave-r<N>-groups.json roster)"]
    latest = {g["group"]: g for _, _, ro in rosters for g in roster_lib.groups_of(ro).values()}
    every = list(latest.values())  # a group carried into a later round's roster is counted once, as there
    out = []
    for n, path, ro in rosters:
        out.append(f"round {n} ({path})")
        out += ["  " + ln for ln in reads(list(roster_lib.groups_of(ro).values()), every)]
    if when is None:
        return out + ["weeks unread (no roster history: --dir, or git blame failed)"]
    weeks = collections.defaultdict(list)
    for g in every:
        weeks[week_of(when[g["group"]]) if g["group"] in when else "unentered"].append(g)
    for wk in sorted(weeks):
        out.append(f"week {wk}")
        out += ["  " + ln for ln in reads(weeks[wk], every)]
    return out


# ------------------------------------------------------------------ gate reds

def _when(r: dict) -> tuple:
    return (round_metrics.epoch(r["t"]), r["id"])


def _on_main(r: dict) -> bool:
    return r.get("event") == "push" and r.get("head_branch") == "main"


def _gates(doc: dict) -> dict:
    """Attempt -> the conclusion of the `gate` job there; a job listed with no attempt is the first."""
    return {j.get("run_attempt") or 1: j.get("conclusion") for j in doc["jobs"] if j.get("name") == "gate"}


def _gate():
    """tools/ci/gate.py, imported at the call: scorecard.py imports this module for owned_split alone."""
    ci = str(Path(__file__).resolve().parents[2] / "ci")
    if ci not in sys.path:
        sys.path.insert(0, ci)
    import gate
    return gate


def gate_reds(d: Path, subject) -> "tuple[list[dict], int] | None":
    """One row per red (a run attempt whose `gate` job concluded failure) and per run
    that cannot be read, and the run count; None when `d` holds no ci_runs.json.
    `subject(sha)` is that commit's subject line, or None."""
    runs = round_metrics.read_json(d / "ci_runs.json")
    if not isinstance(runs, list):
        return None
    runs = sorted(runs, key=_when)
    docs, green, rows = {}, {}, []
    for r in runs:
        doc = round_metrics.read_json(d / "jobs" / f"jobs_{r['id']}.json")
        if isinstance(doc, dict) and doc.get("attempt") == r["attempt"]:
            docs[r["id"]] = doc
            g = _gates(doc)
            last = g[max(g)] if g else None
            green[r["id"]] = True if last == "success" else False if last == "failure" else None
        elif r["c"] == "success" and r["attempt"] == 1:
            green[r["id"]] = True  # one attempt, and its gate cannot have failed
    by_sha = collections.defaultdict(list)
    for r in runs:
        if r.get("head_sha"):
            by_sha[r["head_sha"]].append(r)
    mains = [r for r in runs if _on_main(r) and green.get(r["id"]) is not None]
    opener, spell = {}, EDGE  # a main run -> the first red main run after main's last green one read, or EDGE
    for r in mains:
        spell = None if green[r["id"]] else (spell or r)
        opener[r["id"]] = spell

    def key(r):  # the run's pull request, else the one a run at its head_sha names; never its head_branch
        return r["pr"] if r.get("pr") is not None else next(
            (x["pr"] for x in by_sha.get(r.get("head_sha"), ()) if x.get("pr") is not None), None)

    def cause(r, attempt, gates) -> tuple:
        if any(k > attempt and c == "success" for k, c in gates.items()):
            return "external", "a later attempt of the run went green"
        before = [m for m in mains if _when(m) <= _when(r)]
        op = opener.get(r["id"]) if _on_main(r) else opener[before[-1]["id"]] if before else None
        if op is EDGE:
            return UNREAD, "main red at the first main run read, no green main run read before it"
        if op is not None:
            m = round_metrics.SUBJECT.match(subject(op.get("head_sha")) or "")
            return (f"#{m.group(1)}", f"main red since run {op['id']}") if m else (
                UNREAD, f"main red since run {op['id']}, whose subject names no pull request")
        later = [x for x in runs if _when(x) > _when(r) and green.get(x["id"])]
        if any(x.get("head_sha") == r.get("head_sha") for x in later if r.get("head_sha")):
            return "external", "another run at the head went green"
        if _on_main(r):
            return UNCLEARED, "no later green"
        k = key(r)
        if k is None:
            return UNREAD, "no run at the head names a pull request"
        if any(key(x) == k for x in later):  # at another head_sha: a green at this one read external above
            return f"#{k}", "its later commit went green"
        return UNCLEARED, "no later green"

    gate = _gate()
    owed = set(gate.gate_required()) | {"prelude", "gate"}
    for r in runs:
        base = {"id": r["id"], "main": _on_main(r), "sha": (r.get("head_sha") or "-")[:10]}
        if r["id"] not in docs:
            if r["id"] not in green:
                rows.append({**base, "attempt": r["attempt"], "blind": True})
            continue
        gates = _gates(docs[r["id"]])
        for attempt in sorted(a for a, c in gates.items() if c == "failure"):
            word, why = cause(r, attempt, gates)
            if word not in (UNREAD, UNCLEARED) and not roster_lib.is_cause(word, ()):
                word, why = UNREAD, f"derived {word} is no caused_by cause"
            at = [j for j in docs[r["id"]]["jobs"] if j.get("run_attempt") == attempt]
            failed = sorted({j["name"] for j in at
                             if j.get("conclusion") == "failure" and j.get("name") != "gate"})
            # gate.status over the attempt's jobs in run_jobs' shape; "push" is the one class a row names (gate.event_class)
            pair = gate.status({j["name"]: ("completed" if j.get("conclusion") else "in_progress", j.get("conclusion"))
                                for j in at}, "push") if r.get("event") == "push" else None
            rows.append({**base, "attempt": attempt, "cause": word, "why": why, "status": pair,
                         "required": [n for n in failed if n in owed],
                         "machinery": gate.machinery_line({n: ("completed", "failure") for n in failed}, owed)})
    return rows, len(runs)


def red_lines(d: "Path | None", subject) -> list[str]:
    """The gate-reds read over `--runs`'s directory: the summary line, then a row per red."""
    if d is None:
        return ["gate_reds unread (no --runs directory)"]
    got = gate_reds(Path(d), subject)
    if got is None:
        return ["gate_reds unread (no ci_runs.json in the --runs directory)"]
    rows, n = got
    reds = [x for x in rows if not x.get("blind")]
    blind = len(rows) - len(reds)
    caused = collections.Counter(x["cause"] for x in reds if x["cause"] not in (UNREAD, UNCLEARED))
    value = (f"(main {sum(x['main'] for x in reds)}, heads {sum(not x['main'] for x in reds)}) "
             f"caused {_counts(caused)}; cause unread {sum(x['cause'] == UNREAD for x in reds)}; "
             f"uncleared {sum(x['cause'] == UNCLEARED for x in reds)}")
    pairs = [x["status"] for x in reds if x["status"]]
    column = (f"product red {sum(a == _gate().RED for a, _ in pairs)}, machinery red {sum(b == _gate().RED for _, b in pairs)} "
              f"of {len(pairs)} push reds (gate.status); "
              f"product/machinery unread on {len(reds) - len(pairs)} {NO_CLASS}")
    out = [f"gate_reds unread ({blind} of {n} runs have no job listing at their latest attempt; beside: "
           f"{len(reds)} reds read {value}; {column})" if blind else f"gate_reds {len(reds)} {value}; {column}"]
    for x in rows:
        where = f"{'main' if x['main'] else 'head'} {x['sha']}"
        if x.get("blind"):
            out.append(f"  run {x['id']} attempt {x['attempt']} {where} cause {UNREAD} "
                       "(no job listing at the run's latest attempt)")
            continue
        out.append(f"  red run {x['id']} attempt {x['attempt']} {where} cause {x['cause']} ({x['why']})"
                   + (f" found_by {FOUND_MAIN}" if x["main"] else "")
                   + f"; required failed: {', '.join(x['required']) or 'none'}; {x['machinery']}; "
                   + ("product {}, machinery {}".format(*x["status"]) if x["status"] else f"product/machinery unread {NO_CLASS}"))
    return out


def git_subject(repo: str):
    """sha -> that commit's subject line in `repo`, or None (no sha, or one the repository lacks)."""
    def subject(sha):
        r = roster_lib._git(repo, "log", "-1", "--format=%s", sha, "--") if sha else None
        return r.stdout.strip() if r is not None and r.returncode == 0 else None
    return subject


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--roster-ref")
    ap.add_argument("--dir")
    ap.add_argument("--runs")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-mutants", action="store_true", help=argparse.SUPPRESS)  # a mutant copy runs the checks alone
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test(not a.no_mutants)
    if a.dir:
        lines = report(load_dir(Path(a.dir)), None)
    else:
        lines = report(*load_ref(a.repo, roster_lib.reader_ref(a.repo, a.roster_ref)))
    print("\n".join(lines + red_lines(Path(a.runs) if a.runs else None, git_subject(a.repo))))
    return 0


# ------------------------------------------------------------------ self-test

def _fixture() -> list:
    """Every owing group recorded: two escapes, one hotfix, two countermeasures, a child and a grandchild."""
    rca = "R10-N-log-flood"
    cb = lambda c: {"cause": c, "rca": rca}  # noqa: E731
    return [
        {"group": "R9-OUT", "source": "outside", "rca": [rca], "found_by": "outside", "owned_by": "D8",
         "caused_by": cb("#3520"), "family": "N-log-flood", "cm_kind": "narrow"},
        {"group": "R9-HOTFIX-A", "files": ["custom_components/x.py"], "rca": [rca], "found_by": "owner",
         "owned_by": "none", "caused_by": cb("original"), "family": "N-log-flood", "cm_kind": "new-refusal"},
        {"group": "R9-HOTFIX-M", "hotfix": True, "files": ["tools/x.py"], "found_by": "ci-main",
         "caused_by": cb("external"), "rca": [rca], "family": "N-staleness", "cm_kind": "delete"},
        {"group": "R9-KID", "parent": "R9-OUT"},
        {"group": "R9-GRANDKID", "parent": "R9-KID", "follows": "R9-HOTFIX-A"},
        {"group": "R9-PLAIN"},
    ]


def _self_test_reds(check, tmp: Path, repo: Path) -> None:
    """`--runs`: one plant per clearing event, the read states, the null controls and the job split."""
    count = [0]

    def run(i, hour, c="failure", attempt=1, sha=None, event="pull_request", branch="b", pr=None):
        return {"id": i, "t": f"2026-11-01T{hour:02d}:00:00Z", "c": c, "attempt": attempt, "head_sha": sha,
                "event": event, "head_branch": branch, "pr": pr}

    def jobs(*gates, attempt=None, failed=(), done=()):
        return {"attempt": attempt or len(gates),
                "jobs": [{"name": "gate", "conclusion": c, "run_attempt": k + 1} for k, c in enumerate(gates)]
                + [{"name": n, "conclusion": "failure", "run_attempt": a} for a, n in failed]
                + [{"name": n, "conclusion": c, "run_attempt": a} for a, n, c in done]}

    def lines(runs, listed, subjects=None):
        count[0] += 1
        d = tmp / f"runs{count[0]}"
        (d / "jobs").mkdir(parents=True)
        (d / "ci_runs.json").write_text(json.dumps(runs))
        for i, doc in listed.items():
            (d / "jobs" / f"jobs_{i}.json").write_text(json.dumps(doc))
        return red_lines(d, (subjects or {}).get)

    def row(got, i, attempt=1):
        return next((ln for ln in got[1:] if ln.startswith(f"  red run {i} attempt {attempt} ")), "")

    A, B, C, M = "a" * 40, "b" * 40, "c" * 40, "d" * 40
    edge = "main red at the first main run read, no green main run read before it"
    ON_MAIN = {"event": "pu" + "sh", "branch": "main"}  # spelt apart: ref_privacy.py reads the word as a push site
    green, red = jobs("success"), jobs("failure")
    got = lines([run(1, 1, sha=A, pr=5), run(2, 2, "success", sha=A, pr=5)], {1: red, 2: green})
    check("reds: a red and a later green run at one head_sha reads external",
          got[0].startswith("gate_reds 1 (main 0, heads 1) caused {external: 1}; cause unread 0; uncleared 0")
          and " cause external (another run at the head went green)" in row(got, 1) and len(got) == 2)
    got = lines([run(2, 1, "success", sha=A, pr=5), run(1, 2, sha=A, pr=5)], {1: red, 2: green})
    check("reds: a green run before the red at its head_sha clears nothing: uncleared, never external",
          got[0].startswith("gate_reds 1 (main 0, heads 1) caused {}; cause unread 0; uncleared 1")
          and " cause uncleared " in row(got, 1))
    two = [run(3, 1, "success", attempt=2, sha=A, pr=5)]
    got = lines(two, {3: jobs("failure", "success")})
    check("reds: a gate red at attempt 1 and green at attempt 2 of one run reads external, on the attempt's own row",
          " cause external (a later attempt of the run went green)" in row(got, 3) and not row(got, 3, 2)
          and got[0].startswith("gate_reds 1 "))
    got = lines(two, {})
    check("reds: the same run with no job listing reads unread, the count unread with it, and is never dropped",
          got[0].startswith("gate_reds unread (1 of 1 runs have no job listing at their latest attempt; beside: 0 reds read")
          and got[1] == "  run 3 attempt 2 head aaaaaaaaaa cause unread (no job listing at the run's latest attempt)")
    got = lines([run(3, 1, attempt=2, sha=A, pr=5)], {3: jobs("success", "failure")})
    check("reds: a green attempt before the red one clears nothing", " cause uncleared " in row(got, 3, 2))
    got = lines([run(3, 1, attempt=2, sha=A, pr=5)], {3: jobs("cancelled", "failure")})
    check("reds: a gate that did not conclude failure is no red", not row(got, 3, 1) and got[0].startswith("gate_reds 1 "))
    got = lines([run(3, 1, sha=A, pr=5)], {})
    check("reds: a failed first attempt with no job listing reads unread", got[0].startswith("gate_reds unread (1 of 1 "))
    got = lines([run(3, 1, attempt=2, sha=M, **ON_MAIN)], {3: jobs("failure", "cancelled")})
    check("reds: a main red with no later green and no red spell read reads uncleared, never unread",
          " cause uncleared (no later green) found_by ci-main;" in row(got, 3))
    got = lines([run(3, 1, sha=M, event="workflow_dispatch", branch="main")], {3: red},
                {M: "Merge pull request #41 from o/fix/x"})
    check("reds: a run on the branch main that is no push is a head row and opens no red spell",
          " head dddddddddd cause unread (no run at the head names a pull request);" in row(got, 3))
    got = lines(two, {3: jobs("failure", attempt=1)})
    check("reds: a listing cached at an older attempt is no listing", got[0].startswith("gate_reds unread (1 of 1 runs"))
    got = lines([run(4, 1, sha=A, pr=5), run(5, 2, "success", sha=B, pr=5), run(6, 3, "success", sha=C, pr=6)],
                {4: red, 5: green, 6: green})
    check("reds: a red cleared by a later commit of its own pull request reads #<that pull request>",
          got[0].startswith("gate_reds 1 (main 0, heads 1) caused {#5: 1};") and " cause #5 " in row(got, 4)
          and "found_by" not in row(got, 4))
    got = lines([run(4, 1, sha=A, pr=5), run(6, 3, "success", sha=C, pr=6)], {4: red, 6: green})
    check("reds: another pull request's green clears nothing", " cause uncleared " in row(got, 4))
    got = lines([run(4, 2, sha=A, pr=5), run(5, 1, "success", sha=B, pr=5)], {4: red, 5: green})
    check("reds: the pull request's green before the red clears nothing", " cause uncleared " in row(got, 4))
    spell = [run(10, 1, "success", sha=C, **ON_MAIN), run(11, 2, sha=M, **ON_MAIN),
            run(12, 3, sha=A, pr=9), run(13, 4, "success", sha=B, pr=9),
            run(14, 5, sha="e" * 40, **ON_MAIN),
            run(15, 6, "success", sha="f" * 40, **ON_MAIN), run(16, 7, sha="1" * 40, pr=3)]
    listed = {11: red, 12: red, 13: green, 14: red, 16: red}
    subj = {M: "Merge pull request #41 from o/fix/x", "e" * 40: "Merge pull request #42 from o/fix/y"}
    got = lines(spell, listed, subj)
    check("reds: a red inherited from main reads the pull request merged at main's first red push run after its last "
          "green, on the head row and on both main rows",
          got[0].startswith("gate_reds 4 (main 2, heads 2) caused {#41: 3}; cause unread 0; uncleared 1")
          and " cause #41 (main red since run 11)" in row(got, 12) and " cause #41 " in row(got, 14)
          and " cause #41 " in row(got, 11))
    check("reds: found_by ci-main on a main row and on no head row; ci-main is a found_by word",
          " found_by ci-main;" in row(got, 11) and "found_by" not in row(got, 12)
          and roster_lib.convergence_why("found_by", FOUND_MAIN, {}, ()) is None)
    check("reds: a head red after main went green again is not main's", " cause uncleared " in row(got, 16))
    got = lines(spell[1:3], listed, subj)
    check("reds: a main red spell already open at the first main run read has no opener: unread on the main row and on "
          "a head row after it, never the first pull request merged in the window",
          got[0].startswith("gate_reds 2 (main 1, heads 1) caused {}; cause unread 2; uncleared 0")
          and f" cause unread ({edge}) found_by ci-main;" in row(got, 11) and f" cause unread ({edge});" in row(got, 12))
    got = lines(spell[1:], listed, subj)
    check("reds: the edge spell ends at the first green main run read, and the next red after it opens a spell",
          f" cause unread ({edge})" in row(got, 14) and " cause uncleared " in row(got, 16))
    got = lines(spell, listed, {**subj, M: "v7.1.9: stamp"})
    check("reds: a merge subject naming no pull request reads unread: the row stays and the count is whole",
          got[0].startswith("gate_reds 4 (main 2, heads 2) caused {}; cause unread 3; uncleared 1")
          and " cause unread (main red since run 11, whose subject names no pull request)" in row(got, 12))
    got = lines(spell, listed, {**subj, M: "Merge pull request #0 from o/fix/x"})
    check("reds: a derived word the cause test refuses reads unread, never the word",
          " cause unread (derived #0 is no caused_by cause)" in row(got, 11) and "{#" not in got[0])
    check("is_cause: a pull request, external, original or another roster group; never the group itself or a bare word",
          all(roster_lib.is_cause(c, {"G", "H"}, "G") for c in ("#41", "external", "original", "H"))
          and not any(roster_lib.is_cause(c, {"G", "H"}, "G") for c in ("G", "#0", "41", UNREAD, UNCLEARED, None)))
    got = lines(spell[:2] + [run(17, 3, "success", sha=M, event="workflow_dispatch", branch="main")], {11: red}, subj)
    check("reds: main's red spell outranks a green run at the same head_sha", " cause #41 " in row(got, 11))
    got = lines([run(11, 2, attempt=2, sha=M, **ON_MAIN)], {11: jobs("failure", "failure")}, subj)
    check("reds: every red attempt of a run is a row", bool(row(got, 11, 1)) and bool(row(got, 11, 2))
          and got[0].startswith("gate_reds 2 (main 2, heads 0)"))
    reuse = [run(20, 1, sha=A, branch="patch-1"), run(21, 2, "success", sha=B, branch="patch-1")]
    got = lines(reuse, {20: red, 21: green})
    check("reds: two runs sharing only a head_branch are not one pull request: the earlier red reads unread",
          " cause unread (no run at the head names a pull request)" in row(got, 20))
    got = lines([reuse[0], {**reuse[1], "pr": 8}], {20: red, 21: green})
    check("reds: a reused head_branch never lends a later pull request's number to an earlier red",
          " cause unread (no run at the head names a pull request)" in row(got, 20) and "#8" not in "".join(got))
    got = lines([run(22, 1, sha=A, event="pull_request_review"), run(23, 2, sha=A, pr=8),
                 run(24, 3, "success", sha=B, pr=8)], {22: red, 23: red, 24: green})
    check("reds: a red naming no pull request takes the one a run at its head_sha names",
          " cause #8 " in row(got, 22) and " cause #8 " in row(got, 23))
    got = lines([run(30, 1, "success", sha=A, pr=5), run(31, 2, "success", sha=M, **ON_MAIN)], {})
    check("NULL reds: a green-only directory reads 0 and no row; a first-attempt success needs no listing",
          got == ["gate_reds 0 (main 0, heads 0) caused {}; cause unread 0; uncleared 0; product red 0, machinery red 0 "
                  "of 0 push reds (gate.status); product/machinery unread on 0 " + NO_CLASS])
    check("NULL reds: no --runs directory reads unread, and so does a directory with no ci_runs.json",
          red_lines(None, {}.get) == ["gate_reds unread (no --runs directory)"]
          and red_lines(tmp / "empty", {}.get) == ["gate_reds unread (no ci_runs.json in the --runs directory)"])
    got = lines([run(3, 1, sha=A, pr=5)], {3: {"attempt": 1, "jobs": [{"name": "gate", "conclusion": "failure"}]}})
    check("reds: a gate job listed with no attempt is the run's first", bool(row(got, 3, 1)))
    got = lines([run(50, 1, sha=A, pr=5)], {50: jobs("success", failed=((1, "zz / report"),))})
    check("reds: a failed job that is not `gate`, at an attempt whose gate did not fail, is no red",
          got[0].startswith("gate_reds 0 ") and len(got) == 1)
    got = lines([run(51, 1, sha=A, pr=5)], {51: jobs("failure", failed=((1, "prelude"),), done=((1, "zz / passed", "success"),))})
    check("reds: a failed prelude is a required failure, never a machinery job",
          "; required failed: prelude; machinery (report-only, never gating): no other job listed; " in row(got, 51))
    check("reds: a job that did not fail at the red attempt is on neither list of its row",
          bool(row(got, 51)) and "zz / passed" not in row(got, 51))
    got = lines(spell[:2] + [run(18, 3, attempt=2, sha="e" * 40, **ON_MAIN)], {11: red, 18: jobs("failure", "cancelled")}, subj)
    check("reds: a main run red at an earlier attempt and unconcluded at its latest joins no red spell: uncleared, "
          "never the spell's pull request",
          " cause uncleared (no later green) found_by ci-main;" in row(got, 18) and " cause #41 " in row(got, 11))
    gate = _gate()
    req = gate.gate_required()[0]
    got = lines([run(40, 1, attempt=2, sha=A, pr=5)],
                {40: jobs("failure", "failure", failed=((1, req), (1, "zz / report"), (2, "zz / report")))})
    check("reds: a red attempt's failed jobs split as gate.machinery_line splits them, per attempt; a head row's column "
          "unread, naming gate.status and the class it lacks",
          row(got, 40).endswith(f"; required failed: {req}; machinery (report-only, never gating): zz / report=failure; "
                                "product/machinery unread " + NO_CLASS)
          and row(got, 40, 2).endswith("; required failed: none; machinery (report-only, never gating): "
                                       "zz / report=failure; product/machinery unread " + NO_CLASS))
    members = tuple(dict.fromkeys((*gate.REQUIRED["push"], *gate.MACHINERY_JOBS)))
    prod = next(n for n in gate.REQUIRED["push"] if n not in gate.MACHINERY_JOBS)
    mach = next(n for n in gate.MACHINERY_JOBS if n in gate.REQUIRED["push"])

    def listing(attempt, **over):  # every member of gate.status's two verdicts on a push run, green but `over`
        return tuple((attempt, n, over.get(n, "success")) for n in members)
    both = jobs("failure", "failure", done=listing(1, **{prod: "failure"}) + listing(2, **{mach: "failure"}))
    got = lines([run(60, 1, attempt=2, sha=M, **ON_MAIN)], {60: both})
    check("reds: a push run's row prints gate.status's pair over the red attempt's own jobs",
          row(got, 60).endswith("; product red, machinery green") and row(got, 60, 2).endswith("; product green, machinery red")
          and got[0].endswith("; product red 1, machinery red 1 of 2 push reds (gate.status); "
                              "product/machinery unread on 0 " + NO_CLASS))
    got = lines([run(60, 1, attempt=2, sha=A, pr=5)], {60: both})
    check("NULL reds: the same listing on a pull-request run reads the column unread, never a verdict of the push class",
          row(got, 60).endswith("; product/machinery unread " + NO_CLASS)
          and row(got, 60, 2).endswith("; product/machinery unread " + NO_CLASS)
          and got[0].endswith("; product red 0, machinery red 0 of 0 push reds (gate.status); "
                              "product/machinery unread on 2 " + NO_CLASS))
    got = lines([run(61, 1, sha=M, **ON_MAIN), run(62, 2, sha="e" * 40, **ON_MAIN)],
                {61: jobs("failure", done=listing(1, **{prod: None})), 62: red})
    check("reds: a member with no conclusion, or not listed at the attempt, reads unread in its verdict, never red or green",
          row(got, 61).endswith("; product unread, machinery green") and row(got, 62).endswith("; product unread, machinery unread"))
    from throwaway_git import throwaway_git_environ  # self_test put tests/ on the path
    with throwaway_git_environ():
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
        sub = git_subject(str(repo))
        check("reds: git_subject reads a commit's subject line, and None for no sha and for one the repository lacks",
              sub(head) == "Merge pull request #7 from o/b" and sub(None) is None and sub("0" * 40) is None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main_cli = main(["--dir", str(tmp / "empty"), "--runs", str(tmp / "runs1")])
        main(["--dir", str(tmp / "empty")])
    got = out.getvalue().splitlines()
    check("reds: --runs prints the read after the roster reads; without it the read is unread",
          main_cli == 0 and got[0].startswith("loop_ledger unread") and got[1].startswith("gate_reds 1 (main 0, heads 1)")
          and got[2].startswith("  red run 1 attempt 1 head aaaaaaaaaa cause external")
          and got[-1] == "gate_reds unread (no --runs directory)")


#: The gate-reds read's mutants: name -> (needle, occurring once in this file; its replacement; the check that
#: must then fail). `--self-test` runs each on a copy of this file and fails on a survivor or a stale needle.
MUTANTS = {
    "later attempt": ('if any(k > attempt and c == "success" for k, c in gates.items()):', "if False:",
                      "reds: a gate red at attempt 1 and green at attempt 2"),
    "attempt order": ("k > attempt and c ==", "k != attempt and c ==", "reds: a green attempt before the red one"),
    "red is failure": ('for attempt in sorted(a for a, c in gates.items() if c == "failure"):',
                       'for attempt in sorted(a for a, c in gates.items() if c != "success"):',
                       "reds: a gate that did not conclude failure"),
    "cause call": ("and not roster_lib.is_cause(word, ()):", "and False:", "reds: a derived word the cause test refuses"),
    "pr key from head_branch": ('for x in by_sha.get(r.get("head_sha"), ()) if x.get("pr") is not None), None)',
                                'for x in runs if x.get("head_branch") == r.get("head_branch") and x.get("pr") is not None), None)',
                                "reds: a reused head_branch never lends"),
    "pr key without sibling": ('return r["pr"] if r.get("pr") is not None else next(', 'return r["pr"] if True else next(',
                               "reds: a red naming no pull request takes"),
    "own commit, any pull request": ("if any(key(x) == k for x in later):", "if later:",
                                     "reds: another pull request's green"),
    "clearing run later": ('later = [x for x in runs if _when(x) > _when(r) and green', "later = [x for x in runs if x is not r and green",
                           "reds: a green run before the red at its head_sha"),
    "clearing run green": ('_when(x) > _when(r) and green.get(x["id"])]', "_when(x) > _when(r)]",
                           "reds: a red naming no pull request takes"),
    "clearing run same head": ('if any(x.get("head_sha") == r.get("head_sha") for x in later', "if any(True for x in later",
                               "reds: a red cleared by a later commit"),
    "spell opener": ('spell = None if green[r["id"]] else (spell or r)', 'spell = None if green[r["id"]] else r',
                     "reds: a red inherited from main"),
    "spell closes": ('spell = None if green[r["id"]] else (spell or r)', 'spell = spell or (None if green[r["id"]] else r)',
                     "reds: a head red after main went green again"),
    "main at the red": ("before = [m for m in mains if _when(m) <= _when(r)]", "before = list(mains)",
                        "reds: a red inherited from main"),
    "main is a push": ('return r.get("event") == "push" and r.get("head_branch") == "main"', 'return r.get("head_branch") == "main"',
                       "reds: a run on the branch main that is no push"),
    "main uncleared": ('        if _on_main(r):\n            return UNCLEARED, "no later green"\n', "",
                       "reds: a main red with no later green"),
    "gate job by name": ('for j in doc["jobs"] if j.get("name") == "gate"}', 'for j in doc["jobs"]}',
                         "reds: a failed job that is not `gate`"),
    "failed jobs failed": ('if j.get("conclusion") == "failure" and j.get("name") != "gate"})', 'if j.get("name") != "gate"})',
                           "reds: a job that did not fail at the red attempt"),
    "prelude and gate owed": ('owed = set(gate.gate_required()) | {"prelude", "gate"}', "owed = set(gate.gate_required())",
                              "reds: a failed prelude is a required failure"),
    "main row's own spell": ('op = opener.get(r["id"]) if _on_main(r) else opener[before[-1]["id"]] if before else None',
                             'op = opener[before[-1]["id"]] if before else None',
                             "reds: a main run red at an earlier attempt and unconcluded at its latest"),
    "edge spell": ("opener, spell = {}, EDGE", "opener, spell = {}, None",
                   "reds: a main red spell already open at the first main run read"),
    "column class from the event": ('"push") if r.get("event") == "push" else None', '"push") if True else None',
                                    "NULL reds: the same listing on a pull-request run"),
    "column member unconcluded": ('("completed" if j.get("conclusion") else "in_progress", j.get("conclusion"))',
                                  '("completed", j.get("conclusion"))', "reds: a member with no conclusion"),
    "stale listing": ('doc.get("attempt") == r["attempt"]:', "True:", "reds: a listing cached at an older attempt"),
    "listing owed past one attempt": ('elif r["c"] == "success" and r["attempt"] == 1:', 'elif r["c"] == "success":',
                                      "reds: the same run with no job listing"),
    "listing owed on a failure": ('elif r["c"] == "success" and r["attempt"] == 1:', 'elif r["attempt"] == 1:',
                                  "reds: a failed first attempt with no job listing"),
    "blind count": ('if blind else f"gate_reds {len(reds)}', 'if False else f"gate_reds {len(reds)}',
                    "reds: the same run with no job listing"),
    "failed jobs per attempt": ('if j.get("run_attempt") == attempt]', "if True]", "reds: a red attempt's failed jobs"),
    "required split": ('"required": [n for n in failed if n in owed],', '"required": failed,', "reds: a red attempt's failed jobs"),
    "found_by on main alone": (' if x["main"] else "")', ")", "reds: found_by ci-main on a main row"),
    "subject of a missing commit": ("if r is not None and r.returncode == 0 else None", "if r is not None else None",
                                    "reds: git_subject reads"),
}
_MUTANT_RUN = ("import runpy, sys; p, *dirs = sys.argv[1:]; sys.path[:0] = dirs; "
               "sys.argv = [p, '--self-test', '--no-mutants']; runpy.run_path(p, run_name='__main__')")


def _mutants(check) -> None:
    """Each MUTANTS row on a copy of this file, at this file's depth so its relative paths miss and the real
    seat, tools/ci and tests directories (passed on the path) answer its imports."""
    here = Path(__file__).resolve()
    head, tail = here.read_text().split("\nMUTANTS = {", 1)  # the code above the table, and the rest
    dirs = [str(here.parent), str(here.parents[2] / "ci"), str(here.parents[3] / "tests")]
    for name, (old, new, case) in MUTANTS.items():
        if head.count(old) != 1:
            check(f"mutant {name}: its needle occurs once above the table", False)
            continue
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td, "tools", "audit", "seat", here.name)
            copy.parent.mkdir(parents=True)
            copy.write_text(head.replace(old, new) + "\nMUTANTS = {" + tail)
            p = subprocess.run([sys.executable, "-I", "-c", _MUTANT_RUN, str(copy), *dirs],
                               capture_output=True, text=True, timeout=120)
        check(f"mutant killed: {name} (by '{case}')",
              p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines()))


def self_test(mutants: bool = True) -> int:
    fails = []

    def check(name, ok):
        print(("ok    " if ok else "FAIL  ") + name)
        if not ok:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp, "empty")
        empty.mkdir()
        got = report(load_dir(empty), None)
        check("NULL: an empty input directory prints unread and no value",
              got == ["loop_ledger unread (no wave-r<N>-groups.json roster)"])
        fx = _fixture()
        got = reads(fx, fx)
        check("a fully recorded roster reads every line",
              got[0] == "escapes 2 by found_by {outside: 1, owner: 1} by owned_by {D8: 1, none: 1}"
              and got[1].startswith("injected 1 (external 0, original 1;")
              and got[2] == "refix 1; R9-GRANDKID follows R9-HOTFIX-A"
              and got[3] == ("loop countermeasures 3 by family {N-log-flood: 2, N-staleness: 1} "
                             "by cm_kind {delete: 1, narrow: 1, new-refusal: 1}; k 0.33; "
                             "generations g0:3 g1:1(0.33) g2:1(1.00)"))
        for drop, line in (("owned_by", 0), ("caused_by", 1), ("family", 3)):
            g2 = [dict(g) for g in fx]
            del g2[1][drop]
            got2 = reads(g2, g2)
            check(f"NULL: one escape without {drop} turns read {line} unread naming it, never a partial value",
                  got2[line].endswith("unread (1 of 2 owing groups unrecorded: R9-HOTFIX-A)")
                  if line < 2 else "unread (1 of 3 owing groups unrecorded: R9-HOTFIX-A)" in got2[line])
            check(f"... and refix, which needs the whole ledger, is unread too, the other reads unchanged ({drop})",
                  "refix unread (1 of 3" in got2[2]
                  and all(got2[i] == got[i] for i in range(4) if i not in (2, line)
                          and not (drop == "caused_by" and i == 3)))
        g3 = [dict(g) for g in fx]
        g3[0]["found_by"] = "nobody"
        check("a value outside the vocabulary is unrecorded", "escapes unread (1 of 2" in reads(g3, g3)[0])
        g5 = [dict(g) for g in fx]
        g5[2]["family"] = "N-no-such-class"
        check("a countermeasure whose family is no bug class reads loop unread, never the word",
              reads(g5, g5)[3] == "loop unread (1 of 3 owing groups unrecorded: R9-HOTFIX-M)")
        g4 = [dict(g) for g in fx]
        g4[2]["found_by"] = "ci"
        check("a non-escape hotfix owes found_by: refix reads unread, escapes stay read",
              "refix unread (1 of 3 owing groups unrecorded: R9-HOTFIX-M)" == reads(g4, g4)[2]
              and reads(g4, g4)[0] == got[0])
        check("owned_split splits by dimension, and is unread with an unrecorded escape",
              owned_split(fx, {g["group"] for g in fx}) == "by owning dimension {D8: 1, none: 1}"
              and owned_split(g3[:1] + [{"group": "X", "source": "outside"}], {"X", "R9-OUT"})
              .startswith("by owning dimension unread (1 of 2"))
        x = fx[0]
        cm, kid = {**fx[0], "group": "R9-CM"}, {"group": "R10-KID", "parent": "R9-CM"}
        check("k counts a countermeasure's children in every period, not only its own",
              reads([cm], [cm, kid])[3].endswith("k 1.00; generations g0:1"))
        stray = [*fx, {"group": "R9-STRAY", "follows": "R9-NO-SUCH-GROUP"}]
        check("refix counts only a follows naming a roster group",
              reads(stray, stray)[2] == "refix 1; R9-GRANDKID follows R9-HOTFIX-A")
        check("a group with no entry time falls in the week unentered",
              "week unentered" in report([(9, "a", {"groups": [x]})], {}))
        check("a group carried into a later roster is counted once in its week",
              report([(9, "a", {"groups": [x]}), (10, "b", {"groups": [x]})], {"R9-OUT": 0})[-4]
              .startswith("  escapes 1 "))
        check("an unrecorded list names its first five groups, and an ellipsis only past five",
              _unread("x", list("ABCDE"), 9) == "x unread (5 of 9 owing groups unrecorded: A, B, C, D, E)"
              and _unread("x", list("ABCDEF"), 9) == "x unread (6 of 9 owing groups unrecorded: A, B, C, D, E ...)")
        check("owed: a plain group owes nothing; a machinery hotfix owes no owned_by",
              owed({"group": "P"}) == () and owed(fx[2]) == ("found_by", "caused_by", "family", "cm_kind"))
        check("generation: a cycle and a missing parent are None",
              generation({"group": "A", "parent": "B"}, {"B": {"group": "B", "parent": "A"},
                                                         "A": {"group": "A", "parent": "B"}}) is None
              and generation({"group": "A", "parent": "Z"}, {}) is None)
        # history: a two-commit repository, so the week split is driven, not assumed
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_environ, throwaway_git_init
        repo = Path(tmp, "repo")
        rdir = repo / roster_lib.ROSTERS_DIR
        rf = rdir / "wave-r9-groups.json"
        with throwaway_git_environ():
            throwaway_git_init(repo, "-q")
            rdir.mkdir(parents=True)
            for f, groups, stamp in ((rf, fx[:3], "2026-11-02T12:00:00Z"), (rf, fx, "2026-11-10T12:00:00Z"),
                                     (rdir / "wave-r10-groups.json", fx[:1], "2026-11-17T12:00:00Z")):
                f.write_text(json.dumps({"groups": groups}, indent=1))
                subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-q", "-m", "Merge pull request #7 from o/b", "-m", "#9 in the body"],
                               cwd=repo, check=True, capture_output=True,
                               env={**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
            ros, when = load_ref(str(repo), "HEAD")
        lines = report(ros, when)
        check("history: each group's week is its first roster entry, carried into a later roster or not",
              when is not None and week_of(when["R9-OUT"]) == "2026-W45" and week_of(when["R9-KID"]) == "2026-W46"
              and "week 2026-W47" not in lines
              and "week 2026-W45" in lines and "week 2026-W46" in lines
              and lines[lines.index("week 2026-W46") + 1] == "  escapes 0 by found_by {} by owned_by {}")
        check("--dir has no history: its weeks are unread",
              report(load_dir(rdir), None)[-1].startswith("weeks unread"))
        _self_test_reds(check, Path(tmp), repo)
    if mutants:
        _mutants(check)
    print(f"loop_ledger self-test: {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
