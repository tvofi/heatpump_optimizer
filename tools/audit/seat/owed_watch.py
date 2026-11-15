#!/usr/bin/env python3
"""owed_watch.py -- the owed-event watch: who was fired, whether a seat is on it, what is owed past its grace.

    python3 -I tools/audit/seat/owed_watch.py cp-owed --repo O/R --fired LEDGER [--checkout DIR] [--roster-ref REF]
    python3 -I tools/audit/seat/owed_watch.py --self-test

WHY THIS EXISTS (R11-PRE-STANDING-SCRIPTS part 1, design/R11-PRE-STANDING-SCRIPTS 375ce7ff3f,
approved at design-verdict be6cc24cae). The owner's directive (tvofi 2026-11-09, triage
s6-batch141.md P515): "never let the critical path or outside PRs slip, ever". The watch ran only
as a session-local loop. This module owns the fired-ledger read, the "a seat is on it" predicate
and every owed-by-grace arm; orchestrator_tick.py imports the first two and its FIRE-OWED level,
and the beat's `cp-owed` row (beat_jobs.py) runs `cp-owed` here.

THE WATCHED SET is computed, never hand-kept: every open roster group `roster_lib.is_outside` is
true for, plus every group `roster_lib.critical_path_read` publishes at the roster ref, and the
open pull requests mapped to them (`group_for_branch`, else `group_for_pr`). An unreadable
critical-path file is UNREADABLE, never an empty set.

THE ARMS, one `CP-OWED <arm> <subject> ...` line per step past its grace (GRACE_MIN):
  merge-no-approval  a `Fix review: merge <head>` verdict at the PR head, no APPROVED review at it
  approved-unmerged  an APPROVED review at the head of a still-open PR
  blocked-no-fire    a `Fix review: blocked <head>` verdict at the head, no FIRED line naming the PR
                     and no handoff ref moved since the verdict
  head-no-dispatch   no verdict at the head and no reviewer dispatch whose prompt names the head
  UNFIRED            a dispatch ref of the group (fixer, designer, design reviewer, reviewer) with
                     no FIRED line naming the group and no return ref moved since it was published
  DESIGN-REVIEW-OWED a design tip no design verdict names (P510's predicate); a `seat-refused`
                     verdict is no review; a tip whose note opens `Design blocked:` is a designer
                     stop, owed by the dispatch drain, never here
  FIXER-OWED         an approve at the design tip, no fixer dispatch and no handoff ref since
  SEAT-SILENT        the group's newest FIRED line with no return ref moved since it, keyed on
                     refs and never on a cloud session's status (a dead session reads running)
"After" compares a FIRED line's leading UTC stamp with the step's commit time; an unstamped line
is never "after" anything. Lines are ranked by `roster_lib.dispatch_rank` (hotfix, then
critical path or outside), the critical path ahead of outside inside a rank, oldest first.
Exit 0 with the lines, 2 with `cp-owed: UNREADABLE <what>` lines when a read failed.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(SEAT))
import roster_lib  # noqa: E402
import topic_grammar  # noqa: E402

SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
SEAT_KINDS = ("handoff-wip", "handoff", "handoff-body")
FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
#: carry 4's graces, minutes. UNFIRED takes FIRE_GRACE_MIN (the same step as FIRE-OWED: published,
#: not fired) and FIXER-OWED the design-review step's 10 (verdict in, next seat not dispatched);
#: the carry names no figure for either.
GRACE_MIN = {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15,
             "head-no-dispatch": 25, "UNFIRED": FIRE_GRACE_MIN, "DESIGN-REVIEW-OWED": 10,
             "FIXER-OWED": 10, "SEAT-SILENT": 90}
FIX_VERDICT = re.compile(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)")
DESIGN_VERDICT = re.compile(r"^Design review: ([a-z-]+) ([0-9a-f]{40})(.*)$")
DESIGN_BLOCKED = "Design blocked:"
FAMILIES = ("verdict", "dispatch", "design", "design-verdict", "handoff", "handoff-wip", "handoff-body", "probe")
RETURN_FAMILIES = ("handoff", "handoff-wip", "handoff-body", "design", "design-verdict")


# ------------------------------------------------------------ the fired ledger (moved from the tick)

def fired(path) -> "list[tuple]":
    """[(utc datetime or None, line)] for each FIRED line of the dispatch seat's ledger."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            rows = [l.strip() for l in fh if "FIRED" in l]
    except (OSError, TypeError):
        return []
    out = []
    for l in rows:
        m = FIRED_STAMP.match(l)
        when = None
        if m:
            when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
                tzinfo=datetime.timezone.utc)
        out.append((when, l))
    return out


