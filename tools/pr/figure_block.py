#!/usr/bin/env python3
"""Registered figures for a pull request, rendered by the run and never stored in the body.

``figure_registry.json`` names the instruments a figure may be rendered from. It
is read from the BASE tree (``--base``), so a pull request cannot add an
instrument and use it in the same pull request: **the author chooses no
command**, only a registered name. Each registered instrument runs in a
throwaway worktree of the head, with the registry's ``files`` overlaid from the
base, so the program is the base's and the tree it measures is the head's.

A rendered block names the head it was rendered at, so a block stored in a body
went stale at every head move no seat made: the merge-main bot's commit, a
recarry, a remerge (PC-1113-10, PC-1113-19;
dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md). A body therefore stores
none. ``pr-contract`` renders every registered instrument at the head it grades
into its job summary, and no head move leaves anything in the body to redo.

    figure_block.py render NAME  [--base REF] [--head REF]   print one rendered block
    figure_block.py verify BODY                              refuse a body that carries a block,
                                                             rendered, empty or typed (read-only)
    figure_block.py strip  BODY                              delete every block from a body file
    figure_block.py --self-test

``verify`` (``pr-contract``, ``prepr.sh``) reads the body alone and runs no
instrument. ``strip`` is the sweep for a body written before this rule: it
deletes each block, marker to marker, and leaves every other byte. A free-form
figure under ``## Figures`` stays as it was, well-formed and resolvable, never
executed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REGISTRY = "tools/pr/figure_registry.json"
OPEN_RE = re.compile(r"^<!-- figure-block: (?P<name>[a-z][a-z0-9-]*)(?P<attrs>(?: [a-z]+=[0-9a-f]{40})*) -->$")
CLOSE = "<!-- /figure-block -->"
FENCE = "~~~text"
FENCE_END = "~~~"
PLACEHOLDERS = ("mb", "head", "base", "workdir")


class Refused(Exception):
    pass


def _git(root: str, *args: str) -> str:
    p = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=False)
    if p.returncode:
        raise Refused(f"git {' '.join(args)}: {p.stderr.strip() or 'failed'}")
    return p.stdout.strip()


def load_registry(root: str, base: str) -> dict:
    """The registry as the BASE tree holds it; a base without one registers nothing."""
    p = subprocess.run(["git", "-C", root, "show", f"{base}:{REGISTRY}"], capture_output=True, text=True, check=False)
    if p.returncode:
        return {}
    data = json.loads(p.stdout)
    return data.get("instruments", {})


def parse(text: str):
    """Yield (start, end, name, attrs, body) per block; line indexes are [start, end]."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = OPEN_RE.match(lines[i])
        if not m:
            if lines[i].startswith("<!-- figure-block"):
                raise Refused(f"line {i + 1}: a figure-block marker that does not parse: {lines[i][:80]!r}")
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j] != CLOSE:
            if lines[j].startswith("<!-- figure-block"):
                raise Refused(f"line {j + 1}: a figure-block opens inside another")
            j += 1
        if j >= len(lines):
            raise Refused(f"line {i + 1}: figure-block {m['name']} is never closed")
        attrs = dict(a.split("=") for a in m["attrs"].split())
        out.append((i, j, m["name"], attrs, lines[i + 1:j]))
        i = j + 1
    return lines, out


def render_text(name: str, attrs: dict, output: str) -> list[str]:
    a = "".join(f" {k}={attrs[k]}" for k in ("mb", "head") if k in attrs)
    return [f"<!-- figure-block: {name}{a} -->", FENCE, *output.rstrip("\n").split("\n"), FENCE_END, CLOSE]


