#!/usr/bin/env python3
"""Refuse a tree whose policy, instruments or workflows are not origin/main's.

    python3 -I tools/audit/seat/base_fresh.py tree    [--dir D] [--rev R] [--handoff] [--no-fetch]
    python3 -I tools/audit/seat/base_fresh.py ensure  [--dir D] [--no-fetch]
    python3 -I tools/audit/seat/base_fresh.py reset   [--dir D] [--no-fetch]
    python3 -I tools/audit/seat/base_fresh.py overlay --file F --of <tracked path> --patch P [--dir D] [--no-fetch]
    python3 -I tools/audit/seat/base_fresh.py --self-test

WHY (dev/audit/rca/R11-RCA-PLAN-OBJECTIVE-MISSING.md). A seat executes the
contracts, instruments and workflow scripts of whatever tree it was started
in, and nothing compared that tree with origin/main: the freshness barriers
that existed (tick_loop.sh P14, beatd.py P581, pr_args.sh pr_tools_fresh) each
cover one instrument's own code paths. This one's unit is the seat's tree.

TREE. For each path under POLICY whose blob at HEAD differs from main's:
  STALE  main changed it after HEAD's merge base: the tree holds a superseded copy;
  OWN    only this branch changed it: the seat's own committed diff, allowed.
A tracked POLICY file with an uncommitted edit, and an untracked file under
POLICY, are STALE too: nothing on origin holds what the seat would execute.
`--rev R` judges a commit instead of the checkout (no uncommitted state).
`--handoff` is the check before a head freezes: an uncommitted edit still
refuses, and files main moved since the base are listed without refusing,
because a head behind main is not merged for that (fixer.md step 6) and its
reviewer reads policy from origin/main.

RESET moves a checkout that holds no work to origin/main: clean of tracked
edits and with no commit origin/main lacks, it is checked out there, on its
branch when it has one (`checkout -B`), detached otherwise. A checkout with a
commit of its own, or a dirty one, is never moved and the answer says why.
tick_loop.sh's restart calls this, so the rule exists once.

ENSURE is what a checkout that carries no work runs before use: TREE, and
when that refuses, RESET, then TREE again. Its last line is `BASE-FRESH PASS`,
`BASE-RESET <old> -> <new>` (the caller restarts whatever it had already read
from the old tree) or `BASE-FRESH FAIL`.

OVERLAY judges a local copy of a tracked file (a Workflow script launched by
path): it must be main's current file with its declared patch applied.

Exit 0 fresh (or reset, or a --handoff listing); 1 a refusal, each with its
repair; 2 nothing could be read (no checkout, no origin/main, a failed fetch,
a shallow clone), which is a refusal too: an unread base is not a fresh one.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

#: What a seat executes rather than edits: the index and its twin, the
#: contracts, rules, skills, hooks and workflow scripts, the owner's rulings,
#: and the instruments.
POLICY = ("CLAUDE.md", "AGENTS.md", "dev/governance", "dev/programme/RULINGS.md",
          ".claude/workflows", ".claude/rules", ".claude/skills", ".claude/hooks",
          "tools/audit", "tools/policy", "tools/pr", "tools/plan")
SELF = "tools/audit/seat/base_fresh.py"
FETCH_TIMEOUT = 30
DETAIL = 12  # STALE lines that carry main's commit; a log per path is ~70 ms each


class Unread(Exception):
    """Nothing could be measured; the message names what and the repair."""


def _git(d: str, *a: str, timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, timeout=timeout)


def _out(d: str, *a: str) -> str:
    r = _git(d, *a)
    if r.returncode:
        raise Unread(f"git {' '.join(a[:3])} failed in {d}: {(r.stderr.strip().splitlines() or ['no output'])[-1][:160]}")
    return r.stdout.strip()


def _fetch(d: str, main: str) -> None:
    remote, _, branch = main.partition("/")
    try:
        r = _git(d, "fetch", "-q", remote, f"+refs/heads/{branch}:refs/remotes/{remote}/{branch}", timeout=FETCH_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise Unread(f"git fetch {remote} {branch} did not answer in {FETCH_TIMEOUT} s; rerun, or pass --no-fetch "
                     "straight after a fetch of your own") from None
    if r.returncode:
        raise Unread(f"git fetch {remote} {branch} failed: {(r.stderr.strip().splitlines() or ['no output'])[-1][:160]}")


def _names(d: str, a: str, b: str) -> list[str]:
    return [x for x in _out(d, "diff", "--no-renames", "--name-only", a, b, "--", *POLICY).splitlines() if x]


def measure(d: str, main: str, rev: str | None = None) -> dict:
    """{head, main, base, stale, own, dirty} of the checkout at `d`, or of `rev` in it."""
    if _git(d, "rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
        raise Unread(f"{d} is not a git checkout")
    if _git(d, "rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        raise Unread(f"{d} is a shallow clone, so no merge base is readable: git -C {d} fetch --unshallow origin")
    head = _out(d, "rev-parse", "--verify", f"{rev or 'HEAD'}^{{commit}}")
    m = _git(d, "rev-parse", "--verify", f"{main}^{{commit}}")
    if m.returncode:
        raise Unread(f"{main} does not resolve in {d}: git -C {d} fetch origin main")
    msha = m.stdout.strip()
    base = _git(d, "merge-base", head, msha).stdout.strip()
    if not base:
        raise Unread(f"{head[:10]} and {main} share no history in {d}")
    moved = set(_names(d, base, msha))
    differs = _names(d, head, msha)
    dirty: list[str] = []
    if rev is None:
        top = _out(d, "rev-parse", "--show-toplevel")
        st = _git(top, "status", "--porcelain", "--untracked-files=all", "--", *POLICY)
        if st.returncode:
            raise Unread(f"git status failed in {top}")
        for ln in st.stdout.splitlines():  # unstripped: a leading space is the first status column
            if ln.strip():
                dirty.append(ln[3:].split(" -> ")[-1].strip('"'))
    return {"head": head, "main": msha, "base": base, "dirty": dirty,
            "stale": [p for p in differs if p in moved], "own": [p for p in differs if p not in moved]}


def _repair(d: str, main: str, m: dict) -> str:
    parts = []
    if m["stale"]:
        parts.append(f"python3 -I {SELF} ensure --dir {d} (a checkout that carries no work: it is moved to {main}), "
                     f"or git -C {d} merge {main} (a branch with commits; never rebase a handed-off one)")
    if m["dirty"]:
        parts.append("commit the edit on a branch, or drop it (git checkout -- <path>; an untracked copy: delete it, "
                     "or judge it with the overlay verb)")
    return "; ".join(parts) + "; then restart the step that read the stale files"


def tree(d: str, main: str, *, rev: str | None = None, handoff: bool = False, fetch: bool = True) -> int:
    if fetch:
        _fetch(d, main)
    m = measure(d, main, rev)
    word = "LISTED" if handoff else "STALE"
    for i, p in enumerate(m["stale"]):
        when = _out(d, "log", "-1", "--format=%h %cI %s", m["main"], "--", p)[:90] if i < DETAIL else "..."
        print(f"  {word} {p}: main changed it after this tree's base {m['base'][:10]} ({when})")
    for p in m["dirty"]:
        print(f"  STALE {p}: an uncommitted or untracked policy, instrument or workflow file (an overlay)")
    print(f"  own {len(m['own'])} file(s) this branch changes itself")
    bad = m["dirty"] if handoff else m["stale"] + m["dirty"]
    if handoff and m["stale"]:
        print(f"  note: {len(m['stale'])} file(s) main moved since the base are not merged for a handoff (fixer.md "
              f"step 6); the reviewer reads policy from {main}")
    if bad:
        print(f"  repair: {_repair(d, main, {**m, 'stale': [] if handoff else m['stale']})}")
    print(f"BASE-FRESH {'FAIL' if bad else 'PASS'} {m['head'][:10]} vs {main} {m['main'][:10]} "
          f"(stale {len(m['stale']) + len(m['dirty'])}, own {len(m['own'])})")
    return 1 if bad else 0


def reset_why(d: str, main: str) -> tuple[str | None, str, str]:
    """(why the checkout is not moved or None when it was, old head, new head)."""
    top = _out(d, "rev-parse", "--show-toplevel")
    old, new = _out(top, "rev-parse", "HEAD"), _out(top, "rev-parse", "--verify", f"{main}^{{commit}}")
    if old == new:
        return None, old, new
    br = _git(top, "symbolic-ref", "-q", "--short", "HEAD").stdout.strip()
    own = _git(top, "rev-list", "--count", f"{main}..HEAD").stdout.strip() or "unknown"
    if own != "0":
        who = f"the branch {br}" if br else "the detached head"
        return f"{who} holds {own} commit(s) {main} lacks; it is never moved", old, new
    if _out(top, "status", "--porcelain", "--untracked-files=no"):
        return "the tree is dirty", old, new
    if _git(top, "checkout", "-q", *(["-B", br] if br else ["--detach"]), main).returncode:
        return "the checkout failed", old, new
    return None, old, new


def reset(d: str, main: str, *, fetch: bool = True) -> int:
    if fetch:
        _fetch(d, main)
    why, old, new = reset_why(d, main)
    if why:
        print(f"BASE-RESET REFUSED: {why}")
        return 1
    print(f"BASE-RESET {old[:10]} -> {new[:10]}" if old != new else f"BASE-RESET none: already at {main} {new[:10]}")
    return 0


def ensure(d: str, main: str, *, fetch: bool = True) -> int:
    if fetch:
        _fetch(d, main)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = tree(d, main, fetch=False)
    if rc == 0:
        print(buf.getvalue(), end="")
        return 0
    why, old, new = reset_why(d, main)
    if why or old == new:  # not movable, or level with main and still refused (an uncommitted edit)
        print(buf.getvalue(), end="")
        if why:
            print(f"  not reset: {why}")
        return 1
    with contextlib.redirect_stdout(buf):
        rc = tree(d, main, fetch=False)
    if rc:
        print(buf.getvalue(), end="")
        return 1
    print(f"BASE-RESET {old[:10]} -> {new[:10]}: {d} held no work and was behind {main}; restart whatever "
          "already read the old tree")
    return 0


def overlay(d: str, main: str, file: str, of: str, patch: str, *, fetch: bool = True) -> int:
    if fetch:
        _fetch(d, main)
    r = _git(d, "show", f"{main}:{of}")
    if r.returncode:
        raise Unread(f"{main}:{of} is not a tracked file")
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "target")
        Path(target).write_text(r.stdout)
        p = subprocess.run(["patch", "-s", "-f", "--no-backup-if-mismatch", "-r", "-", target, patch],
                           capture_output=True, text=True)
        if p.returncode:
            print(f"  STALE {file}: its patch no longer applies to {main}:{of}; main moved the file under the overlay")
            print(f"  repair: re-derive the patch against {main}:{of}, regenerate the overlay, relaunch")
            print("BASE-FRESH FAIL overlay")
            return 1
        expected = Path(target).read_text()
    if Path(file).read_text().rstrip("\n") != expected.rstrip("\n"):
        print(f"  STALE {file}: not {main}:{of} with its patch applied; the overlay was cut from another version")
        print(f"  repair: patch {main}:{of} with {patch} into {file}, relaunch")
        print("BASE-FRESH FAIL overlay")
        return 1
    print(f"BASE-FRESH PASS overlay {file} = {main}:{of} + {os.path.basename(patch)}")
    return 0


# ---------------------------------------------------------------------------
# the seat-start paths: every one names this instrument (the class's seams)

#: (file, the text it must carry). `.claude/workflows/*.js` is added by glob,
#: so a workflow script added without the check is refused the day it lands.
WIRED = (
    (".claude/hooks/session-start.sh", "base_fresh.py"),               # a local or cloud seat's start
    ("tools/audit/seat/hooks/liveness.py", "BASE-STALE"),              # the orchestrator's wake
    ("tools/audit/seat/cloud_dispatch.py", "base_fresh.py"),           # a cloud seat's start and handoff
    ("tools/audit/seat/review_packet.py", "base_fresh"),               # a reviewer's dispatch
    ("tools/audit/seat/body_push.sh", "base_fresh.py"),                # the handoff
    ("tools/audit/seat/handoff_push.sh", "base_fresh.py"),             # the open
    ("tools/audit/seat/tick_loop.sh", "base_fresh.py"),                # the standing loop's restart
    ("tools/audit/seat/wt_sync.sh", "base_fresh.py"),                  # the snapshot loop
)


def unwired(root: Path) -> list[str]:
    """Every seat-start path that does not name this instrument."""
    rows = list(WIRED) + [(p.relative_to(root).as_posix(), "base_fresh.py")
                          for p in sorted((root / ".claude/workflows").glob("*.js"))]
    out = []
    for rel, needle in rows:
        f = root / rel
        if not f.is_file():
            out.append(f"{rel}: missing")
        elif needle not in f.read_text(errors="replace"):
            out.append(f"{rel}: does not name {needle}")
    return out


def _self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_COMMITTER_NAME="t",
               GIT_AUTHOR_EMAIL="1+t@users.noreply.github.com", GIT_COMMITTER_EMAIL="1+t@users.noreply.github.com")
    saved = dict(os.environ)
    os.environ.clear()
    os.environ.update(env)

    def g(d, *a) -> str:
        r = subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True)
        assert r.returncode == 0, (a, r.stderr)
        return r.stdout.strip()

    def run(fn, *a, **kw) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = fn(*a, **kw)
            except Unread as e:
                print(f"BASE-FRESH UNREAD: {e}")
                rc = 2
        return rc, buf.getvalue()

    try:
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            src, origin = t / "src", t / "o.git"
            subprocess.run(["git", "init", "-q", "-b", "main", str(src)], check=True, env=env)
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True, env=env)

            def land(path: str, text: str) -> str:
                f = src / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text)
                g(src, "add", "-A")
                g(src, "commit", "-qm", path)
                g(src, "push", "-q", str(origin), "HEAD:main")
                return g(src, "rev-parse", "HEAD")

            land("dev/governance/roles/x.md", "contract 1\n")
            land(".claude/workflows/w.js", "a\nb\nc\nd\ne\nf\ng\n")
            c0 = land("custom_components/p.py", "code 1\n")

            def clone(name: str, at: str = "origin/main", branch: str | None = None) -> Path:
                d = t / name
                subprocess.run(["git", "clone", "-q", str(origin), str(d)], check=True, env=env)
                g(d, "checkout", "-q", *(["-b", branch] if branch else ["--detach"]), at)
                return d

            fresh = clone("fresh")
            rc, out = run(tree, str(fresh), "origin/main")
            check("control: a checkout at origin/main passes", rc == 0 and "BASE-FRESH PASS" in out and "(stale 0, own 0)" in out)

            stale = clone("stale")
            own = clone("own", branch="work")
            both = clone("both", branch="work")
            idle = clone("idle", branch="claude/session")
            (own / "dev/governance/roles/x.md").write_text("contract 1\nmy edit\n")
            g(own, "commit", "-qam", "own policy edit")
            (both / "dev/governance/roles/x.md").write_text("my version\n")
            g(both, "commit", "-qam", "own policy edit")
            rc, out = run(tree, str(own), "origin/main")
            check("control: a branch's own committed policy edit on a fresh base passes (own 1)",
                  rc == 0 and "(stale 0, own 1)" in out)

            land("custom_components/p.py", "code 2\n")
            rc, out = run(tree, str(stale), "origin/main")
            check("null control: main moving a file outside the policy paths leaves an old checkout passing",
                  rc == 0 and "(stale 0, own 0)" in out)
            rc, out = run(tree, str(stale), "origin/main", fetch=False)
            c1 = land("dev/governance/roles/x.md", "contract 2\n")
            rc0, _ = run(tree, str(stale), "origin/main", fetch=False)
            check("null control: --no-fetch judges against the origin/main the checkout already has", rc == 0 and rc0 == 0)
            rc, out = run(tree, str(stale), "origin/main")
            check("a checkout behind main on a contract is refused, naming the file, main's commit and the repair",
                  rc == 1 and "  STALE dev/governance/roles/x.md: main changed it after this tree's base "
                  + c0[:10] in out and c1[:7] in out and "repair: " in out and "ensure --dir" in out
                  and out.rstrip().splitlines()[-1].startswith("BASE-FRESH FAIL ") and "(stale 1, own 0)" in out)
            rc, out = run(tree, str(own), "origin/main")
            check("a branch that edited the file main then moved is stale, not own", rc == 1 and "(stale 1, own 0)" in out)
            g(fresh, "fetch", "-q", "origin")
            rc, out = run(tree, str(fresh), "origin/main", rev=c1, fetch=False)
            rc0, out0 = run(tree, str(fresh), "origin/main", rev=c0, fetch=False)
            check("--rev judges a commit: main's tip passes and the old one is refused, the checkout untouched",
                  rc == 0 and rc0 == 1 and "x.md" in out0 and g(fresh, "rev-parse", "HEAD") == c0)
            rc, out = run(tree, str(stale), "origin/main", handoff=True)
            check("--handoff lists what main moved without refusing, and says the reviewer reads main",
                  rc == 0 and "  LISTED dev/governance/roles/x.md" in out and "the reviewer reads policy from origin/main" in out
                  and "BASE-FRESH PASS" in out)

            g(own, "merge", "-q", "--no-edit", "-X", "ours", "origin/main")
            rc, out = run(tree, str(own), "origin/main")
            check("control: after merging origin/main the branch's edit is its own again and it passes",
                  rc == 0 and "(stale 0, own 1)" in out)

            dirty = clone("dirty")
            (dirty / ".claude/workflows/w.js").write_text("a\nb\nc\nd\ne\nf\ng\nmodel: 'fable'\n")
            rc, out = run(tree, str(dirty), "origin/main")
            check("an uncommitted edit to a workflow script on a fresh base is refused as an overlay",
                  rc == 1 and "  STALE .claude/workflows/w.js: an uncommitted or untracked" in out and "(stale 1, own 0)" in out)
            rc, out = run(tree, str(dirty), "origin/main", handoff=True)
            check("--handoff still refuses the uncommitted edit", rc == 1 and "BASE-FRESH FAIL" in out)
            g(dirty, "checkout", "-q", "--", ".")
            (dirty / "tools/audit").mkdir(parents=True)
            (dirty / "tools/audit/copy.py").write_text("x\n")
            rc, out = run(tree, str(dirty), "origin/main")
            check("an untracked file under a policy path is refused", rc == 1 and "tools/audit/copy.py" in out)
            (dirty / "tools/audit/copy.py").unlink()
            (dirty / "notes.txt").write_text("x\n")
            (dirty / "custom_components/p.py").write_text("wip\n")
            rc, out = run(tree, str(dirty), "origin/main")
            check("null control: uncommitted work outside the policy paths is not this check's", rc == 0)

            # RESET and ENSURE: tick_loop.sh's rule, once.
            rc, out = run(reset, str(both), "origin/main")
            check("reset never moves a branch holding a commit origin/main lacks, and says why",
                  rc == 1 and out.strip() == "BASE-RESET REFUSED: the branch work holds 1 commit(s) origin/main lacks; it is never moved")
            rc, out = run(ensure, str(both), "origin/main")
            check("ensure on that branch refuses with the stale file and the reason it was not reset",
                  rc == 1 and "STALE dev/governance/roles/x.md" in out and "not reset: the branch work holds 1 commit" in out)
            (stale / "custom_components/p.py").write_text("wip\n")
            rc, out = run(reset, str(stale), "origin/main")
            check("reset never moves a dirty tree", rc == 1 and out.strip() == "BASE-RESET REFUSED: the tree is dirty"
                  and g(stale, "rev-parse", "HEAD") == c0)
            g(stale, "checkout", "-q", "--", ".")
            rc, out = run(ensure, str(stale), "origin/main")
            check("ensure moves a clean detached checkout with no commit of its own to origin/main and says BASE-RESET",
                  rc == 0 and out.startswith(f"BASE-RESET {c0[:10]} -> {c1[:10]}: ") and g(stale, "rev-parse", "HEAD") == c1
                  and g(stale, "branch", "--show-current") == "")
            rc, out = run(ensure, str(stale), "origin/main")
            check("control: ensure on the moved checkout now reads BASE-FRESH PASS", rc == 0 and "BASE-FRESH PASS" in out
                  and "BASE-RESET" not in out)
            rc, out = run(reset, str(idle), "origin/main")
            check("reset keeps a branch-backed checkout on its branch, at origin/main",
                  rc == 0 and out.strip() == f"BASE-RESET {c0[:10]} -> {c1[:10]}" and g(idle, "rev-parse", "HEAD") == c1
                  and g(idle, "branch", "--show-current") == "claude/session")
            rc, out = run(reset, str(idle), "origin/main")
            check("control: reset on a checkout already at origin/main moves nothing", rc == 0 and out.startswith("BASE-RESET none: "))
            (dirty / ".claude/workflows/w.js").write_text("edited\n")
            g(dirty, "checkout", "-q", "--", "custom_components/p.py")
            rc, out = run(ensure, str(dirty), "origin/main")
            check("ensure cannot repair an uncommitted policy edit: refused, the edit kept",
                  rc == 1 and "BASE-FRESH FAIL" in out and (dirty / ".claude/workflows/w.js").read_text() == "edited\n")

            # OVERLAY: the prototype's three controls.
            old_js = g(src, "show", f"{c0}:.claude/workflows/w.js") + "\n"
            (t / "old.js").write_text(old_js)
            (t / "ov.js").write_text(old_js.replace("d\n", "d model\n"))
            p_old = subprocess.run(["diff", "-u", str(t / "old.js"), str(t / "ov.js")], capture_output=True, text=True).stdout
            (t / "old.patch").write_text(p_old)
            rc, out = run(overlay, str(fresh), "origin/main", str(t / "ov.js"), ".claude/workflows/w.js", str(t / "old.patch"))
            check("control: an overlay that is main's file plus its patch passes", rc == 0 and "BASE-FRESH PASS overlay" in out)
            land(".claude/workflows/w.js", "a\nb\nc\nD2\ne\nf\ng\nobjective\n")
            rc, out = run(overlay, str(fresh), "origin/main", str(t / "ov.js"), ".claude/workflows/w.js", str(t / "old.patch"))
            check("an overlay whose patch no longer applies to main's file is refused",
                  rc == 1 and "its patch no longer applies" in out and "BASE-FRESH FAIL overlay" in out)
            new_js = g(src, "show", "HEAD:.claude/workflows/w.js") + "\n"
            (t / "new.js").write_text(new_js)
            (t / "regen.js").write_text(new_js.replace("a\n", "a model\n"))
            (t / "new.patch").write_text(subprocess.run(["diff", "-u", str(t / "new.js"), str(t / "regen.js")],
                                                        capture_output=True, text=True).stdout)
            rc, out = run(overlay, str(fresh), "origin/main", str(t / "regen.js"), ".claude/workflows/w.js", str(t / "new.patch"))
            check("control: the overlay regenerated from main passes", rc == 0)
            rc, out = run(overlay, str(fresh), "origin/main", str(t / "ov.js"), ".claude/workflows/w.js", str(t / "new.patch"))
            check("the stale overlay judged against main's patch is refused as cut from another version",
                  rc == 1 and "cut from another version" in out)

            # UNREAD: an unread base is a refusal, never a pass.
            (t / "plain").mkdir()
            rc, out = run(tree, str(t / "plain"), "origin/main", fetch=False)
            check("a directory that is no checkout is exit 2, not a pass", rc == 2 and "is not a git checkout" in out)
            rc, out = run(tree, str(fresh), "origin/nowhere", fetch=False)
            check("a main ref that does not resolve is exit 2", rc == 2 and "does not resolve" in out)
            g(fresh, "remote", "set-url", "origin", str(t / "gone.git"))
            rc, out = run(tree, str(fresh), "origin/main")
            rc0, _ = run(tree, str(fresh), "origin/main", fetch=False)
            check("a failed fetch is exit 2 (control: --no-fetch on the same checkout still answers)",
                  rc == 2 and "git fetch origin main failed" in out and rc0 in (0, 1))
            sh = t / "shallow"
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(sh)], check=True, env=env)
            rc, out = run(tree, str(sh), "origin/main", fetch=False)
            check("a shallow clone is exit 2, naming the unshallow fetch", rc == 2 and "fetch --unshallow" in out)
            r = subprocess.run([sys.executable, "-I", __file__, "tree", "--dir", str(t / "plain"), "--no-fetch"],
                               capture_output=True, text=True)
            check("the command line prints BASE-FRESH UNREAD and exits 2 on an unread base",
                  r.returncode == 2 and r.stdout.startswith("BASE-FRESH UNREAD: "))

        # THE CLASS'S SEAMS: every seat-start path of this tree names the instrument.
        root = Path(__file__).resolve().parents[3]
        gaps = unwired(root)
        flows = sorted((root / ".claude/workflows").glob("*.js"))
        check(f"every seat-start path names this instrument: {len(WIRED)} instruments and hooks, {len(flows)} workflow scripts"
              + (f" -- unwired: {'; '.join(gaps)}" if gaps else ""), not gaps and len(flows) > 0)
        with tempfile.TemporaryDirectory() as t2:
            t2 = Path(t2)
            for rel, _ in WIRED:
                (t2 / rel).parent.mkdir(parents=True, exist_ok=True)
                (t2 / rel).write_text("base_fresh.py BASE-STALE\n")
            (t2 / ".claude/workflows").mkdir(parents=True, exist_ok=True)
            (t2 / ".claude/workflows/new.js").write_text("// a workflow added without the check\n")
            (t2 / "tools/audit/seat/wt_sync.sh").write_text("# no check\n")
            (t2 / "tools/audit/seat/body_push.sh").unlink()
            check("the census names an unwired instrument, a missing one and a workflow script added without the check",
                  unwired(t2) == ["tools/audit/seat/body_push.sh: missing",
                                  "tools/audit/seat/wt_sync.sh: does not name base_fresh.py",
                                  ".claude/workflows/new.js: does not name base_fresh.py"])
    finally:
        os.environ.clear()
        os.environ.update(saved)
    print(f"base_fresh self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    for name in ("tree", "ensure", "reset", "overlay"):
        p = sub.add_parser(name)
        p.add_argument("--dir", default=".")
        p.add_argument("--main", default="origin/main")
        p.add_argument("--no-fetch", action="store_true")
        if name == "tree":
            p.add_argument("--rev")
            p.add_argument("--handoff", action="store_true")
        if name == "overlay":
            p.add_argument("--file", required=True)
            p.add_argument("--of", required=True)
            p.add_argument("--patch", required=True)
    a = ap.parse_args(argv)
    fetch = not a.no_fetch
    try:
        if a.mode == "tree":
            return tree(a.dir, a.main, rev=a.rev, handoff=a.handoff, fetch=fetch)
        if a.mode == "ensure":
            return ensure(a.dir, a.main, fetch=fetch)
        if a.mode == "reset":
            return reset(a.dir, a.main, fetch=fetch)
        return overlay(a.dir, a.main, a.file, a.of, a.patch, fetch=fetch)
    except Unread as e:
        print(f"BASE-FRESH UNREAD: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
