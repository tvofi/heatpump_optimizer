#!/usr/bin/env python3
"""Replay the session sweep log's owed blocks through owed_unactioned.py.

    python3 -I replay.py <orch-sweep.log> <checkout> [--acked]

orch-sweep.log is the session board's own output (`orch_sweep.sh`), one
`== SWEEP <UTC> ==` block per sweep, its `-- owed (tick)` block being the
tick's `-> OWED` lines that board kept. Each block becomes one board, read at
its sweep time plus one minute, against one state file, as the sweep would
have run it. Prints one TSV row per sweep: time, rc, owed keys, unactioned
keys. `--acked` writes, at each key's first sweep, an OWED-ACK that the
orchestrator re-takes every sweep (ttl=1): the null control, which must print
rc 0 throughout.
"""
import datetime as dt, importlib.util, os, re, sys, tempfile

log, root = sys.argv[1], sys.argv[2]
acked = "--acked" in sys.argv
spec = importlib.util.spec_from_file_location("ou", os.path.join(root, "tools/audit/seat/owed_unactioned.py"))
ou = importlib.util.module_from_spec(spec); spec.loader.exec_module(ou)

sweeps, cur = [], None
for line in open(log, errors="replace"):
    m = re.match(r"== SWEEP (\S+) ==", line)
    if m:
        cur = [m.group(1), []]; sweeps.append(cur); continue
    s = line.strip()
    if cur and s.startswith("-> OWED"):
        cur[1].append(s)

print("sweep\trc\towed\tunactioned")
with tempfile.TemporaryDirectory() as d:
    state = os.path.join(d, "state.json")
    for at, lines in sweeps:
        t = ou.utc(at)
        board = f"BOARD measured from origin/main at replay, {at}\n" + "\n".join(lines) + "\n"
        acks = []
        if acked:
            keys = ou.board(board)[1]
            acks = [("acks", "\n".join(f"OWED-ACK {at} {k} {(v['shas'] or ['-'])[0]} ttl=1 replay null control: re-taken each sweep"
                                       for k, v in keys.items()))]
        out = []
        rc = ou.run(board, state, acks, t + dt.timedelta(minutes=1), 2, 20, True, out.append)
        head = out[0] if out else ""
        n = re.search(r"owed: (\d+) key", head)
        bad = [o.split()[0] for o in out if re.match(r"  \S+  sweeps=", o)]
        print(f"{at}\t{rc}\t{n.group(1) if n else '?'}\t{','.join(bad)}")
