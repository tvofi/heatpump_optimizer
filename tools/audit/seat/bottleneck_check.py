#!/usr/bin/env python3
"""Bottleneck alert: one line per flow metric past its threshold, for the digest.

    python3 -I bottleneck_check.py --checkout DIR [--roster-ref REF] \
        [--train-log PATH] [--wip-cap N] [--until ISO] [--memory PATH]
    python3 -I bottleneck_check.py --self-test

The owner's proposal 2 (tvofi 2026-11-07): "Add flow board metrics in the plan
HTML and a mechanism to alert you [the orchestrator] on bottlenecks and enable
you to decide whether to act on it." This prints, per breach,

    BOTTLENECK: <metric> <value> vs <threshold> -- <suggested action>

and nothing at all when no metric is past its threshold: silence is the
success, never a zero line. A source the metric cannot read prints
`BOTTLENECK-UNREADABLE: <metric> -- <why>`, because a blind alert is not a
quiet one. A line SUGGESTS; it takes no action. The orchestrator decides.

The metrics are `merge_throughput.bottleneck_metrics`, imported: the flow
board's own computations (`flow_closed`, `flow_verdicts`, `flow_lead`) and two
added there for this alert (`flow_merge_wait`, `train_batches`). Nothing here
re-reads a source.

THE THRESHOLDS (THRESHOLDS below; the owner's, 2026-11-07), each with the
smallest sample that may trip it, so that one verdict or one merge never fires:
  yield       first-pass review yield < 0.6 over 24 h (at least 5 first passes);
  skip-share  train skips / entries > 30 % over the last 2 completed batches
              (at least 3 entries);
  merge-wait  median merge-verdict-to-merge > 2 h over 24 h (at least 3 PRs);
  throughput  roster groups closed per hour < 0.7 x takt over 6 h;
  wip         in-progress groups (pr_cap.wip_groups) at or over the cap;
  block-class one blocked class > 30 % of blocks over 24 h (at least 5 blocks).

--memory PATH (the beat row's form): a metric that stays past its threshold
re-prints the line it first printed, verbatim, so the digest's fold sees no
new line and the wake fires once per trip; a metric back inside its threshold
is forgotten, and its next trip prints afresh. The memory is keyed by the
line's kind and metric, so a breach after an UNREADABLE beat for the same
metric (or the reverse) is a new trip and prints.

--self-test: a planted metrics dict trips each rule exactly once and a null
control (every metric inside its threshold) prints nothing; each rule's
boundary, its minimum sample, its UNREADABLE arm and the trip memory are
cases; and one mutant per rule predicate, and one reverting the memory key,
must be killed.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

#: (metric, threshold, minimum sample). The comparison is each rule's own.
THRESHOLDS = {
    "yield": (0.6, 5),
    "skip-share": (0.30, 3),
    "merge-wait": (2.0, 3),
    "throughput": (0.7, 0),
    "wip": (1.0, 0),
    "block-class": (0.30, 5),
}
SKIP_BATCHES = 2


def _unread(metric: str, why: str) -> str:
    return f"BOTTLENECK-UNREADABLE: {metric} -- {why}"


def judge(m: dict) -> list[str]:
    """The breach lines for one metrics dict (`bottleneck_metrics`' shape)."""
    out: list[str] = []

    v, why = m["yield"]
    if v is None:
        out.append(_unread("yield", why))
    else:
        merged, judged = v
        lim, n = THRESHOLDS["yield"]
        if judged >= n and merged / judged < lim:
            out.append(f"BOTTLENECK: yield {merged / judged:.2f} ({merged}/{judged} first passes, 24 h) "
                       f"vs {lim} -- read the blocked-class mix; brief its top class into the "
                       "open fixers' briefs or a prepr check before dispatching more")

    v, why = m["batches"]
    if v is None:
        out.append(_unread("skip-share", why))
    else:
        done = [b for b in v if b["done"]][-SKIP_BATCHES:]
        entries = sum(b["queue"] for b in done)
        skips = [s for b in done for s in b["skips"]]
        lim, n = THRESHOLDS["skip-share"]
        if entries >= n and len(skips) / entries > lim:
            top, k = Counter(r for _, r in skips).most_common(1)[0]
            out.append(f"BOTTLENECK: skip-share {len(skips) / entries:.0%} ({len(skips)}/{entries}, "
                       f"batches {' '.join(b['tag'] for b in done)}) vs {lim:.0%} -- {k} of "
                       f"{len(skips)} are '{top}': re-add a skipped head only once classify "
                       "reads GREEN, and hold the next launch until the race it names settles")

    v, why = m["merge_wait"]
    if v is None:
        out.append(_unread("merge-wait", why))
    else:
        rows, _ = v
        lim, n = THRESHOLDS["merge-wait"]
        if len(rows) >= n:
            med = statistics.median(r["hours"] for r in rows)
            if med > lim:
                worst = max(rows, key=lambda r: r["hours"])
                out.append(f"BOTTLENECK: merge-wait {med:.1f} h median ({len(rows)} PRs, 24 h; worst "
                           f"#{worst['pr']} {worst['hours']:.1f} h) vs {lim:g} h -- the merge stage "
                           "is the constraint: check the train is live and every verdicted head "
                           "is queued before dispatching review or fix work")

    v, why = m["closed"]
    if v is None:
        out.append(_unread("throughput", why))
    else:
        lim, _ = THRESHOLDS["throughput"]
        rate, want = round(v / 6.0, 6), round(lim * m["takt"], 6)
        if rate < want:
            out.append(f"BOTTLENECK: throughput {rate:.2f}/h ({v} groups closed, 6 h) vs "
                       f"{want:.2f}/h (0.7 x takt {m['takt']:g}) -- find the stage holding the "
                       "work (merge-wait, skip-share, yield above) and drain it before "
                       "dispatching new groups")

    v, why = m["wip"]
    if v is None:
        out.append(_unread("wip", why))
    elif len(v) >= m["wip_cap"]:
        out.append(f"BOTTLENECK: wip {len(v)} in-progress vs cap {m['wip_cap']} -- dispatch no new "
                   "group; move review and merge work first")

    v, why = m["classes"]
    if v is None:
        out.append(_unread("block-class", why))
    else:
        total = sum(v.values())
        lim, n = THRESHOLDS["block-class"]
        if total >= n:
            top, k = v.most_common(1)[0]
            if k / total > lim:
                out.append(f"BOTTLENECK: block-class {top or 'unclassed'} {k / total:.0%} ({k}/{total} "
                           f"blocks, 24 h) vs {lim:.0%} -- a recurring class owes a root-cause seat "
                           "(defect-root-cause.md) or a check that catches it before review")
    return out


def metric_of(line: str) -> str:
    """The metric a line is about: its second word."""
    return line.split()[1]


def state_of(line: str) -> str:
    """The memory key of a line: its kind and metric, its first two words, so
    `BOTTLENECK-UNREADABLE: yield` and `BOTTLENECK: yield` are distinct states."""
    return " ".join(line.split()[:2])


def remembered(lines: list[str], memory: Path | None) -> list[str]:
    """`lines` with each still-tripped state's FIRST line kept verbatim, and
    the memory rewritten: tripped states only, so a recovery forgets."""
    if memory is None:
        return lines
    try:
        old = json.loads(memory.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    now = {state_of(ln): old.get(state_of(ln), ln) for ln in lines}
    memory.parent.mkdir(parents=True, exist_ok=True)
    memory.write_text(json.dumps(now, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return [now[state_of(ln)] for ln in lines]


def live_metrics(checkout: Path, roster_ref: str | None, train_log: Path | None,
                 wip_cap: int, until: str | None) -> dict:
    sys.path.insert(0, str(checkout / "tools" / "audit"))
    import merge_throughput as mt  # the flow board's computations, imported
    roster_lib = mt.roster_lib
    ref = roster_lib.reader_ref(str(checkout), roster_ref)
    why = ""
    try:
        roster = roster_lib.show_roster(str(checkout), ref)
        path = roster_lib.roster_path(str(checkout), ref)
    except (roster_lib.RosterNotFound, ValueError) as e:
        roster, path, why = None, None, f"roster unreadable: {e}"
    crit, cwhy = mt.critical_read(checkout, ref, roster)
    ctx = mt.FlowCtx(repo=checkout, tree="origin/main", remote="origin", roster=roster,
                     roster_unavailable=why, roster_ref=ref, roster_path=path, prefix="",
                     record_prefix="record/", critical=crit, critical_unavailable=cwhy)
    end = (mt.parse_iso(until) if until else mt.flow_default_until(checkout, "origin/main", ref))
    if end is not None and end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return mt.bottleneck_metrics(ctx, end, train_log, wip_cap)


# ------------------------------------------------------------------ self-test

def _fixture(**over) -> dict:
    """Every metric inside its threshold: the null control's input."""
    batch = lambda tag, q, skips, done=True: {"tag": tag, "queue": q, "done": done,
                                               "skips": [(i, "ci: red at the head: gate")
                                                         for i in range(skips)]}
    m = {"takt": 1.0, "wip_cap": 20,
         "yield": ((8, 10), ""),
         "batches": ([batch("a", 9, 9), batch("b", 5, 1), batch("c", 5, 1),
                      batch("d", 4, 4, done=False)], ""),
         "merge_wait": (([{"pr": 1, "hours": 1.0}, {"pr": 2, "hours": 2.0},
                          {"pr": 3, "hours": 9.0}], 0), ""),
         "closed": (6, ""),
         "wip": (["G"] * 19, ""),
         "classes": (Counter({"ci-red": 2, "harness": 2, "defect": 2, "policy": 2, "x": 2}), "")}
    m.update(over)
    return m


def self_test(mutate: str | None = None) -> int:
    global judge
    failures = 0

    def check(name: str, cond: bool, got="") -> None:
        nonlocal failures
        failures += not cond
        if mutate is None:
            print(f"  {'ok  ' if cond else 'FAIL'} {name}" + ("" if cond else f": {got!r}"))

    def fired(m) -> list[str]:
        return [metric_of(ln) for ln in judge(m)]

    check("null control: every metric inside its threshold prints nothing",
          judge(_fixture()) == [], judge(_fixture()))
    planted = {
        "yield": {"yield": ((5, 10), "")},
        "skip-share": {"batches": ([{"tag": "x", "queue": 5, "done": True, "skips": [(1, "r")] * 2},
                                    {"tag": "y", "queue": 1, "done": True, "skips": []}], "")},
        "merge-wait": {"merge_wait": (([{"pr": 1, "hours": 2.5}] * 3, 0), "")},
        "throughput": {"closed": (4, "")},
        "wip": {"wip": (["G"] * 20, "")},
        "block-class": {"classes": (Counter({"mutation-vacuous": 4, "a": 3, "b": 3}), "")},
    }
    for metric, over in planted.items():
        got = fired(_fixture(**over))
        check(f"planted: {metric} past its threshold prints exactly its line", got == [metric], got)
        line = judge(_fixture(**over))[0] if got else ""
        check(f"planted: the {metric} line has the grammar",
              line.startswith(f"BOTTLENECK: {metric} ") and " vs " in line and " -- " in line, line)
    # boundaries: at the threshold is not past it (the owner's `<`, `>`)
    edges = {
        "yield": {"yield": ((6, 10), "")},
        "skip-share": {"batches": ([{"tag": "x", "queue": 10, "done": True, "skips": [(1, "r")] * 3}], "")},
        "merge-wait": {"merge_wait": (([{"pr": 1, "hours": 2.0}] * 3, 0), "")},
        "throughput": {"closed": (4.2, "")},
        "wip": {"wip": (["G"] * 19, "")},
        "block-class": {"classes": (Counter({"a": 3, "b": 3, "c": 3, "d": 1}), "")},
    }
    for metric, over in edges.items():
        got = fired(_fixture(**over))
        check(f"boundary: {metric} exactly at its threshold prints nothing", got == [], got)
    small = {
        "yield": {"yield": ((0, 4), "")},
        "skip-share": {"batches": ([{"tag": "x", "queue": 2, "done": True, "skips": [(1, "r")] * 2}], "")},
        "merge-wait": {"merge_wait": (([{"pr": 1, "hours": 9.0}] * 2, 0), "")},
        "block-class": {"classes": (Counter({"a": 4}), "")},
    }
    for metric, over in small.items():
        got = fired(_fixture(**over))
        check(f"minimum sample: {metric} below its sample prints nothing", got == [], got)
    check("skip-share: a batch still running is not read",
          fired(_fixture(batches=([{"tag": "x", "queue": 5, "done": True, "skips": []},
                                   {"tag": "y", "queue": 5, "done": True, "skips": []},
                                   {"tag": "z", "queue": 5, "done": False,
                                    "skips": [(1, "r")] * 5}], ""))) == [])
    for metric, key in (("yield", "yield"), ("skip-share", "batches"), ("merge-wait", "merge_wait"),
                        ("throughput", "closed"), ("wip", "wip"), ("block-class", "classes")):
        lines = judge(_fixture(**{key: (None, "no source")}))
        check(f"unreadable: {metric} is BOTTLENECK-UNREADABLE, never silent",
              lines == [_unread(metric, "no source")], lines)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        mem = Path(d) / "mem.json"
        first = remembered(judge(_fixture(closed=(4, ""))), mem)
        again = remembered(judge(_fixture(closed=(3, ""))), mem)
        check("memory: a still-tripped metric re-prints its first line verbatim",
              again == first and "4 groups" in first[0], (first, again))
        remembered(judge(_fixture()), mem)
        after = remembered(judge(_fixture(closed=(3, ""))), mem)
        check("memory: a recovery forgets; the next trip prints afresh",
              after and "3 groups" in after[0], after)
        # An UNREADABLE line and a breach line for one metric are distinct
        # memory states: a real breach after an unreadable beat prints itself,
        # and the reverse prints the UNREADABLE line (review 3350).
        mem.unlink()
        blind = judge(_fixture(closed=(None, "no source")))
        remembered(blind, mem)
        breach = remembered(judge(_fixture(closed=(4, ""))), mem)
        check("memory: a breach after UNREADABLE for one metric prints the breach",
              breach and breach[0].startswith("BOTTLENECK: throughput ") and "4 groups" in breach[0],
              breach)
        back = remembered(blind, mem)
        check("memory: UNREADABLE after a breach for one metric prints the UNREADABLE line",
              back == blind, back)
        again = remembered(judge(_fixture(closed=(None, "later reason"))), mem)
        check("memory: UNREADABLE then UNREADABLE stays its first line (null control)",
              again == blind, again)
        # Two metrics tripped in one beat are two memory states: a key of the
        # kind alone would collapse them and print one line twice.
        mem.unlink()
        two = judge(_fixture(closed=(4, ""), wip=(["G"] * 25, "")))
        got = remembered(two, mem)
        check("memory: two metrics tripped together each print their own line",
              len(two) == 2 and got == two and len(set(got)) == 2, (two, got))
    return failures


#: One mutant per rule predicate: (name, source fragment, replacement).
MUTANTS = (
    ("yield-cmp", "merged / judged < lim", "merged / judged <= lim"),
    ("yield-sample", "judged >= n and merged", "judged >= 0 and merged"),
    ("skip-cmp", "len(skips) / entries > lim", "len(skips) / entries >= lim"),
    ("skip-done", 'if b["done"]][-SKIP_BATCHES:]', "][-SKIP_BATCHES:]"),
    ("wait-cmp", "if med > lim:", "if med >= lim:"),
    ("wait-median", "statistics.median(r[\"hours\"]", "max(r[\"hours\"]"),
    ("tput-cmp", "if rate < want:", "if rate <= want:"),
    ("wip-cmp", 'elif len(v) >= m["wip_cap"]:', 'elif len(v) > m["wip_cap"]:'),
    ("class-cmp", "if k / total > lim:", "if k / total >= lim:"),
    ("class-sample", "if total >= n:", "if total >= 0:"),
)
#: The same, applied to `state_of`: the memory key reverted to the metric alone.
MEMORY_MUTANTS = (
    ("memory-key-metric", 'return " ".join(line.split()[:2])', "return line.split()[1]"),
    ("memory-key-kind", 'return " ".join(line.split()[:2])', "return line.split()[0]"),
)


def run_mutants() -> int:
    """Each mutant applied to its function's source (`judge`'s, or
    `state_of`'s) must make the self-test fail."""
    import inspect
    import textwrap
    survived = []
    g = globals()
    for fn, name, frag, repl in ([("judge", *m) for m in MUTANTS]
                                 + [("state_of", *m) for m in MEMORY_MUTANTS]):
        original = g[fn]
        src = textwrap.dedent(inspect.getsource(original))
        if src.count(frag) != 1:
            print(f"  FAIL mutant {name}: anchor occurs {src.count(frag)} times")
            survived.append(name)
            continue
        ns = dict(g)
        exec(compile(src.replace(frag, repl), f"<mutant {name}>", "exec"), ns)
        g[fn] = ns[fn]
        try:
            killed = self_test(mutate=name) > 0
        finally:
            g[fn] = original
        print(f"  {'ok  ' if killed else 'FAIL'} mutant {name} {'killed' if killed else 'SURVIVED'}")
        if not killed:
            survived.append(name)
    return len(survived)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--checkout", type=Path, default=Path(__file__).resolve().parents[3]
                    if len(Path(__file__).resolve().parents) > 3 else Path.cwd())
    ap.add_argument("--roster-ref", default=None)
    ap.add_argument("--train-log", type=Path, default=None)
    ap.add_argument("--wip-cap", type=int, default=20)
    ap.add_argument("--until", default=None)
    ap.add_argument("--memory", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        f = self_test()
        f += run_mutants()
        print(f"{'FAILED' if f else 'ok'}: bottleneck_check self-test")
        return 1 if f else 0
    m = live_metrics(a.checkout, a.roster_ref, a.train_log, a.wip_cap, a.until)
    for line in remembered(judge(m), a.memory):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
