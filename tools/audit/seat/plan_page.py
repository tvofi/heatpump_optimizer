#!/usr/bin/env python3
"""The round's plan page: plan.json and the roster drawn as one HTML file.

    python3 tools/plan/replan.py --out plan.json
    python3 tools/audit/seat/plan_page.py --plan plan.json --html plan.html \
        [--repo .] [--roster-ref REF] [--roster-path PATH] \
        [--gh-repo OWNER/REPO] [--github-snapshot snapshot.json] [--no-fetch]
    python3 tools/audit/seat/plan_page.py --self-test

It draws; it does not plan. Every schedule fact on the page -- each group's
start, finish, wave and lane; the critical path; the stamps; the closure; the
duration model -- is read from `plan.json`, which `tools/plan/replan.py`
writes. A second computation would be a second answer, and the page would
disagree with the plan it claims to show. `plan_table.py` is the markdown
artifact over the roster alone; this is the page over the plan.

What it reads live is display state, not schedule: the roster (through
`roster_lib`, at the plan's own `generated.roster_ref` unless `--roster-ref`
names another; an `origin/` ref is fetched first unless `--no-fetch`), and
from GitHub the issue states, the open pull requests and the merged
pull-request titles, heads and merge commits (`gh`, or a `--github-snapshot`
JSON file of the same shape: {"issues": [{number, title, state}],
"open_prs": [{number, head_ref, title}], "merged_prs": [{number, title,
head_ref, merge_commit_sha, merged_at}]}).

REFUSALS (exit 1, nothing written): a plan `replan.stale_reason` calls stale
-- its roster blob is not the roster's blob at the ref now -- and a plan
`replan.check_plan` refuses. The freshness rule is replan.py's, so `--check`
and this page cannot disagree about which plans are current.

Status classes, one per group:
  done     resume.stage in roster_lib.DONE_STAGES; labelled with the PR it
           merged through (merge commit first, then the latest merged PR
           whose branch answers for the group, then the commit's sha8);
  live     resume.stage in replan.LIVE_STAGES (queued for a slot when the
           plan starts it later than the replan instant);
  partial  a merged `R<N>-GROUP:` titled PR delivered part of an open group;
  blocked  an `after` target is not done, and nothing of it merged;
  ready    everything else.
A branch answers for a group by `roster_lib.group_for_branch`, then by its
last segment against the tails of the roster's `resume.branch` values (with a
`-pr` suffix dropped): `fix/r10-ci-layout-g` names R10-CI-LAYOUT only that way;
failing both, by the one roster group id its title names.

`--self-test` drives every arm from fixtures in a throwaway repository, and
never reaches GitHub: the fetch is replaced by one that fails the test.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(_SEAT))
sys.path.insert(0, str(_SEAT.parents[1] / "plan"))
import roster_lib  # noqa: E402 -- the one roster reader
import replan  # noqa: E402 -- the one owner of plan.json and its freshness

SELF = "tools/audit/seat/plan_page.py"
# The round's tracking issue (CLAUDE.md's #201): the open-issue count leaves it
# out, because it stays open for the whole programme by design.
TRACKING_ISSUE = 201
_ROUND_PREFIX = re.compile(r"\AR\d+-")
_GROUP_ID = re.compile(r"\bR\d+(?:-[A-Z0-9]+)+\b")
_DELIVERY_TITLE = re.compile(r"\A(R\d+-[A-Z0-9-]+):")
_ISO = "%Y-%m-%dT%H:%M:%SZ"


def _t(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, _ISO)


def short(group: str) -> str:
    """A group id without its round prefix: `R10-CI-LAYOUT` -> `CI-LAYOUT`."""
    return _ROUND_PREFIX.sub("", group)


def _stage(group: dict) -> str | None:
    return (group.get("resume") or {}).get("stage")


# ------------------------------------------------------------------- GitHub

def fetch_github(gh_repo: str) -> dict:
    """The snapshot this page reads, from `gh`. The page's only network edge."""
    def gh(*args: str) -> str:
        return subprocess.run(["gh", *args], check=True, capture_output=True,
                              text=True).stdout

    issues = json.loads(gh("issue", "list", "-R", gh_repo, "--state", "all",
                           "--limit", "20000", "--json", "number,title,state"))
    open_prs = [{"number": p["number"], "head_ref": p["headRefName"],
                 "title": p["title"]}
                for p in json.loads(gh("pr", "list", "-R", gh_repo, "--state", "open",
                                       "--limit", "1000", "--json",
                                       "number,headRefName,title"))]
    # Every merged PR, no list cap: closed pulls carrying a merged_at.
    text = gh("api", "--paginate",
              f"repos/{gh_repo}/pulls?state=closed&per_page=100")
    dec, i, pulls = json.JSONDecoder(), 0, []
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        page, i = dec.raw_decode(text, i)
        pulls.extend(page)
    merged = [{"number": p["number"], "title": p["title"],
               "head_ref": p["head"]["ref"], "merge_commit_sha": p.get("merge_commit_sha"),
               "merged_at": p["merged_at"]} for p in pulls if p.get("merged_at")]
    return {"issues": issues, "open_prs": open_prs, "merged_prs": merged}


# -------------------------------------------------------------------- model

def group_of_branch(roster: dict, branch: str) -> str | None:
    """roster_lib's lookup first; the tail of a roster `resume.branch` only as
    the fallback (it is what maps `fix/r10-ci-layout-g` to R10-CI-LAYOUT)."""
    found = roster_lib.group_for_branch(roster, branch)
    if found or not branch:
        return found
    tails = {}
    for g in roster.get("groups", []):
        b = (g.get("resume") or {}).get("branch") or ""
        if b:
            tails[b.rsplit("/", 1)[-1]] = g["group"]
    tail = branch.rsplit("/", 1)[-1]
    return tails.get(tail) or tails.get(tail.replace("-pr", ""))


