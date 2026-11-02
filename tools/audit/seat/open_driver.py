#!/usr/bin/env python3
"""The open driver: one pass opens the pull requests the tick board owes.

    python3 -I tools/audit/seat/open_driver.py [--board FILE] [--once]
    python3 -I tools/audit/seat/open_driver.py --self-test

A pass reads the board's `OWED <utc> handoff-no-pr refs/heads/handoff/<topic>
<sha> [ct=<epoch>]` lines (an `OWED ... handoff-update` line or a
`handoff-body/` ref is not an open and is ignored), drops what must not open,
orders the rest, and launches `open_pr.sh` detached for as many as the cap
allows. The OPEN arm only: cloud_relay.sh's handoff arm owns update_pr.sh.

SKIPPED (`SKIP <topic> <sha8> <reason>`): `moved` (origin's handoff tip is not
the board's sha), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
landed`, the classifier cloud_relay.sh and bus.sh orphans use), `fix-branch`
(fix/<topic> or fix/<topic>-pr exists), `seen` (opened at this sha), `live`
(its run is still going), `backoff` (a failed open waiting its turn), `cap`.

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
critical-path topic (`roster_lib.critical_path`) is never behind a non-critical
one, whatever the file says. Within the critical and the non-critical part a
listed topic keeps its file order, and an OMITTED topic is slotted after the
last listed topic of equal or higher default class (critical, R10-HOTFIX-*,
record topics `triage-*`/`roster-*`, the rest), never after every listed topic.
A board topic unstarted for more than 2 h prints `STARVED <topic> <sha8> <h>h`
(age = now minus the handoff commit's ct).

RUNS (P337 rule 4, carry 4): a run is `bash open_pr.sh` in its own session; its
PID and result file live in `$HPO_STATE_DIR/open-driver/`, and live runs are
counted from those PIDs alone. A (topic, sha) is marked seen ONLY on rc=0; a
failed one is retried with backoff (5 min doubling to 2 h) and prints
`OWED <utc> open-refused <topic> <sha8> rc=<n> <reason>` every pass until it
opens. Log lines: START / RESULT rc=<n> / SKIP / NEEDS-TITLE / STARVED.
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

REPO = "tvofi/heatpump_optimizer"
BOARD_RE = re.compile(r"^OWED \S+ handoff-no-pr refs/heads/handoff/(\S+) ([0-9a-f]{40})(?: ct=(\d+|\?))?")
STARVE_S = 2 * 3600
BACKOFF_S, BACKOFF_MAX_S = 300, 7200
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


def names_group(body_head: str, group: str) -> bool:
    """`group` appears as a whole name in the text: not inside a longer one."""
    return re.search(r"(?<![A-Za-z0-9_-])%s(?![A-Za-z0-9_-])" % re.escape(group), body_head, re.I) is not None


def resolve(topic: str, groups, body_head: str, titles: dict | None = None) -> tuple:
    """(group, title) or (None, why). `groups` are the roster's group ids."""
    words = topic.replace("-", " ")
    t = (titles or {}).get(topic)
    if isinstance(t, dict) and t.get("group") and t.get("title"):
        return t["group"], t["title"]
    m = re.fullmatch(r"triage-s(\d+)-batch(\d+)", topic)
    if m:
        for g in (f"R10-TRIAGE-S{m.group(1)}", f"R10-TRIAGE-B{m.group(2)}"):
            if g in groups:
                return g, f"{g}: {words}"
        return None, "NEEDS-TITLE"
    up = topic.upper()
    if up in groups:  # exact match always wins
        return up, f"{up}: {words}"
    for rx in (r"-p(\d+)", r"-(\d+)"):  # (ii) one trailing -p<N>, then (iii) one trailing -<N>
        m = re.fullmatch(r"(.+)" + rx, topic)
        if m and m.group(1).upper() in groups and names_group(body_head, m.group(1).upper()):
            g = m.group(1).upper()
            return g, f"{g} (part {m.group(2)}): {words}"
    return None, "NEEDS-TITLE"


def default_class(topic: str, group: str | None, critical) -> int:
    if group and roster_lib.norm_group(group) in critical:
        return 0
    if topic.startswith("r10-hotfix-") or (group or "").startswith("R10-HOTFIX-"):
        return 1
    return 2 if topic.startswith(("triage-", "roster-")) else 3


def order(items, priority: list, critical) -> list:
    """items: [(topic, group, ct)]. Critical first; a listed topic keeps its file order;
    an omitted one slots after the last listed topic of equal or higher class."""
    cls = {t: default_class(t, g, critical) for t, g, _ in items}
    idx = {t: i for i, t in enumerate(priority)}

    def pos(t):
        if t in idx:
            return float(idx[t])
        above = [idx[u] for u in idx if u in cls and cls[u] <= cls[t] and (cls[u] == 0) == (cls[t] == 0)]
        return max(above, default=-1) + 0.5

    return sorted(items, key=lambda x: (cls[x[0]] != 0, pos(x[0]), cls[x[0]], x[2] or 0, x[0]))


def backoff(n: int) -> int:
    return min(BACKOFF_S * 2 ** max(n - 1, 0), BACKOFF_MAX_S)


class World:
    """Everything a pass reads or starts outside its own state files."""

    def __init__(self, repo: str, sd: Path):
        self.repo, self.sd = repo, sd

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
        rc = d / f"{topic}.rc"
        rc.unlink(missing_ok=True)
        cmd = f'bash {HERE}/open_pr.sh "$@" > {d}/{topic}.log 2>&1; echo $? > {rc}'
        return subprocess.Popen(["bash", "-c", cmd, "_", topic, sha, title, group], cwd=self.repo, start_new_session=True,
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid

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
        rcf = d / f"{t}.rc"
        rc = int(rcf.read_text().strip() or -1) if rcf.exists() else (None if world.alive(r["pid"]) else -1)
        if rc is None:
            continue
        key = f"{t} {r['sha']}"
        log(f"RESULT {t} {r['sha'][:8]} rc={rc} {reason(d / (t + '.log'))}")
        if rc == 0:
            seen.add(key)
            fails.pop(key, None)
            with open(d / "seen.txt", "a") as fh:
                fh.write(key + "\n")
        else:
            n = fails.get(key, {}).get("n", 0) + 1
            fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": reason(d / (t + ".log"))}
        del runs[t]
    (d / "fails.json").write_text(json.dumps(fails))

    for key, f in sorted(fails.items()):
        t, sha = key.split()
        out(f"OWED {stamp} open-refused {t} {sha[:8]} rc={f['rc']} {f['why']}")

    tips = world.tips()
    main = tips.get("refs/heads/main", "")
    ros = world.roster()
    groups = set(roster_lib.groups_of(ros))
    critical = {roster_lib.norm_group(g) for g in roster_lib.critical_path(ros)}
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
        if tips.get(f"refs/heads/handoff/{topic}") != sha:
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
    for topic, g, ct in order([(c[0], c[1], c[2]) for c in cands], priority, critical):
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
