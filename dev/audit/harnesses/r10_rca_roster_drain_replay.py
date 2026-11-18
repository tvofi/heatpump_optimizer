#!/usr/bin/env python3
"""R10-RCA-ROSTER-DRAIN-REPLAY: what a replayed index-keyed carry op does.

    python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py replay
    python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py census BASE TIP
    python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py mutants
    python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py contained REF
    python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py cost

`replay` applies one op twice to a five-entry fixture through roster_edit's
own `apply_op`, which is what a drain replay does: `drop-carry G 1` removes
two entries, while `drop-carry G --match TEXT` removes one and its replay
refuses (the control). It then shows `roster_queue.replay_unsafe` refusing
the index form and passing the `--match` form.

`census` walks the `drop-carry` commits on the roster branch from BASE
(exclusive) to TIP. For each one, it names the carry entry the commit
removed: the first index where the group's carry list differs before and
after. THE REPLAY RULE: a drop is a replay when an earlier drop in the
window removed an entry at the same (group, index). An index op replayed
from the top of the queue lands on that same pair again. `restored` marks a
replay whose removed text a later `append-carry` in the window added back.
The control is that rule applied to the first drop at each pair, so the
count of first drops that were restored is printed too.

`mutants` plants four mutants in a copy of `roster_queue.py` and runs that
copy's `--self-test`. Each mutant must turn the self-test red, and the
unmutated copy must pass.

`contained REF` counts the carry entries at REF that `--match` cannot name:
an entry whose full text is also inside a sibling entry of the same group
matches both, which `_carry_index` refuses as ambiguous. Only the index
names those. `cost` times `roster_queue.replay_unsafe` per queue line over
100000 calls.

Read-only: it reads git objects and writes only under a temp directory.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path



def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
SEAT = ROOT / "tools/audit/seat"
ROSTER = "dev/programme/rosters/wave-r10-groups.json"
MARK = re.compile(r" \[(implemented|moved|dismissed): [^\]]*\]$")


def _seat(name):
    sys.path.insert(0, str(SEAT))
    return __import__(name)


def replay():
    re_ = _seat("roster_edit")
    rq = _seat("roster_queue")

    def fixture():
        return {"groups": [{"group": "G", "carry": [f"entry {i}" for i in range(5)]}]}

    def twice(**kw):
        r, outcomes = fixture(), []
        for _ in range(2):
            try:
                re_.apply_op(r, "drop-carry", "G", kw.get("value"), None, None, match=kw.get("match"))
                outcomes.append("applied")
            except re_.Refuse as e:
                outcomes.append(f"refused: {e}")
        return r["groups"][0]["carry"], outcomes

    left, out = twice(value="1")
    print(f"INDEX drop-carry G 1, run twice: {out}; removed={5 - len(left)} left={left}")
    left, out = twice(match="entry 1")
    print(f"MATCH drop-carry G --match 'entry 1', run twice: {out}; removed={5 - len(left)} left={left}")
    for line in ("drop-carry G 1", "mark-carry G 1 dismissed x",
                 "drop-carry G --match 'entry 1'", "mark-carry G --match 'entry 1' dismissed x"):
        op, _g, _arg, extra = rq.parse_line(line)
        print(f"GATE {line!r}: {rq.replay_unsafe(op, extra) or 'runs'}")


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT, check=True).stdout


def _carries(sha):
    r = json.loads(_git("show", f"{sha}:{ROSTER}"))
    return {g["group"]: list(g.get("carry") or []) for g in r["groups"]}


def census(base, tip):
    revs = [ln.split(" ", 2) for ln in _git("log", "--reverse", "--format=%H %cI %s",
                                           f"{base}..{tip}", "--", ROSTER).splitlines()]
    prev, drops, appended = _carries(base), [], []
    for sha, when, subj in revs:
        cur = _carries(sha)
        words = subj.split()
        op = words[1] if len(words) > 2 and words[0] == "roster_edit" else None
        grp = words[2] if op else None
        if op == "drop-carry":
            a, b = prev.get(grp, []), cur.get(grp, [])
            i = next(k for k in range(len(a)) if k >= len(b) or a[k] != b[k])
            drops.append((sha[:9], when, grp, i, MARK.sub("", a[i])))
        elif op == "append-carry":
            appended.append((when, grp, MARK.sub("", cur[grp][-1])))
        prev = cur
    seen, replays, firsts = set(), [], []
    for d in drops:
        (replays if (d[2], d[3]) in seen else firsts).append(d)
        seen.add((d[2], d[3]))

    def restored(d):
        return any(g == d[2] and t == d[4] and w > d[1] for w, g, t in appended)
    by = defaultdict(list)
    for d in replays:
        by[(d[2], d[3])].append(d[1][11:16])
        print(f"REPLAY {d[0]} {d[1]} {d[2]} idx={d[3]} restored={'Y' if restored(d) else '-'} {d[4][:60]!r}")
    for (g, i), ts in sorted(by.items()):
        print(f"PAIR {g} idx={i} replayed_at={','.join(ts)}")
    print(f"RESULT drops={len(drops)} replays={len(replays)} "
          f"replays_restored={sum(map(restored, replays))} "
          f"replays_unrestored={sum(not restored(d) for d in replays)} "
          f"firsts={len(firsts)} firsts_restored={sum(map(restored, firsts))}")


def contained(ref):
    n = total = 0
    for g, carry in _carries(ref).items():
        total += len(carry)
        n += sum(any(j != i and a in b for j, b in enumerate(carry)) for i, a in enumerate(carry))
    print(f"RESULT ref={ref} entries={total} contained_in_a_sibling={n}")


def cost():
    import timeit
    rq = _seat("roster_queue")
    us = timeit.timeit(lambda: rq.replay_unsafe("drop-carry", ["--match", "x"]), number=100000) / 100000 * 1e6
    print(f"RESULT replay_unsafe_us_per_line={us:.3f}")


MUTANTS = {
    "M1 predicate never refuses": ('if op in ("drop-carry", "mark-carry") and "--match" not in extra:',
                                   "if False:"),
    "M2 single-op path skips the check": ("        why = replay_unsafe(op, extra)\n        if why:",
                                          "        why = None\n        if why:"),
    "M3 batch path skips the check": ("        why = p and replay_unsafe(p[0], p[3])", "        why = None"),
    "M4 mark-carry left out": ('if op in ("drop-carry", "mark-carry")', 'if op in ("drop-carry",)'),
}


def mutants():
    src = (SEAT / "roster_queue.py").read_text()
    with tempfile.TemporaryDirectory() as t:
        # a copy of tools/ (roster_edit imports its siblings and tools/audit), the rest linked
        seat = Path(t, "tools/audit/seat")
        shutil.copytree(ROOT / "tools", Path(t, "tools"), ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
        for top in ("tests", "dev", ".git"):
            os.symlink(ROOT / top, Path(t, top))
        dst = seat / "roster_queue.py"
        killed = 0
        for name, (a, b) in [("baseline", ("", ""))] + list(MUTANTS.items()):
            if a and src.count(a) != 1:
                print(f"{name}: SITE NOT FOUND (count {src.count(a)})")
                return 2
            dst.write_text(src.replace(a, b) if a else src)
            r = subprocess.run([sys.executable, str(dst), "--self-test"], capture_output=True,
                               text=True, cwd=t)
            fails = [ln[:110] for ln in (r.stdout + r.stderr).splitlines() if ln.startswith("FAIL ")]
            print(f"{name}: rc={r.returncode} fails={len(fails)} {fails}")
            if name == "baseline" and r.returncode != 0:
                return 2
            killed += bool(a) and r.returncode != 0
        print(f"RESULT mutants={len(MUTANTS)} killed={killed}")
        return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["replay"]:
        replay()
    elif cmd == ["census"] and len(sys.argv) == 4:
        census(sys.argv[2], sys.argv[3])
    elif cmd == ["contained"] and len(sys.argv) == 3:
        contained(sys.argv[2])
    elif cmd == ["cost"]:
        cost()
    elif cmd == ["mutants"]:
        sys.exit(mutants())
    else:
        sys.exit(__doc__)
