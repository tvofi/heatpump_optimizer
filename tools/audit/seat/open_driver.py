#!/usr/bin/env python3
"""The open driver: one pass opens the pull requests the tick board owes.

    python3 -I tools/audit/seat/open_driver.py [--board FILE] [--once]
    python3 -I tools/audit/seat/open_driver.py --self-test

A pass reads the board's `OWED <utc> handoff-no-pr refs/heads/handoff/<topic>
<sha> [ct=<epoch>]` lines, bare or as the tick board flags them (`-> OWED: OWED ...`) (an `OWED ... handoff-update` line or a
`handoff-body/` ref is not an open and is ignored), drops what must not open,
orders the rest, and launches `open_pr.sh` detached for as many as the cap
allows. The OPEN arm only: cloud_relay.sh's handoff arm owns update_pr.sh.

LIVE TIP (OPENER-LIVE-TIP, P603): the board is rewritten once per relay pass,
so its sha can lag origin. When origin's handoff tip differs from the board's
sha, the pass logs `RETIP <topic> <board sha8> -> <tip sha8>` and runs every
check below, and the open, at the live tip; `ct` stays the board line's.

SKIPPED (`SKIP <topic> <sha8> <reason>`): `moved` (origin has no handoff ref
for the topic), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
landed`, the classifier cloud_relay.sh and bus.sh orphans use), `fix-branch`
(fix/<topic> or fix/<topic>-pr exists), `seen` (opened at this sha), `live`
(its run is still going), `backoff` (a failed open waiting its turn), `stuck` (three
runs failed), `cap`.

TOPIC -> GROUP (P337 rule 3, P363), each candidate checked against the roster:
the override in open-titles.json first; `triage-s<N>-batch<M>` -> R10-TRIAGE-S<N>
(else R10-TRIAGE-B<M>); then (i) the uppercased topic, (ii) with one trailing
`-p<N>` removed, (iii) with one trailing `-<N>` removed. Exact match wins
(R10-ROSTER-OPS-2, R10-CI-LAYOUT-P1 are groups). A stripped match opens only
when the first three lines of the handoff body name the group as a whole name
(R10-ROSTER-OPS-3 does not name R10-ROSTER-OPS); otherwise `NEEDS-TITLE` and
nothing opens. The title is generated: `<GROUP> (part <N>): <topic words>` for
a stripped match, `<GROUP>: <topic words>` for an exact one.

ORDER (P337 rule 2, P350): `open-priority.txt` lists topics, one per line (`#`
comments), `open-cap.txt` the cap (default 2); both are re-read every pass. A
hotfix topic (R10-HOTFIX-*, or a group `roster_lib.is_hotfix` counts, which
includes `kind` "bug"), then an outside one (`roster_lib.is_outside`) or a
critical-path one (`roster_lib.critical_path`), one class unordered between
them (owner rulings tvofi 2026-11-07, triage P420, and 2026-11-08), is never
behind a topic of a later class, whatever the file says. Within a class a
listed topic keeps its file order, and an OMITTED topic is slotted after the
last listed topic of equal or higher default class (hotfix, outside or
critical, record topics `triage-*`/`roster-*`, the rest), never after every
listed topic.
A board topic unstarted for more than 2 h prints `STARVED <topic> <sha8> <h>h`
(age = now minus the handoff commit's ct).

RUNS (P337 rule 4, carry 4): a run is `bash open_pr.sh` in its own session; its
PID and result file live in `$HPO_STATE_DIR/open-driver/`, and live runs are
counted from those PIDs alone. A (topic, sha) is marked seen ONLY on rc=0; a
failed one is retried with backoff 30 min, then 60 min (doubling, capped at 2 h),
for THREE runs in all. The standing-contracts design's 30 min replaced the old
5-minute start: three fast retries of a content refusal only repeat it. While
fewer than three runs have failed every pass prints
`OWED <utc> open-refused <topic> <sha8> rc=<n> <reason>`; after the third the
(topic, sha) is `stuck`, never relaunched, and every pass prints exactly one
`STUCK <topic> <sha8> rc=<n> <reason>` line instead (beat_jobs.py's OPENER
regex reads the `STUCK ` prefix). A new sha is a new key and starts fresh.
Per-topic files are `t-<stem>.log`/`.rc`, so no topic name can equal
`open-driver.log`; `stem` escapes `%` before `/` so two topics never share a stem.
Log lines: START / RESULT rc=<n> / SKIP / RETIP / NEEDS-TITLE / STARVED.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import roster_lib  # noqa: E402
import topic_grammar  # noqa: E402

REPO = "tvofi/heatpump_optimizer"
# `-> OWED: ` is the tick board's flag on an owed level line (orchestrator_tick.py), the board the beat passes.
BOARD_RE = re.compile(r"^(?:-> OWED: )?OWED \S+ handoff-no-pr refs/heads/handoff/(\S+) ([0-9a-f]{40})(?: ct=(\d+|\?))?")
STARVE_S = 2 * 3600
BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3
DEFAULT_CAP = 2


def state_dir() -> Path:
    return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo")


def parse_board(text: str) -> list:
    """[(topic, sha, ct|None)] from a board, one per topic (the first line wins)."""
    out, seen = [], set()
    for line in text.splitlines():
        m = BOARD_RE.match(line)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ct = m.group(3)
            out.append((m.group(1), m.group(2), int(ct) if ct and ct.isdigit() else None))
    return out


names_group, resolve = topic_grammar.names_group, topic_grammar.group_of  # the grammar's one owner


SKIP_TOPIC_PREFIXES = ("triage-", "roster-")


def default_class(topic: str, group: str | None, critical, outside=frozenset(),
                  hotfix=frozenset()) -> int:
    """0 hotfix, 1 outside or critical (one class, unordered between them), 2
    record, 3 the rest. Owner rulings tvofi 2026-11-07 (triage P420) and
    2026-11-08: hotfix, then the outside requests with the critical path, then
    today's order. A hotfix is a hotfix topic or group name, or a group in
    `hotfix` (`roster_lib.is_hotfix`, which also counts `kind` "bug")."""
    if topic.startswith("r10-hotfix-") or (group or "").startswith("R10-HOTFIX-"):
        return 0
    if group and roster_lib.norm_group(group) in hotfix:
        return 0
    if group and roster_lib.norm_group(group) in outside | critical:
        return 1
    return 2 if topic.startswith(("triage-", "roster-")) else 3


#: Classes at or below this are fenced ahead of every other topic, in class
#: order, whatever the priority file says: hotfix, then outside or critical.
FENCED = 1


def order(items, priority: list, critical, outside=frozenset(), hotfix=frozenset()) -> list:
    """items: [(topic, group, ct)]. Hotfix, then outside or critical, first;
    a listed topic keeps its file order within a class; an omitted one slots after
    the last listed topic of equal or higher class."""
    cls = {t: default_class(t, g, critical, outside, hotfix) for t, g, _ in items}
    idx = {t: i for i, t in enumerate(priority)}

    def pos(t):
        if t in idx:
            return float(idx[t])
        above = [idx[u] for u in idx if u in cls and cls[u] <= cls[t] and (cls[u] <= FENCED) == (cls[t] <= FENCED)]
        return max(above, default=-1) + 0.5

    return sorted(items, key=lambda x: (min(cls[x[0]], FENCED + 1), pos(x[0]), cls[x[0]], x[2] or 0, x[0]))


def stem(topic: str) -> str:
    """The topic as one file name: a ref may hold a slash, a file name may not."""
    return topic.replace("%", "%25").replace("/", "%2F")


def backoff(n: int) -> int:
    return min(BACKOFF_S * 2 ** max(n - 1, 0), BACKOFF_MAX_S)


class World:
    """Everything a pass reads or starts outside its own state files."""

    def __init__(self, repo: str, sd: Path):
        self.repo, self.sd = repo, sd
        self.opener = HERE / "open_pr.sh"

    def git(self, *a):
        return subprocess.run(["git", "-C", self.repo, *a], capture_output=True, text=True)

    def tips(self) -> dict:
        r = self.git("ls-remote", "origin", "refs/heads/handoff/*", "refs/heads/handoff-body/*", "refs/heads/fix/*", "refs/heads/main")
        return {l.split()[1]: l.split()[0] for l in r.stdout.splitlines() if len(l.split()) == 2}

    def body_head(self, topic: str) -> str:
        self.git("fetch", "-q", "origin", f"handoff-body/{topic}")
        r = self.git("show", f"FETCH_HEAD:BODY.md")
        return "\n".join(r.stdout.splitlines()[:3]) if r.returncode == 0 else ""

    def landed(self, main: str, sha: str) -> bool:
        r = subprocess.run([sys.executable, "-I", str(HERE / "ledger.py"), "landed", main], input=sha, cwd=self.repo,
                           capture_output=True, text=True)
        f = r.stdout.split()
        return r.returncode == 0 and len(f) >= 2 and f[1] != "-"

    def roster(self) -> dict:
        return roster_lib.show_roster(self.repo, roster_lib.reader_ref(self.repo, None))

    def launch(self, topic, sha, title, group) -> int:
        d = self.sd / "open-driver"
        rc = d / f"t-{stem(topic)}.rc"
        rc.unlink(missing_ok=True)
        # Paths and the topic travel as arguments, never as shell text: a ref name may hold `$(...)`.
        cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"t-{stem(topic)}.log"), str(rc), topic, sha, title, group]
        return subprocess.Popen(argv, cwd=self.repo, start_new_session=True, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid

    def alive(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return default


def _lines(p: Path) -> list:
    try:
        return [l.split("#")[0].strip() for l in p.read_text().splitlines() if l.split("#")[0].strip()]
    except OSError:
        return []


def reason(log: Path) -> str:
    try:
        ls = [l.strip() for l in log.read_text().splitlines() if l.strip()]
    except OSError:
        return "no log"
    hit = [l for l in ls if re.search(r"REFUSE|CLOSED|ROWLESS|STOPPED|STALE", l)]
    return (hit or ls or ["no output"])[-1][:200]


def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
    """One pass. Returns {'started': [...], 'skipped': {topic: reason}}."""
    d = sd / "open-driver"
    d.mkdir(parents=True, exist_ok=True)
    seen = set(_lines(d / "seen.txt"))
    runs = _load(d / "runs.json", {})
    fails = _load(d / "fails.json", {})
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))

    def log(msg):
        out(msg)
        with open(d / "open-driver.log", "a") as fh:
            fh.write(f"{stamp} {msg}\n")

    for t, r in list(runs.items()):  # reap: a result file settles a run; a vanished PID without one is a kill
        rcf = d / f"t-{stem(t)}.rc"
        rc = int(rcf.read_text().strip() or -1) if rcf.exists() else (None if world.alive(r["pid"]) else -1)
        if rc is None:
            continue
        key = f"{t} {r['sha']}"
        log(f"RESULT {t} {r['sha'][:8]} rc={rc} {reason(d / f"t-{stem(t)}.log")}")
        if rc == 0:
            seen.add(key)
            fails.pop(key, None)
            with open(d / "seen.txt", "a") as fh:
                fh.write(key + "\n")
        else:
            n = fails.get(key, {}).get("n", 0) + 1
            fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": reason(d / f"t-{stem(t)}.log")}
        del runs[t]
    (d / "fails.json").write_text(json.dumps(fails))

    for key, f in sorted(fails.items()):
        t, sha = key.split()
        if f["n"] >= MAX_TRIES:
            out(f"STUCK {t} {sha[:8]} rc={f['rc']} {f['why']}")
        else:
            out(f"OWED {stamp} open-refused {t} {sha[:8]} rc={f['rc']} {f['why']}")

    tips = world.tips()
    main = tips.get("refs/heads/main", "")
    ros = world.roster()
    groups = set(roster_lib.groups_of(ros))
    critical = {roster_lib.norm_group(g) for g in roster_lib.critical_path(ros)}
    outside = {roster_lib.norm_group(str(g.get("group") or "")) for g in ros.get("groups", []) if roster_lib.is_outside(g)}
    hotfix = {roster_lib.norm_group(str(g.get("group") or "")) for g in ros.get("groups", []) if roster_lib.is_hotfix(g)}
    titles = _load(sd / "open-titles.json", {})
    priority = _lines(sd / "open-priority.txt")
    try:
        cap = int((_lines(sd / "open-cap.txt") or [DEFAULT_CAP])[0])
    except ValueError:
        cap = DEFAULT_CAP
    skipped, cands, board_topics = {}, [], []
    for topic, sha, ct in parse_board(board):
        def skip(why):
            skipped[topic] = why
            log(f"SKIP {topic} {sha[:8]} {why}")
        live_tip = tips.get(f"refs/heads/handoff/{topic}")
        if live_tip and live_tip != sha:  # the board lags a relay pass: check and open origin's live tip (P603)
            log(f"RETIP {topic} {sha[:8]} -> {live_tip[:8]}")
            sha = live_tip
        if topic.startswith(SKIP_TOPIC_PREFIXES):  # mut:optopicskip
            skip("batched")  # triage and roster changes wait and merge together with stamps (tvofi 2026-11-04)
        elif live_tip is None:
            skip("moved")
        elif f"refs/heads/handoff-body/{topic}" not in tips:
            skip("no-body")
        elif f"{topic} {sha}" in seen:
            skip("seen")
        elif main and world.landed(main, sha):
            skip("landed")
        elif f"refs/heads/fix/{topic}" in tips or f"refs/heads/fix/{topic}-pr" in tips:
            skip("fix-branch")
        elif topic in runs:
            skip("live")
        elif fails.get(f"{topic} {sha}", {}).get("n", 0) >= MAX_TRIES:
            skip("stuck")
        elif fails.get(f"{topic} {sha}", {}).get("next", 0) > now:
            skip("backoff")
        else:
            board_topics.append((topic, sha, ct))
            g, title = resolve(topic, groups, world.body_head(topic), titles)
            if g is None:
                log(f"NEEDS-TITLE {topic} {sha[:8]}")
            else:
                cands.append((topic, g, ct, sha, title))
    started = []
    live = len(runs)
    by_topic = {c[0]: c for c in cands}
    for topic, g, ct in order([(c[0], c[1], c[2]) for c in cands], priority, critical, outside, hotfix):
        _, _, _, sha, title = by_topic[topic]
        if live >= cap:
            skipped[topic] = "cap"
            log(f"SKIP {topic} {sha[:8]} cap")
            continue
        pid = world.launch(topic, sha, title, g)
        runs[topic] = {"pid": pid, "sha": sha, "started": now}
        live += 1
        started.append(topic)
        log(f"START {topic} {sha[:8]} {g} pid={pid}")
    (d / "runs.json").write_text(json.dumps(runs))
    for topic, sha, ct in board_topics:
        if topic not in started and ct and now - ct > STARVE_S:
            out(f"STARVED {topic} {sha[:8]} {(now - ct) / 3600:.1f}h")
    return {"started": started, "skipped": skipped}


def main(argv) -> int:
    if argv[:1] == ["--self-test"]:
        import open_driver_selftest
        return open_driver_selftest.run()
    board = None
    if "--board" in argv:
        board = argv[argv.index("--board") + 1]
    sd = state_dir()
    text = Path(board).read_text() if board else sys.stdin.read()
    run_pass(text, World(os.getcwd(), sd), sd, time.time())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