def group_of_pr(roster: dict, branch: str, title: str) -> str | None:
    """The group a PR answers for: by branch, else the one roster group id its
    title names (`... (R10-PREPR-CAP)`; #2528's branch names no group)."""
    found = group_of_branch(roster, branch)
    if found:
        return found
    ids = set(roster_lib.groups_of(roster))
    named = {m for m in _GROUP_ID.findall(title or "") if m in ids}
    return named.pop() if len(named) == 1 else None


def merged_pr(group: str, commit: str | None, by_sha: dict, by_group: dict):
    """The PR a done group landed through: by merge commit, else by branch."""
    if commit and len(commit) >= 7:
        for sha, n in by_sha.items():
            if sha.startswith(commit) or commit.startswith(sha[:len(commit)]):
                return n
    return by_group.get(group)


def build_rows(roster: dict, plan: dict, snap: dict) -> list:
    """One row per roster group: status, PR, issues, blockers, schedule."""
    G = roster_lib.groups_of(roster)
    PG = plan["groups"]
    start0 = plan["generated"]["start"]
    crit = set(plan["critical_path"])
    done = {g for g in G if not roster_lib.is_open(G[g])}

    open_pr: dict = {}
    for p in sorted(snap["open_prs"], key=lambda p: p["number"]):
        g = group_of_pr(roster, p["head_ref"], p.get("title", ""))
        if g:
            open_pr.setdefault(g, []).append(p["number"])
    delivered: dict = {}
    by_sha, by_group = {}, {}
    for p in sorted(snap["merged_prs"], key=lambda p: p["merged_at"]):
        m = _DELIVERY_TITLE.match(p["title"])
        if m and m.group(1) in G:
            delivered.setdefault(m.group(1), []).append(p["number"])
        if p.get("merge_commit_sha"):
            by_sha[p["merge_commit_sha"]] = p["number"]
        g = group_of_pr(roster, p["head_ref"], p.get("title", ""))
        if g:
            by_group[g] = p["number"]  # the latest merge for the group
    state = {i["number"]: i for i in snap["issues"]}

    rows = []
    for g, entry in G.items():
        pg = PG[g]
        blk = [a for a in entry.get("after") or [] if a in G and a not in done]
        part = sorted(delivered.get(g) or [])
        sfx = f", part merged #{', #'.join(map(str, part))}" if part else ""
        pr = ", ".join(f"#{n}" for n in open_pr.get(g, [])) or "—"
        if g in done:
            commit = (entry.get("resume") or {}).get("commit")
            n = merged_pr(g, commit, by_sha, by_group)
            st = "done"
            if n:
                label, pr = f"merged PR #{n}", f"#{n}"
            elif commit:
                label, pr = f"merged at {commit[:8]}", "merged"
            else:
                label, pr = "folded into another group (no merge of its own)", "merged"
        elif _stage(entry) in replan.LIVE_STAGES:
            st = "live"
            queued = not pg.get("inherited") and pg["start"] > start0
            label = _stage(entry) + (", queued for a slot" if queued else "") + sfx
        elif blk and not part:
            st, label = "blocked", "waiting on " + ", ".join(map(short, blk))
        elif part:
            st = "partial"
            label = (f"part merged #{', #'.join(map(str, part))}, residual open"
                     + (", waiting on " + ", ".join(map(short, blk)) if blk else ""))
        else:
            st, label = "ready", "ready"
        fixes = set(entry.get("fixes") or [])
        rows.append({
            "g": g, "lane": pg["lane"], "st": st, "label": label, "pr": pr,
            "issues": [(n, n in fixes, (state.get(n) or {}).get("state") != "CLOSED",
                        (state.get(n) or {}).get("title", ""))
                       for n in entry.get("issues") or []],
            "blk": blk, "desc": roster_lib.one_line_brief(entry, 170),
            "crit": g in crit, "wave": None if g in done else pg["wave"],
            "start": None if g in done else pg["start"],
            "finish": None if g in done else pg["finish"]})
    rows.sort(key=lambda r: (r["st"] != "done", r["finish"] or "", r["g"]))
    return rows


# ---------------------------------------------------------------------- svg

