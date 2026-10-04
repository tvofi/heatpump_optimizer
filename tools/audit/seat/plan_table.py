#!/usr/bin/env python3
"""The plan artifact over a wave-groups roster: swimlanes, gantt, detail, ETA.

    python3 tools/audit/seat/plan_table.py [--repo OWNER/REPO] \
        [--roster-ref GITREF | --roster-file PATH] [--out PATH] \
        [--cadence DAYS] [--live overlay.json]

Stateless: every input arrives as a flag -- the roster through `--roster-ref`
(a git ref whose `.claude/workflows/wave-r9-groups.json` is read with
`git show`) or `--roster-file`, the live notes through `--live`. Nothing about
a session is hardcoded, and the tool never writes GitHub state.

Sections emitted (markdown, one file or stdout):
  Swimlanes -- lane rows x wave columns, multiple groups joined with `<br>`.
  Waves     -- a mermaid gantt of the open groups; the critical path (the
               longest after-edge chain, roster_lib.critical_path) is tagged
               `crit`, which GitHub renders highlighted. Done groups are
               satisfied and do not appear; their after-edges no longer
               constrain.
  Groups    -- per-group detail: stage, issue(s) (Fixes bolded), fixer and
               reviewer models, owner gate, one-line description from the
               brief (roster_lib.one_line_brief), and the `--live` note.
  ETA       -- waves x `--cadence` days (default 2.0), per-wave day offsets
               and the total.

`--self-test` runs the tool over a fixture roster and checks the wave math,
the mermaid emission (fence balance, task grammar, every `after` dependency
naming a defined task id, `crit` exactly the critical path), and the
critical-path chain (each consecutive pair joined by a real after-edge, and
its length equal to the wave count).
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_lib  # noqa: E402

SELF = "tools/audit/seat/plan_table.py"
DEFAULT_CADENCE = 2.0  # days per wave; the roster brief's measured cadence

GANTT_BASE = "2026-01-05"  # arbitrary fixed Monday; offsets carry the meaning


def _task_id(group: str, used: dict) -> str:
    """A mermaid-safe task id per group: alphanumerics, unique."""
    cand = "".join(c for c in group if c.isalnum()) or "g"
    cand = cand[0].lower() + cand[1:]
    if cand in used:
        n = 2
        while f"{cand}{n}" in used:
            n += 1
        cand = f"{cand}{n}"
    used[cand] = group
    return cand


def gantt(roster: dict) -> str:
    """The mermaid gantt block for the roster's OPEN groups."""
    G = roster_lib.groups_of(roster)
    open_ = roster_lib.open_groups(roster)
    path = set(roster_lib.critical_path(roster))
    ids: dict = {}
    for g in open_:
        ids[g] = _task_id(g, ids)
    lanes = sorted({open_[g].get("lane") or "?" for g in open_})
    lines = ["gantt",
             "  title Fix waves; crit = the critical path",
             "  dateFormat YYYY-MM-DD",
             "  axisFormat day %d"]
    for lane in lanes:
        lines.append(f"  section {lane}")
        for g in [k for k in open_ if (open_[k].get("lane") or "?") == lane]:
            deps = [ids[a] for a in open_[g].get("after") or [] if a in open_]
            start = GANTT_BASE if not deps else None
            tag = "crit, " if g in path else ""
            when = (f"{start}, 1d" if start
                    else f"after {' '.join(deps)}, 1d")
            lines.append(f"    {g} :{tag}{ids[g]}, {when}")
    return "```mermaid\n" + "\n".join(lines) + "\n```"


def swimlanes(roster: dict) -> str:
    open_ = roster_lib.open_groups(roster)
    waves: dict = {}
    for g in open_:
        waves.setdefault(roster_lib.depth_of(roster)[g], []).append(g)
    lanes = sorted({open_[g].get("lane") or "?" for g in open_})
    n_waves = max(waves) if waves else 0
    head = "| lane \\ wave | " + " | ".join(str(w) for w in range(1, n_waves + 1)) + " |"
    bar = "|---" * (n_waves + 1) + "|"
    rows = []
    for lane in lanes:
        cells = []
        for w in range(1, n_waves + 1):
            gs = [g for g in waves.get(w, [])
                  if (open_[g].get("lane") or "?") == lane]
            cells.append("<br>".join(gs) if gs else "")
        rows.append(f"| {lane} | " + " | ".join(cells) + " |")
    return "\n".join([head, bar] + rows)


