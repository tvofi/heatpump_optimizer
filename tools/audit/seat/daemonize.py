#!/usr/bin/env python3
"""daemonize.py — detach one long-running instrument from the session that
started it, with a log the launch is attributable from its first line.

    python3 tools/audit/seat/daemonize.py --log LOG [--cwd DIR]
             [--env K=V]... [--path-prepend DIR] -- CMD [ARG]...
    python3 tools/audit/seat/daemonize.py --self-test

WHY THIS EXISTS. Round 9 hand-rolled the same wrapper four times in /tmp
(launch-traintest.py, launch-rehearse.py, launch-wait2.py in a scratch dir,
and an earlier train launcher), each a private fork/setsid/dup2/execvp copy
wrapping one merge_train invocation. #2180 made merge_train itself
self-sufficient at a daemonized launch (line-buffered stdout, the BATCH banner
as the first line), but every OTHER long instrument — proof_watch.py's 4.5 h
watch, ci-watch.sh's loop, a long sweep — still dies with the session that
spawned it unless that session re-derives the wrapper. This is the wrapper,
once.

The shape is exactly the one the /tmp copies used, with the two lessons
#2180 recorded built in:

  banner first  the log's FIRST line names the child pid, the UTC time and the
                full argv, written by the child before exec, so a hung run is
                attributable even when nothing after it prints;
  unbuffered    the log file object is opened unbuffered (`buffering=0`) AND
                the child's Python, if the command is python3, is exec'd with
                `-u` prepended when the caller did not pass one — the parent
                never relies on the child re-configuring itself.

Semantics:
  fork     the parent exits 0 immediately after printing the child's pid; the
           child survives the session that started it;
  setsid   the child gets its own session, so it owns no controlling terminal
           and no SIGHUP reaches it when the launching shell dies;
  dup2     stdout and stderr are the log; the log is opened in append mode so
           relaunches extend one attributable file;
  execvp   the child IS the command — no intermediate interpreter lingers, so
           `pgrep -f` matches the instrument, not a wrapper (the pgrep
           self-match trap);

Guards:
  log required   `--log` is mandatory; a detached child with no log is the
                 exact blindness #2180's traintest incident cost hours to;
  --env K=V      only named variables are added; the caller's environment is
                 otherwise passed through untouched;
  --path-prepend DIR prepends one directory to PATH (the seat-venv pattern
                 the /tmp copies hard-coded);
  --cwd DIR      chdir before exec; refused if the directory does not exist,
                 because a launcher that silently keeps the wrong cwd is how
                 three seats once mutated the orchestrator checkout.

No daemon bookkeeping is kept: the pid is printed and logged, and `kill` by
that pid is the stop story. An instrument that wants its own locking (the
proof_watch flock, the gate lease) keeps it — this does not touch locks.

Self-test: offline, no repo state touched. It daemonizes a `python3 -c`
child that writes two lines and exits, polls the log for both plus the
banner, checks the banner's pid equals the pid this process printed, and
daemonizes a second child against the same log to grade append mode.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

BANNER = "===== daemonize pid={pid} {utc} argv: {argv}"


def _banner(pid: int, argv: list[str]) -> bytes:
    return (BANNER.format(pid=pid, utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                      time.gmtime()),
                          argv=" ".join(argv)) + "\n").encode()


def daemonize(argv: list[str], log_path: str, cwd: str | None,
              env_add: dict[str, str], path_prepend: str | None) -> int:
    """Fork, setsid, dup2, exec. Returns the child's pid from the parent's
    side; never returns on the child's (exec or die)."""
    log = open(log_path, "ab", 0)  # unbuffered: nothing is ever held back
    # Prepend -u when the command is a bare python3 without one: the caller
    # may wrap a child that did not get #2180's reconfigure.
    run_argv = list(argv)
    if os.path.basename(run_argv[0]) in ("python3", "python") and \
            "-u" not in run_argv[1:2]:
        run_argv.insert(1, "-u")
    pid = os.fork()
    if pid:
        log.close()
        return pid
    # ---- child ----
    log.write(_banner(os.getpid(), run_argv))
    os.setsid()
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    if log.fileno() > 2:
        log.close()
    if cwd:
        os.chdir(cwd)
    if path_prepend:
        env_add = {**env_add,
                   "PATH": path_prepend + os.pathsep + os.environ.get("PATH", "")}
    os.environ.update(env_add)
    try:
        os.execvp(run_argv[0], run_argv)
    except OSError as exc:  # exec failed: say so in the log, not nowhere
        os.write(2, f"daemonize: exec {run_argv[0]!r} failed: {exc}\n".encode())
        os._exit(127)


