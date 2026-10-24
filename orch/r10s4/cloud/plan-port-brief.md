Group R10-PLAN-ARTIFACT (topic r10-plan-artifact). Port the round-10 plan page into the tree so it is built only by tracked instruments. Today it is built by an out-of-tree generator (inlined below, home paths replaced by $HOME/<...>) that tvofi wants kept; a previous session never merged it. Target: extend tools/audit/seat/plan_table.py (or a small new owning module beside it, per fixer.md step 17) with an `--html` output rendering, from the roster via roster_lib and from tools/plan/replan.py's plan.json: the time-based schedule; the SVG swimlane chart with real time axis and tooltips; the slot-occupancy strip against the cap; critical-path marks; planned stamps; status classes done/live/ready/partial/blocked (blocked = an `after` target not done); "part merged" from merged `R10-X:` PR titles; the PR column per group (roster_lib.group_for_branch first, the generator's tail match as fallback - it is what maps #2529); done groups' merged PR number (merge commit then branch, sha8 fallback); issue chips struck by real issue state; the summary strip; blocked-by = roster after minus done; status filter / hide-merged / tooltip JS; the waves table; the ETA methodology text with every number filled from plan.json/durations.json. Drop: the dependency-depth table; any hard-coded count. Add a freshness refusal: the html refuses (non-zero, nothing written) when plan.json's roster blob differs from the roster ref's blob, and `replan.py --check` must test that same freshness (today it prints PLAN OK on a stale plan - fix it). No GitHub calls in --self-test (inject fixtures). Self-test arms: each status class, the stale refusal (fails on a stale fixture, passes fresh), the PR lookup fallback, the closed-issue strike. Wire the self-test (selftest_wiring.py), list it in INSTRUMENTS.md, keep tmp_paths/ref_privacy clean (no home paths in output). Also check the unverified `;` in plan_table's gantt title against mermaid 11.4.1 grammar and fix if it mis-parses. Sanity-check your generated page against the live roster and `gh pr list` the way the out-of-tree checks did (group count = roster, stages = roster, open PRs shown, no merged PR shown open). Run prepr with PREPR_SKIP_CLOSURES=1 (tvofi 2026-10-21).

----- OUT-OF-TREE gen.py (reference, verbatim except paths) -----
"""Render the round-10 plan page from plan.json. It draws; it does not plan.

    python3 tools/plan/replan.py --out ~/hpo-orch/r10s3/plan/plan.json
    python3 gen.py

Every schedule fact on the page -- each group's start, finish, wave, slot,
level; the critical path; the batches; the stamps; the closure -- is read from
`plan.json`, which `tools/plan/replan.py` writes. This file must not compute a
schedule of its own: a second computation is a second answer, and the page
then disagrees with the plan it claims to show.

What this file still reads live is display state, not schedule: the roster
(briefs, issues, resume.stage), the issue list, open pull requests and merged
pull-request titles. A roster that has moved past the plan is refused, not
papered over.
"""
import json, re, html, datetime as dt
import subprocess, sys

# The one roster reader/lookup: tools from a fresh origin/main export (HPO_TOOLS_SEAT overrides).
import os
sys.path.insert(0, os.environ.get(
    "HPO_TOOLS_SEAT",
    "$HOME/hpo-seats/r10s4/plan-artifact/main-tools/tools/audit/seat"))
import roster_lib

B = "$HOME/hpo-orch/r10s3/"
PLAN = B + "plan/plan.json"

subprocess.run(["git", "-C", "$HOME/heatpump_optimizer", "fetch", "-q",
                "origin", "handoff/audit-r10-roster"], check=True)
_rs = subprocess.run(["git", "-C", "$HOME/heatpump_optimizer", "show",
                      "FETCH_HEAD:dev/programme/rosters/wave-r10-groups.json"],
                     check=True, capture_output=True, text=True).stdout
open(B + "plan-roster.json", "w").write(_rs)
_is = subprocess.run(["gh", "issue", "list", "-R", "tvofi/heatpump_optimizer", "--state", "all",
                      "--limit", "20000", "--json", "number,title,state"],
                     check=True, capture_output=True, text=True).stdout
open(B + "plan-issues.json", "w").write(_is)
R = json.loads(_rs)
P = json.loads(open(PLAN).read())
_ISS = json.load(open(B + "plan-issues.json"))
ISS = {i["number"]: i["title"] for i in _ISS}
ISS_STATE = {i["number"]: i["state"] for i in _ISS}  # real state: OPEN / CLOSED

