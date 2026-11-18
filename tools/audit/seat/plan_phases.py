#!/usr/bin/env python3
"""A round's phases: the linted input file and the plan page's phases section.

    python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json
    python3 tools/audit/seat/plan_phases.py --phases FILE --html page.html

The plan page draws a round's fix groups from the roster and plan.json, which
exist only from the round's fifth phase. The phases file is where everything
before and around them is recorded: one entry per phase of the playbook
(`dev/audit/README.md`, "Running a round: the playbook" and "Round start"), in
the order of `PHASES`. `plan_page.py` imports `section` and draws it above the
group lanes; `--html` draws the section alone as a page, for a round with no
plan yet.

The file (JSON):

    {"round": 11, "as_of": ISO, "note": str?,
     "phases": [{"phase": one of PHASES, "status": one of STATUSES,
                 "waiting_on": str (iff status waiting),
                 "started": ISO?, "finished": ISO?,
                 "forecast": {"start_from": ISO, "start_to": ISO, "basis": str}?,
                 "entry": str?, "exit": str?,
                 "items": [{"name": str, "status": one of STATUSES,
                            "waiting_on": str?, "detail": str?}]?}]}

REFUSALS (`violations`; `--check` exits 1): a status outside `STATUSES`; a
phase outside `PHASES`, repeated, or out of the playbook's order; `waiting`
with no `waiting_on`; a date that is not ISO-8601 UTC; a `started` or
`finished` date on a not-started phase; a `finished` date on a phase not done;
a forecast with no `basis` (a date with no plan behind it); a text field
(`note`, a phase's `waiting_on`, `entry`, `exit`, an item's `name`, `waiting_on`,
`detail`, a forecast's `basis`) that is not a string, and `items` that is not a
list: a file `--check` accepts is a file `section` draws. A phase the file
does not list is drawn "not started" with dashes, never omitted; the page
prints no date or count the file does not carry. An invalid file is drawn as
PHASES UNAVAILABLE with its first violation: the rest of the plan page stands.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import tempfile
from pathlib import Path

# The playbook's order (dev/audit/README.md): round start holds the pickup,
# the start evaluation and the finder-critical groups; fix waves are the
# roster's group lanes (playbook phases 5 to 10).
PHASES = (
    ("round-start", "Round start"),
    ("finders", "Finders"),
    ("verify-judge", "Verify, judge"),
    ("plan", "Architect plan"),
    ("fix-waves", "Fix waves"),
    ("stamps", "Stamps"),
    ("closure", "Closure"),
)
STATUSES = {"not-started": "not started", "running": "running",
            "waiting": "waiting", "done": "done"}
# The plan page's pill classes, so a phase reads in the page's own language.
_PILL = {"not-started": "held", "running": "live", "waiting": "blocked", "done": "done"}
_ISO = "%Y-%m-%dT%H:%M:%SZ"
_FILE = re.compile(r"\Around(\d+)\Z")


def _t(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, _ISO)


def _date_ok(v) -> bool:
    try:
        _t(v)
        return True
    except (TypeError, ValueError):
        return False


# The text the section prints, by the object holding it (an item's name is
# checked with its presence, a forecast's basis with its own). Every value is a
# string when present: `section` escapes each, and an escape of a number or a
# list is a crash on the plan page, not a refusal in the file.
_TEXT_DOC = ("note",)
_TEXT_PHASE = ("waiting_on", "entry", "exit")
_TEXT_ITEM = ("waiting_on", "detail")


def _text_violations(where: str, x: dict, keys: tuple) -> list:
    return [f"{where}: {k} not text ({x[k]!r})"
            for k in keys if x.get(k) is not None and not isinstance(x[k], str)]


def violations(doc) -> list:
    """Every refusal the file earns, in reading order; empty when it is sound."""
    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]
    bad = _text_violations("file", doc, _TEXT_DOC)
    if not isinstance(doc.get("round"), int):
        bad.append("round: not an integer")
    if not _date_ok(doc.get("as_of")):
        bad.append(f"as_of: not ISO-8601 UTC ({doc.get('as_of')!r})")
    order = [p for p, _ in PHASES]
    last = -1
    phases = doc.get("phases")
    if not isinstance(phases, list):
        return bad + ["phases: not a list"]
    for i, ph in enumerate(phases):
        pid = ph.get("phase") if isinstance(ph, dict) else None
        where = f"phases[{i}] {pid}"
        if pid not in order:
            bad.append(f"{where}: unknown phase (one of {', '.join(order)})")
            continue
        if order.index(pid) <= last:
            bad.append(f"{where}: out of the playbook's order, or repeated")
        last = max(last, order.index(pid))
        bad += _status_violations(where, ph) + _text_violations(where, ph, _TEXT_PHASE)
        st = ph.get("status")
        for k in ("started", "finished"):
            if ph.get(k) is not None and not _date_ok(ph[k]):
                bad.append(f"{where}: {k} not ISO-8601 UTC ({ph[k]!r})")
        if st == "not-started" and (ph.get("started") or ph.get("finished")):
            bad.append(f"{where}: a date on a not-started phase (put a plan's date in forecast, with its basis)")
        if ph.get("finished") and st != "done":
            bad.append(f"{where}: finished on a phase not done")
        fc = ph.get("forecast")
        if fc is not None:
            if not (isinstance(fc, dict) and isinstance(fc.get("basis"), str) and fc["basis"].strip()):
                bad.append(f"{where}: a forecast with no basis (a date with no plan behind it)")
            elif not (_date_ok(fc.get("start_from")) and _date_ok(fc.get("start_to"))):
                bad.append(f"{where}: forecast start_from/start_to not ISO-8601 UTC")
        items = ph.get("items")
        if items is not None and not isinstance(items, list):
            bad.append(f"{where}: items not a list")
            items = []
        for j, it in enumerate(items or []):
            if not (isinstance(it, dict) and isinstance(it.get("name"), str) and it["name"].strip()):
                bad.append(f"{where} items[{j}]: no name (text)")
                continue
            iw = f"{where} item {it['name']}"
            bad += _status_violations(iw, it) + _text_violations(iw, it, _TEXT_ITEM)
    return bad


def _status_violations(where: str, x: dict) -> list:
    st = x.get("status")
    if not isinstance(st, str) or st not in STATUSES:
        return [f"{where}: unknown status {st!r} (one of {', '.join(STATUSES)})"]
    wo = x.get("waiting_on")
    if st == "waiting" and not (isinstance(wo, str) and wo.strip()):
        return [f"{where}: waiting on nothing named (waiting_on)"]
    return []


def load(path: str | Path):
    """(doc, violations) for a phases file; a file that does not parse is one violation."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, [f"{Path(path).name}: {type(exc).__name__}: {exc}"]
    return doc, violations(doc)


