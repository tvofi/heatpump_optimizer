#!/usr/bin/env python3
"""beatd.py -- the one supervised beat: a job table run on a schedule, never an agent loop.

    python3 -I tools/audit/seat/beatd.py run --state S [--jobs FILE] [--repo DIR]
        [--once | --for SECONDS]
    python3 -I tools/audit/seat/beatd.py status --state S [--jobs FILE] [--repo DIR]
        [--pulse FILE] [--now EPOCH]
    python3 -I tools/audit/seat/beatd.py held --state S
    python3 -I tools/audit/seat/beatd.py --self-test

WHY THIS EXISTS (R10-ORCH-BEATD, design note on design/R10-ORCH-BEATD 32e249d2e,
arm (a)). The programme's daemons were hand-launched, one per seat, with no
bookkeeping, and agent-hosted loops ended their turns and went silent. This is
the engine that replaces them: one process, a table of jobs, a journal. Arm (a)
ships the engine and no production table; the rows are arm (b)'s.

THE TABLE. `{"version": 1, "class_wait_s": 60, "jobs": [...]}`; `class_wait_s`
is optional (default 60). Each job has exactly the keys `name`, `argv` (a list;
an argv[0] holding `/` is relative to the repository; `$S` in any argument is
the state directory), `cwd` (`orch`, the beat's checkout, or a path),
`interval_s`, `timeout_s`, `heartbeat_s` (seconds or null), `env_pass` (names
passed through from the beat's environment), `class` (null or
`orch-checkout`) and `kind` (`periodic`: started every interval; `watch`:
restarted interval_s after its instance ends). An unknown or missing key, a
wrong type, a duplicate name, `interval_s < 60` on a watch job, or an
unreadable file refuses: `beatd: REFUSE <reason>`, rc 2, and zero jobs run.

RUN. `run` holds `S/beatd/beatd.lock` (a second run exits 75, `ALREADY
RUNNING`). Each job runs on its own thread, in its own process group, under
`S/beatd/<job>.lock` (held elsewhere: `outcome=locked`). At timeout_s the group
gets SIGTERM, and SIGKILL 10 s later unless it has emptied, even when its
leader exited on the SIGTERM (`outcome=timeout`). A class job holds
`S/beatd/<class>.lock` for its whole run and waits at most class_wait_s for it,
then records `outcome=busy`. A lock file holds its owner's pid while held and
is emptied on release, so a non-empty lock whose pid is dead is an owner that
died holding it. A job's environment is HOME, USER, LOGNAME, LANG, LC_ALL,
TMPDIR, SHELL, its env_pass names, `HPO_BEATD_JOB=<name>`, `HPO_REAL_GIT`,
`HPO_GIT_SHIM_LOG=S/beatd/git-retry.log`, the ref-lock timeout
(`core.filesRefLockTimeout=30000` through GIT_CONFIG_COUNT), and PATH with
`beatd_shims` first. The real git is resolved once, before that prepend: the
first `git` on the beat's own PATH, canonicalised; it refuses rc 2 when there
is none, when it is a shim (line 2 `# hpo-git-shim`), or when it does not
answer `--version` with `git version`. `--once` runs each job once; `--for N`
stops scheduling after N seconds. Either way the run waits for its jobs.

JOURNAL (`S/beatd/journal.log`), one line per event:
    START <utc> beatd pid=<p> code=<HEAD sha> supervisor=<HPO_BEATD_SUPERVISOR|none>
    RUNNING <utc> <job> pid=<p> elapsed=<s>   (at start, then every heartbeat_s)
    PASS <utc> <job> start=<utc> dur=<s> rc=<rc> outcome=ok|failed|timeout|locked|busy|unreadable
    STOP <utc> beatd pid=<p>

STATUS. One `JOB <name> <state> age=<s> last=<outcome>` line per job, where
state is `late` (age since its last PASS, or since START, exceeds interval_s +
timeout_s), `running`, `idle` (a watch job with no instance), `ok`, or the last
outcome when that is not ok. Then the alarms: `DOWN` (beatd.lock free),
`ALERT lock-owner-dead <lock> pid=<p>`, `ALERT pulse-silent <pulse line>` for
each `PULSE <arm> STOPPED` line of the pulse file (default S/beatd/pulse.txt,
pulse.py's output; absent prints `pulse=none`), and `STALE-CODE behind=<n>`
when the START code is behind origin/main. rc 0 clean, 1 any alarm (late,
DOWN, a non-ok last outcome, an ALERT, STALE-CODE), 2 unreadable (table,
journal line, or the staleness read). An unreadable input is never clean.

HELD. `held` is beatd.lock's one reader for other scripts: rc 0 and
`held pid=<p>` while a beat holds it, rc 1 `free` otherwise. Its probe is a
shared non-blocking flock released at once; `run` retries its own lock for
0.6 s, so a probe never costs a starting beat its instance.

Not here, stated: no job row (arm (b)), no refusal in any other script (arms
(b), (c)), and no supervisor unit (host config the owner applies; until then
`supervisor=none`).
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHIMS = Path(__file__).resolve().parent / "beatd_shims"
MARKER = "# hpo-git-shim"
KEYS = {"name", "argv", "cwd", "interval_s", "timeout_s", "heartbeat_s",
        "env_pass", "class", "kind"}
CLASSES = {None, "orch-checkout"}
KINDS = {"periodic", "watch"}
BASE_ENV = ("HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR", "SHELL")
KILL_GRACE_S = 10.0
OUTCOMES = ("ok", "failed", "timeout", "locked", "busy", "unreadable")
LINE_RE = re.compile(
    r"^(?:START \S+ beatd pid=\d+ code=\S+ supervisor=\S+"
    r"|RUNNING \S+ \S+ pid=\d+ elapsed=\d+"
    r"|PASS \S+ \S+ start=\S+ dur=\d+ rc=-?\d+ outcome=(?:%s)"
    r"|STOP \S+ beatd pid=\d+)$" % "|".join(OUTCOMES))


class Refuse(Exception):
    """A refusal: printed as `beatd: REFUSE <reason>`, rc 2."""


def utc(t: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if t is None else t))


def parse_utc(s: str) -> float:
    import calendar
    return float(calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")))


# ---------------------------------------------------------------- the table

def load_table(path: Path) -> dict:
    """The validated table, or Refuse. Never a partial table."""
    try:
        doc = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise Refuse(f"job table {path} unreadable: {e}") from None
    if not isinstance(doc, dict) or set(doc) - {"version", "class_wait_s", "jobs"} \
            or doc.get("version") != 1 or not isinstance(doc.get("jobs"), list):
        raise Refuse(f"job table {path}: want {{version: 1, jobs: [...]}} "
                     "(optional class_wait_s), nothing else")
    wait = doc.get("class_wait_s", 60)
    if not isinstance(wait, (int, float)) or isinstance(wait, bool) or wait < 0:
        raise Refuse("class_wait_s must be a number >= 0")
    seen: set[str] = set()
    for i, j in enumerate(doc["jobs"]):
        if not isinstance(j, dict) or set(j) != KEYS:
            got = set(j) if isinstance(j, dict) else set()
            raise Refuse(f"job {i}: keys must be exactly {sorted(KEYS)}; "
                         f"unknown {sorted(got - KEYS)}, missing {sorted(KEYS - got)}")
        name = j["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) \
                or name in seen or name == "beatd" or name in CLASSES:
            raise Refuse(f"job {i}: bad or duplicate name {name!r}")
        seen.add(name)
        if not (isinstance(j["argv"], list) and j["argv"]
                and all(isinstance(a, str) and a for a in j["argv"])):
            raise Refuse(f"{name}: argv must be a non-empty list of strings")
        if not isinstance(j["cwd"], str) or not j["cwd"]:
            raise Refuse(f"{name}: cwd must be 'orch' or a path")
        for k in ("interval_s", "timeout_s"):
            v = j[k]
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
                raise Refuse(f"{name}: {k} must be a positive number")
        hb = j["heartbeat_s"]
        if hb is not None and (not isinstance(hb, (int, float)) or isinstance(hb, bool) or hb <= 0):
            raise Refuse(f"{name}: heartbeat_s must be a positive number or null")
        if not (isinstance(j["env_pass"], list) and all(isinstance(e, str) for e in j["env_pass"])):
            raise Refuse(f"{name}: env_pass must be a list of names")
        if j["class"] not in CLASSES:
            raise Refuse(f"{name}: class must be null or orch-checkout")
        if j["kind"] not in KINDS:
            raise Refuse(f"{name}: kind must be periodic or watch")
        if j["kind"] == "watch" and j["interval_s"] < 60:
            raise Refuse(f"{name}: a watch job's interval_s must be >= 60")
    return {"class_wait_s": float(wait), "jobs": doc["jobs"]}


# ---------------------------------------------------------------- locks

class Lock:
    """An flock'd file holding its owner's pid; emptied on release."""

    def __init__(self, path: Path):
        self.path, self.fd = path, None

    def take(self, wait_s: float = 0.0, step: float = 0.2) -> bool:
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)  # owner-only, as gate_lock.py
        deadline = time.monotonic() + wait_s
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    os.close(fd)
                    return False
                time.sleep(step)
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={os.getpid()}\n".encode())
        self.fd = fd
        return True

    def drop(self) -> None:
        if self.fd is not None:
            os.ftruncate(self.fd, 0)
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


def lock_pid(path: Path) -> int | None:
    try:
        m = re.match(r"pid=(\d+)", path.read_text())
    except OSError:
        return None
    return int(m.group(1)) if m else None


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def held(state: Path) -> int | None:
    """The holder's pid (0 when unrecorded) while beatd.lock is held, else None."""
    path = state / "beatd" / "beatd.lock"
    if not path.exists():
        return None
    fd = os.open(path, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
    except OSError:
        return lock_pid(path) or 0
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return None
    finally:
        os.close(fd)


# ---------------------------------------------------------------- real git

def is_shim(path: str) -> bool:
    try:
        with open(path, errors="replace") as f:
            f.readline()
            return f.readline().rstrip("\n") == MARKER
    except OSError:
        return False


def resolve_git(path_var: str) -> str:
    """The first `git` on path_var, canonicalised, or Refuse (none, a shim, not git)."""
    for d in path_var.split(os.pathsep):
        c = os.path.join(d or ".", "git")
        if os.path.isfile(c) and os.access(c, os.X_OK):
            real = os.path.join(os.path.realpath(d or "."), "git")
            break
    else:
        raise Refuse("no git on PATH")
    if is_shim(real):
        raise Refuse(f"the first git on PATH is a shim ({real}); "
                     "run the beat with the real git's directory first")
    try:
        out = subprocess.run([real, "--version"], capture_output=True, text=True,
                             timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Refuse(f"{real} --version failed: {e}") from None
    if not out.startswith("git version"):
        raise Refuse(f"{real} does not answer --version with 'git version'")
    return real


# ---------------------------------------------------------------- the beat

def kill_group(pgid: int, at: float) -> None:
    """SIGKILL process group pgid at `at`, unless it empties first. A timed-out
    job whose leader exits on SIGTERM can leave a descendant that ignores it;
    the job lock must not drop while that descendant runs."""
    try:
        while time.time() < at:
            os.killpg(pgid, 0)
            time.sleep(0.1)
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:  # the group is empty
        pass


def next_start(kind: str, prev: float, start: float, end: float, interval_s: float) -> float:
    """A periodic job's next start is on its grid (prev, or this start when it
    ran late); a watch job restarts interval_s after its instance ends."""
    return (end if kind == "watch" else max(prev, start)) + interval_s


class Beat:
    def __init__(self, state: Path, table: dict, repo: Path, real_git: str):
        self.dir = state / "beatd"
        self.state, self.table, self.repo, self.git = state, table, repo, real_git
        self.jlock = threading.Lock()
        self.stop = threading.Event()
        self.procs: dict[str, subprocess.Popen] = {}

    def journal(self, line: str) -> None:
        with self.jlock, open(self.dir / "journal.log", "a") as f:
            f.write(line + "\n")

    def env(self, job: dict) -> dict:
        e = {k: os.environ[k] for k in (*BASE_ENV, *job["env_pass"]) if k in os.environ}
        e.update(HPO_BEATD_JOB=job["name"], HPO_REAL_GIT=self.git,
                 HPO_GIT_SHIM_LOG=str(self.dir / "git-retry.log"),
                 GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.filesRefLockTimeout",
                 GIT_CONFIG_VALUE_0="30000",
                 PATH=os.pathsep.join([str(SHIMS), os.environ.get("PATH", "")]))
        return e

    def argv(self, job: dict) -> list[str]:
        a = [x.replace("$S", str(self.state)) for x in job["argv"]]
        if "/" in a[0] and not os.path.isabs(a[0]):
            a[0] = str(self.repo / a[0])
        return a

    def run_one(self, job: dict) -> None:
        name, t0 = job["name"], time.time()
        rc, outcome = -1, "ok"
        jl = Lock(self.dir / f"{name}.lock")
        cl = Lock(self.dir / f"{job['class']}.lock") if job["class"] else None
        if not jl.take():
            outcome = "locked"
        elif cl and not cl.take(self.table["class_wait_s"]):
            outcome = "busy"
        else:
            rc, outcome = self.supervise(job, t0)
        if cl:
            cl.drop()
        jl.drop()
        self.journal(f"PASS {utc()} {name} start={utc(t0)} dur={int(time.time() - t0)} "
                     f"rc={rc} outcome={outcome}")

    def supervise(self, job: dict, t0: float) -> tuple[int, str]:
        cwd = str(self.repo) if job["cwd"] == "orch" else job["cwd"]
        with open(self.dir / f"{job['name']}.out", "ab") as out:
            try:
                p = subprocess.Popen(self.argv(job), cwd=cwd, env=self.env(job),
                                     stdin=subprocess.DEVNULL, stdout=out,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            except OSError:
                return -1, "unreadable"
            self.procs[job["name"]] = p
            hb = job["heartbeat_s"]
            beat = t0
            self.journal(f"RUNNING {utc()} {job['name']} pid={p.pid} elapsed=0")
            outcome, kill_at = None, None
            while p.poll() is None:
                now = time.time()
                if outcome is None and now - t0 >= job["timeout_s"]:
                    outcome, kill_at = "timeout", now + KILL_GRACE_S
                    os.killpg(p.pid, signal.SIGTERM)
                elif kill_at is not None and now >= kill_at:
                    os.killpg(p.pid, signal.SIGKILL)
                    kill_at = None
                elif hb and now - beat >= hb:
                    beat = now
                    self.journal(f"RUNNING {utc()} {job['name']} pid={p.pid} "
                                 f"elapsed={int(now - t0)}")
                time.sleep(0.1)
            if kill_at is not None:  # the leader exited inside the grace; the group may not have
                kill_group(p.pid, kill_at)
            self.procs.pop(job["name"], None)
        rc = p.returncode
        return rc, outcome or ("ok" if rc == 0 else "failed")

    def loop(self, job: dict, once: bool) -> None:
        nxt = time.time()
        while not self.stop.is_set():
            start = time.time()
            self.run_one(job)
            if once:
                return
            nxt = next_start(job["kind"], nxt, start, time.time(), job["interval_s"])
            self.stop.wait(max(0.0, nxt - time.time()))

    def code(self) -> str:
        r = subprocess.run([self.git, "-C", str(self.repo), "rev-parse", "HEAD"],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "unknown"

    def run(self, once: bool, for_s: float | None) -> int:
        sup = os.environ.get("HPO_BEATD_SUPERVISOR") or "none"
        self.journal(f"START {utc()} beatd pid={os.getpid()} code={self.code()} supervisor={sup}")
        threads = [threading.Thread(target=self.loop, args=(j, once), daemon=True)
                   for j in self.table["jobs"]]
        for t in threads:
            t.start()

        def term(*_):
            self.stop.set()
            for p in list(self.procs.values()):
                try:
                    os.killpg(p.pid, signal.SIGTERM)
                except OSError:
                    pass
        signal.signal(signal.SIGTERM, term)
        if for_s is not None:
            tm = threading.Timer(for_s, self.stop.set)
            tm.daemon = True
            tm.start()
        for t in threads:
            while t.is_alive():
                t.join(0.2)
        self.journal(f"STOP {utc()} beatd pid={os.getpid()}")
        return 0


def cmd_run(a) -> int:
    state = Path(a.state)
    table = load_table(Path(a.jobs))
    real = resolve_git(os.environ.get("PATH", ""))
    d = state / "beatd"
    d.mkdir(parents=True, exist_ok=True)
    inst = Lock(d / "beatd.lock")
    if not inst.take(wait_s=0.6):
        print(f"beatd: ALREADY RUNNING pid={lock_pid(d / 'beatd.lock')}", file=sys.stderr)
        return 75
    try:
        return Beat(state, table, Path(a.repo).resolve(), real).run(a.once, a.for_s)
    finally:
        inst.drop()


# ---------------------------------------------------------------- status

def read_journal(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    for i, ln in enumerate(lines, 1):
        if not LINE_RE.match(ln):
            raise Refuse(f"journal line {i} unreadable: {ln[:80]!r}")
    return lines


def status(state: Path, table: dict, repo: Path, pulse: Path, now: float,
           git: str = "git") -> tuple[int, list[str]]:
    d = state / "beatd"
    lines = read_journal(d / "journal.log")
    out, alarms = [], 0
    start, code = None, None
    last: dict[str, tuple[float, str]] = {}
    running: dict[str, int] = {}
    for ln in lines:
        f = ln.split()
        if f[0] == "START":
            start, code = parse_utc(f[1]), f[4].split("=", 1)[1]
            running.clear()
        elif f[0] == "RUNNING":
            running[f[2]] = int(f[3].split("=", 1)[1])
        elif f[0] == "PASS":
            last[f[2]] = (parse_utc(f[1]), f[-1].split("=", 1)[1])
            running.pop(f[2], None)
    pid = held(state)
    if pid is None:
        running.clear()  # no beat: a RUNNING line with no PASS is a dead instance
    for j in table["jobs"]:
        n = j["name"]
        t, outcome = last.get(n, (start, "none"))
        age = int(now - t) if t is not None else -1
        if n in running:
            st = "running"
        elif j["kind"] == "watch":
            st = "idle"
        elif t is None or age > j["interval_s"] + j["timeout_s"]:
            st = "late"
        else:
            st = "ok" if outcome in ("ok", "none") else outcome
        if st == "idle" and outcome not in ("ok", "none"):
            st = outcome
        if st not in ("ok", "running", "idle"):
            alarms += 1
        out.append(f"JOB {n} {st} age={age} last={outcome}")
    if pid is None:
        out.append("DOWN beatd.lock is free" + (f" (last START {utc(start)})" if start else ""))
        alarms += 1
    for lk in sorted(d.glob("*.lock")) if d.is_dir() else []:
        p = lock_pid(lk)
        if p is not None and not pid_alive(p):
            out.append(f"ALERT lock-owner-dead {lk.name} pid={p}")
            alarms += 1
    if pulse.exists():
        for ln in pulse.read_text().splitlines():
            if re.match(r"^PULSE \S+ STOPPED\b", ln):
                out.append(f"ALERT pulse-silent {ln}")
                alarms += 1
    else:
        out.append("pulse=none")
    rc = 0
    if code and code != "unknown":
        r = subprocess.run([git, "-C", str(repo), "rev-list", "--count", f"{code}..origin/main"],
                           capture_output=True, text=True)
        if r.returncode or not r.stdout.strip().isdigit():
            out.append(f"UNREADABLE code-staleness {(r.stderr or r.stdout).strip()[-80:]}")
            rc = 2
        elif int(r.stdout) > 0:
            out.append(f"STALE-CODE behind={int(r.stdout)} code={code[:12]}")
            alarms += 1
    out.append(f"beatd status: {len(table['jobs'])} jobs, {alarms} alarms at {utc(now)}")
    return rc or (1 if alarms else 0), out


def cmd_status(a) -> int:
    state = Path(a.state)
    pulse = Path(a.pulse) if a.pulse else state / "beatd" / "pulse.txt"
    rc, out = status(state, load_table(Path(a.jobs)), Path(a.repo), pulse,
                     float(a.now) if a.now is not None else time.time())
    print("\n".join(out))
    return rc


def cmd_held(a) -> int:
    pid = held(Path(a.state))
    print("free" if pid is None else f"held pid={pid}")
    return 1 if pid is None else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:  # [case ...] [--no-mutants] narrow it, for a seat
        rest = [x for x in argv[1:] if x != "--no-mutants"]
        return self_test(rest or None, "--no-mutants" not in argv)
    ap = argparse.ArgumentParser(prog="beatd.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "status", "held"):
        p = sub.add_parser(name)
        p.add_argument("--state", required=True)
        if name != "held":
            p.add_argument("--jobs", default=str(Path(__file__).with_name("beatd.jobs.json")))
            p.add_argument("--repo", default=str(ROOT))
    r = sub.choices["run"]
    g = r.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true")
    g.add_argument("--for", dest="for_s", type=float)
    s = sub.choices["status"]
    s.add_argument("--pulse")
    s.add_argument("--now", type=float)
    a = ap.parse_args(argv)
    try:
        return {"run": cmd_run, "status": cmd_status, "held": cmd_held}[a.cmd](a)
    except Refuse as e:
        print(f"beatd: REFUSE {e}", file=sys.stderr)
        return 2


# ---------------------------------------------------------------- self-test
# Every fixture is a temp directory; bash fixtures run under /bin/bash (3.2 on
# macOS: no bash-4 construct, no empty-array expansion under set -u). Each case
# has a null control, and MUTANTS below plants one predicate change per case in
# a temp copy and asserts that case goes red on it.

SELF = Path(__file__).resolve()
MUTANT_WORKERS = 4
SHIM = SHIMS / "git"
SELFTEST_MARK = "# " + "-" * 64 + " self-test"


def _job(name, argv, **kw):
    j = {"name": name, "argv": argv, "cwd": "orch", "interval_s": 3600, "timeout_s": 60,
         "heartbeat_s": None, "env_pass": [], "class": None, "kind": "periodic"}
    j.update(kw)
    return j


def _table(w: Path, jobs, **top) -> Path:
    p = w / f"jobs{len(list(w.glob('jobs*.json')))}.json"
    p.write_text(json.dumps({"version": 1, **top, "jobs": jobs}))
    return p


def _beat(prog: Path, *args, env=None, timeout=120) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(prog), *map(str, args)],
                          capture_output=True, text=True, env=env, timeout=timeout)


def _jr(state: Path) -> list[str]:
    p = state / "beatd" / "journal.log"
    return p.read_text().splitlines() if p.exists() else []


def _passes(state: Path, job: str) -> list[str]:
    return [x for x in _jr(state) if x.startswith("PASS ") and x.split()[2] == job]


def case1(prog, w):
    """(a)1 a malformed table runs zero jobs; null: the well-formed one runs it."""
    mark = w / "ran"
    good = _job("touch", ["/usr/bin/touch", str(mark)])
    res = {}
    other = {**good, "name": "other"}
    for label, bad in (("unknown key", {**other, "extra": 1}),
                       ("missing key", {k: v for k, v in other.items() if k != "kind"}),
                       ("watch under 60 s", {**other, "kind": "watch", "interval_s": 30})):
        s = w / f"s1-{label.replace(' ', '')}"
        r = _beat(prog, "run", "--state", s, "--jobs", _table(w, [good, bad]), "--once")
        res[label] = (r.returncode == 2 and "beatd: REFUSE" in r.stderr
                      and not mark.exists() and not _jr(s))
    s = w / "s1-unreadable"
    (w / "garbage.json").write_text("{")
    r = _beat(prog, "run", "--state", s, "--jobs", w / "garbage.json", "--once")
    res["unreadable"] = r.returncode == 2 and "REFUSE" in r.stderr and not mark.exists()
    r = _beat(prog, "run", "--state", w / "s1-null", "--jobs", _table(w, [good]), "--once")
    res["null: good table runs"] = r.returncode == 0 and mark.exists()
    return res


def case2(prog, w):
    """(a)2 a second run exits 75; null: after the first ends, a run gets the lock."""
    s = w / "s2"
    t = _table(w, [_job("sleep", ["/bin/sleep", "4"])])
    first = subprocess.Popen([sys.executable, "-I", str(prog), "run", "--state", str(s),
                              "--jobs", str(t), "--once"], umask=0o022,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for _ in range(100):
        if any(x.startswith("RUNNING") for x in _jr(s)):
            break
        time.sleep(0.1)
    held_rc = _beat(prog, "held", "--state", s).returncode
    second = _beat(prog, "run", "--state", s, "--jobs", t, "--once")
    first.wait(60)
    modes = [(s / "beatd" / f).stat().st_mode & 0o777 if (s / "beatd" / f).exists() else None
             for f in ("beatd.lock", "sleep.lock")]
    third = _beat(prog, "run", "--state", s, "--jobs", _table(w, [_job("t", ["/usr/bin/true"])]),
                  "--once")
    res = {"second run exits 75": second.returncode == 75 and "ALREADY RUNNING" in second.stderr,
           "held reads 0 while it runs": held_rc == 0,
           "lock files are owner-only under umask 022": modes == [0o600, 0o600],
           "null: a run after the first exits 0": first.returncode == 0 and third.returncode == 0}
    return {**res, **_case2_term(prog, w)}


def _case2_term(prog, w):
    """SIGTERM to a scheduling beat TERMs its running group and stops it: rc 0, the
    job's PASS, then STOP. Null: the job was running, unfinished, when the signal went."""
    s = w / "s2-term"
    t = _table(w, [_job("long", ["/bin/sleep", "300"], timeout_s=600)])
    beat = subprocess.Popen([sys.executable, "-I", str(prog), "run", "--state", str(s),
                             "--jobs", str(t)], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    for _ in range(200):
        if any(x.startswith("RUNNING") for x in _jr(s)):
            break
        time.sleep(0.1)
    mid = _jr(s)
    beat.send_signal(signal.SIGTERM)
    try:
        rc = beat.wait(20)
    except subprocess.TimeoutExpired:
        beat.kill()
        rc = None
    for ln in _jr(s):
        if ln.startswith("RUNNING "):
            try:
                os.killpg(int(ln.split()[3].split("=", 1)[1]), signal.SIGKILL)
            except OSError:
                pass
    jr, lp = _jr(s), _passes(s, "long")
    return {"SIGTERM stops the beat and TERMs its job: rc 0, PASS rc=-15, STOP":
            rc == 0 and len(lp) == 1 and lp[0].endswith("rc=-15 outcome=failed")
            and jr[-1].startswith("STOP "),
            "null: the job was running when the beat got SIGTERM":
            any(x.startswith("RUNNING ") for x in mid) and not _passes_in(mid, "long")}


def _passes_in(lines: list[str], job: str) -> list[str]:
    return [x for x in lines if x.startswith("PASS ") and x.split()[2] == job]


def _zombie(pid: int) -> bool:
    """Killed but unreaped: a container whose pid 1 reaps no orphans keeps it (Linux /proc)."""
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] == "Z"
    except (OSError, IndexError):
        return False


def _gone(pidf: Path) -> bool:
    """The pid in pidf is dead (or a zombie); a survivor is killed here, after the read."""
    time.sleep(0.5)
    gc = int(pidf.read_text()) if pidf.exists() else None
    gone = gc is not None and (not pid_alive(gc) or _zombie(gc))
    if gc and not gone:
        os.kill(gc, signal.SIGKILL)
    return gone


def _stubborn(prog, w, label: str, leader_ignores: bool) -> tuple[bool, bool, list[str]]:
    """A timed-out job whose grandchild ignores SIGTERM; its leader too when leader_ignores.
    Returns (one PASS outcome=timeout, the grandchild gone when the beat returned, PASS lines)."""
    import shlex
    s, pf = w / f"s3-{label}", w / f"{label}.pid"
    inner = f"trap '' TERM; echo $$ > {pf}; exec sleep 300"
    outer = ("trap '' TERM; " if leader_ignores else "") + f"bash -c {shlex.quote(inner)} & wait"
    try:
        r = _beat(prog, "run", "--state", s, "--jobs",
                  _table(w, [_job(label, ["/bin/bash", "-c", outer], timeout_s=2)]),
                  "--once", timeout=40)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = None
    gone = _gone(pf)
    for ln in _jr(s):
        if ln.startswith("RUNNING "):
            try:
                os.killpg(int(ln.split()[3].split("=", 1)[1]), signal.SIGKILL)
            except OSError:
                pass
    p = _passes(s, label)
    return rc == 0 and len(p) == 1 and p[0].endswith("outcome=timeout"), gone, p


def case3(prog, w):
    """(a)3 over-time reads timeout and its group is gone; in-time reads ok; a heartbeat
    job journals RUNNING past elapsed=0 (null: one with none journals RUNNING once).
    A grandchild ignoring SIGTERM is SIGKILLed after the grace although its leader
    exited on the TERM, before the beat moves on; null: a leader ignoring it too."""
    import shlex
    s = w / "s3"
    pidf, mark = w / "grandchild.pid", w / "termed"
    trapper = f"trap 'echo TERM > {mark}; exit 0' TERM; sleep 300 & wait"
    slow = _job("slow", ["/bin/bash", "-c", f"sleep 300 & echo $! > {pidf}; "
                         f"bash -c {shlex.quote(trapper)} & wait"], timeout_s=2, heartbeat_s=1)
    fast = _job("fast", ["/bin/sleep", "0"], timeout_s=30)
    r = _beat(prog, "run", "--state", s, "--jobs", _table(w, [slow, fast]), "--once", timeout=60)
    gone = _gone(pidf)
    sp = _passes(s, "slow")
    fp = _passes(s, "fast")
    beats = [x for x in _jr(s) if x.startswith("RUNNING ") and x.split()[2] == "slow"]
    st_ok, st_gone, _ = _stubborn(prog, w, "stubborn", leader_ignores=False)
    nl_ok, nl_gone, nl_p = _stubborn(prog, w, "both", leader_ignores=True)
    st_beats = [x for x in _jr(w / "s3-stubborn") if x.startswith("RUNNING ")]
    return {"over-time job reads timeout": r.returncode == 0 and len(sp) == 1
            and sp[0].endswith("outcome=timeout"),
            "its process group was killed": gone,
            "its process group took SIGTERM before any SIGKILL": mark.exists(),
            "null: in-time job reads ok": len(fp) == 1 and fp[0].endswith("outcome=ok"),
            "a heartbeat job journals RUNNING past elapsed=0":
            any(int(x.rsplit("=", 1)[1]) >= 1 for x in beats),
            "null: a job with no heartbeat journals RUNNING once": len(st_beats) == 1,
            "a TERM-ignoring grandchild is killed after its leader exits": st_ok and st_gone,
            "null: a leader ignoring TERM too is killed at the grace, rc -9":
            nl_ok and nl_gone and "rc=-9 " in nl_p[0]}


def case4(prog, w):
    """(a)4 a slow job does not delay a fast one; null: the fast job alone runs as often."""
    s = w / "s4"
    t = _table(w, [_job("slow", ["/bin/sleep", "5"], interval_s=1),
                   _job("fast", ["/usr/bin/true"], interval_s=1)])
    def run(state, table):
        try:
            return _beat(prog, "run", "--state", state, "--jobs", table, "--for", "4",
                         timeout=30).returncode
        except subprocess.TimeoutExpired:  # a beat that never stops scheduling
            return None
    rc = run(s, t)
    fast, slow = _passes(s, "fast"), _passes(s, "slow")
    s0 = w / "s4-null"
    run(s0, _table(w, [_job("fast", ["/usr/bin/true"], interval_s=1)]))
    alone = _passes(s0, "fast")
    first_slow = parse_utc(slow[0].split()[1]) if slow else 0.0
    before = [x for x in fast if parse_utc(x.split()[1]) < first_slow]
    sched = _load(prog).next_start
    return {"fast passes while slow runs": rc == 0 and len(slow) == 1 and len(before) >= 3,
            "null: fast alone passes as often": len(alone) >= 3,
            # a watch job's interval_s is >= 60, past a fixture's budget: the rule, not a run
            "a watch job restarts interval_s after its instance ends":
            sched("watch", 160.0, 100.0, 130.0, 60) == 190.0,
            "null: a periodic job keeps its grid, or restarts from a late start":
            sched("periodic", 160.0, 100.0, 130.0, 60) == 220.0
            and sched("periodic", 100.0, 150.0, 170.0, 60) == 210.0}


def _load(prog: Path):
    """The beatd module at prog (the tree under test, a mutant copy included)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"beatd_under_test_{os.getpid()}", prog)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case5(prog, w):
    """(a)5 class jobs never interleave; a third past class_wait_s is busy.
    Null: the same two jobs with no class do overlap."""
    def pair(cls, label, wait=60, third=False):
        s = w / f"s5-{label}"
        log = w / f"{label}.log"
        body = f'echo "start $HPO_BEATD_JOB" >> {log}; sleep 2; echo "end $HPO_BEATD_JOB" >> {log}'
        jobs = [_job(n, ["/bin/bash", "-c", body], **{"class": cls}) for n in ("one", "two")]
        if third:
            jobs.append(_job("three", ["/bin/bash", "-c", body], **{"class": cls}))
        _beat(prog, "run", "--state", s, "--jobs", _table(w, jobs, class_wait_s=wait), "--once")
        ev = log.read_text().split("\n") if log.exists() else []
        return s, [x for x in ev if x]
    _, ev = pair("orch-checkout", "class")
    serial = len(ev) == 4 and ev[0].split()[0] == "start" and ev[1].split()[0] == "end" \
        and ev[0].split()[1] == ev[1].split()[1]
    _, ev0 = pair(None, "noclass")
    overlap = len(ev0) == 4 and [x.split()[0] for x in ev0[:2]] == ["start", "start"]
    s3, _ = pair("orch-checkout", "busy", wait=1, third=True)
    busy = [x for x in _jr(s3) if x.startswith("PASS ") and x.endswith("outcome=busy")]
    return {"class jobs never interleave": serial,
            "null: class-less jobs overlap": overlap,
            "past class_wait_s records busy": len(busy) == 2}


RACE = r'''
set -u
W=$1; SHIMDIR=$2; MODE=$3
cd "$W"
( SLOW=1 git -C c fetch -q origin ) & sleep 1
p=$PATH; [ "$MODE" = noshim ] || p=$SHIMDIR:$PATH
if [ "$MODE" = child ]; then
  env PATH="$p" bash -c 'git -C c fetch -q origin' 2>"$W/err"; rc=$?
else
  env PATH="$p" git -C c fetch -q origin 2>"$W/err"; rc=$?
fi
wait
echo "rc=$rc same=$([ "$(git -C c rev-parse origin/main)" = "$(git -C up rev-parse main)" ] && echo 1 || echo 0) err=$(grep -c 'cannot lock ref' "$W/err")"
'''


def _shim_env(w: Path, retries="2") -> dict:
    """The beat's job env for a git child, as Beat.env builds it (no PATH: the fixture sets it)."""
    real = resolve_git(os.environ.get("PATH", ""))
    e = {k: v for k, v in os.environ.items() if k in BASE_ENV}
    e.update(PATH=os.environ.get("PATH", ""), HPO_REAL_GIT=real,
             HPO_GIT_SHIM_LOG=str(w / "retry.log"), HPO_GIT_RETRIES=retries,
             GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.filesRefLockTimeout",
             GIT_CONFIG_VALUE_0="30000")
    return e


def _race_repos(w: Path) -> str:
    """up and its clone c under w, built by tests/throwaway_git.py; c's
    reference-transaction hook holds the ref lock 3 s when SLOW is set; up is
    one commit ahead. Returns the real git."""
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_clone, throwaway_git_init
    real = resolve_git(os.environ.get("PATH", ""))
    w.mkdir(parents=True, exist_ok=True)
    env = throwaway_git_init(w / "up", "-q", "-b", "main", git=(real,))
    commit = [real, "commit", "-q", "--allow-empty", "-m"]
    subprocess.run([*commit, "a"], cwd=w / "up", env=env, check=True, capture_output=True)
    throwaway_git_clone(w / "up", w / "c", "-q", git=(real,))
    hook = w / "c" / ".git" / "hooks" / "reference-transaction"
    hook.write_text('#!/bin/sh\n[ "$1" = prepared ] && [ -n "${SLOW:-}" ] && sleep 3\nexit 0\n')
    hook.chmod(0o755)
    subprocess.run([*commit, "r"], cwd=w / "up", env=env, check=True, capture_output=True)
    return real


def _race(w: Path, shimdir: Path, mode: str, retries="2") -> dict:
    _race_repos(w)
    r = subprocess.run(["/bin/bash", "-c", RACE, "race", str(w), str(shimdir), mode],
                       capture_output=True, text=True, env=_shim_env(w, retries), timeout=120)
    m = re.search(r"rc=(\d+) same=(\d) err=(\d+)", r.stdout)
    log = w / "retry.log"
    return {"rc": int(m.group(1)) if m else -1, "same": m and m.group(2) == "1",
            "err": int(m.group(3)) if m else -1,
            "retries": len(log.read_text().splitlines()) if log.exists() else 0}


DISCOVERY = r'''
set -u
W=$1; SHIM=$2; REALDIR=$3
mkdir -p "$W/a/tools/audit/seat/beatd_shims" "$W/b" "$W/empty" "$W/rg" "$W/fake"
cp "$SHIM" "$W/a/tools/audit/seat/beatd_shims/git"; cp "$SHIM" "$W/b/git"
printf '#!/bin/sh\necho not-git\n' > "$W/fake/git"; chmod +x "$W/fake/git"
cd "$W/a"
bound() { "$@" & p=$!; ( /bin/sleep 5; kill -9 $p 2>/dev/null ) & k=$!; wait $p; r=$?; kill $k 2>/dev/null; wait $k 2>/dev/null; [ $r = 137 ] && r=124; return $r; }
run() { out=$(PATH="$2" HPO_REAL_GIT="${3:-}" bound git --version 2>&1); r=$?; echo "$1|$r|${out%%$'\n'*}"; }
S=$W/a/tools/audit/seat/beatd_shims; B=$REALDIR:/usr/bin:/bin
run absolute             "$S:$B"
run relative             "tools/audit/seat/beatd_shims:$B"
run trailing-slash       "$S/:$B"
run two-copies           "$S:$W/b:$B"
run duplicate            "$S:$S:$B"
run real-git-is-shim     "$S:$B" "$W/b/git"
run real-git-is-dir      "$S:$B" "$W/empty"
run no-real-git          "$S:$W/b:$W/empty"
'''


def _discovery(w: Path, shim: Path) -> dict:
    w.mkdir(parents=True, exist_ok=True)
    real = resolve_git(os.environ.get("PATH", ""))
    r = subprocess.run(["/bin/bash", "-c", DISCOVERY, "disc", str(w), str(shim),
                        os.path.dirname(real)], capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if k in BASE_ENV}, timeout=120)
    out = {}
    for ln in r.stdout.splitlines():
        name, rc, text = (ln.split("|", 2) + ["", ""])[:3]
        out[name] = (int(rc), text)
    return out


def case6(prog, w, shim=SHIM):
    """(a)6 the two-fetcher race, discovery, and the beat's own git refusals."""
    sd = shim.parent
    res = {}
    fx = _race(w / "r-fix", sd, "shim")
    res["race: B through the shim exits 0, origin/main current, a retry logged"] = (
        fx["rc"] == 0 and fx["same"] and fx["retries"] >= 1)
    nl = _race(w / "r-null", sd, "noshim")
    res["null: B with no shim exits 1 with cannot lock ref"] = nl["rc"] == 1 and nl["err"] >= 1
    ch = _race(w / "r-child", sd, "child")
    res["race through a child inherits the shim"] = ch["rc"] == 0 and ch["retries"] >= 1
    e = _shim_env(w / "plain")
    (w / "plain").mkdir()
    e["PATH"] = f"{sd}:{e['PATH']}"
    st = subprocess.run(["git", "-C", str(ROOT), "status", "--short"], env=e,
                        capture_output=True, text=True)
    res["git status through the shim logs no retry"] = (
        st.returncode == 0 and not (w / "plain" / "retry.log").exists())
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    throwaway_git_init(w / "plain", "-q")
    fe = subprocess.run(["git", "-C", str(w / "plain"), "fetch", "nowhere"], env=e,
                        capture_output=True, text=True)
    res["a missing remote fails once, git's message, no retry"] = (
        fe.returncode != 0 and "nowhere" in fe.stderr
        and not (w / "plain" / "retry.log").exists())
    d = _discovery(w / "disc", shim)
    for c in ("absolute", "relative", "trailing-slash", "two-copies", "duplicate",
              "real-git-is-shim", "real-git-is-dir"):
        rc, text = d.get(c, (-1, ""))
        res[f"discovery {c}: rc 0 within 5 s"] = rc == 0 and text.startswith("git version")
    rc, text = d.get("no-real-git", (-1, ""))
    res["discovery no-real-git: rc 127, one line"] = (
        rc == 127 and text == "git shim: no real git on PATH")
    t = _table(w, [_job("t", ["/usr/bin/true"])])
    for label, path in (("a shim", f"{w / 'disc' / 'b'}:{os.environ.get('PATH', '')}"),
                        ("not git", f"{w / 'disc' / 'fake'}:{os.environ.get('PATH', '')}"),
                        ("no git", "/nonexistent")):
        r = _beat(prog, "run", "--state", w / f"s6-{label.replace(' ', '')}", "--jobs", t,
                  "--once", env=dict(os.environ, PATH=path))
        res[f"beatd refuses rc 2 when its git is {label}"] = (
            r.returncode == 2 and "REFUSE" in r.stderr)
    r = _beat(prog, "run", "--state", w / "s6-null", "--jobs", t, "--once")
    res["null: beatd with the real git first runs"] = r.returncode == 0
    return res


def case6_beat(prog, w):
    """(a)6 through the beat itself: B as a beat job retries; its env carries the shim."""
    s = w / "s6b"
    rw = w / "r-beat"
    real = g = _race_repos(rw)
    a = subprocess.Popen(["/bin/bash", "-c", f"SLOW=1 {g} -C {rw}/c fetch -q origin"],
                         stderr=subprocess.DEVNULL)
    time.sleep(1)
    t = _table(w, [_job("fetch", ["/bin/bash", "-c",
                                  f'env > {rw}/env; git -C {rw}/c fetch -q origin'],
                        timeout_s=60)])
    r = _beat(prog, "run", "--state", s, "--jobs", t, "--once")
    a.wait(60)
    p = _passes(s, "fetch")
    log = s / "beatd" / "git-retry.log"
    envs = (rw / "env").read_text() if (rw / "env").exists() else ""
    return {"beat job B exits ok through the shim": r.returncode == 0 and len(p) == 1
            and p[0].endswith("outcome=ok"),
            "beat job's retry lands in S/beatd/git-retry.log": log.exists()
            and len(log.read_text().splitlines()) >= 1,
            "job env: HPO_BEATD_JOB, HPO_REAL_GIT, shim first": "HPO_BEATD_JOB=fetch" in envs
            and f"HPO_REAL_GIT={real}" in envs and f"PATH={SHIMS}" in envs}


def case7(prog, w):
    """(a)7 status: each alarm against a fixture; null: a healthy fixture has none."""
    real = resolve_git(os.environ.get("PATH", ""))
    repo = w / "repo7"
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    env = throwaway_git_init(repo, "-q", "-b", "main", git=(real,))
    # every call under the throwaway env: commit-tree needs its identity on a runner with none
    g = lambda *a: subprocess.run([real, "-C", str(repo), *a], check=True, env=env,
                                  capture_output=True, text=True).stdout.strip()
    subprocess.run([real, "commit", "-q", "--allow-empty", "-m", "a"], cwd=repo, env=env,
                   check=True, capture_output=True)
    old = g("rev-parse", "HEAD")
    g("update-ref", "refs/remotes/origin/main", old)
    now = 1_800_000_000.0
    jobs = [_job("p", ["/usr/bin/true"], interval_s=300, timeout_s=60),
            _job("w", ["/usr/bin/true"], interval_s=300, timeout_s=60, kind="watch")]
    tbl = _table(w, jobs)

    def fixture(label, lines, hold=True, lock=None, pulse=None, head=old):
        s = w / f"s7-{label}"
        (s / "beatd").mkdir(parents=True)
        (s / "beatd" / "journal.log").write_text("".join(x + "\n" for x in lines))
        g("update-ref", "refs/remotes/origin/main", head)
        holder = None
        if hold:
            holder = Lock(s / "beatd" / "beatd.lock")
            holder.take()
        if lock:
            (s / "beatd" / "p.lock").write_text(f"pid={lock}\n")
        if pulse:
            (s / "beatd" / "pulse.txt").write_text(pulse)
        r = _beat(prog, "status", "--state", s, "--jobs", tbl, "--repo", repo, "--now", now,
                  env=dict(os.environ, PATH=f"{os.path.dirname(real)}:{os.environ.get('PATH', '')}"))
        if holder:
            holder.drop()
        return r.returncode, r.stdout + r.stderr
    st = f"START {utc(now - 1000)} beatd pid=1 code={old} supervisor=none"
    ok_p = f"PASS {utc(now - 100)} p start={utc(now - 101)} dur=1 rc=0 outcome=ok"
    ok_w = f"PASS {utc(now - 100)} w start={utc(now - 101)} dur=1 rc=0 outcome=ok"
    dead = subprocess.Popen(["/usr/bin/true"])
    dead.wait()
    new = g("commit-tree", "-p", old, "-m", "b", g("rev-parse", "HEAD^{tree}"))
    res = {}
    rc, out = fixture("healthy", [st, ok_p, ok_w])
    res["null: healthy prints no alarm, rc 0"] = (
        rc == 0 and not re.search(r"late|DOWN|busy|ALERT|STALE", out) and "JOB w idle" in out)
    late = f"PASS {utc(now - 361)} p start={utc(now - 362)} dur=1 rc=0 outcome=ok"
    rc, out = fixture("late", [st, late, ok_w])
    res["late past interval + timeout"] = rc == 1 and "JOB p late" in out
    inwin = f"PASS {utc(now - 330)} p start={utc(now - 331)} dur=1 rc=0 outcome=ok"
    rc, out = fixture("inwindow", [st, inwin, ok_w])
    res["null: past interval, inside interval + timeout, is not late"] = rc == 0 and "JOB p ok" in out
    rc, out = fixture("down", [st, ok_p, ok_w], hold=False)
    res["DOWN when beatd.lock is free"] = rc == 1 and "DOWN" in out
    busy = f"PASS {utc(now - 100)} p start={utc(now - 160)} dur=60 rc=-1 outcome=busy"
    rc, out = fixture("busy", [st, busy, ok_w])
    res["busy last outcome alarms"] = rc == 1 and "JOB p busy" in out
    run_w = f"RUNNING {utc(now - 50)} w pid=1 elapsed=0"
    rc, out = fixture("watchrun", [st, ok_p, run_w])
    res["null: a running watch job is not idle"] = rc == 0 and "JOB w running" in out
    rc, out = fixture("deadowner", [st, ok_p, ok_w], lock=dead.pid)
    res["lock-owner-dead for a dead pid"] = rc == 1 and f"ALERT lock-owner-dead p.lock pid={dead.pid}" in out
    rc, out = fixture("liveowner", [st, ok_p, ok_w], lock=os.getpid())
    res["null: a live owner is no alarm"] = rc == 0 and "ALERT" not in out
    rc, out = fixture("pulse", [st, ok_p, ok_w],
                      pulse="PULSE opener ok\nPULSE verdict STOPPED seat merge: 3h\n")
    res["pulse-silent while beatd reads healthy"] = (
        rc == 1 and "ALERT pulse-silent PULSE verdict STOPPED" in out and "JOB p ok" in out)
    rc, out = fixture("pulseok", [st, ok_p, ok_w], pulse="PULSE opener ok\n")
    res["null: a pulse with nothing stopped is no alarm"] = rc == 0 and "ALERT" not in out
    rc, out = fixture("stale", [st, ok_p, ok_w], head=new)
    res["STALE-CODE behind=1"] = rc == 1 and "STALE-CODE behind=1" in out
    st_bad = f"START {utc(now - 1000)} beatd pid=1 code={'0' * 39}1 supervisor=none"
    rc, out = fixture("staleunread", [st_bad, ok_p, ok_w])
    res["an unreadable staleness read is rc 2, never clean"] = (
        rc == 2 and "UNREADABLE code-staleness" in out)
    run_p = f"RUNNING {utc(now - 50)} p pid=1 elapsed=0"
    rc, out = fixture("deadrunning", [st, ok_w, run_p], hold=False)
    res["a RUNNING line with no PASS under a free beatd.lock is a dead instance"] = (
        rc == 1 and "JOB p late" in out)
    rc, out = fixture("liverunning", [st, ok_w, run_p])
    res["null: the same lines under a held beatd.lock read running"] = (
        rc == 0 and "JOB p running" in out)
    rc, out = fixture("badline", [st, "PASS garbage"])
    res["an unreadable journal line refuses rc 2"] = rc == 2 and "REFUSE journal line 2" in out
    return res


def case7_cli(prog, w):
    """(a)7 the status CLI over the case's own fixture rc (mutant-run path)."""
    s = w / "s7cli"
    (s / "beatd").mkdir(parents=True)
    now = time.time()
    (s / "beatd" / "journal.log").write_text(
        f"PASS {utc(now - 361)} p start={utc(now - 362)} dur=1 rc=0 outcome=ok\n")
    holder = Lock(s / "beatd" / "beatd.lock")
    holder.take()
    r = _beat(prog, "status", "--state", s, "--jobs",
              _table(w, [_job("p", ["/usr/bin/true"], interval_s=300, timeout_s=60)]),
              "--now", now)
    holder.drop()
    return {"status CLI: late job, rc 1": r.returncode == 1 and "JOB p late" in r.stdout}


def case8(prog, w):
    """(a)8 held rc 0 while beatd.lock is held, rc 1 when free."""
    s = w / "s8"
    (s / "beatd").mkdir(parents=True)
    free0 = _beat(prog, "held", "--state", s).returncode
    holder = Lock(s / "beatd" / "beatd.lock")
    holder.take()
    h = _beat(prog, "held", "--state", s)
    holder.drop()
    free1 = _beat(prog, "held", "--state", s).returncode
    return {"held: rc 0 while held": h.returncode == 0 and f"pid={os.getpid()}" in h.stdout,
            "null: rc 1 with no lock file": free0 == 1,
            "null: rc 1 after release": free1 == 1}


CASES = {"1": case1, "2": case2, "3": case3, "4": case4, "5": case5, "6": case6,
         "6b": case6_beat, "7": case7, "7c": case7_cli, "8": case8}

# One predicate change per case: (file, anchor, replacement, case, the check it must break).
MUTANTS = {
    "m1_parse_defaults_to_zero_jobs": (
        "beatd", '        raise Refuse(f"job table {path} unreadable: {e}") from None',
        '        doc = {"version": 1, "jobs": []}', "1", "unreadable"),
    "m1b_unknown_key_accepted": (
        "beatd", "if not isinstance(j, dict) or set(j) != KEYS:",
        "if not isinstance(j, dict) or not KEYS <= set(j):", "1", "unknown key"),
    "m2_no_instance_flock": (
        "beatd", "    if not inst.take(wait_s=0.6):", "    if not True:", "2",
        "second run exits 75"),
    "m2_lock_world_readable": (
        "beatd", "os.O_RDWR | os.O_CREAT, 0o600)", "os.O_RDWR | os.O_CREAT, 0o644)", "2",
        "lock files are owner-only under umask 022"),
    "m3_no_killpg": (
        "beatd", 'now + KILL_GRACE_S\n                    os.killpg(p.pid, signal.SIGTERM)',
        'now + KILL_GRACE_S\n                    p.terminate()', "3",
        "its process group took SIGTERM before any SIGKILL"),
    "m3_no_group_kill_after_leader": (
        "beatd", "                kill_group(p.pid, kill_at)\n", "                pass\n", "3",
        "a TERM-ignoring grandchild is killed after its leader exits"),
    "m3_kill_group_no_sigkill": (
        "beatd", "        os.killpg(pgid, signal.SIGKILL)\n", "        pass\n", "3",
        "a TERM-ignoring grandchild is killed after its leader exits"),
    "m3_no_sigkill_live_leader": (
        "beatd", "                    os.killpg(p.pid, signal.SIGKILL)\n", "                    pass\n",
        "3", "null: a leader ignoring TERM too is killed at the grace, rc -9"),
    "m3_no_heartbeat": (
        "beatd", "elif hb and now - beat >= hb:", "elif False:", "3",
        "a heartbeat job journals RUNNING past elapsed=0"),
    "m4_watch_as_periodic": (
        "beatd", '(end if kind == "watch" else max(prev, start))', "max(prev, start)", "4",
        "a watch job restarts interval_s after its instance ends"),
    "m2_sigterm_handler_off": (
        "beatd", "        signal.signal(signal.SIGTERM, term)", "        pass", "2",
        "SIGTERM stops the beat and TERMs its job: rc 0, PASS rc=-15, STOP"),
    "m4_serial_jobs": (
        "beatd", "        for t in threads:\n            t.start()",
        "        for t in threads:\n            t.start(); t.join()", "4",
        "fast passes while slow runs"),
    "m5_class_ignored": (
        "beatd", 'cl = Lock(self.dir / f"{job[\'class\']}.lock") if job["class"] else None',
        "cl = None", "5", "class jobs never interleave"),
    "m6_retries_zero": (
        "shim", "max=${HPO_GIT_RETRIES:-2}", "max=0", "6",
        "race: B through the shim exits 0, origin/main current, a retry logged"),
    "m6_no_shim_prepend": (
        "beatd", "PATH=os.pathsep.join([str(SHIMS), os.environ.get(\"PATH\", \"\")]))",
        "PATH=os.environ.get(\"PATH\", \"\"))", "6b", "beat job B exits ok through the shim"),
    "m6_drop_C_skip": (
        "shim", "-C|-c|--git-dir", "-c|--git-dir", "6",
        "race: B through the shim exits 0, origin/main current, a retry logged"),
    # round 3's rule (f0f046929 spike shims/git): skip only the entry spelled as its own dir
    "m6_string_compare": (
        "shim", '    if usable "$d/git"; then real=$(cd "$d" && pwd -P)/git; break; fi',
        '    if [ "$d" != "$(cd "$(dirname "$0")" && pwd)" ] && [ -x "$d/git" ]; then real=$d/git; break; fi',
        "6", "discovery relative: rc 0 within 5 s"),
    "m6_marker_via_head": (
        "shim", "is_shim() { local l1= l2=; { IFS= read -r l1; IFS= read -r l2; } < \"$1\" 2>/dev/null; [ \"$l2\" = '# hpo-git-shim' ]; }",
        "is_shim() { [ \"$(head -2 \"$1\" 2>/dev/null | tail -1)\" = '# hpo-git-shim' ]; }",
        "6", "discovery no-real-git: rc 127, one line"),
    "m6_real_git_dir_accepted": (
        "shim", 'usable() { [ -f "$1" ] && [ -x "$1" ]', 'usable() { [ -x "$1" ]', "6",
        "discovery real-git-is-dir: rc 0 within 5 s"),
    "m6_beatd_trusts_any_git": (
        "beatd", '    if not out.startswith("git version"):', "    if False:", "6",
        "beatd refuses rc 2 when its git is not git"),
    "m7_late_without_timeout": (
        "beatd", 'age > j["interval_s"] + j["timeout_s"]:', 'age > j["interval_s"]:', "7",
        "null: past interval, inside interval + timeout, is not late"),
    "m7_no_pulse_alarm": (
        "beatd", r'if re.match(r"^PULSE \S+ STOPPED\b", ln):', "if False:", "7",
        "pulse-silent while beatd reads healthy"),
    "m7_unreadable_staleness_clean": (
        "beatd", "            rc = 2\n", "            rc = 0\n", "7",
        "an unreadable staleness read is rc 2, never clean"),
    "m7_dead_running_kept": (
        "beatd", "        running.clear()  # no beat", "        pass  # no beat", "7",
        "a RUNNING line with no PASS under a free beatd.lock is a dead instance"),
    "m8_held_always_free": (
        "beatd", "        return lock_pid(path) or 0\n", "        return None\n", "8",
        "held: rc 0 while held"),
}


def _mutant_copy(w: Path, name: str) -> tuple[Path, Path]:
    """A temp tree holding beatd.py and beatd_shims/git with one plant applied."""
    f, anchor, repl = MUTANTS[name][:3]
    d = w / "tree" / "tools" / "audit" / "seat"
    (d / "beatd_shims").mkdir(parents=True)
    prog, shim = d / "beatd.py", d / "beatd_shims" / "git"
    btxt, stxt = SELF.read_text(), SHIM.read_text()
    if f == "beatd":
        btxt = btxt.replace(anchor, repl, 1)
    else:
        stxt = stxt.replace(anchor, repl, 1)
    prog.write_text(btxt)
    shim.write_text(stxt)
    shim.chmod(0o755)
    return prog, shim


def _run_case(case: str, prog: Path, shim: Path, w: Path) -> dict:
    fn = CASES[case]
    w.mkdir(parents=True, exist_ok=True)
    if case == "6":
        return fn(prog, w, shim)
    return fn(prog, w)


def self_test(only: list[str] | None = None, mutants: bool = True) -> int:
    import tempfile
    checks = fails = 0

    def check(name: str, ok: bool) -> None:
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
    names: dict[str, set] = {}
    for case in only or CASES:
        with tempfile.TemporaryDirectory(prefix="beatd-st-") as td:
            got = _run_case(case, SELF, SHIM, Path(td))
            names[case] = set(got)
            for k, ok in got.items():
                check(f"({case}) {k}", ok)
    for name, (f, anchor, repl, case, target) in MUTANTS.items():
        if case not in names:
            continue
        text = production(SELF.read_text()) if f == "beatd" else SHIM.read_text()
        check(f"anchor {name} occurs once in production, changes it, names a check of ({case})",
              text.count(anchor) == 1 and anchor != repl and target in names[case])
    if mutants:
        def plant(name: str) -> dict:
            case = MUTANTS[name][3]
            with tempfile.TemporaryDirectory(prefix="beatd-mu-") as td:
                prog, shim = _mutant_copy(Path(td), name)
                try:
                    return _run_case(case, prog, shim, Path(td) / "w")
                except Exception as e:  # a crash is no kill: its target reads unset
                    return {"crash": f"{type(e).__name__}: {str(e)[:80]}"}
        # The fixtures are sleep-bound, so the mutants run MUTANT_WORKERS at once
        # (instrument-self-tests' wall clock); each has its own temp tree and state.
        todo = [n for n, m in MUTANTS.items() if not only or m[3] in only]
        with ThreadPoolExecutor(MUTANT_WORKERS) as pool:
            results = dict(zip(todo, pool.map(plant, todo)))
        for name in todo:
            case, target, got = MUTANTS[name][3], MUTANTS[name][4], results[name]
            check(f"mutant {name} turns ({case}) '{target}' red"
                  + (f" [crash {got['crash']}]" if "crash" in got else ""),
                  got.get(target) is False)
    print(f"beatd self-test: {checks} checks, {fails} failed")
    return 1 if fails else 0


def production(text: str) -> str:
    """beatd.py above the self-test, where every plant must land."""
    return text.split(SELFTEST_MARK, 1)[0]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