def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
    """The SVG chart on the plan's time axis; and how many critical-path links
    it draws (a link crossing more than one lane or two hours is left to the
    ◆ marks and the caption)."""
    now = _t(plan["generated"]["start"])
    # The axis runs to the last planned stamp: the minor stamp lands after
    # closure, and an axis ending at closure would not draw it.
    end = max([_t(plan["summary"]["closure"])] + [_t(s["at"]) for s in plan["stamps"]])
    slots = plan["generated"]["caps"]["slots"]
    span_h = max(1.0, (end - now).total_seconds() / 3600)
    W, LW, RH = 1180, 120, 24

    def px(t: dt.datetime) -> float:
        return LW + (t - now).total_seconds() / 3600 / span_h * (W - LW - 20)

    open_rows = [dict(r, s=_t(r["start"]), f=_t(r["finish"]))
                 for r in rows if r["st"] != "done"]
    lanes = list(replan.LANES) + sorted({r["lane"] for r in open_rows} - set(replan.LANES))
    tracks_of: dict = {lane: [] for lane in lanes}
    for r in open_rows:
        for track in tracks_of[r["lane"]]:
            if all(r["s"] >= o["f"] or r["f"] <= o["s"] for o in track):
                track.append(r)
                break
        else:
            tracks_of[r["lane"]].append([r])
    parts, ypos, y = [], {}, 34 + 52 + 6
    # Occupancy: groups in flight each hour against the slot cap, from the
    # plan's own start and finish -- the constraint made visible, not re-run.
    occ = [(now + dt.timedelta(hours=h),
            sum(1 for r in open_rows if r["s"] <= now + dt.timedelta(hours=h) < r["f"]))
           for h in range(int(span_h) + 1)]
    top = max([slots] + [c for _, c in occ])

    def oy(c: int) -> float:
        return 34 + 52 - (c / top) * 46

    parts.append('<polyline points="' + " ".join(f"{px(t):.1f},{oy(c):.1f}" for t, c in occ)
                 + '" class="occ"/>')
    parts.append(f'<line x1="{LW}" y1="{oy(slots):.1f}" x2="{W - 20}" y2="{oy(slots):.1f}" '
                 f'class="slotcap"/><text x="10" y="46" class="lanelab">slots</text>'
                 f'<text x="10" y="62" class="tick">cap {slots}</text>')
    for h in range(0, int(span_h) + 1, 12):
        t = now + dt.timedelta(hours=h)
        parts.append(f'<line x1="{px(t):.1f}" y1="{y}" x2="{px(t):.1f}" y2="__H__" class="grid"/>'
                     f'<text x="{px(t):.1f}" y="14" class="tick">{t.strftime("%a %Hh")}</text>')
    lane_idx = {}
    for li, lane in enumerate(lanes):
        lane_idx[lane] = li
        tracks = tracks_of[lane] or [[]]
        h = len(tracks) * (RH + 6) + 10
        parts.append(f'<rect x="0" y="{y}" width="{W}" height="{h}" class="lane"/>'
                     f'<text x="10" y="{y + 18}" class="lanelab">{html.escape(lane)}</text>')
        for i, track in enumerate(tracks):
            for r in track:
                x0, x1 = px(r["s"]), px(r["f"])
                yy = y + 6 + i * (RH + 6)
                ypos[r["g"]] = (x0, x1, yy + RH / 2)
                name, w = short(r["g"]), max(x1 - x0, 4)
                # A label stays inside its bar, cut to fit, or is not drawn:
                # text outside a box reads as naming the next bar along.
                room = int((w - (18 if r["crit"] else 8)) / 6.2)
                txt = name if room >= len(name) else (name[:room - 1] + "…" if room >= 4 else "")
                when = r["s"].strftime("%a %d %b %H:%M")
                parts.append(
                    f'<g class="grp" data-st="{r["st"]}" data-name="{html.escape(name)}" '
                    f'data-state="{html.escape(r["label"])}" data-start="{when}" '
                    f'data-eta="{r["finish"]}" data-wave="{r["wave"]}">'
                    f'<title>{r["g"]}: {html.escape(r["label"])}, starts {when}, '
                    f'ETA {r["finish"]}, wave {r["wave"]}</title>')
                if w < 16:  # widen a narrow bar's hover target, not the bar
                    parts.append(f'<rect x="{x0 - 3:.1f}" y="{yy}" width="{w + 8:.1f}" '
                                 f'height="{RH}" fill="transparent"/>')
                parts.append(f'<rect x="{x0:.1f}" y="{yy}" width="{w:.1f}" height="{RH}" '
                             f'rx="3" class="bar {r["st"]}{" crit" if r["crit"] else ""}"/>')
                if r["crit"]:
                    parts.append(f'<text x="{x0 + 3:.1f}" y="{yy + 16}" class="critmark">◆</text>')
                if txt:
                    parts.append(f'<text x="{x0 + 13:.1f}" y="{yy + 16}" class="barlab">'
                                 f'{html.escape(txt)}</text>')
                parts.append("</g>")
        y += h + 4
    PG, arrows = plan["groups"], []
    chain = plan["critical_path"]
    for a, b in zip(chain, chain[1:]):
        if a not in ypos or b not in ypos:
            continue
        gap_h = abs((_t(PG[b]["start"]) - _t(PG[a]["finish"])).total_seconds()) / 3600
        if abs(lane_idx[PG[a]["lane"]] - lane_idx[PG[b]["lane"]]) > 1 or gap_h > 2:
            continue
        (ax, ay), (bx, by) = ypos[a][1:], (ypos[b][0], ypos[b][2])
        if abs(bx - ax) < 2 and abs(by - ay) < 2:
            continue  # back to back: the bars already touch
        arrows.append(f'<path d="M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}" class="critline"/>')
    for s in plan["stamps"]:
        x = px(_t(s["at"]))
        if x <= W - 10:
            parts.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{y}" class="stampline"/>'
                         f'<text x="{x + 3:.1f}" y="{y + 14}" class="stamplab">'
                         f'{html.escape(s["version"])}</text>')
    svg = (f'<svg viewBox="0 0 {W} {y + 22}" width="{W}" role="img" aria-label="Swimlanes">'
           + "".join(parts).replace("__H__", str(y)) + "".join(arrows) + "</svg>")
    return svg, len(arrows)


# --------------------------------------------------------------------- page

def _when(s: str) -> str:
    return _t(s).strftime("%a %d %b %H:%M")


