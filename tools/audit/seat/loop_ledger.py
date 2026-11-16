#!/usr/bin/env python3
"""The loop ledger: the convergence record's reads, per round and per week.

    python3 -I loop_ledger.py [--repo DIR] [--roster-ref REF]
    python3 -I loop_ledger.py --dir DIR
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
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script's directory
import roster_lib  # noqa: E402
from scorecard import escape_sets  # noqa: E402  line E's two sets are the escapes

ESCAPE_FIELDS = ("found_by", "owned_by", "caused_by")
HOTFIX_FIELDS = ("found_by", "caused_by")
CM_FIELDS = ("caused_by", "family", "cm_kind")
SHOWN = 5  # unrecorded names printed per read
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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--roster-ref")
    ap.add_argument("--dir")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.dir:
        lines = report(load_dir(Path(a.dir)), None)
    else:
        lines = report(*load_ref(a.repo, roster_lib.reader_ref(a.repo, a.roster_ref)))
    print("\n".join(lines))
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


def self_test() -> int:
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
                subprocess.run(["git", "commit", "-q", "-m", "r"], cwd=repo, check=True, capture_output=True,
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
    print(f"loop_ledger self-test: {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
