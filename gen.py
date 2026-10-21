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
