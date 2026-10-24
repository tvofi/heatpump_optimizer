#!/usr/bin/env python3
"""The roster seat's queue runner: one roster_edit.py op per queue line.

    python3 -I tools/audit/seat/roster_queue.py run FIRST LAST --queue Q --report R \
        --edit-checkout DIR --worktree WT --lint-clone LC [--alive FILE] [--branch B]
    python3 -I tools/audit/seat/roster_queue.py readback SHA GROUP TEXTFILE
    python3 -I tools/audit/seat/roster_queue.py --self-test

`run` applies queue lines FIRST..LAST (1-based; blank and `#` lines skipped, a
leading line number dropped). Each line is `<op> <group> [arg] [--flag value ...]`, passed to
`roster_edit.py` with `--push`. WHY IT EXISTS: the lint gate refuses a push
whose `--lint-cwd` is not exactly `origin/main`, and main moves faster than a
checkout another seat owns can be kept level (2026-10-24: four refusals). So
the runner lints from `--lint-clone`, a checkout it owns, fetched and detached
at `origin/main` before every attempt, and retries up to four times when the
refusal is that main moved or the push lost a race with a clean lint
(the roster worktree is removed between attempts). It never moves
`--edit-checkout` (the orchestrator's), which only supplies the tool and the
roster. A refusal is reported, never forced.

Every `append-carry <group> @file` is read back from the pushed commit: the
roster JSON at that SHA must hold the file's text exactly as one carry entry.
`readback` prints the figures; the report line says FAILED when none match.
One report line per op: `roster: <op> <group> pushed <sha9> [| readback: ...]`
or `roster: <op> <group> refused rc=N <last three lines>`. `--alive` is
touched after each report line. Blind spot, stated: only append-carry with an
@file is read back here; other ops are read from the roster JSON by the caller.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROSTER_REL = "dev/programme/rosters/wave-r10-groups.json"
MOVED = "not origin/main"


def _git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def _walk(o, grp):
    if isinstance(o, dict):
        if grp in (o.get("group"), o.get("id"), o.get("name")) and "carry" in o:
            yield o
        for v in o.values():
            yield from _walk(v, grp)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v, grp)


def readback(sha, grp, fn, cwd=None, rel=ROSTER_REL):
    """One line: the carry count, the indices equal to the file's text, the
    last entry's lengths. Raises when the SHA, roster or group is absent."""
    s = _git("show", f"{sha}:{rel}", cwd=cwd)
    if s.returncode:
        raise RuntimeError(f"no {rel} at {sha}: {s.stderr.strip()[-120:]}")
    g = next(_walk(json.loads(s.stdout), grp), None)
    if g is None:
        raise RuntimeError(f"group {grp} not in the roster at {sha}")
    want = Path(fn).read_text().strip()
    c = g["carry"]
    hit = [i for i, x in enumerate(c) if x.strip() == want]
    last = c[-1] if c else ""
    return (f"{grp} {sha[:9]} n_carry={len(c)} exact-match-index={hit} "
            f"last120={last[:120]!r} len={len(last)}/{len(want)}"), bool(hit)


def parse_line(ln):
    if not ln.strip() or ln.lstrip().startswith("#"):
        return None
    t = shlex.split(ln)
    if t and t[0][0].isdigit():
        t = t[1:]
    if len(t) < 2:
        return None
    # A flag (`--match TEXT` on drop-carry) is never the op's positional value:
    # everything from the first `--` token on is passed through to roster_edit.
    rest = t[2:]
    if rest and rest[0].startswith("--"):
        return t[0], t[1], "", rest
    return t[0], t[1], (rest[0] if rest else ""), rest[1:]


def run_queue(a, python=None):
    env = dict(os.environ)
    shims = Path(a.edit_checkout, "tools/audit/seat/shims")
    if shims.is_dir():
        env["PATH"] = f"{shims}:{env['PATH']}"
    editor = a.editor or str(Path(a.edit_checkout, "tools/audit/seat/roster_edit.py"))
    py = python or "seat-python3"

    def sh(*c):
        return subprocess.run(c, capture_output=True, text=True, env=env, cwd=a.edit_checkout)

    def rep(s):
        with open(a.report, "a") as f:
            f.write(s + "\n")
        if a.alive:
            Path(a.alive).touch()

    sh("git", "fetch", "-q", "origin")  # fetch only: the edit checkout is never moved
    lines = Path(a.queue).read_text().split("\n")[a.first - 1:a.last]
    for ln in lines:
        p = parse_line(ln)
        if not p:
            continue
        op, g, arg, extra = p
        cmd = [py, editor, op, g] + ([arg] if arg else []) + extra + [
            "--checkout", a.edit_checkout, "--worktree", a.worktree,
            "--lint-cwd", a.lint_clone, "--push"]
        if a.branch:
            cmd += ["--branch", a.branch]
        for attempt in (1, 2, 3, 4):
            _git("fetch", "-q", "origin", cwd=a.lint_clone)
            _git("checkout", "-q", "--detach", "origin/main", cwd=a.lint_clone)
            r = sh(*cmd)
            out = r.stdout + r.stderr
            m = re.search(r"pushed handoff\S* at ([0-9a-f]+)", out)
            if r.returncode == 0 and m:
                rb = ""
                if op == "append-carry" and arg.startswith("@"):
                    try:
                        rb = " | readback: " + readback(m.group(1), g, arg[1:], cwd=a.worktree)[0]
                    except Exception as e:  # noqa: BLE001 - reported, not hidden
                        rb = f" | readback: FAILED {str(e)[-200:]}"
                rep(f"roster: {op} {g} pushed {m.group(1)[:9]}{rb}")
                break
            if attempt < 4 and (MOVED in out or ("failed to push" in out and "lint gate: TOTAL: 0" in out)):
                sh("git", "worktree", "remove", "--force", a.worktree)
                continue
            rep(f"roster: {op} {g} refused rc={r.returncode} " + " | ".join(out.strip().split("\n")[-3:])[:400])
            break
    return 0