def detail(roster: dict, live: dict) -> str:
    G = roster_lib.groups_of(roster)
    depth = roster_lib.depth_of(roster)
    fixes_of = {g: set(G[g].get("fixes") or []) for g in G}
    rows = ["| group | lane | wave | stage | issues | models | owner gate | what | live note |",
            "|---|---|---|---|---|---|---|---|---|"]
    for g, gr in G.items():
        stage = (gr.get("resume") or {}).get("stage") or "?"
        issues = ", ".join(f"**#{n}**" if n in fixes_of[g] else f"#{n}"
                           for n in gr.get("issues") or []) or "-"
        models = f"{gr.get('fixerModel') or '-'}/{gr.get('reviewerModel') or '-'}"
        gate = gr.get("owner_gate")
        gate = ("yes: " + str(gate).replace("|", "/")) if gate else "-"
        note = str(live.get(g, "")).replace("|", "/")
        rows.append(f"| {g} | {gr.get('lane') or '-'} | {depth[g]} | {stage} | "
                    f"{issues} | {models} | {gate} | "
                    f"{roster_lib.one_line_brief(gr)} | {note} |")
    return "\n".join(rows)


def eta(roster: dict, cadence: float) -> str:
    open_ = roster_lib.open_groups(roster)
    depth = roster_lib.depth_of(roster)
    waves: dict = {}
    for g in open_:
        waves.setdefault(depth[g], []).append(g)
    n = max(waves) if waves else 0
    rows = [f"Cadence {cadence:g} days per wave (`--cadence`); "
            f"{n} wave(s) of work, total {n * cadence:g} days from wave-1 start.",
            "", "| wave | groups | starts (day) | ends (day) |", "|---|---|---|---|"]
    for w in range(1, n + 1):
        rows.append(f"| {w} | {len(waves.get(w, []))} | "
                    f"{(w - 1) * cadence:g} | {w * cadence:g} |")
    return "\n".join(rows)


def render(roster: dict, source: str, cadence: float, live: dict) -> str:
    depth = roster_lib.depth_of(roster)
    open_ = roster_lib.open_groups(roster)
    waves: dict = {}
    for g in open_:
        waves.setdefault(depth[g], []).append(g)
    n_all = len(roster_lib.groups_of(roster))
    path = roster_lib.critical_path(roster)
    unknown = sorted(set(live) - set(roster_lib.groups_of(roster)))
    if unknown:
        print(f"plan_table: live overlay names no roster group: {unknown}",
              file=sys.stderr)
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    parts = [f"# Plan table ({source})",
             f"Generated by `{SELF}` {today}; roster {source}.",
             "",
             f"{len(open_)} open group(s) of {n_all}; "
             f"{max(waves) if waves else 0} "
             f"wave(s); critical path: {' -> '.join(path) or '-'} "
             f"({len(path)}).",
             "", "## Swimlanes", "", swimlanes(roster),
             "", "## Waves", "", gantt(roster),
             "", "## Groups", "", detail(roster, live),
             "", "## ETA", "", eta(roster, cadence), ""]
    return "\n".join(parts)


# ------------------------------------------------------------------ self-test
def _fixture_roster() -> dict:
    def g(gid, lane, after, stage="not-started", issues=(), fixes=(),
          brief="", gate=None):
        return {"group": gid, "lane": lane, "issues": list(issues),
                "fixes": list(fixes), "wave": None, "after": list(after),
                "brief": brief, "fixerModel": "sonnet",
                "reviewerModel": "opus", "owner_gate": gate,
                "resume": {"stage": stage, "branch": f"handoff/{gid.lower()}"}}
    # A(w1) -> B(w2) and C(w2); D after B only (w3); E done, constrains nobody.
    return {"repo": "fixture/roster", "session": "fixture", "groups": [
        g("R9-A", "L1", [], "in-progress", (10,), (10,),
          "tvofi, 2026-01-01 (fixture): Does the first thing. A second sentence.",
          "gate for A"),
        g("R9-B", "L1", ["R9-A"], brief="Waits on A."),
        g("R9-C", "L2", ["R9-A"], brief="Also waits on A."),
        g("R9-D", "L2", ["R9-B"], brief="Last wave."),
        g("R9-E", "L1", ["R9-D"], stage="done", brief="Already done."),
    ]}