def fire_names(n: int, topics: list, line: str) -> bool:
    """A FIRED line names a PR by number, topic or its payload file
    (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
    return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
        t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)


def seat_on(n: int, topics: list, heads: dict, rows: list, now, age_min, blocked_md,
            kinds=SEAT_KINDS) -> bool:
    """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
    handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs).
    `age_min(ref, sha)` and `blocked_md(sha)` are the caller's git reads."""
    cutoff = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
    for when, l in rows:
        if (when is None or when >= cutoff) and fire_names(n, topics, l):
            return True
    for t in topics:
        for fam in kinds:
            refs = [f"{fam}/{t}"]
            if fam == "handoff-wip":  # a split seat step-pushes under the family's topic (topic-family.md)
                refs += sorted(k for k in heads if k.startswith("handoff-wip/")
                               and k != refs[0] and topic_grammar.family(t).fullmatch(k[len("handoff-wip/"):]))  # mut:wipfamily
            for ref in refs:
                sha = heads.get(ref)
                if fam == "handoff-wip" and sha and blocked_md(sha) is not None:  # mut:blockedseat
                    continue  # a stop on a question is owed by blocked_stops, not a seat on the PR
                age = age_min(ref, sha) if sha else None
                if age is not None and age <= SEAT_WINDOW_MIN:
                    return True
    return False


def fire_owed(payload_dir, rows: list, now) -> "list[str]":
    """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
    out = []
    for f in sorted(Path(payload_dir).glob("payload-*.json")):
        age = (now.timestamp() - f.stat().st_mtime) / 60
        if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in rows):
            out.append(f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
                       "(firing is a RemoteTrigger call: the orchestrator's turn)")
    return out


# ------------------------------------------------------------------------------ cp-owed, pure

def _names_group(g: dict, line: str) -> bool:
    """A FIRED line names the group: its id, its topic, or one of its pull requests."""
    return fire_names(-1, [g["gid"], g["topic"]], line) or any(fire_names(n, [], line) for n in g["prs"])


def _fired_since(g: dict, rows: list, t: float) -> bool:
    return any(when is not None and when >= t and _names_group(g, l) for when, l in rows)


def _group_refs(g: dict, refs: dict, families) -> "list[str]":
    """The group's refs in `families`: <family>/<topic> (any family member for handoff-wip and
    dispatch/fixer-), <family>/<gid> (design refs carry the group's case), and per pull request
    verdict/<n>, probe/rev-<n>-<nonce> and dispatch/reviewer-rev-<n>."""
    fam_t, gid = topic_grammar.family(g["topic"]), g["gid"].lower()
    out = []
    for ref in refs:
        family, _, rest = ref.partition("/")
        if family not in families:
            continue
        low = rest.lower()
        if family == "dispatch":
            ok = (low.startswith("fixer-") and fam_t.fullmatch(low[6:])) or low in (
                f"designer-{gid}", f"design-reviewer-{gid}") or any(low == f"reviewer-rev-{n}" for n in g["prs"])
        elif family in ("design", "design-verdict"):
            ok = low == gid
        elif family == "verdict":
            ok = any(low == str(n) for n in g["prs"])
        elif family == "probe":
            ok = any(low.startswith(f"rev-{n}-") for n in g["prs"])
        else:
            ok = bool(fam_t.fullmatch(low)) if family == "handoff-wip" else low == g["topic"]
        if ok:
            out.append(ref)
    return out


def _returned_since(g: dict, refs: dict, ctime: dict, t: float) -> bool:
    return any(ctime[refs[r]] >= t for r in _group_refs(g, refs, RETURN_FAMILIES + ("verdict", "probe")))


def cp_owed(groups: dict, prs: list, refs: dict, ctime: dict, first: dict, rows: list, now: float,
            graces: dict = GRACE_MIN) -> "list[str]":
    """The CP-OWED lines, ranked. groups: gid -> {gid, topic, tags, rank, prs}; prs: dicts
    number/head/gid/head_t/approved_t; refs: `<family>/<name>` -> sha; ctime: sha -> epoch;
    first: sha -> the first line of the tip's note (VERDICT.md, verdict.md, design.md, PROMPT.md);
    rows: `fired()`'s output, stamps as epochs or None."""
    owed = []

    def owe(g, arm, subject, since, detail):
        age = int((now - since) // 60)
        if now - since > graces[arm] * 60:  # mut:grace
            tags = " ".join(g["tags"])
            owed.append(((g["rank"], "CP" not in g["tags"], -age),
                         f"CP-OWED {arm} {subject} {age}m past its {graces[arm]}m grace [{tags}] -- {detail}"))

    for p in prs:
        g, n, head = groups[p["gid"]], p["number"], p["head"]
        vsha = refs.get(f"verdict/{n}")
        m = FIX_VERDICT.match(first.get(vsha, "")) if vsha else None
        at_head = bool(m) and m[2] == head
        if p.get("approved_t") is not None:
            owe(g, "approved-unmerged", f"#{n}", p["approved_t"], f"approved at {head[:12]}, not merged")
        elif at_head and m[1] == "merge":
            owe(g, "merge-no-approval", f"#{n}", ctime[vsha], f"merge verdict at {head[:12]}, no approval")
        if at_head and m[1] == "blocked":
            t = ctime[vsha]
            if not _fired_since(g, rows, t) and not any(  # mut:blockedfire
                    ctime[refs[r]] >= t for r in _group_refs(g, refs, ("handoff", "handoff-wip", "handoff-body"))):
                owe(g, "blocked-no-fire", f"#{n}", t, f"blocked at {head[:12]}, no fire and no repair since")
        if not at_head:
            dsha = refs.get(f"dispatch/reviewer-rev-{n}")
            if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead
                owe(g, "head-no-dispatch", f"#{n}", p["head_t"], f"head {head[:12]} has no verdict and no reviewer dispatch")

    for gid, g in groups.items():
        for ref in _group_refs(g, refs, ("dispatch",)):
            t = ctime[refs[ref]]
            if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired
                owe(g, "UNFIRED", gid, t, f"{ref} published, no FIRED line and no return since")
        dsha = refs.get(next((r for r in refs if r.lower() == f"design/{gid.lower()}"), ""))
        if dsha and not first.get(dsha, "").startswith(DESIGN_BLOCKED):  # mut:designblocked
            vsha = refs.get(next((r for r in refs if r.lower() == f"design-verdict/{gid.lower()}"), ""))
            m = DESIGN_VERDICT.match(first.get(vsha, "")) if vsha else None
            refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused
            kind = m[1] if m and m[2] == dsha and not refused else None  # the review at the tip, if any
            if kind is None:
                owe(g, "DESIGN-REVIEW-OWED", gid, ctime[dsha], f"design/{gid} at {dsha[:12]} has no design review")
            elif kind == "approve":
                t = ctime[vsha]
                if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))
                           if not r.startswith(("dispatch/design", "dispatch/reviewer-rev-"))):  # mut:fixerowed
                    owe(g, "FIXER-OWED", gid, t, f"design approved at {dsha[:12]}, no fixer dispatched")
        last = max((when for when, l in rows if when is not None and _names_group(g, l)), default=None)
        if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent
            owe(g, "SEAT-SILENT", gid, last, "fired, no return ref since")
    return [line for _, line in sorted(owed)]