def render(roster: dict, roster_src: str, plan: dict, snap: dict) -> str:
    """The page. Pure: every input is an argument."""
    rows = build_rows(roster, plan, snap)
    svg, drawn = swimlanes(plan, rows)
    gen, summ = plan["generated"], plan["summary"]
    caps, model = gen["caps"], gen["model"]
    slots, every = caps["slots"], caps["stamp_every"]
    chain = plan["critical_path"]
    waves_of = {g: w["wave"] for w in plan["waves"] for g in w["groups"]}
    counts = {k: sum(1 for r in rows if r["st"] == k)
              for k in ("done", "live", "ready", "partial", "blocked")}
    open_iss = sum(1 for i in snap["issues"]
                   if i["state"] == "OPEN" and i["number"] != TRACKING_ISSUE)
    order = {k: i for i, k in enumerate(("S", "M", "L", "XL"))}
    sizes = ", ".join(f"{k} {v:g} h" for k, v in sorted(
        model["sizes_hours"].items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))
    e = html.escape

    def chip(n, closer, is_open, title):
        cls = "chip" + (" closer" if closer else "") + ("" if is_open else " closed")
        return f'<span class="{cls}" title="{e(title)}">#{n}</span>'

    trs = "".join(
        f'<tr class="{r["st"]}" data-st="{r["st"]}"><td class="g">'
        + ('<span class="cp" title="critical path">◆</span>' if r["crit"] else "")
        + f'{e(short(r["g"]))}<div class="lanec">{e(r["lane"])}</div></td>'
        f'<td class="d">{e(r["desc"])}</td>'
        f'<td><span class="pill {r["st"]}">{e(r["label"])}</span></td>'
        f'<td class="mono">{e(r["pr"])}</td>'
        f'<td>{"".join(chip(*i) for i in r["issues"]) or "—"}</td>'
        f'<td class="blk">{e(", ".join(map(short, r["blk"]))) or "—"}</td>'
        f'<td class="mono">{r["finish"] or "—"}</td>'
        f'<td class="mono">{r["wave"] or "—"}</td></tr>' for r in rows)
    stamps = "".join(
        f'<tr><td class="mono">{e(s["version"])}</td><td class="mono">{_when(s["at"])}</td>'
        f'<td>{e(", ".join(map(short, s["carries"])) or "—")}</td>'
        f'<td class="mono">{e(s["kind"])}</td></tr>' for s in plan["stamps"])
    waves = "".join(
        f'<tr><td class="mono">{w["wave"]}</td><td class="mono">{_when(w["opens"])}</td>'
        f'<td class="mono">{_when(w["drains"])}</td>'
        f'<td>{e(", ".join(map(short, w["groups"])) or "—")}</td>'
        f'<td class="mono">{e(w["stamp"] or "—")}</td></tr>' for w in plan["waves"])
    crit = " → ".join(f'{e(short(g))} <span class="cpw">w{waves_of.get(g, "—")}</span>'
                      for g in chain)
    inherited = len((gen.get("inherited_coordinator") or {}).get("groups") or [])
    try:
        rnd = f"Round {roster_lib.roster_round(roster_src.rsplit(':', 1)[-1])} "
    except roster_lib.RosterNotFound:
        rnd = ""
    fill = {
        "title": f"{rnd}Fix Plan",
        "now": _t(gen["start"]).strftime("%d %b %H:%M"),
        "source": e(f'{roster_src} @ {gen["roster_blob"][:12]}'),
        "tracking": str(TRACKING_ISSUE), "open_iss": str(open_iss),
        "end": _t(summ["closure"]).strftime("%a %d %b %H:%M"),
        "svg": svg, "crit": crit or "—", "trs": trs, "stamps": stamps, "waves": waves,
        "slots": str(slots), "every": str(every),
        "slots_note": e(
            f"Read from plan.json: {summ['groups_open']} open groups, {summ['batches']} "
            f"merge batches, closure {summ['closure']}. A wave is the set of groups "
            f"dispatched at one instant; the next opens as soon as one of the {slots} "
            f"pull-request slots frees. Coordinator cap {caps['coordinator_cap']}; "
            f"{inherited} inherited in-progress coordinator groups are recorded in "
            f"plan.json. The line above the lanes is how many groups are in flight at "
            f"each hour, riding the cap. Stamps: one patch per {every} production groups, "
            f"the minor at closure. Hover any bar, however narrow, for its name, state, "
            f"start, ETA and wave. {drawn} of {max(0, len(chain) - 1)} critical-path links "
            f"are drawn; the ◆ and the caption carry the rest."),
        "sizes": e(sizes),
        "sizes_provenance": e(model.get("sizes_provenance") or ""),
        "live_pct": f"{model['live_remaining_fraction'] * 100:g}",
        "window": f"{caps['batch_window_minutes']:g}",
    }
    fill.update({f"n_{k}": str(v) for k, v in counts.items()})
    page = re.sub(r"\{\{(\w+)\}\}", lambda m: fill[m.group(1)], _TEMPLATE)
    return page


# ---------------------------------------------------------------------- cli