groups = {g["group"]: g for g in R["groups"]}
PG = P["groups"]
NOW = dt.datetime.strptime(P["generated"]["start"], "%Y-%m-%dT%H:%M:%SZ")

# The plan is the schedule; a roster that has moved since it was written is a
# stale page, refused loudly. (Done-ness moving is fine -- those groups are
# already finished on both sides.)
_open_roster = {g for g, x in groups.items()
                if (x.get("resume") or {}).get("stage") not in ("done", "rca-done")}
_open_plan = {g for g, x in PG.items() if not x.get("done")}
if _open_roster != _open_plan:
    raise SystemExit(
        f"plan.json is stale against the roster: "
        f"{sorted(_open_roster - _open_plan)} opened, "
        f"{sorted(_open_plan - _open_roster)} closed since the replan. "
        f"Run tools/plan/replan.py --out {PLAN}")

PR = {}
_open = json.loads(subprocess.run(["gh", "pr", "list", "-R", "tvofi/heatpump_optimizer", "--state", "open",
                                   "--limit", "100", "--json", "number,headRefName"],
                                  capture_output=True, text=True).stdout or "[]")
# branch -> roster group: the roster's own resume.branch names it
_branches = {(((s.get("resume") or {}).get("branch") or "")).rsplit("/", 1)[-1]: g
             for g, s in groups.items()}
def _group_of_branch(branch):
    # roster_lib's lookup first; gen.py's own tail match only as a fallback
    # (it is what catches fix/r10-ci-layout-g -> R10-CI-LAYOUT)
    _g = roster_lib.group_for_branch(R, branch)
    if _g:
        return _g
    _t = branch.rsplit("/", 1)[-1]
    return _branches.get(_t) or _branches.get(_t.replace("-pr", ""))


for _p in _open:
    _g = _group_of_branch(_p["headRefName"])
    if _g:
        PR[_g] = (PR[_g] + ", " if _g in PR else "") + f"#{_p['number']}"


def _paginated(path):
    """`gh api --paginate`: concatenated JSON arrays, decoded without a size cap."""
    _txt = subprocess.run(["gh", "api", "--paginate", path], check=True,
                          capture_output=True, text=True).stdout
    _dec, _i, _out = json.JSONDecoder(), 0, []
    while _i < len(_txt):
        if _txt[_i].isspace():
            _i += 1
            continue
        _v, _i = _dec.raw_decode(_txt, _i)
        _out.extend(_v)
    return _out


# every merged PR, no 1000 cap: closed pulls with a merged_at
_merged = [p for p in _paginated("repos/tvofi/heatpump_optimizer/pulls?state=closed&per_page=100")
           if p.get("merged_at")]
DELIVERED = {}
for _p in _merged:
    _m = re.match(r"^(R10-[A-Z0-9-]+):", _p["title"])
    if _m and _m.group(1) in groups:
        DELIVERED.setdefault(_m.group(1), []).append(_p["number"])
MERGED_BY_SHA = {p["merge_commit_sha"]: p["number"] for p in _merged if p.get("merge_commit_sha")}
MERGED_BY_GROUP = {}
for _p in sorted(_merged, key=lambda p: p["merged_at"]):
    _g = _group_of_branch(_p["head"]["ref"])
    if _g:
        MERGED_BY_GROUP[_g] = _p["number"]  # latest merge for the group


def merged_pr(g, commit):
    """The PR a done group landed through: by merge commit, else by branch; None if neither."""
    if commit and len(commit) >= 7:
        for _sha, _n in MERGED_BY_SHA.items():
            if _sha.startswith(commit) or commit.startswith(_sha[:len(commit)]):
                return _n
    return MERGED_BY_GROUP.get(g)

MERGED = {}
for g in groups:
    st = (groups[g].get("resume") or {}).get("stage")
    if st in ("done", "rca-done"):
        c = (groups[g].get("resume") or {}).get("commit")
        MERGED[g] = merged_pr(g, c) or (c or "done")[:8]
LIVE = {g: (groups[g].get("resume") or {}).get("stage")
        for g in groups if (groups[g].get("resume") or {}).get("stage") in
        ("in-progress", "in-review", "fixing", "review")}