# ------------------------------------------------------------------------------ cp-owed, live

def sh(argv, cwd=None):
    p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


class Unreadable(Exception):
    pass


def _epoch(iso: str) -> float:
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def read_world(repo: str, checkout: str, fired_path: str, roster_ref, run=sh):
    """The pure core's inputs, read over gh and git; Unreadable names the first read that failed."""
    git = lambda *a: run(["git", "-C", checkout, *a])
    ref = roster_lib.reader_ref(checkout, roster_ref)
    try:
        roster = roster_lib.show_roster(checkout, ref)
    except (roster_lib.RosterNotFound, ValueError) as e:
        raise Unreadable(f"roster at {ref}: {e}")
    cp, why = roster_lib.critical_path_read(checkout, ref)
    if cp is None:
        raise Unreadable(f"critical path: {why}")
    groups = {}
    for gid, g in roster_lib.open_groups(roster).items():
        tags = [t for t, on in (("HOTFIX", roster_lib.is_hotfix(g)), ("CP", roster_lib.norm_group(gid) in cp),
                                ("OUTSIDE", roster_lib.is_outside(g))) if on]
        if "CP" in tags or "OUTSIDE" in tags:
            groups[gid] = {"gid": gid, "topic": roster_lib.branch_of(g).split("/", 1)[-1].lower(), "tags": tags,
                           "rank": roster_lib.dispatch_rank(roster, gid, cp), "prs": []}
    code, o = run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "300",
                   "--json", "number,headRefOid,headRefName,reviews"])
    try:
        listed = json.loads(o) if code == 0 else None
        if not isinstance(listed, list):
            raise ValueError(o.strip()[-120:])
    except ValueError as e:
        raise Unreadable(f"open pull requests: {e}")
    prs = []
    for p in listed:
        gid = roster_lib.group_for_branch(roster, p.get("headRefName") or "") or roster_lib.group_for_pr(roster, p["number"])
        if gid in groups:
            groups[gid]["prs"].append(p["number"])
            ok = [_epoch(r["submittedAt"]) for r in p.get("reviews") or ()
                  if r.get("state") == "APPROVED" and (r.get("commit") or {}).get("oid") == p["headRefOid"]]
            prs.append({"number": p["number"], "head": p["headRefOid"], "gid": gid,
                        "approved_t": max(ok) if ok else None})
    code, o = git("ls-remote", "origin", *(f"refs/heads/{f}/*" for f in FAMILIES))
    if code:
        raise Unreadable(f"ls-remote: {o.strip()[-120:]}")
    every = {l.split()[1][len("refs/heads/"):]: l.split()[0] for l in o.splitlines()
             if len(l.split()) == 2 and l.split()[1].startswith("refs/heads/")}
    refs = {r: every[r] for g in groups.values() for r in _group_refs(g, every, FAMILIES)}
    want = sorted(set(refs.values()) | {p["head"] for p in prs})
    if want:
        code, o = git("fetch", "-q", "origin", *(f"refs/heads/{r}" for r in sorted(refs)),
                      *(f"refs/pull/{p['number']}/head" for p in prs))
        if code:
            raise Unreadable(f"fetch: {o.strip()[-120:]}")
        code, o = git("log", "--no-walk", "--format=%H %ct", *want)
        if code:
            raise Unreadable(f"commit times: {o.strip()[-120:]}")
    ctime = {l.split()[0]: float(l.split()[1]) for l in (o.splitlines() if want else []) if len(l.split()) == 2}
    first = {}
    for r, sha in refs.items():
        note = {"verdict": "VERDICT.md", "design-verdict": "verdict.md", "design": "design.md",
                "dispatch": "PROMPT.md"}.get(r.split("/", 1)[0])
        if note:
            code, o = git("show", f"{sha}:{note}")
            first[sha] = (o.splitlines() or [""])[0] if code == 0 else ""
    for p in prs:
        p["head_t"] = ctime.get(p["head"])
        if p["head_t"] is None:
            raise Unreadable(f"#{p['number']}'s head {p['head'][:12]} commit time")
    rows = [(w.timestamp() if w else None, l) for w, l in fired(fired_path)]
    return groups, prs, refs, ctime, first, rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=("cp-owed",))
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--fired", help="the dispatch seat's fire ledger")
    ap.add_argument("--checkout", default=".")
    ap.add_argument("--roster-ref")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cmd != "cp-owed" or not a.fired:
        ap.error("cp-owed needs --fired")
    try:
        world = read_world(a.repo, a.checkout, a.fired, a.roster_ref)
    except Unreadable as e:
        print(f"cp-owed: UNREADABLE {e}")
        return 2
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    for line in cp_owed(*world, now):
        print(line)
    return 0


