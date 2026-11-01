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
import stat
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
        stub.chmod(0o700)

        def install(src_text):
            dst = w / "own" / "gh"
            dst.write_text(src_text)
            dst.chmod(0o700)

        # Hermetic PATH: the shim and the stub, plus a dir of symlinks to the few
        # utilities the shim runs. Never /usr/bin or /bin, where a host may carry
        # a real gh (the CI runner does; a Mac does not).
        tools = w / "tools"
        tools.mkdir()
        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3", "chmod"):
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

        # The parent field is the caller's argv[0] and, for an interpreter, at most one more
        # word (the shim's header states the rule): these arms pin that a wrapper's argv list,
        # env assignment, pipe or gh flag value does not reach the log through the real ps.
        def field(via, sh=None):
            run([], via=via, shim_text=sh)
            m_ = LINE.fullmatch(log.read_text().splitlines()[-1])
            return m_.group(3) if m_ else None
        caller = w / "caller.py"
        caller.write_text("import subprocess, sys\nsubprocess.run(['gh', 'pr', 'comment', '--body', sys.argv[-1]])\n")
        py, pyn = sys.executable, Path(sys.executable).name  # the seat's python3 shim needs a real HOME
        shapes = {  # wrapper command line -> the exact parent field it must log
            f"{py} -c \"import subprocess as s;s.run(['gh','pr','comment','--body','LEAKVAL'])\"": f"{pyn} -c",
            f"{py} -c \"import subprocess as s;s.run(['gh','api','-fx=LEAKVAL','repos/o/r'])\"": f"{pyn} -c",
            "GH_TOKEN=ghp_LEAKVAL gh api user; :": "sh -c",
            "echo ghp_LEAKVAL | gh secret set NAME; :": "sh -c",
            "env GH_TOKEN=ghp_LEAKVAL gh api user; :": "sh -c",  # env execs gh: sh is the parent
            "gh api repos/o/r -fbody=LEAKVAL; :": "sh -c",
            "env gh pr create --title T --body LEAKVAL x; :": "sh -c",
            f"{py} -I {caller} --body LEAKVAL": f"{pyn} {caller}"[:80],
            f"cd {w} && {py} -m caller --body LEAKVAL": f"{pyn} -m caller",
        }
        got = {via: field(via) for via in shapes}
        for via, want_f in shapes.items():
            label = via.replace(str(w), "W").replace(py, "PY")  # no host path in a check name
            check(f"parent field of `{label[:52]}` is exactly the caller, no value", got[via] == want_f)
        census = ["-f", "-F", "-H", "-b", "-n", "-t", "-T", "-q", "-d", "--body", "--body-file", "--notes",
                  "--notes-file", "--title", "--subject", "--desc", "--description", "--field", "--raw-field",
                  "--header", "--input", "--jq", "--template", "--env-file", "--squash-merge-commit-message",
                  "-A", "--author-email", "-S", "--search", "-m", "--milestone", "-l", "--label", "-a",
                  "--assignee", "-r", "--reviewer", "-B", "--base", "--match-head-commit", "-p", "--preview",
                  "-e", "--env"]
        leaked = [f for f in census if field(f"gh api repos/o/r {f} CENSUS_VAL; :") != "sh -c"]
        check("census: every gh value flag through a sh -c parent logs exactly `sh -c`", not leaked)
        # mutants of the field rule: each must trip a shape arm
        def field_mutant(name, old, new_, via, want_f):
            mut_ = good.replace(old, new_)
            check(f"mutant killed: {name}", mut_ != good and field(via, mut_) != want_f)
            install(good)
        field_mutant("the whole parent argv logged", '"$pcmd" | tr -c', '"$pargs" | tr -c',
                     "GH_TOKEN=ghp_LEAKVAL gh api user; :", "sh -c")
        field_mutant("-c does not end the field", "c|e|s) pcmd=", "c|e|s) ;; xx) pcmd=",
                     "echo ghp_LEAKVAL | gh secret set NAME; :", "sh -c")
        field_mutant("-m does not take its module", '-m) pcmd="$pcmd -m ${pw[$((i + 1))]}"; end=1 ;;', "",
                     f"cd {w} && {py} -m caller --body LEAKVAL", f"{pyn} -m caller")
        field_mutant("python is not followed to its script", "python|python[0-9]*|Python|pypy*) flags=", "xx) flags=",
                     f"{py} -I {caller} --body LEAKVAL", f"{pyn} {caller}"[:80])

        # Exact-field arms over a stated parent command line: a fake `ps` prints it, so the
        # perl, ruby and node shapes need no such interpreter on the host. The real-ps arms
        # above pin that the shim reads its true parent; these pin the field rule itself.
        ftools = w / "ftools"
        ftools.mkdir()
        for t in tools.iterdir():
            if t.name != "ps":
                (ftools / t.name).symlink_to(os.readlink(t))
        (ftools / "ps").write_text('#!/bin/sh\nprintf "%s\\n" "$HPO_FAKE_PARGS"\n')
        (ftools / "ps").chmod(0o700)
        fpath = f"{w / 'own'}:{w / 'real'}:{ftools}"

        def ffield(pargs, sh=None):
            run(["api", "x"], shim_text=sh, path=fpath, env_extra={"HPO_FAKE_PARGS": pargs})
            m_ = LINE.fullmatch(log.read_text().splitlines()[-1])
            return m_.group(3) if m_ else None
        long_script = "/" + "d" * 90 + "/s.sh"
        fshapes = {  # parent command line -> the exact field; LEAKVAL is a caller's value
            "python3 -c__import__('subprocess').run(['gh','api','-fx=LEAKVAL'])": "python3 -c",
            "python3 -Bc__import__('subprocess').run(['gh','api','-fx=LEAKVAL'])": "python3 -Bc",
            "perl -esystem('gh','api','-fx=LEAKVAL')": "perl -e",
            "ruby -esystem('gh','api','-fx=LEAKVAL')": "ruby -e",
            "node --eval=require('child_process').execFileSync('gh',['-fx=LEAKVAL'])": "node --eval",
            "node --print=LEAKVAL": "node --print",
            "bash --command=LEAKVAL": "bash --command",
            "sh -s LEAKVAL": "sh -s",
            "sh -s -- LEAKVAL": "sh -s",
            "bash -s -- --token LEAKVAL": "bash -s",
            "python3 -W ignore::LEAKVAL caller.py": "python3",
            "python3 -WLEAKVAL caller.py": "python3",
            "python3 -X LEAKVAL caller.py": "python3",
            "python3 -W error -m caller_mod LEAKVAL": "python3",
            "python3 -X 'a LEAKVAL' caller.py": "python3",  # a value of one argv word with a space
            "python3 -W \"ignore LEAKVAL\" caller.py": "python3",
            "bash -o LEAKVAL s.sh": "bash",
            "node --require ./LEAKVAL.js n.js": "node",
            "node -p LEAKVAL": "node",
            "ruby -r LEAKVAL x.rb": "ruby",
            "perl -MLEAKVAL -e x": "perl",
            "python3 -I caller.py --body LEAKVAL": "python3 caller.py",  # null control: not cut to nothing
            "sh ./a=b/s.sh LEAKVAL": "sh ./a?b/s.sh",  # `=` in a kept word is logged `?`
            f"sh {long_script} LEAKVAL": f"sh {long_script}"[:80],  # the 80-character cut
        }
        fgot = {pa: ffield(pa) for pa in fshapes}
        for pa, want_f in fshapes.items():
            check(f"exact field of parent `{pa[:48]}` is `{want_f[:24]}`", fgot[pa] == want_f)

        # mutants of each rule of the field: each must change an exact-field arm
        def fmutant(name, reps, pargs):
            mut_ = good
            for old, new_ in reps:
                mut_ = mut_.replace(old, new_)
            check(f"mutant killed: {name}", mut_ != good and ffield(pargs, mut_) != fshapes[pargs])
            install(good)
        glued = "python3 -c__import__('subprocess').run(['gh','api','-fx=LEAKVAL'])"
        fmutant("a code option logged whole, not cut after its letter",
                [('pcmd="$pcmd ${a:0:$((j + 1))}"', 'pcmd="$pcmd $a"')], glued)
        fmutant("-s passed over as a no-value letter, not ending the field",
                [("c|e|s)", "c|e)"), ("[abfhik", "[sabfhik")], "sh -s LEAKVAL")
        fmutant("an unknown option letter passed over, not ending the field",
                [("*) end=1; break ;;\n          esac", "*) ;;\n          esac")], "ruby -r LEAKVAL x.rb")
        fmutant("an unknown long option passed over, not ending the field",
                [("--*) end=1 ;;", "--*) ;;")], "node --require ./LEAKVAL.js n.js")
        fmutant("a value-taking letter read as no-value, its value taken as the script",
                [("vals='[WX]'", "vals="), ("[bBdEhiIOqPRSuvVx]", "[bBdEhiIOqPRSuvVxWX]")],
                "python3 -W ignore::LEAKVAL caller.py")
        fmutant("a value-taking letter skips one word as its value, not ending the field",
                [("$vals) end=1; break ;;", '$vals) [ "$((j + 1))" -eq "${#a}" ] && i=$((i + 1)); break ;;')],
                "python3 -X 'a LEAKVAL' caller.py")
        fmutant("`=` allowed in the parent field",
                [("tr -c 'A-Za-z0-9_./: -' '?' | cut", "tr -c 'A-Za-z0-9_./:= -' '?' | cut")], "sh ./a=b/s.sh LEAKVAL")
        fmutant("the 80-character cut removed", [(" | cut -c1-80)", ")")], f"sh {long_script} LEAKVAL")
        fmutant("--eval/--print/--command passed over",
                [('--eval|--eval=*|--print|--print=*|--command|--command=*) pcmd="$pcmd ${a%%=*}"; end=1 ;;',
                  "--eval*|--print*|--command*) ;;")],
                "node --eval=require('child_process').execFileSync('gh',['-fx=LEAKVAL'])")
        fmutant("a long code option logged with its attached code",
                [('pcmd="$pcmd ${a%%=*}"', 'pcmd="$pcmd $a"')], "node --print=LEAKVAL")

        # a log written by an earlier shim (0644) is made owner-only on the next call; a
        # rotated one too, since mv keeps the mode
        old_log = w / "oldmode" / "gh-calls.log"
        old_log.parent.mkdir()
        old_log.write_text("x\n")
        os.chmod(old_log, 0o600 | 0o044)
        run(["api", "om"], state=old_log.parent)
        check("an existing 0644 log is 0600 after the next call", stat.S_IMODE(old_log.stat().st_mode) == 0o600)
        os.chmod(old_log, 0o600 | 0o044)
        run(["api", "om"], state=old_log.parent, env_extra={"HPO_GH_LOG_MAX": "1"})
        rot = Path(f"{old_log}.1")
        check("a 0644 log rotated to .1 is 0600 there",
              rot.exists() and stat.S_IMODE(rot.stat().st_mode) == 0o600 and stat.S_IMODE(old_log.stat().st_mode) == 0o600)
        mut_c = good.replace('  chmod 600 "$log"\n', "")
        os.chmod(old_log, 0o600 | 0o044)
        run(["api", "om"], state=old_log.parent, shim_text=mut_c)
        check("mutant killed: no chmod of an existing log",
              mut_c != good and stat.S_IMODE(old_log.stat().st_mode) != 0o600)
        install(good)

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
        # the log names callers: created owner-only whatever the caller's umask (alert 46)
        def modes(sh, st):
            st.parent.mkdir(exist_ok=True)
            run([], state=st, shim_text=sh, via="umask 022; gh api modes")
            lg = st / "gh-calls.log"
            return (stat.S_IMODE(st.stat().st_mode) if st.exists() else None,
                    stat.S_IMODE(lg.stat().st_mode) if lg.exists() else None)
        check("under umask 022 the shim makes its state dir 0700 and its log 0600",
              modes(None, w / "modes" / "state") == (0o700, 0o600))
        # the tightened umask is the logging subshell's alone: the real gh keeps the caller's
        (w / "real2").mkdir()
        (w / "real2" / "gh").write_text("#!/bin/sh\numask\n")
        (w / "real2" / "gh").chmod(0o700)
        um_path = f"{w / 'own'}:{w / 'real2'}:{tools}"
        um = lambda sh=None: run([], shim_text=sh, path=um_path, via="umask 022; gh api um").stdout.strip()
        check("the real gh runs under the caller's umask (022), not the shim's", um() == b"0022")
        check("mutant killed: no umask 077 in the shim",
              "umask 077" in good and modes(good.replace("umask 077", ":"), w / "modes_m" / "state") != (0o700, 0o600))
        check("mutant killed: the umask leaks past the logging subshell",
              "(\n  umask 077\n" in good and um(good.replace("(\n  umask 077\n", "umask 077\n(\n")) == b"0077")
        install(good)
        os.chmod(w / "state", 0o500)
        if os.access(w / "state", os.W_OK):
            print("  skip unwritable-directory arm (running as a user who can write anyway)")
        else:
            r3 = run(["api", "x"])
            check("null control: a read-only state directory is skipped, not fatal",
                  r3.stdout == b"STUB api x\nIN\n" and r3.returncode == 7 and r3.stderr == b"ERR\n")
        os.chmod(w / "state", 0o700)

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
            tripped = {"input": "tokfile3" in t_, "clean": False, "mkdir": not l_.exists()}[arm]
            if arm == "clean":
                run(["api", "a$b"], shim_text=m, state=w / f"m_{name}")
                tripped = l_.exists() and "a$b" in l_.read_text()
            check(f"mutant killed: {name}", ok and tripped)
            install(good)

        killed("no --input skip", "--input|", "", "input")
        killed("clean() is cat", "tr -c 'A-Za-z0-9_./:-' '?'", "cat", "clean")
        killed("no mkdir of the state dir", '  mkdir -p "$state"\n', "", "mkdir")

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
        (decoy / "gh").chmod(0o700)
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
        (w / "real" / "gh").chmod(0o700)
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