def status(g):
    if g in MERGED:
        _m = str(MERGED[g])
        return ("done", f"merged PR #{_m}" if _m.isdigit()
                else ("folded into another group (no merge of its own)" if _m == "done"
                      else f"merged at {_m}"))
    if g in LIVE:
        _pm = sorted(DELIVERED.get(g) or [])
        _sfx = f", part merged #{', #'.join(str(n) for n in _pm)}" if _pm else ""
        if not PG[g].get("inherited") and PG[g]["start"] > P["generated"]["start"]:
            return ("live", f"{LIVE[g]}, queued for a slot{_sfx}")
        return ("live", LIVE[g] + _sfx)
    _wait = [a for a in groups[g].get("after", [])
             if a in groups and (groups[a].get("resume") or {}).get("stage") not in ("done", "rca-done")]
    _done_prs = sorted(DELIVERED.get(g) or [])
    if _wait and not _done_prs:
        return ("blocked", "waiting on " + ", ".join(a[4:] for a in _wait))
    if _done_prs:
        return ("partial", f"part merged #{', #'.join(str(n) for n in _done_prs)}, residual open"
                + (", waiting on " + ", ".join(a[4:] for a in _wait) if _wait else ""))
    return ("ready", f"ready · depth {PG[g]['level']}")


def desc(g):
    b = groups[g].get("brief", "")
    cut = re.split(r"(?<=[.])\s", b.replace("\n", " "), maxsplit=1)[0]
    return (cut[:170] + "…") if len(cut) > 170 else cut


SLOTS = P["generated"]["caps"]["slots"]
crit = set(P["critical_path"])
waves_by_group = {g: w["wave"] for w in P["waves"] for g in w["groups"]}
LANES = ("Learners", "Core model", "Product UX", "Replay", "Instruments", "Docs")

rows = []
for g in sorted(groups, key=lambda g: (not g in MERGED, PG[g]["finish"] or "", g)):
    st, sl = status(g)
    iss = groups[g].get("issues", [])
    fx = set(groups[g].get("fixes", []))
    rows.append(dict(
        g=g, lane=PG[g]["lane"], st=st, sl=sl,
        pr=(f"#{MERGED[g]}" if str(MERGED[g]).isdigit() else "merged") if g in MERGED else PR.get(g, "—"),
        iss=[(n, n in fx, ISS_STATE.get(n) != "CLOSED") for n in iss],
        blk=[a for a in groups[g].get("after", []) if a in groups and
             (groups[a].get("resume") or {}).get("stage") not in ("done", "rca-done")], d=desc(g),
        eta=None if g in MERGED else PG[g]["finish"],
        crit=g in crit,
        s=None if g in MERGED else NOW,
        wave=None if g in MERGED else PG[g]["wave"],
        start=dt.datetime.strptime(PG[g]["start"], "%Y-%m-%dT%H:%M:%SZ") if PG[g]["start"] else None,
        f=dt.datetime.strptime(PG[g]["finish"], "%Y-%m-%dT%H:%M:%SZ") if PG[g]["finish"] else None))

# ------------------------------------------------------------------ swimlanes
open_rows = [r for r in rows if r["st"] != "done"]
end = dt.datetime.strptime(P["summary"]["closure"], "%Y-%m-%dT%H:%M:%SZ")
span_h = max(1.0, (end - NOW).total_seconds() / 3600)
W, LW, RH = 1180, 120, 24
px = lambda t: LW + (t - NOW).total_seconds() / 3600 / span_h * (W - LW - 20)
lane_rows = {l: [] for l in LANES}
for r in open_rows:
    rows_l = lane_rows[r["lane"]]
    for track in rows_l:
        if all(r["start"] >= o["f"] or r["f"] <= o["start"] for o in track):
            track.append(r)
            break
    else:
        rows_l.append([r])
y, parts, ypos = 34 + 52 + 6, [], {}
# Occupancy strip: how many groups run at each hour, against the slot cap. The
# line rides the cap instead of fanning out; that is the constraint made
# visible. It is computed from the plan's own start/finish, not re-scheduled.
_occ = []
for _t in range(0, int(span_h) + 1):
    _tt = NOW + dt.timedelta(hours=_t)
    _occ.append((_tt, sum(1 for r in open_rows if r["start"] <= _tt < r["f"])))
