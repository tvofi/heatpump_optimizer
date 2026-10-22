#!/usr/bin/env python3
"""pulse_replay.py -- replay tools/audit/seat/pulse.py's judge over history (R10-RCA-ORCH-CONTINUITY).

Builds, every --step-min minutes of a window (default 15), the snapshot pulse.py would have read at
that time, and judges it with pulse.py's own `judge` (imported, never copied).
Two arms are replayable from history; the verdict arm is not (review/<N> refs
are overwritten, so a past board's verdicts are gone) and is printed `n/a`.

  state-beat  exact: main's first-parent commit times against the state ref's
              commit times, both from git;
  opener      approximate: a handoff-body ref whose first commit is at least
              --opener-h old at the sample, with no pull request headed
              fix/<t>, fix/<t>-pr or handoff/<t> created by then, and whose
              handoff/<t> tip is not an ancestor of main at the sample, judged
              against the newest fix/ or handoff/ pull request opened by then. It
              stands in for `bus.sh orphans`, which reads only the present;
              its content arm (superseded) is not replayed.

    python3 dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z \
        --until 2026-10-21T08:00Z [--repo tvofi/heatpump_optimizer] [--remote origin]

Prints one line per sample an arm reads STOPPED, then the contiguous windows per
arm and the count of samples judged. Needs a full clone with the handoff,
handoff-body and state refs fetched, and `gh` for the pull-request list.
"""
from __future__ import annotations

import argparse
import bisect
import calendar
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "audit" / "seat"))
import pulse  # noqa: E402


def git(*a: str) -> str:
    return subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout


def epoch(s: str) -> int:
    return calendar.timegm(time.strptime(s.rstrip("Z"), "%Y-%m-%dT%H:%M"))


def iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(t))


def pull_requests(repo: str) -> list[dict]:
    out: list[dict] = []
    for page in range(1, 11):
        p = subprocess.run(["gh", "api", f"repos/{repo}/pulls?state=all&per_page=100&page={page}"
                            "&sort=created&direction=desc",
                            "--jq", "[.[] | {h: .head.ref, c: .created_at}]"],
                           check=True, capture_output=True, text=True)
        rows = json.loads(p.stdout)
        out += rows
        if len(rows) < 100:
            break
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--opener-h", type=float, default=3.0)
    ap.add_argument("--state-min", type=float, default=45.0)
    ap.add_argument("--step-min", type=int, default=15, help="the replay's sampling step")
    a = ap.parse_args(argv)
    t0, t1, r = epoch(a.since), epoch(a.until), a.remote
    b = pulse.bounds_s(a.opener_h, 2.0, a.state_min)
    main_c = sorted((int(t), h) for t, h in (l.split() for l in
                    git("log", "--first-parent", "--format=%ct %H", f"{r}/main").splitlines()))
    main_t = [t for t, _ in main_c]
    state_t = sorted(int(x) for x in git("log", "--format=%ct", f"{r}/handoff/audit-r10-plan").split())
    opened: dict[str, int] = {}
    prs = pull_requests(a.repo)
    opens = sorted(epoch(p["c"][:16]) for p in prs if p["h"].startswith(("fix/", "handoff/")))
    for p in prs:
        c = epoch(p["c"][:16])
        opened[p["h"]] = min(c, opened.get(p["h"], c))
    topics = []
    for ref in git("for-each-ref", "--format=%(refname:short)", f"refs/remotes/{r}/handoff-body").split():
        t = ref.split("/handoff-body/", 1)[1]
        first = int(git("log", "--format=%ct", "--max-parents=0", ref).split()[-1])
        tip = git("rev-parse", "--verify", "--quiet", f"refs/remotes/{r}/handoff/{t}").strip() if subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"refs/remotes/{r}/handoff/{t}"],
            capture_output=True).returncode == 0 else None
        pr = min((opened[h] for h in (f"fix/{t}", f"fix/{t}-pr", f"handoff/{t}") if h in opened), default=None)
        topics.append((t, first, tip, pr))
    anc_cache: dict[tuple[str, str], bool] = {}

    def ancestor(tip: str, head: str) -> bool:
        k = (tip, head)
        if k not in anc_cache:
            anc_cache[k] = subprocess.run(["git", "merge-base", "--is-ancestor", tip, head]).returncode == 0
        return anc_cache[k]

    stops: dict[str, list[int]] = {"opener": [], "state-beat": []}
    samples = 0
    for now in range(t0, t1 + 1, a.step_min * 60):
        samples += 1
        i = bisect.bisect_right(main_t, now) - 1
        j = bisect.bisect_right(state_t, now) - 1
        lines = []
        for t, first, tip, pr in topics:
            if first > now or (pr is not None and pr <= now) or tip is None:
                continue
            if i >= 0 and ancestor(tip, main_c[i][1]):
                continue
            lines.append(f"ORPHAN {t} {tip[:7]} {(now - first) / 3600:.1f}h uncovered=? repair=opener")
        k = bisect.bisect_right(opens, now) - 1
        snap = {"now": now, "last_open_t": opens[k] if k >= 0 else None, "orphans": {"rc": 1 if lines else 0,
                                        "out": "\n".join(lines + [f"orphans: {len(lines)} stranded"])},
                "verdicts": [], "open_heads": {}, "state_ref": "handoff/audit-r10-plan",
                "main_t": None, "state_t": state_t[j] if j >= 0 else None}
        if i >= 0 and j >= 0:  # pulse.read_state's rule, imported
            snap["main_t"] = pulse.oldest_unfollowed(main_t[:i + 1], state_t[j])
        for arm, word, detail in pulse.judge(snap, b):
            if arm in stops and word == "STOPPED":
                stops[arm].append(now)
                print(f"{iso(now)} {arm} STOPPED {detail}")
    print(f"replay: {samples} samples every {a.step_min} min judged, {iso(t0)}..{iso(t1)}; "
          "verdict arm n/a (refs overwritten)")
    for arm, ts in stops.items():
        wins, start, prev = [], None, None
        for t in ts:
            if start is None or t - prev > a.step_min * 60:
                if start is not None:
                    wins.append((start, prev))
                start = t
            prev = t
        if start is not None:
            wins.append((start, prev))
        print(f"WINDOWS {arm}: {len(ts)} sample(s) stopped in {len(wins)} window(s): "
              + ", ".join(f"{iso(s)}..{iso(e)}" for s, e in wins))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
