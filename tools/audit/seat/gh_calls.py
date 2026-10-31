#!/usr/bin/env python3
"""Reader for the gh call log the seat gh shim writes (P284).

    gh_calls.py --top [--since <utc>] [--limit N] [--log PATH]
    gh_calls.py --coverage [PID ...]
    gh_calls.py --self-test

--top ranks callers (the parent command) and endpoints (subcommand + target)
by call count, over $HPO_STATE_DIR/gh-calls.log and its rotated .1 (default
state root $HOME/.local/state/hpo). `--since` keeps lines whose UTC stamp is
not before it; a stamp is the shim's `YYYY-MM-DDTHH:MM:SSZ`, and a value that
is not one is refused, never read as "everything". A line the shim did not
write is counted and reported, not ranked.

--coverage names, for each given pid (default: every process whose command
line holds a known daemon name), whether the `gh` its PATH finds first is the
shim -- the line-2 marker `# hpo-gh-shim` -- or not, and so whether its calls
are logged. Read from /proc/<pid>/environ: Linux hosts only; elsewhere pass no
pid and read the PATH by hand. A process whose environ is unreadable is
reported `unreadable`, never counted as covered.

Blind spots, stated: calls from a host that does not install the shim (cloud
seats share the token from another host) and record_row.py's direct
urllib read are not counted.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

MARKER = "# hpo-gh-shim"
SHIM = Path(__file__).resolve().parent / "shims" / "seat-gh"
STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
LINE = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (\d+) (.*) (\S+) (\S+)")
DAEMONS = ("beatd.py", "tick_loop.sh", "sweep_driver.py", "orchestrator_tick.py",
           "roster_queue.py", "merge_train.py", "heartbeat.sh", "daemonize.py")


def state_dir():
    return Path(os.environ.get("HPO_STATE_DIR") or Path.home() / ".local/state/hpo")


def read_lines(log: Path):
    out = []
    for p in (Path(f"{log}.1"), log):
        try:
            out += p.read_text(errors="replace").splitlines()
        except OSError:
            pass
    return out


def top(lines, since=None, limit=10):
    """(callers, endpoints, malformed, kept) -- Counter, Counter, int, int."""
    if since is not None and not STAMP.fullmatch(since):
        raise ValueError(f"--since wants YYYY-MM-DDTHH:MM:SSZ, got {since!r}")
    callers, endpoints, bad, kept = Counter(), Counter(), 0, 0
    for ln in lines:
        m = LINE.fullmatch(ln)
        if not m:
            bad += 1
            continue
        if since is not None and m.group(1) < since:
            continue
        kept += 1
        callers[m.group(3)] += 1
        endpoints[f"{m.group(4)} {m.group(5)}"] += 1
    return callers, endpoints, bad, kept


def render_top(lines, since=None, limit=10):
    callers, endpoints, bad, kept = top(lines, since, limit)
    out = [f"gh calls: {kept}" + (f" since {since}" if since else "") + (f", {bad} unreadable line(s)" if bad else "")]
    for title, c in (("callers", callers), ("endpoints", endpoints)):
        out.append(f"{title}:")
        out += [f"  {n:6d}  {k}" for k, n in c.most_common(limit)] or ["  (none)"]
    return "\n".join(out)


def first_gh_is_shim(path: str):
    """True/False: the first executable `gh` on PATH is/is not the shim; None: no gh."""
    for d in path.split(":"):
        p = Path(d or ".") / "gh"
        if p.is_file() and os.access(p, os.X_OK):
            try:
                with open(p, errors="replace") as f:
                    f.readline()
                    return f.readline().rstrip("\n") == MARKER
            except OSError:
                return False
    return None


def proc_path(pid):
    try:
        env = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
    except OSError:
        return None
    for kv in env:
        if kv.startswith(b"PATH="):
            return kv[5:].decode(errors="replace")
    return ""


def daemon_pids():
    pids = []
    for p in Path("/proc").glob("[0-9]*"):
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if int(p.name) != os.getpid() and any(d in cmd for d in DAEMONS) and "gh_calls.py" not in cmd:
            pids.append((int(p.name), cmd.strip()[:80]))
    return pids


def coverage(pids):
    rows = []
    for pid, cmd in pids:
        path = proc_path(pid)
        if path is None:
            rows.append((pid, cmd, "unreadable"))
            continue
        r = first_gh_is_shim(path)
        rows.append((pid, cmd, {True: "shim first: logged", False: "real gh first: NOT logged",
                                None: "no gh on PATH"}[r]))
    return rows


def self_test():
    if not SHIM.is_file():
        print(f"gh_calls self-test: no shim at {SHIM}")
        return 1
    pass_n = fail_n = 0

    def check(name, cond):
        nonlocal pass_n, fail_n
        if cond:
            pass_n += 1
            print(f"  ok   {name}")
        else:
            fail_n += 1
            print(f"  FAIL {name}")

    with tempfile.TemporaryDirectory() as w:
        w = Path(w)
        (w / "real").mkdir()
        (w / "own").mkdir()
        stub = w / "real" / "gh"
        stub.write_text('#!/bin/sh\nprintf "STUB %s\\n" "$*"; cat; printf "ERR\\n" >&2; exit 7\n')
        stub.chmod(0o755)

        def install(src_text):
            dst = w / "own" / "gh"
            dst.write_text(src_text)
            dst.chmod(0o755)

        good = SHIM.read_text()
        install(good)
        log = w / "state" / "gh-calls.log"
        (w / "state").mkdir()

        def run(args, state=None, shim_text=None, stdin=b"IN\n", env_extra=None):
            if shim_text is not None:
                install(shim_text)
            env = {"PATH": f"{w / 'own'}:{w / 'real'}:/usr/bin:/bin",
                   "HPO_STATE_DIR": str(state or w / "state"), "HOME": str(w)}
            env.update(env_extra or {})
            r = subprocess.run([str(w / "own" / "gh"), *args], input=stdin, capture_output=True, env=env)
            return r

        r = run(["api", "repos/o/r/pulls", "-f", "body=secret"])
        text = log.read_text() if log.exists() else ""
        want = b"STUB api repos/o/r/pulls -f body=secret\nIN\n"
        check("stub bytes (stdout, stdin forwarded) pass through the shim", r.stdout == want)
        check("the stub's stderr and exit code pass through", r.stderr == b"ERR\n" and r.returncode == 7)
        m = LINE.fullmatch(text.strip())
        check("one log line naming parent and path", bool(m) and m.group(4) == "api" and m.group(5) == "repos/o/r/pulls"
              and text.count("\n") == 1 and int(m.group(2)) == os.getpid() and "python" in m.group(3))
        check("a -f body=secret argument never reaches the log", "secret" not in text and "body" not in text)

        run(["api", "-X", "POST", "repos/o/r/issues?per_page=9", "--input", "tokfile"])
        run(["pr", "view", "12", "-R", "o/r"])
        run(["api", "-fbody=hush", "graphql"])
        run(["api", "-f", "body=leak", "-F", "n=leak2", "repos/o/r/labels"])
        lines = log.read_text().splitlines()
        check("-X value, --input value and query string are dropped",
              lines[1].endswith(" api repos/o/r/issues") and "tokfile" not in "".join(lines) and "per_page" not in "".join(lines))
        check("a pr call logs its verb", lines[2].endswith(" pr view"))
        check("a glued -f value is dropped", lines[3].endswith(" api graphql") and "hush" not in "".join(lines))
        check("-f/-F values placed before the path are dropped, the path still found",
              lines[4].endswith(" api repos/o/r/labels") and "leak" not in "".join(lines))

        # null control: an unwritable log leaves output and status unchanged
        bad = w / "nostate"
        r2 = run(["api", "repos/o/r/pulls", "-f", "body=secret"], state=bad)
        check("null control: an unwritable log leaves output and status unchanged",
              r2.stdout == want and r2.stderr == b"ERR\n" and r2.returncode == 7 and not bad.exists())
        os.chmod(w / "state", 0o500)
        if os.access(w / "state", os.W_OK):
            print("  skip unwritable-directory arm (running as a user who can write anyway)")
        else:
            r3 = run(["api", "x"])
            check("null control: a read-only state directory is skipped, not fatal",
                  r3.stdout == b"STUB api x\nIN\n" and r3.returncode == 7 and r3.stderr == b"ERR\n")
        os.chmod(w / "state", 0o755)

        # rotation
        before = len(log.read_text().splitlines())
        run(["api", "rot"], env_extra={"HPO_GH_LOG_MAX": "10"})
        check("a log past the cap is rotated to .1",
              Path(f"{log}.1").exists() and len(Path(f"{log}.1").read_text().splitlines()) == before
              and len(log.read_text().splitlines()) == 1)

        # mutation: dropping the exec pass-through must fail the byte arm
        mut = good.replace('exec "$real" "$@"', '"$real" "$@" >/dev/null; true')
        check("mutant: the exec line is present in the shim being mutated", mut != good)
        rm = run(["api", "repos/o/r/pulls", "-f", "body=secret"], shim_text=mut)
        check("mutation: dropping the exec pass-through fails the byte arm",
              not (rm.stdout == want and rm.returncode == 7))
        install(good)

        # a shim is never its own real gh
        (w / "real" / "gh").unlink()
        r4 = run(["api", "x"])
        check("no real gh: one line, rc 127, no self-exec", r4.returncode == 127 and b"no real gh" in r4.stderr)

        # reader
        sample = ["2026-10-29T15:00:00Z 1 bus.sh confirm api repos/o/r/pulls",
                  "2026-10-29T15:01:00Z 2 bus.sh confirm api repos/o/r/pulls",
                  "2026-10-29T16:00:00Z 3 tick pr view", "junk"]
        c, e, bad_n, kept = top(sample)
        check("top ranks callers and endpoints by count",
              c.most_common(1) == [("bus.sh confirm", 2)] and e.most_common(1) == [("api repos/o/r/pulls", 2)] and bad_n == 1 and kept == 3)
        c, e, bad_n, kept = top(sample, since="2026-10-29T15:30:00Z")
        check("--since drops earlier lines", kept == 1 and list(c) == ["tick"])
        try:
            top(sample, since="yesterday")
            check("a malformed --since is refused", False)
        except ValueError:
            check("a malformed --since is refused", True)
        check("coverage reads the shim marker, not the name",
              first_gh_is_shim(f"{w / 'own'}") is True and first_gh_is_shim(f"{w / 'real'}") is None)
        (w / "real" / "gh").write_text("#!/bin/sh\n# other\n")
        (w / "real" / "gh").chmod(0o755)
        check("a real gh ahead of the shim reads as not logged",
              first_gh_is_shim(f"{w / 'real'}:{w / 'own'}") is False)
    print(f"gh_calls self-test: {pass_n + fail_n} checks, {fail_n} failed")
    return 1 if fail_n else 0


def main(argv):
    a = list(argv)
    if "--self-test" in a:
        return self_test()
    log = state_dir() / "gh-calls.log"
    since = None
    limit = 10
    try:
        if "--log" in a:
            log = Path(a[a.index("--log") + 1])
        if "--since" in a:
            since = a[a.index("--since") + 1]
        if "--limit" in a:
            limit = int(a[a.index("--limit") + 1])
    except (IndexError, ValueError):
        print(__doc__, file=sys.stderr)
        return 2
    if "--coverage" in a:
        rest = [x for x in a[a.index("--coverage") + 1:] if x.isdigit()]
        pids = [(int(x), "") for x in rest] or daemon_pids()
        rows = coverage(pids)
        for pid, cmd, verdict in rows or [(0, "", "no known daemon process found")]:
            print(f"{pid} {cmd} -- {verdict}")
        return 0
    if "--top" in a:
        try:
            print(render_top(read_lines(log), since, limit))
        except ValueError as e:
            print(f"gh_calls: {e}", file=sys.stderr)
            return 2
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