_maxc = max([SLOTS] + [c for _, c in _occ])
_oy = lambda c: 34 + 52 - (c / _maxc) * 46
parts.append('<polyline points="' + " ".join(f"{px(t):.1f},{_oy(c):.1f}" for t, c in _occ) +
             '" class="occ"/>')
parts.append(f'<line x1="{LW}" y1="{_oy(SLOTS):.1f}" x2="{W-20}" y2="{_oy(SLOTS):.1f}" class="slotcap"/>')
parts.append(f'<text x="10" y="46" class="lanelab">slots</text>'
             f'<text x="10" y="62" class="tick">cap {SLOTS}</text>')
for t in range(0, int(span_h) + 1, 12):
    x = px(NOW + dt.timedelta(hours=t))
    lab = (NOW + dt.timedelta(hours=t)).strftime("%a %Hh")
    parts.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x:.1f}" y2="__H__" class="grid"/>'
                 f'<text x="{x:.1f}" y="14" class="tick">{lab}</text>')
lane_idx = {}
for li, l in enumerate(LANES):
    lane_idx[l] = li
    tracks = lane_rows[l] or [[]]
    h = len(tracks) * (RH + 6) + 10
    parts.append(f'<rect x="0" y="{y}" width="{W}" height="{h}" class="lane"/>'
                 f'<text x="10" y="{y+18}" class="lanelab">{l}</text>')
    for i, track in enumerate(tracks):
        for r in track:
            x0, x1 = px(r["start"]), px(r["f"])
            yy = y + 6 + i * (RH + 6)
            ypos[r["g"]] = (x0, x1, yy + RH / 2)
            cls = "bar " + r["st"] + (" crit" if r["crit"] else "")
            name = r["g"][4:]
            _w = max(x1 - x0, 4)
            # labels stay inside their bar: truncate to fit, and draw none when
            # even four characters will not fit -- text outside a box reads as
            # naming the next bar along
            _room = int((_w - (18 if r["crit"] else 8)) / 6.2)
            _txt = name if _room >= len(name) else (name[:_room - 1] + "…" if _room >= 4 else "")
            parts.append(f'<g class="grp" data-st="{r["st"]}" data-name="{r["g"][4:]}" '
                         f'data-state="{html.escape(r["sl"])}" '
                         f'data-start="{r["start"].strftime("%a %d %b %H:%M")}" '
                         f'data-eta="{r["eta"]}" data-wave="{r["wave"]}">'
                         f'<title>{r["g"]}: {html.escape(r["sl"])}, starts '
                         f'{r["start"].strftime("%a %d %b %H:%M")}, ETA {r["eta"]}, wave '
                         f'{r["wave"]}</title>')
            if _w < 16:  # too narrow to point at: widen the hover target without moving the bar
                parts.append(f'<rect x="{x0 - 3:.1f}" y="{yy}" width="{_w + 8:.1f}" '
                             f'height="{RH}" fill="transparent"/>')
            parts.append(f'<rect x="{x0:.1f}" y="{yy}" width="{_w:.1f}" height="{RH}" rx="3" '
                         f'class="{cls}"/>')
            if r["crit"]:
                # the chain's mark: it carries the reading where a connector
                # would have to cross lanes and hours to get there
                parts.append(f'<text x="{x0 + 3:.1f}" y="{yy + 16}" class="critmark">◆</text>')
            if _txt:
                parts.append(f'<text x="{x0 + 13:.1f}" y="{yy+16}" class="barlab">'
                             f'{html.escape(_txt)}</text>')
            parts.append('</g>')
    y += h + 4