def main(argv=None, fetch=fetch_github) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plan")
    p.add_argument("--html", help="the page to write")
    p.add_argument("--repo", default=".")
    p.add_argument("--roster-ref", default=None,
                   help="default: the plan's own generated.roster_ref")
    p.add_argument("--roster-path", default=None)
    p.add_argument("--gh-repo", default="tvofi/heatpump_optimizer")
    p.add_argument("--github-snapshot", default=None,
                   help="read GitHub state from this JSON file instead of gh")
    p.add_argument("--no-fetch", action="store_true",
                   help="read an origin/ roster ref as this clone has it")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return _self_test()
    if not (a.plan and a.html):
        p.error("--plan and --html are required")
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    ref = a.roster_ref or plan["generated"].get("roster_ref") or ""
    if ref.startswith("origin/") and not a.no_fetch:
        r = subprocess.run(["git", "-C", a.repo, "fetch", "-q", "origin",
                            f"+refs/heads/{ref[7:]}:refs/remotes/{ref}"],
                           capture_output=True, text=True)
        if r.returncode:
            print(f"plan_page: refused: cannot fetch {ref} to test freshness: "
                  f"{r.stderr.strip()[:200]} (--no-fetch reads it as it is)",
                  file=sys.stderr)
            return 1
    bad = replan.check_plan(plan)
    stale = replan.stale_reason(plan, a.repo, ref, a.roster_path)
    if stale:
        bad.append(f"freshness: {stale}")
    if bad:
        print(f"plan_page: refused, nothing written: {len(bad)} violation(s)",
              file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        return 1
    if "model" not in plan["generated"]:
        print("plan_page: refused, nothing written: plan.json records no duration "
              "model (generated.model); re-run tools/plan/replan.py", file=sys.stderr)
        return 1
    path = roster_lib.roster_path(a.repo, ref, a.roster_path)
    roster = roster_lib.show_roster(a.repo, ref, path)
    snap = (json.loads(Path(a.github_snapshot).read_text(encoding="utf-8"))
            if a.github_snapshot else fetch(a.gh_repo))
    page = render(roster, f"{ref}:{path}", plan, snap)
    Path(a.html).write_text(page, encoding="utf-8")
    print(f"wrote {a.html}: {len(roster_lib.groups_of(roster))} groups, "
          f"closure {plan['summary']['closure']}")
    return 0


# ------------------------------------------------------------------ self-test

def _self_test() -> int:
    """Every status class, the PR lookups, the struck chip, the summary strip,
    the filled methodology text, and the stale refusal -- all offline."""
    import tempfile
    sys.path.insert(0, str(_SEAT.parents[2] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    fails: list = []
    n = [0]

    def check(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {str(got)[:300]})")

    def grp(gid, lane, after=(), stage="not-started", branch="", commit=None,
            issues=(), fixes=()):
        resume = {"stage": stage}
        if branch:
            resume["branch"] = branch
        if commit:
            resume["commit"] = commit
        return {"group": gid, "lane": lane, "kind": "defect", "size": "S",
                "after": list(after), "issues": list(issues), "fixes": list(fixes),
                "brief": f"tvofi, 2026-01-01: Does {gid}. More.", "resume": resume}

    roster = {"groups": [
        grp("R9-DONE-SHA", "CO", stage="done", commit="aaaaaaa1", issues=(11,), fixes=(11,)),
        grp("R9-DONE-BR", "CO", stage="done", commit="bbbbbbbb"),
        grp("R9-DONE-NONE", "LE", stage="done", commit="cccccccc"),
        grp("R9-LIVE", "LE", stage="in-progress", branch="fix/r9-live-g", issues=(12,)),
        grp("R9-PART", "UX"),
        grp("R9-BLOCK", "UX", after=("R9-LIVE",)),
        grp("R9-READY", "IN", after=("R9-DONE-SHA",), issues=(13,), fixes=(13,)),
    ]}
    snap = {
        "issues": [{"number": 11, "title": "eleven", "state": "CLOSED"},
                   {"number": 12, "title": "twelve", "state": "OPEN"},
                   {"number": 13, "title": "thirteen", "state": "OPEN"},
                   {"number": TRACKING_ISSUE, "title": "tracking", "state": "OPEN"}],
        # head `handoff/r9-live-g-pr`: not resume.branch, and its tail is not
        # the group id, so only the tail fallback answers for R9-LIVE.
        "open_prs": [{"number": 31, "head_ref": "handoff/r9-live-g-pr", "title": "x"},
                     {"number": 32, "head_ref": "fix/other", "title": "ci: y (R9-READY)"},
                     {"number": 33, "head_ref": "fix/two", "title": "R9-READY and R9-PART"}],
        "merged_prs": [
            # #21 names its group by neither branch nor title: only the merge
            # commit the roster records ties it to R9-DONE-SHA.
            {"number": 21, "title": "x", "head_ref": "elsewhere",
             "merge_commit_sha": "aaaaaaa1" + "0" * 32, "merged_at": "2026-01-01T00:00:00Z"},
            {"number": 22, "title": "y", "head_ref": "fix/r9-done-br",
             "merge_commit_sha": "d" * 40, "merged_at": "2026-01-02T00:00:00Z"},
            {"number": 23, "title": "R9-PART: part one", "head_ref": "fix/r9-part-1",
             "merge_commit_sha": "e" * 40, "merged_at": "2026-01-03T00:00:00Z"}]}
    durations = json.loads((_SEAT.parents[1] / "plan" / "durations.json").read_text())
    start = dt.datetime(2026, 1, 5, 0, 0)

    def fetch_refused(_repo):
        fails.append("the self-test reached for GitHub")
        raise SystemExit(3)

    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        rpath = repo / roster_lib.ROSTERS_DIR / "wave-r9-groups.json"
        rpath.parent.mkdir(parents=True)
        throwaway_git_init(repo, "-q", "-b", "main")

        def commit(r: dict) -> None:
            rpath.write_text(json.dumps(r), encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "r"], check=True)
        commit(roster)
        r_, ref_, blob_ = replan.load_roster(str(repo), "main")
        plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS), start,
                                 "v1.0.0", ref_, blob_)
        planf, snapf = Path(td) / "plan.json", Path(td) / "snap.json"
        planf.write_text(json.dumps(plan), encoding="utf-8")
        snapf.write_text(json.dumps(snap), encoding="utf-8")

        rows = {r["g"]: r for r in build_rows(roster, plan, snap)}
        st = {g: (r["st"], r["label"], r["pr"]) for g, r in rows.items()}
        check("done: the PR is found by merge commit",
              st["R9-DONE-SHA"] == ("done", "merged PR #21", "#21"), st["R9-DONE-SHA"])
        check("done: the PR is found by branch when no merge commit matches",
              st["R9-DONE-BR"] == ("done", "merged PR #22", "#22"), st["R9-DONE-BR"])
        check("done: no PR found falls back to the commit's sha8",
              st["R9-DONE-NONE"] == ("done", "merged at cccccccc", "merged"),
              st["R9-DONE-NONE"])
        check("live", st["R9-LIVE"][0] == "live" and st["R9-LIVE"][1] == "in-progress",
              st["R9-LIVE"])
        check("the open PR maps by the branch-tail fallback",
              st["R9-LIVE"][2] == "#31", st["R9-LIVE"])
        check("the fallback is needed: roster_lib alone does not map it",
              roster_lib.group_for_branch(roster, "handoff/r9-live-g-pr") is None)
        check("an open PR whose branch names no group maps by its title",
              st["R9-READY"][2] == "#32", st["R9-READY"])
        check("a title naming two groups maps to neither",
              "#33" not in st["R9-PART"][2] + st["R9-READY"][2], st["R9-PART"])
        check("partial: a merged R9-PART: title on an open group",
              st["R9-PART"][:2] == ("partial", "part merged #23, residual open"),
              st["R9-PART"])
        check("blocked: an after target not done",
              st["R9-BLOCK"][:2] == ("blocked", "waiting on LIVE"), st["R9-BLOCK"])
        check("ready: its only after target is done", st["R9-READY"][0] == "ready",
              st["R9-READY"])
        check("blocked-by is the roster's after less the done groups",
              rows["R9-BLOCK"]["blk"] == ["R9-LIVE"] and rows["R9-READY"]["blk"] == [],
              (rows["R9-BLOCK"]["blk"], rows["R9-READY"]["blk"]))

        page = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
                      plan, snap)
        check("a closed issue's chip is struck",
              '<span class="chip closer closed" title="eleven">#11</span>' in page)
        check("an open issue's chip is not",
              '<span class="chip" title="twelve">#12</span>' in page
              and '<span class="chip closer" title="thirteen">#13</span>' in page)
        for cls, want in (("done", 3), ("live", 1), ("ready", 1), ("partial", 1),
                          ("blocked", 1)):
            check(f"rows carry the {cls} class", page.count(f'<tr class="{cls}"') == want,
                  page.count(f'<tr class="{cls}"'))
            check(f"the summary strip counts {cls}",
                  f"<b>{want}</b><span>{_STRIP[cls]}</span>" in page)
        check("the open-issue count leaves out the tracking issue",
              "<b>2</b><span>open issues" in page)
        check("every template field is filled", "{{" not in page,
              re.findall(r"\{\{\w+\}\}", page))
        check("the round comes from the roster path", "<h1>Round 9 Fix Plan</h1>" in page)
        model = plan["generated"]["model"]
        check("the methodology states the plan's sizes and live fraction",
              f"S {model['sizes_hours']['S']:g} h" in page
              and f"{model['live_remaining_fraction'] * 100:g}%" in page)
        check("every open group has a bar; no done group does",
              all(f'data-name="{short(g)}"' in page for g in rows if rows[g]["st"] != "done")
              and 'data-name="DONE-SHA"' not in page)
        check("critical-path groups carry the mark",
              all(rows[g]["crit"] for g in plan["critical_path"])
              and page.count('class="critmark"') == len(plan["critical_path"]))
        check("a planned stamp is drawn", 'class="stampline"' in page)
        check("the filter and hide-merged controls ship",
              'id="hide-done"' in page and 'data-f="blocked"' in page)
        check("no machine path in the page", not re.search(r"/(home|Users|tmp)/", page))

        out = Path(td) / "page.html"
        argv = ["--plan", str(planf), "--html", str(out), "--repo", str(repo),
                "--github-snapshot", str(snapf)]
        check("a fresh plan renders (null control)",
              main(argv, fetch=fetch_refused) == 0 and out.is_file())
        out.unlink()
        moved = json.loads(json.dumps(roster))
        moved["groups"][3]["resume"]["stage"] = "done"
        commit(moved)
        rc = main(argv, fetch=fetch_refused)
        check("a stale plan is refused, nothing written",
              rc == 1 and not out.exists(), (rc, out.exists()))
        check("and replan --check refuses the same plan",
              bool(replan.stale_reason(plan, str(repo))))
    print(f"plan_page self-test: {n[0]} checks, {len(fails)} failed")
    for f in fails:
        print("FAIL", f)
    return 1 if fails else 0