def _self_test():
    fails = []
    n = [0]

    def ck(name, ok):
        n[0] += 1
        if not ok:
            fails.append(name)
            print("  FAIL", name)

    ck("parse: numbered", parse_line("7 set-stage G done") == ("set-stage", "G", "done", []))
    ck("parse: blank/comment", parse_line("") is None and parse_line("# x") is None)
    ck("parse: quoted arg", parse_line("append-carry G 'a b'") == ("append-carry", "G", "a b", []))
    ck("parse: drop-carry --match keeps the flag and its text",
       parse_line("drop-carry G --match 'x.py:1-2'") == ("drop-carry", "G", "", ["--match", "x.py:1-2"]))
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "repo"
        repo.mkdir()
        _git("init", "-q", cwd=repo)
        _git("config", "user.email", "a@b", cwd=repo)
        _git("config", "user.name", "a", cwd=repo)
        (repo / ROSTER_REL).parent.mkdir(parents=True)
        (repo / ROSTER_REL).write_text(json.dumps({"groups": [{"group": "G", "carry": ["one", "two\nlines"]}]}))
        _git("add", "-A", cwd=repo)
        _git("commit", "-qm", "r", cwd=repo)
        sha = _git("rev-parse", "HEAD", cwd=repo).stdout.strip()
        (t / "c.txt").write_text("two\nlines\n")
        (t / "d.txt").write_text("three")
        line, ok = readback(sha, "G", t / "c.txt", cwd=repo)
        ck("readback: exact match found at index 1", ok and "exact-match-index=[1]" in line and "n_carry=2" in line)
        line, ok = readback(sha, "G", t / "d.txt", cwd=repo)
        ck("readback: absent text is no match (null control)", not ok and "exact-match-index=[]" in line)
        try:
            readback(sha, "NOPE", t / "c.txt", cwd=repo)
            ck("readback: unknown group raises", False)
        except RuntimeError:
            ck("readback: unknown group raises", True)

        # run_queue against a stub editor and a stub origin
        stub = t / "stub.py"
        (t / "calls").write_text("")
        (t / "mode").write_text("moved1")
        stub.write_text(
            "import sys,pathlib\n"
            f"c=pathlib.Path({str(t / 'calls')!r}); m=pathlib.Path({str(t / 'mode')!r})\n"
            "c.write_text(c.read_text()+' '.join(sys.argv[2:5])+'\\n')\n"
            f"pathlib.Path({str(t / 'argv')!r}).open('a').write(' '.join(sys.argv[1:])+'\\n')\n"
            "if 'BAD' in sys.argv: print('REFUSED: unknown group'); sys.exit(2)\n"
            "if m.read_text()=='moved1':\n"
            "    m.write_text('ok'); print('--lint-cwd x is not origin/main'); sys.exit(3)\n"
            f"print('pushed handoff/x at {sha}')\n")
        q = t / "q.txt"
        q.write_text(f"1 append-carry G @{t / 'c.txt'}\n# skip\n\n2 set-stage BAD done\n3 set-stage G done\n4 drop-carry G --match 'x.py:1-2'\n")
        a = argparse.Namespace(first=1, last=6, queue=str(q), report=str(t / "rep"),
                               edit_checkout=str(repo), worktree=str(repo), lint_clone=str(repo),
                               alive=str(t / "alive"), branch=None, editor=str(stub))
        run_queue(a, python=sys.executable)
        rep = (t / "rep").read_text().strip().split("\n")
        calls = (t / "calls").read_text().strip().split("\n")
        ck("run: one report line per op", len(rep) == 4)
        ck("run: moved main retried (first op called twice)", calls[0] == calls[1])
        ck("run: pushed + readback on append-carry", rep[0].startswith("roster: append-carry G pushed " + sha[:9])
           and "exact-match-index=[1]" in rep[0])
        ck("run: refusal reported, not retried", "refused rc=2" in rep[1] and sum("BAD" in c for c in calls) == 1)
        ck("run: later op still runs", rep[2] == f"roster: set-stage G pushed {sha[:9]}")
        dl = [x for x in (t / "argv").read_text().split("\n") if x.startswith("drop-carry")]
        ck("run: drop-carry --match reaches the editor as a flag, not a value",
           len(dl) == 1 and dl[0].startswith("drop-carry G --match x.py:1-2 --checkout ")
           and rep[3] == f"roster: drop-carry G pushed {sha[:9]}")
        ck("run: alive touched", (t / "alive").exists())
    print(f"roster_queue self-test: {n[0]} checks, {len(fails)} failed")
    return 1 if fails else 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--self-test"]:
        return _self_test()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("first", type=int)
    r.add_argument("last", type=int)
    for k in ("queue", "report", "edit-checkout", "worktree", "lint-clone"):
        r.add_argument("--" + k, required=True)
    r.add_argument("--alive")
    r.add_argument("--branch")
    r.add_argument("--editor")
    b = sub.add_parser("readback")
    b.add_argument("sha")
    b.add_argument("group")
    b.add_argument("file")
    a = p.parse_args(argv)
    if a.cmd == "run":
        return run_queue(a)
    line, ok = readback(a.sha, a.group, a.file)
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