# ------------------------------------------------------------------------------ self-test
SELF_TEST_MARK = "# " + "-" * 78 + " self-test"


def _world(arm: str, grace0: bool):
    """A planted world: one critical-path group CPG (PR #11) and one outside group OUT (PR #12),
    every timestamp 60 min before now. `arm` plants exactly one owed step; "none" plants none."""
    now, t = 1_800_000_000.0, 1_800_000_000.0 - 3600
    h = {k: c * 40 for k, c in (("h11", "1"), ("h12", "2"), ("d", "d"), ("v", "e"), ("x", "f"))}
    groups = {"CPG": {"gid": "CPG", "topic": "r11-cpg", "tags": ["CP"], "rank": 1, "prs": [11]},
              "OUT": {"gid": "OUT", "topic": "r11-out", "tags": ["OUTSIDE"], "rank": 1, "prs": [12]}}
    prs = [{"number": 11, "head": h["h11"], "gid": "CPG", "head_t": t, "approved_t": None},
           {"number": 12, "head": h["h12"], "gid": "OUT", "head_t": t, "approved_t": None}]
    refs = {"dispatch/reviewer-rev-11": "a1" * 20, "dispatch/reviewer-rev-12": "a2" * 20,
            "verdict/12": "b2" * 20, "handoff/r11-cpg": "c1" * 20}
    first = {"a1" * 20: f"CLOUD REVIEWER seat for PR #11, at head {h['h11']}. Bus nonce: x",
             "a2" * 20: f"CLOUD REVIEWER seat for PR #12, at head {h['h12']}. Bus nonce: y",
             "b2" * 20: f"Fix review: blocked {'0' * 40} code: old head"}
    ctime = {h["h11"]: t, h["h12"]: t, "c1" * 20: t + 90, "b2" * 20: t + 90}  # each seat returned after its fire
    rows = [(t + 60, "FIRED reviewer #11"), (t + 60, "FIRED reviewer #12")]
    if arm == "merge-no-approval":
        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
    elif arm == "approved-unmerged":
        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
        prs[0]["approved_t"] = t
    elif arm == "blocked-no-fire":
        refs["verdict/12"], first["9" * 40] = "9" * 40, f"Fix review: blocked {h['h12']} code: x"
        rows = [(t - 60, "FIRED reviewer #12"), (t + 60, "FIRED reviewer #11")]
    elif arm == "head-no-dispatch":
        first["a1" * 20] = f"CLOUD REVIEWER seat for PR #11, at head {'7' * 40}. Bus nonce: x"
    elif arm == "UNFIRED":
        refs["dispatch/designer-OUT"] = "8" * 40
        ctime["8" * 40] = t + 120
    elif arm in ("DESIGN-REVIEW-OWED", "seat-refused", "revise-at-tip", "design-blocked"):
        refs["design/OUT"], first[h["d"]] = h["d"], ("Design blocked: ref_privacy refused" if arm == "design-blocked"
                                                    else "# OUT: a design")
        if arm in ("seat-refused", "revise-at-tip"):
            refs["design-verdict/OUT"] = h["v"]
            first[h["v"]] = f"Design review: revise {h['d']}" + (" seat-refused" if arm == "seat-refused" else "")
    elif arm == "FIXER-OWED":
        refs["design/OUT"], refs["design-verdict/OUT"] = h["d"], h["v"]
        first[h["d"]], first[h["v"]] = "# OUT: a design", f"Design review: approve {h['d']}"
        ctime[h["v"]] = t + 120
    elif arm == "SEAT-SILENT":
        rows.append((t + 300, "FIRED fixer for r11-out"))
    for sha in refs.values():
        ctime.setdefault(sha, t)
    if grace0:
        return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 0)
    return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 24 * 60)


