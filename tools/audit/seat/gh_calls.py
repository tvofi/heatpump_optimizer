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
import shutil
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

        # Hermetic PATH: the shim and the stub, plus a dir of symlinks to the few
        # utilities the shim runs. Never /usr/bin or /bin, where a host may carry
        # a real gh (the CI runner does; a Mac does not).
        tools = w / "tools"
        tools.mkdir()
        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3"):
            found = shutil.which(tool)
            if found:
                (tools / tool).symlink_to(found)
        hermetic = f"{w / 'own'}:{w / 'real'}:{tools}"

        def gh_on(path):
            """Every executable gh a shell would meet on `path`, in order (not just the first)."""
            return [f"{d}/gh" for d in path.split(":") if d and os.access(f"{d}/gh", os.X_OK) and Path(f"{d}/gh").is_file()]

        def hermetic_ok(path, shim_dir):
            """The guard: the only gh on the PATH is the shim under test, or none."""
            return gh_on(path) in ([], [f"{shim_dir}/gh"])

        good = SHIM.read_text()
        install(good)
        log = w / "state" / "gh-calls.log"
        (w / "state").mkdir()

        def run(args, state=None, shim_text=None, stdin=b"IN\n", env_extra=None, path=None, via=None):
            if shim_text is not None:
                install(shim_text)
            env = {"PATH": path or hermetic,
                   "HPO_STATE_DIR": str(state or w / "state"), "HOME": str(w)}
            env.update(env_extra or {})
            cmd = [str(w / "own" / "gh"), *args] if via is None else ["sh", "-c", via]
            r = subprocess.run(cmd, input=stdin, capture_output=True, env=env, timeout=60)
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

        # round-2 arms: --input before the path, a token outside the allowed set
        run(["api", "--input", "tokfile2", "repos/o/r/inp"])
        run(["api", "repos/o/r$x;y\\z"])
        ln = log.read_text().splitlines()
        check("--input FILE placed before the path is skipped, the path is the target",
              ln[-2].endswith(" api repos/o/r/inp") and "tokfile2" not in "".join(ln))
        check("a token outside the allowed set is logged with ? for each such character",
              ln[-1].endswith(" api repos/o/r?x?y?z"))

        # the parent's command line is redacted from the first value-bearing flag on
        planted = {
            "sh -c 'gh api repos/o/r -f body=PLANT1; :'": "PLANT1",
            "sh -c 'gh issue comment 1 --body PLANT2; :'": "PLANT2",
            "sh -c 'gh api repos/o/r --field=k=PLANT3; :'": "PLANT3",
            "sh -c 'gh api repos/o/r -fbody=PLANT4; :'": "PLANT4",
            "sh -c 'env gh pr create --title T --body PLANT5 x; :'": "PLANT5",
        }
        pl_lines = []
        for cmdline, secret in planted.items():
            run([], via=cmdline.split("'")[1])
            pl_lines.append((secret, log.read_text().splitlines()[-1]))
        check("planted -f/--body/--field/glued values never reach the parent field",
              all(sec not in ln_ for sec, ln_ in pl_lines))
        check("and the flag name stays with a <redacted> marker (the fixture is not vacuous)",
              all("<redacted>" in ln_ for _, ln_ in pl_lines) and " -f <redacted>" in pl_lines[0][1]
              and "gh api repos/o/r" in pl_lines[0][1])
        census = ["-f", "-F", "-H", "-b", "-n", "-t", "-T", "-q", "-d", "--body", "--body-file", "--notes",
                  "--notes-file", "--title", "--subject", "--desc", "--description", "--field", "--raw-field",
                  "--header", "--input", "--jq", "--template", "--env-file", "--squash-merge-commit-message"]
        leaked = []
        for flag in census:
            run([], via=f"gh api repos/o/r {flag} CENSUS_VAL; :")
            if "CENSUS_VAL" in log.read_text().splitlines()[-1]:
                leaked.append(flag)
        check("census: no value-bearing gh flag leaks its value through the parent field", not leaked)
        run([], via="python3 -m json.tool /dev/null >/dev/null 2>&1; gh api repos/o/r; :")
        check("a non-gh parent keeps its -m argument", "-m json.tool" in log.read_text().splitlines()[-1])

        # null control: an unwritable log leaves output and status unchanged
        (w / "afile").write_text("x")
        bad = w / "afile" / "state"  # under a regular file: it cannot be created or written
        r2 = run(["api", "repos/o/r/pulls", "-f", "body=secret"], state=bad)
        check("null control: an unwritable log leaves output and status unchanged",
              r2.stdout == want and r2.stderr == b"ERR\n" and r2.returncode == 7 and not bad.exists())
        fresh = w / "fresh" / "state"
        run(["api", "made"], state=fresh)
        check("a missing state directory is created and the call logged (not silently dropped)",
              (fresh / "gh-calls.log").is_file() and (fresh / "gh-calls.log").read_text().rstrip().endswith(" api made"))
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

        # round-2 mutants of the shim: each must trip its arm
        def killed(name, old, new_, arm):
            m = good
            for o_, n_ in zip(old if isinstance(old, tuple) else (old,), new_ if isinstance(new_, tuple) else (new_,)):
                m = m.replace(o_, n_)
            ok = m != good
            if arm != "mkdir":
                (w / f"m_{name}").mkdir()
            r_ = run(["api", "--input", "tokfile3", "repos/o/r/m"], shim_text=m, state=w / f"m_{name}")
            l_ = (w / f"m_{name}" / "gh-calls.log")
            t_ = l_.read_text() if l_.exists() else ""
            run([], via="gh api repos/o/r -f body=MUT; :", shim_text=m, state=w / f"m_{name}")
            t2 = l_.read_text() if l_.exists() else ""
            tripped = {"input": "tokfile3" in t_, "clean": False, "mkdir": not l_.exists(),
                       "redact": "MUT" in t2}[arm]
            if arm == "clean":
                run(["api", "a$b"], shim_text=m, state=w / f"m_{name}")
                tripped = l_.exists() and "a$b" in l_.read_text()
            check(f"mutant killed: {name}", ok and tripped)
            install(good)

        killed("no --input skip", "--input|", "", "input")
        killed("clean() is cat", "tr -c 'A-Za-z0-9_./:-' '?'", "cat", "clean")
        killed("no mkdir of the state dir", '  mkdir -p "$state"\n', "", "mkdir")
        killed("no parent redaction", ("($longf)", "[fFHbntTqd]"), ("(ZZZ)", "[Z]"), "redact")

        # a shim is never its own real gh. The PATH is hermetic: no real gh on any host.
        (w / "real" / "gh").unlink()
        no_gh_path = f"{w / 'own'}:{tools}"
        check("the hermetic guard: the only gh is the shim, or none, on the arm's PATH",
              hermetic_ok(no_gh_path, w / "own") and gh_on(no_gh_path) == [f"{w / 'own'}/gh"])
        r4 = run(["api", "x"], path=no_gh_path)
        check("no real gh: one line, rc 127, no self-exec", r4.returncode == 127 and b"no real gh" in r4.stderr)

        # planted defect (the CI red, reproduced on a host with no /usr/bin/gh): a fake
        # executable gh ahead of /usr/bin. The old PATH shape finds it and the old
        # arm goes red; the hermetic shape never sees it and stays green.
        decoy = w / "decoy"
        decoy.mkdir()
        (decoy / "gh").write_text("#!/bin/sh\necho DECOY\n")
        (decoy / "gh").chmod(0o755)
        old_path = f"{w / 'own'}:{w / 'real'}:{decoy}:/usr/bin:/bin"
        r5 = run(["api", "x"], path=old_path)
        check("control: with a fake gh on the old-style PATH the old arm is red (the shim execs it)",
              not (r5.returncode == 127 and b"no real gh" in r5.stderr) and b"DECOY" in r5.stdout)
        check("control: the same fake gh is invisible to the hermetic PATH, the arm stays green",
              run(["api", "x"], path=no_gh_path).returncode == 127)
        # mutation of the guard: a PATH that lets the fake gh in must be refused by it
        check("mutation: a PATH that includes the fake gh fails the hermetic guard",
              not hermetic_ok(f"{no_gh_path}:{decoy}", w / "own"))
        check("mutation: the old-style PATH fails the hermetic guard",
              not hermetic_ok(old_path, w / "own"))

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