# Critical path connectors: consecutive links of the chain only, and only where
# the link is legible -- same lane or the next one, and no more than two hours
# apart. One dashed line per pair at most. A link that would cross the chart
# is not drawn; the ◆ on each bar and the caption carry the chain instead.
arrows, skipped = [], 0
_chain = list(P["critical_path"])
for _prev, _next in zip(_chain, _chain[1:]):
    if _prev not in ypos or _next not in ypos:
        skipped += 1
        continue
    _lp, _ln = lane_idx[PG[_prev]["lane"]], lane_idx[PG[_next]["lane"]]
    _gap = abs((dt.datetime.strptime(PG[_next]["start"], "%Y-%m-%dT%H:%M:%SZ") -
                dt.datetime.strptime(PG[_prev]["finish"], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()) / 3600
    if abs(_lp - _ln) > 1 or _gap > 2:
        skipped += 1
        continue
    ax, ay = ypos[_prev][1], ypos[_prev][2]
    bx, by = ypos[_next][0], ypos[_next][2]
    if abs(bx - ax) < 2 and abs(by - ay) < 2:
        skipped += 1  # back-to-back: the two bars already touch
        continue
    arrows.append(f'<path d="M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}" class="critline"/>')
for name in P["stamps"]:
    t = dt.datetime.strptime(name["at"], "%Y-%m-%dT%H:%M:%SZ")
    x = px(t)
    if x <= W - 10:
        parts.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{y}" class="stampline"/>'
                     f'<text x="{x+3:.1f}" y="{y+14}" class="stamplab">{name["version"]}</text>')
svg = (f'<svg viewBox="0 0 {W} {y+22}" width="{W}" role="img" aria-label="Swimlanes">' +
       "".join(parts).replace("__H__", str(y)) + "".join(arrows) + "</svg>")


def chip(n, closer, open_):
    t = html.escape(ISS.get(n, ""))
    c = "chip" + (" closer" if closer else "") + ("" if open_ else " closed")
    return f'<span class="{c}" title="{t}">#{n}</span>'


trs = []
for r in rows:
    trs.append(
        f'<tr class="{r["st"]}" data-st="{r["st"]}"><td class="g">'
        f'{"<span class=\"cp\" title=\"critical path\">◆</span>" if r["crit"] else ""}'
        f'{r["g"][4:]}<div class="lanec">{r["lane"]}</div></td>'
        f'<td class="d">{html.escape(r["d"])}</td>'
        f'<td><span class="pill {r["st"]}">{html.escape(r["sl"])}</span></td>'
        f'<td class="mono">{r["pr"]}</td>'
        f'<td>{"".join(chip(*i) for i in r["iss"]) or "—"}</td>'
        f'<td class="blk">{", ".join(b[4:] for b in r["blk"]) or "—"}</td>'
        f'<td class="mono">{r["eta"] or "—"}</td>'
        f'<td class="mono">{r["wave"] or "—"}</td></tr>')
stamp_rows = "".join(
    f'<tr><td class="mono">{s["version"]}</td>'
    f'<td class="mono">{dt.datetime.strptime(s["at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%a %d %b %H:%M")}</td>'
    f'<td>{html.escape(", ".join(c[4:] for c in s["carries"]) or "—")}</td>'
    f'<td class="mono">{s["kind"]}</td></tr>' for s in P["stamps"])
counts = {k: sum(1 for r in rows if r["st"] == k)
          for k in ("done", "live", "ready", "partial", "blocked")}
open_iss = len([n for n, s_ in ISS_STATE.items() if s_ == "OPEN" and n != 201])
# The caption carries the chain in order with each link's wave, so the reading
# never depends on a line surviving a lane or hour gap.
crit_caption = " → ".join(
    f'{g[4:]} <span class="cpw">w{waves_by_group.get(g, "—")}</span>' for g in _chain)
_dur = json.load(open(os.path.join(os.path.dirname(roster_lib.__file__), "..", "..", "plan", "durations.json")))
_DUR_SIZES = ", ".join(f"{k} {v:g} h" for k, v in sorted(_dur["sizes_hours"].items(), key=lambda kv: ["S", "M", "L", "XL"].index(kv[0])))
_LIVE_PCT = f"{_dur['live_remaining_fraction'] * 100:.0f}"
data = dict(
    svg=svg, trs="".join(trs), stamps=stamp_rows,
    end=end.strftime("%a %d %b %H:%M"),
    crit=crit_caption,
    counts=counts, total=len(rows), open_iss=open_iss,
    now=NOW.strftime("%d %b %H:%M"),
    slots_note=(
        f"Read from plan.json: {P['summary']['groups_open']} open groups, "
        f"{P['summary']['batches']} merge batches, closure {P['summary']['closure']}. "
        f"A wave is the set of groups dispatched at one instant; the next opens as soon as "
        f"one of the {SLOTS} pull-request slots frees. Coordinator cap "
        f"{P['generated']['caps']['coordinator_cap']}; "
        f"{len((P['generated'].get('inherited_coordinator') or {}).get('groups') or [])} inherited "
        f"in-progress coordinator groups are recorded in plan.json. The line above the lanes is "
        f"how many groups are in flight at each hour, riding the cap. Stamps: one patch per "
        f"{P['generated']['caps']['stamp_every']} production groups, the minor at closure. "
        f"Hover any bar, however narrow, for its name, state, start, ETA and wave. "
        f"{skipped} of {max(0, len(_chain) - 1)} critical-path links are drawn; the ◆ and the "
        f"caption carry the rest."),
    slots=SLOTS, dur_sizes=_DUR_SIZES, live_pct=_LIVE_PCT)
tpl = open(B + "plan/tpl.html").read()
for k, v in data.items():
    tpl = tpl.replace("{{" + k + "}}", str(v) if not isinstance(v, dict) else "")
for k, v in counts.items():
    tpl = tpl.replace("{{n_" + k + "}}", str(v))
# Waves, as the model emits them.
_wrow = ""
for w in P["waves"]:
    _names = ", ".join(g[4:] for g in w["groups"]) or "—"
    _wrow += (f'<tr><td class="mono">{w["wave"]}</td>'
              f'<td class="mono">{dt.datetime.strptime(w["opens"], "%Y-%m-%dT%H:%M:%SZ").strftime("%a %d %b %H:%M")}</td>'
              f'<td class="mono">{dt.datetime.strptime(w["drains"], "%Y-%m-%dT%H:%M:%SZ").strftime("%a %d %b %H:%M")}</td>'
              f'<td>{html.escape(_names)}</td>'
              f'<td class="mono">{html.escape(w["stamp"] or "—")}</td></tr>')
_disp = ('<section><h2>Waves</h2><p>Waves overlap. A wave is the set of groups dispatched at one '
         f'moment, and the next opens as soon as one of the {SLOTS} pull-request slots frees. '
         f'The cap still binds: no more than {SLOTS} groups in flight. A patch stamp is cut once '
         f'{P["generated"]["caps"]["stamp_every"]} production groups have landed. '
         'Every row below is the plan model\'s output.'
         '</p><table><thead><tr><th>wave</th><th>opens (UTC)</th><th>last merge (UTC)</th>'
         '<th>groups</th><th>stamp it cuts</th></tr></thead><tbody>' + _wrow + '</tbody></table></section>')
tpl = tpl.replace("</main>", _disp + "</main>")
open(B + "plan/round-10-plan.html", "w").write(tpl)
print(data["end"], "|", crit_caption.replace('<span class="cpw">', "(").replace("</span>", ")"),
      "|", counts, "| arrows drawn", len(arrows), "of", max(0, len(_chain) - 1))

----- OUT-OF-TREE tpl.html -----
<meta charset="utf-8">
<title>Round 10 Fix Plan</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a control-room board — summary strip, swimlane chart, then the full group ledger. */
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
body{background:var(--bg);color:var(--fg);font:15px/1.45 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:20px 40px}
main{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:22px}
h1{font:700 2.1rem/1 var(--display);letter-spacing:.01em;margin:0;text-wrap:balance}
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
.waveline{stroke:var(--line);stroke-width:1;stroke-dasharray:6 4}
.wavelab{fill:var(--muted);font-size:9px}
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
td.d{min-width:260px;max-width:440px;color:var(--fg)}
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
.tw{display:inline-block;margin:0 4px 4px 0;padding:0 6px;border-radius:4px;font:.78rem var(--mono);border:1px solid var(--line);color:var(--muted)}
.tw.live{color:var(--live);border-color:var(--live)}
.tw.ready{color:var(--ready);border-color:var(--ready)}
.tw.partial{color:var(--partial);border-color:var(--partial);border-style:dashed}
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
  <h1>Round 10 Fix Plan</h1>
  <p class="sub">heatpump_optimizer audit programme · snapshot {{now}} UTC · schedule read from <code>plan.json</code> · tracking issue #201</p>
</header>

<div class="strip">
  <div class="stat"><b>{{n_done}}</b><span>groups merged</span></div>
  <div class="stat"><b>{{n_live}}</b><span>fixers working</span></div>
  <div class="stat"><b>{{n_ready}}</b><span>ready, not started</span></div>
  <div class="stat"><b>{{n_blocked}}</b><span>waiting on a group</span></div>
  <div class="stat"><b>{{n_partial}}</b><span>part merged, residual open</span></div>
  <div class="stat"><b>{{open_iss}}</b><span>open issues (excl. #201)</span></div>
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
    <button type="button" id="f-all" data-f="all" aria-pressed="true">All</button>
    <button type="button" id="f-live" data-f="live" aria-pressed="false">Working</button>
    <button type="button" id="f-ready" data-f="ready" aria-pressed="false">Ready</button>
    <button type="button" id="f-blocked" data-f="blocked" aria-pressed="false">Waiting</button>
    <button type="button" id="f-partial" data-f="partial" aria-pressed="false">Part merged</button>
    <button type="button" id="f-done" data-f="done" aria-pressed="false">Merged</button>
    <label class="chk"><input type="checkbox" id="hide-done"> Hide merged</label>
  </div>
  <div class="scroll">
  <table>
    <thead><tr><th>Group</th><th>Description</th><th>Status</th><th>PR</th><th>Issues</th><th>Blocked by</th><th>ETA (UTC)</th><th>Wave</th></tr></thead>
    <tbody id="rows">{{trs}}</tbody>
  </table>
  </div>
  <p class="note">Issue chips: bold border = this group closes it; struck through = already closed. ◆ marks the critical path. Blocked-by lists only unmerged groups on the replanned graph. <b>Part merged</b> means a merged pull request delivered part of the group and its own brief names the residual, so the group stays open and is not counted as merged.</p>
</section>

<section>
  <h2>Planned stamps</h2>
  <div class="scroll"><table>
    <thead><tr><th>Version</th><th>Projected (UTC)</th><th>Carries</th><th>Kind</th></tr></thead>
    <tbody>{{stamps}}</tbody>
  </table></div>
  <p class="note">Cadence: one patch stamp per ~5 production groups merged, once main's Tests are green and the release notes name every merged PR. The minor stamp closes the programme.</p>
</section>

<section>
  <h2>How the ETAs are computed</h2>
  <p class="note">Every figure on this page is <code>plan.json</code>'s, written by <code>tools/plan/replan.py</code>; this renderer draws it and computes no schedule of its own. A wave is the set of groups dispatched at one moment, and the next opens as soon as one of {{slots}} pull-request slots frees, so a wave never waits for the previous one to drain; the cap limits concurrency, not the wave boundary. Duration is dispatch to merge by roster size, from <code>tools/plan/durations.json</code>: {{dur_sizes}}, the median lead time of done round-10 groups of that size (S is above M because small groups waited in review; XL has no merged sample and is 1.5 × L). A group whose fixer is already working gets {{live_pct}}% of its size duration as the remaining estimate. Those are measured lead times, not effort: review rounds and queueing are inside them, so the slot schedule is an upper bound on closure. The batching window is 0 minutes — merge as soon as a batch is ready — because closure is the first objective; the measured trade is in <code>durations.json</code>.</p>
</section>
</main>
<div id="tip" class="tip" hidden></div>
<script>
(function(){
  var tip=document.getElementById('tip');
  function move(e){
    var x=Math.min(e.clientX+14, window.innerWidth-310), y=Math.max(8,e.clientY-12);
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  document.querySelectorAll('svg g.grp').forEach(function(g){
    g.addEventListener('mouseenter',function(e){
      var d=g.dataset;
      tip.innerHTML='<b>'+d.name+'</b><br><span>'+d.state+'</span><br>starts '+d.start+
                    '<br>ETA '+d.eta+'<br>wave '+d.wave;
      tip.hidden=false; move(e);
    });
    g.addEventListener('mousemove',move);
    g.addEventListener('mouseleave',function(){tip.hidden=true});
  });
})();
</script>
<script>
(function(){
  var bs=document.querySelectorAll('.filters button'), rows=document.querySelectorAll('#rows tr'),
      hide=document.getElementById('hide-done'), f='all';
  var bars=document.querySelectorAll('svg g.grp');
  function apply(){
    rows.forEach(function(r){
      var isDone=r.getAttribute('data-st')==='done';
      var okF=(f==='all'||r.getAttribute('data-st')===f);
      r.hidden=!(okF && !(hide.checked && isDone));
    });
    bars.forEach(function(b){
      var st=b.getAttribute('data-st');
      var okF=(f==='all'||st===f);
      b.style.display=(okF && !(hide.checked && st==='done'))?'':'none';
    });
  }
  bs.forEach(function(b){b.addEventListener('click',function(){
    bs.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
    f=b.getAttribute('data-f'); apply();
  })});
  hide.addEventListener('change',apply);
})();
</script>
