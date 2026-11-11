#!/usr/bin/env python3
"""r10_relay_owed_class_reach.py -- which relay OWED rows does the tick clear? (R10-RCA-HANDOFF-SLIP)

The enumeration is the writer set, not a list of kinds: every line of
cloud_relay.sh before its `self_test()` (the self-test's fixture rows write no
production OWED) that writes an OWED row -- `logline OWED "..."`, a call of
`owed`, a literal `printf 'OWED ...' >>` (all appended to the log), or
`level_line <kind>` (the level file, a tree at or after b38c6431a). Each
writer's row is built from its own source text (`$pr` -> a PR number of its
own, any other `$var` -> a placeholder).

Two passes are simulated. An event row is appended once. A level kind
(probe-ref, handoff-no-pr: owed on every pass until disposed) appended to the
log is appended on both passes; a `level_line` row goes through the tree's own
`level_set`, run by bash on both passes, into `<log>.level`. The tree's
production `relay_owed`, unmodified, then reads the result twice: without
POSTED rows, and with a POSTED for every writer's PR after its OWED rows.

Classification is by what the tick under test does, never by the row's own
tokens: an event the first read prints and the second does not is cleared by
its PR's POSTED; one the second still prints is uncleared; one the first does
not print is unreported. A level is live (no POSTED closes it), so its count
is the lines printed against one item per level writer; a surplus is history
replayed as a level. Healthy: events_uncleared=0 events_unreported=0
level_lines=level_items.

    python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py [tick.py] [cloud_relay.sh]

Run from the repository root; the default paths are relative to it.

RESULT writers=<n> events=<n> events_cleared=<n> events_uncleared=<n> events_unreported=<n> level_writers=<n> level_lines=<n> level_items=<n>
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import types
from pathlib import Path

TICK = Path(sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/orchestrator_tick.py")
RELAY = Path(sys.argv[2] if len(sys.argv) > 2 else "tools/audit/seat/cloud_relay.sh")
LEVEL = ("probe-ref", "handoff-no-pr")  # written on every pass until disposed
UTC = "2026-10-21T01:00:00Z"
PASSES = 2
WRITER = re.compile(r"""logline OWED "([^"]+)"|\bowed ("[^;|&]+)|printf 'OWED ([^']+)' ([^>]+)>>|\blevel_line (\S+) """)
DEFS = ("#", "owed()", "level_line()", "level_set()")


def rows_for(m: re.Match, pr: str) -> tuple[str, str, str]:
    """(kind, sink, row): sink is `log` or `level`."""
    sub = lambda s: re.sub(r"\$\{?\w+\}?", "x" * 8, s.replace("$pr", pr).replace('"$pr"', pr))
    if m.group(1):  # logline OWED "<text>" -> OWED <utc> <text>
        text = sub(m.group(1))
        return text.split()[0], "log", f"OWED {UTC} {text}"
    if m.group(2):  # owed "$pr" <sha> <why> -> logline OWED "$1 $2 $3"
        args = re.findall(r'"[^"]*"|\S+', m.group(2))
        return "owed()", "log", f"OWED {UTC} " + " ".join(sub(a.strip('"')) for a in args[:3])
    if m.group(5):  # level_line <kind> "$ref" "$sha" -> OWED <utc> <kind> <ref> <sha>
        return m.group(5), "level", f"OWED {UTC} {m.group(5)} {'r' * 8} {'s' * 8}"
    fmt, args = m.group(3), m.group(4).split()  # printf 'OWED <fmt>' <args>
    vals = iter(sub(a.strip('"')) if a.strip('"') == "$pr" else "y" * 8 for a in args)
    return fmt.split()[0], "log", re.sub(r"%s", lambda _: next(vals, "z"), "OWED " + fmt)


def level_set_src(text: str) -> str:
    """The tree's own relay_log() and level_set() definitions, verbatim."""
    out, take = [], False
    for line in text.splitlines():
        if line.startswith(("relay_log() {", "level_set() {")):
            take = True
        if take:
            out.append(line)
            if line.startswith("relay_log() {") or line == "}":
                take = False
    return "\n".join(out)


def main() -> int:
    spec = importlib.util.spec_from_file_location("hpo_tick", TICK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hpo_tick"] = mod
    spec.loader.exec_module(mod)
    cls = next(c for c in vars(mod).values() if isinstance(c, type) and "relay_owed" in vars(c))
    text = RELAY.read_text()
    writers = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("self_test()"):
            break
        if line.lstrip().startswith(DEFS):
            continue
        for m in WRITER.finditer(line):
            pr = str(2600 + len(writers))
            writers.append((n, pr, *rows_for(m, pr)))
    log = []
    for p in range(PASSES):  # a level kind appended to the log is appended on every pass
        log += [row for _, _, kind, sink, row in writers if sink == "log" and (p == 0 or kind in LEVEL)]
    posted = [f"POSTED {UTC} {pr} {'p' * 40}" for _, pr, *_ in writers]

    def read(d: str, rows: list[str]) -> list[str]:
        p = Path(d, "cloud-relay.log")
        p.write_text("\n".join(rows) + "\n")
        s = types.SimpleNamespace(relay_log=str(p), out=[])
        s.line = lambda S, t, flag=False: s.out.append(t)
        s.unreadable = lambda *a: s.out.append("UNREADABLE")
        cls.relay_owed(s, "S")
        return [o[len("OWED: "):] for o in s.out if o.startswith("OWED: ")]

    with tempfile.TemporaryDirectory() as d:
        lv = [(kind, row) for _, _, kind, sink, row in writers if sink == "level"]
        fn = level_set_src(text)
        for _ in range(PASSES if lv else 0):  # every pass rewrites <kind>'s lines through level_set
            for kind, row in lv:
                Path(d, f"lines.{kind}").write_text(row + "\n")
                subprocess.run(["bash", "-c", f'{fn}\nlevel_set "$1" "$2"', "-", kind, str(Path(d, f"lines.{kind}"))],
                               env={"LOG": str(Path(d, "cloud-relay.log")), "PATH": "/usr/bin:/bin"}, check=True)
        before, after = read(d, log), read(d, log + posted)
    print(f"log rows {len(log)}, level writers {len(lv)}, {PASSES} passes, {len(writers)} OWED writers; "
          f"printed without POSTED {len(before)}, with POSTED {len(after)}")
    ev = {"cleared": 0, "uncleared": 0, "unreported": 0}
    lw = level_lines = 0
    for n, pr, kind, sink, row in writers:
        b, a = before.count(row), after.count(row)
        if kind in LEVEL:
            lw += 1
            level_lines += a
            verdict = f"level: {a} line(s) printed for 1 item"
        else:
            verdict = "unreported" if b == 0 else "uncleared" if a else "cleared"
            ev[verdict] += a if verdict == "uncleared" else 1
            verdict = f"event: {verdict} by POSTED {pr}"
        print(f"  cloud_relay.sh:{n:<4} {kind:<18} -> {sink:<5} {verdict}")
    print(f"RESULT writers={len(writers)} events={len(writers) - lw} events_cleared={ev['cleared']} "
          f"events_uncleared={ev['uncleared']} events_unreported={ev['unreported']} "
          f"level_writers={lw} level_lines={level_lines} level_items={lw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