ARMS = tuple(GRACE_MIN)


def _aged(world):
    """A planted world's refs and heads moved 1e8 s into the past, so a run at the real clock reads them old."""
    groups, prs, refs, ctime, first, rows = world
    return groups, prs, refs, {k: v - 1e8 for k, v in ctime.items()}, first, rows


def cases(mod) -> "dict[str, bool]":
    res = {}
    run = lambda arm, g0=True: mod.cp_owed(*_world(arm, g0))
    base = run("none")
    res["null: every step answered, nothing is owed (grace 0)"] = base == []
    for arm in ARMS:
        got = run(arm)
        res[f"planted {arm}: one line at grace 0"] = (
            len(got) == 1 and got[0].startswith(f"CP-OWED {arm} ") and "past its 0m grace" in got[0])
        res[f"null {arm}: inside its grace prints nothing"] = run(arm, False) == []
    res["DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"] = (
        [l.split()[1] for l in run("seat-refused")] == ["DESIGN-REVIEW-OWED"])
    res["DESIGN-REVIEW-OWED null: a class-open revise at the tip is a review (the designer owes)"] = run("revise-at-tip") == []
    res["DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"] = run("design-blocked") == []
    w = list(_world("UNFIRED", True))
    w[2]["handoff/r11-out"], w[3]["c9" * 20] = "c9" * 20, w[3]["8" * 40] + 60
    res["UNFIRED null: a return ref newer than the dispatch is a fire"] = mod.cp_owed(*w) == []
    def variant(arm, **extra):
        """`arm`'s world with refs added: name -> (sha, seconds after the world's step time, first line)."""
        w = list(_world(arm, True))
        for ref, (sha, dt, line) in extra.items():
            w[2][ref.replace("__", "/")], w[3][sha], w[4][sha] = sha, w[6] - 3600 + dt, line
        return mod.cp_owed(*w)
    got = variant("none", dispatch__fixer_x=("f1" * 20, 120, ""))
    res["UNFIRED: only the group's own dispatch refs count (a stranger's fixer dispatch is not the group's)"] = got == []
    got = variant("none", **{"dispatch__fixer-r11-out-p2": ("f1" * 20, 120, "")})
    res["UNFIRED: a fixer dispatch of a family member (-p2) is the group's"] = (
        [l.split()[1:3] for l in got] == [["UNFIRED", "OUT"]])
    for name, ref, line in (("a design push", "design__OUT", "Design blocked: x"),
                            ("a probe verdict", "probe__rev-12-abcd", ""),
                            ("a family member's step push", "handoff-wip__r11-out-p1", "")):
        res[f"SEAT-SILENT null: {name} after the fire is a return"] = variant("SEAT-SILENT", **{ref: ("f2" * 20, 400, line)}) == []
    res["SEAT-SILENT: a design push of another group is no return"] = (
        [l.split()[1] for l in variant("SEAT-SILENT", design__OUTX=("f2" * 20, 400, "Design blocked: x"))] == ["SEAT-SILENT"])
    res["blocked-no-fire null: a handoff ref at the verdict's own second is a repair"] = (
        variant("blocked-no-fire", **{"handoff__r11-out": ("f3" * 20, 0, "")}) == [])
    w = list(_world("UNFIRED", True))
    w[5] = w[5] + [(w[3]["8" * 40], "FIRED designer R11-out OUT")]
    res["UNFIRED null: a FIRED line naming the group, stamped at the dispatch's own second, is a fire"] = not any(
        l.split()[1] == "UNFIRED" for l in mod.cp_owed(*w))
    w[5][-1] = (w[3]["8" * 40] - 1, "FIRED designer OUT")
    res["UNFIRED: a FIRED line a second before the dispatch is no fire for it"] = (
        [l.split()[1] for l in mod.cp_owed(*w) if l.split()[1] == "UNFIRED"] == ["UNFIRED"])
    res["FIXER-OWED's age runs from the approve verdict, not from another ref"] = " 58m past " in (run("FIXER-OWED") or [""])[0]
    res["the line names the step's age in whole minutes"] = " 60m past its 0m grace " in (run("merge-no-approval") or [""])[0]
    w = list(_world("none", True))
    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["HOTFIX", "OUTSIDE"], 0
    w[0]["CPG"]["tags"] = ["CP"]
    w[2]["design/OUT"], w[2]["design/CPG"] = "d1" * 20, "d2" * 20
    w[3]["d1" * 20] = w[3]["d2" * 20] = w[6] - 7200
    ranked = mod.cp_owed(*w)
    res["rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"] = (
        [l.split()[2] for l in ranked] == ["OUT", "CPG"])
    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["OUTSIDE"], 1
    res["rank: inside one rank the critical path is ahead of outside"] = (
        [l.split()[2] for l in mod.cp_owed(*w)] == ["CPG", "OUT"])
    return res