def discover(repo: str | Path) -> Path | None:
    """The running round's phases file in a checkout: the highest-numbered
    `dev/programme/round<N>/phases.json`, or None."""
    found = []
    for p in (Path(repo) / "dev" / "programme").glob("round*/phases.json"):
        m = _FILE.match(p.parent.name)
        if m:
            found.append((int(m.group(1)), p))
    return max(found)[1] if found else None


# ------------------------------------------------------------------ drawing

def _pill(st: str, label: str) -> str:
    return f'<span class="pill {_PILL[st]}">{html.escape(label)}</span>'


def _label(x: dict) -> str:
    st = x["status"]
    return f"waiting on {x['waiting_on']}" if st == "waiting" else STATUSES[st]


def _when(s: str | None) -> str:
    return _t(s).strftime("%a %d %b %H:%M") if s else "—"


def rows_of(doc: dict) -> list:
    """Every phase of the playbook, in its order: the file's entry, or a
    not-started placeholder carrying nothing."""
    given = {p["phase"]: p for p in doc.get("phases") or []}
    return [dict(given.get(pid) or {"phase": pid, "status": "not-started"}, title=title)
            for pid, title in PHASES]


def timeline(doc: dict, rows: list, axis: tuple | None = None) -> str:
    """The phases on a time axis. `axis` is the plan page's own `(start, end)`:
    the swimlanes' geometry, scale and ticks, so a phase lines up with the
    group lanes under it, and a phase reaching past either end is cut there
    and says so. With no axis, the file's own: its earliest date to its
    latest. A running bar ends at `as_of`, a forecast is a dashed window, a
    phase with no date says so in its row."""
    now = _t(doc["as_of"])
    if axis:
        t0, t1 = axis
        span = max(3600.0, (t1 - t0).total_seconds())
        W, LW, step = 1180, 120, 12
    else:
        pts = [now]
        for r in rows:
            pts += [_t(r[k]) for k in ("started", "finished") if r.get(k)]
            fc = r.get("forecast")
            if fc:
                pts += [_t(fc["start_from"]), _t(fc["start_to"])]
        t0, t1 = min(pts), max(pts)
        span = max(3600.0, (t1 - t0).total_seconds()) * 1.04
        W, LW = 1180, 230
        step = 6 if span <= 3 * 86400 else 24
    t_end = t0 + dt.timedelta(seconds=span)
    RH = 26

    def px(t):
        return LW + (min(max(t, t0), t_end) - t0).total_seconds() / span * (W - LW - 20)

    e, parts = html.escape, []
    H = 22 + len(rows) * (RH + 6) + 6
    h0 = t0 if axis else t0.replace(minute=0, second=0)
    for k in range(0, int(span // 3600) + 2, step):
        t = h0 + dt.timedelta(hours=k)
        if t0 <= t <= t_end:
            parts.append(f'<line x1="{px(t):.1f}" y1="20" x2="{px(t):.1f}" y2="{H}" class="grid"/>'
                         f'<text x="{px(t):.1f}" y="14" class="tick">{t.strftime("%a %Hh")}</text>')

    def note(y, text):
        parts.append(f'<text x="{LW + 4}" y="{y + 17}" class="tick">{e(text)}</text>')
    for i, r in enumerate(rows):
        y = 22 + i * (RH + 6)
        parts.append(f'<text x="10" y="{y + 17}" class="lanelab">{e(r["title"])}</text>')
        cls = _PILL[r["status"]]
        tip = f'{r["title"]}: {_label(r)}'
        if r.get("started"):
            a = _t(r["started"])
            b = _t(r["finished"]) if r.get("finished") else now
            if b < t0 or a > t_end:
                note(y, f'{_label(r)}, {_when(r["started"])} to '
                     f'{_when(r["finished"]) if r.get("finished") else "now"}, off this axis')
            else:
                w = max(px(b) - px(a), 4)
                parts.append(f'<g class="phase"><title>{e(tip)}, started {_when(r["started"])}'
                             f'{", finished " + _when(r["finished"]) if r.get("finished") else ", open"}</title>'
                             f'<rect x="{px(a):.1f}" y="{y}" width="{w:.1f}" height="{RH}" rx="3" '
                             f'class="bar {cls}{"" if r.get("finished") else " open"}"/>'
                             + (f'<text x="{px(a) + 4:.1f}" y="{y + 17}" class="barlab">◂ since '
                                f'{_when(r["started"])}</text>' if a < t0 else "") + "</g>")
        fc = r.get("forecast")
        if fc:
            a, b = _t(fc["start_from"]), _t(fc["start_to"])
            if a > t_end:
                note(y, f'forecast start {_when(fc["start_from"])} to {_when(fc["start_to"])}, past this axis')
            else:
                parts.append(f'<g class="phase"><title>{e(r["title"])}: forecast start '
                             f'{_when(fc["start_from"])} to {_when(fc["start_to"])} ({e(fc["basis"])})</title>'
                             f'<rect x="{px(a):.1f}" y="{y}" width="{max(px(b) - px(a), 4):.1f}" '
                             f'height="{RH}" rx="3" class="bar forecast"/>'
                             f'<text x="{px(a) - 6:.1f}" y="{y + 17}" class="barlab" text-anchor="end">forecast start</text></g>')
        if not r.get("started") and not fc:
            note(y, f"{_label(r)} — no date")
    if t0 <= now <= t_end:
        parts.append(f'<line x1="{px(now):.1f}" y1="20" x2="{px(now):.1f}" y2="{H}" class="nowline"/>'
                     f'<text x="{px(now) + 3:.1f}" y="{H - 2}" class="tick">as of</text>')
    return (f'<svg viewBox="0 0 {W} {H + 4}" width="{W}" height="{H + 4}" role="img" '
            f'aria-label="round phases">{"".join(parts)}</svg>')


_CSS = """<style>
.bar.done{fill:var(--done-bg);stroke:var(--done)}
.bar.open{stroke-dasharray:6 2}
.bar.forecast{fill:transparent;stroke:var(--muted);stroke-dasharray:3 3}
.nowline{stroke:var(--accent);stroke-width:1.4}
ul.items{margin:0;padding-left:1.1em;font-size:.86rem;columns:2 26rem;column-gap:28px}
ul.items li{margin:2px 0;break-inside:avoid}
</style>"""


#: The phases whose duration the plan's model prices: `phase_hours`, keyed by
#: these ids, which `replan.build_plan` copies from `durations.json` into
#: `generated.model` (`replan.MODEL_FIELDS`) and `plan_page.render` hands to
#: `section`. One the model has no figure for is printed "duration
#: unmeasured", never a typed constant or a zero.
MODEL_TIMED = ("finders", "verify-judge", "plan")


def _model_duration(r: dict, phase_hours: dict | None) -> str:
    """The Planned cell of a phase with no forecast: the model's duration for a
    phase it prices (not done), "duration unmeasured" where it has none, a dash
    for every other phase."""
    if r["status"] == "done" or r["phase"] not in MODEL_TIMED:
        return "—"
    h = (phase_hours or {}).get(r["phase"])
    if isinstance(h, bool) or not isinstance(h, (int, float)) or h <= 0:
        return "duration unmeasured"
    return f"{h:g} h (plan model)"


def section(doc, bad: list | None = None, where: str = "", axis: tuple | None = None,
            phase_hours: dict | None = None) -> str:
    """The phases section for the plan page: a timeline and one row per phase,
    the running phases' items under them. `bad` (from `violations`) draws the
    UNAVAILABLE section instead, naming the first refusal. `axis` is the plan
    page's `(start, end)`: given, the timeline is drawn on it (`timeline`),
    and the fix-waves row points at the group lanes, which are that phase."""
    e = html.escape
    if bad:
        return (f'<section>\n  <h2>Round phases</h2>\n  <p><b>PHASES UNAVAILABLE — '
                f'{len(bad)} violation(s) in {e(where)}: {e(bad[0])}</b></p>\n</section>\n')
    rows = rows_of(doc)
    trs = []
    for r in rows:
        fc = r.get("forecast")
        planned = (f'start {_when(fc["start_from"])} to {_when(fc["start_to"])}'
                   f'<div class="lanec">{e(fc["basis"])}</div>' if fc else _model_duration(r, phase_hours))
        items = ""
        if r.get("items") and r["status"] != "done":
            items = '<tr class="items"><td></td><td colspan="6"><ul class="items">' + "".join(
                f'<li>{_pill(it["status"], _label(it))} <b>{e(it["name"])}</b>'
                + (f' — {e(it["detail"])}' if it.get("detail") else "") + "</li>"
                for it in r["items"]) + "</ul></td></tr>"
        trs.append(
            f'<tr data-phase="{e(r["phase"])}" data-st="{e(r["status"])}"><td class="g">{e(r["title"])}</td>'
            f'<td class="st">{_pill(r["status"], _label(r))}</td>'
            f'<td class="mono">{_when(r.get("started"))}</td><td class="mono">{_when(r.get("finished"))}</td>'
            f'<td>{planned}</td><td class="d">{e(r.get("entry") or "—")}</td>'
            f'<td class="d">{e(r.get("exit") or "—")}</td></tr>{items}')
    note = f'<p class="note"><b>{e(doc["note"])}</b></p>' if doc.get("note") else ""
    return (f'{_CSS}\n<section id="phases">\n  <h2>Round {doc["round"]} phases</h2>\n  {note}\n'
            f'  <p class="note">State as of {_when(doc["as_of"])} UTC, read from the round\'s phases file '
            f'({e(where)}); the phases are the playbook\'s, in its order (<code>dev/audit/README.md</code>). '
            'A phase the file does not list is drawn not started. A dash is a date the file does not '
            'carry, never a guess; a dashed outline is a forecast window with its basis.'
            + (' The fix waves are the group lanes below, on the same time axis; the stamps are the '
               'planned-stamps table.' if axis else '') + '</p>\n'
            f'  <div class="scroll">{timeline(doc, rows, axis)}</div>\n'
            '  <div class="scroll"><table><thead><tr><th>Phase</th><th>Status</th>'
            '<th>Started (UTC)</th><th>Finished (UTC)</th><th>Planned</th><th>Entry</th><th>Exit</th>'
            f'</tr></thead><tbody>{"".join(trs)}</tbody></table></div>\n</section>\n')


def shown(path: str | Path, repo: str | Path) -> str:
    """How the page names the file: relative to the checkout, else its bare
    name -- a host path never reaches a public page (`plan_public.py`)."""
    p = Path(path).resolve()
    try:
        return p.relative_to(Path(repo).resolve()).as_posix()
    except ValueError:
        return p.name


# ---------------------------------------------------------------- self-test

def fixture() -> dict:
    """A round with each status on a phase and on an item, a forecast with
    its basis, and two phases (fix waves, closure) the file does not list."""
    return {"round": 9, "as_of": "2026-01-05T12:00:00Z", "phases": [
        {"phase": "round-start", "status": "done", "started": "2026-01-01T00:00:00Z",
         "finished": "2026-01-02T00:00:00Z", "entry": "ENTRY-RS", "exit": "EXIT-RS",
         "items": [{"name": "ITEM-HIDDEN", "status": "done"}]},
        {"phase": "finders", "status": "running", "started": "2026-01-02T00:00:00Z",
         "items": [{"name": "ITEM-DONE", "status": "done"},
                   {"name": "ITEM-RUN", "status": "running", "detail": "DETAIL-RUN"},
                   {"name": "ITEM-WAIT", "status": "waiting", "waiting_on": "QUEUE-X"},
                   {"name": "ITEM-NOT", "status": "not-started"}]},
        {"phase": "verify-judge", "status": "waiting", "waiting_on": "THE-JUDGE"},
        {"phase": "plan", "status": "not-started",
         "forecast": {"start_from": "2026-01-06T08:00:00Z", "start_to": "2026-01-06T20:00:00Z",
                      "basis": "BASIS-PLAN"}},
        {"phase": "stamps", "status": "not-started"}]}


def fixture_checks(check) -> None:
    """The phases arms of plan_page.py's self-test, which runs them: each
    refusal against the fixture it refuses, and the drawing;
    `check(name, ok, got)`."""
    import copy
    doc = fixture()
    check("phases: the fixture is sound (null control)", violations(doc) == [], violations(doc))

    def refuses(mutate, why):
        d = copy.deepcopy(doc)
        mutate(d)
        got = violations(d)
        check(f"phases: refused, {why}", any(why in b for b in got), got)
    ph = lambda d, i: d["phases"][i]  # noqa: E731
    refuses(lambda d: ph(d, 1).update(status="started"), "unknown status")
    refuses(lambda d: ph(d, 1)["items"][0].update(status="ok"), "unknown status")
    refuses(lambda d: d["phases"].reverse(), "out of the playbook's order")
    refuses(lambda d: d["phases"].insert(1, dict(ph(d, 0))), "out of the playbook's order")
    refuses(lambda d: ph(d, 0).update(phase="intake"), "unknown phase")
    refuses(lambda d: ph(d, 2).pop("waiting_on"), "waiting on nothing named")
    refuses(lambda d: ph(d, 1)["items"][2].pop("waiting_on"), "waiting on nothing named")
    refuses(lambda d: ph(d, 4).update(started="2026-01-07T00:00:00Z"), "a date on a not-started phase")
    refuses(lambda d: ph(d, 3)["forecast"].pop("basis"), "a forecast with no basis")
    refuses(lambda d: ph(d, 1).update(finished="2026-01-03T00:00:00Z"), "finished on a phase not done")
    refuses(lambda d: ph(d, 1).update(started="2 Jan"), "not ISO-8601 UTC")
    _census(check)
    rows = rows_of(doc)
    check("phases: every playbook phase is a row, in order; an unlisted one is not started",
          [r["phase"] for r in rows] == [p for p, _ in PHASES]
          and [r["status"] for r in rows if r["phase"] in ("fix-waves", "closure")]
          == ["not-started"] * 2, [(r["phase"], r["status"]) for r in rows])
    s = section(doc, [], "dev/programme/round9/phases.json")
    tr = {m.group(1): m.group(0) for m in re.finditer(r'<tr data-phase="([a-z-]+)".*?</tr>', s, re.S)}
    check("phases: the section draws a row per phase in the playbook's order",
          list(tr) == [p for p, _ in PHASES], list(tr))
    check("phases: a phase with no date prints dashes, never a date or a zero",
          all(tr[p].count('<td class="mono">—</td>') == 2 and "<td>—</td>" in tr[p]
              and not re.search(r"\d", re.sub(r"<[^>]+>|data-[a-z]+=\"[^\"]*\"", "", tr[p]))
              for p in ("stamps", "fix-waves", "closure")),
          {p: tr.get(p, "")[:200] for p in ("stamps", "fix-waves", "closure")})
    check("phases: a waiting phase names what it waits on", "waiting on THE-JUDGE" in tr["verify-judge"],
          tr["verify-judge"][:300])
    check("phases: a forecast prints its window and its basis",
          "Tue 06 Jan 08:00" in tr["plan"] and "BASIS-PLAN" in tr["plan"]
          and 'class="bar forecast"' in s, tr["plan"][:300])
    items = s.split('data-phase="finders"', 1)[1].split('data-phase="verify-judge"', 1)[0]
    check("phases: the running phase's items are drawn under it, each with its status",
          all(x in items for x in ("ITEM-DONE", "ITEM-RUN", "DETAIL-RUN", "waiting on QUEUE-X",
                                   "ITEM-NOT")), items[:400])
    check("phases: a done phase's items are not drawn", "ITEM-HIDDEN" not in s)
    check("phases: entry and exit are the file's words", "ENTRY-RS" in s and "EXIT-RS" in s)
    bad = section(None, ["X: unknown status"], "f.json")
    check("phases: an invalid file draws PHASES UNAVAILABLE, no table, no date",
          "PHASES UNAVAILABLE" in bad and "<table" not in bad and "X: unknown status" in bad, bad)
    # On the plan page's axis: cut at its ends, and saying so.
    t = dt.datetime
    cut = timeline(doc, rows_of(doc), (t(2026, 1, 1, 12), t(2026, 1, 6, 0)))
    check("phases: on an axis starting inside a phase, the bar is cut and names its start",
          "◂ since Thu 01 Jan 00:00" in cut, re.findall(r"◂[^<]*", cut))
    late = timeline(doc, rows_of(doc), (t(2026, 1, 3), t(2026, 1, 5, 6)))
    check("phases: a phase wholly before the axis and a forecast past it are named, not drawn",
          "done, Thu 01 Jan 00:00 to Fri 02 Jan 00:00, off this axis" in late
          and "past this axis" in late and 'class="bar forecast"' not in late
          and "as of" not in late, re.findall(r"[^>]*axis<", late))
    check("phases: null control, an axis holding every date cuts and omits nothing",
          "◂" not in (whole := timeline(doc, rows_of(doc), (t(2025, 12, 31), t(2026, 1, 8))))
          and "axis<" not in whole and "as of" in whole)
    with tempfile.TemporaryDirectory() as td:
        for n in (9, 11, 10):
            (Path(td) / f"dev/programme/round{n}").mkdir(parents=True)
            (Path(td) / f"dev/programme/round{n}/phases.json").write_text("{}")
        (Path(td) / "dev/programme/roundx").mkdir()
        (Path(td) / "dev/programme/roundx/phases.json").write_text("{}")
        found = discover(td)
        check("phases: discovery takes the highest-numbered round's file",
              found is not None and found.parent.name == "round11", found)
        check("phases: a host path is shown by its bare name, a checkout path relative",
              shown(found, "/elsewhere") == "phases.json"
              and shown(found, td) == "dev/programme/round11/phases.json")
    with tempfile.TemporaryDirectory() as td:
        check("phases: null control, a checkout with no phases file discovers none",
              discover(td) is None)


_JUNK = (5, 1.5, True, False, 0, [], ["x"], {}, {"x": "y"}, "")


def _nodes(x, path=()):
    """Every node of a JSON value as its path: the file's whole input surface."""
    yield path
    if isinstance(x, dict):
        for k, v in x.items():
            yield from _nodes(v, path + (k,))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _nodes(v, path + (i,))


def _census(check) -> None:
    """A file `violations` accepts is a file `section` draws: every node of a
    fully populated file, each replaced by each junk value, either earns a
    violation or draws -- on the plan page's axis and without one -- and
    `violations` itself never raises. The nodes come from the file, not from a
    list of field names, so a field the section starts reading is covered by
    being in the fixture."""
    import copy
    full = fixture()
    full["note"] = "NOTE-FULL"
    full["phases"][0]["waiting_on"] = "WAIT-FULL"
    axis = (dt.datetime(2026, 1, 1), dt.datetime(2026, 1, 8))
    paths = list(_nodes(full))
    keys = {p[-1] for p in paths if p and isinstance(p[-1], str)}
    read = {"note", "waiting_on", "entry", "exit", "detail", "name", "basis"}
    check("phases census: the fixture populates every text field the section reads",
          read <= keys, sorted(read - keys))
    crashed, ran = [], 0
    for path in paths[1:]:
        for junk in _JUNK:
            d = copy.deepcopy(full)
            at = d
            for k in path[:-1]:
                at = at[k]
            at[path[-1]] = junk
            ran += 1
            try:
                if not violations(d):
                    section(d, [], "f.json", axis)
                    section(d, [], "f.json")
            except Exception as exc:  # noqa: BLE001 -- any crash is the finding
                crashed.append((path, junk, type(exc).__name__))
    check("phases census: no accepted file crashes the section, no check crashes", not crashed, crashed[:5])
    check("phases census: null control, the unmutated full file is accepted and drawn",
          violations(full) == [] and "NOTE-FULL" in section(full, [], "f.json")
          and ran == len(_JUNK) * (len(paths) - 1), ran)


def page(doc, bad: list, where: str) -> str:
    """The section alone as a page, in the plan page's stylesheet."""
    import plan_page  # noqa: PLC0415 -- the stylesheet's one owner; imports this module
    style = re.search(r"<style>.*?</style>", plan_page._TEMPLATE, re.S).group(0)
    title = f"Round {doc['round']} Plan" if doc and not bad else "Round Plan"
    return ("<!doctype html>\n<meta charset=\"utf-8\">\n"
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n{style}\n<main>\n<header><h1>{html.escape(title)}</h1></header>\n"
            f"{section(doc, bad, where)}</main>\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", metavar="FILE", help="lint a phases file; exit 1 on a violation")
    p.add_argument("--phases", metavar="FILE")
    p.add_argument("--html", metavar="OUT", help="with --phases: the section alone as a page")
    a = p.parse_args(argv)
    path = a.check or a.phases
    if not path:
        p.error("--check FILE or --phases FILE --html OUT")
    doc, bad = load(path)
    for b in bad:
        print(f"plan_phases: {path}: {b}", file=sys.stderr)
    if a.html:
        Path(a.html).write_text(page(doc, bad, shown(path, Path.cwd())), encoding="utf-8")
        print(f"wrote {a.html}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
