#!/usr/bin/env python3
"""r10_ledger_class_reach.py -- does every obligation the relay writes reach a closer? (R10-ORCH-LEDGER)

The companion of r10_relay_owed_class_reach.py, applying its rule to the tree
after the obligations ledger: that harness enumerates the writers of OWED rows
appended to cloud-relay.log, and the ledger retires that path, so at a ledger
tree it finds the relay's level writers only. This one enumerates the writer
set the ledger has instead, never a list of kinds:

  event writers  every line of cloud_relay.sh before `self_test()` calling
                 `ledger_open <kind>` (each opens an event in events.tsv);
  level writers  every `level_line <kind>` there (rewritten into <log>.level
                 by the tree's own `level_set`), and every kind ledger.py's
                 `handoff_level` writes (`OWED {now} <kind> ...`).

Each event writer's row is opened through the production CLI (`ledger.py
open`) in a scratch home, under a PR of its own and a sha of its own. A writer
whose kind the ledger refuses is `refused`. The production `fold` then reads
the store twice: with nothing read, and with the writer's closer applied -- for
a PR-keyed kind, a read-back of the approver verdict naming its sha (for
`verdict-unposted`, the verdict's own first line); for any other, the
producer's `close` through the CLI. An event the first fold does not print is
unreported, one the second still prints is uncleared, the rest cleared. A
level kind must be a ledger kind (else `level_unkinded`), and the relay's
`level_set` run on two passes must leave one line per writer.

    python3 -I dev/audit/harnesses/r10_ledger_class_reach.py [cloud_relay.sh] [ledger.py]

Run from the repository root. Healthy: events_uncleared=0 events_unreported=0
events_refused=0 level_unkinded=0 level_lines=level_items. A tree with no
ledger.py prints RESULT ledger=absent.

RESULT ledger=present writers=<n> events=<n> events_cleared=<n> events_uncleared=<n> events_unreported=<n> events_refused=<n> level_writers=<n> level_unkinded=<n> level_lines=<n> level_items=<n>
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RELAY = Path(sys.argv[1] if len(sys.argv) > 1 else "tools/audit/seat/cloud_relay.sh")
LEDGER = Path(sys.argv[2] if len(sys.argv) > 2 else "tools/audit/seat/ledger.py")
EVENT = re.compile(r"\bledger_open ([a-z-]+) ")
LEVEL = re.compile(r"\blevel_line ([a-z-]+) ")
LEDGER_LEVEL = re.compile(r'f"OWED \{now\} ([a-z-]+) ')
PASSES = 2


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
    if not LEDGER.is_file():
        print(f"{LEDGER} is absent at this tree")
        print("RESULT ledger=absent")
        return 0
    spec = importlib.util.spec_from_file_location("hpo_ledger", LEDGER)
    lg = importlib.util.module_from_spec(spec)
    sys.modules["hpo_ledger"] = lg
    spec.loader.exec_module(lg)
    text = RELAY.read_text()
    writers = []  # (where, kind, sink)
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("self_test()"):
            break
        if line.lstrip().startswith(("#", "ledger_open()", "level_line()", "level_set()")):
            continue
        writers += [(f"cloud_relay.sh:{n}", m.group(1), "event") for m in EVENT.finditer(line)]
        writers += [(f"cloud_relay.sh:{n}", m.group(1), "level") for m in LEVEL.finditer(line)]
    for n, line in enumerate(LEDGER.read_text().splitlines(), 1):
        writers += [(f"ledger.py:{n}", m.group(1), "level") for m in LEDGER_LEVEL.finditer(line)]
    ev = {"cleared": 0, "uncleared": 0, "unreported": 0, "refused": 0}
    lw = unkinded = level_lines = 0
    with tempfile.TemporaryDirectory() as d:
        for i, (where, kind, sink) in enumerate(writers):
            home = Path(d, f"w{i}")
            home.mkdir()
            log, pr, sha = str(home / "cloud-relay.log"), str(2700 + i), f"{i:040x}"
            if sink == "level":
                lw += 1
                if kind not in lg.KINDS:
                    unkinded += 1
                fn, lines = level_set_src(text), home / "lines"
                for _ in range(PASSES):
                    lines.write_text(f"OWED 2026-10-23T00:00:00Z {kind} refs/heads/x/{i} {sha}\n")
                    subprocess.run(["bash", "-c", f'{fn}\nlevel_set "$1" "$2"', "-", kind, str(lines)],
                                   env={"LOG": log, "PATH": "/usr/bin:/bin"}, check=True)
                got = sum(1 for l in Path(log + ".level").read_text().splitlines() if f" {kind} " in l)
                level_lines += got
                print(f"  {where:<20} {kind:<22} -> level {got} line(s) for 1 item"
                      + ("" if kind in lg.KINDS else " (NO LEDGER KIND)"))
                continue
            verdict = f"Fix review: merge {sha}"
            why = verdict if kind == "verdict-unposted" else "x"
            cli = lambda *a: subprocess.run([sys.executable, "-I", str(LEDGER), "--log", log, *a],
                                            capture_output=True, text=True).returncode
            if cli("open", kind, pr, sha, why) != 0:
                ev["refused"] += 1
                print(f"  {where:<20} {kind:<22} -> event refused by the ledger")
                continue
            before = {(k, s) for k, s, *_ in lg.fold(lg.events(home, log))[0]}
            if kind in lg.PR_KEYED:
                after = lg.fold(lg.events(home, log), {pr: sha}, {pr: [verdict]})[0]
                closer = "read-back"
            else:
                cli("close", kind, pr, sha, "done")
                after, closer = lg.fold(lg.events(home, log))[0], "close"
            after = {(k, s) for k, s, *_ in after}
            res = ("unreported" if (kind, pr) not in before
                   else "uncleared" if (kind, pr) in after else "cleared")
            ev[res] += 1
            print(f"  {where:<20} {kind:<22} -> event {res} by its {closer}")
    events = len(writers) - lw
    print(f"RESULT ledger=present writers={len(writers)} events={events} events_cleared={ev['cleared']} "
          f"events_uncleared={ev['uncleared']} events_unreported={ev['unreported']} "
          f"events_refused={ev['refused']} level_writers={lw} level_unkinded={unkinded} "
          f"level_lines={level_lines} level_items={lw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