#: one edit per arm, in a temp copy of this file; the named case must fail.
MUTANTS = {
    "grace_ignored": ("if now - since > graces[arm] * 60:  # mut:grace", "if True:  # mut:grace",
                      "null merge-no-approval: inside its grace prints nothing"),
    "approval_ignored": ('if p.get("approved_t") is not None:', "if False:", "planted approved-unmerged: one line at grace 0"),
    "merge_arm": ('elif at_head and m[1] == "merge":', "elif False:", "planted merge-no-approval: one line at grace 0"),
    "blocked_fire": ("if not _fired_since(g, rows, t) and not any(  # mut:blockedfire", "if any(  # mut:blockedfire",
                     "planted blocked-no-fire: one line at grace 0"),
    "dispatch_head": ('if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead',
                      "if not dsha:  # mut:dispatchhead", "planted head-no-dispatch: one line at grace 0"),
    "unfired": ("if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired",
                "if not _fired_since(g, rows, t):  # mut:unfired",
                "UNFIRED null: a return ref newer than the dispatch is a fire"),
    "unfired_dropped": ('owe(g, "UNFIRED", gid, t,', 'None and owe(g, "UNFIRED", gid, t,', "planted UNFIRED: one line at grace 0"),
    "design_blocked": ("if dsha and not first.get(dsha, \"\").startswith(DESIGN_BLOCKED):  # mut:designblocked",
                       "if dsha:  # mut:designblocked",
                       "DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"),
    "seat_refused": ('refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused',
                     "refused = False  # mut:seatrefused",
                     "DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"),
    "design_review_dropped": ("            if kind is None:\n", "            if False:\n",
                              "planted DESIGN-REVIEW-OWED: one line at grace 0"),
    "fixer_owed": ('if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
                   'if any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
                   "planted FIXER-OWED: one line at grace 0"),
    "silent": ("if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent",
               "if False:  # mut:silent", "planted SEAT-SILENT: one line at grace 0"),
    "rank_cp_first": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append(((g["rank"], "CP" in g["tags"], -age),',
                      "rank: inside one rank the critical path is ahead of outside"),
    "rank_dropped": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append((("CP" not in g["tags"], -age),',
                     "rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"),
}


def read_world_checks() -> "dict[str, bool]":
    """read_world over a throwaway origin: the roster and critical-path file on main, the watched
    groups' refs and two pull-request heads; gh answered by a fake, every git read real."""
    sys.path.insert(0, str(SEAT.parents[2] / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_environ, throwaway_git_init
    res = {}
    with tempfile.TemporaryDirectory() as d, throwaway_git_environ():
        o, c = Path(d) / "o", Path(d) / "c"
        throwaway_git_init(o, "-q", "-b", "main")
        g = lambda *a, cwd=o: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()

        def commit(branch, name, text, when):
            g("checkout", "-q", "--orphan" if branch != "main" else "-B", branch)
            g("rm", "-rqf", "--ignore-unmatch", ".")
            (o / name).parent.mkdir(parents=True, exist_ok=True)
            (o / name).write_text(text)
            g("add", name)
            env = {"GIT_COMMITTER_DATE": f"@{when} +0000", "GIT_AUTHOR_DATE": f"@{when} +0000"}
            subprocess.run(["git", "commit", "-qm", branch], cwd=o, check=True, capture_output=True,
                           env={**__import__("os").environ, **env})
            return g("rev-parse", "HEAD")
        roster = {"groups": [
            {"group": "R11-CPG", "resume": {"stage": "not-started", "branch": "fix/r11-cpg"}},
            {"group": "R11-OUT", "source": "outside", "resume": {"stage": "not-started", "pr": 12}},
            {"group": "R11-OFF", "resume": {"stage": "not-started"}},
            {"group": "R11-SHUT", "source": "outside", "resume": {"stage": "done"}}]}
        commit("main", f"{roster_lib.ROSTERS_DIR}/wave-r11-groups.json", json.dumps(roster), 1_000)
        (o / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps({"critical": ["R11-CPG"]}))
        g("add", "-A")
        g("commit", "-qm", "cp")
        h11 = commit("work11", "x", "11", 2_000)
        h12 = commit("work12", "x", "12", 3_000)
        v12 = commit("verdict/12", "VERDICT.md", f"Fix review: merge {h12}\n", 4_000)
        r11 = commit("dispatch/reviewer-rev-11", "PROMPT.md", f"CLOUD REVIEWER seat for PR #11, at head {h11}.\nRole\n", 5_000)
        dz = commit("design/R11-OUT", "design.md", "# a design\n", 6_000)
        commit("design/R11-OFF", "design.md", "# not watched\n", 6_000)
        hf = commit("handoff/r11-cpg", "x", "h", 7_000)
        g("update-ref", "refs/pull/11/head", h11)
        g("update-ref", "refs/pull/12/head", h12)
        g("checkout", "-q", "main")
        throwaway_git_clone(o, c, "-q")
        led = Path(d) / "fired.log"
        led.write_text("2026-11-15T11:30:00Z FIRED reviewer #11\n")
        prs = [{"number": 11, "headRefOid": h11, "headRefName": "fix/r11-cpg", "reviews": []},
               {"number": 12, "headRefOid": h12, "headRefName": "patch-1", "reviews": [
                   {"state": "APPROVED", "submittedAt": "2026-11-15T10:00:00Z", "commit": {"oid": h12}},
                   {"state": "APPROVED", "submittedAt": "2026-11-15T11:00:00Z", "commit": {"oid": h11}},
                   {"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-15T12:00:00Z", "commit": {"oid": h12}}]},
               {"number": 13, "headRefOid": h11, "headRefName": "fix/r11-off", "reviews": []}]
        calls = []

        def fake(answer):
            def run(argv, cwd=None):
                calls.append(argv)
                return answer if argv[0] == "gh" else sh(argv, cwd)
            return run
        groups, got_prs, refs, ctime, first, rows = read_world("o/r", str(c), str(led), None, fake((0, json.dumps(prs))))
        res["read_world: the watched set is the open critical-path and outside groups, nothing else"] = (
            sorted(groups) == ["R11-CPG", "R11-OUT"] and groups["R11-CPG"]["tags"] == ["CP"]
            and groups["R11-OUT"]["tags"] == ["OUTSIDE"] and groups["R11-CPG"]["topic"] == "r11-cpg")
        res["read_world: a pull request maps by branch, else by resume.pr; an unwatched group's is dropped"] = (
            [(p["number"], p["gid"]) for p in got_prs] == [(11, "R11-CPG"), (12, "R11-OUT")]
            and groups["R11-OUT"]["prs"] == [12])
        res["read_world: approval is the newest APPROVED review at the head, never at another commit"] = (
            got_prs[1]["approved_t"] == _epoch("2026-11-15T10:00:00Z") and got_prs[0]["approved_t"] is None)
        res["read_world: the watched groups' refs, never an unwatched group's"] = (
            sorted(refs) == ["design/R11-OUT", "dispatch/reviewer-rev-11", "handoff/r11-cpg", "verdict/12"])
        res["read_world: commit times from git, for every ref tip and pull-request head"] = (
            [ctime.get(x) for x in (h11, h12, v12, r11, dz, hf)] == [2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0]
            and [p["head_t"] for p in got_prs] == [2000.0, 3000.0])
        res["read_world: each tip's note is read to its first line"] = (
            first.get(v12) == f"Fix review: merge {h12}" and first.get(r11) == f"CLOUD REVIEWER seat for PR #11, at head {h11}."
            and first.get(dz) == "# a design" and hf not in first)
        res["read_world: the fire ledger's stamps are epochs"] = rows == [(_epoch("2026-11-15T11:30:00Z"), "2026-11-15T11:30:00Z FIRED reviewer #11")]
        res["read_world: gh is asked for the open pull requests of the repo given"] = any(
            a[:3] == ["gh", "pr", "list"] and "o/r" in a and "open" in a for a in calls)
        for name, answer in (("a gh refusal", (1, "HTTP 403")), ("a non-list answer", (0, "{}"))):
            try:
                read_world("o/r", str(c), str(led), None, fake(answer))
                res[f"read_world: {name} is Unreadable, never an empty list"] = False
            except Unreadable as e:
                res[f"read_world: {name} is Unreadable, never an empty list"] = "open pull requests" in str(e)
        def failing(word, out=None):
            def run(argv, cwd=None):
                if argv[0] == "gh":
                    return 0, json.dumps(prs)
                if word in argv:
                    return (0, out) if out is not None else (1, f"{word} refused")
                return sh(argv, cwd)
            return run
        for word, out, why in (("ls-remote", None, "ls-remote"), ("fetch", None, "fetch"), ("log", None, "commit times"),
                               ("log", f"{h12} 3000\n", "#11's head")):
            try:
                read_world("o/r", str(c), str(led), None, failing(word, out))
                ok = False
            except Unreadable as e:
                ok = str(e).startswith(why)
            res[f"read_world: a failed {word}{' missing a head' if out else ''} is Unreadable ({why})"] = ok
        try:
            read_world("o/r", str(c), str(led), "refs/heads/nope", fake((0, "[]")))
            res["read_world: an unreadable roster ref is Unreadable"] = False
        except Unreadable as e:
            res["read_world: an unreadable roster ref is Unreadable"] = str(e).startswith("roster at refs/heads/nope")
        g("checkout", "-q", "main", cwd=c)
        (c / roster_lib.CRITICAL_PATH_NAME).write_text("not json")
        g("commit", "-qam", "bad", cwd=c)
        try:
            read_world("o/r", str(c), str(led), "HEAD", fake((0, "[]")))
            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = False
        except Unreadable as e:
            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = "critical path" in str(e)
    return res


def self_test() -> int:
    import importlib.util
    res = cases(sys.modules[__name__])
    res.update(read_world_checks())
    # the moved FIRE-OWED level and fired-ledger read, against the tick's own fixture shape
    with tempfile.TemporaryDirectory() as d:
        now = datetime.datetime(2026, 11, 15, 12, 0, tzinfo=datetime.timezone.utc)
        pf = Path(d) / "payload-fix-86-r1.json"
        pf.write_text("{}")
        old = (now - datetime.timedelta(minutes=60)).timestamp()
        os.utime(pf, (old, old))
        led = Path(d) / "fired.log"
        led.write_text("2026-11-15T11:30:00Z FIRED payload-fix-86-r1.json\nno fire here\nFIRED #3 unstamped\n")
        rows = fired(led)
        res["fired: FIRED lines only, stamped as UTC, an unstamped one None"] = (
            [w and w.isoformat() for w, _ in rows] == ["2026-11-15T11:30:00+00:00", None])
        res["fire_owed: an unfired payload past its grace owes; one a FIRED line names does not"] = (
            len(fire_owed(d, [], now)) == 1 and fire_owed(d, rows, now) == []
            and " rendered 60m ago" in (fire_owed(d, [], now) or [""])[0])
        edge = (now - datetime.timedelta(minutes=FIRE_GRACE_MIN)).timestamp()
        os.utime(pf, (edge, edge))
        res["fire_owed: a payload exactly FIRE_GRACE_MIN old is still inside its grace"] = fire_owed(d, [], now) == []
        res["graces are carry 4's figures, UNFIRED at FIRE_GRACE_MIN; the tick's two windows unchanged (120, 15)"] = (
            GRACE_MIN == {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15, "head-no-dispatch": 25,
                          "UNFIRED": 15, "DESIGN-REVIEW-OWED": 10, "FIXER-OWED": 10, "SEAT-SILENT": 90}
            and (SEAT_WINDOW_MIN, FIRE_GRACE_MIN) == (120, 15))
        edge = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
        on = lambda rows, age: seat_on(7, ["r11-a"], {"handoff/r11-a": "a" * 40} if age is not None else {}, rows, now,
                                       lambda ref, sha: age, lambda sha: None)
        res["seat_on: a fire or a ref move exactly SEAT_WINDOW_MIN old is still a seat; one minute older is not"] = (
            on([(edge, "FIRED #7")], None) and not on([(edge - datetime.timedelta(minutes=1), "FIRED #7")], None)
            and on([], SEAT_WINDOW_MIN) and not on([], SEAT_WINDOW_MIN + 1))
        res["fire_names: #3 names PR 3, never PR 30; a topic matches as a whole word"] = (
            fire_names(3, [], "FIRED #3 x") and not fire_names(3, [], "FIRED #30")
            and fire_names(9, ["r11-a"], "FIRED fixer R11-A") and not fire_names(9, ["r11-a"], "FIRED r11-ab"))
    import contextlib
    import io
    real = globals()["read_world"]
    try:
        for answer, rc_want, out_want in ((Unreadable("open pull requests: x"), 2, "cp-owed: UNREADABLE open pull requests: x\n"),
                                          (_aged(_world("merge-no-approval", True)[:6]), 0, "CP-OWED merge-no-approval #11 ")):
            def stub(*a, answer=answer):
                if isinstance(answer, Exception):
                    raise answer
                return answer
            globals()["read_world"] = stub
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(["cp-owed", "--fired", "/dev/null"])
            res[f"main: cp-owed exits {rc_want} printing {out_want.split(':')[0].split(' #')[0].strip()}"] = (
                rc == rc_want and buf.getvalue().startswith(out_want))
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                main(["cp-owed"])
                res["main: cp-owed without --fired is a usage error"] = False
            except SystemExit as e:
                res["main: cp-owed without --fired is a usage error"] = e.code == 2
    finally:
        globals()["read_world"] = real
    failed = 0
    for name, ok in res.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        failed += not ok
    total = len(res)
    full = Path(__file__).read_text()
    cut = full.index(SELF_TEST_MARK)  # a site is counted and edited above the self-test only
    src, rest = full[:cut], full[cut:]
    with tempfile.TemporaryDirectory() as d:
        for i, (mname, (old, new, case)) in enumerate(MUTANTS.items()):
            total += 1
            if src.count(old) != 1:
                print(f"  FAIL mutant {mname}: its site appears {src.count(old)} times")
                failed += 1
                continue
            p = Path(d) / f"owed_watch_m{i}.py"
            p.write_text(src.replace(old, new) + rest)
            spec = importlib.util.spec_from_file_location(f"owed_watch_m{i}", p)
            m = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(m)
                killed = cases(m).get(case) is False
            except Exception as e:  # a crash is no kill
                print(f"    mutant {mname} crashed: {e.__class__.__name__}: {e}")
                killed = False
            print(f"  {'ok  ' if killed else 'FAIL'} mutant {mname} killed by: {case}")
            failed += not killed
    print(f"owed_watch self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