def overlay_program(wt: str, base: str, head: str, files: list[str], exclude: str) -> dict:
    """Lay the base's copy of ``files`` over the head's worktree ``wt``; the environment the run needs.

    The overlay is the program the run executes, never the head's change, and an
    instrument that asks git what the branch changed (`tests/closure.py`'s
    `changed_files`: tracked changes against HEAD, then untracked files) must not
    be handed it: a branch forked before main changed `tests/closure.py` read as
    having edited a gate file and rendered `MODE: FULL`. The index goes back to
    the head's; a file the head tracks is marked skip-worktree, and one only the
    base has is named in an excludes file the returned environment points git at.
    """
    if not files:
        return {}
    for f in files:
        _git(wt, "checkout", base, "--", f)  # the base's program, not the head's
    _git(wt, "reset", "-q", head, "--", *files)
    tracked = [f for f in _git(wt, "ls-files", "--", *files).split("\n") if f]
    if tracked:
        _git(wt, "update-index", "--skip-worktree", "--", *tracked)
    with open(exclude, "w", encoding="utf-8") as fh:
        fh.write("".join(f"/{f}\n" for f in files if f not in tracked))
    return {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.excludesFile", "GIT_CONFIG_VALUE_0": exclude}


def run_instrument(root: str, base: str, head: str, mb: str, name: str, reg: dict) -> str:
    """Run one registered instrument over the head's tree with the base's program."""
    if name not in reg:
        raise Refused(f"`{name}` is not in the registry at {base[:12]}:{REGISTRY} "
                      f"({', '.join(sorted(reg)) or 'it registers nothing'}); a pull request cannot add an instrument and use it")
    ent = reg[name]
    tmp = tempfile.mkdtemp(prefix="figblock-")
    wt = os.path.join(tmp, "wt")
    workdir = os.path.join(tmp, "work")
    os.mkdir(workdir)
    try:
        _git(root, "worktree", "add", "--detach", "-q", wt, head)
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TMPDIR", "VIRTUAL_ENV")}
        env.update(overlay_program(wt, base, head, ent.get("files", []), os.path.join(tmp, "overlay-exclude")))
        sub = dict(mb=mb, head=head, base=base, workdir=workdir)
        argv = [a.format(**sub) for a in ent["argv"]]
        env["PYTHONPATH"] = "tests/hastub"
        p = subprocess.run(argv, cwd=wt, env=env, capture_output=True, text=True, timeout=ent.get("timeout_s", 300), check=False)
        if p.returncode not in ent.get("ok_rc", [0]):
            raise Refused(f"`{name}` exited {p.returncode}: {(p.stderr or p.stdout).strip()[-300:]}")
        lines = p.stdout.rstrip("\n").split("\n")
        if "grep" in ent:
            lines = [ln for ln in lines if re.search(ent["grep"], ln)]
        if "tail" in ent:
            lines = lines[-int(ent["tail"]):]
        if not lines or lines == [""]:
            raise Refused(f"`{name}` printed nothing after its filter")
        return "\n".join(lines)
    finally:
        subprocess.run(["git", "-C", root, "worktree", "remove", "--force", wt], capture_output=True, check=False)
        shutil.rmtree(tmp, ignore_errors=True)


def context(root: str, base: str, head: str) -> tuple[str, str]:
    head_sha = _git(root, "rev-parse", "--verify", head + "^{commit}")
    return head_sha, _git(root, "merge-base", base, head_sha)


def cmd_render(root, base, head, name):
    head_sha, mb = context(root, base, head)
    out = run_instrument(root, base, head_sha, mb, name, load_registry(root, base))
    print("\n".join(render_text(name, {"mb": mb, "head": head_sha}, out)))


MARKER = "<!-- figure-block"
CLOSE_MARKER = "<!-- /figure-block"


def verify_text(text: str) -> list[str]:
    """One problem per figure-block marker in ``text``; none for a body that stores no block.

    Any marker is refused, whatever sits between a pair: a rendered block names
    a head that the next head move makes false, an empty marker asks a writer
    that no longer exists to fill it, and a typed one was never a measurement.
    The read is of lines, not of well-formed blocks, so a malformed or unclosed
    marker is refused like any other and cannot hide what follows it.
    """
    problems, opened = [], False
    for i, line in enumerate(text.split("\n")):
        if line.startswith(MARKER):
            m = OPEN_RE.match(line)
            opened = True
            problems.append(f"line {i + 1}: a stored figure block ({'`' + m.group('name') + '`' if m else 'its marker does not parse'}); "
                            "a body stores no rendered figure -- pr-contract renders the registered instruments at the head it "
                            "grades into its job summary. Delete the block: `figure_block.py strip <body>`")
        elif line.startswith(CLOSE_MARKER):
            if not opened:
                problems.append(f"line {i + 1}: a figure-block close marker with no block above it; delete the line")
            opened = False
    return problems


def strip_text(text: str) -> tuple[str, int]:
    """``text`` without its figure blocks, and how many were cut; every other line is kept as it was."""
    lines, blocks = parse(text)
    for i, j, _name, _attrs, _body in reversed(blocks):
        del lines[i:j + 1]
    return "\n".join(lines), len(blocks)


def cmd_strip(body_path):
    text = open(body_path, encoding="utf-8").read()
    out, n = strip_text(text)
    if n:
        open(body_path, "w", encoding="utf-8").write(out)
    print(f"figure_block: stripped {n} block(s)")
    return 0


def cmd_verify(body_path):
    problems = verify_text(open(body_path, encoding="utf-8").read())
    for p in problems:
        print(f"  ERROR   [figure-block] {p}")
    print(f"figure_block verify: {len(problems)} stored block marker(s) refused")
    return 1 if problems else 0


def _scope(root: str, mb: str, workdir: str) -> int:
    """The registered `scope-line` instrument: the gate's MODE line for the diff since ``mb``."""
    p = subprocess.run([sys.executable, "tests/closure.py", "select", "--diff", mb, "--workdir", workdir],
                       cwd=root, capture_output=True, text=True, check=False)
    scope = os.path.join(workdir, "scope.txt")
    if p.returncode or not os.path.exists(scope):
        print(p.stderr[-300:], file=sys.stderr)
        return 1
    mode = [ln for ln in open(scope, encoding="utf-8").read().split("\n") if ln.strip().startswith("MODE:")]
    print(mode[0].strip() if mode else "no MODE line")
    return 0 if mode else 1


def _self_test() -> int:
    results = []

    def check(name, ok):
        results.append(bool(ok))
        print(("  ok  " if ok else "  FAIL") + " " + name)

    def refused(fn):
        try:
            fn()
        except Refused:
            return True
        return False

    tmp = tempfile.mkdtemp(prefix="figblock-st-")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests"))
        from throwaway_git import throwaway_git_init
        env = throwaway_git_init(tmp, "-q", "-b", "main")

        def g(*a, cwd=tmp):
            subprocess.run(["git", *a], cwd=cwd, env=env, check=True, capture_output=True)
        os.makedirs(os.path.join(tmp, "tools/pr"))
        reg = {"instruments": {"mb": {"argv": ["git", "merge-base", "{base}", "{head}"], "files": []},
                               "bad": {"argv": ["false"], "files": []}}}
        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
        open(os.path.join(tmp, "f"), "w").write("1")
        g("add", "-A"); g("commit", "-qm", "base")
        g("checkout", "-qb", "topic")
        open(os.path.join(tmp, "f"), "w").write("2")
        # a head that adds an instrument the base lacks
        reg["instruments"]["evil"] = {"argv": ["echo", "pwned"], "files": []}
        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
        g("commit", "-qam", "head")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, text=True).stdout.strip()
        mbsha = subprocess.run(["git", "rev-parse", "main"], cwd=tmp, capture_output=True, text=True).stdout.strip()
        body = os.path.join(tmp, "body.md")
        free = "## Figures\nfree-form: `git log`\n"
        check("a body with no block passes, its free-form line beside it (null control)", verify_text(free) == [])
        rendered = "\n".join(render_text("mb", {"mb": mbsha, "head": head}, run_instrument(tmp, "main", head, mbsha, "mb", load_registry(tmp, "main"))))
        check("render prints the base registry's instrument at the head", mbsha + "\n~~~" in rendered and f"head={head}" in rendered)
        stored = verify_text(free + rendered + "\n")
        check("a body storing a rendered block is refused, the block named", len(stored) == 1 and "(`mb`)" in stored[0] and stored[0].startswith("line 3:"))
        check("an empty marker is refused: no writer fills it", len(verify_text(free + "<!-- figure-block: mb -->\n<!-- /figure-block -->\n")) == 1)
        check("a typed block is refused", len(verify_text(free + "<!-- figure-block: mb -->\n~~~text\nMODE: SCOPED\n~~~\n<!-- /figure-block -->\n")) == 1)
        check("two stored blocks are two refusals", len(verify_text(free + (rendered + "\n") * 2)) == 2)
        check("a malformed marker is refused, not skipped", len(verify_text("<!-- figure-block: Mb -->\n")) == 1
              and "does not parse" in verify_text("<!-- figure-block: Mb -->\n")[0])
        check("an unclosed block is refused", len(verify_text("<!-- figure-block: mb -->\nx\n")) == 1)
        check("a close marker with no block above it is refused", len(verify_text(free + "<!-- /figure-block -->\n")) == 1)
        # The defect: a stored block named its head, so a head no seat moved (the
        # merge-main bot, a recarry) left the body false. With nothing stored the
        # same body passes at the moved head; cmd_verify reads no head at all.
        _w(body, free)
        g("commit", "-q", "--allow-empty", "-m", "a head move the seat did not make")
        check("a body with no stored block passes at a head moved under it", cmd_verify(body) == 0)
        check("and the block rendered at the old head, stored, is refused there", cmd_verify(_w(body, free + rendered + "\n")) == 1)
        check("strip deletes each stored block and keeps every other line", cmd_strip(_w(body, "a\n" + rendered + "\nb\n" + rendered + "\nc\n")) == 0
              and open(body).read() == "a\nb\nc\n" and cmd_verify(body) == 0)
        check("null: strip writes nothing to a body with no block", cmd_strip(_w(body, free)) == 0 and open(body).read() == free)
        check("strip refuses an unclosed block and leaves the file", refused(lambda: cmd_strip(_w(body, "<!-- figure-block: mb -->\nx\n")))
              and open(body).read() == "<!-- figure-block: mb -->\nx\n")
        check("an instrument registered only by the head is refused (null: the base's own mb renders above)",
              refused(lambda: run_instrument(tmp, "main", head, mbsha, "evil", load_registry(tmp, "main"))))
        check("an unknown name is refused", refused(lambda: run_instrument(tmp, "main", head, mbsha, "nope", load_registry(tmp, "main"))))
        check("an instrument that exits non-zero is refused", refused(lambda: run_instrument(tmp, "main", head, mbsha, "bad", load_registry(tmp, "main"))))
        # The overlay is the program, never the head's diff: what `tests/closure.py`'s
        # `changed_files` adds to a branch's diff (tracked changes against HEAD,
        # untracked files) is empty inside the run, for a program main changed
        # after the branch forked and for one main added.
        g("checkout", "-q", "main")
        seen = "git diff --no-renames --name-only HEAD; git ls-files --others --exclude-standard; echo ran:$(cat ver)\n"
        reg["instruments"].pop("evil")
        reg["instruments"]["seen"] = {"argv": ["sh", "prog.sh"], "files": ["prog.sh", "ver", "late"]}
        open(os.path.join(tmp, REGISTRY), "w").write(json.dumps(reg))
        open(os.path.join(tmp, "prog.sh"), "w").write(seen)
        open(os.path.join(tmp, "ver"), "w").write("1")
        g("add", "-A"); g("commit", "-qm", "main registers a program")
        g("checkout", "-qb", "old")
        open(os.path.join(tmp, "f"), "w").write("3")
        g("commit", "-qam", "a branch that touches no program")
        g("checkout", "-q", "main")
        open(os.path.join(tmp, "ver"), "w").write("2")
        open(os.path.join(tmp, "late"), "w").write("added after the fork")
        g("add", "-A"); g("commit", "-qm", "main changes the program and adds a file to it")
        g("checkout", "-q", "old")
        old_sha, old_mb = context(tmp, "main", "HEAD")
        check("a program main changed or added after the fork runs as the base's and is not the head's diff",
              run_instrument(tmp, "main", old_sha, old_mb, "seen", load_registry(tmp, "main")) == "ran:2")
        open(os.path.join(tmp, "ver"), "w").write("mine")
        g("commit", "-qam", "the branch edits the program itself")
        own_sha, own_mb = context(tmp, "main", "HEAD")
        check("null: a file the instrument's run leaves changed in the head's tree is still listed",
              run_instrument(tmp, "main", own_sha, own_mb, "seen",
                             {**load_registry(tmp, "main"), "seen": {"argv": ["sh", "-e", "-c", "echo x > f; " + seen.strip()], "files": []}})
              == "f\nran:mine")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    failed = results.count(False)
    print(f"figure_block self-test: {len(results)} checks, {failed} failed")
    return 1 if failed else 0


def _w(path: str, text: str) -> str:
    open(path, "w").write(text)
    return path


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    if argv[:1] == ["_scope"]:
        return _scope(os.getcwd(), argv[1], argv[2])
    opts = {"--base": "origin/main", "--head": "HEAD"}
    pos = []
    it = iter(argv)
    for a in it:
        if a in opts:
            opts[a] = next(it, "")
        else:
            pos.append(a)
    if len(pos) != 2 or pos[0] not in ("render", "verify", "strip"):
        print(__doc__)
        return 2
    try:
        if pos[0] == "render":
            cmd_render(_git(os.getcwd(), "rev-parse", "--show-toplevel"), opts["--base"], opts["--head"], pos[1])
            return 0
        # verify and strip read the body alone; --base and --head are accepted and unread.
        return cmd_verify(pos[1]) if pos[0] == "verify" else cmd_strip(pos[1])
    except Refused as e:
        print(f"  ERROR   [figure-block] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