def _self_test() -> int:
    roster = _fixture_roster()
    failed = []

    n_checks = [0]

    def check(name, ok, got=""):
        n_checks[0] += 1
        if not ok:
            failed.append(f"{name} (got: {got})")

    # wave math (gen_table_rev3.py's recurrence): A 1; B, C 2; D 3; done E out.
    depth = roster_lib.depth_of(roster)
    check("wave A", depth["R9-A"] == 1, depth)
    check("wave B", depth["R9-B"] == 2, depth)
    check("wave C", depth["R9-C"] == 2, depth)
    check("wave D", depth["R9-D"] == 3, depth)
    check("done group still depthed", depth["R9-E"] == 4, depth)
    open_ = roster_lib.open_groups(roster)
    check("done group not open", set(open_) == {"R9-A", "R9-B", "R9-C", "R9-D"},
          sorted(open_))

    # critical path: the longest chain over OPEN groups; E's edge is satisfied.
    path = roster_lib.critical_path(roster)
    check("critical path", path == ["R9-A", "R9-B", "R9-D"], path)
    G = roster_lib.groups_of(roster)
    for a, b in zip(path, path[1:]):
        check(f"chain edge {a}->{b}", a in (G[b].get("after") or []))
    check("chain length equals wave count",
          len(path) == max(roster_lib.depth_of(roster)[g] for g in open_))

    # mermaid emission: balanced fence, task grammar, deps defined, crit path.
    block = gantt(roster)
    check("mermaid fence balance", block.startswith("```mermaid\n")
          and block.endswith("\n```") and block.count("```") == 2)
    body = block[len("```mermaid\n"):-len("\n```")]
    task_ids, crit, deps = {}, set(), {}
    for line in body.splitlines():
        s = line.strip()
        if not line.startswith("    ") or s in ("",) or " :" not in line:
            # header and directive lines sit at two spaces; sections too.
            if line and not line.startswith("    ") and line.strip() not in (
                    "gantt",) and not line.startswith("  "):
                failed.append(f"unexpected gantt line: {line!r}")
            continue
        name, rest = s.split(" :", 1)
        fields = rest.split(", ")
        i = 0
        if fields[0] == "crit":
            crit.add(name); i = 1
        tid = fields[i]
        task_ids[name] = tid
        i += 1
        if i < len(fields) and fields[i].startswith("after"):
            deps[tid] = fields[i][len("after"):].split()
    check("task count", len(task_ids) == len(open_), task_ids)
    defined = set(task_ids.values())
    for tid, ds in deps.items():
        for dname in ds:
            check(f"dep defined {tid}", dname in defined, ds)
    path_ids = set(path)
    check("crit exactly the critical path", crit == path_ids, crit)
    roots = sorted(tid for tid in defined if tid not in deps)
    check("one root (A; done E's edge satisfied)", len(roots) == 1, roots)

    # render: swimlane cell, live overlay, eta, one-line brief.
    live = {"R9-B": "fixer in flight", "R9-NOPE": "warned"}
    text = render(roster, "fixture", DEFAULT_CADENCE, live)
    check("swimlane cell join", "| L1 | R9-A | R9-B |" in text, text[:0])
    check("overlay note rendered", "fixer in flight" in text)
    check("one-line brief strips attribution and one sentence",
          "Does the first thing." in text
          and "A second sentence" not in text
          and "tvofi, 2026-01-01" not in text)
    check("eta total", f"{3 * DEFAULT_CADENCE:g} days" in text)
    check("fixes bolded", "**#10**" in text)
    check("owner gate rendered", "yes: gate for A" in text)
    check("done group listed with stage", "| R9-E | L1 | 4 | done |" in text)

    # empty roster renders, does not raise (a degenerate roster is a document).
    empty = render({"groups": []}, "fixture", 1, {})
    check("empty roster renders", "0 open group(s) of 0" in empty)

    print(f"plan_table self-test: {n_checks[0]} checks, {len(failed)} failed")
    for f in failed:
        print("FAIL", f)
    return 1 if failed else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--repo", default="tvofi/heatpump_optimizer")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--roster-ref", default="handoff/audit-r9-fixplan")
    src.add_argument("--roster-file")
    p.add_argument("--out")
    p.add_argument("--cadence", type=float, default=DEFAULT_CADENCE)
    p.add_argument("--live")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)
    if a.self_test:
        return _self_test()
    if a.roster_file:
        roster = roster_lib.load_roster_file(a.roster_file)
        source = a.roster_file
    else:
        roster = roster_lib.show_roster(a.repo, a.roster_ref)
        source = a.roster_ref
    live = {}
    if a.live:
        live = json.loads(Path(a.live).read_text(encoding="utf-8"))
        if not isinstance(live, dict):
            print("plan_table: --live must be a {group: note} object",
                  file=sys.stderr)
            return 2
    text = render(roster, source, a.cadence, live)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(text.encode())} bytes)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