_STRIP = {"done": "groups merged", "live": "fixers working", "ready": "ready, not started",
          "blocked": "waiting on a group", "partial": "part merged, residual open"}

# The page. `{{name}}` is filled by `render`; every value is escaped there.
_TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{
  --bg:#f3f5f6; --panel:#ffffff; --fg:#17232b; --muted:#5d6b74; --line:#d8dee2;
  --accent:#d9561f; --done:#2f8f5b; --live:#1f6fb0; --ready:#a07a00; --blocked:#8a96a0; --partial:#75508f;
  --done-bg:#e3f2ea; --live-bg:#e2eef8; --ready-bg:#f6efd6; --blocked-bg:#eceff1; --partial-bg:#efe8f6;
  --display:"Barlow Condensed","Arial Narrow",sans-serif; --body:"Source Sans 3","Segoe UI",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#10171c; --panel:#162028; --fg:#e4ebef; --muted:#93a3ad; --line:#2a3842;
  --accent:#f07a42; --done:#5cc48a; --live:#5aa7e6; --ready:#d9b440; --blocked:#76848e; --partial:#b78be0;
  --done-bg:#173226; --live-bg:#152b3d; --ready-bg:#33290f; --blocked-bg:#1e2a32; --partial-bg:#2a1f38; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#10171c; --panel:#162028; --fg:#e4ebef; --muted:#93a3ad; --line:#2a3842;
  --accent:#f07a42; --done:#5cc48a; --live:#5aa7e6; --ready:#d9b440; --blocked:#76848e; --partial:#b78be0;
  --done-bg:#173226; --live-bg:#152b3d; --ready-bg:#33290f; --blocked-bg:#1e2a32; --partial-bg:#2a1f38; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.45 var(--body);margin:0;padding:20px 16px 40px}
main{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:22px}
h1{font:700 2.1rem/1 var(--display);letter-spacing:.01em;margin:0}
h2{font:600 1.25rem/1.1 var(--display);letter-spacing:.04em;text-transform:uppercase;margin:0 0 10px}
.sub{color:var(--muted);margin:6px 0 0}
.strip{display:flex;flex-wrap:wrap;gap:10px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:10px 14px;min-width:120px;flex:1}
.stat b{display:block;font:600 1.6rem/1.1 var(--mono);font-variant-numeric:tabular-nums}
.stat span{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.stat.end b{color:var(--accent);font-size:1.15rem;padding-top:6px}
section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;min-width:0}
.scroll{overflow-x:auto}
svg{display:block;font-family:var(--mono)}
.grid{stroke:var(--line);stroke-width:1}
.tick{fill:var(--muted);font-size:10px}
.lane{fill:transparent;stroke:var(--line)}
.lanelab{fill:var(--muted);font:600 13px var(--display);letter-spacing:.05em;text-transform:uppercase}
.bar{stroke-width:1}
.bar.live{fill:var(--live-bg);stroke:var(--live)}
.bar.ready{fill:var(--ready-bg);stroke:var(--ready)}
.bar.blocked{fill:var(--blocked-bg);stroke:var(--blocked)}
.bar.partial{fill:var(--partial-bg);stroke:var(--partial);stroke-dasharray:3 2}
.bar.crit{stroke:var(--accent);stroke-width:2.2}
.barlab{fill:var(--fg);font-size:10.5px;paint-order:stroke;stroke:var(--panel);stroke-width:3;stroke-linejoin:round}
.critline{fill:none;stroke:var(--accent);stroke-width:1.6;stroke-dasharray:4 3;opacity:.85}
.critmark{fill:var(--accent);font-size:10px;paint-order:stroke;stroke:var(--panel);stroke-width:2.5;stroke-linejoin:round}
.cpw{color:var(--muted);font:600 .8em var(--mono)}
.occ{fill:none;stroke:var(--accent);stroke-width:1.6;opacity:.9}
.slotcap{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 3}
.stampline{stroke:var(--done);stroke-width:1.2;stroke-dasharray:1 3}
.stamplab{fill:var(--done);font-size:10px;font-weight:600}
.chk{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;color:var(--muted);margin-left:6px}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:.85rem;color:var(--muted);margin-top:10px}
.legend i{display:inline-block;width:14px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px;border:1px solid}
.cpnote{font-size:.9rem;margin-top:8px}
.cpnote b{color:var(--accent)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th{font:600 .8rem var(--display);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;border-bottom:2px solid var(--line);padding:6px 8px;white-space:nowrap}
td{border-bottom:1px solid var(--line);padding:7px 8px;vertical-align:top}
td.g{font:600 .85rem var(--mono);white-space:nowrap}
td.d{min-width:260px;max-width:440px}
.lanec{font:400 .72rem var(--body);color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap;font-size:.82rem}
.blk{color:var(--muted);font-size:.82rem;max-width:200px}
.cp{color:var(--accent);margin-right:4px}
.pill{display:inline-block;border-radius:999px;padding:1px 9px;font-size:.78rem;white-space:nowrap;border:1px solid}
.pill.done{background:var(--done-bg);color:var(--done);border-color:var(--done)}
.pill.live{background:var(--live-bg);color:var(--live);border-color:var(--live)}
.pill.ready{background:var(--ready-bg);color:var(--ready);border-color:var(--ready)}
.pill.blocked{background:var(--blocked-bg);color:var(--blocked);border-color:var(--blocked)}
.pill.partial{background:var(--partial-bg);color:var(--partial);border-color:var(--partial);border-style:dashed}
.chip{display:inline-block;font:.76rem var(--mono);border:1px solid var(--line);border-radius:4px;padding:0 5px;margin:0 3px 3px 0}
.chip.closer{border-color:var(--fg);font-weight:600}
.chip.closed{text-decoration:line-through;color:var(--muted)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}
.filters button{font:600 .8rem var(--body);background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:999px;padding:4px 12px;cursor:pointer}
.filters button[aria-pressed="true"]{background:var(--fg);color:var(--panel);border-color:var(--fg)}
.filters button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.note{color:var(--muted);font-size:.85rem;max-width:72ch}
.tip{position:fixed;z-index:20;max-width:300px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 10px;font:12px/1.4 var(--body);box-shadow:0 8px 22px rgba(0,0,0,.18);pointer-events:none}
.tip b{font-family:var(--mono);font-size:12.5px}
.tip span{color:var(--muted)}
</style>
<main>
<header>
  <h1>{{title}}</h1>
  <p class="sub">heatpump_optimizer audit programme · snapshot {{now}} UTC · schedule read from <code>plan.json</code> (roster {{source}}) · tracking issue #{{tracking}}</p>
</header>

<div class="strip">
  <div class="stat"><b>{{n_done}}</b><span>groups merged</span></div>
  <div class="stat"><b>{{n_live}}</b><span>fixers working</span></div>
  <div class="stat"><b>{{n_ready}}</b><span>ready, not started</span></div>
  <div class="stat"><b>{{n_blocked}}</b><span>waiting on a group</span></div>
  <div class="stat"><b>{{n_partial}}</b><span>part merged, residual open</span></div>
  <div class="stat"><b>{{open_iss}}</b><span>open issues (excl. #{{tracking}})</span></div>
  <div class="stat end"><b>{{end}}</b><span>projected programme close</span></div>
</div>

<section>
  <h2>Swimlanes</h2>
  <div class="scroll">{{svg}}</div>
  <div class="legend">
    <span><i style="background:var(--live-bg);border-color:var(--live)"></i>fixer working</span>
    <span><i style="background:var(--ready-bg);border-color:var(--ready)"></i>ready</span>
    <span><i style="background:var(--blocked-bg);border-color:var(--blocked)"></i>waiting</span>
    <span><i style="background:var(--partial-bg);border-color:var(--partial);border-style:dashed"></i>part merged</span>
    <span><i style="background:transparent;border-color:var(--accent);border-width:2px"></i>critical path (◆ marks each link)</span>
    <span><i style="background:transparent;border-color:var(--done);border-style:dashed"></i>planned stamp</span>
    <span><i style="background:transparent;border:0;border-top:2px solid var(--accent)"></i>groups in flight above the {{slots}}-slot cap line</span>
  </div>
  <p class="cpnote"><b>Critical path:</b> {{crit}}</p>
  <p class="note">{{slots_note}}</p>
</section>

<section>
  <h2>Groups</h2>
  <div class="filters" role="group" aria-label="Filter by status">
    <button type="button" data-f="all" aria-pressed="true">All</button>
    <button type="button" data-f="live" aria-pressed="false">Working</button>
    <button type="button" data-f="ready" aria-pressed="false">Ready</button>
    <button type="button" data-f="blocked" aria-pressed="false">Waiting</button>
    <button type="button" data-f="partial" aria-pressed="false">Part merged</button>
    <button type="button" data-f="done" aria-pressed="false">Merged</button>
    <label class="chk"><input type="checkbox" id="hide-done"> Hide merged</label>
  </div>
  <div class="scroll"><table>
    <thead><tr><th>Group</th><th>Description</th><th>Status</th><th>PR</th><th>Issues</th><th>Blocked by</th><th>ETA (UTC)</th><th>Wave</th></tr></thead>
    <tbody id="rows">{{trs}}</tbody>
  </table></div>
  <p class="note">Issue chips: bold border = this group closes it; struck through = the issue is closed. ◆ marks the critical path. Blocked-by lists the roster's <code>after</code> groups not yet done. <b>Part merged</b> means a merged pull request titled with the group delivered part of it and its brief names the residual, so the group stays open and is not counted as merged.</p>
</section>

<section>
  <h2>Waves</h2>
  <p class="note">Waves overlap. A wave is the set of groups dispatched at one moment, and the next opens as soon as one of the {{slots}} pull-request slots frees; the cap still binds, no more than {{slots}} groups in flight. A patch stamp is cut once {{every}} production groups have landed. Every row is the plan model's output.</p>
  <div class="scroll"><table>
    <thead><tr><th>wave</th><th>opens (UTC)</th><th>last merge (UTC)</th><th>groups</th><th>stamp it cuts</th></tr></thead>
    <tbody>{{waves}}</tbody>
  </table></div>
</section>

<section>
  <h2>Planned stamps</h2>
  <div class="scroll"><table>
    <thead><tr><th>Version</th><th>Projected (UTC)</th><th>Carries</th><th>Kind</th></tr></thead>
    <tbody>{{stamps}}</tbody>
  </table></div>
  <p class="note">Cadence: one patch stamp per {{every}} production groups merged, once main's Tests are green and the release notes name every merged PR. The minor stamp closes the programme.</p>
</section>

<section>
  <h2>How the ETAs are computed</h2>
  <p class="note">Every figure on this page is <code>plan.json</code>'s, written by <code>tools/plan/replan.py</code>; this renderer draws it and computes no schedule of its own. A wave is the set of groups dispatched at one moment, and the next opens as soon as one of {{slots}} pull-request slots frees, so a wave never waits for the previous one to drain; the cap limits concurrency, not the wave boundary. Duration is dispatch to merge by roster size, as the plan recorded it from <code>tools/plan/durations.json</code>: {{sizes}}. {{sizes_provenance}} A group whose fixer is already working gets {{live_pct}}% of its size duration as the remaining estimate. Those are measured lead times, not effort: review rounds and queueing are inside them, so the slot schedule is an upper bound on closure. The batching window is {{window}} minutes; its measured trade is in <code>durations.json</code>.</p>
</section>
</main>
<div id="tip" class="tip" hidden></div>
<script>
(function(){
  var tip=document.getElementById('tip');
  function move(e){
    tip.style.left=Math.min(e.clientX+14, window.innerWidth-310)+'px';
    tip.style.top=Math.max(8,e.clientY-12)+'px';
  }
  document.querySelectorAll('svg g.grp').forEach(function(g){
    g.addEventListener('mouseenter',function(e){
      var d=g.dataset, b=document.createElement('b'), s=document.createElement('span');
      b.textContent=d.name; s.textContent=d.state;
      tip.replaceChildren(b, document.createElement('br'), s, document.createElement('br'),
        'starts '+d.start, document.createElement('br'), 'ETA '+d.eta,
        document.createElement('br'), 'wave '+d.wave);
      tip.hidden=false; move(e);
    });
    g.addEventListener('mousemove',move);
    g.addEventListener('mouseleave',function(){tip.hidden=true});
  });
  var bs=document.querySelectorAll('.filters button'), rows=document.querySelectorAll('#rows tr'),
      bars=document.querySelectorAll('svg g.grp'), hide=document.getElementById('hide-done'), f='all';
  function shown(st){ return (f==='all'||st===f) && !(hide.checked && st==='done'); }
  function apply(){
    rows.forEach(function(r){ r.hidden=!shown(r.getAttribute('data-st')); });
    bars.forEach(function(b){ b.style.display=shown(b.getAttribute('data-st'))?'':'none'; });
  }
  bs.forEach(function(b){b.addEventListener('click',function(){
    bs.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
    f=b.getAttribute('data-f'); apply();
  })});
  hide.addEventListener('change',apply);
})();
</script>
"""


if __name__ == "__main__":
    sys.exit(main())
