#!/usr/bin/env python3
"""r10_relay_owed_class_reach.py -- which relay OWED kinds can a POSTED clear? (R10-RCA-HANDOFF-SLIP)

The enumeration is the writer set, not a list of kinds: every line of
cloud_relay.sh that appends an OWED row to its log (`logline OWED "..."`, a
call of `owed`, or a literal `printf 'OWED ...'`). Each writer's row is built
from its own source text (`$pr` -> a PR number of its own, any other
`$var` -> a placeholder), a writer reached on every pass until disposed
(probe-ref, handoff-no-pr) is written twice, and every PR gets its POSTED row
after its OWED rows. The log then goes through orchestrator_tick.py's
production `relay_owed`, unmodified, and the harness counts the OWED lines it
still prints per writer. A writer whose row keys on its PR number is cleared
by that POSTED and prints 0: that is the null control, in the same run.

    python3 -I dev/audit/harnesses/r10_relay_owed_class_reach.py [tick.py] [cloud_relay.sh]

Run from the repository root; the default paths are relative to it.

RESULT writers=<n> kinds_on_kind_token=<n> uncleared_lines=<n> pr_keyed_writers=<n> pr_keyed_lines=<n>
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import types
from pathlib import Path

TICK = Path(sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/orchestrator_tick.py")
RELAY = Path(sys.argv[2] if len(sys.argv) > 2 else "tools/audit/seat/cloud_relay.sh")
LEVEL = ("probe-ref", "handoff-no-pr")  # written on every pass until disposed
UTC = "2026-10-21T01:00:00Z"
WRITER = re.compile(r"""logline OWED "([^"]+)"|\bowed ("[^;|&]+)|printf 'OWED ([^']+)' ([^>]+)>>""")


def rows_for(m: re.Match, pr: str) -> tuple[str, list[str]]:
    sub = lambda s: re.sub(r"\$\{?\w+\}?", "x" * 8, s.replace("$pr", pr).replace('"$pr"', pr))
    if m.group(1):  # logline OWED "<text>" -> OWED <utc> <text>
        text = sub(m.group(1))
        return text.split()[0], [f"OWED {UTC} {text}"]
    if m.group(2):  # owed "$pr" <sha> <why> -> logline OWED "$1 $2 $3"
        args = re.findall(r'"[^"]*"|\S+', m.group(2))
        return "owed()", [f"OWED {UTC} " + " ".join(sub(a.strip('"')) for a in args[:3])]
    fmt, args = m.group(3), m.group(4).split()  # printf 'OWED <fmt>' <args>
    vals = iter(sub(a.strip('"')) if a.strip('"') == "$pr" else "y" * 8 for a in args)
    return fmt.split()[0], [re.sub(r"%s", lambda _: next(vals, "z"), "OWED " + fmt)]


def main() -> int:
    spec = importlib.util.spec_from_file_location("hpo_tick", TICK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hpo_tick"] = mod
    spec.loader.exec_module(mod)
    cls = next(c for c in vars(mod).values() if isinstance(c, type) and "relay_owed" in vars(c))
    writers = []
    for n, line in enumerate(RELAY.read_text().splitlines(), 1):
        if line.lstrip().startswith(("#", "owed()")):
            continue
        for m in WRITER.finditer(line):
            pr = str(2600 + len(writers))
            kind, rows = rows_for(m, pr)
            writers.append((n, kind, pr, rows * (2 if kind in LEVEL else 1)))
    log = [r for _, _, _, rows in writers for r in rows]
    log += [f"POSTED {UTC} {pr} {'p' * 40}" for _, _, pr, _ in writers]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "cloud-relay.log")
        p.write_text("\n".join(log) + "\n")
        s = types.SimpleNamespace(relay_log=str(p), out=[])
        s.line = lambda S, t, flag=False: s.out.append(t)
        s.unreadable = lambda *a: s.out.append("UNREADABLE")
        cls.relay_owed(s, "S")
    printed = [o for o in s.out if o.startswith("OWED: ")]
    on_kind, pr_keyed, pr_lines = set(), 0, 0
    print(f"log rows {len(log)} ({len(writers)} OWED writers, {len(writers)} POSTED); printed OWED lines {len(printed)}")
    for n, kind, pr, rows in writers:
        left = sum(1 for o in printed if o[len("OWED: "):] in rows)
        keyed = rows[0].split()[2]
        print(f"  cloud_relay.sh:{n:<4} {kind:<18} keyed on {keyed!r:<16} rows {len(rows)} after POSTED {pr}: {left} still OWED")
        if keyed == pr:
            pr_keyed += 1
            pr_lines += left
        else:
            on_kind.add(kind)
    uncleared = len(printed) - pr_lines
    print(f"RESULT writers={len(writers)} kinds_on_kind_token={len(on_kind)} uncleared_lines={uncleared} "
          f"pr_keyed_writers={pr_keyed} pr_keyed_lines={pr_lines}")
    print("kinds keyed on the kind token: " + " ".join(sorted(on_kind)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