def self_test() -> int:
    import tempfile
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        ok = ok and cond

    # The command line, parsed (R10-TICK j): the documented `-- CMD` form
    # must yield exactly CMD, a later `--` stays the command's, the bare form
    # still parses, and an empty command is refused.
    def cli(*argv):
        try:
            return parse_cli(list(argv)).cmd
        except SystemExit as e:
            return f"exit {e.code}"

    check("`-- CMD` parses to CMD, the `--` dropped",
          cli("--log", "L", "--", "python3", "-c", "x") == ["python3", "-c", "x"])
    check("options before `--` still parse",
          parse_cli(["--log", "L", "--cwd", "/", "--env", "A=1", "--",
                     "true"]).env_add == {"A": "1"})
    check("a later `--` belongs to the command",
          cli("--log", "L", "--", "git", "log", "--", "p")
          == ["git", "log", "--", "p"])
    check("the bare form without `--` still parses",
          cli("--log", "L", "true") == ["true"])
    check("an empty command after `--` is refused", cli("--log", "L", "--")
          == "exit 2")

    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "t.log")
        marker = os.path.join(tmp, "done")
        # The child exits with os._exit AFTER printing and never flushes: only
        # an unbuffered stdout — the -u this launcher prepends — can deliver
        # its lines. The printed literals are split at the source ('li'+'ne')
        # so the banner's argv echo cannot satisfy the checks for them: the
        # banner contains the command string, and an unsplit literal would
        # make "output reached the log" true even when nothing was written.
        child = (
            "import os;"
            f"open({marker!r},'w').write('x');"
            "print('li'+'ne-one'); print('li'+'ne-two'); os._exit(0)"
        )
        pid = daemonize(["python3", "-c", child], log, tmp, {}, None)
        print(f"daemonize: child pid {pid}")
        # Poll, never sleep-fixed: a loaded box must not false-fail.
        got = ""
        for _ in range(100):
            time.sleep(0.1)
            if os.path.exists(log):
                got = open(log, "rb").read().decode(errors="replace")
            if marker in got and "line-two" in got:
                break
        check("banner is the log's first line and names a pid",
              got.splitlines()[:1] and
              got.splitlines()[0].startswith("===== daemonize pid="))
        check("banner's pid is the pid the parent returned",
              f"pid={pid} " in got.splitlines()[0] + " ")
        check("child output reached the log unflushed (fork/setsid/dup2/-u)",
              "line-one" in got and "line-two" in got)
        i_banner, i_one = got.find("===== daemonize"), got.find("line-one")
        check("banner precedes the child's output in the log",
              i_banner != -1 and i_one != -1 and i_banner < i_one)
        # Append mode, graded for real: a second launch must extend the same
        # attributable file, not truncate the first run's evidence. (The
        # draft's fifth check ran `pgrep -f daemonize ... or True`, which can
        # never fail — the pgrep self-match trap made it ungradeable, and a
        # check that cannot fail pins nothing.)
        pid2 = daemonize(["python3", "-c", "print('se'+'cond-run')"], log,
                         tmp, {}, None)
        got2 = got
        for _ in range(100):
            time.sleep(0.1)
            got2 = open(log, "rb").read().decode(errors="replace")
            if got2.count("second-run") >= 1 and \
                    got2.count("===== daemonize pid=") >= 2:
                break
        check("append mode: a relaunch extends the log, first run intact",
              got2.count("===== daemonize pid=") >= 2
              and "line-one" in got2 and "second-run" in got2)
    print("SELF-TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


USAGE = ("usage: daemonize.py --log LOG [--cwd DIR] [--env K=V]... "
         "[--path-prepend DIR] -- CMD [ARG]...")


def parse_cli(argv: list[str]) -> argparse.Namespace:
    """The options and the command. The command is everything after the
    FIRST `--`, split here rather than by argparse: `nargs=REMAINDER` keeps
    that `--` as the command's first word on Python 3.14, so the documented
    `-- CMD` form was refused as an empty command (R10-TICK j). A later `--`
    belongs to the command (`git log -- path`) and is kept. Without any `--`
    the bare `--log L CMD` form still parses through REMAINDER."""
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[0])
    ap.add_argument("--log", required=True)
    ap.add_argument("--cwd")
    ap.add_argument("--env", action="append", default=[], metavar="K=V")
    ap.add_argument("--path-prepend")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    if "--" in argv:
        i = argv.index("--")
        a = ap.parse_args(argv[:i])
        a.cmd = argv[i + 1:]
    else:
        a = ap.parse_args(argv)
    if not a.cmd or a.cmd[0] == "--":
        ap.error(USAGE)
    a.env_add = {}
    for kv in a.env:
        k, _, v = kv.partition("=")
        if not k:
            ap.error(f"--env wants K=V, got {kv!r}")
        a.env_add[k] = v
    if a.cwd and not os.path.isdir(a.cwd):
        ap.error(f"--cwd {a.cwd!r} does not exist")
    return a


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    a = parse_cli(sys.argv[1:])
    pid = daemonize(a.cmd, a.log, a.cwd, a.env_add, a.path_prepend)
    print(f"daemonize: detached pid {pid} log {a.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
